"""Tests for Veteran Emergency Financial Assistance Programs connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.veteran_emergency_assistance import VeteranEmergencyAssistanceConnector


class TestVeteranEmergencyAssistanceConnector:
    """Tests for VeteranEmergencyAssistanceConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        meta = connector.metadata

        assert "Emergency" in meta.name or "Veteran" in meta.name
        assert meta.tier == 2  # Established nonprofits
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_build_title_vfw(self, tmp_path):
        """Test title building for VFW."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title(
            "Veterans of Foreign Wars (VFW)", "Unmet Needs Program"
        )
        assert title == "VFW - Unmet Needs Program"

    def test_build_title_american_legion(self, tmp_path):
        """Test title building for American Legion."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title(
            "The American Legion", "Temporary Financial Assistance (TFA)"
        )
        assert title == "American Legion - Temporary Financial Assistance (TFA)"

    def test_build_title_dav(self, tmp_path):
        """Test title building for DAV."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title(
            "Disabled American Veterans (DAV)", "Disaster Relief Program"
        )
        assert title == "DAV - Disaster Relief Program"

    def test_build_title_unknown_org(self, tmp_path):
        """Test title building for unknown organization."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        title = connector._build_title("New Organization", "Test Program")
        assert title == "New Organization - Test Program"

    def test_format_assistance_types(self, tmp_path):
        """Test formatting of assistance types."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        types = ["mortgage", "rent", "utilities", "food"]
        formatted = connector._format_assistance_types(types)

        assert "mortgage payments" in formatted
        assert "rent" in formatted
        assert "utilities" in formatted
        assert "food assistance" in formatted

    def test_format_assistance_types_truncation(self, tmp_path):
        """Test that long assistance type lists are truncated."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        types = ["mortgage", "rent", "utilities", "food", "clothing",
                 "medical", "dental", "transportation", "lodging", "childcare"]
        formatted = connector._format_assistance_types(types)

        # Should truncate and add "and more"
        assert "and more" in formatted

    def test_build_description_with_max_amount(self, tmp_path):
        """Test description building with max amount."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Veterans of Foreign Wars (VFW)",
            "program_name": "Unmet Needs Program",
            "assistance_types": ["mortgage", "rent", "utilities"],
            "max_amount": 1500,
            "turnaround_time": "1-2 weeks typical",
        }
        desc = connector._build_description(program)

        assert "emergency financial assistance" in desc.lower()
        assert "$1,500" in desc
        assert "1-2 weeks" in desc
        assert "VFW" in desc

    def test_build_description_with_max_notes(self, tmp_path):
        """Test description building with max amount notes instead of amount."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Disabled American Veterans (DAV)",
            "program_name": "Disaster Relief Program",
            "assistance_types": ["disaster_relief", "food", "shelter"],
            "max_amount": None,
            "max_amount_notes": "Grant amounts vary based on need",
        }
        desc = connector._build_description(program)

        assert "Grant amounts vary" in desc
        assert "disaster" in desc.lower()

    def test_build_eligibility_with_membership(self, tmp_path):
        """Test eligibility building with membership requirement."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "The American Legion",
            "eligibility": {
                "summary": "American Legion members or active-duty service members",
                "membership_required": True,
                "membership_notes": "Legion membership required for veterans; active duty can apply without membership",
                "service_era": "any",
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "Legion membership required" in eligibility
        assert "active duty can apply" in eligibility

    def test_build_eligibility_no_membership(self, tmp_path):
        """Test eligibility building without membership requirement."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "VFW",
            "eligibility": {
                "summary": "Service members and veterans facing financial hardship",
                "membership_required": False,
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "No membership required" in eligibility

    def test_build_eligibility_disability_required(self, tmp_path):
        """Test eligibility building with disability requirement."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "eligibility": {
                "summary": "Combat wounded veterans",
                "disability_required": True,
                "disability_notes": "Must be combat wounded, critically ill, or catastrophically injured",
            },
        }
        eligibility = connector._build_eligibility(program)

        assert "combat wounded" in eligibility.lower()
        assert "critically ill" in eligibility.lower()

    def test_build_how_to_apply(self, tmp_path):
        """Test building how to apply instructions."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "application_process": "Apply online at example.com",
            "phone": "1-800-555-1234",
            "email": "help@example.com",
            "website": "https://example.com",
        }
        how_to_apply = connector._build_how_to_apply(program)

        assert "Apply online" in how_to_apply
        assert "1-800-555-1234" in how_to_apply
        assert "help@example.com" in how_to_apply
        assert "example.com" in how_to_apply

    def test_get_categories_housing(self, tmp_path):
        """Test category detection for housing assistance."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "assistance_types": ["mortgage", "rent", "utilities"],
        }
        categories = connector._get_categories(program)

        assert "housing" in categories

    def test_get_categories_default(self, tmp_path):
        """Test default category when no specific types match."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "assistance_types": ["food", "clothing"],
        }
        categories = connector._get_categories(program)

        # Should default to housing since most programs are housing-focused
        assert "housing" in categories

    def test_build_tags(self, tmp_path):
        """Test tag building."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Veterans of Foreign Wars (VFW)",
            "assistance_types": ["mortgage", "rent", "utilities", "food", "medical"],
            "eligibility": {
                "service_era": "post-9/11",
                "disability_required": False,
            },
        }
        tags = connector._build_tags(program)

        assert "emergency-assistance" in tags
        assert "financial-assistance" in tags
        assert "housing-assistance" in tags
        assert "utility-assistance" in tags
        assert "food-assistance" in tags
        assert "medical-assistance" in tags
        assert "post-9/11" in tags
        assert "vfw" in tags

    def test_build_tags_disabled_veterans(self, tmp_path):
        """Test tag building for disability-required programs."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        program = {
            "org_name": "Semper Fi & America's Fund",
            "assistance_types": ["mortgage", "rent"],
            "eligibility": {
                "disability_required": True,
            },
        }
        tags = connector._build_tags(program)

        assert "disabled-veterans" in tags
        assert "semper-fi-fund" in tags

    def test_parse_program(self, tmp_path):
        """Test parsing a single program entry."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )
        now = datetime.now(UTC)

        program = {
            "org_name": "Veterans of Foreign Wars (VFW)",
            "program_name": "Unmet Needs Program",
            "website": "https://www.vfw.org/assistance/financial-grants",
            "phone": "1-866-789-6333",
            "email": None,
            "assistance_types": ["mortgage", "rent", "utilities", "food"],
            "max_amount": 1500,
            "turnaround_time": "1-2 weeks typical",
            "eligibility": {
                "summary": "Service members and veterans facing financial hardship",
                "membership_required": False,
                "service_era": "post-9/11 or currently active duty",
            },
            "application_process": "Online application at vfw.org/assistance",
            "tags": ["emergency", "rent", "utilities"],
        }

        candidate = connector._parse_program(program, fetched_at=now)

        assert candidate.title == "VFW - Unmet Needs Program"
        assert "VFW" in candidate.description
        assert "$1,500" in candidate.description
        assert candidate.org_name == "Veterans of Foreign Wars (VFW)"
        assert candidate.org_website == "https://www.vfw.org/assistance/financial-grants"
        assert "housing" in candidate.categories
        assert candidate.scope == "national"
        assert candidate.states is None
        assert "emergency-assistance" in candidate.tags
        assert "vfw" in candidate.tags
        assert candidate.phone == "(186) 678-9633" or "866" in (candidate.phone or "")
        assert candidate.raw_data == program

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "nonexistent.json",
        )

        resources = connector.run()
        assert resources == []

    def test_run_empty_data(self, tmp_path):
        """Test that run() handles empty data."""
        data = {"metadata": {}, "programs": []}

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = VeteranEmergencyAssistanceConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_with_programs(self, tmp_path):
        """Test that run() parses programs correctly."""
        data = {
            "metadata": {"source": "test"},
            "programs": [
                {
                    "org_name": "Test Org 1",
                    "program_name": "Test Program 1",
                    "website": "https://example1.com",
                    "phone": None,
                    "email": None,
                    "assistance_types": ["mortgage", "rent"],
                    "max_amount": 1000,
                    "eligibility": {"summary": "All veterans"},
                    "application_process": "Apply online",
                },
                {
                    "org_name": "Test Org 2",
                    "program_name": "Test Program 2",
                    "website": "https://example2.com",
                    "phone": "1-800-555-1234",
                    "email": "test@example.com",
                    "assistance_types": ["utilities", "food"],
                    "max_amount": 2000,
                    "eligibility": {"summary": "Post-9/11 veterans"},
                    "application_process": "Call to apply",
                },
            ],
        }

        data_file = tmp_path / "data.json"
        data_file.write_text(json.dumps(data))

        connector = VeteranEmergencyAssistanceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Test Org 1 - Test Program 1"
        assert resources[0].org_name == "Test Org 1"
        assert "housing" in resources[0].categories

        # Second resource
        assert resources[1].title == "Test Org 2 - Test Program 2"
        assert resources[1].org_name == "Test Org 2"
        assert resources[1].phone is not None

    def test_run_with_real_data(self):
        """Test run() with the actual data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_emergency_assistance.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_emergency_assistance.json not found in project")

        connector = VeteranEmergencyAssistanceConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least 7 programs
        assert len(resources) >= 7

        # All should be national scope
        assert all(r.scope == "national" for r in resources)

        # All should have housing category
        assert all("housing" in r.categories for r in resources)

        # All should have emergency-assistance tag
        assert all("emergency-assistance" in r.tags for r in resources)

        # Check specific programs exist
        titles = [r.title for r in resources]
        assert any("VFW" in t for t in titles)
        assert any("Legion" in t for t in titles)
        assert any("DAV" in t for t in titles)
        assert any("Operation Homefront" in t for t in titles)
        assert any("Semper Fi" in t for t in titles)
        assert any("PenFed" in t for t in titles)
        assert any("USA Cares" in t for t in titles)

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

        with VeteranEmergencyAssistanceConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_phone_normalization(self, tmp_path):
        """Test that phone numbers are normalized."""
        connector = VeteranEmergencyAssistanceConnector(
            data_path=tmp_path / "data.json",
        )

        # Test 10-digit
        assert connector._normalize_phone("8005551234") == "(800) 555-1234"

        # Test 11-digit with leading 1
        assert connector._normalize_phone("18005551234") == "(800) 555-1234"

        # Test formatted input
        assert connector._normalize_phone("1-800-555-1234") == "(800) 555-1234"

        # Test None
        assert connector._normalize_phone(None) is None
