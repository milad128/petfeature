# Product Spec v13 — Newsletter AI Draft Agent (دستیار هوش مصنوعی خبرنامه)

**Version:** v13
**Status:** Shipped
**Author:** Milad Mirzaei
**Date:** July 2026
**Depends on:** v11.5 (Telegram channel live), v12 (optional — independent)

---

## Overview

v13 adds an AI-powered newsletter workflow to the admin CMS. Milad opens the newsletter section, clicks one button, and Claude generates a Persian newsletter draft based on content published since the last send. He reviews, edits, and sends it to @petfeature.

Two components:
1. **Newsletter campaign log** — records every newsletter sent; gives the AI a reference point for "what's new"
2. **AI draft agent** — queries new content, passes it to Claude Haiku, returns an editable Persian Telegram-formatted draft

No auto-posting on publish. No per-content-item buttons. Admin initiates every send deliberately.

---

## Problem Statement

After v11.5, visitors can join @petfeature. But writing a newsletter digest — synthesising what's new across posts, books, and tools — is time-consuming. The admin knows the content exists but has to manually scan and summarise it.

v13 eliminates the writing step: one click, Claude produces a ready-to-edit Persian draft that covers exactly what's new since the last campaign.

---

## Target Users

- **Milad (admin):** When it's time for a newsletter, one click produces a draft in Persian — review, adjust, send. No blank-page problem.
- **Channel subscribers:** Receive a well-written, timely digest in Persian.

---

## User Stories

- *As admin, I want to see a log of all past newsletters so that I know what was already sent and when.*
- *As admin, I want to save draft newsletters before sending so that I can review and edit them before they go out.*
- *As admin, I want to click one button to generate a newsletter draft so that I don't have to write it from scratch.*
- *As admin, I want the AI draft to cover only content published since the last newsletter so that I don't repeat what subscribers already received.*
- *As admin, I want to edit the AI draft before sending so that I have full control over what goes out.*
- *As admin, I want to write a newsletter manually (without AI) so that I can send announcements not tied to specific new content.*

---

## Acceptance Criteria

### A — Newsletter campaign log

- [ ] Admin page at `/admin/newsletters/` lists all campaigns in reverse chronological order
- [ ] Each row shows: Jalali send date, first 80 chars of body, status (پیش‌نویس / ارسال شده)
- [ ] Clicking a row opens the campaign detail — full body and send timestamp
- [ ] Draft campaigns shown at the top of the list, clearly labelled
- [ ] Admin can delete a draft campaign; sent campaigns cannot be deleted
- [ ] Admin sidebar shows "خبرنامه" nav item; sub-items: "لاگ خبرنامه‌ها" + "خبرنامه جدید"

### B — AI draft agent

- [ ] `/admin/newsletters/new/` shows two entry points: "ایجاد پیش‌نویس با هوش مصنوعی" and "نوشتن دستی"
- [ ] Clicking "ایجاد پیش‌نویس" triggers POST to `/admin/newsletters/draft/ai/`
- [ ] System queries DB for all Posts, Books, and Tools published **after** `sent_at` of the most recent sent campaign
- [ ] If no sent campaign exists yet → includes all published content (first newsletter scenario)
- [ ] If no new content found since last send → shows: "محتوای جدیدی از آخرین خبرنامه منتشر نشده است." and stops
- [ ] New content list (title + excerpt per item) is passed to Claude Haiku with the system prompt
- [ ] Claude returns a Persian newsletter draft formatted for Telegram HTML (`parse_mode=HTML`)
- [ ] Draft is saved to `NewsletterCampaign` (status=`draft`) and loaded into the compose textarea
- [ ] If `ANTHROPIC_API_KEY` is not set, AI button is hidden — no 500 errors; manual compose still works

### C — Compose panel (shared by AI draft and manual)

- [ ] Editable textarea pre-filled with AI draft (or blank for manual)
- [ ] Character counter shown (Telegram limit: 4096 chars)
- [ ] "ذخیره پیش‌نویس" — saves to DB (status=`draft`), redirects to campaign log
- [ ] "ارسال به کانال" — posts to Telegram, updates campaign status to `sent`, records `sent_at`
- [ ] On send success: flash "پیام با موفقیت ارسال شد", redirect to `/admin/newsletters/`
- [ ] On send failure: flash "ارسال ناموفق — لطفاً دوباره تلاش کنید", stay on compose page; draft preserved

### D — Configuration

- [ ] New env vars: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID` (default: `@petfeature`), `ANTHROPIC_API_KEY`
- [ ] If `TELEGRAM_BOT_TOKEN` not set → send button disabled, shows warning; draft/save still works
- [ ] If `ANTHROPIC_API_KEY` not set → AI draft button hidden; manual compose unaffected

---

## Data Model

### `NewsletterCampaign`

```python
class NewsletterCampaign(Base):
    __tablename__ = "newsletter_campaigns"

    id: int (PK)
    body: str (Text)          # full Telegram message body
    status: str               # "draft" | "sent"
    created_at: datetime
    sent_at: datetime | None  # null for drafts
```

**Migration required:** `alembic revision --autogenerate -m "add newsletter_campaigns table"`

---

## AI Agent Design

### System prompt (sent to Claude)

```
تو دستیار نویسنده خبرنامه پت‌فیچر هستی — یک دانشنامه فارسی برای مدیران محصول.
وظیفه‌ات نوشتن یک پیام خبرنامه کوتاه و جذاب برای کانال تلگرام @petfeature است.

