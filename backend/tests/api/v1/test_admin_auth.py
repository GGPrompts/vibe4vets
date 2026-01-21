"""Tests for admin authentication on admin endpoints."""

import hashlib

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def valid_api_key() -> str:
    """Generate a valid admin API key."""
    return "test-admin-secret-key"


@pytest.fixture
def valid_api_key_hash(valid_api_key: str) -> str:
    """Get the SHA-256 hash of the valid API key."""
    return hashlib.sha256(valid_api_key.encode()).hexdigest()


@pytest.fixture
def client_with_auth(valid_api_key_hash: str):
    """Create a test client with admin auth configured."""
    # Save original value
    original_hash = settings.admin_api_key_hash

    # Set the hash for testing
    settings.admin_api_key_hash = valid_api_key_hash

    client = TestClient(app)
    yield client

    # Restore original value
    settings.admin_api_key_hash = original_hash


class TestAdminEndpointsWithoutAuth:
    """Test that admin endpoints return 401 without API key."""

    @pytest.fixture(autouse=True)
    def setup_auth(self, valid_api_key_hash: str):
        """Configure admin auth for all tests in this class."""
        original_hash = settings.admin_api_key_hash
        settings.admin_api_key_hash = valid_api_key_hash
        yield
        settings.admin_api_key_hash = original_hash

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    # admin.py endpoints
    def test_review_queue_requires_auth(self, client: TestClient):
        """Test /admin/review-queue returns 401 without auth."""
        response = client.get("/api/v1/admin/review-queue")
        assert response.status_code == 401
        assert "Missing API key" in response.json()["detail"]

    def test_sources_requires_auth(self, client: TestClient):
        """Test /admin/sources returns 401 without auth."""
        response = client.get("/api/v1/admin/sources")
        assert response.status_code == 401

    def test_dashboard_stats_requires_auth(self, client: TestClient):
        """Test /admin/dashboard/stats returns 401 without auth."""
        response = client.get("/api/v1/admin/dashboard/stats")
        assert response.status_code == 401

    def test_jobs_requires_auth(self, client: TestClient):
        """Test /admin/jobs returns 401 without auth."""
        response = client.get("/api/v1/admin/jobs")
        assert response.status_code == 401

    def test_run_job_requires_auth(self, client: TestClient):
        """Test POST /admin/jobs/{name}/run returns 401 without auth."""
        response = client.post("/api/v1/admin/jobs/refresh/run")
        assert response.status_code == 401

    # feedback.py admin endpoints
    def test_feedback_admin_requires_auth(self, client: TestClient):
        """Test /feedback/admin returns 401 without auth."""
        response = client.get("/api/v1/feedback/admin")
        assert response.status_code == 401

    def test_feedback_stats_requires_auth(self, client: TestClient):
        """Test /feedback/admin/stats/summary returns 401 without auth."""
        response = client.get("/api/v1/feedback/admin/stats/summary")
        assert response.status_code == 401

    # analytics.py admin endpoints
    def test_analytics_summary_requires_auth(self, client: TestClient):
        """Test /analytics/admin/summary returns 401 without auth."""
        response = client.get("/api/v1/analytics/admin/summary")
        assert response.status_code == 401

    def test_analytics_dashboard_requires_auth(self, client: TestClient):
        """Test /analytics/admin/dashboard returns 401 without auth."""
        response = client.get("/api/v1/analytics/admin/dashboard")
        assert response.status_code == 401

    def test_analytics_popular_searches_requires_auth(self, client: TestClient):
        """Test /analytics/admin/popular-searches returns 401 without auth."""
        response = client.get("/api/v1/analytics/admin/popular-searches")
        assert response.status_code == 401


