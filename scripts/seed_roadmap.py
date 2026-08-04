"""
seed_roadmap.py — Seed placeholder RoadmapResource rows for v16.

Run once after `alembic upgrade head`:
    python scripts/seed_roadmap.py

All rows are created without external_url or book_id (i.e. "missing links").
Fill them via the admin panel at /admin/roadmap/missing-links/.

Existing rows are NOT overwritten — the script is idempotent:
if a row with the same (level_slug, competency_slug, area_slug, title) already
exists it is skipped.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.roadmap import RoadmapResource  # noqa: F401  (ensures table is known)
from app.services.roadmap_data import (
    APM_COMPETENCY_DATA,
    COMPETENCY_BY_SLUG,
    L0_AREAS,
    LEVELS,
    LEVEL_BY_SLUG,
)


# ── Seed definitions ──────────────────────────────────────────────────────────
# Each entry becomes one RoadmapResource row (placeholder, no link yet).

def _l0_rows() -> list[dict]:
    """One row per L0 area (for the Getting Hired page)."""
    rows = []
    for i, area in enumerate(L0_AREAS):
        rows.append({
            "level_slug":      "hiring",
            "competency_slug": None,
            "area_slug":       area.slug,
            "category":        None,
            "title":           f"[منبع ورود] {area.name}",
            "resource_type":   "article",
            "reading_time":    None,
            "difficulty":      None,
            "has_persian":     False,
            "is_required":     True,
            "external_url":    None,
            "book_id":         None,
            "homework_text":   None,
            "sort_order":      (i + 1) * 10,
        })
    return rows


def _apm_rows() -> list[dict]:
    """
    Seed the APM (L1) level resources.

    For each competency in APM_COMPETENCY_DATA we create one placeholder
    resource. Category 'passive' gets no row (passive competencies have no
    study material by design).
    """
    rows = []
    sort = 10
    for slug, cd in APM_COMPETENCY_DATA.items():
        if cd.category == "passive":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        rows.append({
            "level_slug":      "apm",
            "competency_slug": slug,
            "area_slug":       None,
            "category":        cd.category,
            "title":           f"[منبع] {comp.fa}",
            "resource_type":   "book",
            "reading_time":    None,
            "difficulty":      None,
            "has_persian":     False,
            "is_required":     True,
            "external_url":    None,
            "book_id":         None,
            "homework_text":   None,
            "sort_order":      sort,
        })
        sort += 10
    return rows


def _stub_level_rows() -> list[dict]:
    """
    One placeholder resource per stub level (pm, senior-pm, lead, director, cpo).
    Just a single sentinel row so the level shows up in the admin list.
    """
    stub_slugs = ["pm", "senior-pm", "lead", "director", "cpo"]
    rows = []
    for slug in stub_slugs:
        lv = LEVEL_BY_SLUG[slug]
        rows.append({
            "level_slug":      slug,
            "competency_slug": None,
            "area_slug":       None,
            "category":        "entry",
            "title":           f"[placeholder] {lv.fa}",
            "resource_type":   "article",
            "reading_time":    None,
            "difficulty":      None,
            "has_persian":     False,
            "is_required":     True,
            "external_url":    None,
            "book_id":         None,
            "homework_text":   None,
            "sort_order":      10,
        })
    return rows


ALL_ROWS: list[dict] = [
    *_l0_rows(),
    *_apm_rows(),
    *_stub_level_rows(),
]


# ── DB helpers ────────────────────────────────────────────────────────────────

async def _row_exists(db: AsyncSession, row: dict) -> bool:
    """Return True if a resource with this (level, competency/area, title) exists."""
    stmt = select(RoadmapResource).where(
        RoadmapResource.level_slug == row["level_slug"],
        RoadmapResource.title == row["title"],
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def seed(db: AsyncSession) -> None:
    created = 0
    skipped = 0
    for row in ALL_ROWS:
        if await _row_exists(db, row):
            skipped += 1
            continue
        resource = RoadmapResource(**row)
        db.add(resource)
        created += 1

    await db.commit()
    print(f"✅  Seeded {created} row(s), skipped {skipped} duplicate(s).")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    async with async_session_factory() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
