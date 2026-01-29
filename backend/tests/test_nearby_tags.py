"""Tests for nearby endpoint with tags filtering.

Note: Full integration tests require PostgreSQL with PostGIS for spatial queries.
These tests verify that the endpoint correctly accepts and parses the tags parameter.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client."""
    client = TestClient(app)
    yield client


def test_nearby_accepts_tags_parameter(client: TestClient):
    """Test that the nearby endpoint accepts tags parameter without error."""
    # Mock the ResourceService.list_nearby to avoid needing a real database
    with patch("app.api.v1.resources.ResourceService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.list_nearby.return_value = None  # Simulates zip not found
        mock_service_class.return_value = mock_service

        # Call the endpoint with tags parameter
        response = client.get(
            "/api/v1/resources/nearby",
            params={
                "zip": "12345",
                "tags": "combat_veteran,female_veteran",
            },
        )

        # Endpoint should return 404 for zip not found (not a parameter error)
        assert response.status_code == 404
        assert response.json()["detail"] == "Zip code not found"

        # Verify the service was called with parsed tags
        mock_service.list_nearby.assert_called_once()
        call_kwargs = mock_service.list_nearby.call_args[1]
        assert call_kwargs["tags"] == ["combat_veteran", "female_veteran"]


def test_nearby_tags_with_categories(client: TestClient):
    """Test that nearby endpoint correctly handles both tags and categories."""
    with patch("app.api.v1.resources.ResourceService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.list_nearby.return_value = None
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/resources/nearby",
            params={
                "zip": "22201",
                "categories": "housing,employment",
                "tags": "hud-vash,ssvf",
                "radius": "50",
            },
        )

        assert response.status_code == 404

        mock_service.list_nearby.assert_called_once()
        call_kwargs = mock_service.list_nearby.call_args[1]
        assert call_kwargs["categories"] == ["housing", "employment"]
        assert call_kwargs["tags"] == ["hud-vash", "ssvf"]
        assert call_kwargs["radius_miles"] == 50


def test_nearby_without_tags(client: TestClient):
    """Test that nearby endpoint works without tags (backward compatible)."""
    with patch("app.api.v1.resources.ResourceService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.list_nearby.return_value = None
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/resources/nearby",
            params={"zip": "90210"},
        )

        assert response.status_code == 404

        mock_service.list_nearby.assert_called_once()
        call_kwargs = mock_service.list_nearby.call_args[1]
        assert call_kwargs["tags"] is None


def test_nearby_empty_tags(client: TestClient):
    """Test that empty tags string is handled correctly."""
    with patch("app.api.v1.resources.ResourceService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.list_nearby.return_value = None
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/resources/nearby",
            params={"zip": "10001", "tags": ""},
        )

        assert response.status_code == 404

        mock_service.list_nearby.assert_called_once()
        call_kwargs = mock_service.list_nearby.call_args[1]
        # Empty string should result in None (no tags filter)
        assert call_kwargs["tags"] is None
