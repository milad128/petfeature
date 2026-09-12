"""REST API v1 — for future SPA, mobile, or integrations."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services import learning as learning_service

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


class ProgressUpdate(BaseModel):
    resource_id: int
    status: str = ""


class RatingUpdate(BaseModel):
    resource_id: int
    stars: int


@router.post("/learning/{level_slug}/progress/")
async def api_learning_progress(
    request: Request,
    level_slug: str,
    payload: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="login_required")
    if not learning_service.is_enrollable(level_slug):
        raise HTTPException(status_code=404)
    enrollment = await learning_service.get_enrollment(db, user.id, level_slug)
    if enrollment is None:
        raise HTTPException(status_code=403, detail="not_enrolled")
    try:
        update = await learning_service.set_resource_status(
            db, enrollment.id, payload.resource_id, payload.status
        )
    except ValueError as exc:
        code = str(exc)
        if code == "bad_resource":
            raise HTTPException(status_code=404, detail="bad_resource")
        raise HTTPException(status_code=400, detail="invalid_status")
    progress = await learning_service.compute_progress(db, enrollment)
    return {
        "ok": True,
        "progress": progress.as_dict(),
        "prompt_rating": update.prompt_rating,
        "resource_id": payload.resource_id,
    }


@router.post("/learning/{level_slug}/rate/")
async def api_learning_rate(
    request: Request,
    level_slug: str,
    payload: RatingUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="login_required")
    if not learning_service.is_enrollable(level_slug):
        raise HTTPException(status_code=404)
    try:
        row = await learning_service.upsert_resource_rating(
            db, user.id, level_slug, payload.resource_id, payload.stars
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_enrolled":
            raise HTTPException(status_code=403, detail="not_enrolled")
        if code == "bad_resource":
            raise HTTPException(status_code=404, detail="bad_resource")
        raise HTTPException(status_code=422, detail="invalid_stars")
    return {"ok": True, "stars": row.stars}
