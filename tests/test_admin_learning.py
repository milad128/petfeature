"""v18 enrollment admin — stats, list filters, detail, analytics snippet."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.page_view import PageView
from app.models.roadmap import RoadmapResource
from app.models.user import User
from app.services import learning as learning_service


async def _user(db, *, suffix: str = "1", name: str = "سارا تست") -> User:
    user = User(
        name=name,
        email=f"sara{suffix}@example.com",
        google_id=f"gid-admin-{suffix}",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _resource(
    db,
    *,
    slug: str = "apm",
    required: bool = True,
    title: str = "Inspired",
    category: str = "entry",
) -> RoadmapResource:
    row = RoadmapResource(
        level_slug=slug,
        category=category,
        title=title,
        resource_type="book",
        is_required=required,
        sort_order=10,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def test_overview_empty_zeros(db_session):
    overview = await learning_service.admin_overview(db_session, 30)
    assert overview["snapshot"]["active"] == 0
    assert overview["snapshot"]["learning"] == 0
    assert overview["snapshot"]["completed"] == 0
    assert overview["snapshot"]["unenrolled"] == 0
    assert overview["snapshot"]["unique_learners"] == 0
    assert overview["snapshot"]["avg_progress"] is None
    assert overview["period"]["new_enrolls"] == 0
    assert [row["slug"] for row in overview["levels"]] == ["hiring", "apm", "pm"]
    assert all(row["active"] == 0 for row in overview["levels"])
    assert overview["stalled"] == []
    assert overview["status_mix"][0]["key"] == "blank"
    assert overview["status_mix"][0]["count"] == 0


async def test_overview_snapshot_and_period(db_session):
    sara = await _user(db_session, suffix="s")
    nima = await _user(db_session, suffix="n", name="نیما")
    req = await _resource(db_session)
    await _resource(db_session, title="Second")

    apm = await learning_service.get_or_create_enrollment(db_session, sara.id, "apm")
    await learning_service.get_or_create_enrollment(db_session, sara.id, "pm")
    await learning_service.get_or_create_enrollment(db_session, nima.id, "hiring")

    await learning_service.set_resource_status(db_session, apm.id, req.id, "DONE")
    await learning_service.unenroll(db_session, nima.id, "hiring")

    old = await learning_service.get_or_create_enrollment(db_session, nima.id, "pm")
    old.enrolled_at = datetime.now(timezone.utc) - timedelta(days=40)
    await db_session.commit()

    overview = await learning_service.admin_overview(db_session, 30)
    snap = overview["snapshot"]
    assert snap["active"] == 3  # sara apm, sara pm, nima pm
    assert snap["unique_learners"] == 2
    assert snap["unenrolled"] == 1
    assert snap["learning"] == 3
    assert snap["completed"] == 0
    assert overview["period"]["new_enrolls"] == 3  # 40-day-old pm excluded
    assert overview["period"]["new_unenrolls"] == 1

    all_time = await learning_service.admin_overview(db_session, None)
    assert all_time["period"]["new_enrolls"] == 4
    assert all_time["series_bucket"] == "month"

    hiring_row = next(r for r in overview["levels"] if r["slug"] == "hiring")
    assert hiring_row["unenrolled"] == 1
    assert hiring_row["active"] == 0


async def test_overview_stalled_and_avg_progress(db_session):
    user = await _user(db_session)
    await _resource(db_session)
    await _resource(db_session, title="B")
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    enrollment.enrolled_at = datetime.now(timezone.utc) - timedelta(days=20)
    await db_session.commit()

    overview = await learning_service.admin_overview(db_session, 30)
    assert overview["snapshot"]["avg_progress"] == 0
    assert len(overview["stalled"]) == 1
    assert overview["stalled"][0]["id"] == enrollment.id


async def test_overview_conversion_from_path_views(db_session):
    user = await _user(db_session)
    await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    db_session.add(
        PageView(
            path="/path/apm/",
            page_type="roadmap_level",
            visitor_token="tok-1",
        )
    )
    db_session.add(
        PageView(
            path="/path/apm/",
            page_type="roadmap_level",
            visitor_token="tok-2",
        )
    )
    await db_session.commit()

    overview = await learning_service.admin_overview(db_session, 30)
    apm = next(r for r in overview["levels"] if r["slug"] == "apm")
    assert apm["views"] == 2
    assert apm["new_enrolls"] == 1
    assert apm["conversion"] == 50


async def test_list_filters_search_and_progress(db_session):
    sara = await _user(db_session, suffix="s", name="سارا احمدی")
    nima = await _user(db_session, suffix="n", name="نیما رضایی")
    req1 = await _resource(db_session, title="A")
    req2 = await _resource(db_session, title="B")

    apm = await learning_service.get_or_create_enrollment(db_session, sara.id, "apm")
    await learning_service.set_resource_status(db_session, apm.id, req1.id, "DONE")
    await learning_service.set_resource_status(db_session, apm.id, req2.id, "SKIPPED")
    await learning_service.get_or_create_enrollment(db_session, nima.id, "pm")
    hiring = await learning_service.get_or_create_enrollment(db_session, nima.id, "hiring")
    await learning_service.unenroll(db_session, nima.id, "hiring")

    tracker = await learning_service.compute_progress(db_session, apm)
    listing = await learning_service.admin_list_enrollments(db_session, state="active")
    assert listing["total"] == 2
    apm_row = next(r for r in listing["rows"] if r["id"] == apm.id)
    assert apm_row["progress"].pct == tracker.pct == 50
    assert apm_row["badge_fa"] == "در حال یادگیری"
    assert apm_row["last_progress_at"] is not None

    by_level = await learning_service.admin_list_enrollments(
        db_session, level="apm", state="all"
    )
    assert by_level["total"] == 1

    unenrolled = await learning_service.admin_list_enrollments(
        db_session, state="unenrolled"
    )
    assert unenrolled["total"] == 1
    assert unenrolled["rows"][0]["id"] == hiring.id
    assert unenrolled["rows"][0]["badge_fa"] is None

    search = await learning_service.admin_list_enrollments(
        db_session, state="all", q="احمدی"
    )
    assert search["total"] == 1
    assert search["rows"][0]["user_name"] == "سارا احمدی"

    email_ok = await learning_service.admin_list_enrollments(
        db_session, state="all", q="saras@"
    )
    assert email_ok["total"] == 1


async def test_admin_get_enrollment_includes_unenrolled(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "STUDYING"
    )
    await learning_service.unenroll(db_session, user.id, "apm")

    detail = await learning_service.admin_get_enrollment(db_session, enrollment.id)
    assert detail is not None
    assert detail["state"] == "unenrolled"
    assert detail["badge_fa"] is None
    assert detail["groups"][0]["resources"][0]._status == "STUDYING"
    assert detail["progress"].studying == 1
    assert await learning_service.admin_get_enrollment(db_session, 99999) is None


async def test_admin_pages_require_login(client):
    for path in (
        "/admin/learning/",
        "/admin/learning/enrollments/",
        "/admin/learning/enrollments/1/",
    ):
        resp = await client.get(path, follow_redirects=False)
        assert resp.status_code == 303, path
        assert "/admin/login/" in resp.headers["location"]


async def test_admin_overview_page_empty(admin_client):
    resp = await admin_client.get("/admin/learning/")
    assert resp.status_code == 200
    assert "ثبت‌نام فعال" in resp.text
    assert "ثبت‌نام متوقف‌شده‌ای نیست." in resp.text
    assert "همه ثبت‌نام‌ها" in resp.text
    assert "۰" in resp.text


async def test_admin_list_and_detail_pages(admin_client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )

    listing = await admin_client.get("/admin/learning/enrollments/")
    assert listing.status_code == 200
    assert "سارا تست" in listing.text
    assert "learn-status" not in listing.text

    detail = await admin_client.get(
        f"/admin/learning/enrollments/{enrollment.id}/"
    )
    assert detail.status_code == 200
    assert "پیشرفت = (خوندم + قبلاً می‌دونستم) ÷ منابع الزامی" in detail.text
    assert "Inspired" in detail.text
    assert "خوندم" in detail.text
    assert "learn-status" not in detail.text
    assert "بازگشت به فهرست" in detail.text
    assert 'name="status"' not in detail.text

    missing = await admin_client.get("/admin/learning/enrollments/99999/")
    assert missing.status_code == 404


async def test_analytics_snippet_links_to_learning_admin(admin_client, db_session):
    user = await _user(db_session)
    await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    resp = await admin_client.get("/admin/analytics/")
    assert resp.status_code == 200
    assert "آمار ثبت‌نام یادگیری" in resp.text
    assert "/admin/learning/" in resp.text
    assert "<th>ثبت‌نام فعال</th>" not in resp.text
