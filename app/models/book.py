"""Book and related models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Table, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.category import book_categories


class BookStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class MediaLinkType(str, enum.Enum):
    VIDEO = "video"
    PODCAST = "podcast"
    WEBSITE = "website"
    ARTICLE = "article"
    BOOK = "book"


class BookCommentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


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
    ratings: Mapped[list["BookRating"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    comments: Mapped[list["BookComment"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", order_by="BookComment.created_at"
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

    @property
    def average_rating(self) -> float:
        if not self.ratings:
            return 0.0
        return round(sum(r.stars for r in self.ratings) / len(self.ratings), 1)

    @property
    def rating_count(self) -> int:
        return len(self.ratings)

    @property
    def approved_comments(self) -> list["BookComment"]:
        return [c for c in self.comments if c.status == BookCommentStatus.APPROVED.value]

    @property
    def approved_comment_count(self) -> int:
        return len(self.approved_comments)

    @property
    def pending_comment_count(self) -> int:
        return len([c for c in self.comments if c.status == BookCommentStatus.PENDING.value])


class BookMediaLink(Base):
    __tablename__ = "book_media_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20))
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)

    book: Mapped["Book"] = relationship(back_populates="media_links")


class BookRating(Base):
    __tablename__ = "book_ratings"
    __table_args__ = (UniqueConstraint("book_id", "visitor_token", name="uq_book_rating_visitor"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    visitor_token: Mapped[str] = mapped_column(String(64))
    stars: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    book: Mapped["Book"] = relationship(back_populates="ratings")


class BookComment(Base):
    __tablename__ = "book_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    author_name: Mapped[str] = mapped_column(String(150))
    author_email: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=BookCommentStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    book: Mapped["Book"] = relationship(back_populates="comments")
