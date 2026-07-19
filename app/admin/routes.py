"""Admin CMS routes — content management for books and about page."""

from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.auth import (
    is_admin_authenticated,
    login_admin,
    logout_admin,
    redirect_if_authenticated,
)
from app.core.database import get_db
from app.core.templates import templates
from app.models.book import BookCommentStatus, BookStatus
from app.models.category import Category
from app.models.post import CommentStatus, PostStatus
from app.models.tool import ToolStatus
from app.schemas.about import AboutForm, LinkInput
from app.schemas.book import BookForm
from app.schemas.category import CategoryForm
from app.schemas.post import PostForm
from app.schemas.tool import ToolFileInput, ToolForm
from app.services import about as about_service
from app.services import analytics as analytics_service
from app.services import books as book_service
from app.services import categories as category_service
from app.services import contact as contact_service
from app.services import posts as post_service
from app.services import tools as tool_service
from app.services import uploads as upload_service
from app.services.media import delete_media_file, get_media_files, human_size, upload_media_file

router = APIRouter()


def _admin_context(request: Request, **extra):
    return {"request": request, **extra}


def _guard_admin(request: Request) -> Optional[RedirectResponse]:
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    return None


@router.get("/", name="admin_dashboard", include_in_schema=False)
async def admin_dashboard(request: Request):
    if redirect := _guard_admin(request):
        return redirect
    return RedirectResponse(url="/admin/books/", status_code=303)


@router.get("/login/", name="admin_login")
async def admin_login_get(request: Request, error: Optional[str] = None):
    if redirect := redirect_if_authenticated(request):
        return redirect
    return templates.TemplateResponse(
        request,
        "admin/login.html",
        _admin_context(request, error=error),
    )


@router.post("/login/", name="admin_login_post")
async def admin_login_post(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
):
    if redirect := redirect_if_authenticated(request):
        return redirect
    from app.admin.auth import verify_credentials

    if verify_credentials(username, password):
        login_admin(request)
        return RedirectResponse(url="/admin/books/", status_code=303)
    return templates.TemplateResponse(
        request,
        "admin/login.html",
        _admin_context(request, error="نام کاربری یا رمز عبور اشتباه است."),
        status_code=401,
    )


@router.get("/logout/", name="admin_logout")
async def admin_logout(request: Request):
    logout_admin(request)
    return RedirectResponse(url="/admin/login/", status_code=303)


@router.get("/books/", name="admin_books")
async def admin_books_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    q: str = "",
):
    if redirect := _guard_admin(request):
        return redirect
    books = await book_service.list_books(db)
    if q.strip():
        query = q.strip().lower()
        books = [
            b
            for b in books
            if query in b.title.lower()
            or any(query in author.lower() for author in (b.authors or []))
        ]
    book_view_counts = await analytics_service.view_counts_by_type(db, "book")
    return templates.TemplateResponse(
        request,
        "admin/books_list.html",
        _admin_context(
            request,
            page_title="کتاب‌ها",
            active_nav="books",
            books=books,
            search_query=q,
            view_counts=book_view_counts,
        ),
    )


