"""Admin contact inbox — unread badge and message detail."""

from __future__ import annotations

from app.models.contact import ContactMessage


async def _seed_message(
    db,
    *,
    email: str = "milad@example.com",
    name: str = "میلاد",
    subject: str = "موضوع تست",
    message: str = "سلام پیام دارم",
    is_read: bool = False,
) -> ContactMessage:
    row = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message,
        is_read=is_read,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def test_contact_list_requires_login(client):
    resp = await client.get("/admin/contact/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login/" in resp.headers["location"]


async def test_unread_badge_on_nav(admin_client, db_session):
    await _seed_message(db_session, message="پیام خوانده‌نشده برای بج")
    resp = await admin_client.get("/admin/contact/")
    assert resp.status_code == 200
    assert "nav-badge" in resp.text
    assert "پیام خوانده‌نشده برای بج" in resp.text
    assert "مشاهده" in resp.text


async def test_no_badge_when_all_read(admin_client, db_session):
    await _seed_message(db_session, is_read=True, message="قبلاً خوانده شده")
    resp = await admin_client.get("/admin/books/")
    assert resp.status_code == 200
    assert "پیام‌های تماس" in resp.text
    # Badge is only rendered when unread_contact_count is truthy
    assert 'href="/admin/contact/"' in resp.text
    contact_nav = resp.text.split("پیام‌های تماس", 1)[1].split("آنالیتیکس", 1)[0]
    assert "nav-badge" not in contact_nav


async def test_detail_shows_full_message_and_marks_read(admin_client, db_session):
    long_body = "سلام پیام دارم\n" + ("خط دوم طولانی. " * 20)
    msg = await _seed_message(db_session, message=long_body)
    assert msg.is_read is False

    resp = await admin_client.get(f"/admin/contact/{msg.id}/")
    assert resp.status_code == 200
    assert long_body in resp.text
    assert "بازگشت به فهرست" in resp.text
    assert "milad@example.com" in resp.text

    await db_session.refresh(msg)
    assert msg.is_read is True


async def test_detail_missing_404(admin_client):
    resp = await admin_client.get("/admin/contact/99999/")
    assert resp.status_code == 404


async def test_detail_requires_login(client, db_session):
    msg = await _seed_message(db_session)
    resp = await client.get(f"/admin/contact/{msg.id}/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login/" in resp.headers["location"]
