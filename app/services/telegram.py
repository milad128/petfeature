"""Telegram Bot API integration — send messages to the channel."""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


async def send_to_channel(text: str) -> bool:
    """
    Send a Telegram HTML-formatted message to the configured channel.
    Returns True on success, False on failure.
    If TELEGRAM_BOT_TOKEN is not set, returns False immediately.
    """
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set — skipping send")
        return False

    url = f"{TELEGRAM_API}/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_channel_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    proxies = {"all://": settings.telegram_proxy} if settings.telegram_proxy else None

    try:
        async with httpx.AsyncClient(timeout=15.0, proxies=proxies) as client:
            response = await client.post(url, json=payload)
            data = response.json()
            if response.status_code == 200 and data.get("ok"):
                return True
            logger.error(
                "Telegram send failed: status=%s body=%s",
                response.status_code,
                data,
            )
            return False
    except Exception as exc:
        logger.error("Telegram send exception: %s", exc)
        return False
