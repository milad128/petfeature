"""Roadmap models — RoadmapResource and ImmigrationVideo."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.jalali import format_reading_time


class RoadmapResource(Base):
    """A single learning resource row belonging to a roadmap level/competency/area."""

    __tablename__ = "roadmap_resources"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Grouping keys ─────────────────────────────────────────────────────────
    level_slug: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    # 'hiring' | 'apm' | 'pm' | 'senior-pm' | 'lead' | 'director' | 'cpo'

    competency_slug: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    # e.g. 'product-discovery'; null for L0 area resources

    area_slug: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # e.g. 'role-clarity'; null for level resources

    category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 'entry' | 'core' | 'supporting' | 'bridge'; null for L0

    # Content ───────────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True
    )  # free-text shown in parens after resource_type, e.g. "رایگان"
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 'book' | 'article' | 'podcast' | 'course' | 'tool' | 'guide'

    reading_time: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True
    )  # e.g. "3h", "20m", "ongoing"

    difficulty: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )  # 1 | 2 | 3

    has_persian: Mapped[bool] = mapped_column(Boolean, default=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    # Link resolution (mutually exclusive) ──────────────────────────────────
    external_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    book_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )

    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships ─────────────────────────────────────────────────────────
    book: Mapped[Optional["Book"]] = relationship(  # noqa: F821
        "Book", lazy="joined", foreign_keys=[book_id]
    )

    # ── Computed helpers ────────────────────────────────────────────────────
    @property
    def link_url(self) -> Optional[str]:
        """Resolve the best URL for this resource (book page or external)."""
        if self.book_id and self.book:
            return f"/library/{self.book.slug}/"
        return self.external_url

    @property
    def is_linked(self) -> bool:
        return bool(self.external_url or self.book_id)

    @property
    def link_type(self) -> str:
        """'book' | 'external' | 'none'"""
        if self.book_id:
            return "book"
        if self.external_url:
            return "external"
        return "none"

    @property
    def reading_time_display(self) -> str:
        return format_reading_time(self.reading_time)

    @property
    def difficulty_stars(self) -> str:
        if not self.difficulty:
            return ""
        return "★" * self.difficulty + "☆" * (3 - self.difficulty)

    @property
    def resource_type_fa(self) -> str:
        mapping = {
            "book": "کتاب",
            "article": "مقاله",
            "podcast": "پادکست",
            "course": "دوره",
            "tool": "ابزار",
            "guide": "راهنما",
            "video": "ویدیو",
            "practice-tool": "ابزار تمرین",
        }
        return mapping.get(self.resource_type, self.resource_type)

    @property
    def type_display(self) -> str:
        """Display label for resource type only (subtitle shown with title in UI)."""
        return self.resource_type_fa


class ImmigrationVideo(Base):
    """A video resource shown on the hiring page's immigration section."""

    __tablename__ = "immigration_videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    where: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # e.g. "گفت‌وگو با یک مدیر محصول مهاجرت‌کرده"
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
