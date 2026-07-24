---
name: project-v13-newsletter-bot
description: v13 Newsletter AI Draft Agent — campaign log (NewsletterCampaign model) + AI draft via Claude Haiku + admin compose panel; no auto-posting; ~2 days; backlog
metadata:
  type: project
---

v13 adds an AI-powered newsletter workflow. Admin initiates every send deliberately — no auto-posting on publish, no per-item send buttons.

**Status:** Backlog

**Channel:** @petfeature

**Two features:**
1. Campaign log at `/admin/newsletters/` — all sent + draft campaigns in `NewsletterCampaign` table
2. AI draft agent — one button queries content published since last sent campaign → passes to Claude Haiku → returns editable Persian Telegram-formatted draft

**Key decisions:**
- NO auto-post on publish (removed by Milad — admin sends deliberately)
- NO per-item "ارسال به کانال" button (removed same reason)
- `parse_mode=HTML` — not MarkdownV2
- No library for Telegram — single `httpx` POST to Bot API
- `anthropic` SDK; model: `claude-haiku-4-5`
- AI diff: query content published AFTER `max(sent_at)` from `NewsletterCampaign`; first run includes everything
- All features gracefully disabled if env vars missing

**New DB model:** `NewsletterCampaign` (id, body, status: draft/sent, created_at, sent_at) — **requires Alembic migration**

**New env vars:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID` (default: @petfeature), `ANTHROPIC_API_KEY`

**Effort:** ~2 days

**Depends on:** v11.5. [[project-v11.5-telegram-channel]]

**How to apply:** When engineer implements v13, remind: (1) bot setup via @BotFather, (2) add bot as channel admin with post permission only, (3) first AI draft run includes all content — expected behaviour.
