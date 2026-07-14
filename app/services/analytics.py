"""Analytics query functions for the admin dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jalali import format_jalali
from app.models.book import Book
from app.models.page_view import PageView
from app.models.post import Post
from app.models.tool import Tool


def period_cutoff(period: str) -> Optional[datetime]:
    """Return the UTC datetime for the start of the selected period, or None for 'all'."""
    now = datetime.utcnow()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "7d":
        return now - timedelta(days=7)
    if period == "30d":
        return now - timedelta(days=30)
    return None  # 'all'


def _base_query(period: str):
    """Base PageView select with optional period filter applied."""
    cutoff = period_cutoff(period)
    filters = []
    if cutoff:
        filters.append(PageView.created_at >= cutoff)
    return filters


# ── Summary cards ─────────────────────────────────────────────────────────

async def get_summary(session: AsyncSession, period: str) -> dict:
    filters = _base_query(period)

    total = await session.execute(
        select(func.count(PageView.id)).where(*filters)
    )
    total_views = total.scalar() or 0

    unique = await session.execute(
        select(func.count(distinct(PageView.visitor_token))).where(*filters)
    )
    unique_visitors = unique.scalar() or 0

    # Busiest day
    day_col = func.date(PageView.created_at)
    busiest_q = (
        select(day_col.label("day"), func.count(PageView.id).label("cnt"))
        .where(*filters)
        .group_by(day_col)
        .order_by(func.count(PageView.id).desc())
        .limit(1)
    )
    busiest_row = (await session.execute(busiest_q)).first()
    busiest_day = ""
    if busiest_row:
        # Convert the date string/object to Jalali
        day_val = busiest_row[0]
        if day_val:
            try:
                if isinstance(day_val, str):
                    from datetime import date
                    day_date = datetime.strptime(day_val[:10], "%Y-%m-%d").date()
                elif isinstance(day_val, datetime):
                    day_date = day_val.date()
                else:
                    day_date = day_val
                busiest_day = format_jalali(day_date)
            except Exception:
                busiest_day = str(day_val)

    return {
        "total_views": total_views,
        "unique_visitors": unique_visitors,
        "busiest_day": busiest_day,
    }


# ── Top content ───────────────────────────────────────────────────────────

async def top_books(session: AsyncSession, period: str, limit: int = 10) -> list[dict]:
    filters = _base_query(period) + [PageView.page_type == "book", PageView.entity_id.isnot(None)]

    stmt = (
        select(
            Book.id,
            Book.title,
            Book.slug,
            func.count(PageView.id).label("views"),
            func.count(distinct(PageView.visitor_token)).label("unique_views"),
        )
        .join(PageView, (PageView.entity_id == Book.id) & (PageView.page_type == "book"))
        .where(*filters)
        .group_by(Book.id, Book.title, Book.slug)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {"id": r[0], "title": r[1], "slug": r[2], "views": r[3], "unique_views": r[4]}
        for r in rows
    ]


async def top_posts(session: AsyncSession, period: str, limit: int = 10) -> list[dict]:
    filters = _base_query(period) + [PageView.page_type == "post", PageView.entity_id.isnot(None)]

    stmt = (
        select(
            Post.id,
            Post.title,
            Post.slug,
            Post.view_count,
            func.count(PageView.id).label("views"),
            func.count(distinct(PageView.visitor_token)).label("unique_views"),
        )
        .join(PageView, (PageView.entity_id == Post.id) & (PageView.page_type == "post"))
        .where(*filters)
        .group_by(Post.id, Post.title, Post.slug, Post.view_count)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": r[0],
            "title": r[1],
            "slug": r[2],
            "old_view_count": r[3],
            "views": r[4],
            "unique_views": r[5],
        }
        for r in rows
    ]


async def top_tools(session: AsyncSession, period: str, limit: int = 10) -> list[dict]:
    filters = _base_query(period) + [PageView.page_type == "tool", PageView.entity_id.isnot(None)]

    stmt = (
        select(
            Tool.id,
            Tool.title,
            Tool.slug,
            func.count(PageView.id).label("views"),
            func.count(distinct(PageView.visitor_token)).label("unique_views"),
        )
        .join(PageView, (PageView.entity_id == Tool.id) & (PageView.page_type == "tool"))
        .where(*filters)
        .group_by(Tool.id, Tool.title, Tool.slug)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {"id": r[0], "title": r[1], "slug": r[2], "views": r[3], "unique_views": r[4]}
        for r in rows
    ]


# ── Daily traffic table ───────────────────────────────────────────────────

async def daily_traffic(session: AsyncSession, period: str) -> list[dict]:
    filters = _base_query(period)

    # For 'all', limit to last 90 days
    if period == "all":
        cutoff_90 = datetime.utcnow() - timedelta(days=90)
        filters = [PageView.created_at >= cutoff_90]

    day_col = func.date(PageView.created_at).label("day")
    stmt = (
        select(
            day_col,
            func.count(PageView.id).label("views"),
            func.count(distinct(PageView.visitor_token)).label("unique_views"),
        )
        .where(*filters)
        .group_by(day_col)
        .order_by(day_col.desc())
    )
    rows = (await session.execute(stmt)).all()

    result = []
    for row in rows:
        day_val = row[0]
        try:
            if isinstance(day_val, str):
                day_date = datetime.strptime(day_val[:10], "%Y-%m-%d").date()
            elif isinstance(day_val, datetime):
                day_date = day_val.date()
            else:
                day_date = day_val
            day_label = format_jalali(day_date)
        except Exception:
            day_label = str(day_val)
        result.append({"day": day_label, "views": row[1], "unique_views": row[2]})

    return result


# ── Referrers ─────────────────────────────────────────────────────────────

async def top_referrers(session: AsyncSession, period: str, limit: int = 10) -> list[dict]:
    filters = _base_query(period)

    stmt = (
        select(
            PageView.referrer_domain,
            func.count(PageView.id).label("views"),
        )
        .where(*filters)
        .group_by(PageView.referrer_domain)
        .order_by(func.count(PageView.id).desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {"domain": r[0] or "مستقیم", "views": r[1]}
        for r in rows
    ]


# ── Per-entity view counts for admin list pages ───────────────────────────

async def view_counts_by_type(session: AsyncSession, page_type: str) -> dict:
    """Return {entity_id: total_view_count} for the given page_type (all time)."""
    stmt = (
        select(PageView.entity_id, func.count(PageView.id).label("cnt"))
        .where(PageView.page_type == page_type, PageView.entity_id.isnot(None))
        .group_by(PageView.entity_id)
    )
    rows = (await session.execute(stmt)).all()
    return {r[0]: r[1] for r in rows}