@router.get("/books/new/", name="admin_book_new")
async def admin_book_new_get(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    all_books = await book_service.list_books_for_select(db)
    all_categories = await category_service.list_categories(db)
    return templates.TemplateResponse(
        request,
        "admin/book_form.html",
        _admin_context(
            request,
            page_title="کتاب جدید",
            active_nav="books",
            book=None,
            all_books=all_books,
            all_categories=all_categories,
            form_error=None,
        ),
    )


@router.post("/books/new/", name="admin_book_create")
async def admin_book_new_post(
    request: Request,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    subtitle: str = Form(""),
    published_year: str = Form(""),
    slug: str = Form(""),
    cover: str = Form(""),
    status: str = Form(BookStatus.DRAFT.value),
    show_in_library: str = Form("true"),
    note: str = Form(""),
    authors: str = Form("[]"),
    category_ids: str = Form("[]"),
    quotes: str = Form("[]"),
    buy_link_title: str = Form(""),
    buy_link_url: str = Form(""),
    download: str = Form(""),
    media_links: str = Form("[]"),
    referred_book_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
    download_file: Optional[UploadFile] = File(None),
):
    if redirect := _guard_admin(request):
        return redirect
    all_books = await book_service.list_books_for_select(db)
    all_categories = await category_service.list_categories(db)
    form_data = _parse_book_form(
        title=title,
        subtitle=subtitle,
        published_year=published_year,
        slug=slug.strip().lower(),
        cover=cover,
        status=status,
        show_in_library=show_in_library,
        note=note,
        authors=authors,
        category_ids=category_ids,
        quotes=quotes,
        buy_link_title=buy_link_title,
        buy_link_url=buy_link_url,
        download=download,
        media_links=media_links,
        referred_book_ids=referred_book_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/book_form.html",
            _admin_context(
                request,
                page_title="کتاب جدید",
                active_nav="books",
                book=await _raw_book_preview(
                    db, title, subtitle, published_year, slug, cover, status, note,
                    authors, category_ids, quotes, buy_link_title, buy_link_url, download,
                    media_links, referred_book_ids, show_in_library=show_in_library,
                ),
                all_books=all_books,
                all_categories=all_categories,
                form_error=_format_validation_error(form_data),
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_book_uploads(
        form_data,
        cover=cover,
        cover_file=cover_file,
        download=download,
        download_file=download_file,
    )
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/book_form.html",
            _admin_context(
                request,
                page_title="کتاب جدید",
                active_nav="books",
                book=await _form_as_book_preview(db, form_data),
                all_books=all_books,
                all_categories=all_categories,
                form_error=upload_error,
            ),
            status_code=422,
        )

    existing = await book_service.get_book_by_slug(db, form_data.slug)
    if existing:
        return templates.TemplateResponse(
            request,
            "admin/book_form.html",
            _admin_context(
                request,
                page_title="کتاب جدید",
                active_nav="books",
                book=await _form_as_book_preview(db, form_data),
                all_books=all_books,
                all_categories=all_categories,
                form_error="این نامک (slug) قبلاً استفاده شده است.",
            ),
            status_code=422,
        )

    book = await book_service.create_book(db, form_data)
    return RedirectResponse(url=f"/admin/books/{book.slug}/edit/?saved=1", status_code=303)


@router.get("/books/{slug}/edit/", name="admin_book_edit")
async def admin_book_edit_get(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    saved: Optional[int] = None,
):
    if redirect := _guard_admin(request):
        return redirect
    book = await book_service.get_book_by_slug(db, slug)
    if book is None:
        return RedirectResponse(url="/admin/books/", status_code=303)
    all_books = await book_service.list_books_for_select(db, exclude_id=book.id)
    all_categories = await category_service.list_categories(db)
    return templates.TemplateResponse(
        request,
        "admin/book_form.html",
        _admin_context(
            request,
            page_title=f"ویرایش: {book.title}",
            active_nav="books",
            book=book,
            all_books=all_books,
            all_categories=all_categories,
            form_error=None,
            saved=bool(saved),
        ),
    )


@router.post("/books/{slug}/edit/", name="admin_book_update")
async def admin_book_edit_post(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    subtitle: str = Form(""),
    published_year: str = Form(""),
    form_slug: str = Form("", alias="slug"),
    cover: str = Form(""),
    status: str = Form(BookStatus.DRAFT.value),
    show_in_library: str = Form("true"),
    note: str = Form(""),
    authors: str = Form("[]"),
    category_ids: str = Form("[]"),
    quotes: str = Form("[]"),
    buy_link_title: str = Form(""),
    buy_link_url: str = Form(""),
    download: str = Form(""),
    media_links: str = Form("[]"),
    referred_book_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
    download_file: Optional[UploadFile] = File(None),
):
    if redirect := _guard_admin(request):
        return redirect
    book = await book_service.get_book_by_slug(db, slug)
    if book is None:
        return RedirectResponse(url="/admin/books/", status_code=303)

    all_books = await book_service.list_books_for_select(db, exclude_id=book.id)
    all_categories = await category_service.list_categories(db)
    form_data = _parse_book_form(
        title=title,
        subtitle=subtitle,
        published_year=published_year,
        slug=form_slug.strip().lower(),
        cover=cover,
        status=status,
        show_in_library=show_in_library,
        note=note,
        authors=authors,
        category_ids=category_ids,
        quotes=quotes,
        buy_link_title=buy_link_title,
        buy_link_url=buy_link_url,
        download=download,
        media_links=media_links,
        referred_book_ids=referred_book_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/book_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="books",
                book=await _raw_book_preview(
                    db, title, subtitle, published_year, form_slug, cover, status, note,
                    authors, category_ids, quotes, buy_link_title, buy_link_url, download,
                    media_links, referred_book_ids, show_in_library=show_in_library,
                ),
                all_books=all_books,
                all_categories=all_categories,
                form_error=_format_validation_error(form_data),
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_book_uploads(
        form_data,
        cover=cover,
        cover_file=cover_file,
        download=download,
        download_file=download_file,
        old_cover=book.cover,
        old_download=book.download_file,
    )
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/book_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="books",
                book=await _form_as_book_preview(db, form_data, form_data.slug),
                all_books=all_books,
                all_categories=all_categories,
                form_error=upload_error,
            ),
            status_code=422,
        )

    if form_data.slug != slug:
        existing = await book_service.get_book_by_slug(db, form_data.slug)
        if existing:
            return templates.TemplateResponse(
                request,
                "admin/book_form.html",
                _admin_context(
                    request,
                    page_title=f"ویرایش: {book.title}",
                    active_nav="books",
                    book=await _form_as_book_preview(db, form_data, form_data.slug),
                    all_books=all_books,
                    all_categories=all_categories,
                    form_error="این نامک (slug) قبلاً استفاده شده است.",
                ),
                status_code=422,
            )

    await book_service.update_book(db, book, form_data)
    return RedirectResponse(url=f"/admin/books/{form_data.slug}/edit/?saved=1", status_code=303)


@router.post("/books/{slug}/delete/", name="admin_book_delete")
async def admin_book_delete(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    if redirect := _guard_admin(request):
        return redirect
    book = await book_service.get_book_by_slug(db, slug)
    if book:
        await book_service.delete_book(db, book)
    return RedirectResponse(url="/admin/books/", status_code=303)


@router.get("/posts/", name="admin_posts")
async def admin_posts_list(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    posts = await post_service.list_posts(db)
    post_view_counts = await analytics_service.view_counts_by_type(db, "post")
    return templates.TemplateResponse(
        request,
        "admin/posts_list.html",
        _admin_context(
            request,
            page_title="یادداشت‌ها",
            active_nav="posts",
            posts=posts,
            view_counts=post_view_counts,
        ),
    )


@router.get("/posts/new/", name="admin_post_new")
async def admin_post_new_get(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    all_books = await book_service.list_books_for_select(db)
    return templates.TemplateResponse(
        request,
        "admin/post_form.html",
        _admin_context(
            request,
            page_title="یادداشت جدید",
            active_nav="posts",
            post=None,
            form_error=None,
            all_books=all_books,
        ),
    )


@router.post("/posts/new/", name="admin_post_create")
async def admin_post_new_post(
    request: Request,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    slug: str = Form(""),
    cover: str = Form(""),
    body: str = Form(""),
    excerpt: str = Form(""),
    status: str = Form(PostStatus.DRAFT.value),
    is_featured: str = Form("false"),
    published_date: str = Form(""),
    related_book_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
):
    if redirect := _guard_admin(request):
        return redirect
    all_books = await book_service.list_books_for_select(db)
    form_data = _parse_post_form(
        title=title,
        slug=slug.strip().lower(),
        cover=cover,
        body=body,
        excerpt=excerpt,
        status=status,
        is_featured=is_featured,
        published_date=published_date,
        related_book_ids=related_book_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title="یادداشت جدید",
                active_nav="posts",
                post=_raw_post_preview(
                    title, slug, cover, body, excerpt, status, is_featured, published_date
                ),
                form_error=_format_validation_error(form_data),
                all_books=all_books,
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_post_upload(form_data, cover=cover, cover_file=cover_file)
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title="یادداشت جدید",
                active_nav="posts",
                post=_form_as_post_preview(form_data),
                form_error=upload_error,
                all_books=all_books,
            ),
            status_code=422,
        )

    existing = await post_service.get_post_by_slug(db, form_data.slug)
    if existing:
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title="یادداشت جدید",
                active_nav="posts",
                post=_form_as_post_preview(form_data),
                form_error="این نامک (slug) قبلاً استفاده شده است.",
                all_books=all_books,
            ),
            status_code=422,
        )
    if form_data.status == PostStatus.PUBLISHED.value and not form_data.cover:
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title="یادداشت جدید",
                active_nav="posts",
                post=_form_as_post_preview(form_data),
                form_error="برای انتشار یادداشت، تصویر کاور الزامی است.",
                all_books=all_books,
            ),
            status_code=422,
        )

    post = await post_service.create_post(db, form_data)
    return RedirectResponse(url=f"/admin/posts/{post.slug}/edit/?saved=1", status_code=303)


