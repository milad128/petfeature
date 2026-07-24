# Product Spec v11.5 — Telegram Channel Integration (کانال تلگرام)

**Version:** v11.5
**Status:** Shipped (commit 4a4cb8c)
**Author:** Milad Mirzaei
**Date:** July 2026
**Note:** v11 email subscriber model + admin page remain in the codebase (shipped in 8ffcb9e). v11.5 replaced the public footer form only — the `Subscriber` DB table and `/admin/subscribers/` are still live.
**Depends on:** v1–v10

---

## Overview

v11 (email newsletter) is cancelled. The Iranian audience is on Telegram — a channel reach of 60–80% open rate is structurally better than email for this market. v11.5 replaces the email subscription footer strip with a Telegram channel join section pointing to @petfeature.

This is a pure frontend change: no new model, no migration, no new route. The v11 email subscriber code in the working tree must **not be committed** — it is superseded by this spec.

---

## Problem Statement

Petfeature.ir has no audience distribution channel. Visitors read content but have no way to stay updated when new books, posts, or tools are published. Email was the planned solution (v11) but is a poor fit for the Iranian market: low open rates, provider payment friction, and deliverability complexity.

---

## Target User

Visitors to petfeature.ir — Persian-speaking Product Managers — who want to be notified when new content is published. They are already on Telegram daily.

---

## User Stories

- *As a visitor, I want to join the petfeature Telegram channel so that I receive updates when new content is published, without filling out a form.*
- *As the site owner, I want visitors to find the Telegram channel easily from any page so that I grow the channel audience over time.*

---

## Acceptance Criteria

### Footer strip (all public pages)
- [ ] The email subscription form (`nls-strip` section in `base.html`) is removed entirely
- [ ] A Telegram join section replaces it in the same footer area
- [ ] The section displays: a short Persian headline, a one-line description, and a "عضویت در کانال" button
- [ ] The button links to `https://t.me/petfeature` and opens in a new tab (`target="_blank" rel="noopener"`)
- [ ] The channel handle `@petfeature` is visible as supporting text
- [ ] Design is RTL-consistent; button is styled to match the site's existing button palette
- [ ] Section is responsive — stacks vertically on mobile

### Code cleanup (prerequisite — do before committing v11.5)
- [ ] Revert / do not commit: `app/models/subscriber.py`
- [ ] Revert / do not commit: `app/schemas/subscriber.py`
- [ ] Revert / do not commit: `app/services/subscribers.py`
- [ ] Revert / do not commit: `alembic/versions/4716ef14fd90_add_subscribers_table.py`
- [ ] Revert / do not commit: `app/templates/admin/subscribers_list.html`
- [ ] Revert subscriber route additions from `app/web/routes.py` and `app/admin/routes.py`
- [ ] Revert admin nav link for "مشترکین" from `app/templates/admin/base.html`

### No regressions
- [ ] All other footer content (brand name, nav links) remains unchanged
- [ ] No broken routes (`/subscribe/` must not exist)
- [ ] `alembic upgrade head` succeeds with no new migration

---

## Out of Scope

| Item | Reason |
|------|--------|
| Subscriber count display | No data to show |
| Telegram Bot auto-posting | v13 |
| Email subscription | Cancelled permanently |
| Analytics on channel clicks | Nice-to-have; add later |

---

## Content Copy (Persian)

**Headline:** با پت فیچر در تلگرام باشید
**Body:** یادداشت تازه، کتاب جدید، ابزار کاربردی — هر بار که چیز جدیدی منتشر می‌شه، اول در کانال.
**Button:** عضویت در کانال
**Supporting text:** @petfeature

---

## Implementation Note

**Effort:** ~2 hours (template edit + CSS)
**Migration:** None
**Env vars:** None
**Files to touch:** `app/templates/base.html`, `app/static/css/main.css`

---

## Open Questions

| Question | Status |
|----------|--------|
| Should the Telegram section also appear in the site header/nav as an icon link? | Open — low effort, decide during implementation |
| Should we add a Telegram icon in the footer brand area? | Open |
