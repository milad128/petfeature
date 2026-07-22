---
name: project-v13-newsletter-bot
description: v13 Newsletter Bot — Telegram Bot auto-posts to @petfeature on new content publish; admin compose panel; backlog July 2026
metadata:
  type: project
---

v13 wires a Telegram Bot to the admin CMS. Auto-posts to @petfeature channel when admin publishes Post, Book, or Tool. Admin compose panel for custom messages.

**Status:** Backlog

**Channel:** @petfeature

**Key decisions:**
- Auto-post fires only on FIRST publish — not on edit of already-published content
- Telegram API failure never blocks publishing (fire-and-forget; errors logged only)
- `parse_mode=HTML` for message formatting (not MarkdownV2 — too complex to escape)
- No library — single `httpx` POST to `https://api.telegram.org/bot{token}/sendMessage`
- If `TELEGRAM_BOT_TOKEN` not set, all features silently disabled (no errors)
- No DB table for sent messages in v13 — log table deferred to v14+

**New env vars:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID` (default: `@petfeature`)

**New files:** `app/services/telegram.py`, `app/templates/admin/telegram_compose.html`

**Message format:** Emoji + bold title + 150-char excerpt + link + content-type hashtag (`#یادداشت`, `#کتاب`, `#ابزار`)

**Effort:** ~1.5 days

**Depends on:** v11.5 (channel must be live). [[project-v11.5-telegram-channel]]

**How to apply:** When engineer asks about newsletter/Telegram sending, refer to this spec. Bot setup is manual (one-time via @BotFather). Remind to add bot as channel admin with post permission.
