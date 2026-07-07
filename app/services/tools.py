"""Tool (template library) CRUD and query services."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.post import Post
from app.models.tool import Tool, ToolFile, ToolStatus
from app.schemas.tool import ToolFileInput, ToolForm


async def list_tools(session: AsyncSession, *, published_only: bool = False) -> list[Tool]:
    stmt = (
        select(Tool)
        .options(selectinload(Tool.category), selectinload(Tool.files))
        .order_by(Tool.updated_at.desc())
    )
    if published_only:
        stmt = stmt.where(Tool.status == ToolStatus.PUBLISHED.value)
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def get_tool_by_slug(session: AsyncSession, slug: str) -> Optional[Tool]:
    stmt = (
        select(Tool)
        .options(
            selectinload(Tool.category),
            selectinload(Tool.files),
            selectinload(Tool.related_books),
            selectinload(Tool.related_posts),
        )
        .where(Tool.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_tool(session: AsyncSession, data: ToolForm) -> Tool:
    tool = Tool(
        title=data.title,
        slug=data.slug,
        cover=data.cover or None,
        category_id=data.category_id,
        short_description=data.short_description.strip(),
        body=data.body,
        status=data.status,
    )
    _sync_files(tool, data.files)
    await _sync_related_books(session, tool, data.related_book_ids)
    await _sync_related_posts(session, tool, data.related_post_ids)
    session.add(tool)
    await session.commit()
    await session.refresh(tool, ["category", "files", "related_books", "related_posts"])
    return tool


async def update_tool(session: AsyncSession, tool: Tool, data: ToolForm) -> Tool:
    tool.title = data.title
    tool.slug = data.slug
    tool.cover = data.cover or None
    tool.category_id = data.category_id
    tool.short_description = data.short_description.strip()
    tool.body = data.body
    tool.status = data.status
    tool.files.clear()
    _sync_files(tool, data.files)
    await _sync_related_books(session, tool, data.related_book_ids)
    await _sync_related_posts(session, tool, data.related_post_ids)
    await session.commit()
    await session.refresh(tool, ["category", "files", "related_books", "related_posts"])
    return tool


async def delete_tool(session: AsyncSession, tool: Tool) -> None:
    from app.services import uploads as upload_service

    upload_service.delete_local_tool_cover(tool.cover)
    for file in tool.files:
        upload_service.delete_local_tool_file(file.file)
    await session.delete(tool)
    await session.commit()


def _sync_files(tool: Tool, files: list[ToolFileInput]) -> None:
    for i, item in enumerate(files):
        file_path = item.file.strip()
        if not file_path:
            continue
        tool.files.append(
            ToolFile(
                name=item.name.strip() or "فایل",
                description=item.description.strip() or None,
                file=file_path,
                sort_order=i,
            )
        )


async def _sync_related_books(session: AsyncSession, tool: Tool, book_ids: list[int]) -> None:
    if not book_ids:
        tool.related_books = []
        return
    stmt = select(Book).where(Book.id.in_(book_ids))
    result = await session.execute(stmt)
    tool.related_books = list(result.scalars().all())


async def _sync_related_posts(session: AsyncSession, tool: Tool, post_ids: list[int]) -> None:
    if not post_ids:
        tool.related_posts = []
        return
    stmt = select(Post).where(Post.id.in_(post_ids))
    result = await session.execute(stmt)
    tool.related_posts = list(result.scalars().all())


def parse_tool_files(raw: str) -> list[ToolFileInput]:
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            files = []
            for item in parsed:
                name = str(item.get("name", "")).strip()
                if not name:
                    continue
                files.append(
                    ToolFileInput(
                        name=name,
                        description=str(item.get("description", "")).strip(),
                        file=str(item.get("file", "")).strip(),
                    )
                )
            return files
    except (json.JSONDecodeError, ValueError, AttributeError):
        pass
    return []


def parse_id_list(raw: str) -> list[int]:
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
