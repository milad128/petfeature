"""Shared pytest fixtures for the petfeature test suite.

Tests run entirely against a throwaway SQLite database (no Postgres needed),
which the app already supports (`app/core/database.py` handles a `sqlite` URL).

Key mechanics:
  * Env vars are set BEFORE importing the app so config (secret key, admin
    credentials, DB URL) is deterministic.
  * The module-level `engine` / `async_session_factory` in `app.core.database`
    are rebuilt with a NullPool SQLite engine and monkey-patched in place. Every
    DB access path — the `get_db` dependency AND the analytics/auth middleware,
    which import `async_session_factory` at call time — therefore hits the test
    DB. NullPool opens a fresh connection per operation, which sidesteps
    aiosqlite "attached to a different loop" errors across pytest-asyncio's
    per-test event loops.
"""

from __future__ import annotations

import os

# ── Environment must be configured before the app is imported ───────────────
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-pass")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./.pytest_petfeature.db")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.core.database as database
import app.models  # noqa: F401  — registers every ORM table on Base.metadata
from app.core.database import Base

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# Rebuild the engine/session factory with NullPool and patch the module globals
# so all code paths use the test database.
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)
TestSessionFactory = async_sessionmaker(test_engine, expire_on_commit=False)

database.engine = test_engine
database.async_session_factory = TestSessionFactory

# Import the app AFTER the environment + DB patch are in place.
from app.main import app  # noqa: E402

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]


@pytest_asyncio.fixture(autouse=True)
async def _fresh_schema():
    """Give every test a clean schema (create before, drop after)."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """A raw AsyncSession for testing service-layer functions directly."""
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """An in-process HTTP client that exercises the real middleware stack."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def admin_client(client):
    """A client with an authenticated admin session cookie."""
    resp = await client.post(
        "/admin/login/",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        follow_redirects=False,
    )
    assert resp.status_code == 303, "admin login should redirect on success"
    return client
