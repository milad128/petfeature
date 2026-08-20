---
name: rtl-coverage-test-patterns
description: Patterns and findings from the full-site RTL coverage audit (tests/test_rtl_coverage.py)
metadata:
  type: project
---

Full RTL coverage for every user-facing GET page was added in `tests/test_rtl_coverage.py` (23 tests). The contract is: status 200 AND `dir="rtl"` in body (or 404 + RTL for the unknown roadmap slug).

**Pages covered:**
- Static public: `/`, `/library/`, `/blog/`, `/tools/`, `/about/`, `/contact/` (parametrized)
- Detail (with seeded data): `/library/{slug}/`, `/blog/{slug}/`, `/tools/{slug}/`
- Detail null-state (no data): all three detail routes with non-existent slugs — they render RTL even when the item is None
- Roadmap: `/path/`, `/path/hiring/`, `/path/apm/` (full page), `/path/{pm,senior-pm,lead,director,cpo}/` (stubs, parametrized)
- Roadmap unknown slug: `/path/totally-unknown-slug/` — returns 404 with RTL template (not an error, by design)
- Admin: `/admin/login/` (unauthenticated), `/admin/books/` (via `admin_client`)

**Key findings:**
- All roadmap and admin pages already rendered RTL correctly — no bugs found.
- `post_service.create_post()` cannot be used in tests: see [[post-orm-seed-workaround]].
- `book_service.create_book()` and `tool_service.create_tool()` work fine from `db_session` in tests.
- Tool requires a `Category` FK; seed category via ORM `db_session.add(Category(...))` + `flush()` before creating the tool.
- The `_fresh_schema` autouse fixture gives full isolation; all 23 tests pass individually and as a suite.

**Why:** As of 2026-08-20, total suite is 34 tests (11 pre-existing + 23 new RTL tests).
