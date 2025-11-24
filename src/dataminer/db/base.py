"""SQLAlchemy database base configuration."""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from dataminer.core.config import get_settings

# Define naming conventions for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""

    metadata = metadata


def get_engine() -> AsyncEngine:
    """Create and return async database engine."""
    settings = get_settings()
    return create_async_engine(
        str(settings.database_url).replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    """Create and return async session maker."""
    return async_sessionmaker(engine, expire_on_commit=False)


# For Alembic migrations (synchronous)
def get_sync_engine_url() -> str:
    """Get synchronous database URL for Alembic."""
    settings = get_settings()
    return str(settings.database_url)