@router.get("/posts/{slug}/edit/", name="admin_post_edit")
async def admin_post_edit_get(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    saved: Optional[int] = None,
):
    if redirect := _guard_admin(request):
        return redirect
    post = await post_service.get_post_by_slug(db, slug)
    if post is None:
        return RedirectResponse(url="/admin/posts/", status_code=303)
    all_books = await book_service.list_books_for_select(db)
    return templates.TemplateResponse(
        request,
        "admin/post_form.html",
        _admin_context(
            request,
            page_title=f"ویرایش: {post.title}",
            active_nav="posts",
            post=post,
            form_error=None,
            saved=bool(saved),
            all_books=all_books,
        ),
    )


@router.post("/posts/{slug}/edit/", name="admin_post_update")
async def admin_post_edit_post(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    slug_field: str = Form("", alias="slug"),
    cover: str = Form(""),
    body: str = Form(""),
    excerpt: str = Form(""),
    status: str = Form(PostStatus.DRAFT.value),
    is_featured: str = Form("false"),
    published_date: str = Form(""),
    related_book_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
):
    if redirect := _guard_admin(request):
        return redirect
    post = await post_service.get_post_by_slug(db, slug)
    if post is None:
        return RedirectResponse(url="/admin/posts/", status_code=303)
    all_books = await book_service.list_books_for_select(db)

    form_data = _parse_post_form(
        title=title,
        slug=slug_field.strip().lower(),
        cover=cover,
        body=body,
        excerpt=excerpt,
        status=status,
        is_featured=is_featured,
        published_date=published_date,
        existing_published_date=post.published_date,
        related_book_ids=related_book_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="posts",
                post=_raw_post_preview(
                    title, slug_field, cover, body, excerpt, status, is_featured, published_date
                ),
                form_error=_format_validation_error(form_data),
                all_books=all_books,
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_post_upload(
        form_data, cover=cover, cover_file=cover_file, old_cover=post.cover
    )
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="posts",
                post=_form_as_post_preview(form_data, form_data.slug),
                form_error=upload_error,
                all_books=all_books,
            ),
            status_code=422,
        )

    if form_data.slug != slug:
        existing = await post_service.get_post_by_slug(db, form_data.slug)
        if existing:
            return templates.TemplateResponse(
                request,
                "admin/post_form.html",
                _admin_context(
                    request,
                    page_title=f"ویرایش: {post.title}",
                    active_nav="posts",
                    post=_form_as_post_preview(form_data, form_data.slug),
                    form_error="این نامک (slug) قبلاً استفاده شده است.",
                    all_books=all_books,
                ),
                status_code=422,
            )
    if form_data.status == PostStatus.PUBLISHED.value and not form_data.cover:
        return templates.TemplateResponse(
            request,
            "admin/post_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {post.title}",
                active_nav="posts",
                post=_form_as_post_preview(form_data, form_data.slug),
                form_error="برای انتشار یادداشت، تصویر کاور الزامی است.",
                all_books=all_books,
            ),
            status_code=422,
        )

    await post_service.update_post(db, post, form_data)
    return RedirectResponse(url=f"/admin/posts/{form_data.slug}/edit/?saved=1", status_code=303)


@router.post("/posts/{slug}/delete/", name="admin_post_delete")
async def admin_post_delete(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    post = await post_service.get_post_by_slug(db, slug)
    if post:
        await post_service.delete_post(db, post)
    return RedirectResponse(url="/admin/posts/", status_code=303)


@router.get("/posts/comments/", name="admin_post_comments")
async def admin_post_comments_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    status: str = "pending",
):
    if redirect := _guard_admin(request):
        return redirect
    valid_statuses = {s.value for s in CommentStatus}
    status = status if status in valid_statuses else CommentStatus.PENDING.value
    comments = await post_service.list_comments(db, status=status)
    return templates.TemplateResponse(
        request,
        "admin/post_comments_list.html",
        _admin_context(
            request,
            page_title="نظرهای یادداشت‌ها",
            active_nav="post_comments",
            comments=comments,
            current_status=status,
        ),
    )


