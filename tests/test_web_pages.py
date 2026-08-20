"""SSR "frontend" tests — assert public pages render as RTL HTML.

No browser is involved: we assert on the server-rendered HTML returned by the
Jinja2 templates (status code + RTL/Persian markup).
"""

import pytest

PUBLIC_PAGES = [
    "/",
    "/library/",
    "/blog/",
    "/tools/",
    "/about/",
    "/contact/",
]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
async def test_public_page_renders(client, path):
    resp = await client.get(path)
    assert resp.status_code == 200, f"{path} should return 200"
    body = resp.text
    # base.html declares `<html lang="fa" dir="rtl">` — every page extends it.
    assert 'dir="rtl"' in body, f"{path} should render RTL HTML"


async def test_home_is_html(client):
    resp = await client.get("/")
    assert resp.headers["content-type"].startswith("text/html")
