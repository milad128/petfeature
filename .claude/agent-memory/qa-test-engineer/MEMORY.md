# QA Test Engineer Memory Index

- [Post ORM seed workaround](feedback_post_orm_seed.md) — Never use `post_service.create_post()` in tests (direct or via HTTP); MissingGreenlet from session.refresh on selectin relationship under aiosqlite NullPool
- [RTL coverage test patterns](project_rtl_coverage.md) — Full-site RTL audit: pages covered, seeding patterns, known quirks (tool needs category FK, post needs ORM seed)
- [Admin CMS coverage](project_admin_cms_coverage.md) — 25%→48% after test_admin_cms.py; what's covered, the 1 skip (post create), and remaining 52% gap
