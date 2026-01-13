"""API endpoint tests.

Note: These tests require PostgreSQL due to PostgreSQL-specific features (ARRAY, TSVECTOR).
For unit tests without a database, we test that the app loads correctly.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client."""
    client = TestClient(app)
    yield client


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_openapi_schema_loads(client: TestClient):
    """Test that OpenAPI schema loads correctly."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Vibe4Vets API"
    assert "/api/v1/resources" in schema["paths"]
    assert "/api/v1/search" in schema["paths"]
    assert "/api/v1/admin/review-queue" in schema["paths"]


def test_docs_available(client: TestClient):
    """Test that API docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available(client: TestClient):
    """Test that ReDoc is available."""
    response = client.get("/redoc")
    assert response.status_code == 200
