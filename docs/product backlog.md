# Product Backlog — پت فیچر

Unscheduled feature ideas and epics. Nothing here has a committed version or timeline. Items move into a versioned spec when they are prioritized and scoped.

---

## Epic: Roadmap (مسیر)

A structured, opinionated learning path that guides readers through the library and blog.


| Idea                        | Description                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Roadmap page** (`/path/`) | Ordered list of learning steps; intro section explaining who the path is for                            |
| **Path steps**              | Each step: title, description, level tag (مقدماتی/میانی/پیشرفته), links to library books and blog posts |
| **Step ordering**           | `sort_order` field; admin reorders via form or drag-and-drop                                            |
| **Admin: Manage steps**     | CRUD path steps; assign linked books and posts; reorder                                                 |
| **Multiple paths**          | One canonical path in v1; potentially separate paths per role/level later                               |


**Open questions when scoping:**

- Path shape — linear (1→2→3) or branching by track?
- Level tags taxonomy
- Step card layout — accordion or expanded?
- Allow text-only steps (no linked content)?

**Data model:** `PathStep` (title, description, sort_order, level), `path_step_books` M2M, `path_step_posts` M2M

---



## Epic: Newsletter + Contact

Audience growth and reader-to-author communication.


| Idea                                 | Description                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| **Newsletter page** (`/newsletter/`) | Subscription form: نام، ایمیل; success message on submit; footer CTA on all pages |
| **Duplicate handling**               | Existing email handled gracefully (no error exposed)                              |
| **Email service integration**        | Provider TBD — Resend, Mailchimp, or Buttondown                                   |
| **Contact page** (`/contact/`)       | Form: نام، ایمیل، پیام; success message; author LinkedIn link                     |
| **Admin: View subscribers**          | Read-only list: name, email, subscribed_at                                        |
| **Admin: View contact messages**     | List + full message view; author replies via email directly                       |
| **Spam protection**                  | Honeypot + rate limiting on both forms                                            |


**Open questions when scoping:**

- Newsletter CTA placement — footer only, or also inline on home/library/blog?
- Email provider choice
- Contact form delivery — DB only, or also forward to author email in real time?

**Data model:** `Subscriber` (name, email, subscribed_at), `ContactMessage` (name, email, body, created_at)

---



## Epic: Book Engagement (Reactions + Comments)

Let visitors express reactions and share thoughts on library books.


| Idea                              | Description                                                                             |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| **Book like**                     | Toggle button (♥); total like count; visitor-token dedup; no login required             |
| **Book star rating**              | 1–5 stars; average + count shown; visitor-token dedup; optional display on library grid |
| **Read book comments**            | Approved comments shown chronologically below book content                              |
| **Post book comment**             | Form: نام، (ایمیل TBD)، متن; pending queue by default                                   |
| **Admin: Moderate book comments** | Approve / reject / delete; pending queue default view                                   |


**Open questions when scoping:**

- Who can comment — all visitors or logged-in users only?
- Moderation policy — pre or post moderation?
- Comment email field — required, optional, or hidden?
- Show rating on library grid cards?
- Show both like + rating, or pick one?

**Data model:** `BookLike`, `BookRating`, `BookComment` (all keyed on book_id + visitor_token or author fields)

---



## Epic: Visitor Analytics

Give the admin visibility into traffic across all public pages.


| Idea                                      | Description                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------- |
| **Page view tracking**                    | Server-side, passive; records path, page_type, visitor_token (hashed IP+UA), timestamp |
| **Bot filtering**                         | Exclude known crawler User-Agents from counts                                          |
| **Admin dashboard** (`/admin/analytics/`) | Total views, unique visitors, top books, top posts, per-page breakdown                 |
| **Period filters**                        | Today / Last 7 days / Last 30 days / This month / All time                             |
| **Traffic chart**                         | Views per day over selected period (SVG or lightweight JS chart)                       |
| **Jalali date labels**                    | Period labels in Shamsi calendar                                                       |


**Open questions when scoping:**

- Chart rendering — server-side SVG or client-side JS?
- Top N count — 5, 10, or 20?
- Data pruning — admin-controlled retention?
- Referrer / UTM tracking?

**Data model:** `PageView` (path, page_type, visitor_token, created_at) with indexes on created_at, path, visitor_token

---



## Other Ideas


| Idea                                                    | Notes                                      |
| ------------------------------------------------------- | ------------------------------------------ |
| Full-text search across books + posts                   | Post-MVP                                   |
| User registration + login                               | Prerequisite for any personalized features |
| Blog post reactions (extend post rating to other types) | Post-v2                                    |
| Comment replies / threads                               | Flat comments first                        |
| Email notifications on new comment                      | Nice-to-have                               |
| User profile / account page                             | Needs auth first                           |
| English version                                         | Not planned                                |
| Mobile app                                              | Web-first                                  |


---

*Backlog last updated: July 2026*