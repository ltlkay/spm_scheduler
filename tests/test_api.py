import os
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import get_db
from app.base import Base

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/spm_db_test",
)

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL)
    yield engine
    await engine.dispose()

@pytest.fixture(autouse=True)
async def setup_db(test_engine):
    async with test_engine.begin() as conn:
        from app import models
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.tasks.run_scan")
async def test_create_job_returns_id(mock_run_scan):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/jobs", json={"parameters": {"scan_size_um": 5.0}})
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
    assert "id" in resp.json()

@pytest.mark.asyncio
@patch("app.tasks.run_scan")
async def test_get_unknown_job_returns_404(mock_run_scan):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/jobs/99999")
    assert resp.status_code == 404