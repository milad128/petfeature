"""Public website pages (SSR with Jinja2)."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {"page_title": "خانه"},
    )


@router.get("/library/", name="library")
async def library(request: Request):
    # Placeholder: books will come from services/models later.
    books = []
    return templates.TemplateResponse(
        request,
        "pages/library.html",
        {"page_title": "کتابخانه", "books": books},
    )


@router.get("/library/{slug}/", name="book_detail")
async def book_detail(request: Request, slug: str):
    # Placeholder: load book by slug from DB later.
    return templates.TemplateResponse(
        request,
        "pages/book_detail.html",
        {"page_title": slug, "slug": slug, "book": None},
    )


@router.get("/about/", name="about")
async def about(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/about.html",
        {"page_title": "درباره من"},
    )
