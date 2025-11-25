"""Field API endpoint tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from dataminer.db.repositories.source import SourceRepository


async def _create_test_source(
    db_session: AsyncSession,
    source_id: str,
    source_name: str = "Test Source",
) -> None:
    """Helper to create a test source directly in the database."""
    repo = SourceRepository(db_session)
    await repo.create_source(
        source_id=source_id,
        source_name=source_name,
        country_code="TST",
        primary_language="en",
        legal_system="common_law",
        document_type="judgment",
        is_active=True,
        phase=1,
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_fields_source_not_found(async_client_with_db: AsyncClient) -> None:
    """Test listing fields for non-existent source."""
    response = await async_client_with_db.get("/v1/dataminer/sources/INVALID/fields")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["message"].lower()


@pytest.mark.asyncio
async def test_get_field_invalid_uuid(async_client_with_db: AsyncClient) -> None:
    """Test getting field with invalid UUID format."""
    response = await async_client_with_db.get("/v1/dataminer/fields/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_field_missing_name(async_client_with_db: AsyncClient) -> None:
    """Test creating field without required field_name."""
    response = await async_client_with_db.post(
        "/v1/dataminer/sources/TEST_SOURCE/fields",
        json={},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_field_source_not_found(async_client_with_db: AsyncClient) -> None:
    """Test creating field for non-existent source."""
    response = await async_client_with_db.post(
        "/v1/dataminer/sources/NONEXISTENT/fields",
        json={"field_name": "test_field"},
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["message"].lower()


@pytest.mark.asyncio
async def test_update_field_not_found(async_client_with_db: AsyncClient) -> None:
    """Test updating non-existent field."""
    response = await async_client_with_db.put(
        "/v1/dataminer/fields/00000000-0000-0000-0000-000000000000",
        json={"field_name": "updated_name"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_field_not_found(async_client_with_db: AsyncClient) -> None:
    """Test deleting non-existent field."""
    response = await async_client_with_db.delete(
        "/v1/dataminer/fields/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_full_field_lifecycle(
    async_client_with_db: AsyncClient, db_session: AsyncSession
) -> None:
    """Test complete field CRUD lifecycle with database.

    This test creates a source, then tests all field operations:
    - Create field
    - List fields
    - Get field by ID
    - Update field
    - Delete field
    """
    # First, create a source directly in the database
    await _create_test_source(db_session, "FIELD_TEST", "Field Test Source")

    # Create a field
    create_response = await async_client_with_db.post(
        "/v1/dataminer/sources/FIELD_TEST/fields",
        json={
            "field_name": "case_number",
            "field_display_name": "Case Number",
            "field_category": "critical",
            "field_type": "text",
            "extraction_method": "regex",
            "is_required": True,
            "confidence_threshold": 0.9,
        },
    )
    assert create_response.status_code == 201
    created_field = create_response.json()
    assert created_field["field_name"] == "case_number"
    assert created_field["field_display_name"] == "Case Number"
    assert created_field["field_category"] == "critical"
    assert created_field["is_required"] is True
    field_id = created_field["field_id"]

    # List fields for source
    list_response = await async_client_with_db.get("/v1/dataminer/sources/FIELD_TEST/fields")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] == 1
    assert len(list_data["items"]) == 1
    assert list_data["items"][0]["field_name"] == "case_number"

    # Get field by ID
    get_response = await async_client_with_db.get(f"/v1/dataminer/fields/{field_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["field_id"] == field_id
    assert get_data["field_name"] == "case_number"

    # Update field
    update_response = await async_client_with_db.put(
        f"/v1/dataminer/fields/{field_id}",
        json={
            "field_display_name": "Updated Case Number",
            "confidence_threshold": 0.95,
        },
    )
    assert update_response.status_code == 200
    updated_field = update_response.json()
    assert updated_field["field_display_name"] == "Updated Case Number"
    assert float(updated_field["confidence_threshold"]) == 0.95

    # Delete field
    delete_response = await async_client_with_db.delete(f"/v1/dataminer/fields/{field_id}")
    assert delete_response.status_code == 204

    # Verify field is deleted
    get_deleted_response = await async_client_with_db.get(f"/v1/dataminer/fields/{field_id}")
    assert get_deleted_response.status_code == 404


@pytest.mark.asyncio
async def test_field_filtering(async_client_with_db: AsyncClient, db_session: AsyncSession) -> None:
    """Test field filtering by category, type, and required status."""
    # Create source
    await _create_test_source(db_session, "FILTER_TEST", "Filter Test Source")

    # Create multiple fields with different categories
    await async_client_with_db.post(
        "/v1/dataminer/sources/FILTER_TEST/fields",
        json={
            "field_name": "critical_field",
            "field_category": "critical",
            "field_type": "text",
            "is_required": True,
        },
    )
    await async_client_with_db.post(
        "/v1/dataminer/sources/FILTER_TEST/fields",
        json={
            "field_name": "standard_field",
            "field_category": "standard",
            "field_type": "date",
            "is_required": False,
        },
    )
    await async_client_with_db.post(
        "/v1/dataminer/sources/FILTER_TEST/fields",
        json={
            "field_name": "another_critical",
            "field_category": "critical",
            "field_type": "number",
            "is_required": True,
        },
    )

    # Filter by category
    category_response = await async_client_with_db.get(
        "/v1/dataminer/sources/FILTER_TEST/fields?category=critical"
    )
    assert category_response.status_code == 200
    category_data = category_response.json()
    assert category_data["total"] == 2
    assert all(f["field_category"] == "critical" for f in category_data["items"])

    # Filter by field_type
    type_response = await async_client_with_db.get(
        "/v1/dataminer/sources/FILTER_TEST/fields?field_type=text"
    )
    assert type_response.status_code == 200
    type_data = type_response.json()
    assert type_data["total"] == 1
    assert type_data["items"][0]["field_type"] == "text"

    # Filter by is_required
    required_response = await async_client_with_db.get(
        "/v1/dataminer/sources/FILTER_TEST/fields?is_required=true"
    )
    assert required_response.status_code == 200
    required_data = required_response.json()
    assert required_data["total"] == 2
    assert all(f["is_required"] is True for f in required_data["items"])


@pytest.mark.asyncio
async def test_field_pagination(
    async_client_with_db: AsyncClient, db_session: AsyncSession
) -> None:
    """Test field pagination with limit and offset."""
    # Create source
    await _create_test_source(db_session, "PAGE_TEST", "Pagination Test Source")

    # Create 5 fields
    for i in range(5):
        await async_client_with_db.post(
            "/v1/dataminer/sources/PAGE_TEST/fields",
            json={
                "field_name": f"field_{i}",
                "field_category": "standard",
                "display_order": i,
            },
        )

    # Test limit
    limit_response = await async_client_with_db.get(
        "/v1/dataminer/sources/PAGE_TEST/fields?limit=2"
    )
    assert limit_response.status_code == 200
    limit_data = limit_response.json()
    assert limit_data["total"] == 5
    assert len(limit_data["items"]) == 2
    assert limit_data["limit"] == 2

    # Test offset
    offset_response = await async_client_with_db.get(
        "/v1/dataminer/sources/PAGE_TEST/fields?limit=2&offset=2"
    )
    assert offset_response.status_code == 200
    offset_data = offset_response.json()
    assert offset_data["total"] == 5
    assert len(offset_data["items"]) == 2
    assert offset_data["offset"] == 2


@pytest.mark.asyncio
async def test_duplicate_field_name_rejected(
    async_client_with_db: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that duplicate field names within same source are rejected."""
    # Create source
    await _create_test_source(db_session, "DUP_TEST", "Duplicate Test Source")

    # Create first field
    first_response = await async_client_with_db.post(
        "/v1/dataminer/sources/DUP_TEST/fields",
        json={"field_name": "unique_field"},
    )
    assert first_response.status_code == 201

    # Try to create field with same name
    duplicate_response = await async_client_with_db.post(
        "/v1/dataminer/sources/DUP_TEST/fields",
        json={"field_name": "unique_field"},
    )
    assert duplicate_response.status_code == 409
    assert "already exists" in duplicate_response.json()["message"].lower()


@pytest.mark.asyncio
async def test_update_field_duplicate_name_rejected(
    async_client_with_db: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that updating field to duplicate name is rejected."""
    # Create source
    await _create_test_source(db_session, "UPD_DUP_TEST", "Update Duplicate Test Source")

    # Create two fields
    await async_client_with_db.post(
        "/v1/dataminer/sources/UPD_DUP_TEST/fields",
        json={"field_name": "field_one"},
    )
    second_response = await async_client_with_db.post(
        "/v1/dataminer/sources/UPD_DUP_TEST/fields",
        json={"field_name": "field_two"},
    )
    field_two_id = second_response.json()["field_id"]

    # Try to update field_two to have same name as field_one
    update_response = await async_client_with_db.put(
        f"/v1/dataminer/fields/{field_two_id}",
        json={"field_name": "field_one"},
    )
    assert update_response.status_code == 409
    assert "already exists" in update_response.json()["message"].lower()
