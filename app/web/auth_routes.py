"""Public auth routes — Google OAuth login / logout / profile (v12)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, login_user, logout_user, oauth
from app.core.config import settings
from app.core.database import get_db
from app.core.templates import templates
from app.services import users as user_service

router = APIRouter()


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
    return await oauth.google.authorize_redirect(
        request, settings.google_redirect_uri
    )


# ── Google OAuth callback ─────────────────────────────────────────────────────

@router.get("/auth/google/callback/", name="auth_google_callback")
async def auth_google_callback(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo") or {}
        google_id: str = userinfo["sub"]
        email: str = userinfo["email"].lower()
        name: str = userinfo.get("name", email)
    except Exception:
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
async def profile(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        request.session["next"] = "/profile/"
        return RedirectResponse(url="/login/", status_code=303)
    return templates.TemplateResponse(
        request,
        "pages/profile.html",
        {"page_title": "داشبورد من", "current_user": current_user},
    )
