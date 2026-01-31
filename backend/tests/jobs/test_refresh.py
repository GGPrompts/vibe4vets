"""Tests for the refresh job."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from jobs.refresh import CONNECTOR_REGISTRY, RefreshJob, get_available_connectors


class TestRefreshJob:
    """Tests for RefreshJob class."""

    def test_job_properties(self):
        """Test job name and description."""
        job = RefreshJob()

        assert job.name == "refresh"
        assert "refresh" in job.description.lower()

    def test_get_connectors_all(self):
        """Test getting all connectors."""
        job = RefreshJob()

        # Mock the connector registry to avoid instantiation issues
        # Use clear=True to replace the entire registry
        with patch.dict(
            CONNECTOR_REGISTRY,
            {
                "test1": MagicMock,
                "test2": MagicMock,
            },
            clear=True,
        ):
            connectors = job._get_connectors()
            assert len(connectors) == 2

    def test_get_connectors_specific(self):
        """Test getting a specific connector."""
        job = RefreshJob()

        mock_cls = MagicMock()
        with patch.dict(CONNECTOR_REGISTRY, {"test_conn": mock_cls}, clear=True):
            connectors = job._get_connectors("test_conn")
            assert len(connectors) == 1
            mock_cls.assert_called_once()

    def test_get_connectors_not_found(self):
        """Test getting a non-existent connector."""
        job = RefreshJob()

        with patch.dict(CONNECTOR_REGISTRY, {}, clear=True):
            connectors = job._get_connectors("nonexistent")
            assert len(connectors) == 0

    def test_execute_no_connectors(self):
        """Test execute with no connectors found."""
        job = RefreshJob()
        mock_session = MagicMock()

        with patch.dict(CONNECTOR_REGISTRY, {}, clear=True):
            stats = job.execute(mock_session, connector_name="nonexistent")

        assert "error" in stats
        assert stats["connectors_run"] == 0

    def test_execute_with_dry_run(self):
        """Test execute in dry-run mode."""
        job = RefreshJob()
        mock_session = MagicMock()

        # Create mock connector
        mock_connector = MagicMock()
        mock_connector.metadata.name = "Test Connector"
        mock_connector.metadata.tier = 1
        mock_connector.run.return_value = []

        # Mock connector instantiation
        mock_cls = MagicMock(return_value=mock_connector)

        # Mock ETL pipeline
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.stats.extracted = 0
        mock_result.stats.normalized = 0
        mock_result.stats.deduplicated = 0
        mock_result.stats.created = 0
        mock_result.stats.updated = 0
        mock_result.stats.skipped = 0
        mock_result.stats.failed = 0
        mock_result.errors = []
        mock_result.started_at = datetime.now(UTC)
        mock_result.completed_at = datetime.now(UTC)

        with patch.dict(CONNECTOR_REGISTRY, {"test": mock_cls}, clear=True):
            with patch("jobs.refresh.ETLPipeline") as mock_pipeline_cls:
                mock_pipeline = MagicMock()
                mock_pipeline.dry_run.return_value = mock_result
                mock_pipeline_cls.return_value = mock_pipeline

                stats = job.execute(mock_session, dry_run=True)

        assert stats["success"] is True
        mock_pipeline.dry_run.assert_called_once()

    def test_execute_full_run(self):
        """Test execute with full ETL run."""
        job = RefreshJob()
        mock_session = MagicMock()

        # Create mock connector
        mock_connector = MagicMock()
        mock_connector.metadata.name = "Test Connector"
        mock_connector.metadata.tier = 1
        mock_connector.run.return_value = []

        mock_cls = MagicMock(return_value=mock_connector)

        # Mock ETL pipeline result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.stats.extracted = 10
        mock_result.stats.normalized = 8
        mock_result.stats.deduplicated = 2
        mock_result.stats.created = 5
        mock_result.stats.updated = 3
        mock_result.stats.skipped = 0
        mock_result.stats.failed = 0
        mock_result.errors = []
        mock_result.started_at = datetime.now(UTC)
        mock_result.completed_at = datetime.now(UTC)

        with patch.dict(CONNECTOR_REGISTRY, {"test": mock_cls}, clear=True):
            with patch("jobs.refresh.ETLPipeline") as mock_pipeline_cls:
                mock_pipeline = MagicMock()
                mock_pipeline.run.return_value = mock_result
                mock_pipeline_cls.return_value = mock_pipeline

                # Mock the geocoding method to return an int
                with patch.object(job, "_geocode_from_zip_centroids", return_value=0):
                    stats = job.execute(mock_session, dry_run=False)

        assert stats["success"] is True
        assert stats["extracted"] == 10
        assert stats["created"] == 5
        assert stats["updated"] == 3
        mock_pipeline.run.assert_called_once()

    def test_format_message_success(self):
        """Test formatting success message."""
        job = RefreshJob()

        stats = {
            "success": True,
            "created": 5,
            "updated": 3,
            "skipped": 2,
        }

        message = job._format_message(stats)

        assert "5 created" in message
        assert "3 updated" in message
        assert "2 skipped" in message

    def test_format_message_failure(self):
        """Test formatting failure message."""
        job = RefreshJob()

        stats = {
            "success": False,
            "errors": 3,
        }

        message = job._format_message(stats)

        assert "failed" in message.lower()
        assert "3 errors" in message


class TestGetAvailableConnectors:
    """Tests for get_available_connectors function."""

    def test_returns_connector_metadata(self):
        """Test that connector metadata is returned."""
        mock_connector = MagicMock()
        mock_connector.metadata.name = "Test Connector"
        mock_connector.metadata.url = "https://test.com"
        mock_connector.metadata.tier = 1
        mock_connector.metadata.frequency = "daily"
        mock_connector.metadata.requires_auth = False

        mock_cls = MagicMock(return_value=mock_connector)

        with patch.dict(CONNECTOR_REGISTRY, {"test": mock_cls}, clear=True):
            connectors = get_available_connectors()

        assert len(connectors) == 1
        assert connectors[0]["name"] == "test"
        assert connectors[0]["display_name"] == "Test Connector"
        assert connectors[0]["tier"] == 1

    def test_handles_connector_init_failure(self):
        """Test that connector initialization failures are handled."""
        mock_cls = MagicMock(side_effect=RuntimeError("Init failed"))

        with patch.dict(CONNECTOR_REGISTRY, {"failing": mock_cls}, clear=True):
            connectors = get_available_connectors()

        assert len(connectors) == 1
        assert connectors[0]["name"] == "failing"
        assert "error" in connectors[0]
