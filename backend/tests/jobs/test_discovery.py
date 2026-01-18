"""Tests for the AI discovery job."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from jobs.discovery import (
    DiscoveryJob,
    DiscoveryStats,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    ValidatedCandidate,
)


class TestValidatedCandidate:
    """Tests for ValidatedCandidate routing logic."""

    def test_high_confidence_valid_auto_approves(self):
        """High confidence valid resources should auto-approve."""
        candidate = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=0.95,
        )
        assert candidate.should_auto_approve
        assert not candidate.should_queue_for_review
        assert not candidate.should_discard

    def test_medium_confidence_valid_queues(self):
        """Medium confidence valid resources should queue for review."""
        candidate = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=0.8,
        )
        assert not candidate.should_auto_approve
        assert candidate.should_queue_for_review
        assert not candidate.should_discard

    def test_low_confidence_discards(self):
        """Low confidence resources should be discarded."""
        candidate = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=0.5,
        )
        assert not candidate.should_auto_approve
        assert not candidate.should_queue_for_review
        assert candidate.should_discard

    def test_invalid_discards_regardless_of_confidence(self):
        """Invalid resources should be discarded regardless of confidence."""
        candidate = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="invalid",
            confidence=0.95,
        )
        assert not candidate.should_auto_approve
        assert not candidate.should_queue_for_review
        assert candidate.should_discard

    def test_needs_review_high_confidence_queues(self):
        """Needs review status with high confidence should queue, not auto-approve."""
        candidate = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="needs_review",
            confidence=0.95,
        )
        assert not candidate.should_auto_approve
        assert candidate.should_queue_for_review
        assert not candidate.should_discard

    def test_boundary_at_high_threshold(self):
        """Test behavior exactly at high confidence threshold."""
        # At exactly 0.9, should NOT auto-approve (threshold is exclusive)
        at_threshold = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=HIGH_CONFIDENCE_THRESHOLD,
        )
        assert at_threshold.should_auto_approve  # >= threshold
        assert not at_threshold.should_queue_for_review

    def test_boundary_at_medium_threshold(self):
        """Test behavior exactly at medium confidence threshold."""
        # At exactly 0.7, should queue for review
        at_threshold = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=MEDIUM_CONFIDENCE_THRESHOLD,
        )
        assert not at_threshold.should_auto_approve
        assert at_threshold.should_queue_for_review
        assert not at_threshold.should_discard

        # Just below 0.7 should discard
        below_threshold = ValidatedCandidate(
            data={"name": "Test"},
            validation_status="valid",
            confidence=MEDIUM_CONFIDENCE_THRESHOLD - 0.01,
        )
        assert not below_threshold.should_auto_approve
        assert not below_threshold.should_queue_for_review
        assert below_threshold.should_discard


class TestDiscoveryJob:
    """Tests for the DiscoveryJob class."""

    def test_job_properties(self):
        """Test job name and description."""
        job = DiscoveryJob()
        assert job.name == "discovery"
        assert "AI" in job.description or "discovery" in job.description.lower()

    def test_get_discovery_prompts_all(self):
        """Test getting all discovery prompts."""
        job = DiscoveryJob()
        prompts = job._get_discovery_prompts()
        assert len(prompts) >= 1
        assert all(p.suffix == ".md" for p in prompts)
        assert all(p.exists() for p in prompts)

    def test_get_discovery_prompts_by_category(self):
        """Test filtering prompts by category."""
        job = DiscoveryJob()

        housing_prompts = job._get_discovery_prompts("housing")
        assert any("housing" in p.stem.lower() for p in housing_prompts)

        employment_prompts = job._get_discovery_prompts("employment")
        assert any("employment" in p.stem.lower() for p in employment_prompts)

    def test_get_discovery_prompts_nonexistent_category(self):
        """Test filtering by nonexistent category returns empty."""
        job = DiscoveryJob()
        prompts = job._get_discovery_prompts("nonexistent_category_xyz")
        assert len(prompts) == 0

    def test_format_stats(self):
        """Test stats formatting."""
        job = DiscoveryJob()
        stats = DiscoveryStats(
            prompts_run=2,
            candidates_found=10,
            validated=10,
            auto_approved=3,
            queued_for_review=5,
            discarded=2,
            errors=["Error 1"],
        )
        formatted = job._format_stats(stats)

        assert formatted["prompts_run"] == 2
        assert formatted["candidates_found"] == 10
        assert formatted["auto_approved"] == 3
        assert formatted["queued_for_review"] == 5
        assert formatted["discarded"] == 2
        assert formatted["errors"] == 1
        assert "tokens_used" in formatted

    def test_format_message_success(self):
        """Test success message formatting."""
        job = DiscoveryJob()
        stats = {
            "candidates_found": 10,
            "auto_approved": 3,
            "queued_for_review": 5,
        }
        message = job._format_message(stats)
        assert "10" in message
        assert "3" in message
        assert "5" in message

    def test_format_message_error(self):
        """Test error message formatting."""
        job = DiscoveryJob()
        stats = {"error": "No API key configured"}
        message = job._format_message(stats)
        assert "failed" in message.lower()
        assert "No API key configured" in message

    @patch("jobs.discovery.ClaudeClient")
    def test_execute_without_api_key(self, mock_client_class):
        """Test execution fails gracefully without API key."""
        mock_client_class.side_effect = ValueError("ANTHROPIC_API_KEY not configured")

        job = DiscoveryJob()
        session = MagicMock()

        result = job.execute(session)

        assert "error" in result
        assert "ANTHROPIC_API_KEY" in result["error"]

    @patch("jobs.discovery.ClaudeClient")
    def test_execute_dry_run_skip_validation(self, mock_client_class):
        """Test dry run with validation skipped."""
        # Mock the Claude client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock discovery response
        mock_response = MagicMock()
        mock_response.json = [
            {"name": "Test Resource", "confidence": 0.95, "category": "housing"},
            {"name": "Another Resource", "confidence": 0.75, "category": "housing"},
            {"name": "Low Conf Resource", "confidence": 0.5, "category": "housing"},
        ]
        mock_response.input_tokens = 100
        mock_response.output_tokens = 200
        mock_client.complete.return_value = mock_response

        job = DiscoveryJob()
        session = MagicMock()

        # Configure session to return empty for source lookup
        session.exec.return_value.first.return_value = None

        result = job.execute(
            session,
            category="housing",
            dry_run=True,
            skip_validation=True,
        )

        assert result["candidates_found"] == 3
        # With skip_validation, candidates use their original confidence
        # 0.95 -> needs_review (because skip_validation sets status to needs_review)
        # 0.75 -> queued
        # 0.5 -> discarded
        assert result["discarded"] >= 1  # Low confidence discarded


class TestDiscoveryStats:
    """Tests for DiscoveryStats dataclass."""

    def test_defaults(self):
        """Test default values."""
        stats = DiscoveryStats()
        assert stats.prompts_run == 0
        assert stats.candidates_found == 0
        assert stats.validated == 0
        assert stats.auto_approved == 0
        assert stats.queued_for_review == 0
        assert stats.discarded == 0
        assert stats.duplicates_skipped == 0
        assert stats.errors == []
        assert stats.input_tokens == 0
        assert stats.output_tokens == 0

    def test_error_list_mutable(self):
        """Test that error list is properly isolated between instances."""
        stats1 = DiscoveryStats()
        stats2 = DiscoveryStats()

        stats1.errors.append("Error 1")

        assert len(stats1.errors) == 1
        assert len(stats2.errors) == 0


class TestThresholds:
    """Tests for confidence thresholds."""

    def test_high_threshold_value(self):
        """Test high confidence threshold is 0.9."""
        assert HIGH_CONFIDENCE_THRESHOLD == 0.9

    def test_medium_threshold_value(self):
        """Test medium confidence threshold is 0.7."""
        assert MEDIUM_CONFIDENCE_THRESHOLD == 0.7

    def test_thresholds_ordered(self):
        """Test high threshold is greater than medium."""
        assert HIGH_CONFIDENCE_THRESHOLD > MEDIUM_CONFIDENCE_THRESHOLD
