---
name: project-v6.1-roadmap-analytics
description: Spec for extending analytics to classify and display roadmap page traffic (v16 pages were falling into "other")
metadata:
  type: project
---

# v6.1 — Roadmap Analytics Extension

**Status:** Spec complete, ready for implementation. ~3–4h effort.

**Why:** Roadmap pages (/path/, /path/hiring/, /path/{slug}/) shipped in v16 but fall into the "other" analytics bucket. Milad can't see roadmap traffic breakdown in the admin dashboard.

**How to apply:** Implement before v17 — roadmap level traffic data informs whether L2–L6 full pages should be prioritized.

## Decisions (closed)

- Slug → Persian label mapping happens in the **template layer**, not the service
- Roadmap traffic **rolls up into the global KPI** (total views card) — excluding it would make the KPI misleading; breakdown section appears below

## Tracking layer (app/core/analytics.py `_classify_path`)

| Path | page_type | slug |
|------|-----------|------|
| `/path/` | `roadmap` | None |
| `/path/hiring/` | `roadmap_hiring` | None |
| `/path/{level_slug}/` | `roadmap_level` | level_slug |

- No new DB columns or migrations — existing schema (`path`, `page_type`, `entity_id`) is sufficient
- `entity_id` stays NULL (levels are static data, no integer PK model)

## Service layer (app/services/analytics.py)

- New function: `top_roadmap_levels(session, period)` → list of `{slug, views, unique_views}` ordered by views desc, cap 10
- Counts only `page_type = "roadmap_level"` rows

## Admin dashboard (/admin/analytics/)

- New "مسیر یادگیری" section below Tools leaderboard
- Total roadmap views KPI: landing + hiring + all levels combined, for selected period
- Hiring page single-stat row: "صفحه استخدام: X بازدید"
- Per-level leaderboard: slug (mapped to Persian label in template) | views | unique views
- Same visual style as existing book/post/tool leaderboard tables

## Out of scope

- No historical backfill of existing "other" rows
- No referrer breakdown per roadmap level
- No per-level entity FK resolution
