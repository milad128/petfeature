---
name: project-v15-bookshelf
description: Bookshelf (قفسه کتاب) feature — renamed from Reading List; PRD written July 2026; backlog, blocked on v12
metadata:
  type: project
---

v15 Bookshelf (قفسه کتاب) spec written July 2026. Renamed from "Reading List" (لیست مطالعه).

Key decisions:
- All 3 reading statuses in scope: می‌خواهم بخوانم / در حال خواندن / خواندم (stored as want/reading/read)
- Private only — no shareable URL
- Social proof save count shown on book detail when count ≥ 2
- Sort by date added only (newest first)
- Admin "در قفسه" column on books list (all-time distinct user save count)
- "خواندم" review modal: marking a book as read opens a modal to rate + comment. Reuses existing v4 BookRating + BookComment (no new models); comment goes through v4 moderation queue; both fields optional but ≥1 required; dismissable; read status saves regardless. Adds v4 as a dependency. Effort now ~2.5 days.
- Route: `/profile/bookshelf/`
- Model: `ReadingListItem` (user_id FK, book_id FK, status, added_at) with unique constraint on (user_id, book_id)
- New service file: `app/services/bookshelf.py`
- Estimated effort: ~2 dev days

**Why:** Blocked on v12 User Auth — needs `User` model and session middleware before any user-scoped features can be built.

**How to apply:** Do not scope or prioritize v15 until v12 is shipped. When v12 ships, v15 is the natural next user-facing feature.

See: `docs/product-spec-v15.md`

[[project-v12-user-auth]]
