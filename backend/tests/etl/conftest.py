"""Pytest fixtures for ETL tests."""

from datetime import UTC, datetime
from typing import Any, Self

import pytest

from connectors.base import ResourceCandidate, SourceMetadata

# Note: The etl_session fixture uses the main conftest's session fixture
# which already has PostgreSQL ARRAY/JSONB -> SQLite TEXT compilers registered


@pytest.fixture(name="etl_session")
def etl_session_fixture(session):
    """Alias for the main session fixture for ETL tests.

    Uses the session from tests/conftest.py which has SQLite compatibility
    for PostgreSQL types.
    """
    yield session


@pytest.fixture
def sample_candidate() -> ResourceCandidate:
    """Create a sample ResourceCandidate for testing."""
    return ResourceCandidate(
        title="VA Employment Services",
        description=("Employment assistance for veterans including job placement and career counseling."),
        source_url="https://www.va.gov/employment",
        org_name="U.S. Department of Veterans Affairs",
        org_website="https://www.va.gov",
        address="810 Vermont Avenue NW",
        city="Washington",
        state="DC",
        zip_code="20420",
        categories=["employment", "training"],
        tags=["va-benefits", "job-placement"],
        phone="1-800-827-1000",
        email="contact@va.gov",
        hours="Monday-Friday 8am-5pm",
        eligibility="All veterans with honorable discharge",
        how_to_apply="Visit your local VA office or apply online at va.gov",
        scope="national",
        states=["DC"],
        raw_data={"source": "va.gov"},
        fetched_at=datetime.now(UTC),
    )


@pytest.fixture
def minimal_candidate() -> ResourceCandidate:
    """Create a minimal ResourceCandidate with only required fields."""
    return ResourceCandidate(
        title="Basic Resource",
        description="A basic resource description.",
        source_url="https://example.com/resource",
        org_name="Example Organization",
    )


@pytest.fixture
def candidate_missing_fields() -> ResourceCandidate:
    """Create a ResourceCandidate missing required fields."""
    return ResourceCandidate(
        title="",  # Missing title
        description="Has description",
        source_url="https://example.com",
        org_name="",  # Missing org_name
    )


@pytest.fixture
def sample_source_metadata() -> SourceMetadata:
    """Create sample source metadata."""
    return SourceMetadata(
        name="Test Source",
        url="https://example.com",
        tier=2,
        frequency="weekly",
    )


class MockConnector:
    """Mock connector for testing."""

    def __init__(
        self,
        candidates: list[ResourceCandidate],
        name: str = "Mock Source",
        tier: int = 2,
    ):
        self._candidates = candidates
        self._metadata = SourceMetadata(
            name=name,
            url="https://mock.example.com",
            tier=tier,
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        return self._candidates

    @property
    def metadata(self) -> SourceMetadata:
        return self._metadata

    def close(self) -> None:
        """No-op close for mock."""
        pass

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        self.close()


class FailingConnector:
    """Connector that raises an exception for testing error handling."""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Failing Source",
            url="https://fail.example.com",
            tier=4,
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        raise RuntimeError("Simulated connector failure")

    def close(self) -> None:
        """No-op close for mock."""
        pass

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        self.close()


@pytest.fixture
def mock_connector(sample_candidate) -> MockConnector:
    """Create a mock connector with one sample candidate."""
    return MockConnector([sample_candidate])


@pytest.fixture
def failing_connector() -> FailingConnector:
    """Create a connector that fails."""
    return FailingConnector()


class TimeoutConnector:
    """Connector that raises a timeout exception for testing."""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Timeout Source",
            url="https://timeout.example.com",
            tier=4,
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        import httpx

        raise httpx.TimeoutException("Connection timed out")

    def close(self) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.close()


class AuthFailureConnector:
    """Connector that raises an auth failure exception for testing."""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Auth Failure Source",
            url="https://auth-fail.example.com",
            tier=1,
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        import httpx

        # Create a mock response object
        class MockResponse:
            status_code = 401

        raise httpx.HTTPStatusError("Unauthorized", request=None, response=MockResponse())

    def close(self) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.close()


@pytest.fixture
def timeout_connector() -> TimeoutConnector:
    """Create a connector that times out."""
    return TimeoutConnector()


@pytest.fixture
def auth_failure_connector() -> AuthFailureConnector:
    """Create a connector that fails auth."""
    return AuthFailureConnector()
