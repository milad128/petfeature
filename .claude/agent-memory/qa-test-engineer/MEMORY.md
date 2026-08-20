# QA Test Engineer Memory Index

- [Post ORM seed workaround](feedback_post_orm_seed.md) — Never use `post_service.create_post()` in tests; use ORM directly to avoid MissingGreenlet lazy-load error
- [RTL coverage test patterns](project_rtl_coverage.md) — Full-site RTL audit: pages covered, seeding patterns, known quirks (tool needs category FK, post needs ORM seed)
