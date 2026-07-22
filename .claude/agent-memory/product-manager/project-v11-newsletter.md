---
name: project-v11-newsletter
description: v11 Newsletter implemented locally July 2026 — footer subscription form + admin subscriber list; code done, not yet committed
metadata:
  type: project
---

v11 PRD written and saved to `docs/product-spec-v11.md` (July 2026). **Status: In Progress — fully implemented in working tree, not yet committed or deployed.**

**Scope:** Subscriber model + footer subscription form (name + email) + admin `/admin/subscribers/` list. No email sending in v11 — collection only.

**Key decisions:**
- Footer strip (Option A) recommended over dedicated page — maximises reach with zero navigation friction
- Single opt-in — lower friction; add double opt-in later if spam becomes a problem
- Duplicate emails show success silently — no email enumeration
- Honeypot + rate limiting (max 3/IP/hour) for spam protection
- Resend recommended as email provider — deferred to v12+ (password reset shares the same provider)
- Admin list is read-only in v11; no unsubscribe/delete action yet

**Data model:** `Subscriber` (id, name, email, subscribed_at, is_active); UNIQUE on email; Alembic migration required.

**How to apply:** v11 is independent of v12 (auth). Can ship before or after. Coordinate email provider choice with v12 password reset. [[project-v12-user-auth]]
