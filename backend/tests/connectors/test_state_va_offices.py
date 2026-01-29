"""Tests for State VA Offices connector with detailed location data."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.state_va_offices import StateVAOfficesConnector


class TestStateVAOfficesConnector:
    """Tests for StateVAOfficesConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "State VA Offices (Detailed)"
        assert meta.tier == 3  # State-level agencies
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "nasdva.us" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = StateVAOfficesConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = StateVAOfficesConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_main_office(self):
        """Test parsing a main office entry."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        office = {
            "name": "Texas Veterans Commission Headquarters",
            "address": "1700 North Congress Avenue",
            "city": "Austin",
            "zip_code": "78701",
            "phone": "(512) 463-6564",
            "fax": "(512) 475-2395",
            "email": "info@tvc.texas.gov",
            "website": "https://www.tvc.texas.gov/",
            "hours": "Monday-Friday 8:00 AM - 5:00 PM",
        }

        services = [
            "VA claims assistance",
            "Education benefits",
            "Employment services",
        ]

        candidate = connector._parse_office(
            state="TX",
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            office=office,
            services=services,
            is_main_office=True,
            fetched_at=now,
        )

        assert candidate.title == "Texas Veterans Commission Headquarters"
        assert "Texas Veterans Commission" in candidate.description
        assert "headquarters" in candidate.description.lower()
        assert candidate.org_name == "Texas Veterans Commission"
        assert candidate.org_website == "https://www.tvc.texas.gov/"
        assert "benefits" in candidate.categories
        assert "supportServices" in candidate.categories
        assert candidate.scope == "state"
        assert candidate.states == ["TX"]
        assert "state-va" in candidate.tags
        assert "state-tx" in candidate.tags
        assert "headquarters" in candidate.tags
        assert candidate.phone == "(512) 463-6564"
        assert candidate.email == "info@tvc.texas.gov"
        assert candidate.hours == "Monday-Friday 8:00 AM - 5:00 PM"
        assert "Austin" in candidate.address
        assert "78701" in candidate.address
        assert candidate.raw_data["is_main_office"] is True

    def test_parse_regional_office(self):
        """Test parsing a regional office entry."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        office = {
            "name": "Houston Regional Office",
            "address": "6900 Almeda Road",
            "city": "Houston",
            "zip_code": "77030",
            "phone": "(713) 383-2727",
        }

        candidate = connector._parse_office(
            state="TX",
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            office=office,
            services=["VA claims assistance"],
            is_main_office=False,
            fetched_at=now,
        )

        assert candidate.title == "Houston Regional Office"
        assert "regional" in candidate.description.lower()
        assert "Texas" in candidate.description
        assert "regional-office" in candidate.tags
        assert "headquarters" not in candidate.tags
        assert candidate.raw_data["is_main_office"] is False

    def test_build_full_address(self):
        """Test full address building."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        # Full address
        addr = connector._build_full_address(
            address="1700 North Congress Avenue",
            city="Austin",
            state="TX",
            zip_code="78701",
        )
        assert addr == "1700 North Congress Avenue, Austin, TX 78701"

        # Without zip
        addr = connector._build_full_address(
            address="1700 North Congress Avenue",
            city="Austin",
            state="TX",
            zip_code=None,
        )
        assert addr == "1700 North Congress Avenue, Austin, TX"

        # Address only
        addr = connector._build_full_address(
            address="1700 North Congress Avenue",
            city=None,
            state=None,
            zip_code=None,
        )
        assert addr == "1700 North Congress Avenue"

        # No address
        addr = connector._build_full_address(
            address=None,
            city="Austin",
            state="TX",
            zip_code="78701",
        )
        assert addr is None

    def test_build_title_main_office(self):
        """Test title building for main office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        title = connector._build_title(
            agency_name="Texas Veterans Commission",
            office_name="Texas Veterans Commission Headquarters",
            state="TX",
            is_main_office=True,
        )
        assert title == "Texas Veterans Commission Headquarters"

    def test_build_title_no_office_name(self):
        """Test title building without office name."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        title = connector._build_title(
            agency_name="Texas Veterans Commission",
            office_name=None,
            state="TX",
            is_main_office=True,
        )
        assert title == "Texas Veterans Commission - Main Office"

    def test_build_title_regional_office(self):
        """Test title building for regional office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        title = connector._build_title(
            agency_name="Texas Veterans Commission",
            office_name="Houston Regional Office",
            state="TX",
            is_main_office=False,
        )
        assert title == "Houston Regional Office"

    def test_build_description_main_office(self):
        """Test description building for main office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            office_name="Headquarters",
            services=["VA claims assistance", "Education benefits"],
            is_main_office=True,
        )

        assert "Texas Veterans Commission" in desc
        assert "headquarters" in desc.lower()
        assert "Texas" in desc
        assert "VA claims assistance" in desc

    def test_build_description_regional_office(self):
        """Test description building for regional office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            office_name="Houston Regional Office",
            services=["VA claims assistance"],
            is_main_office=False,
        )

        assert "regional" in desc.lower()
        assert "Texas" in desc

    def test_build_tags_main_office(self):
        """Test tag building for main office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="TX",
            services=["VA claims assistance", "Education benefits", "Employment services"],
            is_main_office=True,
        )

        assert "state-va" in tags
        assert "state-benefits" in tags
        assert "headquarters" in tags
        assert "state-tx" in tags
        assert "education-benefits" in tags
        assert "employment-services" in tags

    def test_build_tags_regional_office(self):
        """Test tag building for regional office."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="TX",
            services=["VA claims assistance"],
            is_main_office=False,
        )

        assert "state-va" in tags
        assert "regional-office" in tags
        assert "headquarters" not in tags

    def test_build_tags_with_services(self):
        """Test service-based tag generation."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="TX",
            services=[
                "Veterans homes",
                "State cemetery",
                "Healthcare referrals",
                "Women veterans programs",
                "Property tax exemptions",
                "Emergency assistance",
            ],
            is_main_office=True,
        )

        assert "veterans-home" in tags
        assert "cemetery" in tags
        assert "healthcare" in tags
        assert "women-veterans" in tags
        assert "property-tax-exemption" in tags
        assert "emergency-assistance" in tags

    def test_eligibility_text(self):
        """Test that eligibility text includes state name."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility("Texas")

        assert "Texas" in eligibility
        assert "Veterans" in eligibility
        assert "discharge status" in eligibility
        assert "Family members" in eligibility

    def test_how_to_apply_text(self):
        """Test how_to_apply text generation."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")

        how_to = connector._build_how_to_apply(
            agency_name="Texas Veterans Commission",
            office_name="Headquarters",
            phone="(512) 463-6564",
            email="info@tvc.texas.gov",
            website="https://www.tvc.texas.gov/",
        )

        assert "(512) 463-6564" in how_to
        assert "www.tvc.texas.gov" in how_to
        assert "DD-214" in how_to

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = StateVAOfficesConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "State VA offices data file not found" in str(exc_info.value)

    def test_run_parses_json_with_regional_offices(self, tmp_path):
        """Test that run() parses main and regional offices."""
        test_data = {
            "source": "Test",
            "offices": [
                {
                    "state": "TX",
                    "state_name": "Texas",
                    "agency_name": "Texas Veterans Commission",
                    "main_office": {
                        "name": "TVC Headquarters",
                        "address": "1700 North Congress Avenue",
                        "city": "Austin",
                        "zip_code": "78701",
                        "phone": "(512) 463-6564",
                        "website": "https://www.tvc.texas.gov/",
                    },
                    "services": ["VA claims assistance", "Education benefits"],
                    "regional_offices": [
                        {
                            "name": "Houston Regional Office",
                            "address": "6900 Almeda Road",
                            "city": "Houston",
                            "zip_code": "77030",
                            "phone": "(713) 383-2727",
                        },
                        {
                            "name": "San Antonio Regional Office",
                            "address": "3601 South Congress Avenue",
                            "city": "San Antonio",
                            "zip_code": "78204",
                            "phone": "(210) 921-8002",
                        },
                    ],
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = StateVAOfficesConnector(data_path=test_file)
        resources = connector.run()

        # Should have 1 main office + 2 regional offices = 3 resources
        assert len(resources) == 3

        # First should be main office
        main = resources[0]
        assert main.title == "TVC Headquarters"
        assert "Austin" in main.address
        assert main.raw_data["is_main_office"] is True
        assert "headquarters" in main.tags

        # Others should be regional offices
        houston = resources[1]
        assert houston.title == "Houston Regional Office"
        assert "Houston" in houston.address
        assert houston.raw_data["is_main_office"] is False
        assert "regional-office" in houston.tags

        san_antonio = resources[2]
        assert san_antonio.title == "San Antonio Regional Office"
        assert "San Antonio" in san_antonio.address

    def test_run_office_without_regional_offices(self, tmp_path):
        """Test parsing office with no regional offices."""
        test_data = {
            "source": "Test",
            "offices": [
                {
                    "state": "RI",
                    "state_name": "Rhode Island",
                    "agency_name": "Rhode Island Office of Veterans Services",
                    "main_office": {
                        "name": "RI OVS Main Office",
                        "address": "560 Jefferson Boulevard",
                        "city": "Warwick",
                        "zip_code": "02886",
                        "phone": "(401) 921-2152",
                    },
                    "services": ["VA claims assistance"],
                    "regional_offices": [],
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = StateVAOfficesConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].title == "RI OVS Main Office"

    def test_run_with_real_data(self):
        """Test run() with the actual state VA offices data file."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "state_va_offices.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("state_va_offices.json not found in project")

        connector = StateVAOfficesConnector(data_path=data_file)
        resources = connector.run()

        # Should have more resources than states due to regional offices
        # 56 states/territories + regional offices
        assert len(resources) >= 56

        # Count unique states
        states = {r.state for r in resources}
        assert len(states) >= 50  # At least 50 states

        # Check for expected states
        assert "TX" in states
        assert "CA" in states
        assert "NY" in states
        assert "FL" in states
        assert "DC" in states  # District of Columbia

        # Check for territories
        assert "PR" in states  # Puerto Rico
        assert "GU" in states  # Guam

        # All should be state scope
        assert all(r.scope == "state" for r in resources)

        # All should have state-va tag
        assert all("state-va" in r.tags for r in resources)

        # Check categories
        assert all("benefits" in r.categories for r in resources)
        assert all("supportServices" in r.categories for r in resources)

        # Check that we have both main and regional offices
        main_offices = [r for r in resources if r.raw_data.get("is_main_office")]
        regional_offices = [r for r in resources if not r.raw_data.get("is_main_office")]

        assert len(main_offices) >= 50  # At least one per state
        assert len(regional_offices) > 0  # Some states have regional offices

    def test_resource_structure(self):
        """Test that all required fields are present in resources."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        office = {
            "name": "Test Office",
            "address": "123 Main St",
            "city": "Austin",
            "zip_code": "78701",
            "phone": "(512) 555-1234",
            "email": "test@example.com",
            "website": "https://example.com",
            "hours": "9-5",
        }

        candidate = connector._parse_office(
            state="TX",
            state_name="Texas",
            agency_name="Test Agency",
            office=office,
            services=["Service 1"],
            is_main_office=True,
            fetched_at=now,
        )

        # Required fields
        assert candidate.title is not None
        assert candidate.description is not None
        assert candidate.source_url is not None
        assert candidate.org_name is not None
        assert candidate.categories is not None
        assert candidate.tags is not None
        assert candidate.scope is not None
        assert candidate.eligibility is not None
        assert candidate.how_to_apply is not None
        assert candidate.fetched_at is not None
        assert candidate.raw_data is not None

        # Optional fields that should be present
        assert candidate.address is not None
        assert candidate.city is not None
        assert candidate.state is not None
        assert candidate.zip_code is not None
        assert candidate.phone is not None
        assert candidate.email is not None
        assert candidate.hours is not None
        assert candidate.org_website is not None

    def test_phone_normalization(self):
        """Test that phone numbers are normalized."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        # Test various phone formats
        test_cases = [
            ("5125551234", "(512) 555-1234"),
            ("(512) 555-1234", "(512) 555-1234"),
            ("512-555-1234", "(512) 555-1234"),
            ("1-512-555-1234", "(512) 555-1234"),
        ]

        for input_phone, expected in test_cases:
            office = {
                "name": "Test",
                "phone": input_phone,
            }

            candidate = connector._parse_office(
                state="TX",
                state_name="Texas",
                agency_name="Test",
                office=office,
                services=[],
                is_main_office=True,
                fetched_at=now,
            )

            assert candidate.phone == expected, f"Failed for input: {input_phone}"

    def test_empty_services_list(self):
        """Test parsing office with empty services list."""
        connector = StateVAOfficesConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        office = {
            "name": "Test Office",
            "address": "123 Main St",
            "city": "Austin",
            "zip_code": "78701",
            "phone": "(512) 555-1234",
        }

        candidate = connector._parse_office(
            state="TX",
            state_name="Texas",
            agency_name="Test Agency",
            office=office,
            services=[],
            is_main_office=True,
            fetched_at=now,
        )

        # Should still create a valid resource
        assert candidate.title is not None
        assert "Services include:" not in candidate.description
