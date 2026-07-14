"""Pydantic schemas for about page form."""

from pydantic import BaseModel, Field


class LinkInput(BaseModel):
    title: str = ""
    url: str = ""


class JobInput(BaseModel):
    years: str = ""
    role: str = ""
    company: str = ""
    desc: str = ""


class CampInput(BaseModel):
    kind: str = ""
    name: str = ""
    status: str = ""
    desc: str = ""
    url: str = ""


class AboutForm(BaseModel):
    author_name: str = Field(min_length=1, max_length=200)
    author_photo: str = ""
    author_bio: str = ""
    pet_feature_body: str = ""
    site_story_body: str = ""
    links: list[LinkInput] = Field(default_factory=list)
    jobs: list[JobInput] = Field(default_factory=list)
    camps: list[CampInput] = Field(default_factory=list)
