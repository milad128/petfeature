"""Visitor analytics middleware — captures PageView events after every public response."""

from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Optional
from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── Bot User-Agent filter ─────────────────────────────────────────────────
BOT_UA_SUBSTRINGS = [
    "bot", "crawler", "spider", "scraper",
    "curl", "wget",
    "python-requests", "python-httpx",
    "go-http-client", "java/",
    "ahrefsbot", "semrushbot", "mj12bot", "dotbot",
    "bingbot", "googlebot", "yandexbot", "baiduspider",
]

# ── Path classification ───────────────────────────────────────────────────
_BOOK_RE   = re.compile(r"^/library/([^/]+)/$")
_POST_RE   = re.compile(r"^/blog/([^/]+)/$")
_TOOL_RE   = re.compile(r"^/tools/([^/]+)/$")

_STATIC_PREFIXES = ("/static/", "/admin/", "/api/")

# Paths that terminate early (POST endpoints, etc.) without a slug
_EXCLUDED_POST_PATTERNS = re.compile(
    r"^/(library|blog|tools)/[^/]+/(rate|comment|download)/.*$"
)


def _is_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    return any(sub in ua for sub in BOT_UA_SUBSTRINGS)


def _extract_referrer_domain(referer_header: Optional[str]) -> Optional[str]:
    if not referer_header:
        return None
    try:
        return urlparse(referer_header).netloc or None
    except Exception:
        return None


def _classify_path(path: str):
    """Return (page_type, slug_or_None)."""
    if path == "/":
        return "home", None
    if path == "/library/":
        return "library", None
    if path == "/blog/":
        return "blog", None
    if path == "/tools/":
        return "tools", None
    if path == "/about/":
        return "about", None
    if path == "/contact/":
        return "contact", None
    m = _BOOK_RE.match(path)
    if m:
        return "book", m.group(1)
    m = _POST_RE.match(path)
    if m:
        return "post", m.group(1)
    m = _TOOL_RE.match(path)
    if m:
        return "tool", m.group(1)
    return "other", None


def _fallback_token(ip: str, ua: str) -> str:
    """Hash IP + UA into a 32-char hex string when cookie is absent."""
    raw = f"{ip}:{ua}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


async def _resolve_entity_id(slug: str, page_type: str) -> Optional[int]:
    """Look up entity_id from slug for book/post/tool detail pages."""
    from sqlalchemy import select
    from app.core.database import async_session_factory

    async with async_session_factory() as session:
        if page_type == "book":
            from app.models.book import Book
            result = await session.execute(
                select(Book.id).where(Book.slug == slug).limit(1)
            )
        elif page_type == "post":
            from app.models.post import Post
            result = await session.execute(
                select(Post.id).where(Post.slug == slug).limit(1)
            )
        elif page_type == "tool":
            from app.models.tool import Tool
            result = await session.execute(
                select(Tool.id).where(Tool.slug == slug).limit(1)
            )
        else:
            return None
        row = result.first()
        return row[0] if row else None


async def _record_page_view(
    path: str,
    page_type: str,
    slug: Optional[str],
    visitor_token: str,
    referrer_domain: Optional[str],
) -> None:
    """Write one PageView row. Runs as a background task."""
    from app.core.database import async_session_factory
    from app.models.page_view import PageView

    entity_id: Optional[int] = None
    if slug and page_type in ("book", "post", "tool"):
        entity_id = await _resolve_entity_id(slug, page_type)

    async with async_session_factory() as session:
        pv = PageView(
            path=path,
            page_type=page_type,
            entity_id=entity_id,
            visitor_token=visitor_token,
            referrer_domain=referrer_domain,
        )
        session.add(pv)
        await session.commit()


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Track every public GET request that returns 2xx as a PageView."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Only track GET requests
        if request.method != "GET":
            return response

        path = request.url.path

        # Skip non-public paths
        if any(path.startswith(pfx) for pfx in _STATIC_PREFIXES):
            return response

        # Skip POST-style sub-routes (rate, comment, download)
        if _EXCLUDED_POST_PATTERNS.match(path):
            return response

        # Skip error responses
        if response.status_code >= 400:
            return response

        # Skip bots
        ua = request.headers.get("user-agent", "")
        if _is_bot(ua):
            return response

        page_type, slug = _classify_path(path)

        # visitor_token: prefer cookie, fallback to hash
        from app.core.visitor import VISITOR_COOKIE_NAME
        token = request.cookies.get(VISITOR_COOKIE_NAME)
        if not token:
            ip = (request.client.host if request.client else "") or ""
            token = _fallback_token(ip, ua)

        referrer_domain = _extract_referrer_domain(
            request.headers.get("referer")
        )

        # Schedule background write — never blocks the response
        asyncio.create_task(
            _record_page_view(path, page_type, slug, token, referrer_domain)
        )

        return response
