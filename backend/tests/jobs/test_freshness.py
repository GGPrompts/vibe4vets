"""Tests for the freshness update job."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from jobs.freshness import FreshnessJob
from jobs.base import JobStatus


class TestFreshnessJob:
    """Tests for FreshnessJob class."""

    def test_job_properties(self):
        """Test job name and description."""
        job = FreshnessJob()

        assert job.name == "freshness"
        assert "freshness" in job.description.lower()

    def test_execute_updates_scores(self):
        """Test that execute updates freshness scores."""
        job = FreshnessJob()
        mock_session = MagicMock()

        # Mock TrustService
        with patch("jobs.freshness.TrustService") as mock_trust_cls:
            mock_trust = MagicMock()
            mock_trust.refresh_all_freshness_scores.return_value = 5
            mock_trust.get_stale_resources.return_value = [MagicMock(), MagicMock()]
            mock_trust_cls.return_value = mock_trust

            # Mock count queries
            with patch.object(job, "_count_active_resources", return_value=10):
                with patch.object(job, "_get_average_freshness", return_value=0.75):
                    stats = job.execute(mock_session)

        assert stats["total_active"] == 10
        assert stats["updated"] == 5
        assert stats["unchanged"] == 5
        assert stats["average_freshness"] == 0.75
        assert stats["stale_count"] == 2

        mock_trust.refresh_all_freshness_scores.assert_called_once()

    def test_execute_with_no_resources(self):
        """Test execute when no resources exist."""
        job = FreshnessJob()
        mock_session = MagicMock()

        with patch("jobs.freshness.TrustService") as mock_trust_cls:
            mock_trust = MagicMock()
            mock_trust.refresh_all_freshness_scores.return_value = 0
            mock_trust.get_stale_resources.return_value = []
            mock_trust_cls.return_value = mock_trust

            with patch.object(job, "_count_active_resources", return_value=0):
                with patch.object(job, "_get_average_freshness", return_value=None):
                    stats = job.execute(mock_session)

        assert stats["total_active"] == 0
        assert stats["updated"] == 0
        assert stats["average_freshness"] is None
        assert stats["stale_count"] == 0

    def test_format_message(self):
        """Test formatting statistics message."""
        job = FreshnessJob()

        stats = {
            "total_active": 100,
            "updated": 25,
            "average_freshness": 0.82,
            "stale_count": 10,
        }

        message = job._format_message(stats)

        assert "25/100" in message
        assert "82" in message  # percentage
        assert "10 stale" in message

    def test_format_message_no_average(self):
        """Test formatting message when no average available."""
        job = FreshnessJob()

        stats = {
            "total_active": 0,
            "updated": 0,
            "average_freshness": None,
            "stale_count": 0,
        }

        message = job._format_message(stats)

        assert "N/A" in message

    def test_count_active_resources(self):
        """Test counting active resources."""
        job = FreshnessJob()
        mock_session = MagicMock()
        mock_session.exec.return_value.one.return_value = 42

        count = job._count_active_resources(mock_session)

        assert count == 42

    def test_count_active_resources_none(self):
        """Test counting when query returns None."""
        job = FreshnessJob()
        mock_session = MagicMock()
        mock_session.exec.return_value.one.return_value = None

        count = job._count_active_resources(mock_session)

        assert count == 0

    def test_get_average_freshness(self):
        """Test getting average freshness score."""
        job = FreshnessJob()
        mock_session = MagicMock()
        mock_session.exec.return_value.one.return_value = 0.85

        avg = job._get_average_freshness(mock_session)

        assert avg == 0.85

    def test_get_average_freshness_none(self):
        """Test getting average when no resources exist."""
        job = FreshnessJob()
        mock_session = MagicMock()
        mock_session.exec.return_value.one.return_value = None

        avg = job._get_average_freshness(mock_session)

        assert avg is None


class TestFreshnessJobIntegration:
    """Integration-style tests for FreshnessJob."""

    def test_full_run_workflow(self):
        """Test the full job workflow through run() method."""
        job = FreshnessJob()

        with patch("jobs.base.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)

            with patch("jobs.freshness.TrustService") as mock_trust_cls:
                mock_trust = MagicMock()
                mock_trust.refresh_all_freshness_scores.return_value = 3
                mock_trust.get_stale_resources.return_value = []
                mock_trust_cls.return_value = mock_trust

                with patch.object(job, "_count_active_resources", return_value=10):
                    with patch.object(job, "_get_average_freshness", return_value=0.9):
                        result = job.run()

        assert result.status.value == "completed"
        assert result.job_name == "freshness"
        assert result.stats["updated"] == 3
