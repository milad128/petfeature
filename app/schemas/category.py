"""Pydantic schemas for book category forms."""

from pydantic import BaseModel, Field


class CategoryForm(BaseModel):
    name: str = Field(min_length=1, max_length=100)
