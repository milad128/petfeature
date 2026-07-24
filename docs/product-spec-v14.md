# Product Spec v14 — User Dashboard (داشبورد کاربر)

**Version:** v14
**Status:** Backlog
**Author:** Milad Mirzaei
**Date:** July 2026
**Depends on:** v12 (Google Login — user identity required)

---

## Overview

v14 turns the minimal v12 profile page into a real user dashboard. Logged-in users get two sections:

1. **خبرنامه (Newsletter)** — subscribe to the email newsletter and join the Telegram channel from one place
2. **نظرات من (My Comments)** — see all comments the user has posted across books and posts, with their approval status and any admin replies

This gives users a reason to have an account on petfeature.ir — their interactions with the site are now visible, trackable, and managed from one page.

---

## Problem Statement

After v12, a logged-in user's profile page shows only their name, email, and join date — essentially an empty page. Users have no reason to register and no reason to come back to their profile.

v14 surfaces two things users genuinely want to know:
1. "Am I subscribed to updates?" → Newsletter section
2. "Was my comment approved? Did the admin reply?" → Comments section

Both use data that already exists in the DB (Subscriber model from v11, PostComment/BookComment from v2/v4) — this is mostly a presentation layer with one new migration.

---

## Target Users

- **Logged-in visitor:** A Persian-speaking PM who has posted comments on books or posts and wants to know if the admin approved or replied. Also wants to manage how they receive petfeature updates.

---

## User Stories

### Newsletter
- *As a logged-in user, I want to see whether my email is subscribed to the newsletter so that I know if I'll receive email updates.*
- *As a logged-in user, I want to subscribe or unsubscribe from the email newsletter from my dashboard so that I control my inbox.*
- *As a logged-in user, I want a button to join the Telegram channel directly from my dashboard so that I have one place to manage all petfeature notifications.*

### My Comments
- *As a logged-in user, I want to see all comments I've posted on petfeature so that I can track my engagement with the content.*
- *As a logged-in user, I want to see the approval status of each comment so that I know if it's visible to other readers.*
- *As a logged-in user, I want to see admin replies to my comments from my dashboard so that I don't have to search back through all pages to find them.*

---

## Acceptance Criteria

### Dashboard layout (`/profile/`)

- [ ] Profile page has two clearly labelled sections below the user info: "خبرنامه" and "نظرات من"
- [ ] Page is accessible only when logged in (existing v12 auth guard)
- [ ] RTL layout consistent with rest of site

---

### Section A — Newsletter (خبرنامه)

#### Email subscription
- [ ] Check if the user's Google email exists in the `Subscriber` table (from v11)
- [ ] If **subscribed**: show "✓ ایمیل شما در لیست خبرنامه است" + "لغو اشتراک" button
- [ ] If **not subscribed**: show "عضویت در خبرنامه ایمیلی" button
- [ ] Clicking "عضویت": adds the user's Google email + name to `Subscriber` (same logic as public form); shows success state
- [ ] Clicking "لغو اشتراک": sets `is_active=False` on the `Subscriber` record; shows unsubscribed state
- [ ] No email field shown — email comes from the user's Google account automatically
- [ ] Duplicate subscription handled silently (reactivate the existing record if `is_active=False`)

#### Telegram channel
- [ ] Show a "عضویت در کانال تلگرام @petfeature" button linking to `https://t.me/petfeature` (new tab)
- [ ] No tracking of whether the user actually joined — Telegram doesn't expose this; button is always shown
- [ ] Short description: "برای دریافت سریع‌تر محتوای جدید، کانال تلگرام ما رو دنبال کنید."

---

### Section B — My Comments (نظرات من)

#### Data prerequisite
- [ ] `PostComment` table gains a nullable `user_id` FK → `users.id` — **new migration**
- [ ] `BookComment` table gains a nullable `user_id` FK → `users.id` — **new migration**
- [ ] When a logged-in user submits a comment (on any post or book), `user_id` is set on the record
- [ ] Existing anonymous comments (null `user_id`) are unaffected

#### Comment list display
- [ ] All `PostComment` + `BookComment` records where `user_id = current_user.id`, ordered by `created_at DESC`
- [ ] Each comment card shows:
  - Content type badge: "یادداشت" or "کتاب"
  - Title of the post or book (linked to its public page)
  - The comment text (truncated to 200 chars if long; "بیشتر" expands inline)
  - Submission date (Jalali)
  - Status badge: **در انتظار تأیید** (yellow) / **تأیید شده** (green) / **رد شده** (red)
- [ ] If the comment has an admin reply (`reply_text` is not null):
  - Admin reply is shown below the comment, clearly labelled "پاسخ پت فیچر:"
  - Reply text displayed in full
  - Reply date (Jalali)
