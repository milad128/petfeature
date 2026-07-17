"""Blog post and related models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class CommentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    cover: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    body: Mapped[str] = mapped_column(Text, default="")
    excerpt: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=PostStatus.DRAFT.value)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    read_time_minutes: Mapped[int] = mapped_column(Integer, default=1)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    ratings: Mapped[list["PostRating"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    comments: Mapped[list["PostComment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", order_by="PostComment.created_at"
    )

    @property
    def average_rating(self) -> float:
        if not self.ratings:
            return 0.0
        return round(sum(r.stars for r in self.ratings) / len(self.ratings), 1)

    @property
    def rating_count(self) -> int:
        return len(self.ratings)

    @property
    def approved_comments(self) -> list["PostComment"]:
        return [c for c in self.comments if c.status == CommentStatus.APPROVED.value]

    @property
    def approved_comment_count(self) -> int:
        return len(self.approved_comments)

    @property
    def pending_comment_count(self) -> int:
        return len([c for c in self.comments if c.status == CommentStatus.PENDING.value])


class PostRating(Base):
    __tablename__ = "post_ratings"
    __table_args__ = (UniqueConstraint("post_id", "visitor_token", name="uq_post_rating_visitor"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    visitor_token: Mapped[str] = mapped_column(String(64))
    stars: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="ratings")


class PostComment(Base):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    author_name: Mapped[str] = mapped_column(String(150))
    author_email: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=CommentStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    post: Mapped["Post"] = relationship(back_populates="comments")
