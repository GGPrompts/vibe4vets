"""Tests for Feeding America Food Bank Network connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.feeding_america import FeedingAmericaConnector


class TestFeedingAmericaConnector:
    """Tests for FeedingAmericaConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )
        meta = connector.metadata

        assert meta.name == "Feeding America Food Bank Network"
        assert meta.tier == 2  # Major national nonprofit network
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "feedingamerica.org" in meta.url

    def test_extract_state_from_state_name(self, tmp_path):
        """Test state extraction from state names."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        # Test full state names
        assert connector._extract_state("Arkansas Foodbank", "") == "AR"
        assert connector._extract_state("Montana Food Bank Network", "") == "MT"
        assert connector._extract_state("", "connecticut-food-bank") == "CT"

    def test_extract_state_from_city(self, tmp_path):
        """Test state extraction from city names."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        # Test city names
        assert connector._extract_state("Greater Chicago Food Depository", "") == "IL"
        assert connector._extract_state("Atlanta Community Food Bank", "") == "GA"
        assert connector._extract_state("Houston Food Bank", "") == "TX"

    def test_extract_state_from_region(self, tmp_path):
        """Test state extraction from regional names."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        # Test regional names (use space-separated names, not slug format)
        assert connector._extract_state("Silicon Valley Food Bank", "") == "CA"
        assert connector._extract_state("Mahoning Valley Food Bank", "") == "OH"
        assert connector._extract_state("Food Bank of the Heartland", "") == "NE"

    def test_extract_state_none(self, tmp_path):
        """Test state extraction returns None for unknown names."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        # Unknown names should return None
        assert connector._extract_state("Unknown Food Bank", "unknown-slug") is None

    def test_build_description(self, tmp_path):
        """Test description building."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        desc = connector._build_description(
            name="Test Food Bank",
            state="TX",
            counties=["Travis", "Williamson", "Hays"],
            service_area=None,
        )

        assert "Test Food Bank" in desc
        assert "Feeding America" in desc
        assert "Travis" in desc
        assert "Williamson" in desc
        assert "Veterans" in desc

    def test_build_description_with_service_area(self, tmp_path):
        """Test description building with service area."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        desc = connector._build_description(
            name="Test Food Bank",
            state="CA",
            counties=[],
            service_area="Northern California",
        )

        assert "Northern California" in desc

    def test_build_description_state_only(self, tmp_path):
        """Test description building with just state."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        desc = connector._build_description(
            name="Test Food Bank",
            state="NY",
            counties=[],
            service_area=None,
        )

        assert "NY" in desc

    def test_build_eligibility(self, tmp_path):
        """Test eligibility building."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        eligibility = connector._build_eligibility()

        assert "anyone in need" in eligibility.lower()
        assert "Veteran" in eligibility
        assert "military" in eligibility.lower()

    def test_build_how_to_apply_with_website(self, tmp_path):
        """Test how to apply building with website."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        how_to_apply = connector._build_how_to_apply(
            name="Test Food Bank",
            website="https://testfoodbank.org",
            phone="555-123-4567",
            slug="test-food-bank",
        )

        assert "testfoodbank.org" in how_to_apply
        assert "555-123-4567" in how_to_apply
        assert "211" in how_to_apply

    def test_build_how_to_apply_without_website(self, tmp_path):
        """Test how to apply building without website."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        how_to_apply = connector._build_how_to_apply(
            name="Test Food Bank",
            website=None,
            phone=None,
            slug="test-food-bank",
        )

        assert "feedingamerica.org" in how_to_apply
        assert "test-food-bank" in how_to_apply
        assert "211" in how_to_apply

    def test_build_tags(self, tmp_path):
        """Test tag building."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        tags = connector._build_tags(
            name="Second Harvest Community Food Bank",
            state="CA",
            counties=["Stanislaus", "San Joaquin"],
        )

        assert "food-bank" in tags
        assert "food-assistance" in tags
        assert "feeding-america" in tags
        assert "state-ca" in tags
        assert "second-harvest" in tags
        assert "community-food-bank" in tags

    def test_build_tags_regional(self, tmp_path):
        """Test tag building for regional food banks."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        tags = connector._build_tags(
            name="North Texas Regional Food Bank",
            state="TX",
            counties=[],
        )

        assert "regional-food-bank" in tags
        assert "state-tx" in tags

    def test_parse_food_bank(self, tmp_path):
        """Test parsing a single food bank entry."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )
        now = datetime.now(UTC)

        food_bank = {
            "name": "Central Texas Food Bank",
            "slug": "central-texas-food-bank",
            "state": "TX",
            "website": "https://centraltexasfoodbank.org",
            "phone": "512-555-1234",
            "email": "info@ctfb.org",
            "address": "6500 Metropolis Drive",
            "city": "Austin",
            "zip_code": "78744",
            "counties": ["Travis", "Williamson", "Hays"],
            "service_area": "Central Texas",
        }

        candidate = connector._parse_food_bank(food_bank, fetched_at=now)

        assert candidate.title == "Feeding America - Central Texas Food Bank"
        assert "Feeding America" in candidate.description
        assert candidate.org_name == "Central Texas Food Bank"
        assert candidate.org_website == "https://centraltexasfoodbank.org"
        assert candidate.address == "6500 Metropolis Drive"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78744"
        assert candidate.categories == ["food"]
        assert candidate.scope == "regional"
        assert candidate.states == ["TX"]
        assert "food-bank" in candidate.tags
        assert "feeding-america" in candidate.tags
        assert candidate.phone == "(512) 555-1234"
        assert candidate.raw_data["network"] == "Feeding America"

    def test_parse_food_bank_state_extraction(self, tmp_path):
        """Test that state is extracted when not provided."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )
        now = datetime.now(UTC)

        food_bank = {
            "name": "Greater Chicago Food Depository",
            "slug": "greater-chicago-food-depository",
            "state": None,  # Not provided
            "website": None,
            "phone": None,
            "email": None,
            "address": None,
            "city": None,
            "zip_code": None,
            "counties": [],
            "service_area": None,
        }

        candidate = connector._parse_food_bank(food_bank, fetched_at=now)

        # Should extract IL from "Chicago"
        assert candidate.state == "IL"
        assert candidate.states == ["IL"]

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "nonexistent.json",
        )

        resources = connector.run()
        assert resources == []

    def test_run_empty_data(self, tmp_path):
        """Test that run() handles empty data."""
        data = {"food_banks": []}

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = FeedingAmericaConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_with_food_banks(self, tmp_path):
        """Test that run() parses food banks correctly."""
        data = {
            "source": "Feeding America",
            "food_banks": [
                {
                    "name": "Test Food Bank 1",
                    "slug": "test-food-bank-1",
                    "state": "TX",
                    "website": "https://example1.com",
                    "phone": "555-111-1111",
                    "email": None,
                    "address": "100 First St",
                    "city": "Austin",
                    "zip_code": "78701",
                    "counties": ["Travis"],
                    "service_area": None,
                },
                {
                    "name": "Test Food Bank 2",
                    "slug": "test-food-bank-2",
                    "state": "CO",
                    "website": "https://example2.com",
                    "phone": "555-222-2222",
                    "email": "test@example.com",
                    "address": "200 Second Ave",
                    "city": "Denver",
                    "zip_code": "80201",
                    "counties": ["Denver", "Adams"],
                    "service_area": "Metro Denver",
                },
            ],
        }

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = FeedingAmericaConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Feeding America - Test Food Bank 1"
        assert resources[0].org_name == "Test Food Bank 1"
        assert resources[0].city == "Austin"
        assert resources[0].state == "TX"
        assert resources[0].categories == ["food"]
        assert resources[0].scope == "regional"

        # Second resource
        assert resources[1].title == "Feeding America - Test Food Bank 2"
        assert resources[1].org_name == "Test Food Bank 2"
        assert resources[1].city == "Denver"
        assert resources[1].state == "CO"
        assert resources[1].email == "test@example.com"

    def test_run_with_real_data(self):
        """Test run() with the actual data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "feeding_america_foodbanks.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("feeding_america_foodbanks.json not found in project")

        connector = FeedingAmericaConnector(data_path=data_file)
        resources = connector.run()

        # Should have around 199 food banks
        assert len(resources) >= 190

        # All should have food category
        assert all("food" in r.categories for r in resources)

        # All should have regional scope
        assert all(r.scope == "regional" for r in resources)

        # All should have feeding-america tag
        assert all("feeding-america" in r.tags for r in resources)

        # Check that state coverage is good (should cover all 50 states + DC + PR)
        states = set(r.state for r in resources if r.state)
        assert len(states) >= 50  # At least 50 states

        # Check first resource structure
        first = resources[0]
        assert first.title
        assert first.description
        assert first.org_name
        assert first.source_url
        assert "feedingamerica.org" in first.source_url
        assert first.eligibility
        assert first.how_to_apply
        assert first.tags
        assert first.raw_data is not None

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps({"food_banks": []}))

        with FeedingAmericaConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_phone_normalization(self, tmp_path):
        """Test that phone numbers are normalized."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )

        # Test 10-digit
        assert connector._normalize_phone("5125551234") == "(512) 555-1234"

        # Test 11-digit with leading 1
        assert connector._normalize_phone("15125551234") == "(512) 555-1234"

        # Test formatted input
        assert connector._normalize_phone("512-555-1234") == "(512) 555-1234"

        # Test None
        assert connector._normalize_phone(None) is None

    def test_source_url_generation(self, tmp_path):
        """Test that source URLs are generated correctly."""
        connector = FeedingAmericaConnector(
            data_path=tmp_path / "data.json",
        )
        now = datetime.now(UTC)

        food_bank = {
            "name": "Test Food Bank",
            "slug": "test-food-bank",
            "state": "TX",
            "website": None,
            "phone": None,
            "email": None,
            "address": None,
            "city": None,
            "zip_code": None,
            "counties": [],
            "service_area": None,
        }

        candidate = connector._parse_food_bank(food_bank, fetched_at=now)

        expected_url = "https://www.feedingamerica.org/find-your-local-foodbank/test-food-bank"
        assert candidate.source_url == expected_url

    def test_all_states_covered(self):
        """Test that most states have at least one food bank."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "feeding_america_foodbanks.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("feeding_america_foodbanks.json not found in project")

        connector = FeedingAmericaConnector(data_path=data_file)
        resources = connector.run()

        states = set(r.state for r in resources if r.state)

        # At least 49 states should be covered (Wyoming is served by regional
        # food banks like Food Bank of the Rockies but doesn't have its own)
        assert len(states) >= 49, f"Only {len(states)} states covered"

        # Verify key states are present
        key_states = {"CA", "TX", "NY", "FL", "PA", "OH", "IL", "GA", "NC"}
        for state in key_states:
            assert state in states, f"{state} not covered"

    def test_special_territories_covered(self):
        """Test that DC and PR are covered."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "feeding_america_foodbanks.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("feeding_america_foodbanks.json not found in project")

        connector = FeedingAmericaConnector(data_path=data_file)
        resources = connector.run()

        states = set(r.state for r in resources if r.state)

        # DC and PR should be included
        assert "DC" in states, "DC not covered"
        assert "PR" in states, "Puerto Rico not covered"
