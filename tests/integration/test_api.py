"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns basic info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_readiness_check(client: TestClient) -> None:
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "checks" in data
    assert isinstance(data["checks"], dict)


def test_openapi_docs(client: TestClient) -> None:
    """Test OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client: TestClient) -> None:
    """Test OpenAPI spec is generated."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec


def test_404_error(client: TestClient) -> None:
    """Test 404 error handling."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client) -> None:
    """Test root endpoint with async client."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
