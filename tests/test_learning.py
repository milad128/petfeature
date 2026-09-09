"""v17 learning enrollment — service + HTTP flows."""

from __future__ import annotations

import base64
import json

import pytest
from itsdangerous import TimestampSigner
from sqlalchemy import select

from app.core.config import settings
from app.models.learning import Enrollment, ResourceProgress
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
        email=f"sara{suffix}@example.com",
        google_id=f"gid-{suffix}",
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


def _login(client, user_id: int) -> None:
    client.cookies.set("session", _session_cookie(user_id))


async def test_enroll_is_idempotent_and_restores(db_session):
    user = await _user(db_session)
    first = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    second = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    assert first.id == second.id

    ok = await learning_service.unenroll(db_session, user.id, "apm")
    assert ok is True
    assert await learning_service.get_enrollment(db_session, user.id, "apm") is None

    restored = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    assert restored.id == first.id
    assert restored.unenrolled_at is None


async def test_progress_formula_ignores_optional_and_skipped(db_session):
    user = await _user(db_session)
    req1 = await _resource(db_session, title="A")
    req2 = await _resource(db_session, title="B")
    await _resource(db_session, title="Opt", required=False)

    enrollment = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    progress = await learning_service.compute_progress(db_session, enrollment)
    assert progress.required == 2
    assert progress.pct == 0
    assert progress.blank == 2

    await learning_service.set_resource_status(db_session, enrollment.id, req1.id, "DONE")
    await learning_service.set_resource_status(db_session, enrollment.id, req2.id, "SKIPPED")
    progress = await learning_service.compute_progress(db_session, enrollment)
    assert progress.done == 1
    assert progress.pct == 50
    assert progress.badge == "in_progress"

    await learning_service.set_resource_status(
        db_session, enrollment.id, req2.id, "ALREADY_KNEW"
    )
    progress = await learning_service.compute_progress(db_session, enrollment)
    assert progress.pct == 100
    await db_session.refresh(enrollment)
    assert enrollment.completed_at is not None


async def test_re_enroll_keeps_progress(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    await learning_service.set_resource_status(
        db_session, enrollment.id, resource.id, "STUDYING"
    )
    await learning_service.unenroll(db_session, user.id, "apm")
    restored = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    resources = await learning_service.list_resources_with_status(
        db_session, "apm", restored
    )
    assert resources[0]._status == "STUDYING"


async def test_stub_level_not_enrollable(db_session):
    user = await _user(db_session)
    with pytest.raises(ValueError):
        await learning_service.get_or_create_enrollment(db_session, user.id, "cpo")


async def test_invalid_status_rejected(db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    enrollment = await learning_service.get_or_create_enrollment(db_session, user.id, "apm")
    with pytest.raises(ValueError):
        await learning_service.set_resource_status(
            db_session, enrollment.id, resource.id, "WANT_TO_STUDY"
        )


async def test_catalog_is_public_without_status_select(client, db_session):
    await _resource(db_session)
    resp = await client.get("/dashboard/learning/apm/")
    assert resp.status_code == 200
    assert "Inspired" in resp.text
    assert "learn-status" not in resp.text
    assert "شروع یادگیری" in resp.text
    assert 'dir="rtl"' in resp.text
    assert "/login/?next=/dashboard/learning/apm/enroll/" in resp.text


async def test_catalog_unknown_slug_404(client):
    resp = await client.get("/dashboard/learning/cpo/")
    assert resp.status_code == 404


async def test_index_requires_login(client):
    resp = await client.get("/dashboard/learning/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/login/" in resp.headers["location"]


async def test_index_empty_state(client, db_session):
    user = await _user(db_session)
    _login(client, user.id)
    resp = await client.get("/dashboard/learning/")
    assert resp.status_code == 200
    assert "هنوز در هیچ سطحی ثبت‌نام نکرده‌اید" in resp.text


async def test_guest_enroll_redirects_to_login(client):
    resp = await client.get(
        "/dashboard/learning/apm/enroll/", follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login/?next=/dashboard/learning/apm/enroll/"


async def test_enroll_post_redirects_to_tracker(client, db_session):
    user = await _user(db_session)
    await _resource(db_session)
    _login(client, user.id)
    resp = await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/learning/apm/track/"

    again = await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    assert again.status_code == 303
    rows = (
        await db_session.execute(select(Enrollment).where(Enrollment.user_id == user.id))
    ).scalars().all()
    assert len(rows) == 1


async def test_tracker_has_status_select(client, db_session):
    user = await _user(db_session)
    await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.get("/dashboard/learning/apm/track/")
    assert resp.status_code == 200
    assert "learn-status" in resp.text
    assert "وضعیت ندارد" in resp.text
    assert "می‌خوام بخونم" not in resp.text


async def test_catalog_after_enroll_has_no_select(client, db_session):
    user = await _user(db_session)
    await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.get("/dashboard/learning/apm/")
    assert resp.status_code == 200
    assert "learn-status" not in resp.text
    assert "ادامه یادگیری" in resp.text


async def test_progress_form_updates_status(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.post(
        "/dashboard/learning/apm/progress/",
        data={"resource_id": str(resource.id), "status": "DONE"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    row = (await db_session.execute(select(ResourceProgress))).scalar_one()
    assert row.status == "DONE"


async def test_path_page_shows_enroll_cta(client):
    resp = await client.get("/path/apm/")
    assert resp.status_code == 200
    assert "شروع یادگیری" in resp.text
    assert "learn-enroll-card" in resp.text
    assert "نفر در حال یادگیری" in resp.text
    assert "نفر این سطح را تمام کرده‌اند" in resp.text


async def test_pm_path_shows_enroll_banner(client):
    resp = await client.get("/path/pm/")
    assert resp.status_code == 200
    assert "learn-enroll-card" in resp.text
    assert "شروع یادگیری این سطح" in resp.text
    assert "در حال یادگیری" in resp.text
    assert "تمام‌کرده" in resp.text


async def test_hiring_page_shows_enroll_cta(client):
    resp = await client.get("/path/hiring/")
    assert resp.status_code == 200
    assert "شروع یادگیری" in resp.text
    assert "learn-status" not in resp.text


async def test_stub_path_has_no_enroll_button(client):
    resp = await client.get("/path/lead/")
    assert resp.status_code == 200
    assert "شروع یادگیری" not in resp.text


async def test_login_stores_enroll_next(client):
    resp = await client.get("/login/?next=/dashboard/learning/apm/enroll/")
    assert resp.status_code == 200
    assert "ورود" in resp.text


async def test_api_progress_requires_auth(client):
    resp = await client.post(
        "/api/v1/learning/apm/progress/",
        json={"resource_id": 1, "status": "DONE"},
    )
    assert resp.status_code == 401


async def test_api_progress_requires_enrollment(client, db_session):
    user = await _user(db_session)
    resource = await _resource(db_session)
    _login(client, user.id)
    resp = await client.post(
        "/api/v1/learning/apm/progress/",
        json={"resource_id": resource.id, "status": "DONE"},
    )
    assert resp.status_code == 403


async def test_profile_shows_learning_badges(client, db_session):
    user = await _user(db_session)
    await _resource(db_session)
    _login(client, user.id)
    await client.post("/dashboard/learning/apm/enroll/", follow_redirects=False)
    resp = await client.get("/profile/")
    assert resp.status_code == 200
    assert "ثبت‌نام شده" in resp.text
    assert "ادامه یادگیری" in resp.text
