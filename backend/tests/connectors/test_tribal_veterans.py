"""Tests for Tribal Veteran Services connector."""

import json
from pathlib import Path

import pytest

from connectors.tribal_veterans import TribalVeteransConnector


class TestTribalVeteransConnector:
    """Tests for TribalVeteransConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = TribalVeteransConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "IHS/VA Tribal Veteran Services"
        assert meta.tier == 2  # Established nonprofit/tribal organizations
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "ihs.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = TribalVeteransConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = TribalVeteransConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_urban_indian_org_basic(self, tmp_path):
        """Test parsing an Urban Indian Organization."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "Indian Health Board of Minneapolis",
                    "city": "Minneapolis",
                    "state": "MN",
                    "phone": "612-721-9800",
                    "website": "https://indianhealthboard.com",
                    "executive_director": "Patrick M. Rock, M.D.",
                    "ihs_region": "Bemidji",
                    "active": True,
                }
            ],
            "va_tribal_programs": [],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        r = resources[0]

        assert "Indian Health Board of Minneapolis" in r.title
        assert "Minneapolis, MN" in r.title
        assert r.city == "Minneapolis"
        assert r.state == "MN"
        assert r.phone == "(612) 721-9800"
        assert r.org_website == "https://indianhealthboard.com"
        assert "healthcare" in r.categories
        assert "supportServices" in r.categories
        assert "mentalHealth" in r.categories
        assert r.scope == "local"
        assert r.states == ["MN"]

    def test_parse_urban_indian_org_tags(self, tmp_path):
        """Test tags for Urban Indian Organization."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "Seattle Indian Health Board",
                    "city": "Seattle",
                    "state": "WA",
                    "ihs_region": "Portland",
                    "active": True,
                }
            ],
            "va_tribal_programs": [],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        r = resources[0]
        tags = r.tags

        assert "tribal" in tags
        assert "native-american" in tags
        assert "alaska-native" in tags
        assert "urban-indian-health" in tags
        assert "ihs" in tags
        assert "va-ihs-mou" in tags
        assert "native-veteran" in tags
        assert "state-wa" in tags
        assert "ihs-portland" in tags

    def test_skips_inactive_organizations(self, tmp_path):
        """Test that inactive organizations are skipped."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "Active Org",
                    "city": "City1",
                    "state": "CA",
                    "active": True,
                },
                {
                    "name": "Inactive Org",
                    "city": "City2",
                    "state": "WA",
                    "active": False,
                },
            ],
            "va_tribal_programs": [],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        assert "Active Org" in resources[0].title

    def test_parse_va_tribal_program_basic(self, tmp_path):
        """Test parsing a VA Tribal Program."""
        test_data = {
            "urban_indian_organizations": [],
            "va_tribal_programs": [
                {
                    "name": "VHA Office of Tribal Health",
                    "type": "va_program",
                    "description": "Provides leadership and guidance for Native Veteran health care.",
                    "contact_email": "VHAOfficeofTribalHealth@va.gov",
                    "website": "https://www.va.gov/health/vha-tribal-health.asp",
                    "scope": "national",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        r = resources[0]

        assert r.title == "VHA Office of Tribal Health"
        assert "Native Veteran health care" in r.description
        assert r.email == "VHAOfficeofTribalHealth@va.gov"
        assert r.org_name == "U.S. Department of Veterans Affairs - Office of Tribal Health"
        assert "benefits" in r.categories
        assert "healthcare" in r.categories
        assert "va-tribal-health" in r.tags
        assert "va-program" in r.tags

    def test_parse_va_program_with_locations(self, tmp_path):
        """Test parsing a VA Tribal Program with specific locations."""
        test_data = {
            "urban_indian_organizations": [],
            "va_tribal_programs": [
                {
                    "name": "VA-IHS Clinic-in-a-Clinic Program",
                    "type": "va_program",
                    "description": "Places VA providers within IHS facilities.",
                    "locations": [
                        {"name": "Chinle Service Unit", "state": "AZ", "opened": "2024"},
                        {"name": "Kayenta Health Center", "state": "AZ", "opened": "2024"},
                    ],
                    "website": "https://www.ihs.gov/vaihsmou/",
                    "scope": "national",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        r = resources[0]

        assert "Chinle Service Unit" in r.description
        assert "Kayenta Health Center" in r.description
        assert r.scope == "local"  # Should be local since locations are specified
        assert r.states == ["AZ"]
        assert "clinic-in-a-clinic" in r.tags
        assert "state-az" in r.tags

    def test_parse_homelessness_program(self, tmp_path):
        """Test that homelessness programs get housing category."""
        test_data = {
            "urban_indian_organizations": [],
            "va_tribal_programs": [
                {
                    "name": "Native American Veteran Homelessness Initiative",
                    "type": "federal_initiative",
                    "description": "Multi-agency effort to address homelessness.",
                    "scope": "national",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        r = resources[0]
        assert "housing" in r.categories

    def test_uio_eligibility_text(self):
        """Test that UIO eligibility text is appropriate."""
        connector = TribalVeteransConnector(data_path="/fake/path.json")

        elig = connector.UIO_ELIGIBILITY
        assert "American Indian" in elig
        assert "Alaska Native" in elig
        assert "enrolled tribal" in elig.lower()
        assert "Native Veterans" in elig

    def test_build_uio_description(self):
        """Test UIO description building."""
        connector = TribalVeteransConnector(data_path="/fake/path.json")

        desc = connector._build_uio_description(
            name="Seattle Indian Health Board",
            city="Seattle",
            state="WA",
            director="Esther Luceo",
            ihs_region="Portland",
        )

        assert "Seattle Indian Health Board" in desc
        assert "Seattle, WA" in desc
        assert "Urban Indian Health Organization" in desc
        assert "IHS-VA Memorandum of Understanding" in desc
        assert "primary medical care" in desc
        assert "traditional healing" in desc
        assert "Esther Luceo" in desc
        assert "IHS Portland Area" in desc

    def test_build_uio_how_to_apply(self):
        """Test UIO how-to-apply instructions."""
        connector = TribalVeteransConnector(data_path="/fake/path.json")

        how = connector._build_uio_how_to_apply(
            name="Denver Indian Health",
            phone="303-953-6618",
            website="https://dihfs.org",
        )

        assert "Denver Indian Health" in how
        assert "(303) 953-6618" in how
        assert "https://dihfs.org" in how
        assert "tribal enrollment documentation" in how
        assert "IHS-VA MOU" in how

    def test_build_uio_tags_with_region(self):
        """Test UIO tag building with IHS region."""
        connector = TribalVeteransConnector(data_path="/fake/path.json")

        tags = connector._build_uio_tags(state="CA", ihs_region="California")

        assert "tribal" in tags
        assert "native-american" in tags
        assert "state-ca" in tags
        assert "ihs-california" in tags

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = TribalVeteransConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "Tribal veteran services data file not found" in str(exc_info.value)

    def test_run_with_mixed_data(self, tmp_path):
        """Test running with both UIOs and VA programs."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "UIO 1",
                    "city": "City1",
                    "state": "TX",
                    "active": True,
                },
                {
                    "name": "UIO 2",
                    "city": "City2",
                    "state": "CA",
                    "active": True,
                },
            ],
            "va_tribal_programs": [
                {
                    "name": "VA Program 1",
                    "type": "va_program",
                    "description": "Test program",
                    "scope": "national",
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 3

        # Check types
        uio_resources = [r for r in resources if "urban-indian-health" in (r.tags or [])]
        va_resources = [r for r in resources if "va-tribal-health" in (r.tags or [])]

        assert len(uio_resources) == 2
        assert len(va_resources) == 1

    def test_run_with_real_data(self):
        """Test run() with the actual tribal veteran services data file."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "tribal_veteran_services.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("tribal_veteran_services.json not found in project")

        connector = TribalVeteransConnector(data_path=data_file)
        resources = connector.run()

        # Should have 38 active UIOs + 4 VA programs = ~42 resources
        assert len(resources) >= 35

        # All UIOs should have required categories
        uio_resources = [r for r in resources if "urban-indian-health" in (r.tags or [])]
        for r in uio_resources:
            assert "healthcare" in r.categories
            assert r.scope == "local"

        # Check for Native Veteran tags
        assert all("native-veteran" in (r.tags or []) for r in resources)

        # Check that there are resources in multiple states
        states = {r.state for r in resources if r.state}
        assert len(states) >= 15  # UIOs are in ~20 states

        # Verify first resource structure
        first = resources[0]
        assert first.title is not None
        assert first.description is not None
        assert first.source_url is not None
        assert first.eligibility is not None

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with TribalVeteransConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "IHS/VA Tribal Veteran Services"

    def test_phone_normalization(self, tmp_path):
        """Test that phone numbers are normalized."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "Test Org",
                    "city": "City",
                    "state": "TX",
                    "phone": "5551234567",
                    "active": True,
                }
            ],
            "va_tribal_programs": [],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        # Should be formatted as (XXX) XXX-XXXX
        assert resources[0].phone == "(555) 123-4567"

    def test_states_served_from_multiple_locations(self, tmp_path):
        """Test that states are collected from multiple program locations."""
        test_data = {
            "urban_indian_organizations": [],
            "va_tribal_programs": [
                {
                    "name": "Multi-State Program",
                    "type": "va_program",
                    "description": "Test program",
                    "locations": [
                        {"name": "Location 1", "state": "AZ"},
                        {"name": "Location 2", "state": "NM"},
                        {"name": "Location 3", "state": "AZ"},  # Duplicate state
                    ],
                    "scope": "national",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        r = resources[0]
        # Should have unique states only
        assert set(r.states) == {"AZ", "NM"}

    def test_uio_default_active_true(self, tmp_path):
        """Test that UIOs without active field default to active=True."""
        test_data = {
            "urban_indian_organizations": [
                {
                    "name": "Test Org Without Active Field",
                    "city": "City",
                    "state": "TX",
                    # Note: no "active" field
                }
            ],
            "va_tribal_programs": [],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = TribalVeteransConnector(data_path=test_file)
        resources = connector.run()

        # Should be included since active defaults to True
        assert len(resources) == 1
