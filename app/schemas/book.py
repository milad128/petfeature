"""Pydantic schemas for book forms."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MediaLinkInput(BaseModel):
    type: str = "video"
    url: str = ""
    title: str = ""

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in {"video", "podcast"}:
            raise ValueError("نوع باید ویدیو یا پادکست باشد")
        return value


class BookForm(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    subtitle: str = Field(default="", max_length=500)
    authors: list[str] = Field(min_length=1)
    published_year: Optional[int] = Field(default=None, ge=1000, le=2100)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    cover: str = ""
    status: str = "draft"
    show_in_library: bool = True
    category_ids: list[int] = Field(default_factory=list)
    note: str = ""
    quotes: list[str] = Field(default_factory=list)
    buy_link_title: str = Field(default="", max_length=300)
    buy_link_url: str = Field(default="", max_length=1000)
    download_file: str = Field(default="", max_length=1000)
    media_links: list[MediaLinkInput] = Field(default_factory=list)
    referred_book_ids: list[int] = Field(default_factory=list)

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, value: list[str]) -> list[str]:
        cleaned = [a.strip() for a in value if a.strip()]
        if not cleaned:
            raise ValueError("حداقل یک نویسنده لازم است")
        return cleaned
