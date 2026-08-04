"""
roadmap_service.py — Business logic for the Roadmap epic.

Public pages call: get_landing_context, get_hiring_context, get_level_context.
Admin routes call: get_roadmap_resources, get_resource, create_resource,
                   update_resource, delete_resource, get_missing_links,
                   count_missing_links.
"""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.roadmap import ImmigrationVideo, RoadmapResource
from app.core.jalali import format_reading_hours, parse_reading_time_to_hours
from app.services.roadmap_data import (
    APM_COMPETENCY_DATA,
    APM_CORE_RATIONALE,
    APM_SUPPORTING_DETAIL,
    APM_TEXTS,
    APM_BRIDGE_CHECKLIST,
    COMPETENCIES,
    COMPETENCY_BY_SLUG,
    DEPTH_LABELS,
    DEPTH_MATRIX,
    DEPTH_SCALE,
    FOUR_CATEGORIES,
    FULL_PAGE_SLUGS,
    L0_AREAS,
    L0_AUDIENCE,
    L0_IMMIGRATION_VIDEOS,
    L0_LEVELS_GRID,
    L0_PHASES,
    L0_PHASE_BY_SLUG,
    LEVEL_BY_SLUG,
    LEVELS,
    STUB_SLUGS,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

_FA_TRANS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _fa(n: int) -> str:
    return str(n).translate(_FA_TRANS)


def _bar_pct(sprint_weeks: int, tenure_months: int) -> int:
    """Percentage of tenure that is sprint (for the progress bar)."""
    if tenure_months == 0:
        return 100
    tenure_weeks = tenure_months * 4.33
    return min(100, round((sprint_weeks / tenure_weeks) * 100))


def _depth_chip_color(depth: int) -> str:
    """CSS background color for a depth chip."""
    if depth == 0:
        return "transparent"
    tint = 26 + depth * 14
    return f"color-mix(in srgb, var(--accent) {tint}%, #3a2d22)"


# ── Landing page context ─────────────────────────────────────────────────────

async def get_landing_context(db: AsyncSession) -> dict:
    """Build context dict for GET /path/."""
    # One query: count resources per level
    stmt = (
        select(RoadmapResource.level_slug, func.count(RoadmapResource.id))
        .where(RoadmapResource.is_required.is_(True))
        .group_by(RoadmapResource.level_slug)
    )
    result = await db.execute(stmt)
    counts: dict[str, int] = {row[0]: row[1] for row in result}

    # Build level card data
    level_cards = []
    for lv in LEVELS:
        pct = _bar_pct(lv.sprint_weeks, lv.tenure_months)
        level_cards.append({
            "slug": lv.slug,
            "num": lv.num,
            "fa": lv.fa,
            "en": lv.en,
            "spec": lv.spec,
            "required": lv.required,
            "reading": lv.reading,
            "sprint": lv.sprint,
            "tenure": lv.tenure,
            "sprint_weeks": lv.sprint_weeks,
            "tenure_months": lv.tenure_months,
            "is_track": lv.is_track,
            "flag": lv.flag,
            "bar_pct": pct,
            "mat_pct": 100 - pct if lv.tenure_months else 0,
            "is_full_page": lv.slug in FULL_PAGE_SLUGS,
            "is_hiring": lv.slug == "hiring",
            "db_count": counts.get(lv.slug, 0),
        })

    # Build matrix rows
    matrix_rows = _build_matrix_rows()

    return {
        "levels": LEVELS,
        "level_cards": level_cards,
        "competencies": COMPETENCIES,
        "depth_matrix": DEPTH_MATRIX,
        "depth_scale": DEPTH_SCALE,
        "depth_labels": DEPTH_LABELS,
        "four_categories": FOUR_CATEGORIES,
        "matrix_rows": matrix_rows,
    }


def _depth_y_pct(depth: int) -> float:
    """Vertical position (%) for a depth chip — higher depth sits higher in the cell."""
    if depth == 0:
        return 94.0
    return 92.0 - (depth / 5.0) * 78.0


def _build_matrix_rows() -> list[dict]:
    """Build the rows for the depth matrix table, including domain header rows."""
    rows = []
    current_domain = None
    for comp in COMPETENCIES:
        if comp.domain != current_domain:
            current_domain = comp.domain
            rows.append({"is_header": True, "domain": comp.domain})
        depths = DEPTH_MATRIX[comp.slug]
        cells = []
        for i, d in enumerate(depths):
            next_d = depths[i + 1] if i < len(depths) - 1 else None
            if next_d is not None:
                if d == 0 or next_d == 0:
                    seg_type = "dashed"
                elif next_d > d:
                    seg_type = "rise"
                elif next_d < d:
                    seg_type = "fall"
                else:
                    seg_type = "flat"
            else:
                seg_type = None
            cells.append({
                "depth": d,
                "label": "—" if d == 0 else str(d),
                "depth_label": DEPTH_LABELS.get(d, ""),
                "seg_type": seg_type,
                "next_depth": next_d,
                "y_pct": _depth_y_pct(d),
                "next_y_pct": _depth_y_pct(next_d) if next_d is not None else _depth_y_pct(d),
            })
        rows.append({
            "is_header": False,
            "slug": comp.slug,
            "fa": comp.fa,
            "domain": comp.domain,
            "cells": cells,
        })
    return rows


# ── Hiring page context ──────────────────────────────────────────────────────

def _sum_resource_reading_hours(resources: list[RoadmapResource]) -> float:
    return sum(parse_reading_time_to_hours(r.reading_time) for r in resources)


async def get_hiring_context(db: AsyncSession) -> dict:
    """Build context dict for GET /path/hiring/."""
    hiring_lv = LEVEL_BY_SLUG["hiring"]

    # Fetch immigration videos from DB
    vid_stmt = select(ImmigrationVideo).order_by(ImmigrationVideo.sort_order.asc())
    vid_result = await db.execute(vid_stmt)
    immigration_videos = [
        {"title": v.title, "where": v.where or "", "url": v.url}
        for v in vid_result.scalars().all()
    ]

    # Fetch all L0 resources grouped by area_slug
    stmt = (
        select(RoadmapResource)
        .where(RoadmapResource.level_slug == "hiring")
        .order_by(RoadmapResource.sort_order.asc())
    )
    result = await db.execute(stmt)
    all_resources: list[RoadmapResource] = list(result.scalars().all())

    # Group resources by area_slug
    resources_by_area: dict[str, list[RoadmapResource]] = {}
    for r in all_resources:
        key = r.area_slug or "__no_area__"
        resources_by_area.setdefault(key, []).append(r)

    # Build area data with their phase
    phase_area_groups: list[dict] = []
    seen_phases: list[str] = []
    phase_map: dict[str, dict] = {}

    for area in L0_AREAS:
        phase = L0_PHASE_BY_SLUG[area.phase_slug]
        if area.phase_slug not in phase_map:
            phase_map[area.phase_slug] = {
                "phase": phase,
                "areas": [],
            }
            seen_phases.append(area.phase_slug)
        phase_map[area.phase_slug]["areas"].append({
            "area": area,
            "resources": resources_by_area.get(area.slug, []),
            "reading_display": format_reading_hours(
                _sum_resource_reading_hours(resources_by_area.get(area.slug, []))
            ),
        })

    phase_area_groups = [phase_map[slug] for slug in seen_phases]

    # Build map data for the visual "ایستگاه" section
    map_phases = []
    for phase in L0_PHASES:
        weeks = phase.end_week - phase.start_week + 1
        sprint_display = f"{phase.sprint} · هفته {_fa(phase.start_week)} تا {_fa(phase.end_week)}"
        map_phases.append({
            "n": phase.n,
            "fa": phase.fa,
            "sprint": sprint_display,
            "weeks": weeks,
            "is_phase2": phase.n == "۲",
        })

    cursor = 0
    map_areas = []
    for group in phase_area_groups:
        is_phase2 = group["phase"].n == "۲"
        for item in group["areas"]:
            area = item["area"]
            from_w = cursor + 1
            to_w = cursor + area.sprint_weeks
            cursor = to_w
            if from_w == to_w:
                week_range = f"هفته {_fa(from_w)}"
            else:
                week_range = f"هفته {_fa(from_w)}–{_fa(to_w)}"
            map_areas.append({
                "n": area.n,
                "name": area.name,
                "short": area.short,
                "sprint": f"{area.sprint_weeks} هفته",
                "weeks": area.sprint_weeks,
                "week_range": week_range,
                "is_phase2": is_phase2,
                "anchor_id": f"station-{area.n}",
            })

    # Stats for the hero aside
    total_reading_hours = sum(
        _sum_resource_reading_hours(resources_by_area.get(area.slug, []))
        for area in L0_AREAS
    )
    reading_fact = (
        f"~{format_reading_hours(total_reading_hours)}"
        if total_reading_hours > 0
        else "—"
    )
    facts = [
        {"label": "منابع اجباری", "value": "۹",           "accent": False},
        {"label": "مطالعه",       "value": reading_fact,  "accent": False},
        {"label": "زمان کار",     "value": "۱۲ هفته",      "accent": True},
        {"label": "طول مسیر",     "value": "۳ تا ۶ ماه",   "accent": True},
    ]

    return {
        "level": hiring_lv,
        "phases": L0_PHASES,
        "phase_area_groups": phase_area_groups,
        "audience": L0_AUDIENCE,
        "immigration_videos": immigration_videos,
        "levels_grid": L0_LEVELS_GRID,
        "map_phases": map_phases,
        "map_areas": map_areas,
        "facts": facts,
    }


# ── Level detail context ─────────────────────────────────────────────────────

async def get_level_context(db: AsyncSession, level_slug: str) -> Optional[dict]:
    """
    Build full context for a level detail page.
    Returns None if the slug is a stub (L2-L6 in v16).
    Returns 'stub' signal dict if slug is valid but not fully built.
    """
    if level_slug not in LEVEL_BY_SLUG:
        return None

    lv = LEVEL_BY_SLUG[level_slug]

    if level_slug in STUB_SLUGS:
        return {"is_stub": True, "level": lv}

    # ── Full page: APM ──────────────────────────────────────────────────────
    stmt = (
        select(RoadmapResource)
        .where(RoadmapResource.level_slug == level_slug)
        .order_by(RoadmapResource.sort_order.asc())
    )
    result = await db.execute(stmt)
    all_resources: list[RoadmapResource] = list(result.scalars().all())

    # Group by category
    resources_by_cat: dict[str, list[RoadmapResource]] = {}
    for r in all_resources:
        resources_by_cat.setdefault(r.category or "other", []).append(r)

    # Group core resources by competency
    core_competencies = []
    comp_data = APM_COMPETENCY_DATA if level_slug == "apm" else {}
    for slug, cd in comp_data.items():
        if cd.category != "core":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        depth = DEPTH_MATRIX[slug][0]  # index 0 = APM (level 1)
        resources = [
            r for r in resources_by_cat.get("core", [])
            if r.competency_slug == slug
        ]
        rationale = APM_CORE_RATIONALE.get(slug, {})
        core_competencies.append({
            "slug": slug,
            "fa": comp.fa,
            "depth": depth,
            "depth_label": DEPTH_LABELS.get(depth, ""),
            "is_habit": comp.is_habit,
            "sprint_weeks": cd.sprint_weeks,
            "maturation_months": cd.maturation_months,
            "reading_hours": cd.reading_hours,
            "reading_hours_display": format_reading_hours(cd.reading_hours),
            "resources": resources,
            "rationale": rationale.get("rationale", ""),
            "quote": rationale.get("quote", ""),
            "practice": rationale.get("practice", ""),
        })

    # Supporting competencies
    supporting_competencies = []
    for slug, cd in comp_data.items():
        if cd.category != "supporting":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        depth = DEPTH_MATRIX[slug][0]
        resources = [
            r for r in resources_by_cat.get("supporting", [])
            if r.competency_slug == slug
        ]
        detail = APM_SUPPORTING_DETAIL.get(slug, {})
        supporting_competencies.append({
            "slug": slug,
            "fa": comp.fa,
            "depth": depth,
            "depth_label": DEPTH_LABELS.get(depth, ""),
            "sprint_weeks": cd.sprint_weeks,
            "maturation_months": cd.maturation_months,
            "reading_hours": cd.reading_hours,
            "reading_hours_display": format_reading_hours(cd.reading_hours),
            "resources": resources,
            "owner_note": detail.get("owner_note", ""),
        })

    # Passive competencies
    passive_competencies = []
    for slug, cd in comp_data.items():
        if cd.category != "passive":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        depth = DEPTH_MATRIX[slug][0]
        passive_competencies.append({
            "slug": slug,
            "fa": comp.fa,
            "depth": depth,
            "depth_label": DEPTH_LABELS.get(depth, ""),
            "passive_how": cd.passive_how,
        })

    # Competency table (all non-passive for this level)
    asks_table = _build_asks_table(level_slug, comp_data)

    # Gantt data for sequence section
    sequence_gantt = _build_sequence_gantt(level_slug, comp_data)

    return {
        "is_stub": False,
        "level": lv,
        "texts": APM_TEXTS if level_slug == "apm" else {},
        "entry_resources": resources_by_cat.get("entry", []),
        "core_competencies": core_competencies,
        "supporting_competencies": supporting_competencies,
        "passive_competencies": passive_competencies,
        "bridge_resources": resources_by_cat.get("bridge", []),
        "bridge_checklist": APM_BRIDGE_CHECKLIST if level_slug == "apm" else [],
        "asks_table": asks_table,
        "sequence_gantt": sequence_gantt,
        "levels": LEVELS,
        "depth_labels": DEPTH_LABELS,
    }


def _build_asks_table(level_slug: str, comp_data: dict) -> list[dict]:
    """Build rows for the 'what this level asks' competency table."""
    level_idx = {"apm": 0, "pm": 1, "senior-pm": 2, "lead": 3, "director": 4, "cpo": 5}
    idx = level_idx.get(level_slug, 0)

    CATEGORY_FA = {
        "entry": "ورود",
        "core": "هسته",
        "supporting": "حمایتی",
        "bridge": "پل",
        "passive": "رایگان",
    }
    rows = []
    for slug, cd in comp_data.items():
        if cd.category == "passive":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        depth = DEPTH_MATRIX[slug][idx]
        rows.append({
            "slug": slug,
            "fa": comp.fa,
            "depth": depth,
            "depth_label": DEPTH_LABELS.get(depth, ""),
            "category": cd.category,
            "category_fa": CATEGORY_FA.get(cd.category, ""),
            "sprint_weeks": cd.sprint_weeks,
            "maturation_months": cd.maturation_months,
            "reading_hours": cd.reading_hours,
            "reading_hours_display": format_reading_hours(cd.reading_hours),
        })
    return rows


def _build_sequence_gantt(level_slug: str, comp_data: dict) -> list[dict]:
    """Build Gantt bars for the sequence section (core competencies only)."""
    week_cursor = 1
    bars = []
    for slug, cd in comp_data.items():
        if cd.category != "core":
            continue
        comp = COMPETENCY_BY_SLUG[slug]
        start = week_cursor
        end = week_cursor + cd.sprint_weeks - 1
        bars.append({
            "slug": slug,
            "fa": comp.fa,
            "start_week": start,
            "end_week": end,
            "sprint_weeks": cd.sprint_weeks,
            "maturation_months": cd.maturation_months,
        })
        week_cursor = end + 1
    return bars


# ── Admin queries ─────────────────────────────────────────────────────────────

async def get_roadmap_resources(
    db: AsyncSession,
    level_slug: Optional[str] = None,
) -> list[RoadmapResource]:
    stmt = (
        select(RoadmapResource)
        .order_by(RoadmapResource.level_slug, RoadmapResource.sort_order)
    )
    if level_slug:
        stmt = stmt.where(RoadmapResource.level_slug == level_slug)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_resource(db: AsyncSession, resource_id: int) -> RoadmapResource:
    stmt = select(RoadmapResource).where(RoadmapResource.id == resource_id)
    result = await db.execute(stmt)
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


async def create_resource(db: AsyncSession, data: dict) -> RoadmapResource:
    resource = RoadmapResource(**data)
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource


async def update_resource(
    db: AsyncSession, resource_id: int, data: dict
) -> RoadmapResource:
    resource = await get_resource(db, resource_id)
    for key, value in data.items():
        setattr(resource, key, value)
    await db.commit()
    await db.refresh(resource)
    return resource


async def delete_resource(db: AsyncSession, resource_id: int) -> None:
    resource = await get_resource(db, resource_id)
    await db.delete(resource)
    await db.commit()


async def get_missing_links(db: AsyncSession) -> list[RoadmapResource]:
    """Return all resources with neither external_url nor book_id."""
    stmt = (
        select(RoadmapResource)
        .where(
            RoadmapResource.external_url.is_(None),
            RoadmapResource.book_id.is_(None),
        )
        .order_by(RoadmapResource.level_slug, RoadmapResource.sort_order)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ── Immigration video CRUD ────────────────────────────────────────────────────

async def get_immigration_videos(db: AsyncSession) -> list[ImmigrationVideo]:
    stmt = select(ImmigrationVideo).order_by(ImmigrationVideo.sort_order.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_immigration_video(db: AsyncSession, video_id: int) -> ImmigrationVideo:
    stmt = select(ImmigrationVideo).where(ImmigrationVideo.id == video_id)
    result = await db.execute(stmt)
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Immigration video not found")
    return video


async def create_immigration_video(db: AsyncSession, data: dict) -> ImmigrationVideo:
    video = ImmigrationVideo(**data)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video


async def update_immigration_video(
    db: AsyncSession, video_id: int, data: dict
) -> ImmigrationVideo:
    video = await get_immigration_video(db, video_id)
    for key, value in data.items():
        setattr(video, key, value)
    await db.commit()
    await db.refresh(video)
    return video


async def delete_immigration_video(db: AsyncSession, video_id: int) -> None:
    video = await get_immigration_video(db, video_id)
    await db.delete(video)
    await db.commit()


async def count_missing_links(db: AsyncSession) -> int:
    stmt = (
        select(func.count(RoadmapResource.id))
        .where(
            RoadmapResource.external_url.is_(None),
            RoadmapResource.book_id.is_(None),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()
