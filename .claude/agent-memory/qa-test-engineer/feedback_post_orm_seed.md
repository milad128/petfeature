---
name: post-orm-seed-workaround
description: Seeding Post rows for tests must use ORM directly, not post_service.create_post(), to avoid a MissingGreenlet lazy-load error
metadata:
  type: feedback
---

Do NOT call `post_service.create_post()` in tests — either directly via `db_session`, or by hitting the admin HTTP route (POST `/admin/posts/new/`). Both paths fail with the same MissingGreenlet error.

`create_post()` ends with `session.refresh(post, ["ratings", "comments", "related_books"])`. Under the NullPool + aiosqlite test setup, this refresh triggers a lazy-load of the `selectin`-mapped `related_books` relationship inside a context that has no greenlet — raising `sqlalchemy.exc.MissingGreenlet`.

**Why:** SQLAlchemy's async sessions cannot perform relationship loads (even via `session.refresh`) outside of a properly managed greenlet context. In production (asyncpg + connection pool), this works fine. In the NullPool aiosqlite test DB, it fails. This affects BOTH direct service calls AND the full HTTP route path.

**How to apply:**
- When seeding a Post for test purposes, construct the ORM model directly and commit:
  ```python
  from app.models.post import Post
  post = Post(title="...", slug="...", body="...", status="draft")
  db_session.add(post)
  await db_session.commit()
  ```
- The admin POST `/admin/posts/new/` create route is skipped in `tests/test_admin_cms.py` with `@pytest.mark.skip`. Edit/update/delete are fully testable because they use ORM-seeded posts (no `create_post()` involved).
- If you need related books on the post, add them via the M2M table (`post_books`) with an `insert()` statement after flush — do not assign via the relationship attribute.
- To get full create-route coverage, use a real Postgres connection pool in CI instead of aiosqlite.

See [[rtl-coverage-test-patterns]] for full test file context.
