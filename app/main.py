"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin.routes import router as admin_router, _inject_comment_badges
from app.api.v1.router import router as api_v1_router
from app.core.analytics import AnalyticsMiddleware
from app.core.auth import UserAuthMiddleware
from app.core.config import settings
from app.web.auth_routes import router as auth_router
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
            ContactMessage,
            PageView,
            Post,
            PostComment,
            PostRating,
            Tool,
            ToolFile,
            User,
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

# Middleware stack — add_middleware wraps in reverse: last added = outermost.
# Desired request flow: Analytics → Session → UserAuth → App
# So add order: UserAuth first (innermost), then Session, then Analytics.
app.add_middleware(UserAuthMiddleware)                                    # innermost: reads session → sets request.state.current_user
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="lax",
    https_only=not settings.debug,
)
app.add_middleware(AnalyticsMiddleware)                                   # outermost: logs page views

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth_router)
app.include_router(web_router)
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(_inject_comment_badges)],
)
app.include_router(api_v1_router, prefix="/api/v1", tags=["api"])
