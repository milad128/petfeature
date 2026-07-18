"""Blog post, rating, and comment services."""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.post import CommentStatus, Post, PostComment, PostRating, PostStatus
from app.schemas.post import CommentForm, PostForm

WORDS_PER_MINUTE = 200

_CRAWLER_UA_RE = re.compile(
    r"bot|crawl|spider|slurp|facebookexternalhit|telegrambot|discordbot|"
    r"whatsapp|preview|monitor|pingdom|uptime",
    re.IGNORECASE,
)


def is_crawler_user_agent(user_agent: Optional[str]) -> bool:
    return bool(user_agent and _CRAWLER_UA_RE.search(user_agent))


def calculate_read_time(body: str) -> int:
    text = re.sub(r"<[^>]+>", " ", body or "")
    word_count = len(text.split())
    return max(1, math.ceil(word_count / WORDS_PER_MINUTE))


def generate_excerpt(body: str, limit: int = 200) -> str:
    text = re.sub(r"<[^>]+>", " ", body or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


async def list_posts(session: AsyncSession, *, published_only: bool = False) -> list[Post]:
    stmt = (
        select(Post)
        .options(selectinload(Post.ratings), selectinload(Post.comments))
        .order_by(Post.published_date.desc().nulls_last(), Post.created_at.desc())
    )
    if published_only:
        stmt = stmt.where(Post.status == PostStatus.PUBLISHED.value)
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def get_post_by_slug(session: AsyncSession, slug: str) -> Optional[Post]:
    stmt = (
        select(Post)
        .options(
            selectinload(Post.ratings),
            selectinload(Post.comments),
            selectinload(Post.related_books),
        )
        .where(Post.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_post_by_id(session: AsyncSession, post_id: int) -> Optional[Post]:
    stmt = (
        select(Post)
        .options(
            selectinload(Post.ratings),
            selectinload(Post.comments),
            selectinload(Post.related_books),
        )
        .where(Post.id == post_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_post(session: AsyncSession, data: PostForm) -> Post:
    post = Post(
        title=data.title,
        slug=data.slug,
        cover=data.cover or None,
        body=data.body,
        excerpt=data.excerpt.strip() or generate_excerpt(data.body),
        status=data.status,
        is_featured=data.is_featured,
        read_time_minutes=calculate_read_time(data.body),
        published_date=_resolve_published_date(data),
    )
    session.add(post)
    await session.flush()  # get post.id before syncing relationships
    await _sync_related_books(session, post, data.related_book_ids)
    await session.commit()
    await session.refresh(post, ["ratings", "comments", "related_books"])
    return post


async def update_post(session: AsyncSession, post: Post, data: PostForm) -> Post:
    post.title = data.title
    post.slug = data.slug
    post.cover = data.cover or None
    post.body = data.body
    post.excerpt = data.excerpt.strip() or generate_excerpt(data.body)
    post.status = data.status
    post.is_featured = data.is_featured
    post.read_time_minutes = calculate_read_time(data.body)
    post.published_date = _resolve_published_date(data, existing=post.published_date)
    await _sync_related_books(session, post, data.related_book_ids)
    await session.commit()
    await session.refresh(post, ["ratings", "comments", "related_books"])
    return post


def _resolve_published_date(data: PostForm, *, existing: Optional[datetime] = None) -> Optional[datetime]:
    if data.published_date is not None:
        return data.published_date
    if data.status == PostStatus.PUBLISHED.value:
        return existing or datetime.now(timezone.utc)
    return existing


async def delete_post(session: AsyncSession, post: Post) -> None:
    from app.services import uploads as upload_service

    upload_service.delete_local_post_cover(post.cover)
    await session.delete(post)
    await session.commit()


async def increment_view_count(session: AsyncSession, post: Post) -> None:
    post.view_count += 1
    await session.commit()


async def rate_post(session: AsyncSession, post: Post, visitor_token: str, stars: int) -> None:
    stmt = select(PostRating).where(
        PostRating.post_id == post.id, PostRating.visitor_token == visitor_token
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        existing.stars = stars
    else:
        session.add(PostRating(post_id=post.id, visitor_token=visitor_token, stars=stars))
    await session.commit()
    await session.refresh(post, ["ratings"])


def has_rated(post: Post, visitor_token: str) -> bool:
    return any(r.visitor_token == visitor_token for r in post.ratings)


async def add_comment(session: AsyncSession, post: Post, data: CommentForm) -> PostComment:
    comment = PostComment(
        post_id=post.id,
        author_name=data.author_name,
        author_email=data.author_email or None,
        body=data.body,
        status=CommentStatus.PENDING.value,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(post, ["comments"])
    return comment


async def list_comments(session: AsyncSession, *, status: Optional[str] = None) -> list[PostComment]:
    stmt = (
        select(PostComment)
        .options(selectinload(PostComment.post))
        .order_by(PostComment.created_at.desc())
    )
    if status:
        stmt = stmt.where(PostComment.status == status)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_comment(session: AsyncSession, comment_id: int) -> Optional[PostComment]:
    stmt = (
        select(PostComment)
        .options(selectinload(PostComment.post))
        .where(PostComment.id == comment_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def set_comment_status(session: AsyncSession, comment: PostComment, status: str) -> None:
    comment.status = status
    await session.commit()


async def delete_comment(session: AsyncSession, comment: PostComment) -> None:
    await session.delete(comment)
    await session.commit()


async def save_comment_reply(
    session: AsyncSession,
    comment: PostComment,
    reply_text: str,  # already stripped; empty string means clear
) -> PostComment:
    if reply_text:
        comment.reply = reply_text
        if comment.reply_at is None:
            comment.reply_at = datetime.now(timezone.utc)
    else:
        comment.reply = None
        comment.reply_at = None
    await session.commit()
    await session.refresh(comment)
    return comment


async def _sync_related_books(session: AsyncSession, post: Post, book_ids: list[int]) -> None:
    if not book_ids:
        post.related_books = []
        return
    stmt = select(Book).where(Book.id.in_(book_ids))
    result = await session.execute(stmt)
    post.related_books = list(result.scalars().all())


def parse_id_list(raw: str) -> list[int]:
    import json

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


def parse_published_date(raw: str) -> Optional[datetime]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
