"""Book and related models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.category import book_categories


class BookStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class MediaLinkType(str, enum.Enum):
    VIDEO = "video"
    PODCAST = "podcast"


book_references = Table(
    "book_references",
    Base.metadata,
    Column("book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("referred_book_id", ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    cover: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    authors: Mapped[list] = mapped_column(JSON, default=list)
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=BookStatus.DRAFT.value)
    show_in_library: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quotes: Mapped[list] = mapped_column(JSON, default=list)
    buy_link_title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    buy_link_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    download_file: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    media_links: Mapped[list["BookMediaLink"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
        order_by="BookMediaLink.sort_order",
    )
    referred_books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary=book_references,
        primaryjoin="Book.id == book_references.c.book_id",
        secondaryjoin="Book.id == book_references.c.referred_book_id",
        lazy="selectin",
    )
    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        "Category",
        secondary=book_categories,
        back_populates="books",
        order_by="Category.name",
    )

    @property
    def authors_display(self) -> str:
        return "، ".join(self.authors or [])

    @property
    def referred_book_ids(self) -> list[int]:
        return [b.id for b in self.referred_books]

    @property
    def category_ids(self) -> list[int]:
        return [c.id for c in self.categories]

    @property
    def category_names(self) -> list[str]:
        return [c.name for c in self.categories]

    @property
    def media_links_data(self) -> list[dict[str, str]]:
        return [
            {"type": link.type, "url": link.url, "title": link.title or ""}
            for link in self.media_links
        ]


class BookMediaLink(Base):
    __tablename__ = "book_media_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20))
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)

    book: Mapped["Book"] = relationship(back_populates="media_links")
