"""Tool (template library) and related models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ToolStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


tool_books = Table(
    "tool_books",
    Base.metadata,
    Column("tool_id", ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)

tool_posts = Table(
    "tool_posts",
    Base.metadata,
    Column("tool_id", ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True),
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
)


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    cover: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    short_description: Mapped[str] = mapped_column(String(500), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default=ToolStatus.DRAFT.value)
    download_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["Category"] = relationship("Category", back_populates="tools")  # noqa: F821
    files: Mapped[list["ToolFile"]] = relationship(
        back_populates="tool", cascade="all, delete-orphan", order_by="ToolFile.sort_order"
    )
    related_books: Mapped[list["Book"]] = relationship(  # noqa: F821
        "Book", secondary=tool_books, lazy="selectin"
    )
    related_posts: Mapped[list["Post"]] = relationship(  # noqa: F821
        "Post", secondary=tool_posts, lazy="selectin"
    )

    @property
    def related_book_ids(self) -> list[int]:
        return [b.id for b in self.related_books]

    @property
    def related_post_ids(self) -> list[int]:
        return [p.id for p in self.related_posts]

    @property
    def files_data(self) -> list[dict[str, str]]:
        return [
            {
                "name": f.name,
                "description": f.description or "",
                "file": f.file,
                "item_type": f.item_type,
            }
            for f in self.files
        ]


class ToolFile(Base):
    __tablename__ = "tool_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file: Mapped[str] = mapped_column(String(1000))
    item_type: Mapped[str] = mapped_column(String(10), default="file", server_default="file")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    tool: Mapped["Tool"] = relationship(back_populates="files")
