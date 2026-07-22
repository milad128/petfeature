"""Pydantic schemas for newsletter subscription."""

from pydantic import BaseModel, Field


class SubscriberForm(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=6)
