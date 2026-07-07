"""Book category CRUD services."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.schemas.category import CategoryForm


async def list_categories(session: AsyncSession, *, with_book_count: bool = False) -> list[Category]:
    stmt = select(Category).order_by(Category.name.asc())
    if with_book_count:
        stmt = stmt.options(selectinload(Category.books), selectinload(Category.tools))
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def get_category(
    session: AsyncSession, category_id: int, *, with_tool_count: bool = False
) -> Optional[Category]:
    if with_tool_count:
        stmt = (
            select(Category)
            .options(selectinload(Category.tools))
            .where(Category.id == category_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    return await session.get(Category, category_id)


async def get_categories_by_ids(session: AsyncSession, category_ids: list[int]) -> list[Category]:
    if not category_ids:
        return []
    stmt = select(Category).where(Category.id.in_(category_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_category(session: AsyncSession, data: CategoryForm) -> Category:
    category = Category(name=data.name.strip())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(session: AsyncSession, category: Category, data: CategoryForm) -> Category:
    category.name = data.name.strip()
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.commit()


def parse_category_ids(raw: str) -> list[int]:
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
