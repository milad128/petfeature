"""Pydantic schemas for contact form."""

from pydantic import BaseModel, EmailStr, Field


class ContactForm(BaseModel):
    name: str = ""
    email: str = Field(min_length=1)
    subject: str = ""
    message: str = Field(min_length=1)
