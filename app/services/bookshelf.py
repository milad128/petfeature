"""Bookshelf service — personal reading list for logged-in users (v15)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.reading_list import ReadingListItem, VALID_STATUSES


async def get_item_for_book(
    db: AsyncSession, user_id: int, book_id: int
) -> Optional[ReadingListItem]:
    """Return the ReadingListItem for (user, book) or None if not saved."""
    return await db.scalar(
        select(ReadingListItem).where(
            ReadingListItem.user_id == user_id,
            ReadingListItem.book_id == book_id,
        )
    )


async def upsert_item(
    db: AsyncSession, user_id: int, book_id: int, status: str
) -> tuple[ReadingListItem, bool]:
    """Insert or update a bookshelf item.

    Returns (item, newly_read) where newly_read is True when the status
    transitions TO 'read' for the first time — used to trigger the review modal.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}")

    existing = await get_item_for_book(db, user_id, book_id)
    newly_read = False

    if existing:
        was_read = existing.status == "read"
        existing.status = status
        newly_read = (status == "read") and not was_read
        await db.commit()
        await db.refresh(existing)
        return existing, newly_read
    else:
        item = ReadingListItem(user_id=user_id, book_id=book_id, status=status)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        newly_read = status == "read"
        return item, newly_read


async def remove_item(db: AsyncSession, user_id: int, book_id: int) -> None:
    """Remove a book from the user's shelf; no-op if not present."""
    await db.execute(
        delete(ReadingListItem).where(
            ReadingListItem.user_id == user_id,
            ReadingListItem.book_id == book_id,
        )
    )
    await db.commit()


async def get_user_bookshelf(
    db: AsyncSession, user_id: int
) -> list[tuple[ReadingListItem, Book]]:
    """Return all (item, book) pairs for a user, newest addition first."""
    rows = (
        await db.execute(
            select(ReadingListItem, Book)
            .join(Book, ReadingListItem.book_id == Book.id)
            .where(ReadingListItem.user_id == user_id)
            .order_by(ReadingListItem.added_at.desc())
        )
    ).all()
    return [(item, book) for item, book in rows]


async def get_bookshelf_summary(db: AsyncSession, user_id: int) -> dict:
    """Return {total, want, reading, read} counts for the summary bar."""
    rows = (
        await db.execute(
            select(ReadingListItem.status, func.count())
            .where(ReadingListItem.user_id == user_id)
            .group_by(ReadingListItem.status)
        )
    ).all()
    counts = {status: count for status, count in rows}
    total = sum(counts.values())
    return {
        "total": total,
        "want": counts.get("want", 0),
        "reading": counts.get("reading", 0),
        "read": counts.get("read", 0),
    }


async def get_book_save_count(db: AsyncSession, book_id: int) -> int:
    """Distinct user count who saved this book (for social proof counter)."""
    return (
        await db.scalar(
            select(func.count(ReadingListItem.user_id.distinct())).where(
                ReadingListItem.book_id == book_id
            )
        )
    ) or 0


async def get_all_book_save_counts(db: AsyncSession) -> dict[int, int]:
    """Return {book_id: save_count} for all books — admin list column."""
    rows = (
        await db.execute(
            select(
                ReadingListItem.book_id,
                func.count(ReadingListItem.user_id.distinct()),
            ).group_by(ReadingListItem.book_id)
        )
    ).all()
    return {book_id: count for book_id, count in rows}