- [ ] If user has no comments: empty state — "هنوز نظری ثبت نکردی. کتاب‌ها و یادداشت‌ها رو بخون و نظرت رو بنویس."
- [ ] Rejected comments shown with status badge but no explanation (admin rejection reason is internal)
- [ ] Pagination: 10 comments per page if more than 10 exist

---

## Data Model Changes

### Migration 1 — Add `user_id` to comments

```python
# PostComment (app/models/post.py)
user_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
)

# BookComment (app/models/book.py)
user_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
)
```

`ondelete="SET NULL"` — if a user account is deleted, comments remain but become anonymous.

**Migration:** `alembic revision --autogenerate -m "add user_id to post_comments and book_comments"`

### No new models needed
- `Subscriber` (v11) — reused as-is for email subscription
- `PostComment` / `BookComment` — extended with `user_id` FK
- `User` (v12) — unchanged

---

## Comment attribution (change to existing comment flow)

When a logged-in user submits a comment on a post or book detail page, the web route must:

1. Read `current_user` from session (via `get_current_user` dependency from v12)
2. Set `user_id = current_user.id` on the new comment record
3. Still set `visitor_token` as before (for backward compatibility and dedup)

Anonymous visitors (not logged in) continue to submit comments with `user_id=None` — no change to their flow.

---

## Routes

| Method | Path | Change |
|--------|------|--------|
| `GET` | `/profile/` | Expand to render newsletter + comments sections |
| `POST` | `/profile/newsletter/subscribe/` | Add user email to Subscriber |
| `POST` | `/profile/newsletter/unsubscribe/` | Set Subscriber.is_active=False |
| `POST` | `/library/{slug}/comment/` | Set `user_id` if user is logged in (existing route, small change) |
| `POST` | `/blog/{slug}/comment/` | Set `user_id` if user is logged in (existing route, small change) |

---

## Technical Design

### New/changed files

| File | Change |
|------|--------|
| `app/templates/pages/profile.html` | Expand with newsletter + comments sections |
| `app/services/users.py` | Add `get_user_comments()`, `subscribe_to_newsletter()`, `unsubscribe_from_newsletter()` |
| `app/web/routes.py` | Add newsletter subscribe/unsubscribe routes; add `user_id` to comment submission |
| `app/models/post.py` | Add `user_id` FK to `PostComment` |
| `app/models/book.py` | Add `user_id` FK to `BookComment` |

### Newsletter subscription logic

```python
# app/services/users.py
async def subscribe_to_newsletter(session, user: User) -> None:
    existing = await session.scalar(
        select(Subscriber).where(Subscriber.email == user.email)
    )
    if existing:
        existing.is_active = True  # reactivate if previously unsubscribed
    else:
        session.add(Subscriber(name=user.name, email=user.email, is_active=True))
    await session.commit()

async def unsubscribe_from_newsletter(session, user: User) -> None:
    existing = await session.scalar(
        select(Subscriber).where(Subscriber.email == user.email)
    )
    if existing:
        existing.is_active = False
        await session.commit()
```

### Comment query

```python
# app/services/users.py
async def get_user_comments(session, user_id: int, page: int = 1):
    # fetch PostComments and BookComments where user_id matches,
    # load related post/book titles and reply_text,
    # return unified list sorted by created_at DESC
```

---

## Out of Scope (v14)

| Item | Reason |
|------|--------|
| Reading List (want/reading/read) | v15 — separate epic |
| Editing or deleting own comments | Adds moderation complexity; deferred |
| User notification (email/Telegram when admin replies) | v15+ — needs background job |
| Public profile page (visible to others) | Social feature — v16+ |
| Retroactively linking old anonymous comments to user | Complex + low value; only new comments get user_id |
| Bookmarks / saved tools | v15+ |
| Account settings (change display name) | Name comes from Google; no edit needed in v14 |

---

## NFRs

- Dashboard must load in a single page request — no separate AJAX calls for sections
- All dates in Jalali
- Status badges must be clearly distinguishable for colour-blind users (use text + colour, not colour alone)
- Empty states must be friendly and direct users toward content
- `user_id` FK uses `SET NULL` on delete — comment data preserved if user deletes account

---

## Effort Estimate

| Task | Estimate |
|------|----------|
| Migration (user_id on PostComment + BookComment) | 1 hour |
| Wire `user_id` into comment submission routes | 1 hour |
| Newsletter subscribe/unsubscribe service + routes | 2 hours |
| `get_user_comments()` service query (unified post + book) | 3 hours |
| Profile page template (newsletter section) | 1.5 hours |
| Profile page template (comments section + pagination) | 3 hours |
| Empty states, status badges, reply display | 1 hour |
| **Total** | **~2 days** |
