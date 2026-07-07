"""Public website pages (SSR with Jinja2)."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import is_rate_limited
from app.core.templates import templates
from app.core.visitor import ensure_visitor_cookie, peek_visitor_token
from app.schemas.book import BookCommentForm
from app.schemas.post import CommentForm
from app.services import about as about_service
from app.services import books as book_service
from app.services import categories as category_service
from app.services import posts as post_service
from app.services import tools as tool_service

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

    visitor_token = peek_visitor_token(request)
    has_rated = book_service.has_rated_book(book, visitor_token) if book else False

    response = templates.TemplateResponse(
        request,
        "pages/book_detail.html",
        {"page_title": book.title if book else slug, "slug": slug, "book": book, "has_rated": has_rated},
    )
    if book:
        ensure_visitor_cookie(request, response, visitor_token)
    return response


@router.post("/library/{slug}/rate/", name="book_rate")
async def book_rate(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    stars: int = Form(...),
):
    book = await book_service.get_book_by_slug(db, slug)
    if book is None or book.status != "published":
        return RedirectResponse(url=request.url_for("library"), status_code=303)

    response = RedirectResponse(url=f"/library/{slug}/#rating", status_code=303)
    visitor_token = peek_visitor_token(request)
    if 1 <= stars <= 5 and not post_service.is_crawler_user_agent(request.headers.get("user-agent")):
        await book_service.rate_book(db, book, visitor_token, stars)
    ensure_visitor_cookie(request, response, visitor_token)
    return response


@router.post("/library/{slug}/comment/", name="book_comment")
async def book_comment(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    author_name: str = Form(""),
    author_email: str = Form(""),
    body: str = Form(""),
    website: str = Form(""),
):
    book = await book_service.get_book_by_slug(db, slug)
    if book is None or book.status != "published":
        return RedirectResponse(url=request.url_for("library"), status_code=303)

    client_ip = request.client.host if request.client else "unknown"
    if website.strip() or is_rate_limited("book_comment", client_ip, max_hits=5, window_seconds=3600):
        return RedirectResponse(url=f"/library/{slug}/#comments", status_code=303)

    try:
        data = BookCommentForm(author_name=author_name, author_email=author_email, body=body)
    except ValidationError:
        return RedirectResponse(url=f"/library/{slug}/#comments", status_code=303)

    await book_service.add_book_comment(db, book, data)
    return RedirectResponse(url=f"/library/{slug}/?commented=1#comments", status_code=303)


@router.get("/about/", name="about")
async def about(request: Request, db: AsyncSession = Depends(get_db)):
    about_page = await about_service.get_about_page(db)
    return templates.TemplateResponse(
        request,
        "pages/about.html",
        {"page_title": "درباره من", "about": about_page},
    )


@router.get("/blog/", name="blog")
async def blog(request: Request, db: AsyncSession = Depends(get_db)):
    all_posts = await post_service.list_posts(db, published_only=True)
    featured = next((p for p in all_posts if p.is_featured), None)
    posts = [p for p in all_posts if p is not featured]
    return templates.TemplateResponse(
        request,
        "pages/blog.html",
        {
            "page_title": "بلاگ",
            "posts": posts,
            "featured": featured,
            "post_count": len(all_posts),
        },
    )


@router.get("/blog/{slug}/", name="post_detail")
async def post_detail(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    post = await post_service.get_post_by_slug(db, slug)
    if post is not None and post.status != "published":
        post = None

    visitor_token = peek_visitor_token(request)
    has_rated = post_service.has_rated(post, visitor_token) if post else False

    response = templates.TemplateResponse(
        request,
        "pages/post_detail.html",
        {"page_title": post.title if post else slug, "slug": slug, "post": post, "has_rated": has_rated},
    )
    if post is None:
        return response

    ensure_visitor_cookie(request, response, visitor_token)

    if not post_service.is_crawler_user_agent(request.headers.get("user-agent")):
        await post_service.increment_view_count(db, post)

    return response


@router.post("/blog/{slug}/rate/", name="post_rate")
async def post_rate(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    stars: int = Form(...),
):
    post = await post_service.get_post_by_slug(db, slug)
    if post is None or post.status != "published":
        return RedirectResponse(url=request.url_for("blog"), status_code=303)

    response = RedirectResponse(url=f"/blog/{slug}/#rating", status_code=303)
    visitor_token = peek_visitor_token(request)
    if 1 <= stars <= 5:
        await post_service.rate_post(db, post, visitor_token, stars)
    ensure_visitor_cookie(request, response, visitor_token)
    return response


@router.post("/blog/{slug}/comment/", name="post_comment")
async def post_comment(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    author_name: str = Form(""),
    author_email: str = Form(""),
    body: str = Form(""),
    website: str = Form(""),
):
    post = await post_service.get_post_by_slug(db, slug)
    if post is None or post.status != "published":
        return RedirectResponse(url=request.url_for("blog"), status_code=303)

    client_ip = request.client.host if request.client else "unknown"
    if website.strip() or is_rate_limited(
        "post_comment", client_ip, max_hits=5, window_seconds=3600
    ):
        return RedirectResponse(url=f"/blog/{slug}/#comments", status_code=303)

    try:
        data = CommentForm(author_name=author_name, author_email=author_email, body=body)
    except ValidationError:
        return RedirectResponse(url=f"/blog/{slug}/#comments", status_code=303)

    await post_service.add_comment(db, post, data)
    return RedirectResponse(url=f"/blog/{slug}/?commented=1#comments", status_code=303)


@router.get("/tools/", name="tools")
async def tools(request: Request, db: AsyncSession = Depends(get_db)):
    all_tools = await tool_service.list_tools(db, published_only=True)
    categories = await category_service.list_categories(db)
    return templates.TemplateResponse(
        request,
        "pages/tools.html",
        {"page_title": "ابزارها", "tools": all_tools, "categories": categories},
    )


@router.get("/tools/{slug}/", name="tool_detail")
async def tool_detail(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    tool = await tool_service.get_tool_by_slug(db, slug)
    if tool is not None and tool.status != "published":
        tool = None
    return templates.TemplateResponse(
        request,
        "pages/tool_detail.html",
        {"page_title": tool.title if tool else slug, "slug": slug, "tool": tool},
    )
