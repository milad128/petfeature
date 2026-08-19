---
name: project-v16-roadmap
description: v16 Learning Roadmap epic — public PM career curriculum + admin CMS; SHIPPED July 2026
metadata:
  type: project
---

v16 is the Roadmap epic (مسیر یادگیری) — the fourth founding epic. **Shipped July 2026.**

**Why:** Persian-speaking PMs have no opinionated learning sequence. The library has books but no curriculum linking them. The roadmap fills that gap.

**How to apply:** v16 is done and live. Future roadmap work is L2+ pages (v17+).

## What shipped

- Public pages: `/path/` (landing with depth matrix + fork), `/path/hiring/` (L0), `/path/apm/` (L1), `/path/{slug}/` stub for L2–L6
- Admin CMS: full resource CRUD at `/admin/roadmap/` + missing-links queue
- Admin CMS: immigration video CRUD at `/admin/immigration-videos/` (added during impl, not in original spec)
- Model: `RoadmapResource` + `ImmigrationVideo` (both in `app/models/roadmap.py`)
- Service: `app/services/roadmap_service.py`
- Constants: `app/services/roadmap_data.py`
- Seed script: `scripts/seed_roadmap.py`

## Key decisions (July 2026)

- **Theme:** Current site theme (light). NOT the dark brown design in the Fable v16 files.
- **Data model:** Hybrid — resources in DB (`RoadmapResource`); all other content (competencies, depths, sprint/mat numbers, body text) hardcoded in `roadmap_data.py`
- **`homework_text` removed from DB** — moved to hardcoded constants per level/competency, not stored per resource row
- **`subtitle` added to `RoadmapResource`** — free-text shown in parens after resource type (e.g. "رایگان")
- **Extra resource types added:** `video`, `practice-tool` (original spec had: book, article, podcast, course, tool, guide)
- **`ImmigrationVideo` model** — added during impl for hiring page immigration section; has full admin CRUD
- **`count_missing_links()`** — service function for admin sidebar badge showing unlinked resource count
- **v16 ships:** L0 + L1 as full pages. L2–L6 = disabled badge on landing, stub pages at their URLs (not redirect, not 404).

## Spec location

`docs/spec-v16-roadmap.md`

## Open questions

- When does v17 (L2 PM) get built? (content + templates for next level)

See [[project-v12-user-auth]] — v16 is independent of v12; does not require auth.
