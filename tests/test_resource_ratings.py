"""v18.1 resource ratings — prompt on DONE/ALREADY_KNEW, admin aggregates."""

from __future__ import annotations

import base64
import json

from itsdangerous import TimestampSigner
from sqlalchemy import func, select

from app.core.config import settings
from app.models.learning import ResourceProgress, ResourceRating
from app.models.roadmap import RoadmapResource
from app.models.user import User
from app.services import learning as learning_service


def _session_cookie(user_id: int) -> str:
    signer = TimestampSigner(settings.secret_key)
    payload = base64.b64encode(json.dumps({"user_id": user_id}).encode("utf-8"))
    return signer.sign(payload).decode("utf-8")


async def _user(db, *, suffix: str = "1") -> User:
    user = User(
        name="سارا تست",
        email=f"rate{suffix}@example.com",
        google_id=f"gid-rate-{suffix}",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _resource(
    db,
    *,
    slug: str = "apm",
    title: str = "Inspired",
) -> RoadmapResource:
    row = RoadmapResource(
        level_slug=slug,
        category="entry",
        title=title,
        resource_type="book",
        is_required=True,
        sort_order=10,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


def _login(client, user_id: int) -> None:
    client.cookies.set("session", _session_cookie(user_id))


async def test_done_prompts_rating(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    update = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    assert update.prompt_rating is True
    assert update.row.status == "DONE"


async def test_already_knew_prompts_rating(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    update = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "ALREADY_KNEW"
    )
    assert update.prompt_rating is True
    assert update.row.status == "ALREADY_KNEW"


async def test_skipped_and_studying_do_not_prompt(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    skipped = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "SKIPPED"
    )
    studying = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "STUDYING"
    )
    assert skipped.prompt_rating is False
    assert studying.prompt_rating is False


async def test_second_done_after_rating_does_not_prompt(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    await learning_service.upsert_resource_rating(
        db_session, user.id, "apm", resource.id, 5
    )
    again = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    assert again.prompt_rating is False


async def test_switch_done_to_already_knew_prompts_if_unrated(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    switched = await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "ALREADY_KNEW"
    )
    assert switched.prompt_rating is True


async def test_upsert_rating_and_change_stars(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    first = await learning_service.upsert_resource_rating(
        db_session, user.id, "apm", resource.id, 5
    )
    first_updated = first.updated_at
    second = await learning_service.upsert_resource_rating(
        db_session, user.id, "apm", resource.id, 2
    )
    assert second.id == first.id
    assert second.stars == 2
    assert second.updated_at >= first_updated
    count = await db_session.scalar(select(func.count()).select_from(ResourceRating))
    assert count == 1


async def test_invalid_stars_rejected(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    try:
        await learning_service.upsert_resource_rating(
            db_session, user.id, "apm", resource.id, 0
        )
        assert False, "expected invalid_stars"
    except ValueError as exc:
        assert str(exc) == "invalid_stars"
    assert (await db_session.scalar(select(func.count()).select_from(ResourceRating))) == 0


async def test_unenroll_keeps_rating_in_admin_average(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    await learning_service.upsert_resource_rating(
        db_session, user.id, "apm", resource.id, 4
    )
    await learning_service.unenroll(db_session, user.id, "apm")
    stats = await learning_service.rating_stats_by_resource_ids(
        db_session, [resource.id]
    )
    assert stats[resource.id] == (4.0, 1)


async def test_api_progress_includes_prompt(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.post(
        "/api/v1/learning/apm/progress/",
        json={"resource_id": resource.id, "status": "DONE"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["prompt_rating"] is True
    assert body["resource_id"] == resource.id


async def test_html_progress_redirects_with_rate_query(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.post(
        "/dashboard/learning/apm/progress/",
        data={"resource_id": str(resource.id), "status": "SKIPPED"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "rate=" not in resp.headers["location"]


async def test_tracker_shows_rate_cta_when_done_unrated(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    await client.post(
        "/dashboard/learning/apm/progress/",
        data={"resource_id": str(resource.id), "status": "DONE"},
        follow_redirects=False,
    )
    resp = await client.get("/dashboard/learning/apm/track/?rate=" + str(resource.id))
    assert resp.status_code == 200
    assert "این منبع چقدر به‌دردت خورد؟" in resp.text
    assert "امتیاز بده" in resp.text
    assert 'action="/dashboard/learning/apm/rate/"' in resp.text
    assert "بعداً" in resp.text


async def test_rate_post_saves_stars(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.post(
        "/dashboard/learning/apm/rate/",
        data={"resource_id": str(resource.id), "stars": "4"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "rate=" not in resp.headers["location"]
    row = (await db_session.execute(select(ResourceRating))).scalar_one()
    assert row.stars == 4
    assert row.user_id == user.id


async def test_rate_invalid_stars_422(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    await client.post(
        "/dashboard/learning/apm/progress/",
        data={"resource_id": str(resource.id), "status": "DONE"},
        follow_redirects=False,
    )
    resp = await client.post(
        "/dashboard/learning/apm/rate/",
        data={"resource_id": str(resource.id), "stars": "6"},
    )
    assert resp.status_code == 422
    assert "امتیاز نامعتبر است" in resp.text
    assert (await db_session.scalar(select(func.count()).select_from(ResourceRating))) == 0
    progress = await db_session.scalar(select(func.count()).select_from(ResourceProgress))
    assert progress == 1


async def test_rate_anonymous_redirects(client, db_session):
    resource = await _resource(db_session)
    resp = await client.post(
        "/dashboard/learning/apm/rate/",
        data={"resource_id": str(resource.id), "stars": "3"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/login/" in resp.headers["location"]


async def test_rate_not_enrolled_403(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    resp = await client.post(
        "/dashboard/learning/apm/rate/",
        data={"resource_id": str(resource.id), "stars": "3"},
        follow_redirects=False,
    )
    assert resp.status_code == 403


async def test_rate_other_level_resource_404(client, db_session):
    user = await _user(db_session)
    hiring = await _resource(db_session, slug="hiring", title="CV")
    await _resource(db_session, slug="apm")
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.post(
        "/dashboard/learning/apm/rate/",
        data={"resource_id": str(hiring.id), "stars": "3"},
        follow_redirects=False,
    )
    assert resp.status_code == 404


async def test_api_rate_anonymous_401(client):
    resp = await client.post(
        "/api/v1/learning/apm/rate/",
        json={"resource_id": 1, "stars": 4},
    )
    assert resp.status_code == 401


async def test_path_page_has_no_rating_ui(client):
    resp = await client.get("/path/apm/")
    assert resp.status_code == 200
    assert "این منبع چقدر به‌دردت خورد؟" not in resp.text
    assert "learn-rate-cta" not in resp.text
    assert "میانگین امتیاز" not in resp.text


async def test_admin_list_shows_dash_then_mean(admin_client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    empty = await admin_client.get("/admin/roadmap/")
    assert empty.status_code == 200
    assert "<th>امتیاز</th>" in empty.text
    assert " رای" not in empty.text

    enrollment = await learning_service.get_or_create_enrollment(
        db_session, user.id, "apm"
    )
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "DONE"
    )
    await learning_service.upsert_resource_rating(
        db_session, user.id, "apm", resource.id, 5
    )
    listed = await admin_client.get("/admin/roadmap/")
    assert "۵.۰ ★" in listed.text
    assert "۱ رای" in listed.text

    edit = await admin_client.get(f"/admin/roadmap/{resource.id}/edit/")
    assert edit.status_code == 200
    assert "امتیاز یادگیرنده‌ها: میانگین ۵.۰ از ۵" in edit.text
    assert "۱ رای" in edit.text

    detail = await admin_client.get(
        f"/admin/learning/enrollments/{enrollment.id}/"
    )
    assert detail.status_code == 200
    assert "امتیاز این کاربر" in detail.text
    assert "۵ از ۵" in detail.text
