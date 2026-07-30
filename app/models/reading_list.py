"""ReadingListItem model — user bookshelf (v15)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

READING_STATUS_LABELS = {
    "want": "می‌خواهم بخوانم",
    "reading": "در حال خواندن",
    "read": "خواندم",
}

VALID_STATUSES = frozenset(READING_STATUS_LABELS)


class ReadingListItem(Base):
    __tablename__ = "reading_list_items"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_reading_list_user_book"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="want")
    # status values: "want" | "reading" | "read"
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @property
    def status_label(self) -> str:
        return READING_STATUS_LABELS.get(self.status, self.status)
