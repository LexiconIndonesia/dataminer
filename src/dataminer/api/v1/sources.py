"""Source management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.api.generated import (
    DocumentSourceResponse,
    DocumentSourceUpdate,
    ExtractionProfileCreate,
    ExtractionProfileResponse,
)
from dataminer.db.models.configuration import (
    DocumentSource,
    SourceExtractionProfile,
)
from dataminer.db.repositories.source import SourceRepository
from dataminer.db.session import get_db

router = APIRouter()


@router.get(
    "/sources",
    response_model=list[DocumentSourceResponse],
    summary="List all document sources",
    description="Get a list of all configured document sources",
)
async def list_sources(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentSource]:
    """List all document sources."""
    repo = SourceRepository(db)
    sources = await repo.get_all_sources()
    return sources


@router.get(
    "/sources/{source_id}",
    response_model=DocumentSourceResponse,
    summary="Get source details",
    description="Get detailed information about a specific document source",
    responses={
        404: {"description": "Source not found"},
    },
)
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentSource:
    """Get document source by ID."""
    repo = SourceRepository(db)
    source = await repo.get_source_by_id(source_id)

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    return source


@router.put(
    "/sources/{source_id}/config",
    response_model=DocumentSourceResponse,
    summary="Update source configuration",
    description="Update configuration for an existing document source",
    responses={
        404: {"description": "Source not found"},
    },
)
async def update_source_config(
    source_id: str,
    update_data: DocumentSourceUpdate,
    db: AsyncSession = Depends(get_db),
) -> DocumentSource:
    """Update document source configuration."""
    repo = SourceRepository(db)

    # Convert to dict and exclude unset fields
    update_dict = update_data.model_dump(exclude_unset=True)

    updated_source = await repo.update_source(source_id, update_dict)

    if not updated_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    return updated_source


@router.get(
    "/sources/{source_id}/profiles",
    response_model=list[ExtractionProfileResponse],
    summary="List extraction profiles",
    description="Get all extraction profiles for a specific source",
    responses={
        404: {"description": "Source not found"},
    },
)
async def list_profiles(
    source_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[SourceExtractionProfile]:
    """List all extraction profiles for a source."""
    repo = SourceRepository(db)

    # Check if source exists
    source = await repo.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    profiles = await repo.get_profiles_by_source(source_id)
    return profiles


@router.post(
    "/sources/{source_id}/profiles",
    response_model=ExtractionProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create extraction profile",
    description="Create a new extraction profile for a document source",
    responses={
        404: {"description": "Source not found"},
        409: {"description": "Profile with same name already exists"},
    },
)
async def create_profile(
    source_id: str,
    profile_data: ExtractionProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> SourceExtractionProfile:
    """Create a new extraction profile for a source."""
    repo = SourceRepository(db)

    # Check if source exists
    source = await repo.get_source_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' not found",
        )

    # Check for duplicate profile name
    if await repo.check_duplicate_profile_name(source_id, profile_data.profile_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile with name '{profile_data.profile_name}' already exists for source '{source_id}'",
        )

    # Create profile
    profile = SourceExtractionProfile(
        source_id=source_id,
        **profile_data.model_dump(),
    )

    created_profile = await repo.create_profile(profile)
    return created_profile
