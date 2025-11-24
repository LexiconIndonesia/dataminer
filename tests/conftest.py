"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import sqlparse
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dataminer.api.app import create_app
from dataminer.core.config import Settings
from dataminer.db.repositories.source import SourceRepository

if TYPE_CHECKING:
    from dataminer.db.queries.models import DocumentSource


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

    # Create tables from SQL schema file
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    if schema_path.exists():
        async with engine.begin() as conn:
            schema_sql = schema_path.read_text()

            # Use sqlparse for robust SQL statement splitting
            # This properly handles semicolons in strings, comments, and function bodies
            statements = sqlparse.split(schema_sql)

            for statement in statements:
                # Strip whitespace and skip empty statements
                statement = statement.strip()
                if statement:
                    # Skip comment-only statements
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

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
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
    """Create a test document source using repository."""
    repo = SourceRepository(db_session)
    source = await repo.create_source(
        source_id="TEST_SC",
        source_name="Test Supreme Court",
        country_code="TST",
        primary_language="en",
        legal_system="common_law",
        document_type="test_judgment",
        is_active=True,
        phase=1,
    )
    await db_session.commit()
    if source is None:
        raise RuntimeError("Failed to create test source")
    return source