@router.post("/posts/comments/{comment_id}/approve/", name="admin_post_comment_approve")
async def admin_post_comment_approve(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    comment = await post_service.get_comment(db, comment_id)
    if comment:
        await post_service.set_comment_status(db, comment, CommentStatus.APPROVED.value)
    return RedirectResponse(url="/admin/posts/comments/", status_code=303)


@router.post("/posts/comments/{comment_id}/reject/", name="admin_post_comment_reject")
async def admin_post_comment_reject(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    comment = await post_service.get_comment(db, comment_id)
    if comment:
        await post_service.set_comment_status(db, comment, CommentStatus.REJECTED.value)
    return RedirectResponse(url="/admin/posts/comments/", status_code=303)


@router.post("/posts/comments/{comment_id}/delete/", name="admin_post_comment_delete")
async def admin_post_comment_delete(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    comment = await post_service.get_comment(db, comment_id)
    if comment:
        await post_service.delete_comment(db, comment)
    return RedirectResponse(url="/admin/posts/comments/", status_code=303)


@router.post("/posts/comments/{comment_id}/reply/", name="admin_post_comment_reply")
async def admin_post_comment_reply(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    comment = await post_service.get_comment(db, comment_id)
    if comment:
        form = await request.form()
        reply_text = str(form.get("reply", "")).strip()
        await post_service.save_comment_reply(db, comment, reply_text)
    return RedirectResponse(url="/admin/posts/comments/?status=approved", status_code=303)


@router.get("/categories/", name="admin_categories")
async def admin_categories_list(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    categories = await category_service.list_categories(db, with_book_count=True)
    return templates.TemplateResponse(
        request,
        "admin/categories_list.html",
        _admin_context(
            request,
            page_title="دسته‌بندی کتاب‌ها",
            active_nav="categories",
            categories=categories,
        ),
    )


@router.get("/categories/new/", name="admin_category_new")
async def admin_category_new_get(request: Request):
    if redirect := _guard_admin(request):
        return redirect
    return templates.TemplateResponse(
        request,
        "admin/category_form.html",
        _admin_context(
            request,
            page_title="دسته‌بندی جدید",
            active_nav="categories",
            category=None,
            form_error=None,
        ),
    )


@router.post("/categories/new/", name="admin_category_create")
async def admin_category_new_post(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(""),
):
    if redirect := _guard_admin(request):
        return redirect
    try:
        form_data = CategoryForm(name=name.strip())
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "admin/category_form.html",
            _admin_context(
                request,
                page_title="دسته‌بندی جدید",
                active_nav="categories",
                category=None,
                form_error=_format_validation_error(exc),
            ),
            status_code=422,
        )

    existing = await _get_category_by_name(db, form_data.name)
    if existing:
        return templates.TemplateResponse(
            request,
            "admin/category_form.html",
            _admin_context(
                request,
                page_title="دسته‌بندی جدید",
                active_nav="categories",
                category=None,
                form_error="این دسته‌بندی از قبل وجود دارد.",
            ),
            status_code=422,
        )

    await category_service.create_category(db, form_data)
    return RedirectResponse(url="/admin/categories/?saved=1", status_code=303)


@router.get("/categories/{category_id}/edit/", name="admin_category_edit")
async def admin_category_edit_get(
    request: Request,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    saved: Optional[int] = None,
):
    if redirect := _guard_admin(request):
        return redirect
    category = await category_service.get_category(db, category_id)
    if category is None:
        return RedirectResponse(url="/admin/categories/", status_code=303)
    return templates.TemplateResponse(
        request,
        "admin/category_form.html",
        _admin_context(
            request,
            page_title=f"ویرایش: {category.name}",
            active_nav="categories",
            category=category,
            form_error=None,
            saved=bool(saved),
        ),
    )


@router.post("/categories/{category_id}/edit/", name="admin_category_update")
async def admin_category_edit_post(
    request: Request,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    name: str = Form(""),
):
    if redirect := _guard_admin(request):
        return redirect
    category = await category_service.get_category(db, category_id)
    if category is None:
        return RedirectResponse(url="/admin/categories/", status_code=303)

    try:
        form_data = CategoryForm(name=name.strip())
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "admin/category_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {category.name}",
                active_nav="categories",
                category=category,
                form_error=_format_validation_error(exc),
            ),
            status_code=422,
        )

    existing = await _get_category_by_name(db, form_data.name)
    if existing and existing.id != category.id:
        return templates.TemplateResponse(
            request,
            "admin/category_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {category.name}",
                active_nav="categories",
                category=category,
                form_error="این دسته‌بندی از قبل وجود دارد.",
            ),
            status_code=422,
        )

    await category_service.update_category(db, category, form_data)
    return RedirectResponse(url=f"/admin/categories/{category.id}/edit/?saved=1", status_code=303)


@router.post("/categories/{category_id}/delete/", name="admin_category_delete")
async def admin_category_delete(
    request: Request,
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    if redirect := _guard_admin(request):
        return redirect
    category = await category_service.get_category(db, category_id, with_tool_count=True)
    if category and not category.tools:
        await category_service.delete_category(db, category)
    return RedirectResponse(url="/admin/categories/", status_code=303)


async def _get_category_by_name(db: AsyncSession, name: str):
    stmt = select(Category).where(Category.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/tools/", name="admin_tools")
async def admin_tools_list(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    tools = await tool_service.list_tools(db)
    tool_view_counts = await analytics_service.view_counts_by_type(db, "tool")
    return templates.TemplateResponse(
        request,
        "admin/tools_list.html",
        _admin_context(
            request,
            page_title="ابزارها",
            active_nav="tools",
            tools=tools,
            view_counts=tool_view_counts,
        ),
    )


@router.get("/tools/new/", name="admin_tool_new")
async def admin_tool_new_get(request: Request, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    all_categories = await category_service.list_categories(db)
    all_books = await book_service.list_books_for_select(db)
    all_posts = await post_service.list_posts(db)
    return templates.TemplateResponse(
        request,
        "admin/tool_form.html",
        _admin_context(
            request,
            page_title="ابزار جدید",
            active_nav="tools",
            tool=None,
            all_categories=all_categories,
            all_books=all_books,
            all_posts=all_posts,
            form_error=None,
        ),
    )


@router.post("/tools/new/", name="admin_tool_create")
async def admin_tool_new_post(
    request: Request,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    slug: str = Form(""),
    cover: str = Form(""),
    category_id: str = Form(""),
    short_description: str = Form(""),
    body: str = Form(""),
    status: str = Form(ToolStatus.DRAFT.value),
    files: str = Form("[]"),
    related_book_ids: str = Form("[]"),
    related_post_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
    tool_file_uploads: list[UploadFile] = File(default=[]),
):
    if redirect := _guard_admin(request):
        return redirect
    all_categories = await category_service.list_categories(db)
    all_books = await book_service.list_books_for_select(db)
    all_posts = await post_service.list_posts(db)

    form_data = _parse_tool_form(
        title=title,
        slug=slug.strip().lower(),
        cover=cover,
        category_id=category_id,
        short_description=short_description,
        body=body,
        status=status,
        files=files,
        related_book_ids=related_book_ids,
        related_post_ids=related_post_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title="ابزار جدید",
                active_nav="tools",
                tool=_raw_tool_preview(
                    title, slug, cover, category_id, short_description, body, status,
                    files, related_book_ids, related_post_ids,
                ),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error=_format_validation_error(form_data),
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_tool_uploads(
        form_data, cover=cover, cover_file=cover_file, tool_file_uploads=tool_file_uploads
    )
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title="ابزار جدید",
                active_nav="tools",
                tool=await _form_as_tool_preview(db, form_data),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error=upload_error,
            ),
            status_code=422,
        )

    existing = await tool_service.get_tool_by_slug(db, form_data.slug)
    if existing:
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title="ابزار جدید",
                active_nav="tools",
                tool=await _form_as_tool_preview(db, form_data),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error="این نامک (slug) قبلاً استفاده شده است.",
            ),
            status_code=422,
        )
    if form_data.status == ToolStatus.PUBLISHED.value and not form_data.cover:
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title="ابزار جدید",
                active_nav="tools",
                tool=await _form_as_tool_preview(db, form_data),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error="برای انتشار ابزار، تصویر کاور الزامی است.",
            ),
            status_code=422,
        )

    tool = await tool_service.create_tool(db, form_data)
    return RedirectResponse(url=f"/admin/tools/{tool.slug}/edit/?saved=1", status_code=303)


