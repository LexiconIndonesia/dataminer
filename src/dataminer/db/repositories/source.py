"""Source repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dataminer.db.models.configuration import (
    DocumentSource,
    SourceExtractionProfile,
)


class SourceRepository:
    """Repository for source-related database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def get_all_sources(self) -> list[DocumentSource]:
        """Get all document sources."""
        stmt = select(DocumentSource).order_by(DocumentSource.source_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_source_by_id(self, source_id: str) -> DocumentSource | None:
        """Get document source by ID."""
        stmt = (
            select(DocumentSource)
            .options(
                selectinload(DocumentSource.extraction_profiles),
                selectinload(DocumentSource.field_definitions),
            )
            .where(DocumentSource.source_id == source_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_source(self, source: DocumentSource) -> DocumentSource:
        """Create a new document source."""
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def update_source(self, source_id: str, update_data: dict) -> DocumentSource | None:
        """Update document source configuration."""
        source = await self.get_source_by_id(source_id)
        if not source:
            return None

        for key, value in update_data.items():
            if hasattr(source, key) and value is not None:
                setattr(source, key, value)

        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def get_profiles_by_source(self, source_id: str) -> list[SourceExtractionProfile]:
        """Get all extraction profiles for a source."""
        stmt = (
            select(SourceExtractionProfile)
            .where(SourceExtractionProfile.source_id == source_id)
            .order_by(SourceExtractionProfile.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_profile(self, profile: SourceExtractionProfile) -> SourceExtractionProfile:
        """Create a new extraction profile."""
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def get_profile_by_id(self, profile_id: UUID) -> SourceExtractionProfile | None:
        """Get extraction profile by ID."""
        stmt = select(SourceExtractionProfile).where(
            SourceExtractionProfile.profile_id == profile_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_duplicate_profile_name(self, source_id: str, profile_name: str) -> bool:
        """Check if profile name already exists for source."""
        stmt = select(SourceExtractionProfile).where(
            SourceExtractionProfile.source_id == source_id,
            SourceExtractionProfile.profile_name == profile_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
