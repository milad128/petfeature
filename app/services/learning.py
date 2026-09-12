"""Learning enrollment and resource progress (v17)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import jdatetime
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jalali import format_jalali, to_fa_digits
from app.models.learning import (
    BADGE_COMPLETED,
    BADGE_ENROLLED,
    BADGE_LABELS,
    BADGE_PROGRESS,
    PROGRESS_STATUSES,
    STATUS_LABELS,
    VALID_STATUSES,
    Enrollment,
    ResourceProgress,
    ResourceRating,
)
from app.models.page_view import PageView
from app.models.roadmap import RoadmapResource
from app.models.user import User
from app.services.roadmap_data import FULL_PAGE_SLUGS, L0_AREAS, LEVEL_BY_SLUG

ENROLLABLE_SLUGS = frozenset(FULL_PAGE_SLUGS) | {"hiring"}
ENROLLABLE_ORDER = ("hiring", *sorted(FULL_PAGE_SLUGS))
STALLED_DAYS = 14
ADMIN_LIST_PER_PAGE = 50
ADMIN_STALLED_LIMIT = 20
ADMIN_PERIODS = ("7", "30", "90", "all")
ADMIN_STATES = ("active", "learning", "completed", "unenrolled", "all")
STATE_LABELS = {
    "active": "فعال",
    "learning": "در حال یادگیری",
    "completed": "تکمیل‌شده",
    "unenrolled": "لغوشده",
    "all": "همه",
}

CATEGORY_FA = {
    "entry": "ورود",
    "core": "هسته",
    "supporting": "حمایتی",
    "bridge": "پل",
}

_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_fa(n: int) -> str:
    return str(n).translate(_FA)


def is_enrollable(level_slug: str) -> bool:
    return level_slug in ENROLLABLE_SLUGS


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def badge_for_pct(pct: int) -> str:
    if pct >= 100:
        return BADGE_COMPLETED
    if pct >= 50:
        return BADGE_PROGRESS
    return BADGE_ENROLLED


@dataclass
class Progress:
    done: int
    required: int
    studying: int
    blank: int
    pct: int
    badge: str
    skipped: int = 0

    @property
    def badge_fa(self) -> str:
        return BADGE_LABELS[self.badge]

    def as_dict(self) -> dict:
        return {
            "done": self.done,
            "required": self.required,
            "studying": self.studying,
            "blank": self.blank,
            "skipped": self.skipped,
            "pct": self.pct,
            "badge": self.badge,
            "badge_fa": self.badge_fa,
            "done_fa": to_fa(self.done),
            "required_fa": to_fa(self.required),
            "studying_fa": to_fa(self.studying),
            "blank_fa": to_fa(self.blank),
            "skipped_fa": to_fa(self.skipped),
            "pct_fa": to_fa(self.pct),
        }


@dataclass
class StatusUpdate:
    row: ResourceProgress | None
    prompt_rating: bool
    resource_id: int


@dataclass
class EnrollmentCard:
    enrollment: Enrollment
    level_slug: str
    level_fa: str
    level_num: str
    progress: Progress


def _progress_from_resources(
    resources: list[RoadmapResource],
    status_by_id: dict[int, str],
) -> Progress:
    done = 0
    required = 0
    studying = 0
    blank = 0
    skipped = 0
    for r in resources:
        status = status_by_id.get(r.id, "")
        if status == "STUDYING":
            studying += 1
        if status == "SKIPPED":
            skipped += 1
        if r.is_required:
            required += 1
            if status in PROGRESS_STATUSES:
                done += 1
            elif not status:
                blank += 1
    pct = round((done / required) * 100) if required else 0
    return Progress(
        done=done,
        required=required,
        studying=studying,
        blank=blank,
        skipped=skipped,
        pct=pct,
        badge=badge_for_pct(pct),
    )


async def _resources_for_level(
    db: AsyncSession, level_slug: str
) -> list[RoadmapResource]:
    result = await db.execute(
        select(RoadmapResource)
        .where(RoadmapResource.level_slug == level_slug)
        .order_by(RoadmapResource.sort_order.asc(), RoadmapResource.id.asc())
    )
    return list(result.scalars().all())


async def _progress_row_map(
    db: AsyncSession, enrollment_id: int
) -> dict[int, ResourceProgress]:
    result = await db.execute(
        select(ResourceProgress).where(
            ResourceProgress.enrollment_id == enrollment_id
        )
    )
    return {row.roadmap_resource_id: row for row in result.scalars().all()}


async def _status_map(
    db: AsyncSession, enrollment_id: int
) -> dict[int, str]:
    rows = await _progress_row_map(db, enrollment_id)
    return {rid: row.status for rid, row in rows.items()}


async def get_enrollment(
    db: AsyncSession, user_id: int, level_slug: str
) -> Optional[Enrollment]:
    return await db.scalar(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.level_slug == level_slug,
            Enrollment.unenrolled_at.is_(None),
        )
    )


async def get_or_create_enrollment(
    db: AsyncSession, user_id: int, level_slug: str
) -> Enrollment:
    if not is_enrollable(level_slug):
        raise ValueError("level_not_enrollable")

    row = await db.scalar(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.level_slug == level_slug,
        )
    )
    if row is None:
        row = Enrollment(user_id=user_id, level_slug=level_slug)
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    if row.unenrolled_at is not None:
        row.unenrolled_at = None
        await db.commit()
        await db.refresh(row)
    return row


async def unenroll(db: AsyncSession, user_id: int, level_slug: str) -> bool:
    row = await get_enrollment(db, user_id, level_slug)
    if row is None:
        return False
    row.unenrolled_at = _utcnow()
    await db.commit()
    return True


async def compute_progress(db: AsyncSession, enrollment: Enrollment) -> Progress:
    resources = await _resources_for_level(db, enrollment.level_slug)
    status_by_id = await _status_map(db, enrollment.id)
    return _progress_from_resources(resources, status_by_id)


async def _maybe_complete(db: AsyncSession, enrollment: Enrollment) -> None:
    progress = await compute_progress(db, enrollment)
    if progress.pct >= 100 and enrollment.completed_at is None:
        enrollment.completed_at = _utcnow()
        await db.commit()


async def _user_stars_map(
    db: AsyncSession, user_id: int, resource_ids: list[int]
) -> dict[int, int]:
    if not resource_ids:
        return {}
    result = await db.execute(
        select(ResourceRating).where(
            ResourceRating.user_id == user_id,
            ResourceRating.roadmap_resource_id.in_(resource_ids),
        )
    )
    return {row.roadmap_resource_id: row.stars for row in result.scalars().all()}


async def _has_rating(db: AsyncSession, user_id: int, resource_id: int) -> bool:
    row_id = await db.scalar(
        select(ResourceRating.id).where(
            ResourceRating.user_id == user_id,
            ResourceRating.roadmap_resource_id == resource_id,
        )
    )
    return row_id is not None


async def rating_stats_by_resource_ids(
    db: AsyncSession, resource_ids: list[int]
) -> dict[int, tuple[float, int]]:
    """Return {resource_id: (avg rounded to 1 decimal, vote count)}."""
    if not resource_ids:
        return {}
    result = await db.execute(
        select(
            ResourceRating.roadmap_resource_id,
            func.avg(ResourceRating.stars),
            func.count(),
        )
        .where(ResourceRating.roadmap_resource_id.in_(resource_ids))
        .group_by(ResourceRating.roadmap_resource_id)
    )
    stats: dict[int, tuple[float, int]] = {}
    for resource_id, avg, count in result.all():
        stats[int(resource_id)] = (round(float(avg), 1), int(count))
    return stats


def apply_rating_stats(
    resources: list[RoadmapResource],
    stats: dict[int, tuple[float, int]],
) -> None:
    for resource in resources:
        pair = stats.get(resource.id)
        resource._avg_stars = pair[0] if pair else None  # type: ignore[attr-defined]
        resource._rating_count = pair[1] if pair else 0  # type: ignore[attr-defined]


async def upsert_resource_rating(
    db: AsyncSession,
    user_id: int,
    level_slug: str,
    resource_id: int,
    stars: int,
) -> ResourceRating:
    if stars not in (1, 2, 3, 4, 5):
        raise ValueError("invalid_stars")
    if not is_enrollable(level_slug):
        raise ValueError("bad_resource")

    enrollment = await get_enrollment(db, user_id, level_slug)
    if enrollment is None:
        raise ValueError("not_enrolled")

    resource = await db.get(RoadmapResource, resource_id)
    if resource is None or resource.level_slug != enrollment.level_slug:
        raise ValueError("bad_resource")

    row = await db.scalar(
        select(ResourceRating).where(
            ResourceRating.user_id == user_id,
            ResourceRating.roadmap_resource_id == resource_id,
        )
    )
    now = _utcnow()
    if row is None:
        row = ResourceRating(
            user_id=user_id,
            roadmap_resource_id=resource_id,
            stars=stars,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
    else:
        row.stars = stars
        row.updated_at = now
    await db.commit()
    await db.refresh(row)
    return row


async def set_resource_status(
    db: AsyncSession,
    enrollment_id: int,
    resource_id: int,
    status: str,
) -> StatusUpdate:
    status = (status or "").strip()
    if status and status not in VALID_STATUSES:
        raise ValueError("invalid_status")

    enrollment = await db.get(Enrollment, enrollment_id)
    if enrollment is None or not enrollment.is_active:
        raise ValueError("no_enrollment")

    resource = await db.get(RoadmapResource, resource_id)
    if resource is None or resource.level_slug != enrollment.level_slug:
        raise ValueError("bad_resource")

    row = await db.scalar(
        select(ResourceProgress).where(
            ResourceProgress.enrollment_id == enrollment_id,
            ResourceProgress.roadmap_resource_id == resource_id,
        )
    )
    previous = row.status if row is not None else ""
    if not status:
        if row is not None:
            await db.delete(row)
            await db.commit()
        await _maybe_complete(db, enrollment)
        return StatusUpdate(row=None, prompt_rating=False, resource_id=resource_id)

    if row is None:
        row = ResourceProgress(
            enrollment_id=enrollment_id,
            roadmap_resource_id=resource_id,
            status=status,
        )
        db.add(row)
    else:
        row.status = status
    await db.commit()
    await db.refresh(row)
    await db.refresh(enrollment)
    await _maybe_complete(db, enrollment)

    prompt_rating = False
    if status in PROGRESS_STATUSES and previous != status:
        prompt_rating = not await _has_rating(
            db, enrollment.user_id, resource_id
        )
    return StatusUpdate(
        row=row, prompt_rating=prompt_rating, resource_id=resource_id
    )


async def list_resources_with_status(
    db: AsyncSession,
    level_slug: str,
    enrollment: Optional[Enrollment],
) -> list[RoadmapResource]:
    """Return v16-ordered resources. Status is attached as `_status` when enrolled."""
    resources = await _resources_for_level(db, level_slug)
    row_map: dict[int, ResourceProgress] = {}
    stars_map: dict[int, int] = {}
    if enrollment is not None:
        row_map = await _progress_row_map(db, enrollment.id)
        stars_map = await _user_stars_map(
            db, enrollment.user_id, [r.id for r in resources]
        )
    for r in resources:
        row = row_map.get(r.id)
        r._status = row.status if row else ""  # type: ignore[attr-defined]
        r._status_updated_at = row.updated_at if row else None  # type: ignore[attr-defined]
        r._stars = stars_map.get(r.id)  # type: ignore[attr-defined]
    return resources


def group_resources(resources: list[RoadmapResource]) -> list[dict]:
    if resources and resources[0].level_slug == "hiring":
        area_fa = {a.slug: a.name for a in L0_AREAS}
        groups: dict[str, list[RoadmapResource]] = {}
        order: list[str] = []
        for r in resources:
            key = r.area_slug or "_other"
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(r)
        return [
            {"key": key, "title": area_fa.get(key, "منابع"), "resources": groups[key]}
            for key in order
        ]

    groups = {}
    order = []
    for r in resources:
        key = r.category or "other"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(r)
    preferred = ["entry", "core", "supporting", "bridge"]
    ordered = [k for k in preferred if k in groups] + [
        k for k in order if k not in preferred
    ]
    return [
        {"key": key, "title": CATEGORY_FA.get(key, key), "resources": groups[key]}
        for key in ordered
    ]


async def get_active_enrollments(
    db: AsyncSession, user_id: int
) -> list[EnrollmentCard]:
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == user_id, Enrollment.unenrolled_at.is_(None))
        .order_by(Enrollment.enrolled_at.desc())
    )
    rows = list(result.scalars().all())
    cards: list[EnrollmentCard] = []
    for row in rows:
        lv = LEVEL_BY_SLUG.get(row.level_slug)
        progress = await compute_progress(db, row)
        cards.append(
            EnrollmentCard(
                enrollment=row,
                level_slug=row.level_slug,
                level_fa=lv.fa if lv else row.level_slug,
                level_num=lv.num if lv else "",
                progress=progress,
            )
        )
    return cards


async def level_social_counts(db: AsyncSession, level_slug: str) -> dict[str, int]:
    learning = await db.scalar(
        select(func.count())
        .select_from(Enrollment)
        .where(
            Enrollment.level_slug == level_slug,
            Enrollment.unenrolled_at.is_(None),
            Enrollment.completed_at.is_(None),
        )
    )
    completed = await db.scalar(
        select(func.count())
        .select_from(Enrollment)
        .where(
            Enrollment.level_slug == level_slug,
            Enrollment.unenrolled_at.is_(None),
            Enrollment.completed_at.is_not(None),
        )
    )
    return {"learning": int(learning or 0), "completed": int(completed or 0)}


async def enroll_counts_by_level(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Enrollment.level_slug, Enrollment.unenrolled_at, Enrollment.completed_at)
    )
    by_slug: dict[str, dict[str, int]] = {}
    for slug, unenrolled_at, completed_at in result:
        bucket = by_slug.setdefault(slug, {"active": 0, "completed": 0})
        if unenrolled_at is None:
            bucket["active"] += 1
            if completed_at is not None:
                bucket["completed"] += 1
    out = []
    for slug in ENROLLABLE_ORDER:
        lv = LEVEL_BY_SLUG.get(slug)
        counts = by_slug.get(slug, {"active": 0, "completed": 0})
        out.append(
            {
                "slug": slug,
                "fa": lv.fa if lv else slug,
                "active": counts["active"],
                "completed": counts["completed"],
            }
        )
    return out


# ── Admin (v18) ────────────────────────────────────────────────────────────


def enrollable_levels() -> list[dict]:
    out = []
    for slug in ENROLLABLE_ORDER:
        lv = LEVEL_BY_SLUG.get(slug)
        out.append(
            {
                "slug": slug,
                "fa": lv.fa if lv else slug,
                "num": lv.num if lv else "",
            }
        )
    return out


def public_path_for(level_slug: str) -> str:
    return f"/path/{level_slug}/"


def _level_fa(slug: str) -> str:
    lv = LEVEL_BY_SLUG.get(slug)
    return lv.fa if lv else slug


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _period_start(period_days: Optional[int]) -> Optional[datetime]:
    if period_days is None:
        return None
    return datetime.now(timezone.utc) - timedelta(days=period_days)


def _in_period(dt: Optional[datetime], start: Optional[datetime]) -> bool:
    if dt is None:
        return False
    if start is None:
        return True
    left, right = _aware(dt), _aware(start)
    return left is not None and right is not None and left >= right


def _older_than(dt: Optional[datetime], cutoff: datetime) -> bool:
    left, right = _aware(dt), _aware(cutoff)
    return left is not None and right is not None and left < right


def _row_state(enrollment: Enrollment) -> str:
    if enrollment.unenrolled_at is not None:
        return "unenrolled"
    if enrollment.completed_at is not None:
        return "completed"
    return "learning"


def _jalali_bucket(dt: datetime, *, months: bool) -> tuple[str, str]:
    aware = _aware(dt) or dt
    naive = aware.replace(tzinfo=None)
    j = jdatetime.datetime.fromgregorian(datetime=naive)
    if months:
        label = to_fa_digits(f"{jdatetime.date.j_months_fa[j.month - 1]} {j.year}")
        return f"{j.year:04d}-{j.month:02d}", label
    return naive.date().isoformat(), format_jalali(naive)


def admin_list_query_string(
    *,
    level: str = "",
    state: str = "active",
    q: str = "",
    page: Optional[int] = None,
) -> str:
    params: list[tuple[str, str]] = []
    if level:
        params.append(("level", level))
    if state and state != "active":
        params.append(("state", state))
    if q:
        params.append(("q", q))
    if page and page > 1:
        params.append(("page", str(page)))
    return urlencode(params)


async def _resources_by_level(
    db: AsyncSession, slugs: set[str]
) -> dict[str, list[RoadmapResource]]:
    if not slugs:
        return {}
    result = await db.execute(
        select(RoadmapResource).where(RoadmapResource.level_slug.in_(slugs))
    )
    by_level: dict[str, list[RoadmapResource]] = {slug: [] for slug in slugs}
    for row in result.scalars():
        by_level.setdefault(row.level_slug, []).append(row)
    return by_level


async def _progress_rows_by_enrollment(
    db: AsyncSession, enrollment_ids: list[int]
) -> dict[int, list[ResourceProgress]]:
    by_id: dict[int, list[ResourceProgress]] = {eid: [] for eid in enrollment_ids}
    if not enrollment_ids:
        return by_id
    result = await db.execute(
        select(ResourceProgress).where(
            ResourceProgress.enrollment_id.in_(enrollment_ids)
        )
    )
    for row in result.scalars():
        by_id.setdefault(row.enrollment_id, []).append(row)
    return by_id


def _progress_from_maps(
    enrollment_id: int,
    level_slug: str,
    resources_by_level: dict[str, list[RoadmapResource]],
    rows_by_enrollment: dict[int, list[ResourceProgress]],
) -> Progress:
    resources = resources_by_level.get(level_slug, [])
    status_by_id = {
        row.roadmap_resource_id: row.status
        for row in rows_by_enrollment.get(enrollment_id, [])
    }
    return _progress_from_resources(resources, status_by_id)


def _last_progress_at(
    rows: list[ResourceProgress],
) -> Optional[datetime]:
    times = [row.updated_at for row in rows if row.updated_at is not None]
    return max(times) if times else None


async def _path_views_by_slug(
    db: AsyncSession, start: Optional[datetime]
) -> dict[str, int]:
    filters = [PageView.path.like("/path/%")]
    if start is not None:
        filters.append(PageView.created_at >= start)
    result = await db.execute(
        select(PageView.path, func.count())
        .where(*filters)
        .group_by(PageView.path)
    )
    counts: dict[str, int] = {}
    for path, n in result:
        slug = (path or "").removeprefix("/path/").strip("/")
        if slug and "/" not in slug:
            counts[slug] = counts.get(slug, 0) + int(n)
    return counts


async def admin_headline_counts(db: AsyncSession) -> dict[str, int]:
    active = await db.scalar(
        select(func.count())
        .select_from(Enrollment)
        .where(Enrollment.unenrolled_at.is_(None))
    )
    completed = await db.scalar(
        select(func.count())
        .select_from(Enrollment)
        .where(
            Enrollment.unenrolled_at.is_(None),
            Enrollment.completed_at.is_not(None),
        )
    )
    unique_learners = await db.scalar(
        select(func.count(func.distinct(Enrollment.user_id))).where(
            Enrollment.unenrolled_at.is_(None)
        )
    )
    return {
        "active": int(active or 0),
        "completed": int(completed or 0),
        "unique_learners": int(unique_learners or 0),
    }


async def admin_overview(
    db: AsyncSession, period_days: Optional[int]
) -> dict:
    start = _period_start(period_days)
    stalled_cutoff = datetime.now(timezone.utc) - timedelta(days=STALLED_DAYS)
    bucket_months = period_days is None

    enroll_result = await db.execute(
        select(
            Enrollment.id,
            Enrollment.user_id,
            Enrollment.level_slug,
            Enrollment.enrolled_at,
            Enrollment.completed_at,
            Enrollment.unenrolled_at,
        )
    )
    enroll_rows = list(enroll_result.all())

    snapshot = {
        "active": 0,
        "learning": 0,
        "completed": 0,
        "unenrolled": 0,
        "unique_learners": 0,
        "avg_progress": None,
    }
    period = {
        "days": period_days,
        "new_enrolls": 0,
        "new_completions": 0,
        "new_unenrolls": 0,
    }
    per_level = {
        slug: {
            "slug": slug,
            "fa": _level_fa(slug),
            "new_enrolls": 0,
            "active": 0,
            "learning": 0,
            "completed": 0,
            "unenrolled": 0,
            "avg_progress": None,
            "views": 0,
            "conversion": None,
        }
        for slug in ENROLLABLE_ORDER
    }
    unique_ids: set[int] = set()
    active_incomplete: list[tuple] = []
    series_enrolls: dict[str, tuple[str, int]] = {}
    series_done: dict[str, tuple[str, int]] = {}

    for row in enroll_rows:
        eid, user_id, slug, enrolled_at, completed_at, unenrolled_at = row
        bucket = per_level.get(slug)
        if _in_period(enrolled_at, start):
            period["new_enrolls"] += 1
            if bucket is not None:
                bucket["new_enrolls"] += 1
            key, label = _jalali_bucket(enrolled_at, months=bucket_months)
            prev = series_enrolls.get(key)
            series_enrolls[key] = (label, (prev[1] if prev else 0) + 1)
        if _in_period(completed_at, start):
            period["new_completions"] += 1
            key, label = _jalali_bucket(completed_at, months=bucket_months)
            prev = series_done.get(key)
            series_done[key] = (label, (prev[1] if prev else 0) + 1)
        if _in_period(unenrolled_at, start):
            period["new_unenrolls"] += 1

        if unenrolled_at is not None:
            snapshot["unenrolled"] += 1
            if bucket is not None:
                bucket["unenrolled"] += 1
            continue

        snapshot["active"] += 1
        unique_ids.add(user_id)
        if bucket is not None:
            bucket["active"] += 1
        if completed_at is None:
            snapshot["learning"] += 1
            if bucket is not None:
                bucket["learning"] += 1
            active_incomplete.append(row)
        else:
            snapshot["completed"] += 1
            if bucket is not None:
                bucket["completed"] += 1

    snapshot["unique_learners"] = len(unique_ids)

    incomplete_ids = [row[0] for row in active_incomplete]
    incomplete_slugs = {row[2] for row in active_incomplete}
    resources_by_level = await _resources_by_level(db, incomplete_slugs)
    rows_by_enrollment = await _progress_rows_by_enrollment(db, incomplete_ids)

    progress_by_id: dict[int, Progress] = {}
    pcts: list[int] = []
    pcts_by_level: dict[str, list[int]] = {}
    for row in active_incomplete:
        progress = _progress_from_maps(
            row[0], row[2], resources_by_level, rows_by_enrollment
        )
        progress_by_id[row[0]] = progress
        pcts.append(progress.pct)
        pcts_by_level.setdefault(row[2], []).append(progress.pct)

    snapshot["avg_progress"] = round(sum(pcts) / len(pcts)) if pcts else None
    for slug, values in pcts_by_level.items():
        if slug in per_level and values:
            per_level[slug]["avg_progress"] = round(sum(values) / len(values))

    views_by_slug = await _path_views_by_slug(db, start)
    for slug, bucket in per_level.items():
        views = int(views_by_slug.get(slug, 0))
        bucket["views"] = views
        if views:
            bucket["conversion"] = round((bucket["new_enrolls"] / views) * 100)

    keys = set(series_enrolls) | set(series_done)
    series = []
    for key in sorted(keys, reverse=True):
        enroll_label, enroll_n = series_enrolls.get(key, ("", 0))
        done_label, done_n = series_done.get(key, ("", 0))
        series.append(
            {
                "key": key,
                "label": enroll_label or done_label,
                "enrolls": enroll_n,
                "completions": done_n,
            }
        )

    active_result = await db.execute(
        select(Enrollment.id, Enrollment.level_slug).where(
            Enrollment.unenrolled_at.is_(None)
        )
    )
    active_pairs = list(active_result.all())
    active_ids = [row[0] for row in active_pairs]
    active_slugs = {row[1] for row in active_pairs}
    resource_counts = {slug: 0 for slug in active_slugs}
    if active_slugs:
        count_rows = await db.execute(
            select(RoadmapResource.level_slug, func.count())
            .where(RoadmapResource.level_slug.in_(active_slugs))
            .group_by(RoadmapResource.level_slug)
        )
        for slug, n in count_rows:
            resource_counts[slug] = int(n)
    mix_counts = {status: 0 for status in STATUS_LABELS}
    progress_total = 0
    if active_ids:
        mix_rows = await db.execute(
            select(ResourceProgress.status, func.count())
            .where(ResourceProgress.enrollment_id.in_(active_ids))
            .group_by(ResourceProgress.status)
        )
        for status, n in mix_rows:
            if status in mix_counts:
                mix_counts[status] = int(n)
            progress_total += int(n)
    expected_slots = sum(resource_counts.get(slug, 0) for _, slug in active_pairs)
    blank_count = max(0, expected_slots - progress_total)
    status_mix = [
        {"key": "blank", "fa": "بدون وضعیت", "count": blank_count},
        {"key": "STUDYING", "fa": STATUS_LABELS["STUDYING"], "count": mix_counts["STUDYING"]},
        {"key": "DONE", "fa": STATUS_LABELS["DONE"], "count": mix_counts["DONE"]},
        {
            "key": "ALREADY_KNEW",
            "fa": STATUS_LABELS["ALREADY_KNEW"],
            "count": mix_counts["ALREADY_KNEW"],
        },
        {"key": "SKIPPED", "fa": STATUS_LABELS["SKIPPED"], "count": mix_counts["SKIPPED"]},
    ]

    stalled_candidates = [
        row
        for row in active_incomplete
        if _older_than(row[3], stalled_cutoff)
        and progress_by_id.get(row[0], Progress(0, 0, 0, 0, 0, BADGE_ENROLLED)).pct == 0
    ]
    stalled_candidates.sort(key=lambda row: _aware(row[3]) or datetime.min.replace(tzinfo=timezone.utc))
    stalled_candidates = stalled_candidates[:ADMIN_STALLED_LIMIT]
    stalled_user_ids = {row[1] for row in stalled_candidates}
    names: dict[int, str] = {}
    if stalled_user_ids:
        users = await db.execute(select(User.id, User.name).where(User.id.in_(stalled_user_ids)))
        names = {uid: name for uid, name in users}
    stalled = [
        {
            "id": row[0],
            "user_name": names.get(row[1], "—"),
            "level_slug": row[2],
            "level_fa": _level_fa(row[2]),
            "enrolled_at": row[3],
        }
        for row in stalled_candidates
    ]

    return {
        "snapshot": snapshot,
        "period": period,
        "levels": [per_level[slug] for slug in ENROLLABLE_ORDER],
        "show_conversion": True,
        "series": series,
        "series_bucket": "month" if bucket_months else "day",
        "status_mix": status_mix,
        "stalled": stalled,
    }


def _apply_admin_list_filters(stmt, *, level: str, state: str, q: str):
    if level and level in ENROLLABLE_SLUGS:
        stmt = stmt.where(Enrollment.level_slug == level)
    if state == "active":
        stmt = stmt.where(Enrollment.unenrolled_at.is_(None))
    elif state == "learning":
        stmt = stmt.where(
            Enrollment.unenrolled_at.is_(None),
            Enrollment.completed_at.is_(None),
        )
    elif state == "completed":
        stmt = stmt.where(
            Enrollment.unenrolled_at.is_(None),
            Enrollment.completed_at.is_not(None),
        )
    elif state == "unenrolled":
        stmt = stmt.where(Enrollment.unenrolled_at.is_not(None))
    if q:
        term = f"%{q}%"
        stmt = stmt.where(or_(User.name.ilike(term), User.email.ilike(term)))
    return stmt


async def admin_list_enrollments(
    db: AsyncSession,
    *,
    level: str = "",
    state: str = "active",
    q: str = "",
    page: int = 1,
    per_page: int = ADMIN_LIST_PER_PAGE,
) -> dict:
    if state not in ADMIN_STATES:
        state = "active"
    if level not in ENROLLABLE_SLUGS:
        level = ""
    q = (q or "").strip()
    page = max(1, page)

    base = select(Enrollment, User).join(User, User.id == Enrollment.user_id)
    filtered = _apply_admin_list_filters(base, level=level, state=state, q=q)
    count_base = (
        select(func.count())
        .select_from(Enrollment)
        .join(User, User.id == Enrollment.user_id)
    )
    count_stmt = _apply_admin_list_filters(count_base, level=level, state=state, q=q)
    total = int(await db.scalar(count_stmt) or 0)
    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1

    result = await db.execute(
        filtered.order_by(Enrollment.enrolled_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    pairs = list(result.all())
    enrollments = [enrollment for enrollment, _user in pairs]
    resources_by_level = await _resources_by_level(
        db, {row.level_slug for row in enrollments}
    )
    rows_by_enrollment = await _progress_rows_by_enrollment(
        db, [row.id for row in enrollments]
    )

    rows = []
    for enrollment, user in pairs:
        progress = _progress_from_maps(
            enrollment.id,
            enrollment.level_slug,
            resources_by_level,
            rows_by_enrollment,
        )
        state_key = _row_state(enrollment)
        rows.append(
            {
                "id": enrollment.id,
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "level_slug": enrollment.level_slug,
                "level_fa": _level_fa(enrollment.level_slug),
                "enrolled_at": enrollment.enrolled_at,
                "last_progress_at": _last_progress_at(
                    rows_by_enrollment.get(enrollment.id, [])
                ),
                "progress": progress,
                "badge_fa": None if state_key == "unenrolled" else progress.badge_fa,
                "state": state_key,
                "state_fa": STATE_LABELS[state_key],
            }
        )

    return {
        "rows": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "level": level,
        "state": state,
        "q": q,
    }


async def admin_get_enrollment(
    db: AsyncSession, enrollment_id: int
) -> Optional[dict]:
    enrollment = await db.get(Enrollment, enrollment_id)
    if enrollment is None:
        return None
    user = await db.get(User, enrollment.user_id)
    resources = await list_resources_with_status(
        db, enrollment.level_slug, enrollment
    )
    progress = _progress_from_resources(
        resources,
        {r.id: getattr(r, "_status", "") for r in resources},
    )
    lv = LEVEL_BY_SLUG.get(enrollment.level_slug)
    state_key = _row_state(enrollment)
    return {
        "enrollment": enrollment,
        "user": user,
        "level_slug": enrollment.level_slug,
        "level_fa": lv.fa if lv else enrollment.level_slug,
        "level_num": lv.num if lv else "",
        "public_path": public_path_for(enrollment.level_slug),
        "progress": progress,
        "groups": group_resources(resources),
        "state": state_key,
        "state_fa": STATE_LABELS[state_key],
        "badge_fa": None if state_key == "unenrolled" else progress.badge_fa,
    }
