"""User service — Google OAuth user management (v12)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


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