@router.get("/tools/{slug}/edit/", name="admin_tool_edit")
async def admin_tool_edit_get(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    saved: Optional[int] = None,
):
    if redirect := _guard_admin(request):
        return redirect
    tool = await tool_service.get_tool_by_slug(db, slug)
    if tool is None:
        return RedirectResponse(url="/admin/tools/", status_code=303)
    all_categories = await category_service.list_categories(db)
    all_books = await book_service.list_books_for_select(db)
    all_posts = await post_service.list_posts(db)
    return templates.TemplateResponse(
        request,
        "admin/tool_form.html",
        _admin_context(
            request,
            page_title=f"ویرایش: {tool.title}",
            active_nav="tools",
            tool=tool,
            all_categories=all_categories,
            all_books=all_books,
            all_posts=all_posts,
            form_error=None,
            saved=bool(saved),
        ),
    )


@router.post("/tools/{slug}/edit/", name="admin_tool_update")
async def admin_tool_edit_post(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db),
    title: str = Form(""),
    slug_field: str = Form("", alias="slug"),
    cover: str = Form(""),
    category_id: str = Form(""),
    short_description: str = Form(""),
    body: str = Form(""),
    status: str = Form(ToolStatus.DRAFT.value),
    files: str = Form("[]"),
    related_book_ids: str = Form("[]"),
    related_post_ids: str = Form("[]"),
    cover_file: Optional[UploadFile] = File(None),
    tool_file_uploads: list[UploadFile] = File(default=[]),
):
    if redirect := _guard_admin(request):
        return redirect
    tool = await tool_service.get_tool_by_slug(db, slug)
    if tool is None:
        return RedirectResponse(url="/admin/tools/", status_code=303)

    all_categories = await category_service.list_categories(db)
    all_books = await book_service.list_books_for_select(db)
    all_posts = await post_service.list_posts(db)

    form_data = _parse_tool_form(
        title=title,
        slug=slug_field.strip().lower(),
        cover=cover,
        category_id=category_id,
        short_description=short_description,
        body=body,
        status=status,
        files=files,
        related_book_ids=related_book_ids,
        related_post_ids=related_post_ids,
    )
    if isinstance(form_data, ValidationError):
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="tools",
                tool=_raw_tool_preview(
                    title, slug_field, cover, category_id, short_description, body, status,
                    files, related_book_ids, related_post_ids,
                ),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error=_format_validation_error(form_data),
            ),
            status_code=422,
        )

    form_data, upload_error = await _resolve_tool_uploads(
        form_data,
        cover=cover,
        cover_file=cover_file,
        tool_file_uploads=tool_file_uploads,
        old_cover=tool.cover,
    )
    if upload_error:
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {title or slug}",
                active_nav="tools",
                tool=await _form_as_tool_preview(db, form_data, form_data.slug),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error=upload_error,
            ),
            status_code=422,
        )

    if form_data.slug != slug:
        existing = await tool_service.get_tool_by_slug(db, form_data.slug)
        if existing:
            return templates.TemplateResponse(
                request,
                "admin/tool_form.html",
                _admin_context(
                    request,
                    page_title=f"ویرایش: {tool.title}",
                    active_nav="tools",
                    tool=await _form_as_tool_preview(db, form_data, form_data.slug),
                    all_categories=all_categories,
                    all_books=all_books,
                    all_posts=all_posts,
                    form_error="این نامک (slug) قبلاً استفاده شده است.",
                ),
                status_code=422,
            )
    if form_data.status == ToolStatus.PUBLISHED.value and not form_data.cover:
        return templates.TemplateResponse(
            request,
            "admin/tool_form.html",
            _admin_context(
                request,
                page_title=f"ویرایش: {tool.title}",
                active_nav="tools",
                tool=await _form_as_tool_preview(db, form_data, form_data.slug),
                all_categories=all_categories,
                all_books=all_books,
                all_posts=all_posts,
                form_error="برای انتشار ابزار، تصویر کاور الزامی است.",
            ),
            status_code=422,
        )

    await tool_service.update_tool(db, tool, form_data)
    return RedirectResponse(url=f"/admin/tools/{form_data.slug}/edit/?saved=1", status_code=303)


@router.post("/tools/{slug}/delete/", name="admin_tool_delete")
async def admin_tool_delete(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    if redirect := _guard_admin(request):
        return redirect
    tool = await tool_service.get_tool_by_slug(db, slug)
    if tool:
        await tool_service.delete_tool(db, tool)
    return RedirectResponse(url="/admin/tools/", status_code=303)


@router.get("/about/", name="admin_about")
async def admin_about_get(
    request: Request,
    db: AsyncSession = Depends(get_db),
    saved: Optional[int] = None,
):
    if redirect := _guard_admin(request):
        return redirect
    about = await about_service.get_about_page(db)
    return templates.TemplateResponse(
        request,
        "admin/about_form.html",
        _admin_context(
            request,
            page_title="درباره من",
            active_nav="about",
            about=about,
            form_error=None,
            saved=bool(saved),
        ),
    )


@router.post("/about/", name="admin_about_update")
async def admin_about_post(
    request: Request,
    db: AsyncSession = Depends(get_db),
    author_name: str = Form(""),
    author_photo: str = Form(""),
    author_bio: str = Form(""),
    pet_feature_body: str = Form(""),
    site_story_body: str = Form(""),
    links: str = Form("[]"),
    jobs: str = Form("[]"),
    camps: str = Form("[]"),
):
    if redirect := _guard_admin(request):
        return redirect
    about = await about_service.get_about_page(db)
    form_data = AboutForm(
        author_name=author_name.strip(),
        author_photo=author_photo.strip(),
        author_bio=author_bio,
        pet_feature_body=pet_feature_body,
        site_story_body=site_story_body,
        links=about_service.parse_links(links),
        jobs=about_service.parse_jobs(jobs),
        camps=about_service.parse_camps(camps),
    )
    try:
        AboutForm.model_validate(form_data.model_dump())
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "admin/about_form.html",
            _admin_context(
                request,
                page_title="درباره من",
                active_nav="about",
                about=_form_as_about_preview(form_data),
                form_error=_format_validation_error(exc),
            ),
            status_code=422,
        )

    await about_service.update_about_page(db, about, form_data)
    return RedirectResponse(url="/admin/about/?saved=1", status_code=303)


