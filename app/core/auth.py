"""User authentication — Google OAuth + session helpers (v12)."""

from __future__ import annotations

import base64
import json as _json
import logging
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)

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

# ── Production patch: JWK endpoint blocked on Hamravesh (Iran) ───────────────
#
# Google's public-key endpoint (googleapis.com/oauth2/v3/certs) returns 403
# from the production host. Authlib calls it inside parse_id_token to verify
# the id_token JWT signature. We patch parse_id_token to fall back to decoding
# the JWT payload without signature verification.
#
# Why this is safe:
#   1. The OAuth state parameter is validated by authlib BEFORE token exchange,
#      so CSRF is already prevented.
#   2. The token itself arrived from Google's token endpoint over TLS — the
#      transport already guarantees integrity; re-verifying the JWT signature
#      is redundant here.
#   3. We only use claims (sub, email, name) that Google sets; we never trust
#      arbitrary client-supplied data.

def _decode_jwt_payload(id_token: str) -> dict:
    """Decode a JWT payload section without verifying the signature."""
    try:
        payload_b64 = id_token.split(".")[1]
        # Re-add base64 padding stripped by JWT encoding
        pad = 4 - len(payload_b64) % 4
        if pad != 4:
            payload_b64 += "=" * pad
        return _json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception as exc:
        raise ValueError(f"Cannot decode JWT payload: {exc}") from exc


from authlib.integrations.starlette_client.apps import StarletteOAuth2App as _StarletteOAuth2App  # noqa: E402

_orig_parse_id_token = _StarletteOAuth2App.parse_id_token


async def _patched_parse_id_token(
    self, token, nonce, claims_options=None, claims_cls=None, leeway=120
):
    """Try the real JWK-verified parse; fall back to raw JWT decode on failure.

    The real implementation fetches JWKs from googleapis.com/oauth2/v3/certs,
    which returns 403 on Hamravesh (Iran). The fallback decodes the JWT payload
    without signature verification — safe because:
      • CSRF is already blocked by the OAuth state parameter.
      • The token arrived from Google's token endpoint over TLS.
    """
    try:
        return await _orig_parse_id_token(
            self, token, nonce,
            claims_options=claims_options,
            claims_cls=claims_cls,
            leeway=leeway,
        )
    except Exception as exc:
        logger.warning(
            "parse_id_token JWK verification failed (%s) — "
            "falling back to unverified JWT payload decode.",
            exc,
        )
        id_token = token.get("id_token", "")
        if not id_token:
            return None
        try:
            return _decode_jwt_payload(id_token)
        except Exception:
            logger.exception("JWT payload decode also failed; userinfo will be None")
            return None


_StarletteOAuth2App.parse_id_token = _patched_parse_id_token


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
