"""Comprehensive RTL coverage — every user-facing GET page must render dir="rtl".

Contract under test: the base template declares `<html lang="fa" dir="rtl">`,
so any page that extends it must include `dir="rtl"` in the returned HTML.

Layers covered:
  1. Static public pages (parametrized) — already in test_web_pages.py, duplicated
     here so this file is self-contained as a RTL audit.
  2. Detail pages that require seeded data (book, post, tool) — rows are created via
     the service layer using `db_session`, then the detail URL is fetched via `client`.
  3. Roadmap pages — /path/, /path/hiring/, /path/apm/ (full), /path/pm/ (stub).
  4. Admin pages — GET /admin/login/ (public) and GET /admin/books/ (authenticated).
"""

import pytest

from app.models.book import Book, BookStatus
from app.models.category import Category
from app.models.post import Post, PostStatus
from app.models.tool import Tool, ToolStatus
from app.schemas.book import BookForm
from app.schemas.tool import ToolForm
from app.services import books as book_service
from app.services import tools as tool_service


# ── Helpers ───────────────────────────────────────────────────────────────────

def _assert_rtl_200(resp, path: str) -> None:
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"
    assert 'dir="rtl"' in resp.text, f'{path} is missing dir="rtl"'


# ── 1. Static public pages ────────────────────────────────────────────────────

STATIC_PUBLIC_PAGES = [
    "/",
    "/library/",
    "/blog/",
    "/tools/",
    "/about/",
    "/contact/",
]


@pytest.mark.parametrize("path", STATIC_PUBLIC_PAGES)
async def test_static_public_page_is_rtl(client, path):
    resp = await client.get(path)
    _assert_rtl_200(resp, path)


# ── 2. Detail pages that need seeded data ────────────────────────────────────

async def test_book_detail_is_rtl(client, db_session):
    """Seed a published book, then verify /library/{slug}/ renders RTL."""
    form = BookForm(
        title="کتاب آزمایشی",
        authors=["نویسنده تست"],
        slug="test-book-rtl",
        status="published",
        show_in_library=True,
    )
    await book_service.create_book(db_session, form)

    resp = await client.get("/library/test-book-rtl/")
    _assert_rtl_200(resp, "/library/test-book-rtl/")


async def test_book_detail_not_found_is_rtl(client):
    """Detail page for a non-existent book slug still renders RTL (graceful null state)."""
    resp = await client.get("/library/slug-does-not-exist/")
    # The route returns 200 with book=None rendered in the template
    _assert_rtl_200(resp, "/library/slug-does-not-exist/")


async def test_post_detail_is_rtl(client, db_session):
    """Seed a published post, then verify /blog/{slug}/ renders RTL.

    We insert the Post row directly via ORM rather than calling
    post_service.create_post() to avoid the lazy-load triggered by
    _sync_related_books when related_book_ids is empty.
    """
    post = Post(
        title="یادداشت آزمایشی",
        slug="test-post-rtl",
        body="<p>محتوای تست</p>",
        status=PostStatus.PUBLISHED.value,
        read_time_minutes=1,
        view_count=0,
    )
    db_session.add(post)
    await db_session.commit()

    resp = await client.get("/blog/test-post-rtl/")
    _assert_rtl_200(resp, "/blog/test-post-rtl/")


async def test_post_detail_not_found_is_rtl(client):
    """Detail page for a non-existent post slug renders RTL (null state)."""
    resp = await client.get("/blog/slug-does-not-exist/")
    _assert_rtl_200(resp, "/blog/slug-does-not-exist/")


async def test_tool_detail_is_rtl(client, db_session):
    """Seed a category + published tool, then verify /tools/{slug}/ renders RTL."""
    # Tool requires a category FK
    category = Category(name="دسته تست")
    db_session.add(category)
    await db_session.flush()

    form = ToolForm(
        title="ابزار آزمایشی",
        slug="test-tool-rtl",
        category_id=category.id,
        short_description="توضیح کوتاه",
        body="<p>محتوا</p>",
        status="published",
    )
    await tool_service.create_tool(db_session, form)

    resp = await client.get("/tools/test-tool-rtl/")
    _assert_rtl_200(resp, "/tools/test-tool-rtl/")


async def test_tool_detail_not_found_is_rtl(client):
    """Detail page for a non-existent tool slug renders RTL (null state)."""
    resp = await client.get("/tools/slug-does-not-exist/")
    _assert_rtl_200(resp, "/tools/slug-does-not-exist/")


# ── 3. Roadmap pages ──────────────────────────────────────────────────────────

async def test_roadmap_landing_is_rtl(client):
    """/path/ — roadmap landing page, no DB data required."""
    resp = await client.get("/path/")
    _assert_rtl_200(resp, "/path/")


async def test_roadmap_hiring_is_rtl(client):
    """/path/hiring/ — L0 hiring page, works with empty DB."""
    resp = await client.get("/path/hiring/")
    _assert_rtl_200(resp, "/path/hiring/")


async def test_roadmap_apm_full_page_is_rtl(client):
    """/path/apm/ — L1 full page (APM), works without any RoadmapResource rows."""
    resp = await client.get("/path/apm/")
    _assert_rtl_200(resp, "/path/apm/")


@pytest.mark.parametrize("stub_slug", ["pm", "senior-pm", "lead", "director", "cpo"])
async def test_roadmap_stub_pages_are_rtl(client, stub_slug):
    """/path/{stub_slug}/ — L2–L6 stub pages return 200 RTL (not 404)."""
    path = f"/path/{stub_slug}/"
    resp = await client.get(path)
    _assert_rtl_200(resp, path)


async def test_roadmap_unknown_slug_renders_rtl(client):
    """/path/unknown-slug/ — unknown slug returns 404 with RTL stub template."""
    resp = await client.get("/path/totally-unknown-slug/")
    # The route renders roadmap_stub.html with status_code=404
    assert resp.status_code == 404, "/path/unknown-slug/ should return 404"
    assert 'dir="rtl"' in resp.text, "/path/unknown-slug/ 404 page should be RTL"


# ── 4. Admin pages ────────────────────────────────────────────────────────────

async def test_admin_login_page_is_rtl(client):
    """GET /admin/login/ is public and must render RTL."""
    resp = await client.get("/admin/login/")
    _assert_rtl_200(resp, "/admin/login/")


async def test_admin_books_page_is_rtl(admin_client):
    """GET /admin/books/ (authenticated) must render RTL."""
    resp = await admin_client.get("/admin/books/")
    _assert_rtl_200(resp, "/admin/books/")
