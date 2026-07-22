# Product Spec v4 — پت فیچر (Book Engagement)

> **Prerequisite:** [Product Spec v3](./product-spec-v3.md) must be shipped first · **Parent:** [Product overview](./product-spec.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)

## 1. Summary

| Field | Value |
|-------|-------|
| **Version** | v4 — Book Engagement |
| **Status** | Shipped |
| **Goal** | Let visitors rate and discuss library books — no login required |
| **Builds on** | v1 Library (shipped), v2 Blog engagement pattern (PostRating, PostComment) |
| **Epic** | Book Engagement |
| **New in v4** | Star rating on book detail, book comments with admin moderation |

**Scope in one sentence:** Add star ratings and a moderated comment section to every book detail page — following the same visitor-token dedup and admin moderation pattern already shipped in v2 Blog.

---

## 2. Problem & Goals

**Problem:** v1–v3 ship the library but visitors have no way to react to or discuss the books. The admin has no signal about which books readers find most valuable.

**v4 goals**

- **Rate a book** — visitors give a 1–5 star rating; average and vote count are shown
- **Comment on a book** — visitors leave comments; admin moderates before they appear publicly
- **Admin moderation** — pending queue for book comments, consistent with post comment moderation in v2

---

## 3. Actors

| Actor | Role |
|-------|------|
| **Visitor** | All v3 capabilities + rates books, reads and posts book comments |
| **Admin (Milad Mirzaei)** | All v3 admin + moderates book comments |

---

## 4. Information Architecture

No new public routes beyond the existing book detail page. Engagement widgets appear on `/library/{slug}/`.

New admin routes under `/admin/books/comments/`.

---

## 5. Feature Requirements

### 5.1 Book star rating — `/library/{slug}/`

| Element | Detail |
|---------|--------|
| Label | «این کتاب چقدر به‌دردت خورد؟» |
| Input | 5-star selector (★ ★ ★ ★ ★) |
| Display | Average score «میانگین امتیاز: N.N از ۵» + vote count «بر اساس N رای» |
| Post-vote | Thank-you state: «ممنون! ✓» |
| Location | Below the book body, above the comments section |
| Auth | No login — visitor token dedup |
| Dedup | One rating per visitor per book; clicking again updates the existing rating |

**Acceptance criteria:**

- `POST /library/{slug}/rate/` stores or updates a `BookRating` row
- Average and count are recalculated and returned on every submit
- Rating widget shows current average on page load, before the visitor has voted
- Visitor cannot submit without selecting a star value
- Crawler user-agents are silently ignored

---

### 5.2 Book comments — `/library/{slug}/`

| Element | Detail |
|---------|--------|
| Header | «نظرها (N)» — shows approved comment count |
| Comment list | Chronological; each shows: commenter name, Jalali date, body |
| Visible | Approved comments only |
| Empty state | «هنوز نظری ثبت نشده — اول نفر باش!» |
| Form fields | نام (required), ایمیل (optional, never shown publicly), متن نظر (required) |
| Submit button | «ارسال نظر ←» |
| On submit | Success message: «نظرت ثبت شد و پس از بررسی منتشر می‌شه ✓» |
| Spam | Hidden honeypot `website` field + rate limiting per IP (reuse `rate_limit.py`) |
| Moderation | All new comments start as `pending`; none auto-approved |
| Location | Below star rating widget |

**Acceptance criteria:**

- `POST /library/{slug}/comment/` saves `BookComment` with status `pending`
- Author email is stored in DB but never rendered on the public page
- Only `approved` comments are shown on the book detail page
- Honeypot submission is silently discarded (no error shown)
- Rate limiter blocks excessive submissions from the same IP
- Comment timestamps are displayed in Shamsi (Jalali) format

---

### 5.3 Admin: Moderate book comments — `/admin/books/comments/`

| Element | Detail |
|---------|--------|
| Default view | Pending queue |
| Filter | By status: pending / approved / rejected |
| Columns | Book title, commenter name, excerpt, date, status |
| Approve | Comment becomes visible on book detail page |
| Reject | Comment hidden from public; kept in DB |
| Delete | Permanently removed |

