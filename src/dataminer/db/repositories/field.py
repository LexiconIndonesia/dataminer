"""Field repository for database operations using SQLC queries."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.db.queries import fields

if TYPE_CHECKING:
    from dataminer.db.queries.models import SourceFieldDefinition


class FieldRepository:
    """Repository for field-related database operations using SQLC."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def get_fields_by_source(
        self,
        source_id: str,
        *,
        field_category: str | None = None,
        field_type: str | None = None,
        is_required: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SourceFieldDefinition]:
        """Get all field definitions for a source with optional filtering and pagination."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        return [
            field
            async for field in querier.list_fields_by_source_filtered(
                source_id=source_id,
                field_category=field_category,
                field_type=field_type,
                is_required=is_required,
                limit_val=limit,
                offset_val=offset,
            )
        ]

    async def count_fields_by_source(
        self,
        source_id: str,
        *,
        field_category: str | None = None,
        field_type: str | None = None,
        is_required: bool | None = None,
    ) -> int:
        """Count field definitions for a source with optional filtering."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        result = await querier.count_fields_by_source_filtered(
            source_id=source_id,
            field_category=field_category,
            field_type=field_type,
            is_required=is_required,
        )
        return result or 0

    async def get_field_by_id(self, field_id: UUID) -> SourceFieldDefinition | None:
        """Get field definition by ID."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        return await querier.get_field_by_id(field_id=field_id)

    async def get_field_source_id(self, field_id: UUID) -> str | None:
        """Get source_id for a field."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        return await querier.get_field_source_id(field_id=field_id)

    async def create_field(
        self,
        source_id: str,
        field_name: str,
        field_display_name: str | None = None,
        field_category: str | None = None,
        field_type: str | None = None,
        extraction_method: str | None = None,
        extraction_section: str | None = None,
        regex_pattern: str | None = None,
        llm_prompt_template_id: UUID | None = None,
        is_required: bool | None = None,
        validation_rules: Any | None = None,
        confidence_threshold: Decimal | None = None,
        normalization_rules: Any | None = None,
        display_order: int | None = None,
    ) -> SourceFieldDefinition | None:
        """Create a new field definition."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        params = fields.CreateFieldParams(
            source_id=source_id,
            field_name=field_name,
            field_display_name=field_display_name,
            field_category=field_category,
            field_type=field_type,
            extraction_method=extraction_method,
            extraction_section=extraction_section,
            regex_pattern=regex_pattern,
            llm_prompt_template_id=llm_prompt_template_id,
            is_required=is_required,
            validation_rules=validation_rules,
            confidence_threshold=confidence_threshold,
            normalization_rules=normalization_rules,
            display_order=display_order,
        )
        return await querier.create_field(arg=params)

    async def update_field(
        self,
        field_id: UUID,
        field_name: str | None = None,
        field_display_name: str | None = None,
        field_category: str | None = None,
        field_type: str | None = None,
        extraction_method: str | None = None,
        extraction_section: str | None = None,
        regex_pattern: str | None = None,
        llm_prompt_template_id: UUID | None = None,
        is_required: bool | None = None,
        validation_rules: Any | None = None,
        confidence_threshold: Decimal | None = None,
        normalization_rules: Any | None = None,
        display_order: int | None = None,
    ) -> SourceFieldDefinition | None:
        """Update field definition."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        params = fields.UpdateFieldParams(
            field_id=field_id,
            field_name=field_name,
            field_display_name=field_display_name,
            field_category=field_category,
            field_type=field_type,
            extraction_method=extraction_method,
            extraction_section=extraction_section,
            regex_pattern=regex_pattern,
            llm_prompt_template_id=llm_prompt_template_id,
            is_required=is_required,
            validation_rules=validation_rules,
            confidence_threshold=confidence_threshold,
            normalization_rules=normalization_rules,
            display_order=display_order,
        )
        return await querier.update_field(arg=params)

    async def delete_field(self, field_id: UUID) -> None:
        """Delete field definition."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        await querier.delete_field(field_id=field_id)

    async def check_duplicate_field_name(self, source_id: str, field_name: str) -> bool:
        """Check if field name already exists for source."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        result = await querier.check_duplicate_field_name(
            source_id=source_id, field_name=field_name
        )
        return bool(result)

    async def check_duplicate_field_name_excluding(
        self, source_id: str, field_name: str, exclude_field_id: UUID
    ) -> bool:
        """Check if field name already exists for source, excluding a specific field."""
        conn = await self.session.connection()
        querier = fields.AsyncQuerier(conn)
        result = await querier.check_duplicate_field_name_excluding(
            source_id=source_id, field_name=field_name, field_id=exclude_field_id
        )
        return bool(result)
