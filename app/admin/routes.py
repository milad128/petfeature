"""Admin CMS routes — content management for books and about page."""

from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
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
from app.models.book import BookStatus
from app.models.category import Category
from app.schemas.about import AboutForm, LinkInput
from app.schemas.book import BookForm
from app.schemas.category import CategoryForm
from app.services import about as about_service
from app.services import books as book_service
from app.services import categories as category_service
from app.services import uploads as upload_service

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
    return templates.TemplateResponse(
        request,
        "admin/books_list.html",
        _admin_context(
            request,
            page_title="کتاب‌ها",
            active_nav="books",
            books=books,
            search_query=q,
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
    category = await category_service.get_category(db, category_id)
    if category:
        await category_service.delete_category(db, category)
    return RedirectResponse(url="/admin/categories/", status_code=303)


async def _get_category_by_name(db: AsyncSession, name: str):
    stmt = select(Category).where(Category.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


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


class _FormAboutPreview:
    def __init__(self, data: AboutForm):
        self.author_name = data.author_name
        self.author_photo = data.author_photo
        self.author_bio = data.author_bio
        self.pet_feature_body = data.pet_feature_body
        self.site_story_body = data.site_story_body
        self.links = [link.model_dump() for link in data.links]


def _form_as_about_preview(data: AboutForm) -> _FormAboutPreview:
    return _FormAboutPreview(data)
