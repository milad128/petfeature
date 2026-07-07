"""Anonymous visitor token cookie — used to dedupe post ratings per browser."""

from __future__ import annotations

import uuid

from fastapi import Request
from starlette.responses import Response

VISITOR_COOKIE_NAME = "visitor_token"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 2  # 2 years


def peek_visitor_token(request: Request) -> str:
    """Read the visitor token if present, otherwise mint one (not yet persisted)."""
    return request.cookies.get(VISITOR_COOKIE_NAME) or uuid.uuid4().hex


def ensure_visitor_cookie(request: Request, response: Response, token: str) -> None:
    """Persist the token as a cookie on the response if the request didn't already have it."""
    if request.cookies.get(VISITOR_COOKIE_NAME) == token:
        return
    response.set_cookie(
        VISITOR_COOKIE_NAME,
        token,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
