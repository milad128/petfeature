---
name: project-v14-user-dashboard
description: v14 User Dashboard — newsletter subscribe/unsubscribe (reuses Subscriber model) + My Comments with status + admin replies; user_id FK on comments; ~2 days; backlog
metadata:
  type: project
---

v14 expands the v12 profile page into a real dashboard with two sections.

**Status:** Backlog

**Depends on:** v12 (Google Login — user identity required). [[project-v12-user-auth]]

**Two sections:**

1. **Newsletter (خبرنامه)**
   - Email: check if user's Google email is in Subscriber table (v11); show subscribe/unsubscribe; no email field — uses Google account email automatically
   - Telegram: always-visible join button → t.me/petfeature
   - Reuses existing `Subscriber` model — no new model

2. **My Comments (نظرات من)**
   - All PostComments + BookComments where `user_id = current_user.id`
   - Shows: content type badge, title (linked), comment text, Jalali date, status badge (در انتظار / تأیید شده / رد شده), admin reply if exists
   - Empty state if no comments yet
   - Pagination: 10 per page

**New migration required:**
- Add `user_id` nullable FK → `users.id` (`SET NULL` on delete) to `PostComment` and `BookComment`
- New comments from logged-in users get `user_id` set; anonymous comments unchanged (user_id=NULL)

**Routes added:**
- `POST /profile/newsletter/subscribe/`
- `POST /profile/newsletter/unsubscribe/`
- Minor change to existing book/post comment routes to set `user_id` when user is logged in

**Effort:** ~2 days

**Does NOT include:** Reading List (v15+), editing/deleting own comments, reply notifications, public profiles
