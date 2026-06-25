"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.routes import router as admin_router
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.web.routes import router as web_router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init / migrations run separately via Alembic on deploy.
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(web_router)
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(api_v1_router, prefix="/api/v1", tags=["api"])
