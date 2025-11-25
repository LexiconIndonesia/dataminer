"""Field management API endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import RootModel
from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.api.generated.models import (
    FieldDefinitionCreate,
    FieldDefinitionListResponse,
    FieldDefinitionResponse,
    FieldDefinitionUpdate,
)
from dataminer.db.repositories.field import FieldRepository
from dataminer.db.repositories.source import SourceRepository
from dataminer.db.session import get_db

router = APIRouter()


def _extract_root_value(value: Any) -> Any:
    """Extract the root value from a RootModel, or return as-is."""
    if isinstance(value, RootModel):
        return value.root
    return value


def _make_timezone_aware(dt: datetime | None) -> datetime | None:
    """Convert naive datetime to UTC timezone-aware datetime."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _prepare_field_for_response(field: Any) -> dict[str, Any]:
    """Prepare a field dataclass for Pydantic model validation.

    Converts naive datetimes to timezone-aware datetimes.
    """
    # Convert dataclass to dict-like access
    data = {
        "field_id": field.field_id,
        "source_id": field.source_id,
        "field_name": field.field_name,
        "field_display_name": field.field_display_name,
        "field_category": field.field_category,
        "field_type": field.field_type,
        "extraction_method": field.extraction_method,
        "extraction_section": field.extraction_section,
        "regex_pattern": field.regex_pattern,
        "llm_prompt_template_id": field.llm_prompt_template_id,
        "is_required": field.is_required,
        "validation_rules": field.validation_rules,
        "confidence_threshold": field.confidence_threshold,
        "normalization_rules": field.normalization_rules,
        "display_order": field.display_order,
        "created_at": _make_timezone_aware(field.created_at),
        "updated_at": _make_timezone_aware(field.updated_at),
    }
    return data


@router.get(
    "/sources/{source_id}/fields",
    response_model=FieldDefinitionListResponse,
    summary="List field definitions",
    description="Get all field definitions for a specific source with optional filtering",
    responses={
        404: {"description": "Source not found"},
    },
)
async def list_fields(
    source_id: str,
    category: Annotated[str | None, Query(description="Filter by field category")] = None,
    field_type: Annotated[str | None, Query(description="Filter by field type")] = None,
    is_required: Annotated[bool | None, Query(description="Filter by required status")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of results")] = 50,
    offset: Annotated[int, Query(ge=0, description="Number of results to skip")] = 0,
    db: AsyncSession = Depends(get_db),
) -> FieldDefinitionListResponse:
    """List field definitions for a source with optional filtering and pagination."""
    source_repo = SourceRepository(db)
    field_repo = FieldRepository(db)

    # Check if source exists
    source = await source_repo.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    # Get fields with filtering and pagination
    fields_list = await field_repo.get_fields_by_source(
        source_id=source_id,
        field_category=category,
        field_type=field_type,
        is_required=is_required,
        limit=limit,
        offset=offset,
    )

    # Get total count
    total = await field_repo.count_fields_by_source(
        source_id=source_id,
        field_category=category,
        field_type=field_type,
        is_required=is_required,
    )

    # Convert SQLC dataclasses to Pydantic models with timezone-aware datetimes
    items = [
        FieldDefinitionResponse.model_validate(_prepare_field_for_response(field))
        for field in fields_list
    ]

    return FieldDefinitionListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/sources/{source_id}/fields",
    response_model=FieldDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create field definition",
    description="Create a new field definition for a document source",
    responses={
        404: {"description": "Source not found"},
        409: {"description": "Field with same name already exists"},
    },
)
async def create_field(
    source_id: str,
    field_data: FieldDefinitionCreate,
    db: AsyncSession = Depends(get_db),
) -> FieldDefinitionResponse:
    """Create a new field definition for a source."""
    source_repo = SourceRepository(db)
    field_repo = FieldRepository(db)

    # Check if source exists
    source = await source_repo.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    # Check for duplicate field name
    if await field_repo.check_duplicate_field_name(source_id, field_data.field_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Field with name '{field_data.field_name}' already exists for source '{source_id}'",
        )

    # Extract values from RootModels and prepare parameters
    confidence_threshold = _extract_root_value(field_data.confidence_threshold)
    if confidence_threshold is not None:
        confidence_threshold = Decimal(str(confidence_threshold))

    created_field = await field_repo.create_field(
        source_id=source_id,
        field_name=field_data.field_name,
        field_display_name=_extract_root_value(field_data.field_display_name),
        field_category=_extract_root_value(field_data.field_category),
        field_type=_extract_root_value(field_data.field_type),
        extraction_method=_extract_root_value(field_data.extraction_method),
        extraction_section=_extract_root_value(field_data.extraction_section),
        regex_pattern=_extract_root_value(field_data.regex_pattern),
        llm_prompt_template_id=_extract_root_value(field_data.llm_prompt_template_id),
        is_required=_extract_root_value(field_data.is_required),
        validation_rules=_extract_root_value(field_data.validation_rules),
        confidence_threshold=confidence_threshold,
        normalization_rules=_extract_root_value(field_data.normalization_rules),
        display_order=_extract_root_value(field_data.display_order),
    )

    if not created_field:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create field",
        )

    # Convert DB model to API response type with timezone-aware datetimes
    return FieldDefinitionResponse.model_validate(_prepare_field_for_response(created_field))


