# Product Spec v11 — Newsletter (مشترکین)

**Version:** v11  
**Status:** Shipped (commit 8ffcb9e)  
**Author:** Milad Mirzaei  
**Date:** July 2026  
**Depends on:** v1–v10

---

## Overview

v11 adds an email newsletter subscription feature. Visitors can subscribe with their name and email; Milad can manage the subscriber list from the admin panel and send updates when new content is published.

This is a pure audience-growth feature — no login required, no personalisation, no content gating. It is fully independent of the User Registration epic (v12).

---

## Problem Statement

petfeature.ir has no mechanism for visitors to stay updated. When a new book note, post, or tool is published, interested readers have no way to know unless they happen to revisit the site. A newsletter subscription captures that intent at low friction — one form, two fields — and gives Milad a direct channel to his audience.

---

## Target Users

- **Subscriber (visitor):** A Persian-speaking PM professional who finds the site valuable and wants to be notified of new content. No account required.
- **Admin (Milad):** Needs to see who has subscribed and export the list for use with an email provider.

---

## User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| U1 | Visitor | Enter my name and email to subscribe to the newsletter | I'm notified when new content is published |
| U2 | Visitor | See a clear success message after subscribing | I know my subscription was received |
| U3 | Visitor | Not see an error if I accidentally submit the same email twice | The experience is frictionless |
| U4 | Visitor | See a newsletter CTA without navigating away from the page I'm on | I can subscribe wherever I am on the site |
| U5 | Admin | View all subscribers with name, email, and subscribe date | I know the size and composition of my audience |
| U6 | Admin | See subscriber count at a glance | I can track growth without counting rows |
| U7 | Admin | Export or copy subscriber emails | I can import the list into my email provider |

---

## Data Model

**New model: `Subscriber`**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | Integer | PK, auto-increment | |
| `name` | String(200) | NOT NULL | Display name, used in email greetings |
| `email` | String(300) | NOT NULL, UNIQUE | Lowercased before save |
| `subscribed_at` | DateTime | NOT NULL, server_default=now() | |
| `is_active` | Boolean | NOT NULL, default=True | Soft-delete / unsubscribe flag |

**Alembic migration required** — creates the `subscribers` table.

**Email uniqueness:** enforced at DB level (UNIQUE constraint) and at service level. Duplicate submissions are detected and handled silently (no error shown to the visitor — see AC below).

---

## Acceptance Criteria

### Subscription form

**Placement options (decide before implementation):**

| Option | Description |
|--------|-------------|
| A — Footer strip (recommended) | A full-width "عضو خبرنامه شو" section at the bottom of `base.html`, visible on every public page |
| B — Dedicated page (`/newsletter/`) | A standalone subscription page; footer links to it |
| C — Both | Footer strip + dedicated page (strip posts to `/newsletter/`) |

**Recommendation: Option A** — the footer strip maximises reach with zero navigation friction. A dedicated page can be added later as a landing target for external links.

**Form fields:**

1. نام (text, required, max 200 chars)
2. ایمیل (email input, required, max 300 chars)
3. Submit button: "عضو شو"

**On valid submission:**

4. Email is lowercased and trimmed before processing.
5. If the email is new: a `Subscriber` record is created with `is_active=True`. Page re-renders (or redirects) with a success message: "ممنون! اشتراک شما ثبت شد."
6. If the email already exists (duplicate): no new record is created, no error is shown. The same success message is displayed — the subscriber simply gets no feedback that they were already subscribed. This prevents email enumeration.
7. If the form is submitted with missing or invalid fields: an inline Persian validation error is shown. No record is created.

**Spam protection:**

8. A honeypot hidden field (`<input type="text" name="website" style="display:none">`) is included. If the honeypot field is non-empty on submission, the request is silently dropped (no record, success message shown — bots see success to avoid retry loops).
9. Rate limiting: max 3 subscription attempts per IP per hour (consistent with the contact form rate limiting pattern already in the codebase).

### Admin subscriber list (`GET /admin/subscribers/`)

