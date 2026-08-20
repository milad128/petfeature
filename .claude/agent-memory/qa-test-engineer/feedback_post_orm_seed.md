---
name: post-orm-seed-workaround
description: Seeding Post rows for tests must use ORM directly, not post_service.create_post(), to avoid a MissingGreenlet lazy-load error
metadata:
  type: feedback
---

Do NOT call `post_service.create_post()` in tests. Its `_sync_related_books` helper assigns `post.related_books = []`, which triggers a synchronous lazy-load on an async session — raising `sqlalchemy.exc.MissingGreenlet`.

**Why:** SQLAlchemy's async sessions cannot perform lazy relationship loads inside sync attribute-assignment paths. The service is safe in production (called from async route handlers under greenlet context), but not when called directly from test code that uses `db_session`.

**How to apply:** When seeding a Post for test purposes, construct the ORM model directly and commit:

```python
from app.models.post import Post, PostStatus

post = Post(
    title="...",
    slug="...",
    body="...",
    status=PostStatus.PUBLISHED.value,
    read_time_minutes=1,
    view_count=0,
)
db_session.add(post)
await db_session.commit()
```

If you need related books on the post, add them via the M2M table (`post_books`) with an `insert()` statement after the flush — do not assign via relationship.

See [[rtl-coverage-test-patterns]] for the full test file context.