@router.get(
    "/fields/{field_id}",
    response_model=FieldDefinitionResponse,
    summary="Get field details",
    description="Get detailed information about a specific field definition",
    responses={
        404: {"description": "Field not found"},
    },
)
async def get_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
) -> FieldDefinitionResponse:
    """Get field definition by ID."""
    from uuid import UUID

    field_repo = FieldRepository(db)

    try:
        parsed_field_id = UUID(field_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: '{field_id}'",
        ) from None

    field = await field_repo.get_field_by_id(parsed_field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID '{field_id}' not found",
        )

    # Convert DB model to API response type with timezone-aware datetimes
    return FieldDefinitionResponse.model_validate(_prepare_field_for_response(field))


@router.put(
    "/fields/{field_id}",
    response_model=FieldDefinitionResponse,
    summary="Update field definition",
    description="Update an existing field definition",
    responses={
        404: {"description": "Field not found"},
        409: {"description": "Field with same name already exists"},
    },
)
async def update_field(
    field_id: str,
    update_data: FieldDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
) -> FieldDefinitionResponse:
    """Update field definition."""
    from uuid import UUID

    field_repo = FieldRepository(db)

    try:
        parsed_field_id = UUID(field_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: '{field_id}'",
        ) from None

    # Check if field exists
    existing_field = await field_repo.get_field_by_id(parsed_field_id)
    if not existing_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID '{field_id}' not found",
        )

    # Get field_name from update_data
    field_name = _extract_root_value(update_data.field_name)

    # Check for duplicate field name if updating field_name
    if (
        field_name is not None
        and field_name != existing_field.field_name
        and await field_repo.check_duplicate_field_name_excluding(
            existing_field.source_id, field_name, parsed_field_id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Field with name '{field_name}' already exists for source '{existing_field.source_id}'",
        )

    # Extract values from RootModels and prepare parameters
    confidence_threshold = _extract_root_value(update_data.confidence_threshold)
    if confidence_threshold is not None:
        confidence_threshold = Decimal(str(confidence_threshold))

    updated_field = await field_repo.update_field(
        field_id=parsed_field_id,
        field_name=field_name,
        field_display_name=_extract_root_value(update_data.field_display_name),
        field_category=_extract_root_value(update_data.field_category),
        field_type=_extract_root_value(update_data.field_type),
        extraction_method=_extract_root_value(update_data.extraction_method),
        extraction_section=_extract_root_value(update_data.extraction_section),
        regex_pattern=_extract_root_value(update_data.regex_pattern),
        llm_prompt_template_id=_extract_root_value(update_data.llm_prompt_template_id),
        is_required=_extract_root_value(update_data.is_required),
        validation_rules=_extract_root_value(update_data.validation_rules),
        confidence_threshold=confidence_threshold,
        normalization_rules=_extract_root_value(update_data.normalization_rules),
        display_order=_extract_root_value(update_data.display_order),
    )

    if not updated_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID '{field_id}' not found",
        )

    # Convert DB model to API response type with timezone-aware datetimes
    return FieldDefinitionResponse.model_validate(_prepare_field_for_response(updated_field))


@router.delete(
    "/fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete field definition",
    description="Delete a field definition",
    responses={
        404: {"description": "Field not found"},
    },
)
async def delete_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete field definition."""
    from uuid import UUID

    field_repo = FieldRepository(db)

    try:
        parsed_field_id = UUID(field_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: '{field_id}'",
        ) from None

    # Check if field exists
    existing_field = await field_repo.get_field_by_id(parsed_field_id)
    if not existing_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field with ID '{field_id}' not found",
        )

    await field_repo.delete_field(parsed_field_id)