**Acceptance criteria:**

- Matches the existing `/admin/posts/comments/` pattern
- Default view shows pending queue
- Admin can filter by status
- Approve / reject / delete actions via POST

---

## 6. Content Model (v4 additions)

New entities on top of the existing `Book` model:

| Entity | Key fields |
|--------|------------|
| **BookRating** | `id`, `book_id` (FK → Book, cascade delete), `visitor_token`, `stars` (1–5), `created_at` |
| **BookComment** | `id`, `book_id` (FK → Book, cascade delete), `author_name`, `author_email` (nullable), `body`, `status` (pending/approved/rejected), `created_at` |

**Constraints:**

- `BookRating`: unique on `(book_id, visitor_token)` — upsert on re-rate
- `BookComment`: no uniqueness — a visitor may comment more than once

**Calculated fields (not stored):**

- `average_rating` — `avg(stars)` from `BookRating` where `book_id` matches
- `rating_count` — `count(*)` from `BookRating` where `book_id` matches
- `approved_comment_count` — `count(*)` from `BookComment` where `book_id` and `status = approved`

**Alembic migration:** `008_add_book_engagement.py`

---

## 7. Routes

| Route | Purpose |
|-------|---------|
| `POST /library/{slug}/rate/` | Submit or update book star rating |
| `POST /library/{slug}/comment/` | Submit book comment (goes to pending) |
| `GET /admin/books/comments/` | List all book comments (default: pending) |
| `POST /admin/books/comments/{id}/approve/` | Approve comment |
| `POST /admin/books/comments/{id}/reject/` | Reject comment |
| `POST /admin/books/comments/{id}/delete/` | Delete comment permanently |

---

## 8. Services

Mirror `app/services/posts.py` patterns:

| Function | Purpose |
|----------|---------|
| `rate_book(db, book_id, visitor_token, stars)` | Upsert `BookRating` |
| `create_book_comment(db, book_id, author_name, email, body)` | Insert `BookComment` (status=pending) |
| `list_book_comments(db, status)` | Admin list with optional status filter |
| `moderate_book_comment(db, comment_id, action)` | approve / reject / delete |

---

## 9. Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| Visitor dedup | Reuse `app/core/visitor.py` — same `visitor_token` cookie as v2 |
| Comment spam | Honeypot field + reuse `app/core/rate_limit.py` |
| Moderation default | All comments start `pending` |
| Jalali dates | Comment timestamps in Shamsi format (reuse `jalali.py`) |
| Mobile | Rating widget and comment form fully responsive |
| Crawler filtering | Reuse `posts.is_crawler_user_agent` logic on rating route |

---

## 10. Out of Scope (v4)

| Item | Notes |
|------|-------|
| Book like (♥ reaction) | Deferred to backlog — star rating covers the engagement signal |
| Like/rating badges on library grid | Defer until engagement data exists |
| Email notifications on new comment | Nice-to-have — backlog |
| Comment replies / threads | Flat comments only, consistent with v2 |
| User login gating | Not planned — visitor-token dedup only |
| Book share buttons | Not part of engagement epic |

---

## 11. Open Questions (resolved in implementation)

| # | Question | Resolution |
|---|----------|------------|
| 1 | Email field on comment form — required, optional, or hidden? | Optional — implemented to match v2 post comment pattern |
| 2 | Show rating widget before any votes exist? | Yes — empty state shown, invites first rating |
| 3 | Show rating average on library grid cards? | Deferred — not shown on grid; only on book detail page |
| 4 | Admin nav: where does "Book Comments" appear? | Under کتابخانه section as «نظرها», consistent with Blog → نظرها |

---

## 12. Dependency on v3

v4 assumes v3 provides:

- Library with slug-based book URLs
- Admin CMS with book CRUD
- Visitor token infrastructure (`visitor.py`) and rate limiting (`rate_limit.py`) from v2

---

## 13. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Rating participation rate (ratings / book page views) | Measures engagement depth |
| Average book rating | Quality signal for admin |
| Comments per book | Discussion depth |
| Comment moderation queue clearance time | Admin keeps discussion clean |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*v4 spec — July 2026 · Shipped*