قوانین:
- فارسی بنویس. لحن صمیمی و حرفه‌ای.
- خروجی را با parse_mode=HTML تلگرام فرمت کن (<b>, <a>, \n\n برای پاراگراف).
- حداکثر ۳۰۰ کلمه.
- برای هر محتوای جدید یک بند کوتاه بنویس: عنوان، یک جمله توضیح، لینک.
- در انتها یک جمله دعوت به تعامل اضافه کن.
- از هشتگ‌های مناسب استفاده کن: #یادداشت #کتاب #ابزار
```

### User message (generated dynamically)

```
محتوای جدیدی که از آخرین خبرنامه منتشر شده:

یادداشت‌ها:
- [عنوان] — [خلاصه ۱۵۰ کاراکتری] — https://petfeature.ir/blog/[slug]/

کتاب‌ها:
- [عنوان] — [توضیح کوتاه] — https://petfeature.ir/library/[slug]/

ابزارها:
- [عنوان] — [توضیح کوتاه] — https://petfeature.ir/tools/[slug]/

یک پیش‌نویس خبرنامه برای کانال تلگرام بنویس.
```

### Claude model

`claude-haiku-4-5` — fast (~2s), cheap, sufficient for Persian digest summarisation.

### Python sketch

```python
# app/services/newsletter_ai.py
import anthropic
from app.core.config import settings

async def generate_draft(new_content: dict) -> str | None:
    if not settings.anthropic_api_key:
        return None
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    user_msg = build_user_message(new_content)
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return message.content[0].text
```

---

## Technical Design

### New files

| File | Purpose |
|------|---------|
| `app/models/newsletter.py` | `NewsletterCampaign` model |
| `app/services/telegram.py` | `send_to_channel(text)` — httpx POST to Bot API |
| `app/services/newsletter_ai.py` | `generate_draft(new_content)` — Claude integration |
| `app/templates/admin/newsletters_list.html` | Campaign log page |
| `app/templates/admin/newsletter_compose.html` | Compose + AI draft page |

### Modified files

| File | Change |
|------|--------|
| `app/core/config.py` | Add `telegram_bot_token`, `telegram_channel_id`, `anthropic_api_key` |
| `app/admin/routes.py` | Newsletter CRUD routes + AI draft route |
| `app/templates/admin/base.html` | "خبرنامه" nav section with sub-items |
| `alembic/env.py` | Import `NewsletterCampaign` |

### One-time bot setup

1. Create bot via @BotFather → copy `TELEGRAM_BOT_TOKEN`
2. Add bot as admin to @petfeature channel (post messages permission only)
3. Set env vars in Hamravesh: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID=@petfeature`, `ANTHROPIC_API_KEY`

---

## Admin UI Flow

```
/admin/newsletters/             ← campaign log (sent + drafts, reverse chrono)
    [+ خبرنامه جدید] ─────────→ /admin/newsletters/new/
                                    ├── [ایجاد پیش‌نویس با هوش مصنوعی]
                                    │       └── POST /admin/newsletters/draft/ai/
                                    │               → query new content since last send
                                    │               → call Claude Haiku
                                    │               → save as draft
                                    │               → redirect to compose with draft loaded
                                    └── [نوشتن دستی] → blank textarea

                                Compose panel:
                                ┌────────────────────────────────────┐
                                │ [textarea — editable draft or blank] │
                                │ ۲۴۳ / ۴۰۹۶ کاراکتر                │
                                │                                     │
                                │  [ذخیره پیش‌نویس]  [ارسال به کانال] │
                                └────────────────────────────────────┘
```

---

## Out of Scope (v13)

| Item | Reason |
|------|--------|
| Auto-post on content publish | Removed — admin sends deliberately |
| Per-item "ارسال به کانال" button | Removed — same reason |
| Scheduling (send at specific time) | Adds cron complexity; v14+ |
| Image/media in newsletter | `sendPhoto` API; v14+ |
| Retry queue for failed sends | Log only; v14+ |
| Multiple Telegram channels | Single channel only |
| AI model selection in UI | Hardcoded to Haiku; v14+ |
| Reading List (v14+) | Independent epic |

---

## NFRs

- `TELEGRAM_BOT_TOKEN` and `ANTHROPIC_API_KEY` must never appear in HTML, logs, or templates
- AI draft generation should complete in < 5 seconds (Haiku is fast)
- All admin UI must be RTL Persian
- Message HTML must be well-formed — escape `<`, `>`, `&` in user-generated content

---

## Open Questions

| Question | Recommendation |
|----------|---------------|
| Should admin be able to regenerate the AI draft (discard + retry)? | Yes — delete draft campaign, re-trigger |
| Should the AI draft include the previous newsletter body as context to avoid repetition? | Nice-to-have — pass last `sent` campaign body; open for implementation |
| Should the compose panel show a Telegram message preview? | Low priority — textarea sufficient for v13 |

---

## Effort Estimate

| Task | Estimate |
|------|----------|
| `NewsletterCampaign` model + migration | 1 hour |
| `app/services/telegram.py` (send_to_channel) | 1 hour |
| Campaign log page (`/admin/newsletters/`) | 2 hours |
| Compose panel (manual + draft UI, save + send) | 2 hours |
| `app/services/newsletter_ai.py` (Claude + prompt) | 3 hours |
| AI draft route + new content diff query | 2 hours |
| Admin nav + config + env vars | 1 hour |
| **Total** | **~2 days** |
