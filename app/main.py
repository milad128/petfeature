"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin.routes import router as admin_router
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.web.routes import router as web_router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.uploads import ensure_upload_dirs

    ensure_upload_dirs()
    if settings.database_url.startswith("sqlite"):
        from app.core.sqlite_migrations import migrate_books_schema
        from app.core.database import Base, engine
        from app.models import (  # noqa: F401
            AboutPage,
            Book,
            BookMediaLink,
            Category,
            Post,
            PostComment,
            PostRating,
            Tool,
            ToolFile,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(migrate_books_schema)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(web_router)
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(api_v1_router, prefix="/api/v1", tags=["api"])
