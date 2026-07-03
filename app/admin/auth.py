"""Admin session authentication."""

from __future__ import annotations

from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.core.config import settings

ADMIN_SESSION_KEY = "admin_authenticated"


def verify_credentials(username: str, password: str) -> bool:
    return username == settings.admin_username and password == settings.admin_password


def login_admin(request: Request) -> None:
    request.session[ADMIN_SESSION_KEY] = True


def logout_admin(request: Request) -> None:
    request.session.pop(ADMIN_SESSION_KEY, None)


def is_admin_authenticated(request: Request) -> bool:
    return bool(request.session.get(ADMIN_SESSION_KEY))


def redirect_if_authenticated(request: Request) -> Optional[RedirectResponse]:
    if is_admin_authenticated(request):
        return RedirectResponse(url="/admin/books/", status_code=303)
    return None
