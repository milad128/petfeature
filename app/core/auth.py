"""User authentication — Google OAuth + session helpers (v12)."""

from __future__ import annotations

from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

USER_SESSION_KEY = "user_id"

# ── OAuth client ──────────────────────────────────────────────────────────────

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# ── Session helpers ───────────────────────────────────────────────────────────

def login_user(request: Request, user_id: int) -> None:
    """Write user_id into the signed session cookie."""
    request.session[USER_SESSION_KEY] = user_id


def logout_user(request: Request) -> None:
    """Remove user_id from the session cookie."""
    request.session.pop(USER_SESSION_KEY, None)


# ── Middleware — attaches current_user to request.state ───────────────────────

class UserAuthMiddleware(BaseHTTPMiddleware):
    """Resolve the signed session user_id to a User ORM object and attach it to
    request.state.current_user so every template can read it via the request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        from app.core.database import async_session_factory
        from app.services.users import get_user_by_id

        request.state.current_user = None
        user_id = request.session.get(USER_SESSION_KEY)
        if user_id:
            async with async_session_factory() as db:
                user = await get_user_by_id(db, user_id)
                if user and user.is_active:
                    request.state.current_user = user
                elif user and not user.is_active:
                    # Deactivated — evict from session
                    logout_user(request)

        return await call_next(request)


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_user(request: Request) -> Optional["User"]:  # type: ignore[name-defined]
    """FastAPI dependency — returns User from request.state (set by middleware).

    Use this in route handlers that need the user object for logic beyond the
    template (e.g. protected routes, writing user_id to a new record).
    """
    return getattr(request.state, "current_user", None)


def require_login(request: Request) -> "User":  # type: ignore[name-defined]
    """Dependency — raises redirect to /login/ if not authenticated."""
    from fastapi.responses import RedirectResponse

    user = get_current_user(request)
    if user is None:
        request.session["next"] = str(request.url.path)
        raise _LoginRedirect()
    return user


class _LoginRedirect(Exception):
    """Internal signal to redirect unauthenticated users to /login/."""
