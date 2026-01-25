"""Tests for 211 National Resource Database connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.two_one_one import TwoOneOneConnector


@pytest.fixture
def sample_resource_data():
    """Sample resource data matching CA.json format."""
    return {
        "state": "CA",
        "state_name": "California",
        "fetched_at": "2026-01-25T00:00:00Z",
        "source": "211.org",
        "resources": [
            {
                "name": "Test Veterans Center",
                "phone": "1-800-555-1234",
                "phone_alt": "(555) 987-6543",
                "address": "123 Main Street",
                "city": "Los Angeles",
                "zip_code": "90001",
                "email": "info@testcenter.org",
                "description": "Comprehensive veteran services including housing and mental health support",
                "services": ["housing assistance", "mental health", "employment services", "benefits assistance"],
                "website": "https://testcenter.org",
                "source_url": "https://211.org/services/test",
                "hours": "Mon-Fri 9am-5pm",
            },
            {
                "name": "Veterans Crisis Support",
                "phone": "988",
                "description": "24/7 crisis support",
                "services": ["crisis support", "PTSD support", "suicide prevention"],
                "website": "https://crisis.va.gov",
                "source_url": "https://crisis.va.gov",
            },
            {
                "name": "Food Bank for Veterans",
                "phone": "310-555-7890",
                "address": "456 Oak Ave",
                "city": "San Diego",
                "description": "Food assistance program",
                "services": ["food pantry", "meals"],
                "website": "https://foodbank.org",
            },
        ],
    }


@pytest.fixture
def test_data_dir(tmp_path, sample_resource_data):
    """Create test data directory with sample files."""
    data_dir = tmp_path / "test_211_data"
    data_dir.mkdir()

    # Write CA.json
    ca_file = data_dir / "CA.json"
    with open(ca_file, "w") as f:
        json.dump(sample_resource_data, f)

    # Write TX.json with different data
    tx_data = {
        "state": "TX",
        "state_name": "Texas",
        "fetched_at": "2026-01-24T00:00:00Z",
        "resources": [
            {
                "name": "Texas Veterans Housing",
                "phone": "512-555-0000",
                "city": "Austin",
                "description": "Housing services",
                "services": ["housing", "rental assistance"],
                "website": "https://txvet.org",
            }
        ],
    }
    tx_file = data_dir / "TX.json"
    with open(tx_file, "w") as f:
        json.dump(tx_data, f)

    return data_dir


@pytest.fixture
def connector(test_data_dir):
    """Create connector instance with test data."""
    return TwoOneOneConnector(data_dir=test_data_dir, states=["CA", "TX"])


class TestTwoOneOneConnector:
    """Tests for TwoOneOneConnector."""

    def test_metadata(self, connector):
        """Test connector metadata."""
        meta = connector.metadata

        assert meta.name == "211 National Resource Database"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "211.org" in meta.url

    def test_init_default_states(self):
        """Test initialization with default states."""
        connector = TwoOneOneConnector(data_dir="/fake/path")
        assert connector.states == TwoOneOneConnector.AVAILABLE_STATES
        assert len(connector.states) > 10  # Should have multiple states

    def test_init_custom_states(self, test_data_dir):
        """Test initialization with custom states list."""
        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["CA"])
        assert connector.states == ["CA"]

    def test_init_string_path(self, test_data_dir):
        """Test initialization with string path."""
        connector = TwoOneOneConnector(data_dir=str(test_data_dir))
        assert connector.data_dir == Path(test_data_dir)

    def test_load_resources(self, connector):
        """Test run() returns ResourceCandidate list."""
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 4  # 3 from CA + 1 from TX

        # Check first resource
        r = resources[0]
        assert r.title == "Test Veterans Center"
        assert r.org_name == "Test Veterans Center"
        assert "housing and mental health" in r.description
        assert r.state == "CA"
        assert r.city == "Los Angeles"
        assert r.zip_code == "90001"
        assert r.address == "123 Main Street"
        assert r.email == "info@testcenter.org"
        assert r.hours == "Mon-Fri 9am-5pm"
        assert r.phone == "(800) 555-1234"  # Normalized
        assert r.org_website == "https://testcenter.org"
        assert r.source_url == "https://211.org/services/test"
        assert r.scope == "state"
        assert r.states == ["CA"]

    def test_category_mapping(self, connector):
        """Test SERVICE_CATEGORY_MAP correctly maps services."""
        resources = connector.run()

        # Test Veterans Center has multiple categories
        test_center = [r for r in resources if r.title == "Test Veterans Center"][0]
        assert "housing" in test_center.categories
        assert "mental_health" in test_center.categories
        assert "employment" in test_center.categories
        assert "benefits" in test_center.categories

        # Test Crisis Support has mental health categories
        crisis = [r for r in resources if "Crisis" in r.title][0]
        assert "mental_health" in crisis.categories

        # Test Food Bank has food category
        food_bank = [r for r in resources if "Food Bank" in r.title][0]
        assert "food" in food_bank.categories

    def test_category_mapping_partial_match(self):
        """Test category mapping with partial matching."""
        connector = TwoOneOneConnector(data_dir="/fake")

        # Test exact match
        categories = connector._map_categories(["housing assistance"])
        assert "housing" in categories

        # Test partial match
        categories = connector._map_categories(["veterans employment support"])
        assert "employment" in categories

        # Test multiple services
        categories = connector._map_categories(["mental health services", "job training", "food pantry"])
        assert "mental_health" in categories
        assert "employment" in categories
        assert "food" in categories

        # Test unknown service falls back to veteran_services
        categories = connector._map_categories(["unknown service"])
        assert len(categories) == 0  # Unknown services return empty

    def test_phone_normalization(self, connector):
        """Test various phone formats are normalized correctly."""
        # Test via base class method
        assert connector._normalize_phone("1-800-555-1234") == "(800) 555-1234"
        assert connector._normalize_phone("(555) 987-6543") == "(555) 987-6543"
        assert connector._normalize_phone("310-555-7890") == "(310) 555-7890"
        assert connector._normalize_phone("988") == "988"  # Short number preserved
        assert connector._normalize_phone("1.800.555.1234") == "(800) 555-1234"
        assert connector._normalize_phone("800 555 1234") == "(800) 555-1234"
        assert connector._normalize_phone("18005551234") == "(800) 555-1234"
        assert connector._normalize_phone("5551234567") == "(555) 123-4567"
        assert connector._normalize_phone(None) is None
        assert connector._normalize_phone("") is None

    def test_phone_normalization_in_resources(self, connector):
        """Test phone normalization is applied to resources."""
        resources = connector.run()

        # Check that phones are normalized in actual resources
        test_center = [r for r in resources if r.title == "Test Veterans Center"][0]
        assert test_center.phone == "(800) 555-1234"

        # Check alt phone is stored in raw_data
        assert "phone_alt_normalized" in test_center.raw_data
        assert test_center.raw_data["phone_alt_normalized"] == "(555) 987-6543"

    def test_get_resources_by_state(self, connector):
        """Test filter by state works."""
        # First load resources
        connector.run()

        ca_resources = connector.get_resources_by_state("CA")
        assert len(ca_resources) == 3
        assert all(r.state == "CA" for r in ca_resources)

        tx_resources = connector.get_resources_by_state("TX")
        assert len(tx_resources) == 1
        assert tx_resources[0].state == "TX"
        assert tx_resources[0].title == "Texas Veterans Housing"

        # Test non-existent state
        fl_resources = connector.get_resources_by_state("FL")
        assert len(fl_resources) == 0

    def test_get_resources_by_state_auto_run(self, connector):
        """Test get_resources_by_state auto-runs if not loaded."""
        # Don't call run() first
        ca_resources = connector.get_resources_by_state("CA")
        assert len(ca_resources) == 3  # Should auto-load

    def test_get_resources_by_category(self, connector):
        """Test filter by category works."""
        connector.run()

        housing = connector.get_resources_by_category("housing")
        assert len(housing) == 2  # Test Veterans Center + Texas Veterans Housing

        mental_health = connector.get_resources_by_category("mental_health")
        assert len(mental_health) == 2  # Test Veterans Center + Crisis Support

        food = connector.get_resources_by_category("food")
        assert len(food) == 1
        assert "Food Bank" in food[0].title

        # Test non-existent category
        legal = connector.get_resources_by_category("legal")
        assert len(legal) == 0

    def test_get_resources_by_category_auto_run(self, connector):
        """Test get_resources_by_category auto-runs if not loaded."""
        # Don't call run() first
        housing = connector.get_resources_by_category("housing")
        assert len(housing) > 0  # Should auto-load

    def test_stats(self, connector):
        """Test stats output structure."""
        stats = connector.stats()

        assert "total_resources" in stats
        assert stats["total_resources"] == 4

        assert "states_covered" in stats
        assert stats["states_covered"] == 2

        assert "by_state" in stats
        assert stats["by_state"]["CA"] == 3
        assert stats["by_state"]["TX"] == 1

        assert "by_category" in stats
        assert stats["by_category"]["housing"] == 2
        assert stats["by_category"]["mental_health"] == 2
        assert stats["by_category"]["food"] == 1

        # Verify categories are sorted by count (descending)
        category_counts = list(stats["by_category"].values())
        assert category_counts == sorted(category_counts, reverse=True)

    def test_stats_auto_run(self, connector):
        """Test stats auto-runs if not loaded."""
        # Don't call run() first
        stats = connector.stats()
        assert stats["total_resources"] == 4  # Should auto-load

    def test_missing_file_handling(self, test_data_dir):
        """Test graceful handling of missing state files."""
        # Request states that don't exist in test data
        connector = TwoOneOneConnector(
            data_dir=test_data_dir,
            states=["CA", "FL", "NY"],  # Only CA exists
        )

        resources = connector.run()

        # Should only load CA resources without error
        assert len(resources) == 3
        assert all(r.state == "CA" for r in resources)

    def test_malformed_json(self, test_data_dir):
        """Test graceful handling of bad JSON."""
        # Create a malformed JSON file
        bad_file = test_data_dir / "FL.json"
        with open(bad_file, "w") as f:
            f.write("{invalid json content")

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["CA", "FL"])

        # Should load CA successfully and skip FL
        resources = connector.run()
        assert len(resources) == 3  # Only CA resources
        assert all(r.state == "CA" for r in resources)

    def test_empty_json_file(self, test_data_dir):
        """Test handling of empty/minimal JSON file."""
        # Create file with no resources
        empty_file = test_data_dir / "NY.json"
        with open(empty_file, "w") as f:
            json.dump({"state": "NY", "resources": []}, f)

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["NY"])

        resources = connector.run()
        assert len(resources) == 0

    def test_missing_name_skipped(self, test_data_dir):
        """Test resources without names are skipped."""
        data = {
            "state": "AZ",
            "resources": [
                {"name": "", "services": ["housing"]},  # Empty name
                {"services": ["food"]},  # Missing name
                {"name": "Valid Resource", "services": ["mental health"]},
            ],
        }

        az_file = test_data_dir / "AZ.json"
        with open(az_file, "w") as f:
            json.dump(data, f)

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["AZ"])
        resources = connector.run()

        # Only valid resource should be loaded
        assert len(resources) == 1
        assert resources[0].title == "Valid Resource"

    def test_tags_preserved(self, connector):
        """Test original service tags are preserved."""
        resources = connector.run()

        test_center = [r for r in resources if r.title == "Test Veterans Center"][0]
        assert test_center.tags == ["housing assistance", "mental health", "employment services", "benefits assistance"]

    def test_fetched_at_timestamp(self, connector):
        """Test fetched_at timestamp is parsed correctly."""
        resources = connector.run()

        # CA resources should have 2026-01-25 timestamp
        ca_resource = [r for r in resources if r.state == "CA"][0]
        assert ca_resource.fetched_at is not None
        assert ca_resource.fetched_at.year == 2026
        assert ca_resource.fetched_at.month == 1
        assert ca_resource.fetched_at.day == 25

    def test_parse_timestamp_formats(self):
        """Test various timestamp formats are handled."""
        connector = TwoOneOneConnector(data_dir="/fake")

        # ISO format with Z
        ts1 = connector._parse_timestamp("2026-01-25T00:00:00Z")
        assert ts1.year == 2026

        # ISO format with timezone
        ts2 = connector._parse_timestamp("2026-01-25T00:00:00+00:00")
        assert ts2.year == 2026

        # None
        ts3 = connector._parse_timestamp(None)
        assert ts3 is None

        # Invalid format falls back to current time
        ts4 = connector._parse_timestamp("invalid")
        assert ts4.year == datetime.now(UTC).year

    def test_default_description(self, test_data_dir):
        """Test description fallback when not provided."""
        data = {
            "state": "AZ",
            "resources": [
                {
                    "name": "Test Org",
                    "services": ["housing", "food", "employment"],
                    # No description field
                }
            ],
        }

        az_file = test_data_dir / "AZ.json"
        with open(az_file, "w") as f:
            json.dump(data, f)

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["AZ"])
        resources = connector.run()

        assert len(resources) == 1
        assert "Services: housing, food, employment" in resources[0].description

    def test_fallback_to_veteran_services_category(self, test_data_dir):
        """Test resources with no mapped categories get veteran_services."""
        data = {
            "state": "AZ",
            "resources": [{"name": "Test Org", "services": ["unknown service type", "another unknown"]}],
        }

        az_file = test_data_dir / "AZ.json"
        with open(az_file, "w") as f:
            json.dump(data, f)

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["AZ"])
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].categories == ["veteran_services"]

    def test_context_manager(self, connector):
        """Test connector works as context manager."""
        with connector as c:
            resources = c.run()
            assert len(resources) > 0

        # close() should work without error
        connector.close()

    def test_resource_raw_data_preserved(self, connector):
        """Test raw_data field preserves original resource data."""
        resources = connector.run()

        test_center = [r for r in resources if r.title == "Test Veterans Center"][0]

        assert test_center.raw_data is not None
        assert test_center.raw_data["name"] == "Test Veterans Center"
        assert test_center.raw_data["phone"] == "1-800-555-1234"
        assert "phone_alt_normalized" in test_center.raw_data
        assert test_center.raw_data["services"] == [
            "housing assistance",
            "mental health",
            "employment services",
            "benefits assistance",
        ]

    def test_source_url_fallback(self, test_data_dir):
        """Test source_url falls back to website if not provided."""
        data = {
            "state": "AZ",
            "resources": [
                {
                    "name": "Test Org",
                    "website": "https://example.org",
                    # No source_url
                    "services": ["housing"],
                }
            ],
        }

        az_file = test_data_dir / "AZ.json"
        with open(az_file, "w") as f:
            json.dump(data, f)

        connector = TwoOneOneConnector(data_dir=test_data_dir, states=["AZ"])
        resources = connector.run()

        assert resources[0].source_url == "https://example.org"

    def test_multiple_runs_clear_previous(self, connector):
        """Test calling run() multiple times clears previous resources."""
        resources1 = connector.run()
        count1 = len(resources1)

        # Run again
        resources2 = connector.run()
        count2 = len(resources2)

        # Should be same count, not doubled
        assert count1 == count2
        assert count1 == 4

    def test_service_category_map_coverage(self):
        """Test SERVICE_CATEGORY_MAP has expected coverage."""
        map_dict = TwoOneOneConnector.SERVICE_CATEGORY_MAP

        # Verify key categories are present
        assert "housing" in map_dict
        assert "mental health" in map_dict
        assert "employment" in map_dict
        assert "food" in map_dict
        assert "benefits" in map_dict
        assert "legal" in map_dict
        assert "healthcare" in map_dict

        # Verify veteran-specific terms
        assert "HUD-VASH" in map_dict
        assert map_dict["HUD-VASH"] == "housing"
        assert "SSVF" in map_dict
        assert map_dict["SSVF"] == "housing"
        assert "PTSD" in map_dict
        assert map_dict["PTSD"] == "mental_health"
        assert "GI Bill" in map_dict
        assert map_dict["GI Bill"] == "education"
