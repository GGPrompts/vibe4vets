"""Tests for Rural Telehealth connector."""

import json
from pathlib import Path

import pytest

from connectors.rural_telehealth import RuralTelehealthConnector


class TestRuralTelehealthConnector:
    """Tests for RuralTelehealthConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "telehealth.json")
        meta = connector.metadata

        assert "Rural" in meta.name or "Telehealth" in meta.name
        assert meta.tier == 1
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "ruralhealth.va.gov" in meta.url

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "nonexistent.json")

        resources = connector.run()
        assert resources == []

    def test_run_empty_programs(self, tmp_path):
        """Test that run() handles empty programs list."""
        data = {"metadata": {"source": "test"}, "programs": []}
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_parses_va_program(self, tmp_path):
        """Test parsing a VA telehealth program."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "id": "va-atlas",
                    "name": "VA ATLAS Telehealth",
                    "org_name": "U.S. Department of Veterans Affairs",
                    "description": "ATLAS provides Veterans in rural areas access to telehealth.",
                    "tier": 1,
                    "website": "https://www.va.gov/health/atlas/",
                    "phone": "1-800-698-2411",
                    "scope": "national",
                    "categories": ["healthcare"],
                    "tags": ["telehealth", "rural", "va", "atlas"],
                    "eligibility": {
                        "summary": "Veterans enrolled in VA health care",
                        "va_enrollment_required": True,
                    },
                    "services": ["Primary care", "Mental health", "Specialty care"],
                    "access_method": "Contact your local VA to schedule.",
                }
            ],
        }
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "ATLAS" in resource.title
        assert resource.org_name == "U.S. Department of Veterans Affairs"
        assert "rural areas" in resource.description.lower()
        assert resource.phone == "(800) 698-2411"  # Normalized
        assert "healthcare" in resource.categories
        assert "telehealth" in resource.tags
        assert "rural" in resource.tags
        assert "va" in resource.tags
        assert resource.scope == "national"
        assert "VA health care enrollment required" in resource.eligibility

    def test_run_parses_state_program(self, tmp_path):
        """Test parsing a state-scoped telehealth program."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "id": "alaska-flex",
                    "name": "Alaska FLEX Rural Veterans Program",
                    "org_name": "State of Alaska",
                    "description": "FLEX grant-funded telehealth for rural Alaska Veterans.",
                    "tier": 2,
                    "website": "https://health.alaska.gov/",
                    "phone": "907-465-3027",
                    "scope": "state",
                    "states": ["AK"],
                    "categories": ["healthcare"],
                    "tags": ["telehealth", "rural", "flex-grant", "alaska"],
                    "eligibility": {
                        "summary": "Veterans in Southeast Alaska",
                        "va_enrollment_required": False,
                    },
                    "services": ["Primary care", "Mental health counseling"],
                    "coverage_area": "Southeast Alaska: Juneau, Ketchikan, Sitka",
                }
            ],
        }
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Alaska" in resource.title or "FLEX" in resource.title
        assert resource.scope == "state"
        assert resource.states == ["AK"]
        assert "state-ak" in resource.tags
        assert "No VA enrollment required" in resource.eligibility
        assert "Southeast Alaska" in resource.description

    def test_run_creates_location_resources(self, tmp_path):
        """Test that locations create additional resources."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "id": "va-atlas",
                    "name": "VA ATLAS Telehealth",
                    "org_name": "VA",
                    "description": "ATLAS sites for rural Veterans.",
                    "tier": 1,
                    "website": "https://www.va.gov/atlas/",
                    "phone": "1-800-698-2411",
                    "scope": "national",
                    "categories": ["healthcare"],
                    "tags": ["telehealth", "rural", "atlas"],
                    "eligibility": {
                        "summary": "Enrolled Veterans",
                        "va_enrollment_required": True,
                    },
                    "services": ["Primary care"],
                    "locations": [
                        {
                            "name": "Lander VFW Post 7693",
                            "address": "230 Main Street",
                            "city": "Lander",
                            "state": "WY",
                            "zip": "82520",
                        },
                        {
                            "name": "Glasgow American Legion Post 41",
                            "address": "219 6th Avenue South",
                            "city": "Glasgow",
                            "state": "MT",
                            "zip": "59230",
                        },
                    ],
                }
            ],
        }
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        # 1 main program + 2 location-specific resources
        assert len(resources) == 3

        # Check main program
        main = resources[0]
        assert "ATLAS" in main.title
        assert main.scope == "national"

        # Check location resources
        lander = resources[1]
        assert "Lander" in lander.title or "VFW" in lander.title
        assert lander.city == "Lander"
        assert lander.state == "WY"
        assert lander.zip_code == "82520"
        assert lander.scope == "local"
        assert "telehealth-site" in lander.tags

        glasgow = resources[2]
        assert "Glasgow" in glasgow.title or "American Legion" in glasgow.title
        assert glasgow.city == "Glasgow"
        assert glasgow.state == "MT"

    def test_run_parses_nonprofit_telehealth(self, tmp_path):
        """Test parsing a nonprofit telehealth resource."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "id": "cohen-telehealth",
                    "name": "Cohen Veterans Network Telehealth",
                    "org_name": "Cohen Veterans Network",
                    "description": "Free telehealth mental health services.",
                    "tier": 2,
                    "website": "https://www.cohenveteransnetwork.org/",
                    "phone": "1-844-336-4226",
                    "scope": "national",
                    "categories": ["healthcare", "mentalHealth"],
                    "tags": ["telehealth", "mental-health", "free-services", "post-9/11"],
                    "eligibility": {
                        "summary": "Post-9/11 Veterans and their families",
                        "va_enrollment_required": False,
                    },
                    "services": ["Individual therapy", "Family therapy", "PTSD treatment"],
                    "access_method": "Call 1-844-336-4226 to schedule.",
                }
            ],
        }
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Cohen" in resource.title
        assert "mentalHealth" in resource.categories
        assert "mental-health" in resource.tags
        assert "cohen-veterans-network" in resource.tags
        assert "no-va-enrollment" in resource.tags

    def test_build_tags_includes_core_tags(self, tmp_path):
        """Test that core telehealth/rural tags are always present."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "tags": ["some-other-tag"],
            "scope": "national",
            "categories": ["healthcare"],
        }
        tags = connector._build_tags(program)

        assert "telehealth" in tags
        assert "rural" in tags
        # Core tags should appear early in the list (within first 3 positions)
        assert tags.index("telehealth") < 3
        assert tags.index("rural") < 3

    def test_build_tags_state_specific(self, tmp_path):
        """Test that state-scoped programs get state tags."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "tags": ["telehealth"],
            "scope": "state",
            "states": ["MT", "WY"],
            "categories": ["healthcare"],
        }
        tags = connector._build_tags(program)

        assert "state-mt" in tags
        assert "state-wy" in tags

    def test_build_eligibility_with_va_required(self, tmp_path):
        """Test eligibility text when VA enrollment is required."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "eligibility": {
                "summary": "Veterans in rural areas",
                "va_enrollment_required": True,
                "notes": "Priority for Veterans over 40 miles from VA facility",
            }
        }
        eligibility = connector._build_eligibility(program)

        assert "Veterans in rural areas" in eligibility
        assert "VA health care enrollment required" in eligibility
        assert "Priority for Veterans" in eligibility

    def test_build_eligibility_no_va_required(self, tmp_path):
        """Test eligibility text when VA enrollment is not required."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "eligibility": {
                "summary": "All Veterans",
                "va_enrollment_required": False,
            }
        }
        eligibility = connector._build_eligibility(program)

        assert "All Veterans" in eligibility
        assert "No VA enrollment required" in eligibility

    def test_build_description_with_services(self, tmp_path):
        """Test description building includes services."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "description": "Telehealth services for rural Veterans.",
            "services": ["Primary care", "Mental health", "Specialty care", "Pharmacy", "Nutrition", "Social work"],
            "coverage_area": "Southeast Alaska",
        }
        desc = connector._build_description(program)

        assert "Telehealth services" in desc
        assert "Services include:" in desc
        assert "Primary care" in desc
        assert "and 1 more services" in desc  # 6 services, shows 5
        assert "Southeast Alaska" in desc

    def test_build_how_to_apply_with_access_method(self, tmp_path):
        """Test how to apply uses access_method when available."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "access_method": "Contact your local VA facility to schedule.",
            "phone": "1-800-555-1234",
            "email": "help@va.gov",
            "website": "https://www.va.gov/",
        }
        how_to = connector._build_how_to_apply(program)

        assert "Contact your local VA facility" in how_to
        assert "help@va.gov" in how_to

    def test_build_how_to_apply_without_access_method(self, tmp_path):
        """Test how to apply uses phone/website when no access_method."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "phone": "1-800-555-1234",
            "website": "https://www.example.com/",
        }
        how_to = connector._build_how_to_apply(program)

        assert "Call" in how_to
        assert "1-800-555-1234" in how_to
        assert "https://www.example.com/" in how_to

    def test_location_description(self, tmp_path):
        """Test location-specific description building."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        program = {
            "name": "VA ATLAS Telehealth",
            "description": "ATLAS telehealth sites.",
            "services": ["Primary care", "Mental health", "Specialty care"],
        }
        location = {
            "name": "Lander VFW Post 7693",
            "city": "Lander",
            "state": "WY",
        }
        desc = connector._build_location_description(program, location)

        assert "Lander VFW Post 7693" in desc
        assert "Lander, WY" in desc
        assert "ATLAS telehealth site" in desc
        assert "Primary care" in desc

    def test_run_with_real_data(self):
        """Test run() with the actual rural telehealth data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "rural_telehealth_programs.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("rural_telehealth_programs.json not found in project")

        connector = RuralTelehealthConnector(data_path=data_file)
        resources = connector.run()

        # Should have 12+ programs plus their locations
        assert len(resources) >= 12

        # All should have telehealth and rural tags
        assert all("telehealth" in r.tags for r in resources)
        assert all("rural" in r.tags for r in resources)

        # All should have healthcare category
        for r in resources:
            assert "healthcare" in r.categories

        # Check required programs are represented
        titles = [r.title for r in resources]
        title_text = " ".join(titles).lower()
        assert "atlas" in title_text
        assert "connected devices" in title_text or "video connect" in title_text

        # Check VA programs exist
        org_names = {r.org_name for r in resources}
        assert any("Veterans Affairs" in org or "VA" in org for org in org_names)

        # Check structure of first resource
        first = resources[0]
        assert first.title is not None
        assert first.description is not None
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.categories is not None
        assert first.tags is not None

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        data = {"metadata": {"source": "test"}, "programs": []}
        data_file = tmp_path / "telehealth.json"
        data_file.write_text(json.dumps(data))

        with RuralTelehealthConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_phone_normalization(self, tmp_path):
        """Test that phone numbers are normalized."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        # Test 1-800 number normalization
        assert connector._normalize_phone("1-800-698-2411") == "(800) 698-2411"
        assert connector._normalize_phone("8006982411") == "(800) 698-2411"
        assert connector._normalize_phone("18006982411") == "(800) 698-2411"

    def test_title_adds_telehealth_suffix(self, tmp_path):
        """Test that titles without Telehealth get it added."""
        connector = RuralTelehealthConnector(data_path=tmp_path / "test.json")

        # Program without Telehealth in name
        title = connector._build_title("VA Connected Devices Program")
        assert "Rural Telehealth" in title

        # Program with ATLAS in name (special case)
        title = connector._build_title("VA ATLAS Telehealth Sites")
        assert title == "VA ATLAS Telehealth Sites"  # Unchanged

        # Program with Telehealth already
        title = connector._build_title("Montana Veterans Rural Telehealth Network")
        assert title == "Montana Veterans Rural Telehealth Network"  # Unchanged
