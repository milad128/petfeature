"""Public learning catalog and authenticated panel tracker (v17)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.templates import templates
from app.models.learning import STATUS_LABELS
from app.services import learning as learning_service
from app.services.roadmap_data import LEVEL_BY_SLUG

router = APIRouter()


def _require_user(request: Request, next_path: str):
    user = get_current_user(request)
    if user is None:
        request.session["next"] = next_path
        return None
    return user


def _level_or_404(level_slug: str):
    if not learning_service.is_enrollable(level_slug):
        raise HTTPException(status_code=404)
    return LEVEL_BY_SLUG[level_slug]


@router.get("/dashboard/learning/", name="learning_index")
async def learning_index(request: Request, db: AsyncSession = Depends(get_db)):
    user = _require_user(request, "/dashboard/learning/")
    if user is None:
        return RedirectResponse(url="/login/?next=/dashboard/learning/", status_code=303)
    cards = await learning_service.get_active_enrollments(db, user.id)
    return templates.TemplateResponse(
        request,
        "pages/learning_index.html",
        {
            "page_title": "مسیرهای من",
            "current_user": user,
            "cards": cards,
        },
    )


@router.get("/dashboard/learning/{level_slug}/", name="learning_catalog")
async def learning_catalog(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
):
    lv = _level_or_404(level_slug)
    user = get_current_user(request)
    enrollment = None
    if user:
        enrollment = await learning_service.get_enrollment(db, user.id, level_slug)
    resources = await learning_service.list_resources_with_status(db, level_slug, None)
    groups = learning_service.group_resources(resources)
    counts = await learning_service.level_social_counts(db, level_slug)
    return templates.TemplateResponse(
        request,
        "pages/learning_catalog.html",
        {
            "page_title": f"یادگیری — {lv.fa}",
            "level": lv,
            "level_slug": level_slug,
            "groups": groups,
            "enrolled": enrollment is not None,
            "social": counts,
        },
    )


@router.get("/dashboard/learning/{level_slug}/track/", name="learning_track")
async def learning_track(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
):
    lv = _level_or_404(level_slug)
    user = _require_user(request, f"/dashboard/learning/{level_slug}/track/")
    if user is None:
        return RedirectResponse(
            url=f"/login/?next=/dashboard/learning/{level_slug}/track/",
            status_code=303,
        )
    enrollment = await learning_service.get_enrollment(db, user.id, level_slug)
    if enrollment is None:
        return RedirectResponse(
            url=f"/dashboard/learning/{level_slug}/", status_code=303
        )
    resources = await learning_service.list_resources_with_status(
        db, level_slug, enrollment
    )
    groups = learning_service.group_resources(resources)
    progress = await learning_service.compute_progress(db, enrollment)
    studying = next((r for r in resources if getattr(r, "_status", "") == "STUDYING"), None)
    studying_count = sum(1 for r in resources if getattr(r, "_status", "") == "STUDYING")
    return templates.TemplateResponse(
        request,
        "pages/learning_track.html",
        {
            "page_title": f"پیگیری — {lv.fa}",
            "current_user": user,
            "level": lv,
            "level_slug": level_slug,
            "groups": groups,
            "progress": progress,
            "enrollment": enrollment,
            "studying": studying,
            "multi_studying": studying_count > 1,
            "status_labels": STATUS_LABELS,
        },
    )


async def _enroll_and_redirect(db: AsyncSession, user_id: int, level_slug: str):
    _level_or_404(level_slug)
    await learning_service.get_or_create_enrollment(db, user_id, level_slug)
    return RedirectResponse(
        url=f"/dashboard/learning/{level_slug}/track/", status_code=303
    )


@router.get("/dashboard/learning/{level_slug}/enroll/", name="learning_enroll_get")
async def learning_enroll_get(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
):
    user = _require_user(request, f"/dashboard/learning/{level_slug}/enroll/")
    if user is None:
        return RedirectResponse(
            url=f"/login/?next=/dashboard/learning/{level_slug}/enroll/",
            status_code=303,
        )
    return await _enroll_and_redirect(db, user.id, level_slug)


@router.post("/dashboard/learning/{level_slug}/enroll/", name="learning_enroll_post")
async def learning_enroll_post(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
):
    user = _require_user(request, f"/dashboard/learning/{level_slug}/enroll/")
    if user is None:
        return RedirectResponse(
            url=f"/login/?next=/dashboard/learning/{level_slug}/enroll/",
            status_code=303,
        )
    return await _enroll_and_redirect(db, user.id, level_slug)


@router.post("/dashboard/learning/{level_slug}/unenroll/", name="learning_unenroll")
async def learning_unenroll(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
):
    _level_or_404(level_slug)
    user = _require_user(request, f"/dashboard/learning/{level_slug}/track/")
    if user is None:
        return RedirectResponse(url="/login/", status_code=303)
    ok = await learning_service.unenroll(db, user.id, level_slug)
    if not ok:
        return RedirectResponse(
            url=f"/dashboard/learning/{level_slug}/", status_code=303
        )
    return RedirectResponse(url="/dashboard/learning/", status_code=303)


@router.post("/dashboard/learning/{level_slug}/progress/", name="learning_progress")
async def learning_progress(
    request: Request,
    level_slug: str,
    db: AsyncSession = Depends(get_db),
    resource_id: int = Form(...),
    status: str = Form(""),
):
    _level_or_404(level_slug)
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login/", status_code=303)
    enrollment = await learning_service.get_enrollment(db, user.id, level_slug)
    if enrollment is None:
        return RedirectResponse(
            url=f"/dashboard/learning/{level_slug}/", status_code=303
        )
    try:
        await learning_service.set_resource_status(
            db, enrollment.id, resource_id, status
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="وضعیت نامعتبر است")
    return RedirectResponse(
        url=f"/dashboard/learning/{level_slug}/track/", status_code=303
    )
