"""Public website pages (SSR with Jinja2)."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.services import about as about_service
from app.services import books as book_service
from app.services import categories as category_service

router = APIRouter()


@router.get("/", name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {"page_title": "خانه"},
    )


@router.get("/library/", name="library")
async def library(request: Request, db: AsyncSession = Depends(get_db)):
    books = await book_service.list_books(db, published_only=True, library_only=True)
    categories = await category_service.list_categories(db)
    return templates.TemplateResponse(
        request,
        "pages/library.html",
        {"page_title": "کتابخانه", "books": books, "categories": categories},
    )


@router.get("/library/{slug}/", name="book_detail")
async def book_detail(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    book = await book_service.get_book_by_slug(db, slug)
    if book is not None and book.status != "published":
        book = None
    return templates.TemplateResponse(
        request,
        "pages/book_detail.html",
        {"page_title": book.title if book else slug, "slug": slug, "book": book},
    )


@router.get("/about/", name="about")
async def about(request: Request, db: AsyncSession = Depends(get_db)):
    about_page = await about_service.get_about_page(db)
    return templates.TemplateResponse(
        request,
        "pages/about.html",
        {"page_title": "درباره من", "about": about_page},
    )
