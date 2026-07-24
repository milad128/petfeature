---
name: project-v11.5-telegram-channel
description: v11.5 Telegram Channel shipped July 2026 (commit 4a4cb8c) — replaced footer email form with @petfeature join strip; subscriber admin page kept live
metadata:
  type: project
---

v11.5 **SHIPPED** (commit 4a4cb8c, July 2026). Replaced the public footer email form with a Telegram channel join strip pointing to `https://t.me/petfeature`. v11 Subscriber admin page and DB table remain live.

**Status:** Shipped

**Why Telegram over email:** Iranian market. Channel open rates ~60–80% vs email ~15–25%. No payment friction, no deliverability issues, no provider dependency.

**Scope:** Template + CSS only. No new model, migration, or route.

**Channel:** @petfeature → `https://t.me/petfeature`

**Copy (Persian):**
- Headline: با پت فیچر در تلگرام باشید
- Body: یادداشت تازه، کتاب جدید، ابزار کاربردی — هر بار که چیز جدیدی منتشر می‌شه، اول در کانال.
- Button: عضویت در کانال

**Prerequisite:** Revert all v11 email subscriber code before committing v11.5.

**How to apply:** When implementing v11.5, remind engineer to revert subscriber model/service/schema/migration/admin page/routes before touching base.html. [[project-v11-newsletter]]

**Unlocks:** v13 Newsletter Bot (Telegram auto-post). [[project-v13-newsletter-bot]]
