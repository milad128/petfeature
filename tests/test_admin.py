"""Admin auth guard tests — protected routes require a session."""


async def test_admin_requires_login(client):
    resp = await client.get("/admin/books/", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/admin/login/" in resp.headers.get("location", "")


async def test_admin_access_with_session(admin_client):
    resp = await admin_client.get("/admin/books/")
    assert resp.status_code == 200
