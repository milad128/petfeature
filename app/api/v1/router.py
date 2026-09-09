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
        await learning_service.set_resource_status(
            db, enrollment.id, payload.resource_id, payload.status
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_status")
    progress = await learning_service.compute_progress(db, enrollment)
    return {"ok": True, "progress": progress.as_dict()}
