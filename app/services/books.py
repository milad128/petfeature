"""Book CRUD and query services."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book, BookComment, BookCommentStatus, BookMediaLink, BookRating, BookStatus, book_references
from app.models.category import Category
from app.schemas.book import BookCommentForm, BookForm, MediaLinkInput


async def list_books(
    session: AsyncSession, *, published_only: bool = False, library_only: bool = False
) -> list[Book]:
    stmt = (
        select(Book)
        .options(
            selectinload(Book.media_links),
            selectinload(Book.referred_books),
            selectinload(Book.categories),
            selectinload(Book.ratings),
            selectinload(Book.comments),
        )
        .order_by(Book.updated_at.desc())
    )
    if published_only:
        stmt = stmt.where(Book.status == BookStatus.PUBLISHED.value)
    if library_only:
        stmt = stmt.where(Book.show_in_library.is_(True))
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def list_books_for_select(session: AsyncSession, exclude_id: Optional[int] = None) -> list[Book]:
    stmt = select(Book).order_by(Book.title.asc())
    if exclude_id is not None:
        stmt = stmt.where(Book.id != exclude_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_book_by_slug(session: AsyncSession, slug: str) -> Optional[Book]:
    stmt = (
        select(Book)
        .options(
            selectinload(Book.media_links),
            selectinload(Book.referred_books),
            selectinload(Book.categories),
            selectinload(Book.ratings),
            selectinload(Book.comments),
        )
        .where(Book.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_books_by_ids(session: AsyncSession, book_ids: list[int]) -> list[Book]:
    if not book_ids:
        return []
    stmt = select(Book).where(Book.id.in_(book_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_book(session: AsyncSession, data: BookForm) -> Book:
    book = Book(
        cover=data.cover or None,
        title=data.title,
        subtitle=data.subtitle or None,
        authors=data.authors,
        published_year=data.published_year,
        slug=data.slug,
        status=data.status,
        show_in_library=data.show_in_library,
        note=data.note or None,
        quotes=data.quotes,
        buy_link_title=data.buy_link_title or None,
        buy_link_url=data.buy_link_url or None,
        download_file=data.download_file or None,
    )
    _sync_media_links(book, data.media_links)
    await _sync_categories(session, book, data.category_ids)
    session.add(book)
    await session.flush()
    await _sync_referred_books(session, book, data.referred_book_ids)
    await session.commit()
    await session.refresh(book, ["media_links", "referred_books", "categories"])
    return book


async def update_book(session: AsyncSession, book: Book, data: BookForm) -> Book:
    book.cover = data.cover or None
    book.title = data.title
    book.subtitle = data.subtitle or None
    book.authors = data.authors
    book.published_year = data.published_year
    book.slug = data.slug
    book.status = data.status
    book.show_in_library = data.show_in_library
    book.note = data.note or None
    book.quotes = data.quotes
    book.buy_link_title = data.buy_link_title or None
    book.buy_link_url = data.buy_link_url or None
    book.download_file = data.download_file or None
    book.media_links.clear()
    _sync_media_links(book, data.media_links)
    await _sync_categories(session, book, data.category_ids)
    await _sync_referred_books(session, book, data.referred_book_ids)
    await session.commit()
    await session.refresh(book, ["media_links", "referred_books", "categories"])
    return book


async def delete_book(session: AsyncSession, book: Book) -> None:
    from app.services import uploads as upload_service

    upload_service.delete_local_cover(book.cover)
    upload_service.delete_local_download(book.download_file)
    await session.delete(book)
    await session.commit()


def _sync_media_links(book: Book, media_links: list[MediaLinkInput]) -> None:
    for i, link in enumerate(media_links):
        url = link.url.strip()
        if not url:
            continue
        book.media_links.append(
            BookMediaLink(type=link.type, url=url, title=link.title.strip() or None, sort_order=i)
        )


async def _sync_categories(session: AsyncSession, book: Book, category_ids: list[int]) -> None:
    if not category_ids:
        book.categories = []
        return
    stmt = select(Category).where(Category.id.in_(category_ids))
    result = await session.execute(stmt)
    book.categories = list(result.scalars().all())


async def _sync_referred_books(session: AsyncSession, book: Book, referred_ids: list[int]) -> None:
    if book.id is None:
        return
    valid_ids = [book_id for book_id in referred_ids if book_id != book.id]
    await session.execute(delete(book_references).where(book_references.c.book_id == book.id))
    for ref_id in valid_ids:
        await session.execute(
            insert(book_references).values(book_id=book.id, referred_book_id=ref_id)
        )


def parse_json_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_media_links(raw: str) -> list[MediaLinkInput]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            links = []
            for item in parsed:
                url = item.get("url", "").strip()
                if not url:
                    continue
                link_type = item.get("type", "video")
                if link_type not in {"video", "podcast"}:
                    link_type = "video"
                title = str(item.get("title", "")).strip()
                links.append(MediaLinkInput(type=link_type, url=url, title=title))
            return links
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def parse_referred_book_ids(raw: str) -> list[int]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [int(item) for item in parsed if str(item).isdigit()]
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def parse_published_year(raw: str) -> Optional[int]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


# ── Book engagement ────────────────────────────────────────────────────────


async def rate_book(session: AsyncSession, book: Book, visitor_token: str, stars: int) -> None:
    stmt = select(BookRating).where(
        BookRating.book_id == book.id, BookRating.visitor_token == visitor_token
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        existing.stars = stars
    else:
        session.add(BookRating(book_id=book.id, visitor_token=visitor_token, stars=stars))
    await session.commit()
    await session.refresh(book, ["ratings"])


def has_rated_book(book: Book, visitor_token: str) -> bool:
    return any(r.visitor_token == visitor_token for r in book.ratings)


async def add_book_comment(session: AsyncSession, book: Book, data: BookCommentForm) -> BookComment:
    comment = BookComment(
        book_id=book.id,
        author_name=data.author_name,
        author_email=data.author_email or None,
        body=data.body,
        status=BookCommentStatus.PENDING.value,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(book, ["comments"])
    return comment


async def list_book_comments(session: AsyncSession, *, status: Optional[str] = None) -> list[BookComment]:
    stmt = (
        select(BookComment)
        .options(selectinload(BookComment.book))
        .order_by(BookComment.created_at.desc())
    )
    if status:
        stmt = stmt.where(BookComment.status == status)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_book_comment(session: AsyncSession, comment_id: int) -> Optional[BookComment]:
    stmt = (
        select(BookComment)
        .options(selectinload(BookComment.book))
        .where(BookComment.id == comment_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def set_book_comment_status(session: AsyncSession, comment: BookComment, status: str) -> None:
    comment.status = status
    await session.commit()


async def delete_book_comment(session: AsyncSession, comment: BookComment) -> None:
    await session.delete(comment)
    await session.commit()
