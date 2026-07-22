# Product Spec v2 — پت فیچر (Blog)

> **Status: Shipped** · **Prerequisite:** [Product Spec v1](./product-spec-v1.md) · **Parent:** [Product overview](./product-spec.md) · **Next:** [Product Spec v3](./product-spec-v3.md) · **Diagrams:** [Use case diagram](./use-case-diagram.md)

## 1. Summary

| Field | Value |
|--------|--------|
| **Version** | v2 — Blog |
| **Status** | Shipped |
| **Goal** | Publish personal PM essays with clean URLs, social sharing, view counts, star ratings, and a comment section |
| **Builds on** | [Product Spec v1](./product-spec-v1.md) |
| **Design files** | `petfeature redesign/project/Petfeature Blog.dc.html`, `Petfeature Post.dc.html` |
| **New in v2** | Blog list page, post detail page, featured posts, view counts, star rating on posts, post comments, admin post management |

**Scope in one sentence:** Add a full blog (یادداشت) with star ratings, comments, view counts, and social sharing — post reactions and comments are independent of the book system.

---

## 2. Problem & Goals

**Problem:** v1 ships only the library. The author has personal PM essays with no clean home in the new codebase — no proper URLs, no Jalali dates, no view counts, no way for readers to rate or comment.

**v2 goals**

- **Browse Blog** — read PM essays with cover images, Jalali dates, read time, and view counts
- **Featured posts** — highlighted section on the blog list for admin-picked posts
- **Share to Social Networks** — share posts to LinkedIn, X, Telegram with correct OG previews
- **Copy link** — one-click copy of the post URL
- **Star rating on posts** — visitors rate how useful a post was (1–5 stars)
- **Post comments** — visitors leave comments; admin moderates them
- **View count** — every page load increments the post's view counter
- **Admin CMS** — full post management (CRUD, featured toggle, comment moderation)

---

## 3. Actors

| Actor | Role |
|-------|------|
| **Visitor** | All v1 capabilities + reads posts, rates posts, comments, copies link, shares |
| **Admin (Milad Mirzaei)** | All v1 admin + creates/edits/deletes posts, marks featured, moderates comments |
| **Social networks** | External share targets (LinkedIn, X, Telegram) |

---

## 4. Information Architecture (additions)

