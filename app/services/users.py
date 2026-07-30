"""User service — Google OAuth user management (v12) + dashboard data (v14)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


# ── Basic user CRUD ───────────────────────────────────────────────────────────

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.scalar(select(User).where(User.id == user_id))


async def get_or_create_user(
    db: AsyncSession, google_id: str, email: str, name: str
) -> User:
    """Return existing user or create a new one on first Google login."""
    user = await db.scalar(select(User).where(User.google_id == google_id))
    if user:
        # Sync name from Google in case it changed
        if user.name != name:
            user.name = name
            await db.commit()
            await db.refresh(user)
    else:
        user = User(google_id=google_id, email=email.lower(), name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession, page: int = 1, per_page: int = 50
) -> tuple[list[User], int]:
    offset = (page - 1) * per_page
    total = await db.scalar(select(func.count()).select_from(User))
    users = (
        await db.scalars(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page)
        )
    ).all()
    return list(users), total or 0


async def deactivate_user(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.is_active = False
        await db.commit()
        await db.refresh(user)
    return user


async def reactivate_user(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        user.is_active = True
        await db.commit()
        await db.refresh(user)
    return user


# ── Newsletter subscription (v14) ─────────────────────────────────────────────

async def is_subscribed_to_newsletter(db: AsyncSession, email: str) -> bool:
    """Return True if the email has an active subscriber record."""
    from app.models.subscriber import Subscriber
    sub = await db.scalar(
        select(Subscriber).where(Subscriber.email == email.lower())
    )
    return sub is not None and sub.is_active


async def subscribe_to_newsletter(db: AsyncSession, user: User) -> None:
    """Add or reactivate the user's email in the Subscriber table."""
    from app.models.subscriber import Subscriber
    existing = await db.scalar(
        select(Subscriber).where(Subscriber.email == user.email.lower())
    )
    if existing:
        existing.is_active = True
    else:
        db.add(Subscriber(name=user.name, email=user.email.lower(), is_active=True))
    await db.commit()


async def unsubscribe_from_newsletter(db: AsyncSession, user: User) -> None:
    """Set the user's Subscriber record to inactive."""
    from app.models.subscriber import Subscriber
    existing = await db.scalar(
        select(Subscriber).where(Subscriber.email == user.email.lower())
    )
    if existing:
        existing.is_active = False
        await db.commit()


# ── User comments (v14) ───────────────────────────────────────────────────────

@dataclass
class UserComment:
    """Unified comment record for My Comments section on profile page."""
    id: int
    kind: str            # "post" | "book"
    content_title: str
    content_slug: str
    body: str
    status: str
    created_at: datetime
    reply: Optional[str]
    reply_at: Optional[datetime]

    @property
    def body_truncated(self) -> str:
        return self.body[:200] + "…" if len(self.body) > 200 else self.body

    @property
    def status_label(self) -> str:
        mapping = {
            "pending": "در انتظار تأیید",
            "approved": "تأیید شده",
            "rejected": "رد شده",
        }
        return mapping.get(self.status, self.status)


async def get_user_comments(
    db: AsyncSession, user_id: int, page: int = 1, per_page: int = 10
) -> tuple[list[UserComment], int]:
    """Return paginated unified list of PostComments + BookComments for a user."""
    from app.models.post import Post, PostComment
    from app.models.book import Book, BookComment

    # Fetch all post comments for this user (join post for title/slug)
    post_rows = (
        await db.execute(
            select(PostComment, Post.title, Post.slug)
            .join(Post, PostComment.post_id == Post.id)
            .where(PostComment.user_id == user_id)
        )
    ).all()

    # Fetch all book comments for this user (join book for title/slug)
    book_rows = (
        await db.execute(
            select(BookComment, Book.title, Book.slug)
            .join(Book, BookComment.book_id == Book.id)
            .where(BookComment.user_id == user_id)
        )
    ).all()

    comments: list[UserComment] = []
    for pc, post_title, post_slug in post_rows:
        comments.append(UserComment(
            id=pc.id,
            kind="post",
            content_title=post_title,
            content_slug=post_slug,
            body=pc.body,
            status=pc.status,
            created_at=pc.created_at,
            reply=pc.reply,
            reply_at=pc.reply_at,
        ))
    for bc, book_title, book_slug in book_rows:
        comments.append(UserComment(
            id=bc.id,
            kind="book",
            content_title=book_title,
            content_slug=book_slug,
            body=bc.body,
            status=bc.status,
            created_at=bc.created_at,
            reply=bc.reply,
            reply_at=bc.reply_at,
        ))

    # Sort by newest first
    comments.sort(key=lambda c: c.created_at, reverse=True)

    total = len(comments)
    offset = (page - 1) * per_page
    return comments[offset: offset + per_page], total
