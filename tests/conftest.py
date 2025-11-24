"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dataminer.api.app import create_app
from dataminer.core.config import Settings
from dataminer.db.base import Base
from dataminer.db.models.configuration import DocumentSource


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="development",
        debug=True,
        log_level="DEBUG",
        database_url="postgresql://dataminer:password@localhost:5432/dataminer_test",
        redis_url="redis://localhost:6379/1",  # Use different DB for tests
    )


@pytest.fixture
def app(test_settings: Settings) -> Any:
    """Create FastAPI app for testing."""
    return create_app(test_settings)


@pytest.fixture
def client(app: Any) -> Generator[TestClient]:
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client(app: Any) -> AsyncGenerator[AsyncClient]:
    """Create async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    # Use test database
    engine = create_async_engine(
        "postgresql+asyncpg://dataminer:password@localhost:5432/dataminer",
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    """Create test database session."""
    SessionLocal = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with SessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_source(db_session: AsyncSession) -> DocumentSource:
    """Create a test document source."""
    source = DocumentSource(
        source_id="TEST_SC",
        source_name="Test Supreme Court",
        country_code="TST",
        primary_language="en",
        legal_system="common_law",
        document_type="test_judgment",
        is_active=True,
        phase=1,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source