Extends [v1 IA](./product-spec-v1.md#6-information-architecture):

```
Home (/)
├── بلاگ              → /blog/          (new in v2)
│   └── {slug}/        → /blog/{slug}/   (new in v2)
├── کتابخانه          → /library/       (from v1)
│   └── {slug}/        → /library/{slug}/
└── درباره من         → /about/          (from v1)
```

**Global additions**

- **بلاگ** added to main nav (nav: کتابخانه | بلاگ | درباره من)

---

## 5. Feature Requirements

### 5.1 Browse Blog — `/blog/`

**Hero section**
- Page title: یادداشت‌های پت فیچر
- Description: "یادداشت‌ها و برداشت‌های شخصی درباره‌ی مدیریت محصول — چیزهایی که بین خواندن کتاب‌ها و کار روزمره کشف می‌کنم."
- Post count badge: ✍️ N یادداشت

**Featured posts section (مطلب ویژه)**
- Admin can mark any number of posts as featured
- Only the single most-recently-published featured post is shown in the large highlighted card at the top; other posts marked featured simply appear in their normal chronological position in the list
- Featured card shows: title, excerpt, Jalali date, read time, view count (👁)

**Post list**
- Reverse-chronological order (featured post excluded from the list since it's shown above)
- Each post card: cover image, title, excerpt, Jalali date, read time, view count (👁)
- Empty state (no published posts yet): "✍️ هنوز یادداشتی منتشر نشده"

---

### 5.2 Read Blog Post — `/blog/{slug}/`

**Header area**

| Element | Detail |
|---------|--------|
| Breadcrumb | بلاگ ‹ {post title} |
| Title | Post title (large) |
| Author | میلاد میرزایی (fixed — always the author) |
| Date | Jalali (Shamsi) formatted published date |
| Read time | Auto-calculated (word count ÷ 200 wpm); displayed as "N دقیقه مطالعه" |
| View count | 👁 N بازدید — incremented on every page load (server-side) |
| Copy link | 🔗 button — copies post URL to clipboard via JS; label toggles to confirm |

**Body**

| Element | Detail |
|---------|--------|
| Cover image | Large featured image at top |
| Body content | Rich-text HTML |
| Quote highlights | Styled blockquote blocks within the body |

**Star rating widget**

| Element | Detail |
|---------|--------|
| Label | "این یادداشت چقدر به‌دردت خورد؟" |
| Input | 5-star selector (★ ★ ★ ★ ★) |
| Display | Average score ("میانگین امتیاز: N.N از ۵") + vote count ("بر اساس N رای") |
| Post-vote | Thank-you state: "ممنون! ✓" |
| Who | Any visitor — no login required |
| Dedup | Visitor token (cookie/localStorage) — one rating per visitor per post |

**Comments section**

| Element | Detail |
|---------|--------|
| Header | نظرها (N) — shows approved comment count |
| Comment list | Chronological; each shows: commenter name, date, body |
| Visible | Approved comments only |
| Empty state | Graceful if no approved comments yet |
| Add comment form | نام (required)، ایمیل (optional)، متن نظر (required); submit button: "ارسال نظر ←" |
| Auth | No login required — open to all visitors |
| On submit | Success message shown; comment goes to pending queue |

**Share buttons**
- Appear in **two locations**: directly below the post metadata (top) and again at the bottom of the post body
- Channels: LinkedIn, X (Twitter), Telegram

**Footer of post**
- Link back: "همه‌ی یادداشت‌ها"

---

### 5.3 Share to Social Networks

From any post detail page — share buttons appear at **both** the top (below metadata) and the bottom of the post body:

| Channel | Mechanism |
|---------|-----------|
| LinkedIn | Share URL |
| X (Twitter) | Tweet with title + URL |
| Telegram | Telegram share link |
| OG tags | `og:title`, `og:description`, `og:image` in `<head>` for correct social previews |

---

### 5.4 Admin CMS — v2 additions

All routes under `/admin/`.

#### Manage Posts — `/admin/posts/`

**Post list**

| Column | Detail |
|--------|--------|
| Title | Post title |
| Status | Draft / Published |
| Featured | Yes / No |
| Date | Published date (Jalali) |
| Views | View count |
| Rating | Average stars + vote count |
| Comments | Pending + approved count |
| Actions | Edit, Delete |

**Create / Edit Post — `/admin/posts/new/` and `/admin/posts/{slug}/edit/`**

| Field | Detail |
|-------|--------|
| Title | Text input |
| Slug | Auto-generated from title; editable; uniqueness validated |
| Cover image | File upload (JPG/PNG); **required** — post cannot be published without a cover; stored in `static/uploads/post-covers/` |
| Body | Rich-text editor (HTML) |
| Excerpt | Text area; auto-generated from first ~200 chars of body if left empty; admin can override |
| Status | Draft / Published |
| Published date | Date picker; defaults to today when publishing |
| Featured | Toggle (yes/no) — marks post for featured section; featured posts sorted by published date descending |
| Read time | Shown as calculated value (word count ÷ 200); display only, not editable |

**Delete post** — removes post and all its ratings and comments.

#### Manage Post Comments — `/admin/posts/comments/`

| Feature | Detail |
|---------|--------|
| List | All comments across all posts; filterable by status (pending/approved/rejected) |
| Columns | Post title, commenter name, excerpt, date, status |
| Default view | Pending queue |
| Approve | Comment becomes visible on post page |
| Reject | Hidden from post; kept in DB |
| Delete | Permanently removed |

---

## 6. Content Model (v2 additions)

New entities on top of [v1 content model](./product-spec-v1.md#8-content-model-v1):

| Entity | Key fields |
|--------|------------|
| **Post** | id, title, slug (unique), cover (path), body (text), excerpt (text, nullable), published_date, status (draft/published), is_featured (bool, default false), read_time_minutes (int, auto-calculated), view_count (int, default 0), created_at, updated_at |
| **PostRating** | id, post_id (FK), visitor_token, stars (1–5), created_at |
| **PostComment** | id, post_id (FK), author_name, author_email (nullable), body (text), status (pending/approved/rejected), created_at |

**Relationships**

- Post → many PostRating (cascade delete)
- Post → many PostComment (cascade delete)
- PostRating: unique per (post_id, visitor_token) — update on re-rate
- PostComment: moderated; only approved ones shown publicly

**Calculated fields (not stored separately)**

- `read_time_minutes` — calculated on save: `ceil(word_count(body) / 200)`
- `average_rating` — computed from PostRating on read: `avg(stars)` where post_id matches
- `rating_count` — `count(*)` from PostRating where post_id matches
- `approved_comment_count` — `count(*)` from PostComment where post_id and status = approved

---

## 7. Non-Functional Requirements (v2)

| Area | Requirement |
|------|-------------|
| **OG / SEO** | `og:title`, `og:description`, `og:image` on each post page |
| **Jalali dates** | All blog dates displayed in Persian calendar (Shamsi) format |
| **Read time** | Calculated server-side on save: word count ÷ 200 wpm, rounded up |
| **View count** | Incremented server-side on each `GET /blog/{slug}/`; known crawler User-Agents excluded; fire-and-forget (non-blocking) |
| **Copy link** | JS Clipboard API; label changes to confirm state on success |
| **Rating dedup** | Visitor token checked server-side before recording; update existing row on re-rate |
| **Comment spam** | Honeypot field + rate limiting per IP on comment submit |
| **Moderation default** | All new comments start as `pending`; none auto-approved |
| **Mobile** | All sections fully responsive: post cards, rating widget, comment form, share buttons |

---

## 8. Out of Scope (v2)

| Item | Notes |
|------|-------|
| Newsletter subscription | → v4 |
| Contact form | → v4 |
| Learning path (مسیر) | → v3 |
| Book reactions and book comments | → v5 (independent from post system) |
| Full-text search | Not planned yet |
| Comment replies / threads | Flat comments only |
| Email notification on new comment | Not in v2 |
| User registration / login | Not planned yet |

---

## 9. Dependency on v1

v2 assumes v1 provides:

- Book library with full detail pages and slug-based URLs
- About-author page and admin CMS
- Production deployment on Hamravesh Darkube stable

---

---

## 11. Success Metrics

| Metric | Why it matters |
|--------|----------------|
| Blog post views | Content reach |
| Time on post pages | Content resonates |
| Share clicks | Organic reach |
| Average star rating per post | Quality signal |
| Rating participation rate | Reader engagement |
| Comments per post | Deeper engagement |
| Moderation queue clearance time | Admin keeps discussion clean |

---

## Deployment Status

| Field | Value |
|-------|-------|
| **Status** | Shipped |
| **Deploy date** | July 2026 |
| **Platform** | Hamravesh Darkube (production) |
| **Notes** | — |

---

*v2 spec — July 2026 · Updated from design files: Petfeature Blog.dc.html, Petfeature Post.dc.html · **Shipped***
