"""Tests for ETL loader error handling.

These tests use mocks and don't require PostgreSQL.
"""

from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError, OperationalError

from etl.loader import Loader
from etl.models import LoadResult, NormalizedResource


class TestLoaderErrorHandling:
    """Tests for error differentiation in loader (no DB required)."""

    def test_load_result_has_retriable_field(self):
        """Test that LoadResult has retriable field."""
        result = LoadResult(action="failed", error="Test", retriable=True)
        assert result.retriable is True

        result_default = LoadResult(action="created")
        assert result_default.retriable is False

    def test_integrity_error_returns_skipped(self):
        """Test that IntegrityError results in skipped action."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = IntegrityError("duplicate key", {}, Exception("constraint violation"))

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "skipped"
        assert result.error == "Duplicate"
        assert result.retriable is False
        mock_session.rollback.assert_called_once()

    def test_timeout_error_is_retriable(self):
        """Test that timeout OperationalError is marked retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = OperationalError("connection timeout", {}, Exception("timeout expired"))

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Timeout" in result.error
        assert result.retriable is True
        mock_session.rollback.assert_called_once()

    def test_timed_out_error_is_retriable(self):
        """Test that 'timed out' OperationalError is marked retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = OperationalError(
            "query timed out", {}, Exception("query execution exceeded time limit")
        )

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Timeout" in result.error
        assert result.retriable is True
        mock_session.rollback.assert_called_once()

    def test_connection_error_is_retriable(self):
        """Test that connection OperationalError is marked retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = OperationalError("connection refused", {}, Exception("could not connect"))

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Connection" in result.error
        assert result.retriable is True
        mock_session.rollback.assert_called_once()

    def test_disconnect_error_is_retriable(self):
        """Test that disconnect OperationalError is marked retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = OperationalError(
            "server disconnected", {}, Exception("lost connection to server")
        )

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Connection" in result.error
        assert result.retriable is True
        mock_session.rollback.assert_called_once()

    def test_other_operational_error_not_retriable(self):
        """Test that other OperationalError is not retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = OperationalError("syntax error", {}, Exception("SQL syntax error"))

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Database error" in result.error
        assert result.retriable is False
        mock_session.rollback.assert_called_once()

    def test_unexpected_error_not_retriable(self):
        """Test that unexpected exceptions are not retriable."""
        mock_session = MagicMock()
        mock_session.exec.side_effect = ValueError("unexpected value error")

        loader = Loader(mock_session)
        resource = NormalizedResource(
            title="Test",
            description="Test",
            source_url="https://example.com",
            org_name="Test Org",
        )

        result = loader.load(resource)

        assert result.action == "failed"
        assert "Unexpected error" in result.error
        assert result.retriable is False
        mock_session.rollback.assert_called_once()
