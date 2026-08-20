---
name: admin-cms-coverage
description: Admin CMS test coverage findings — what's covered, what's skipped, and known infrastructure limits
metadata:
  type: project
---

Admin CMS coverage was raised from **25% → 48%** (`app/admin/routes.py`) by adding `tests/test_admin_cms.py` (63 tests, 1 skip).

**Covered flows (all via `admin_client` form POSTs):**
- Books: list, new form GET, create (redirect + DB assert), edit GET, update (title + slug rename), delete, duplicate-slug 422, missing-title 422, missing-author 422, ghost-slug redirects
- Categories: list, new form GET, create, edit GET, update, delete, duplicate-name 422, nonexistent graceful redirect
- Posts: list, new form GET, edit GET, update, delete, duplicate-slug 422, missing-title 422, publish-without-cover 422, ghost-slug redirects
- Tools: list, new form GET, create (redirect + DB assert), edit GET, update, delete, duplicate-slug 422, missing-title 422, publish-without-cover 422, ghost-slug redirects
- Auth: login page GET, wrong credentials 401, successful login 303, logout clears session, authenticated redirect from login
- Auth guards: 10 GET routes + 3 POST routes asserted to redirect anonymous to `/admin/login/`
- List content: seeded rows appear in each entity's list view

**Skipped test (1):**
- `TestAdminPosts::test_create_post_draft_redirects_and_persists` — The admin POST `/admin/posts/new/` route calls `post_service.create_post()` which ends with `session.refresh(post, ["ratings","comments","related_books"])`. This triggers a MissingGreenlet error under NullPool + aiosqlite even from the full ASGI stack. See [[post-orm-seed-workaround]].

**Remaining uncovered (~52%):**
- All validation-error re-render paths for books/tools (upload error branches, complex form previews)
- Book/tool update with slug collision 422
- Post comment approve/reject/delete/reply routes
- About page GET + POST
- Contact messages admin routes
- Analytics dashboard routes
- Newsletter/Telegram digest routes (external calls — would need stubs)
- Roadmap admin routes (RoadmapResource/ImmigrationVideo CRUD)
- Users admin list
- Media library routes (file upload — requires real file I/O)
- `_inject_comment_badges` dependency path (runs on every authenticated route, partially exercised)

**Why:** As of 2026-08-20, full suite is 97 passed + 1 skipped.

**How to apply:** When adding more admin CMS tests, follow the same ORM-seed pattern (`_seed_book`, `_seed_post`, `_seed_tool`, `_seed_category` helpers in the test file). Post create via HTTP is the one untestable flow under aiosqlite.
