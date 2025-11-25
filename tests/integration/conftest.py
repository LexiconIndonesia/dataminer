"""Integration test configuration - requires database and external services."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest
import sqlparse
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dataminer.api.app import create_app
from dataminer.core.config import Settings, get_settings
from dataminer.db.session import get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings using values from get_settings()."""
    settings = get_settings()
    # Use test database URL converted to sync format for Settings
    sync_database_url = settings.test_database_url.replace("+asyncpg", "")
    return Settings(
        environment="development",
        debug=True,
        log_level="DEBUG",
        database_url=sync_database_url,
        redis_url=str(settings.redis_url),
    )


@pytest.fixture
def app(test_settings: Settings) -> Any:
    """Create FastAPI app for testing."""
    return create_app(test_settings)


@pytest.fixture
def client(app: Any) -> Generator[TestClient]:
    """Create synchronous test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client(app: Any) -> AsyncGenerator[AsyncClient]:
    """Create async test client (without db override).

    Use this for tests that don't need database access.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine and set up schema."""
    settings = get_settings()
    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    # Set up database schema
    schema_path = Path(__file__).parent.parent.parent / "sql" / "schema" / "current_schema.sql"

    async with engine.begin() as conn:
        # Drop all tables first for clean slate
        await conn.execute(
            text("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
        )

        # Read and execute schema file
        if schema_path.exists():
            schema_sql = schema_path.read_text()
            statements = sqlparse.split(schema_sql)

            for statement in statements:
                statement = statement.strip()
                if statement:
                    parsed = sqlparse.parse(statement)
                    if parsed and not all(
                        token.ttype
                        in (
                            sqlparse.tokens.Comment.Single,
                            sqlparse.tokens.Comment.Multiline,
                            sqlparse.tokens.Whitespace,
                            sqlparse.tokens.Newline,
                        )
                        for stmt in parsed
                        for token in stmt.flatten()
                    ):
                        await conn.execute(text(statement))

        # Reset search_path to include public schema (schema file sets it to empty)
        await conn.execute(text("SET search_path TO public"))

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    """Create test database session."""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client_with_db(test_settings: Settings, db_engine) -> AsyncGenerator[AsyncClient]:
    """Create async test client with database session override.

    This fixture ensures the app uses the same database engine as the tests.
    """
    app = create_app(test_settings)

    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_source(async_client_with_db: AsyncClient) -> dict[str, Any]:
    """Create a test document source via API."""
    response = await async_client_with_db.post(
        "/v1/dataminer/sources",
        json={
            "source_id": "TEST_SC",
            "source_name": "Test Supreme Court",
            "country_code": "TST",
            "primary_language": "en",
            "legal_system": "common_law",
            "document_type": "test_judgment",
            "is_active": True,
            "phase": 1,
        },
    )
    if response.status_code != 201:
        raise RuntimeError(f"Failed to create test source: {response.text}")
    return response.json()
