"""PageView event log model for visitor analytics."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PageView(Base):
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(500))
    page_type: Mapped[str] = mapped_column(String(50))
    # "home" | "library" | "book" | "blog" | "post" | "tools" | "tool"
    # | "about" | "contact" | "other"
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # FK-less int: book.id / post.id / tool.id depending on page_type
    visitor_token: Mapped[str] = mapped_column(String(64), index=True)
    referrer_domain: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    # domain only (e.g. "google.com") — never the full URL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (
        Index("ix_page_views_type_entity", "page_type", "entity_id"),
    )
