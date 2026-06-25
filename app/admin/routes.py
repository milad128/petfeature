"""Admin CMS routes — content management for books and about page."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def admin_dashboard():
    """Placeholder: admin login + dashboard will be implemented here."""
    return {"message": "Admin CMS — coming soon"}