def _format_validation_error(exc: ValidationError) -> str:
    messages = []
    for err in exc.errors():
        field = err.get("loc", ["فیلد"])[0]
        msg = err.get("msg", "مقدار نامعتبر")
        messages.append(f"{field}: {msg}")
    return "؛ ".join(messages)


def _parse_book_form(
    *,
    title: str,
    subtitle: str,
    published_year: str,
    slug: str,
    cover: str,
    status: str,
    show_in_library: str,
    note: str,
    authors: str,
    category_ids: str,
    quotes: str,
    buy_link_title: str,
    buy_link_url: str,
    download: str,
    media_links: str,
    referred_book_ids: str,
) -> Union[BookForm, ValidationError]:
    payload = {
        "title": title.strip(),
        "subtitle": subtitle.strip(),
        "published_year": book_service.parse_published_year(published_year),
        "slug": slug.strip().lower(),
        "cover": cover.strip(),
        "status": status if status in {BookStatus.DRAFT.value, BookStatus.PUBLISHED.value} else BookStatus.DRAFT.value,
        "show_in_library": show_in_library == "true",
        "note": note,
        "authors": book_service.parse_json_list(authors),
        "category_ids": category_service.parse_category_ids(category_ids),
        "quotes": book_service.parse_json_list(quotes),
        "buy_link_title": buy_link_title.strip(),
        "buy_link_url": buy_link_url.strip(),
        "download_file": download.strip(),
        "media_links": book_service.parse_media_links(media_links),
        "referred_book_ids": book_service.parse_referred_book_ids(referred_book_ids),
    }
    try:
        return BookForm.model_validate(payload)
    except ValidationError as exc:
        return exc


async def _resolve_book_uploads(
    form_data: BookForm,
    *,
    cover: str,
    cover_file: Optional[UploadFile],
    download: str,
    download_file: Optional[UploadFile],
    old_cover: Optional[str] = None,
    old_download: Optional[str] = None,
) -> tuple[BookForm, Optional[str]]:
    try:
        resolved_cover = await upload_service.resolve_cover(
            cover,
            cover_file,
            form_data.slug,
            old_cover=old_cover,
        )
        resolved_download = await upload_service.resolve_download(
            download,
            download_file,
            form_data.slug,
            old_download=old_download,
        )
        return form_data.model_copy(
            update={"cover": resolved_cover, "download_file": resolved_download}
        ), None
    except ValueError as exc:
        return form_data, str(exc)


async def _raw_book_preview(
    db: AsyncSession,
    title: str,
    subtitle: str,
    published_year: str,
    slug: str,
    cover: str,
    status: str,
    note: str,
    authors: str,
    category_ids: str,
    quotes: str,
    buy_link_title: str,
    buy_link_url: str,
    download: str,
    media_links: str,
    referred_book_ids: str,
    show_in_library: str = "true",
) -> _FormBookPreview:
    preview = _FormBookPreview.__new__(_FormBookPreview)
    preview.cover = cover.strip()
    preview.title = title.strip()
    preview.subtitle = subtitle.strip()
    preview.authors = book_service.parse_json_list(authors)
    preview.published_year = book_service.parse_published_year(published_year)
    preview.slug = slug.strip().lower()
    preview.status = status if status in {BookStatus.DRAFT.value, BookStatus.PUBLISHED.value} else BookStatus.DRAFT.value
    preview.show_in_library = show_in_library == "true"
    preview.categories = await category_service.get_categories_by_ids(
        db, category_service.parse_category_ids(category_ids)
    )
    preview.category_ids = [c.id for c in preview.categories]
    preview.note = note
    preview.quotes = book_service.parse_json_list(quotes)
    preview.buy_link_title = buy_link_title.strip()
    preview.buy_link_url = buy_link_url.strip()
    preview.download_file = download.strip()
    preview.media_links = [
        {"type": link.type, "url": link.url, "title": link.title}
        for link in book_service.parse_media_links(media_links)
    ]
    preview.media_links_data = preview.media_links
    preview.referred_book_ids = book_service.parse_referred_book_ids(referred_book_ids)
    preview.authors_display = "، ".join(preview.authors)
    return preview


class _FormBookPreview:
    """Lightweight object so book_form.html can re-render after validation errors."""

    def __init__(self, data: BookForm):
        self.cover = data.cover
        self.title = data.title
        self.subtitle = data.subtitle
        self.authors = data.authors
        self.published_year = data.published_year
        self.slug = data.slug
        self.status = data.status
        self.show_in_library = data.show_in_library
        self.category_ids = data.category_ids
        self.categories: list[Category] = []
        self.note = data.note
        self.quotes = data.quotes
        self.buy_link_title = data.buy_link_title
        self.buy_link_url = data.buy_link_url
        self.download_file = data.download_file
        self.media_links = [link.model_dump() for link in data.media_links]
        self.media_links_data = self.media_links
        self.referred_book_ids = data.referred_book_ids
        self.authors_display = "، ".join(data.authors)


async def _form_as_book_preview(
    db: AsyncSession, data: BookForm, slug: Optional[str] = None
) -> _FormBookPreview:
    preview = _FormBookPreview(data)
    if slug:
        preview.slug = slug
    preview.categories = await category_service.get_categories_by_ids(db, data.category_ids)
    return preview


def _parse_post_form(
    *,
    title: str,
    slug: str,
    cover: str,
    body: str,
    excerpt: str,
    status: str,
    is_featured: str,
    published_date: str,
    existing_published_date=None,
    related_book_ids: str = "[]",
) -> Union[PostForm, ValidationError]:
    payload = {
        "title": title.strip(),
        "slug": slug.strip().lower(),
        "cover": cover.strip(),
        "body": body,
        "excerpt": excerpt.strip(),
        "status": status if status in {PostStatus.DRAFT.value, PostStatus.PUBLISHED.value} else PostStatus.DRAFT.value,
        "is_featured": is_featured == "true",
        "published_date": post_service.parse_published_date(published_date) or existing_published_date,
        "related_book_ids": post_service.parse_id_list(related_book_ids),
    }
    try:
        return PostForm.model_validate(payload)
    except ValidationError as exc:
        return exc


async def _resolve_post_upload(
    form_data: PostForm,
    *,
    cover: str,
    cover_file: Optional[UploadFile],
    old_cover: Optional[str] = None,
) -> tuple[PostForm, Optional[str]]:
    try:
        resolved_cover = await upload_service.resolve_post_cover(
            cover, cover_file, form_data.slug, old_cover=old_cover
        )
        return form_data.model_copy(update={"cover": resolved_cover}), None
    except ValueError as exc:
        return form_data, str(exc)


