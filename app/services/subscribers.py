"""Newsletter subscriber services."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriber import Subscriber


async def subscribe(session: AsyncSession, name: str, email: str) -> bool:
    """Create subscriber if email not seen. Returns True always (silent dedup)."""
    normalized_email = email.strip().lower()
    existing = await session.execute(
        select(Subscriber).where(Subscriber.email == normalized_email)
    )
    if existing.scalar_one_or_none() is not None:
        return True

    subscriber = Subscriber(
        name=name.strip(),
        email=normalized_email,
        is_active=True,
    )
    session.add(subscriber)
    await session.commit()
    return True


async def list_subscribers(
    session: AsyncSession, page: int = 1, per_page: int = 50
) -> tuple[list[Subscriber], int]:
    """Paginated list of active subscribers, newest first."""
    count_result = await session.execute(
        select(func.count()).select_from(Subscriber).where(Subscriber.is_active.is_(True))
    )
    total = count_result.scalar_one()

    offset = (page - 1) * per_page
    result = await session.execute(
        select(Subscriber)
        .where(Subscriber.is_active.is_(True))
        .order_by(Subscriber.subscribed_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return list(result.scalars().all()), total
