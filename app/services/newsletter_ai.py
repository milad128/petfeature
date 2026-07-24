"""AI newsletter draft generation via GapGPT (OpenAI-compatible API)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services import newsletters as newsletter_service
from app.services import books as book_service
from app.services import posts as post_service
from app.services import tools as tool_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """تو دستیار نویسنده خبرنامه پت‌فیچر هستی — یک دانشنامه فارسی برای مدیران محصول.
وظیفه‌ات نوشتن یک پیام خبرنامه کوتاه و جذاب برای کانال تلگرام @petfeature است.

قوانین مهم:
- فارسی بنویس. لحن صمیمی و حرفه‌ای.
- خروجی باید متن ساده (plain text) باشد — بدون هیچ تگ HTML مثل <b>, <a>, <i> و غیره.
- از اموجی برای ساختار و جذابیت استفاده کن.
- پاراگراف‌ها را با یک خط خالی از هم جدا کن.
- حداکثر ۳۰۰ کلمه.
- برای هر محتوای جدید: یک عنوان کوتاه با اموجی، یک جمله توضیح، و لینک کامل در خط بعد.
- در انتها یک جمله دعوت به تعامل اضافه کن.
- هشتگ‌های مرتبط را در انتها بیاور: #یادداشت #کتاب #ابزار
- لینک‌ها را به صورت URL کامل بنویس (https://...) نه به صورت تگ HTML."""

SITE_URL = "https://petfeature.ir"


def _excerpt(text: Optional[str], limit: int = 150) -> str:
    if not text:
        return ""
    text = text.strip()
    return text[:limit] + "…" if len(text) > limit else text


def _build_user_message(new_content: dict) -> str:
    parts = ["محتوای جدیدی که از آخرین خبرنامه منتشر شده:\n"]

    posts = new_content.get("posts", [])
    if posts:
        parts.append("یادداشت‌ها:")
        for p in posts:
            excerpt = _excerpt(p.body or "")
            parts.append(f"- {p.title} — {excerpt} — {SITE_URL}/blog/{p.slug}/")

    books = new_content.get("books", [])
    if books:
        parts.append("\nکتاب‌ها:")
        for b in books:
            excerpt = _excerpt(b.note or "")
            parts.append(f"- {b.title} — {excerpt} — {SITE_URL}/library/{b.slug}/")

    tool_list = new_content.get("tools", [])
    if tool_list:
        parts.append("\nابزارها:")
        for t in tool_list:
            excerpt = _excerpt(t.short_description or "")
            parts.append(f"- {t.title} — {excerpt} — {SITE_URL}/tools/{t.slug}/")

    parts.append("\nیک پیش‌نویس خبرنامه برای کانال تلگرام بنویس.")
    return "\n".join(parts)


async def _call_gapgpt(user_message: str) -> Optional[str]:
    """Call GapGPT OpenAI-compatible API. Returns generated text or None on failure."""
    headers = {
        "Authorization": f"Bearer {settings.gapgpt_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.gapgpt_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 1024,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.gapgpt_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            data = response.json()
            if response.status_code == 200:
                return data["choices"][0]["message"]["content"]
            logger.error("GapGPT API error: status=%s body=%s", response.status_code, data)
            return None
    except Exception as exc:
        logger.error("GapGPT call exception: %s", exc)
        return None


async def collect_new_content(session: AsyncSession) -> Optional[dict]:
    """
    Fetch content published since the last sent campaign.
    Returns dict with posts/books/tools lists, or None if nothing new.
    """
    last = await newsletter_service.last_sent_campaign(session)
    since: Optional[datetime] = last.sent_at if last else None

    all_posts = await post_service.list_posts(session, published_only=True)
    all_books = await book_service.list_books(session, status="published")
    all_tools = await tool_service.list_tools(session, published_only=True)

    if since:
        # Make since offset-aware for comparison
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

        def after_since(dt: Optional[datetime]) -> bool:
            if not dt:
                return False
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt > since

        new_posts = [p for p in all_posts if after_since(p.updated_at)]
        new_books = [b for b in all_books if after_since(b.updated_at)]
        new_tools = [t for t in all_tools if after_since(t.updated_at)]
    else:
        # First newsletter — include all published content
        new_posts = list(all_posts)
        new_books = list(all_books)
        new_tools = list(all_tools)

    if not new_posts and not new_books and not new_tools:
        return None

    return {"posts": new_posts, "books": new_books, "tools": new_tools}


async def generate_draft(session: AsyncSession) -> Optional[str]:
    """
    Collect new content and call GapGPT to generate a Persian newsletter draft.
    Returns the draft text, empty string if no new content, or None on API failure.
    Caller should check settings.gapgpt_api_key before calling.
    """
    new_content = await collect_new_content(session)
    if new_content is None:
        return ""  # sentinel: no new content

    user_message = _build_user_message(new_content)
    return await _call_gapgpt(user_message)
