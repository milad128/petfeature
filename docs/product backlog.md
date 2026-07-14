# Product Backlog — پت فیچر

**Shipped:** v1 Library · v2 Blog · v3 Tools · v4 Book Engagement · **v5 About Redesign + Contact** (planned, spec written) · **v6 Visitor Analytics** (planned, spec written)

See [product-spec.md](./product-spec.md) for the versioned roadmap. Nothing below has a committed version or timeline. Items move into a versioned spec when prioritized and scoped.

---

## Epic: Newsletter (مشترکین)

Audience growth — let readers subscribe to stay updated when new content is published.

| Idea | Description |
|------|-------------|
| **Newsletter page** (`/newsletter/`) | Subscription form: نام، ایمیل; success message on submit |
| **Footer CTA** | "عضو خبرنامه شو" strip or inline block on all public pages |
| **Duplicate handling** | Existing email handled gracefully — no error exposed to user |
| **Email service integration** | Provider TBD — Resend, Mailchimp, or Buttondown |
| **Admin: View subscribers** | Read-only list: name, email, subscribed_at |
| **Spam protection** | Honeypot field + rate limiting on submit |

**Open questions when scoping:**
- Email provider choice (Resend is simplest for a solo project)
- CTA placement — footer only, or also inline on home/library/blog?
- Confirmation email (double opt-in) or single opt-in?

**Data model:** `Subscriber` (name, email, subscribed_at, is_active)

---

## ~~Epic: Visitor Analytics~~ → Scoped as v6

**Moved to spec.** See [product-spec-v6.md](./product-spec-v6.md).

Key decisions recorded: `Post.view_count` retained as public counter (Option B); `PageView` powers admin dashboard only; no chart in v6 (table sufficient); bot filtering via UA list; visitor dedup via existing cookie.

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
| Book Engagement | v4 | Book ratings + moderated comments |
| About Redesign + Contact | v5 (planned) | Hero/experience/bootcamps on About; Contact form → DB admin inbox |
| Visitor Analytics | v6 (planned) | PageView log, bot filter, admin dashboard (period, top content, referrers, daily table) |

---

## Other Ideas (post-v5, low priority)

| Idea | Notes |
|------|-------|
| Full-text search across books + posts | Useful once content volume grows; needs thought on UX |
| Email notifications on new contact message | Simple SMTP add-on to v5 Contact; could be v6 |
| Blog post reactions (beyond star rating) | Post-v2; needs UX definition |
| Comment replies / threads | Flat comments first — revisit after engagement data |
| User registration + login | Prerequisite for any personalized features; high effort |
| User profile / account page | Needs auth first |
| English version | Not planned |
| Mobile app | Web-first |

---

*Backlog last updated: July 2026 — v6 Visitor Analytics spec written; analytics epic removed from backlog*
