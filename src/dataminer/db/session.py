"""Database session management.

Session Management Strategy:
- Auto-commit on success: All changes made during a request are automatically
  committed when the request completes successfully.
- Auto-rollback on error: If any exception occurs, all changes are rolled back.
- This pattern works well for CRUD operations where each endpoint represents
  a single transaction.
- For more complex multi-step transactions, consider using explicit session
  management within the endpoint logic.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dataminer.core.config import get_settings

# Create global engine and session maker
settings = get_settings()
engine = create_async_engine(
    str(settings.database_url).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get database session dependency for FastAPI.

    Auto-commit strategy:
    - Commits on successful request completion
    - Rolls back on any exception
    - Ensures data consistency per request

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Changes are auto-committed on success
            item = await db.get(Item, 1)
            item.name = "Updated"
            # No need to call db.commit() explicitly
            return item
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