def _raw_post_preview(
    title: str,
    slug: str,
    cover: str,
    body: str,
    excerpt: str,
    status: str,
    is_featured: str,
    published_date: str,
) -> _FormPostPreview:
    preview = _FormPostPreview.__new__(_FormPostPreview)
    preview.title = title.strip()
    preview.slug = slug.strip().lower()
    preview.cover = cover.strip()
    preview.body = body
    preview.excerpt = excerpt.strip()
    preview.status = status if status in {PostStatus.DRAFT.value, PostStatus.PUBLISHED.value} else PostStatus.DRAFT.value
    preview.is_featured = is_featured == "true"
    preview.published_date = post_service.parse_published_date(published_date)
    preview.read_time_minutes = post_service.calculate_read_time(body)
    return preview


class _FormPostPreview:
    """Lightweight object so post_form.html can re-render after validation errors."""

    def __init__(self, data: PostForm):
        self.title = data.title
        self.slug = data.slug
        self.cover = data.cover
        self.body = data.body
        self.excerpt = data.excerpt
        self.status = data.status
        self.is_featured = data.is_featured
        self.published_date = data.published_date
        self.read_time_minutes = post_service.calculate_read_time(data.body)
        self.related_book_ids = data.related_book_ids
        self.related_books: list = []


def _form_as_post_preview(data: PostForm, slug: Optional[str] = None) -> _FormPostPreview:
    preview = _FormPostPreview(data)
    if slug:
        preview.slug = slug
    return preview


def _parse_tool_form(
    *,
    title: str,
    slug: str,
    cover: str,
    category_id: str,
    short_description: str,
    body: str,
    status: str,
    files: str,
    related_book_ids: str,
    related_post_ids: str,
) -> Union[ToolForm, ValidationError]:
    payload = {
        "title": title.strip(),
        "slug": slug.strip().lower(),
        "cover": cover.strip(),
        "category_id": int(category_id) if category_id.strip().isdigit() else 0,
        "short_description": short_description.strip(),
        "body": body,
        "status": status if status in {ToolStatus.DRAFT.value, ToolStatus.PUBLISHED.value} else ToolStatus.DRAFT.value,
        "files": tool_service.parse_tool_files(files),
        "related_book_ids": tool_service.parse_id_list(related_book_ids),
        "related_post_ids": tool_service.parse_id_list(related_post_ids),
    }
    try:
        return ToolForm.model_validate(payload)
    except ValidationError as exc:
        return exc


async def _resolve_tool_uploads(
    form_data: ToolForm,
    *,
    cover: str,
    cover_file: Optional[UploadFile],
    tool_file_uploads: list[UploadFile],
    old_cover: Optional[str] = None,
) -> tuple[ToolForm, Optional[str]]:
    try:
        resolved_cover = await upload_service.resolve_tool_cover(
            cover, cover_file, form_data.slug, old_cover=old_cover
        )
        resolved_files: list[ToolFileInput] = []
        for i, entry in enumerate(form_data.files):
            upload = tool_file_uploads[i] if i < len(tool_file_uploads) else None
            if upload is not None and upload.filename:
                new_path = await upload_service.save_tool_file_upload(upload, form_data.slug)
                if entry.file and entry.file != new_path:
                    upload_service.delete_local_tool_file(entry.file)
                resolved_files.append(entry.model_copy(update={"file": new_path}))
            else:
                resolved_files.append(entry)
        return form_data.model_copy(update={"cover": resolved_cover, "files": resolved_files}), None
    except ValueError as exc:
        return form_data, str(exc)


def _raw_tool_preview(
    title: str,
    slug: str,
    cover: str,
    category_id: str,
    short_description: str,
    body: str,
    status: str,
    files: str,
    related_book_ids: str,
    related_post_ids: str,
) -> _FormToolPreview:
    preview = _FormToolPreview.__new__(_FormToolPreview)
    preview.title = title.strip()
    preview.slug = slug.strip().lower()
    preview.cover = cover.strip()
    preview.category_id = int(category_id) if category_id.strip().isdigit() else None
    preview.short_description = short_description.strip()
    preview.body = body
    preview.status = status if status in {ToolStatus.DRAFT.value, ToolStatus.PUBLISHED.value} else ToolStatus.DRAFT.value
    preview.files_data = [f.model_dump() for f in tool_service.parse_tool_files(files)]
    preview.related_book_ids = tool_service.parse_id_list(related_book_ids)
    preview.related_post_ids = tool_service.parse_id_list(related_post_ids)
    preview.related_books = []
    preview.related_posts = []
    return preview


class _FormToolPreview:
    """Lightweight object so tool_form.html can re-render after validation errors."""

    def __init__(self, data: ToolForm):
        self.title = data.title
        self.slug = data.slug
        self.cover = data.cover
        self.category_id = data.category_id
        self.short_description = data.short_description
        self.body = data.body
        self.status = data.status
        self.files_data = [f.model_dump() for f in data.files]
        self.related_book_ids = data.related_book_ids
        self.related_post_ids = data.related_post_ids
        self.related_books: list = []
        self.related_posts: list = []


async def _form_as_tool_preview(
    db: AsyncSession, data: ToolForm, slug: Optional[str] = None
) -> _FormToolPreview:
    preview = _FormToolPreview(data)
    if slug:
        preview.slug = slug
    preview.related_books = await book_service.get_books_by_ids(db, data.related_book_ids)
    from app.services.posts import get_post_by_id

    preview.related_posts = [
        p for p in [await get_post_by_id(db, pid) for pid in data.related_post_ids] if p
    ]
    return preview


class _FormAboutPreview:
    def __init__(self, data: AboutForm):
        self.author_name = data.author_name
        self.author_photo = data.author_photo
        self.author_bio = data.author_bio
        self.pet_feature_body = data.pet_feature_body
        self.site_story_body = data.site_story_body
        self.links = [link.model_dump() for link in data.links]
        self.jobs = [job.model_dump() for job in data.jobs]
        self.camps = [camp.model_dump() for camp in data.camps]


def _form_as_about_preview(data: AboutForm) -> _FormAboutPreview:
    return _FormAboutPreview(data)


# ── Book comments ──────────────────────────────────────────────────────────


