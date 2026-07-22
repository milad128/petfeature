# Product Spec v13 — Newsletter Bot (ربات خبرنامه تلگرام)

**Version:** v13
**Status:** Backlog
**Author:** Milad Mirzaei
**Date:** July 2026
**Depends on:** v11.5 (Telegram channel live), v12 (optional — independent)

---

## Overview

v13 wires a Telegram Bot to the admin CMS. When Milad publishes new content (Post, Book, or Tool), a formatted message is sent automatically to the @petfeature Telegram channel. An admin compose panel also allows sending custom one-off messages to the channel.

No third-party library is needed — a single `httpx` POST to the Telegram Bot API is sufficient.

---

## Problem Statement

After v11.5, visitors can join @petfeature. But the channel is only useful if it gets updated. Today, publishing content on petfeature.ir requires a separate manual step to notify the Telegram audience. This friction means notifications get skipped and the channel goes silent.

v13 closes the loop: publishing content on the site automatically notifies the Telegram channel.

---

## Target Users

- **Milad (admin):** Publish once, notify everywhere — no manual Telegram posting needed.
- **Channel subscribers:** Receive a timely, well-formatted update when new content drops.

---

## User Stories

- *As admin, I want new posts/books/tools to automatically notify the Telegram channel so that I don't have to post manually after publishing.*
- *As admin, I want a "ارسال به کانال" button on each content page so that I can trigger a notification on demand (e.g. for re-posts or corrections).*
- *As admin, I want a compose panel to write a custom message and send it to the channel so that I can post announcements not tied to a specific content item.*
- *As a channel subscriber, I want to receive a clear, well-formatted message with a direct link to the new content so that I can read it in one tap.*

---

## Acceptance Criteria

### A — Auto-post on publish

- [ ] When admin sets a Post's status to `published` (new or edit), a Telegram message is sent to the channel
- [ ] When admin publishes a new Book (status → published), a Telegram message is sent
- [ ] When admin publishes a new Tool (status → published), a Telegram message is sent
- [ ] Auto-post fires **only on the first publish** — editing an already-published item does not re-send
- [ ] If the Telegram API call fails (network error, bad token), the publish action still succeeds — Telegram failure must never block content publishing
- [ ] Failed sends are logged to the app error log with enough context to retry manually

### B — On-demand "ارسال به کانال" button

- [ ] Post detail page in admin has a "ارسال به کانال تلگرام" button (only visible for published posts)
- [ ] Same button on Book and Tool admin detail pages
- [ ] Clicking the button sends the standard auto-post message for that item
- [ ] Button shows a flash confirmation: "پیام با موفقیت ارسال شد" or "ارسال ناموفق — لطفاً دوباره تلاش کنید"
- [ ] No rate limiting in v13 — admin is trusted; spam prevention is not in scope

### C — Custom message compose panel

- [ ] Admin page at `/admin/telegram/compose/` with a textarea and a "ارسال به کانال" button
- [ ] Supports plain text; no rich formatting in v13 (Markdown/HTML formatting is v14+)
- [ ] Character counter shown (Telegram limit: 4096 chars)
- [ ] Preview section shows what the message will look like (plain text render)
- [ ] Confirmation flash on success/failure

### D — Configuration

- [ ] Two new env vars: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`
- [ ] `TELEGRAM_CHANNEL_ID` can be a channel username (`@petfeature`) or numeric chat ID
- [ ] If `TELEGRAM_BOT_TOKEN` is not set, all Telegram features are silently disabled — no 500 errors
- [ ] Admin sidebar shows "تلگرام" nav item linking to the compose panel (only when bot is configured)
- [ ] Health check at `/api/v1/health` does **not** test Telegram connectivity

---

## Message Format (Auto-post)

Telegram HTML formatting (`parse_mode=HTML`):

```
📌 <b>[عنوان محتوا]</b>

[خلاصه یا توضیح کوتاه — اول ۱۵۰ کاراکتر از متن یا توضیح ادمین]

🔗 <a href="https://petfeature.ir/[path]/[slug]/">مطالعه در پت فیچر</a>

#[نوع_محتوا]
```

**Content type tags:**
- Post → `#یادداشت`
- Book → `#کتاب`
- Tool → `#ابزار`

---

## Technical Design

### Bot setup (one-time, manual)
1. Create bot via @BotFather → get `TELEGRAM_BOT_TOKEN`
2. Add bot as admin to @petfeature channel (post permission only)
3. Set `TELEGRAM_CHANNEL_ID=@petfeature` in Hamravesh env vars

### API call (no library)
```python
# app/services/telegram.py
import httpx
from app.core.config import settings

async def send_to_channel(text: str) -> bool:
    if not settings.telegram_bot_token:
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_channel_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=payload)
            return r.status_code == 200
    except Exception:
        return False  # never raise; log instead
```

### New config keys (`app/core/config.py`)
```python
telegram_bot_token: str | None = None
telegram_channel_id: str = "@petfeature"
```

### New files
| File | Purpose |
|------|---------|
| `app/services/telegram.py` | `send_to_channel(text)` async function |
| `app/templates/admin/telegram_compose.html` | Compose panel template |

### Modified files
| File | Change |
|------|--------|
| `app/core/config.py` | Add `telegram_bot_token`, `telegram_channel_id` |
| `app/admin/routes.py` | Call `telegram.send_to_channel()` on publish; add compose route; add on-demand button routes |
| `app/templates/admin/base.html` | Add "تلگرام" nav item |
| `app/templates/admin/post_detail.html` | Add "ارسال به کانال" button |
| `app/templates/admin/book_detail.html` | Add "ارسال به کانال" button |
| `app/templates/admin/tool_detail.html` | Add "ارسال به کانال" button |

### No migration needed
No new DB tables. Sent message history is not persisted in v13 — add a `TelegramMessage` log table in v14+ if needed.

---

## Out of Scope (v13)

| Item | Reason |
|------|--------|
| Telegram Markdown/MarkdownV2 formatting | Parse_mode=HTML covers 90% of needs; MarkdownV2 escaping is error-prone |
| Message send history / log table | Low value in v1 — add in v14+ if needed |
| Scheduling (send at a specific time) | Adds complexity; out of scope |
| Subscriber tracking via bot | No bot inbox in v13; channel-only |
| Reading List (v14) | Independent epic |
| Rate limiting the on-demand button | Admin is trusted |
| Telegram login / user auth via Telegram | v12+ concern |

---

## NFRs

- Telegram API failure must never block content publishing (fire-and-forget pattern)
- Bot token must never appear in templates, logs, or HTML responses
- All admin-facing UI must be RTL Persian
- Message text must be well-formed HTML (no unescaped `<`, `>`, `&`)

---

## Open Questions

| Question | Status |
|----------|--------|
| Should the auto-post message include the book cover image (Telegram supports `sendPhoto`)? | Open — `sendPhoto` is more complex; decide during implementation |
| Should failed sends be retried automatically, or just logged? | Recommend: log only in v13; retry queue in v14+ |
| Should admin be able to edit the auto-generated message before sending? | Nice-to-have — open |

---

## Effort Estimate

| Task | Estimate |
|------|----------|
| `app/services/telegram.py` | 2 hours |
| Config keys + env setup | 1 hour |
| Auto-post hook on publish (Post, Book, Tool) | 3 hours |
| On-demand button (3 content types) | 2 hours |
| Compose panel (template + route) | 3 hours |
| Admin nav + conditional display | 1 hour |
| **Total** | **~1.5 days** |
