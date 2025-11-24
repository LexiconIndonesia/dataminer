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

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dataminer.db.base import get_engine

# Create global session maker
engine = get_engine()
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
        finally:
            await session.close()
