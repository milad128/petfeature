"""About page singleton model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AboutPage(Base):
    __tablename__ = "about_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(200), default="میلاد میرزایی")
    author_photo: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    author_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pet_feature_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    site_story_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    links: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