@router.get("/books/comments/", name="admin_book_comments")
async def admin_book_comments_list(
    request: Request,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    current_status = status or "pending"
    comments = await book_service.list_book_comments(db, status=current_status)
    return templates.TemplateResponse(
        request,
        "admin/book_comments_list.html",
        {
            "page_title": "نظرهای کتاب‌ها",
            "active_nav": "book_comments",
            "comments": comments,
            "current_status": current_status,
        },
    )


@router.post("/books/comments/{comment_id}/approve/", name="admin_book_comment_approve")
async def admin_book_comment_approve(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    comment = await book_service.get_book_comment(db, comment_id)
    if comment:
        await book_service.set_book_comment_status(db, comment, BookCommentStatus.APPROVED.value)
    return RedirectResponse(url="/admin/books/comments/?status=pending", status_code=303)


@router.post("/books/comments/{comment_id}/reject/", name="admin_book_comment_reject")
async def admin_book_comment_reject(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    comment = await book_service.get_book_comment(db, comment_id)
    if comment:
        await book_service.set_book_comment_status(db, comment, BookCommentStatus.REJECTED.value)
    return RedirectResponse(url="/admin/books/comments/?status=pending", status_code=303)


@router.post("/books/comments/{comment_id}/delete/", name="admin_book_comment_delete")
async def admin_book_comment_delete(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    comment = await book_service.get_book_comment(db, comment_id)
    if comment:
        await book_service.delete_book_comment(db, comment)
    return RedirectResponse(url="/admin/books/comments/?status=pending", status_code=303)


@router.post("/books/comments/{comment_id}/reply/", name="admin_book_comment_reply")
async def admin_book_comment_reply(request: Request, comment_id: int, db: AsyncSession = Depends(get_db)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    comment = await book_service.get_book_comment(db, comment_id)
    if comment:
        form = await request.form()
        reply_text = str(form.get("reply", "")).strip()
        await book_service.save_book_comment_reply(db, comment, reply_text)
    return RedirectResponse(url="/admin/books/comments/?status=approved", status_code=303)


# ── Contact messages ───────────────────────────────────────────────────────


@router.get("/contact/", name="admin_contact")
async def admin_contact_list(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    messages = await contact_service.list_messages(db)
    unread = sum(1 for m in messages if not m.is_read)
    return templates.TemplateResponse(
        request,
        "admin/contact_list.html",
        _admin_context(
            request,
            page_title="پیام‌های تماس",
            active_nav="contact",
            messages=messages,
            unread_count=unread,
        ),
    )


@router.post("/contact/{message_id}/read/", name="admin_contact_toggle_read")
async def admin_contact_toggle_read(
    request: Request, message_id: int, db: AsyncSession = Depends(get_db)
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    msg = await contact_service.get_message(db, message_id)
    if msg:
        await contact_service.toggle_read(db, msg)
    return RedirectResponse(url="/admin/contact/", status_code=303)


@router.post("/contact/{message_id}/delete/", name="admin_contact_delete")
async def admin_contact_delete(
    request: Request, message_id: int, db: AsyncSession = Depends(get_db)
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    msg = await contact_service.get_message(db, message_id)
    if msg:
        await contact_service.delete_message(db, msg)
    return RedirectResponse(url="/admin/contact/", status_code=303)


# ── Analytics dashboard ────────────────────────────────────────────────────

VALID_PERIODS = {"today", "7d", "30d", "all"}


@router.get("/analytics/", name="admin_analytics")
async def admin_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    period: str = "7d",
):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login/", status_code=303)
    if period not in VALID_PERIODS:
        period = "7d"

    summary = await analytics_service.get_summary(db, period)
    books   = await analytics_service.top_books(db, period)
    posts   = await analytics_service.top_posts(db, period)
    tools   = await analytics_service.top_tools(db, period)
    daily   = await analytics_service.daily_traffic(db, period)
    refs    = await analytics_service.top_referrers(db, period)

    return templates.TemplateResponse(
        request,
        "admin/analytics.html",
        _admin_context(
            request,
            page_title="آنالیتیکس",
            active_nav="analytics",
            period=period,
            summary=summary,
            top_books=books,
            top_posts=posts,
            top_tools=tools,
            daily_traffic=daily,
            top_referrers=refs,
        ),
    )


# ── Editor image upload ────────────────────────────────────────────────────

@router.post("/upload/image/", name="admin_upload_image")
async def admin_upload_image(
    request: Request,
    file: UploadFile = File(...),
):
    """AJAX endpoint: upload an inline image from the post body editor.
    Returns JSON {"url": "..."} on success or {"error": "..."} on failure.
    """
    if not is_admin_authenticated(request):
        return JSONResponse({"error": "احراز هویت نشده"}, status_code=403)
    try:
        url = await upload_service.save_post_image_upload(file)
        return JSONResponse({"url": url})
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)


# ── Media Library ──────────────────────────────────────────────────────────

@router.get("/files/", name="admin_files")
async def admin_files_list(
    request: Request,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
):
    if redirect := _guard_admin(request):
        return redirect
    files, total = await get_media_files(db, page=page, per_page=50)
    base_url = str(request.base_url).rstrip("/")
    return templates.TemplateResponse(
        request,
        "admin/files_list.html",
        _admin_context(
            request,
            page_title="کتابخانه رسانه",
            active_nav="files",
            files=files,
            total=total,
            page=page,
            per_page=50,
            base_url=base_url,
            human_size=human_size,
            error=None,
            show_upload_form=False,
        ),
    )


@router.post("/files/upload", name="admin_files_upload")
async def admin_files_upload(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if redirect := _guard_admin(request):
        return redirect
    try:
        await upload_media_file(file, db)
        return RedirectResponse("/admin/files/", status_code=303)
    except HTTPException as exc:
        files, total = await get_media_files(db, page=1, per_page=50)
        base_url = str(request.base_url).rstrip("/")
        return templates.TemplateResponse(
            request,
            "admin/files_list.html",
            _admin_context(
                request,
                page_title="کتابخانه رسانه",
                active_nav="files",
                files=files,
                total=total,
                page=1,
                per_page=50,
                base_url=base_url,
                human_size=human_size,
                error=exc.detail,
                show_upload_form=True,
            ),
            status_code=400,
        )


@router.post("/files/{file_id}/delete", name="admin_files_delete")
async def admin_files_delete(
    request: Request,
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    if redirect := _guard_admin(request):
        return redirect
    await delete_media_file(file_id, db)
    return RedirectResponse("/admin/files/", status_code=303)
