"""Source repository for database operations using SQLC queries."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.db.queries import profiles, sources

if TYPE_CHECKING:
    from dataminer.db.queries.models import DocumentSource, SourceExtractionProfile


class SourceRepository:
    """Repository for source-related database operations using SQLC."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def get_all_sources(self) -> list[DocumentSource]:
        """Get all document sources."""
        conn = await self.session.connection()
        querier = sources.AsyncQuerier(conn)
        # Convert AsyncIterator to list
        return [source async for source in querier.list_sources()]

    async def get_source_by_id(self, source_id: str) -> DocumentSource | None:
        """Get document source by ID."""
        conn = await self.session.connection()
        querier = sources.AsyncQuerier(conn)
        return await querier.get_source_by_id(source_id=source_id)

    async def create_source(
        self,
        source_id: str,
        source_name: str,
        country_code: str | None = None,
        primary_language: str | None = None,
        secondary_languages: list[str] | None = None,
        legal_system: str | None = None,
        document_type: str | None = None,
        is_active: bool | None = None,
        phase: int | None = None,
    ) -> DocumentSource | None:
        """Create a new document source."""
        conn = await self.session.connection()
        querier = sources.AsyncQuerier(conn)
        return await querier.create_source(
            source_id=source_id,
            source_name=source_name,
            country_code=country_code,
            primary_language=primary_language,
            secondary_languages=secondary_languages,
            legal_system=legal_system,
            document_type=document_type,
            is_active=is_active,
            phase=phase,
        )

    async def update_source(
        self,
        source_id: str,
        source_name: str | None = None,
        is_active: bool | None = None,
        phase: int | None = None,
        avg_accuracy: Decimal | None = None,
        avg_cost_per_document: Decimal | None = None,
    ) -> DocumentSource | None:
        """Update document source configuration."""
        conn = await self.session.connection()
        querier = sources.AsyncQuerier(conn)
        return await querier.update_source(
            source_id=source_id,
            source_name=source_name,
            is_active=is_active,
            phase=phase,
            avg_accuracy=avg_accuracy,
            avg_cost_per_document=avg_cost_per_document,
        )

    async def get_profiles_by_source(self, source_id: str) -> list[SourceExtractionProfile]:
        """Get all extraction profiles for a source."""
        conn = await self.session.connection()
        querier = profiles.AsyncQuerier(conn)
        # Convert AsyncIterator to list
        return [profile async for profile in querier.list_profiles_by_source(source_id=source_id)]

    async def create_profile(
        self,
        source_id: str,
        profile_name: str,
        is_active: bool | None = None,
        is_default: bool | None = None,
        pdf_extraction_method: str | None = None,
        ocr_threshold: Decimal | None = None,
        ocr_language: str | None = None,
        use_document_ai_fallback: bool | None = None,
        segmentation_method: str | None = None,
        segment_size_tokens: int | None = None,
        segment_overlap_tokens: int | None = None,
        llm_model_quick: str | None = None,
        llm_model_detailed: str | None = None,
        llm_temperature: Decimal | None = None,
        max_retries: int | None = None,
        max_cost_per_document: Decimal | None = None,
        enable_deep_dive_pass: bool | None = None,
        deep_dive_confidence_threshold: Decimal | None = None,
    ) -> SourceExtractionProfile | None:
        """Create a new extraction profile."""
        conn = await self.session.connection()
        querier = profiles.AsyncQuerier(conn)
        params = profiles.CreateProfileParams(
            source_id=source_id,
            profile_name=profile_name,
            is_active=is_active,
            is_default=is_default,
            pdf_extraction_method=pdf_extraction_method,
            ocr_threshold=ocr_threshold,
            ocr_language=ocr_language,
            use_document_ai_fallback=use_document_ai_fallback,
            segmentation_method=segmentation_method,
            segment_size_tokens=segment_size_tokens,
            segment_overlap_tokens=segment_overlap_tokens,
            llm_model_quick=llm_model_quick,
            llm_model_detailed=llm_model_detailed,
            llm_temperature=llm_temperature,
            max_retries=max_retries,
            max_cost_per_document=max_cost_per_document,
            enable_deep_dive_pass=enable_deep_dive_pass,
            deep_dive_confidence_threshold=deep_dive_confidence_threshold,
        )
        return await querier.create_profile(arg=params)

    async def get_profile_by_id(self, profile_id: UUID) -> SourceExtractionProfile | None:
        """Get extraction profile by ID."""
        conn = await self.session.connection()
        querier = profiles.AsyncQuerier(conn)
        return await querier.get_profile_by_id(profile_id=profile_id)

    async def check_duplicate_profile_name(self, source_id: str, profile_name: str) -> bool:
        """Check if profile name already exists for source."""
        conn = await self.session.connection()
        querier = profiles.AsyncQuerier(conn)
        result = await querier.check_duplicate_profile_name(
            source_id=source_id, profile_name=profile_name
        )
        return bool(result)
