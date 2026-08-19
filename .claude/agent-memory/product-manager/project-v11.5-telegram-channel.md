---
name: project-v11.5-telegram-channel
description: v11.5 Telegram Channel shipped July 2026 (commit 4a4cb8c) — @petfeature join strip in footer; email newsletter later removed entirely
metadata:
  type: project
---

v11.5 **SHIPPED** (commit 4a4cb8c, July 2026). Replaced the public footer email form with a Telegram channel join strip pointing to `https://t.me/petfeature`. The email newsletter was subsequently removed from the product entirely (July 2026) — see [[project-email-newsletter-removed]].

**Status:** Shipped

**Why Telegram over email:** Iranian market. Channel open rates ~60–80% vs email ~15–25%. No payment friction, no deliverability issues, no provider dependency.

**Scope:** Template + CSS only. No new model, migration, or route.

**Channel:** @petfeature → `https://t.me/petfeature`

**Copy (Persian):**
- Headline: با پت فیچر در تلگرام باشید
- Body: یادداشت تازه، کتاب جدید، ابزار کاربردی — هر بار که چیز جدیدی منتشر می‌شه، اول در کانال.
- Button: عضویت در کانال

**Follow-up:** all email subscriber code and the `subscribers` table still need removing.

**How to apply:** Telegram is the only subscription channel. Never add an email subscription form. [[project-email-newsletter-removed]]

**Unlocks:** v13 Telegram digest. [[project-v13-newsletter-bot]]
