# Product Backlog — پت فیچر

**Shipped:** v1 Library · v2 Blog · v3 Tools · v4 Book Engagement · v5 About Redesign + Contact · v6 Visitor Analytics · v7 Comment Replies · v8 Content Enhancements · v9 Media Library + Book Link Types + Admin Filters

**Planned:** v10 Post Related Books · **v11 Newsletter** (in progress — implemented locally, ready to commit)

See [product-spec.md](./product-spec.md) for the versioned roadmap. Nothing below has a committed version or timeline. Items move into a versioned spec when prioritized and scoped.

---

## ~~Epic: Newsletter~~ → Scoped as v11

**Moved to spec.** See [product-spec-v11.md](./product-spec-v11.md).

Key decisions recorded: footer strip (Option A) recommended; single opt-in; Resend recommended as email provider (deferred to v12+); v11 collects emails only — no sending; duplicate emails show success silently; honeypot + rate limiting for spam protection.

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

**Moved to spec.** See [product-spec-v12.md](./product-spec-v12.md).

Key decisions recorded: email-only auth (no social login in v12); single opt-in (no email verification); server-side session via signed cookie (no JWT); "مرا به خاطر بسپار" = 30-day cookie; password reset requires email provider (Resend recommended — graceful disable if not configured); social login deferred; ship v12 together with v13 Reading List (auth alone has no user-visible value).

---

## Epic: Reading List (لیست مطالعه)

Let registered users build a personal list of books they want to read, are reading, or have finished. The primary "save for later" feature for the site.

| Idea | Description |
|------|-------------|
| **"افزودن به لیست" button on book detail** | Single-click add; button state toggles to "در لیست من" if already added; requires login — unauthenticated users are prompted to register |
| **Reading List page** (`/profile/reading-list/`) | User's personal list of saved books; sorted by date added (newest first) |
| **Reading status** | Optional per-book status: می‌خواهم بخوانم / در حال خواندن / خواندم — lets users track progress |
| **Remove from list** | Remove button on reading list page and/or book detail toggle |
| **Empty state** | "هنوز کتابی به لیستت اضافه نکردی. از کتابخانه شروع کن." with a link to `/library/` |
| **Book count badge** | "X کتاب در لیست" summary on profile page |
| **Admin visibility** | Admin can see aggregate reading list counts per book (how many users saved it) — signals popularity |

**Open questions when scoping:**
- Is reading status (want/reading/read) in scope for v1 reading list, or just a simple saved/unsaved toggle?
- Should the reading list be public (shareable URL) or private by default?
- Should the book detail page show a total "X نفر این کتاب را به لیستشان اضافه کرده‌اند" counter (social proof)?
- Order options on the list page — by date added, by title, by status?

**Data model:** `ReadingListItem` (id, user_id FK→User, book_id FK→Book, status ENUM[want/reading/read], added_at); unique constraint on (user_id, book_id)

**Dependency:** Requires User Registration + Auth epic.

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

*Backlog last updated: July 2026 — v1–v9 shipped; v10 planned; v11 Newsletter implemented locally (ready to commit); v12 User Auth scoped into spec*