10. A new **"مشترکین"** entry appears in the admin sidebar.
11. The page shows a table of all active subscribers (`is_active=True`), sorted by `subscribed_at` descending (newest first). Columns:

| Column | Content |
|--------|---------|
| نام | `name` |
| ایمیل | `email` (LTR, `dir="ltr"`) |
| تاریخ عضویت | Jalali formatted date |

12. A summary line above the table: "**X** مشترک فعال" (total active subscriber count).
13. Pagination: if count exceeds 50, paginate with standard admin pagination. Default page size: 50.
14. No delete or edit actions in v11 — read-only list. Unsubscribe management deferred.

### Email provider integration

15. In v11, the site **only collects emails** — it does not send any emails itself. Sending is handled externally by Milad via the email provider of his choice (see Open Questions).
16. The admin subscriber list is the export mechanism — Milad copies emails from the table or queries the DB directly to import into the provider.
17. No API keys, webhooks, or provider SDK integration in v11. This is explicitly deferred to keep scope tight.

---

## Routes

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/newsletter/subscribe` | Accept form submission; validate, deduplicate, save; redirect/re-render with success |
| `GET` | `/admin/subscribers/` | Admin: render subscriber list |

The footer form (Option A) posts directly to `/newsletter/subscribe`. No GET `/newsletter/` route needed unless Option C is chosen.

---

## NFRs

### RTL / Persian
- All form labels, error messages, success messages, and admin UI copy are in Persian and RTL.
- Email addresses and dates are displayed with `dir="ltr"` to preserve LTR rendering.

### Security
- Email is lowercased and stripped on input — never stored as-is from user input.
- Honeypot field is present on all form renders.
- Rate limiting prevents abuse of the subscription endpoint.
- No subscriber data is exposed to other visitors — admin-only access.

### Performance
- Subscription insert is a single DB write. No external API calls in v11.
- Admin list paginates at 50 rows — no full table load.

---

## Out of Scope (v11)

- Sending newsletter emails from the site (deferred — needs email provider SDK integration).
- Double opt-in / email confirmation flow (deferred — increases friction; revisit if spam becomes a problem).
- Unsubscribe link in emails (deferred — no emails sent in v11).
- Admin unsubscribe / delete subscriber action (deferred).
- Subscriber tags or segments.
- Integration with Mailchimp, Resend, Buttondown, or any external provider API (deferred to v12+).
- Public subscriber count display ("X نفر عضو شده‌اند").

---

## Open Questions

| Question | Decision |
|----------|----------|
| Email provider? | Deferred — v11 only collects; no provider integration yet. Resend is the recommended choice for v12 (simplest API, generous free tier, SMTP fallback). |
| Single opt-in or double opt-in? | Single opt-in for v11 — lower friction, appropriate for a personal site at this scale. If spam becomes an issue, add confirmation email in v12. |
| Footer strip or dedicated page? | **Footer strip (Option A) recommended.** Decide before implementation. |
| Should admin be able to export as CSV? | Deferred — not in v11. Milad can query the DB directly if needed. |
| Should the newsletter CTA appear in the middle of long blog posts? | Deferred — inline CTAs need content design; keep it in the footer for v11. |

---

## Success Metrics

v11 is done when all of the following are true:

- [ ] `subscribers` table exists in production (migration applied).
- [ ] Subscription form is visible on all public pages (footer strip) or at `/newsletter/`.
- [ ] Valid submission creates a `Subscriber` record and shows the Persian success message.
- [ ] Duplicate email submission shows the success message without creating a duplicate record.
- [ ] Honeypot field is present; filled honeypot silently drops the request.
- [ ] Rate limiting rejects more than 3 submissions per IP per hour.
- [ ] **"مشترکین"** appears in the admin sidebar and links to `/admin/subscribers/`.
- [ ] Admin list shows name, email (LTR), Jalali date, sorted by newest first.
- [ ] Active subscriber count summary is shown above the table.
- [ ] Pagination renders correctly when count exceeds 50.

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Not deployed |
| **Deploy date** | — |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | Unscheduled — pending prioritisation after v10 |

---

*July 2026 — v11 spec written. Unscheduled backlog item.*
