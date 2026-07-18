"""Pydantic schemas for blog post, rating, and comment forms."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PostForm(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    cover: str = ""
    body: str = ""
    excerpt: str = Field(default="", max_length=500)
    status: str = "draft"
    is_featured: bool = False
    published_date: Optional[datetime] = None
    related_book_ids: list[int] = Field(default_factory=list)


class CommentForm(BaseModel):
    author_name: str = Field(min_length=1, max_length=150)
    author_email: str = Field(default="", max_length=300)
    body: str = Field(min_length=1, max_length=3000)
    honeypot: str = ""

    @field_validator("author_name", "body")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("این فیلد الزامی است")
        return value

    @field_validator("author_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if value and not _EMAIL_RE.match(value):
            raise ValueError("ایمیل معتبر نیست")
        return value


class RatingForm(BaseModel):
    stars: int = Field(ge=1, le=5)