class TestAdminEndpointsWithInvalidKey:
    """Test that admin endpoints return 401 with invalid API key."""

    @pytest.fixture(autouse=True)
    def setup_auth(self, valid_api_key_hash: str):
        """Configure admin auth for all tests in this class."""
        original_hash = settings.admin_api_key_hash
        settings.admin_api_key_hash = valid_api_key_hash
        yield
        settings.admin_api_key_hash = original_hash

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_invalid_key_returns_401(self, client: TestClient):
        """Test that an invalid API key returns 401."""
        response = client.get(
            "/api/v1/admin/review-queue",
            headers={"X-Admin-Key": "wrong-key"},
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]


class TestAdminEndpointsWithValidKey:
    """Test that admin endpoints work with valid API key."""

    @pytest.fixture(autouse=True)
    def setup_auth(self, valid_api_key_hash: str):
        """Configure admin auth for all tests in this class."""
        original_hash = settings.admin_api_key_hash
        settings.admin_api_key_hash = valid_api_key_hash
        yield
        settings.admin_api_key_hash = original_hash

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_review_queue_with_valid_key(self, client: TestClient, valid_api_key: str):
        """Test /admin/review-queue works with valid auth."""
        response = client.get(
            "/api/v1/admin/review-queue",
            headers={"X-Admin-Key": valid_api_key},
        )
        # Should get through auth - might fail on db but not 401
        assert response.status_code != 401

    def test_jobs_with_valid_key(self, client: TestClient, valid_api_key: str):
        """Test /admin/jobs works with valid auth."""
        response = client.get(
            "/api/v1/admin/jobs",
            headers={"X-Admin-Key": valid_api_key},
        )
        assert response.status_code == 200

    def test_feedback_stats_with_valid_key(self, client: TestClient, valid_api_key: str):
        """Test /feedback/admin/stats/summary works with valid auth."""
        response = client.get(
            "/api/v1/feedback/admin/stats/summary",
            headers={"X-Admin-Key": valid_api_key},
        )
        # Should get through auth - might fail on db but not 401
        assert response.status_code != 401


class TestAdminAuthNotConfigured:
    """Test behavior when admin auth is not configured."""

    @pytest.fixture(autouse=True)
    def setup_no_auth(self):
        """Disable admin auth for tests in this class."""
        original_hash = settings.admin_api_key_hash
        settings.admin_api_key_hash = None
        yield
        settings.admin_api_key_hash = original_hash

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_returns_503_when_not_configured(self, client: TestClient):
        """Test that 503 is returned when auth is not configured."""
        response = client.get("/api/v1/admin/review-queue")
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]


class TestPublicEndpointsNoAuth:
    """Test that public endpoints don't require auth."""

    @pytest.fixture(autouse=True)
    def setup_auth(self, valid_api_key_hash: str):
        """Configure admin auth for all tests in this class."""
        original_hash = settings.admin_api_key_hash
        settings.admin_api_key_hash = valid_api_key_hash
        yield
        settings.admin_api_key_hash = original_hash

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_health_check_no_auth(self, client: TestClient):
        """Test /health doesn't require auth."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_resources_list_no_auth(self, client: TestClient):
        """Test /resources doesn't require auth."""
        response = client.get("/api/v1/resources")
        # May fail due to db issues, but not 401
        assert response.status_code != 401

    def test_search_no_auth(self, client: TestClient):
        """Test /search doesn't require auth."""
        response = client.get("/api/v1/search")
        # May fail due to db issues, but not 401
        assert response.status_code != 401

    def test_feedback_submit_no_auth(self, client: TestClient):
        """Test POST /feedback doesn't require auth (public endpoint)."""
        response = client.post(
            "/api/v1/feedback",
            json={
                "resource_id": "00000000-0000-0000-0000-000000000000",
                "issue_type": "other",
                "description": "test",
            },
        )
        # May fail with 404 (resource not found), but not 401
        assert response.status_code != 401

    def test_analytics_events_no_auth(self, client: TestClient):
        """Test POST /analytics/events doesn't require auth (public endpoint)."""
        response = client.post(
            "/api/v1/analytics/events",
            json={
                "event_type": "page_view",
                "event_name": "test",
            },
        )
        # May fail due to db issues, but not 401
        assert response.status_code != 401
