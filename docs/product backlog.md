# Product Backlog — پت فیچر

**Shipped:** v1 Library · v2 Blog · v3 Tools · v4 Book Engagement · v5 About Redesign + Contact · v6 Visitor Analytics · v7 Comment Replies · v8 Content Enhancements · v9 Media Library + Book Link Types + Admin Filters · v11 Newsletter (email subscriber) · v11.5 Telegram Channel (@petfeature join strip)

**Planned:** v10 Post Related Books

See [spec.md](./spec.md) for the versioned roadmap. Nothing below has a committed version or timeline. Items move into a versioned spec when prioritized and scoped.

---

## Epic: Newsletter → Shipped as v11 + v11.5

Both shipped July 2026.

- **v11** (8ffcb9e) — Email subscriber form in footer + admin subscriber list + `Subscriber` model. Email collection kept as secondary channel.
- **v11.5** (4a4cb8c) — Replaced public footer email form with Telegram channel join strip → `@petfeature`. Subscriber admin page remains live.

**Why Telegram primary:** Iranian market open rates ~60–80% vs email ~15–25%. No payment friction, no deliverability issues.

**Next:** v13 Newsletter Bot — Telegram auto-post on publish + AI draft agent (Claude Haiku generates Persian digest from new content diff). See [spec-v13-newsletter-ai-agent.md](./spec-v13-newsletter-ai-agent.md).

---

## Epic: Roadmap (مسیر یادگیری)

A structured, opinionated learning path guiding readers through the library and blog.

| Idea | Description |
|------|-------------|
| **Roadmap page** (`/path/`) | Ordered list of learning steps; intro explaining who the path is for |
| **Path steps** | Each step: title, description, level tag (مقدماتی/میانی/پیشرفته), links to books and posts |
| **Step ordering** | `sort_order` field; admin reorders via form |
| **Admin: Manage steps** | CRUD path steps; assign linked books/posts; reorder |
| **Multiple paths** | One canonical path first; separate paths per role/level later |

**Open questions when scoping:**
- Path shape — linear (1→2→3) or branching by track?
- Level tag taxonomy
- Step card layout — accordion or expanded cards?
- Allow text-only steps (no linked content)?

**Data model:** `PathStep` (title, description, sort_order, level), `path_step_books` M2M, `path_step_posts` M2M

---

## ~~Epic: User Registration + Auth~~ → Scoped as v12

**Moved to spec.** See [spec-v12-user-auth.md](./spec-v12-user-auth.md).

Key decisions recorded: email-only auth (no social login in v12); single opt-in (no email verification); server-side session via signed cookie (no JWT); "مرا به خاطر بسپار" = 30-day cookie; password reset requires email provider (Resend recommended — graceful disable if not configured); social login deferred; ship v12 together with v13 Reading List (auth alone has no user-visible value).

---

## ~~Epic: Reading List~~ → Scoped as v15 (Bookshelf / قفسه کتاب)

**Moved to spec.** See [spec-v15-bookshelf.md](./spec-v15-bookshelf.md).

Key decisions recorded: renamed from "Reading List" to **Bookshelf** (قفسه کتاب); all 3 reading statuses in scope (می‌خواهم بخوانم / در حال خواندن / خواندم); private only (no shareable URL); social proof save count shown on book detail when count ≥ 2; sort by date added only; admin save count column on books list. Blocked on v12 User Auth.

---

## Epic: Book Like

Deferred from v4. Simple engagement signal — no login required.

| Idea | Description |
|------|-------------|
| **Like button on book detail** | Toggle ♥ button; total like count shown; visitor-token dedup |

**Data model:** `BookLike` (book_id, visitor_token, created_at)

---

## Shipped Epics (reference)

| Epic | Version | Notes |
|------|---------|-------|
| Library | v1 | Books, about page, admin CMS |
| Blog | v2 | Posts, ratings, comments, sharing |
| Tools | v3 | PM template library |
| Book Engagement | v4 | Book star ratings + moderated comments |
| About Redesign + Contact | v5 | Hero/experience/bootcamps on About; contact form → DB admin inbox |
| Visitor Analytics | v6 | PageView log, bot filter, admin dashboard (period, top content, referrers, daily table) |
| Comment Replies | v7 | Admin richtext reply on post + book comments; public threaded display |
| Content Enhancements | v8 | Book website links, post related books (admin only), tool downloadable links |
| Media Library + Book Link Types + Admin Filters | v9 | Admin file manager; book link types article/book; admin books filter; cover preview fit; بلاگ→یادداشت rename |

---

## Other Ideas (low priority, unscheduled)

| Idea | Notes |
|------|-------|
| Full-text search across books + posts | Useful once content volume grows; needs UX thought |
| Email notifications on new contact message | Simple SMTP add-on to Contact (v5); pairs with Newsletter email provider |
| Blog post reactions (beyond star rating) | Needs UX definition before scoping |
| User profile / account page | Covered by User Registration epic above |
| English version | Not planned |
| Mobile app | Web-first |

---

*Backlog last updated: July 2026 — v1–v9, v11 (Newsletter), v11.5 (Telegram Channel) shipped; v10 planned; v12 User Auth + v13 Newsletter Bot scoped into specs; Reading List v14+*
