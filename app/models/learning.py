"""Enrollment and per-resource progress for the learning path (v17)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

STATUS_LABELS = {
    "STUDYING": "دارم می‌خونم",
    "DONE": "خوندم",
    "ALREADY_KNEW": "قبلاً می‌دونستم",
    "SKIPPED": "رد کردم",
}

VALID_STATUSES = frozenset(STATUS_LABELS)
PROGRESS_STATUSES = frozenset({"DONE", "ALREADY_KNEW"})

BADGE_ENROLLED = "enrolled"
BADGE_PROGRESS = "in_progress"
BADGE_COMPLETED = "completed"

BADGE_LABELS = {
    BADGE_ENROLLED: "ثبت‌نام شده",
    BADGE_PROGRESS: "در حال یادگیری",
    BADGE_COMPLETED: "تکمیل‌شده",
}


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "level_slug", name="uq_enrollment_user_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    level_slug: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unenrolled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    progress_rows: Mapped[list["ResourceProgress"]] = relationship(
        "ResourceProgress",
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )

    @property
    def is_active(self) -> bool:
        return self.unenrolled_at is None


class ResourceProgress(Base):
    __tablename__ = "resource_progress"
    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            "roadmap_resource_id",
            name="uq_progress_enrollment_resource",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    roadmap_resource_id: Mapped[int] = mapped_column(
        ForeignKey("roadmap_resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    enrollment: Mapped[Enrollment] = relationship(
        "Enrollment", back_populates="progress_rows"
    )
