"""Tests for Stand Down Events connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.stand_down_events import StandDownEventsConnector


class TestStandDownEventsConnector:
    """Tests for StandDownEventsConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        meta = connector.metadata

        assert "Stand Down" in meta.name
        assert meta.tier == 1  # Official VA program
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "va.gov" in meta.url

    def test_format_date_range_single_day(self, tmp_path):
        """Test date formatting for single-day event."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        result = connector._format_date_range("2026-01-21", "2026-01-21")
        assert result == "January 21, 2026"

    def test_format_date_range_same_month(self, tmp_path):
        """Test date formatting for multi-day event in same month."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        result = connector._format_date_range("2026-01-23", "2026-01-24")
        assert result == "January 23-24, 2026"

    def test_format_date_range_different_months(self, tmp_path):
        """Test date formatting for event spanning months."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        result = connector._format_date_range("2026-03-30", "2026-04-01")
        assert result == "March 30 - April 01, 2026"

    def test_format_date_range_different_years(self, tmp_path):
        """Test date formatting for event spanning years."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        result = connector._format_date_range("2025-12-30", "2026-01-02")
        assert result == "December 30, 2025 - January 02, 2026"

    def test_build_title_with_full_info(self, tmp_path):
        """Test title building with all info."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        title = connector._build_title(
            name="Phoenix Stand Down",
            start_date="2026-03-12",
            end_date="2026-03-13",
            city="Phoenix",
            state="AZ",
        )
        assert title == "Phoenix Stand Down - March 12-13, 2026 (Phoenix, AZ)"

    def test_build_title_single_day(self, tmp_path):
        """Test title building for single-day event."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        title = connector._build_title(
            name="Orland Stand Down",
            start_date="2026-01-21",
            end_date="2026-01-21",
            city="Orland",
            state="CA",
        )
        assert title == "Orland Stand Down - January 21, 2026 (Orland, CA)"

    def test_build_title_minimal(self, tmp_path):
        """Test title building with minimal info."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        title = connector._build_title(
            name="Test Stand Down",
            start_date="2026-05-01",
            end_date="2026-05-01",
            city=None,
            state=None,
        )
        assert title == "Test Stand Down - May 01, 2026"

    def test_get_categories_with_services(self, tmp_path):
        """Test category extraction from services."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")

        # Housing is always included
        categories = connector._get_categories([])
        assert "housing" in categories

        # Employment and legal added based on services
        categories = connector._get_categories(["housing", "employment", "legal", "dental"])
        assert "housing" in categories
        assert "employment" in categories
        assert "legal" in categories

    def test_build_tags(self, tmp_path):
        """Test tag building."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        tags = connector._build_tags(
            services=["health-screening", "dental", "housing", "legal"],
            state="AZ",
        )

        assert "stand-down" in tags
        assert "outreach-event" in tags
        assert "homeless-services" in tags
        assert "veteran-event" in tags
        assert "health-screening" in tags
        assert "dental" in tags
        assert "housing" in tags
        assert "legal" in tags
        assert "state-az" in tags

    def test_build_tags_no_state(self, tmp_path):
        """Test tag building without state."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        tags = connector._build_tags(services=["food", "clothing"], state=None)

        assert "stand-down" in tags
        assert "food" in tags
        assert "clothing" in tags
        assert not any(t.startswith("state-") for t in tags)

    def test_build_description(self, tmp_path):
        """Test description building."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        event = {
            "name": "Phoenix Stand Down",
            "start_date": "2026-03-12",
            "end_date": "2026-03-13",
            "city": "Phoenix",
            "state": "AZ",
            "address": "Human Services Campus, 1201 S 7th Ave",
            "zip_code": "85007",
            "services": ["health-screening", "dental", "housing", "employment"],
            "description": "Two-day comprehensive Stand Down event.",
        }

        desc = connector._build_description(event)

        # Check date is in description
        assert "March 12-13, 2026" in desc
        # Check location
        assert "Phoenix" in desc
        assert "Arizona" in desc
        # Check services
        assert "Health Screening" in desc
        assert "Dental Care" in desc
        assert "Housing Assistance" in desc
        assert "Employment Services" in desc
        # Check address
        assert "Human Services Campus" in desc
        # Check custom description
        assert "Two-day comprehensive Stand Down event" in desc

    def test_build_eligibility(self, tmp_path):
        """Test eligibility text."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        eligibility = connector._build_eligibility()

        assert "All veterans are welcome" in eligibility
        assert "discharge status" in eligibility
        assert "homeless" in eligibility.lower()

    def test_build_how_to_apply(self, tmp_path):
        """Test how to apply text."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        event = {
            "name": "Phoenix Stand Down",
            "start_date": "2026-03-12",
            "end_date": "2026-03-13",
            "city": "Phoenix",
            "state": "AZ",
            "address": "Human Services Campus",
            "organizer_name": "Dawn Henry",
            "organizer_phone": "(602) 340-9393",
        }

        how_to = connector._build_how_to_apply(event)

        assert "March 12-13, 2026" in how_to
        assert "Human Services Campus" in how_to
        assert "Dawn Henry" in how_to
        assert "(602) 340-9393" in how_to
        assert "No appointment" in how_to
        assert "DD-214" in how_to

    def test_build_how_to_apply_minimal(self, tmp_path):
        """Test how to apply with minimal info."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        event = {
            "start_date": "2026-05-01",
        }

        how_to = connector._build_how_to_apply(event)

        assert "May 01, 2026" in how_to
        assert "No appointment" in how_to

    def test_parse_event_full(self, tmp_path):
        """Test parsing a complete event entry."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        now = datetime.now(UTC)

        event = {
            "event_id": "phoenix-az-2026-03-12",
            "name": "Phoenix Stand Down",
            "start_date": "2026-03-12",
            "end_date": "2026-03-13",
            "city": "Phoenix",
            "state": "AZ",
            "address": "Human Services Campus, 1201 S 7th Ave",
            "zip_code": "85007",
            "services": ["health-screening", "dental", "housing", "employment", "legal"],
            "organizer_name": "Dawn Henry",
            "organizer_phone": "(602) 340-9393",
            "description": "Two-day comprehensive Stand Down event.",
            "source_url": "https://www.va.gov/homeless/events.asp",
        }

        candidate = connector._parse_event(event, fetched_at=now)

        assert candidate is not None
        assert "Phoenix Stand Down" in candidate.title
        assert "March 12-13, 2026" in candidate.title
        assert "(Phoenix, AZ)" in candidate.title
        assert candidate.city == "Phoenix"
        assert candidate.state == "AZ"
        assert candidate.zip_code == "85007"
        assert candidate.scope == "local"
        assert candidate.states == ["AZ"]
        assert "housing" in candidate.categories
        assert "employment" in candidate.categories
        assert "legal" in candidate.categories
        assert "stand-down" in candidate.tags
        assert "dental" in candidate.tags
        assert "state-az" in candidate.tags
        assert candidate.phone == "(602) 340-9393"
        assert candidate.org_name == "Dawn Henry"

    def test_parse_event_minimal(self, tmp_path):
        """Test parsing an event with minimal data."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        now = datetime.now(UTC)

        event = {
            "name": "Test Stand Down",
            "start_date": "2026-05-01",
        }

        candidate = connector._parse_event(event, fetched_at=now)

        assert candidate is not None
        assert "Test Stand Down" in candidate.title
        assert "May 01, 2026" in candidate.title
        assert candidate.scope == "local"
        assert "housing" in candidate.categories
        assert "stand-down" in candidate.tags

    def test_parse_event_missing_required(self, tmp_path):
        """Test parsing returns None for missing required fields."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        now = datetime.now(UTC)

        # Missing name
        assert connector._parse_event({"start_date": "2026-05-01"}, fetched_at=now) is None
        # Missing start_date
        assert connector._parse_event({"name": "Test"}, fetched_at=now) is None
        # Empty
        assert connector._parse_event({}, fetched_at=now) is None

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = StandDownEventsConnector(data_path=tmp_path / "nonexistent.json")
        resources = connector.run()
        assert resources == []

    def test_run_with_data(self, tmp_path):
        """Test that run() parses JSON correctly."""
        data = {
            "metadata": {"source": "test"},
            "events": [
                {
                    "event_id": "test-1",
                    "name": "Test Stand Down 1",
                    "start_date": "2026-01-21",
                    "end_date": "2026-01-21",
                    "city": "Orland",
                    "state": "CA",
                    "services": ["health-screening", "housing"],
                },
                {
                    "event_id": "test-2",
                    "name": "Test Stand Down 2",
                    "start_date": "2026-03-12",
                    "end_date": "2026-03-13",
                    "city": "Phoenix",
                    "state": "AZ",
                    "services": ["dental", "legal", "employment"],
                },
            ],
        }

        data_file = tmp_path / "events.json"
        data_file.write_text(json.dumps(data))

        connector = StandDownEventsConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 2

        # First event
        assert "Test Stand Down 1" in resources[0].title
        assert "January 21, 2026" in resources[0].title
        assert resources[0].state == "CA"
        assert "housing" in resources[0].categories

        # Second event
        assert "Test Stand Down 2" in resources[1].title
        assert "March 12-13, 2026" in resources[1].title
        assert resources[1].state == "AZ"
        assert "employment" in resources[1].categories
        assert "legal" in resources[1].categories

    def test_run_with_real_data(self):
        """Test run() with the actual Stand Down events data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "stand_down_events.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("stand_down_events.json not found in project")

        connector = StandDownEventsConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least 5 events
        assert len(resources) >= 5

        # All should have housing category (Stand Downs serve homeless veterans)
        assert all("housing" in r.categories for r in resources)

        # All should have stand-down tag
        assert all("stand-down" in r.tags for r in resources)

        # All should have local scope
        assert all(r.scope == "local" for r in resources)

        # Check date is in every title
        for r in resources:
            # Date should be in title (format includes year)
            assert "202" in r.title  # Year 2020s

        # Check structure of first resource
        first = resources[0]
        assert first.title  # Has title
        assert first.description  # Has description
        assert "va.gov" in first.source_url or "standdown" in first.source_url.lower()
        assert first.eligibility is not None
        assert first.how_to_apply is not None

        # Verify states coverage
        states = {r.state for r in resources if r.state}
        assert len(states) >= 5  # At least 5 different states

    def test_services_mapping(self, tmp_path):
        """Test that services are correctly mapped to tags and categories."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")
        now = datetime.now(UTC)

        event = {
            "name": "Full Service Stand Down",
            "start_date": "2026-06-01",
            "services": [
                "health-screening",
                "dental",
                "housing",
                "employment",
                "legal",
                "benefits",
                "clothing",
                "food",
                "mental-health",
                "substance-use",
            ],
        }

        candidate = connector._parse_event(event, fetched_at=now)

        # Check all services are in tags
        assert "health-screening" in candidate.tags
        assert "dental" in candidate.tags
        assert "housing" in candidate.tags
        assert "employment" in candidate.tags
        assert "legal" in candidate.tags
        assert "benefits" in candidate.tags
        assert "clothing" in candidate.tags
        assert "food" in candidate.tags
        assert "mental-health" in candidate.tags
        assert "substance-use" in candidate.tags

        # Check categories
        assert "housing" in candidate.categories
        assert "employment" in candidate.categories
        assert "legal" in candidate.categories

        # Check services are in description
        assert "Health Screening" in candidate.description
        assert "Dental Care" in candidate.description
        assert "Mental Health Services" in candidate.description

    def test_phone_normalization(self, tmp_path):
        """Test phone number normalization."""
        connector = StandDownEventsConnector(data_path=tmp_path / "events.json")

        # Standard format should be preserved
        assert connector._normalize_phone("(602) 340-9393") == "(602) 340-9393"
        # 10 digits should be formatted
        assert connector._normalize_phone("6023409393") == "(602) 340-9393"
        # 11 digits with leading 1
        assert connector._normalize_phone("16023409393") == "(602) 340-9393"
        # None
        assert connector._normalize_phone(None) is None
