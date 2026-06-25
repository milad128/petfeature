"""REST API v1 — for future SPA, mobile, or integrations."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}
