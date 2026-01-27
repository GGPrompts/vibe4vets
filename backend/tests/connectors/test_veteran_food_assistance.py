"""Tests for Veteran Food Assistance Programs connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.veteran_food_assistance import VeteranFoodAssistanceConnector


class TestVeteranFoodAssistanceConnector:
    """Tests for VeteranFoodAssistanceConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        meta = connector.metadata

        assert "Food" in meta.name or "Veteran" in meta.name
        assert meta.tier == 2  # Established nonprofits and community programs
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_build_title_soldiers_angels(self, tmp_path):
        """Test title building for Soldiers' Angels."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title("Soldiers' Angels", "Military and Veteran Food Distribution")
        assert title == "Soldiers' Angels - Military and Veteran Food Distribution"

    def test_build_title_dvnf(self, tmp_path):
        """Test title building for DVNF."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title(
            "Disabled Veterans National Foundation (DVNF)", "Veterans Food Assistance Program (VFAP)"
        )
        assert title == "DVNF - Veterans Food Assistance Program (VFAP)"

    def test_build_title_vfw(self, tmp_path):
        """Test title building for VFW."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title("VFW Post 10054", "Veterans Food Pantry")
        assert title == "VFW - Veterans Food Pantry"

    def test_build_title_unknown_org(self, tmp_path):
        """Test title building for unknown organization."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title("New Food Bank", "Veteran Program")
        assert title == "New Food Bank - Veteran Program"

    def test_format_services(self, tmp_path):
        """Test formatting of services."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        services = ["fresh_produce", "meat", "non_perishables", "holiday_meals"]
        formatted = connector._format_services(services)

        assert "fresh produce" in formatted
        assert "meat" in formatted
        assert "non-perishable items" in formatted
        assert "holiday meals" in formatted

    def test_format_services_truncation(self, tmp_path):
        """Test that long service lists are truncated."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        services = [
            "fresh_produce",
            "meat",
            "non_perishables",
            "milk",
            "eggs",
            "cheese",
            "pantry_staples",
            "holiday_meals",
        ]
        formatted = connector._format_services(services)

        # Should truncate and add "and more"
        assert "and more" in formatted

    def test_build_description_with_services(self, tmp_path):
        """Test description building with services."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Soldiers' Angels",
            "program_name": "Food Distribution",
            "services": ["fresh_produce", "meat", "non_perishables"],
            "hours": "Monthly distributions",
        }
        desc = connector._build_description(program)

        assert "food assistance" in desc.lower()
        assert "fresh produce" in desc.lower()
        assert "Monthly distributions" in desc

    def test_build_description_with_distribution_cities(self, tmp_path):
        """Test description building with multiple cities."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "National Food Program",
            "program_name": "Veteran Food Distribution",
            "services": ["food_pantry"],
            "distribution_cities": [
                {"city": "Atlanta", "state": "GA"},
                {"city": "Dallas", "state": "TX"},
                {"city": "Denver", "state": "CO"},
            ],
        }
        desc = connector._build_description(program)

        assert "Atlanta, GA" in desc
        assert "Dallas, TX" in desc
        assert "Denver, CO" in desc

    def test_build_eligibility_with_documentation(self, tmp_path):
        """Test eligibility building with documentation requirements."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "eligibility": {
                "summary": "All veterans and their families",
                "veteran_status_required": True,
                "documentation_required": ["military_id", "dd214"],
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "All veterans" in eligibility
        assert "military ID" in eligibility
        assert "DD-214" in eligibility

    def test_build_eligibility_no_documentation(self, tmp_path):
        """Test eligibility building without documentation requirements."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "eligibility": {
                "summary": "No paperwork or income requirements",
                "veteran_status_required": True,
                "documentation_required": [],
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "No paperwork" in eligibility
        assert "Required documentation" not in eligibility

    def test_build_eligibility_active_duty(self, tmp_path):
        """Test eligibility building for active duty programs."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "eligibility": {
                "summary": "Service members at Fort Liberty",
                "veteran_status_required": False,
                "documentation_required": ["military_id"],
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "active duty" in eligibility.lower()

    def test_build_how_to_apply(self, tmp_path):
        """Test building how to apply instructions."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "address": "123 Main Street",
            "city": "San Antonio",
            "state": "TX",
            "zip_code": "78201",
            "hours": "Wednesday 10:00 AM - 12:00 PM",
            "phone": "210-555-1234",
            "email": "help@example.com",
            "website": "https://example.com",
        }
        how_to_apply = connector._build_how_to_apply(program)

        assert "123 Main Street" in how_to_apply
        assert "San Antonio" in how_to_apply
        assert "TX" in how_to_apply
        assert "78201" in how_to_apply
        assert "Wednesday" in how_to_apply
        assert "210-555-1234" in how_to_apply
        assert "help@example.com" in how_to_apply
        assert "example.com" in how_to_apply

    def test_build_tags_food_pantry(self, tmp_path):
        """Test tag building for food pantry programs."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "VFW Post 1234",
            "services": ["food_pantry", "non_perishables", "canned_goods"],
            "scope": "local",
        }
        tags = connector._build_tags(program)

        assert "food-assistance" in tags
        assert "food-insecurity" in tags
        assert "veteran-services" in tags
        assert "food-pantry" in tags
        assert "vfw" in tags

    def test_build_tags_food_distribution(self, tmp_path):
        """Test tag building for food distribution programs."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Soldiers' Angels",
            "services": ["monthly_food_distribution", "fresh_produce", "meat"],
            "scope": "national",
        }
        tags = connector._build_tags(program)

        assert "food-distribution" in tags
        assert "fresh-produce" in tags
        assert "soldiers-angels" in tags
        assert "nationwide" in tags

    def test_build_tags_mobile_pantry(self, tmp_path):
        """Test tag building for mobile pantry programs."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Regional Food Bank",
            "services": ["mobile_pantry", "fresh_produce"],
            "scope": "local",
        }
        tags = connector._build_tags(program)

        assert "mobile-pantry" in tags
        assert "food-distribution" in tags
        assert "fresh-produce" in tags

    def test_build_tags_va_program(self, tmp_path):
        """Test tag building for VA programs."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "VA Food Security Office",
            "services": ["produce_prescriptions", "snap_referrals", "food_bank_referrals"],
            "scope": "national",
        }
        tags = connector._build_tags(program)

        assert "va" in tags
        assert "snap" in tags
        assert "produce-rx" in tags
        assert "nationwide" in tags

    def test_parse_program(self, tmp_path):
        """Test parsing a single program entry."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        now = datetime.now(UTC)

        program = {
            "org_name": "Soldiers' Angels",
            "program_name": "Food Distribution",
            "website": "https://soldiersangels.org/food/",
            "phone": "210-629-0020",
            "email": "info@soldiersangels.org",
            "address": "2895 NE Loop 410",
            "city": "San Antonio",
            "state": "TX",
            "zip_code": "78218",
            "hours": "Monthly; check website",
            "services": ["monthly_food_distribution", "fresh_produce", "meat"],
            "eligibility": {
                "summary": "Homeless, at-risk, or low-income veterans",
                "veteran_status_required": True,
                "documentation_required": ["military_id", "dd214"],
            },
            "scope": "national",
            "states": ["GA", "TX", "CO"],
        }

        candidate = connector._parse_program(program, fetched_at=now)

        assert candidate.title == "Soldiers' Angels - Food Distribution"
        assert "food assistance" in candidate.description.lower()
        assert candidate.org_name == "Soldiers' Angels"
        assert candidate.org_website == "https://soldiersangels.org/food/"
        assert candidate.address == "2895 NE Loop 410"
        assert candidate.city == "San Antonio"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78218"
        assert candidate.hours == "Monthly; check website"
        assert "housing" in candidate.categories
        assert candidate.scope == "national"
        assert candidate.states == ["GA", "TX", "CO"]
        assert "food-assistance" in candidate.tags
        assert "soldiers-angels" in candidate.tags
        assert candidate.phone == "(210) 629-0020"
        assert candidate.raw_data == program

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "nonexistent.json",
        )

        resources = connector.run()
        assert resources == []

    def test_run_empty_data(self, tmp_path):
        """Test that run() handles empty data."""
        data = {"metadata": {}, "programs": []}

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_with_programs(self, tmp_path):
        """Test that run() parses programs correctly."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "org_name": "Test Food Pantry 1",
                    "program_name": "Veteran Food Program",
                    "website": "https://example1.com",
                    "phone": "555-111-1111",
                    "email": None,
                    "address": "100 First St",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78701",
                    "hours": "Monday 9am-12pm",
                    "services": ["food_pantry", "non_perishables"],
                    "eligibility": {"summary": "All veterans"},
                    "scope": "local",
                },
                {
                    "org_name": "Test Food Bank 2",
                    "program_name": "Mobile Pantry",
                    "website": "https://example2.com",
                    "phone": "555-222-2222",
                    "email": "test@example.com",
                    "address": "200 Second Ave",
                    "city": "Denver",
                    "state": "CO",
                    "zip_code": "80201",
                    "hours": "Friday 2pm-5pm",
                    "services": ["mobile_pantry", "fresh_produce"],
                    "eligibility": {"summary": "Veterans and military families"},
                    "scope": "state",
                    "states": ["CO"],
                },
            ],
        }

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Test Food Pantry 1 - Veteran Food Program"
        assert resources[0].org_name == "Test Food Pantry 1"
        assert resources[0].city == "Austin"
        assert resources[0].state == "TX"
        assert resources[0].hours == "Monday 9am-12pm"
        assert "housing" in resources[0].categories

        # Second resource
        assert resources[1].title == "Test Food Bank 2 - Mobile Pantry"
        assert resources[1].org_name == "Test Food Bank 2"
        assert resources[1].city == "Denver"
        assert resources[1].state == "CO"
        assert resources[1].hours == "Friday 2pm-5pm"
        assert resources[1].email == "test@example.com"

    def test_run_with_real_data(self):
        """Test run() with the actual data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_food_assistance.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_food_assistance.json not found in project")

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least 5 programs (acceptance criteria)
        assert len(resources) >= 5

        # All should have food-assistance tag
        assert all("food-assistance" in r.tags for r in resources)

        # All should have housing category (food insecurity tied to housing)
        assert all("housing" in r.categories for r in resources)

        # Check specific programs exist
        titles = [r.title for r in resources]
        assert any("Soldiers' Angels" in t for t in titles)
        assert any("DVNF" in t for t in titles)

        # Check that location info is present for local programs
        local_resources = [r for r in resources if r.scope == "local"]
        for resource in local_resources:
            # Local programs should have city and state at minimum
            assert resource.city is not None, f"{resource.title} missing city"
            assert resource.state is not None, f"{resource.title} missing state"

        # Check first resource structure
        first = resources[0]
        assert first.title
        assert first.description
        assert first.org_name
        assert first.source_url
        assert first.eligibility
        assert first.how_to_apply
        assert first.tags
        assert first.raw_data is not None

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps({"programs": []}))

        with VeteranFoodAssistanceConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_phone_normalization(self, tmp_path):
        """Test that phone numbers are normalized."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )

        # Test 10-digit
        assert connector._normalize_phone("2106290020") == "(210) 629-0020"

        # Test 11-digit with leading 1
        assert connector._normalize_phone("12106290020") == "(210) 629-0020"

        # Test formatted input
        assert connector._normalize_phone("210-629-0020") == "(210) 629-0020"

        # Test None
        assert connector._normalize_phone(None) is None

    def test_format_hours(self, tmp_path):
        """Test hours formatting."""
        connector = VeteranFoodAssistanceConnector(
            data_path=tmp_path / "data.json",
        )

        # Hours should be returned as-is
        assert connector._format_hours("Wednesday 10:00 AM - 12:00 PM") == "Wednesday 10:00 AM - 12:00 PM"
        assert connector._format_hours("Monthly distributions") == "Monthly distributions"
        assert connector._format_hours(None) is None

    def test_complete_location_info(self):
        """Test that programs have complete location information."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_food_assistance.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_food_assistance.json not found in project")

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        # Count programs with complete local addresses
        complete_location_count = 0
        for resource in resources:
            if resource.address and resource.city and resource.state and resource.zip_code:
                complete_location_count += 1

        # At least 5 programs should have complete location info
        assert complete_location_count >= 5, f"Only {complete_location_count} programs have complete location info"

    def test_hours_present(self):
        """Test that programs have hours information."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_food_assistance.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_food_assistance.json not found in project")

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        # All programs should have hours
        for resource in resources:
            assert resource.hours is not None, f"{resource.title} missing hours"

    def test_services_described(self):
        """Test that programs have services described in description."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_food_assistance.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_food_assistance.json not found in project")

        connector = VeteranFoodAssistanceConnector(data_path=data_file)
        resources = connector.run()

        # All programs should mention services in description
        for resource in resources:
            desc_lower = resource.description.lower()
            # Should mention at least one service type
            service_keywords = [
                "food",
                "pantry",
                "distribution",
                "produce",
                "groceries",
                "meals",
                "delivery",
                "snap",
                "nutrition",
            ]
            has_service = any(kw in desc_lower for kw in service_keywords)
            assert has_service, f"{resource.title} description doesn't mention services"
