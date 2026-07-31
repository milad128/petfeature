"""Public auth routes — Google OAuth login / logout / profile (v12)."""

from __future__ import annotations

import logging

from authlib.integrations.base_client.errors import MismatchingStateError, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Form

from app.core.auth import get_current_user, login_user, logout_user, oauth
from app.core.config import settings
from app.core.database import get_db
from app.core.templates import templates
from app.services import bookshelf as bookshelf_service
from app.services import users as user_service
from app.models.book import Book
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter()


def _google_redirect_uri(request: Request) -> str:
    """OAuth callback URL. In DEBUG, derive from the current host (localhost). In prod, use env."""
    if settings.debug:
        path = request.url_for("auth_google_callback")
        base = request.base_url
        return f"{base.scheme}://{base.netloc}{path.path}"
    return settings.google_redirect_uri.rstrip("/") + "/"


async def _fetch_google_userinfo(request: Request, token: dict) -> dict:
    """Return Google profile claims from token userinfo, id_token, or userinfo API."""
    userinfo = token.get("userinfo")
    if isinstance(userinfo, dict) and userinfo.get("sub"):
        return userinfo

    if "id_token" in token:
        try:
            parsed = await oauth.google.parse_id_token(request, token)
            if isinstance(parsed, dict) and parsed.get("sub"):
                return parsed
        except Exception:
            logger.warning("Google id_token parse failed; falling back to userinfo endpoint", exc_info=True)

    resp = await oauth.google.get("userinfo", token=token)
    resp.raise_for_status()
    return resp.json()


# ── Login page ────────────────────────────────────────────────────────────────

@router.get("/login/", name="login")
async def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/profile/", status_code=303)
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request,
        "pages/login.html",
        {"page_title": "ورود", "error": error},
    )


# ── Initiate Google OAuth ─────────────────────────────────────────────────────

@router.get("/auth/google/", name="auth_google")
async def auth_google(request: Request):
    redirect_uri = _google_redirect_uri(request)
    return await oauth.google.authorize_redirect(request, redirect_uri)


# ── Google OAuth callback ─────────────────────────────────────────────────────

@router.get("/auth/google/callback/", name="auth_google_callback")
async def auth_google_callback(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = await _fetch_google_userinfo(request, token)
        google_id = userinfo["sub"]
        email = userinfo["email"].lower()
        name = userinfo.get("name", email)
    except MismatchingStateError:
        logger.warning("Google OAuth state mismatch — session cookie likely lost between redirects")
        return RedirectResponse(url="/login/?error=state", status_code=303)
    except OAuthError as exc:
        logger.error("Google OAuth token exchange failed: %s", exc.error, exc_info=True)
        return RedirectResponse(url="/login/?error=oauth", status_code=303)
    except (KeyError, TypeError, ValueError) as exc:
        logger.error("Google OAuth profile missing required fields: %s", exc, exc_info=True)
        return RedirectResponse(url="/login/?error=profile", status_code=303)
    except Exception:
        logger.exception("Google OAuth callback failed")
        return RedirectResponse(url="/login/?error=generic", status_code=303)

    user = await user_service.get_or_create_user(db, google_id, email, name)

    if not user.is_active:
        return RedirectResponse(url="/login/?error=disabled", status_code=303)

    login_user(request, user.id)
    next_url = request.session.pop("next", None) or "/profile/"
    return RedirectResponse(url=next_url, status_code=303)


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout/", name="logout")
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/", status_code=303)


# ── Profile / dashboard ───────────────────────────────────────────────────────

@router.get("/profile/", name="profile")
async def profile(
    request: Request,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
):
    current_user = get_current_user(request)
    if not current_user:
        request.session["next"] = "/profile/"
        return RedirectResponse(url="/login/", status_code=303)

    from app.services import users as user_service

    comments, total_comments = await user_service.get_user_comments(db, current_user.id, page=page)
    per_page = 10
    total_pages = max(1, -(-total_comments // per_page))  # ceiling division

    return templates.TemplateResponse(
        request,
        "pages/profile.html",
        {
            "page_title": "داشبورد من",
            "current_user": current_user,
            "comments": comments,
            "total_comments": total_comments,
            "page": page,
            "total_pages": total_pages,
        },
    )


# ── Bookshelf (قفسه کتاب) — v15 ──────────────────────────────────────────────

@router.get("/profile/bookshelf/", name="bookshelf")
async def bookshelf_page(request: Request, db: AsyncSession = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        request.session["next"] = "/profile/bookshelf/"
        return RedirectResponse(url="/login/", status_code=303)

    shelf = await bookshelf_service.get_user_bookshelf(db, current_user.id)
    summary = await bookshelf_service.get_bookshelf_summary(db, current_user.id)

    return templates.TemplateResponse(
        request,
        "pages/profile_bookshelf.html",
        {
            "page_title": "قفسه کتاب من",
            "current_user": current_user,
            "shelf": shelf,
            "summary": summary,
        },
    )


@router.post("/profile/bookshelf/add/", name="bookshelf_add")
async def bookshelf_add(
    request: Request,
    db: AsyncSession = Depends(get_db),
    book_id: int = Form(...),
    status: str = Form(...),
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login/", status_code=303)

    try:
        _, newly_read = await bookshelf_service.upsert_item(
            db, current_user.id, book_id, status
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="وضعیت نامعتبر است")

    # Determine redirect target
    referer = request.headers.get("referer", "")
    redirect_url = referer if referer else "/profile/bookshelf/"
    # Newly marked as read → book detail + review modal (from bookshelf or library)
    if newly_read:
        book = await db.scalar(select(Book).where(Book.id == book_id))
        if book:
            redirect_url = f"/library/{book.slug}/?review={book_id}"

    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/profile/bookshelf/remove/", name="bookshelf_remove")
async def bookshelf_remove(
    request: Request,
    db: AsyncSession = Depends(get_db),
    book_id: int = Form(...),
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login/", status_code=303)

    await bookshelf_service.remove_item(db, current_user.id, book_id)
    referer = request.headers.get("referer", "/profile/bookshelf/")
    return RedirectResponse(url=referer, status_code=303)
