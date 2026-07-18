"""Pydantic schemas for tool forms."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ToolFileInput(BaseModel):
    name: str = ""
    description: str = ""
    file: str = ""
    item_type: str = "file"  # "file" or "link"


class ToolForm(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    slug: str = Field(min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")
    cover: str = ""
    category_id: int
    short_description: str = Field(default="", max_length=500)
    body: str = ""
    status: str = "draft"
    files: list[ToolFileInput] = Field(default_factory=list)
    related_book_ids: list[int] = Field(default_factory=list)
    related_post_ids: list[int] = Field(default_factory=list)
