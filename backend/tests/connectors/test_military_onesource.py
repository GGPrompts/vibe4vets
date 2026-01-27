"""Tests for Military OneSource transition assistance connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from connectors.military_onesource import MilitaryOneSourceConnector


class TestMilitaryOneSourceConnector:
    """Tests for MilitaryOneSourceConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = MilitaryOneSourceConnector(data_path=tmp_path / "test.yaml")
        meta = connector.metadata

        assert "Military OneSource" in meta.name
        assert meta.tier == 1  # Official DoD program
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "militaryonesource.mil" in meta.url

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when data file doesn't exist."""
        connector = MilitaryOneSourceConnector(data_path=tmp_path / "nonexistent.yaml")
        resources = connector.run()
        assert resources == []

    def test_run_empty_file(self, tmp_path):
        """Test that run() handles empty YAML file."""
        data_file = tmp_path / "empty.yaml"
        data_file.write_text("programs: []")

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()
        assert resources == []

    def test_run_single_program(self, tmp_path):
        """Test parsing a single program."""
        data = {
            "source": {
                "name": "Military OneSource",
                "url": "https://www.militaryonesource.mil/",
                "contact": {
                    "phone": "800-342-9647",
                    "phone_display": "1-800-342-9647",
                },
            },
            "programs": [
                {
                    "id": "test-program",
                    "name": "Test Transition Program",
                    "category": "employment",
                    "description": "A test program for veterans.",
                    "eligibility": [
                        "Active duty service members",
                        "Veterans within 365 days of separation",
                    ],
                    "who_qualifies": {
                        "active_duty": True,
                        "reserve": True,
                        "national_guard": True,
                        "retirees": False,
                        "veterans_365_days": True,
                        "family": False,
                    },
                    "how_to_apply": "Call 1-800-342-9647 to get started.",
                    "tags": ["transition", "employment"],
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert resource.title == "Test Transition Program"
        assert "test program for veterans" in resource.description.lower()
        assert resource.org_name == "Military OneSource"
        assert resource.categories == ["employment"]
        assert resource.scope == "national"
        assert resource.phone == "1-800-342-9647"
        assert resource.hours == "24/7/365"
        assert "military-onesource" in resource.tags
        assert "transition" in resource.tags

    def test_eligibility_from_list(self, tmp_path):
        """Test eligibility text built from explicit list."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test Program",
                    "eligibility": [
                        "Active duty members within 12 months of separation",
                        "Veterans within 365 days of separation date",
                    ],
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        assert "Active duty members" in resources[0].eligibility
        assert "365 days" in resources[0].eligibility

    def test_eligibility_from_who_qualifies(self, tmp_path):
        """Test eligibility text built from who_qualifies flags."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test Program",
                    "who_qualifies": {
                        "active_duty": True,
                        "reserve": True,
                        "national_guard": True,
                        "retirees": True,
                        "veterans_365_days": True,
                        "family": True,
                    },
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        eligibility = resources[0].eligibility.lower()
        assert "active duty" in eligibility
        assert "reserve" in eligibility
        assert "national guard" in eligibility
        assert "retirees" in eligibility
        assert "365 days" in eligibility
        assert "family" in eligibility

    def test_how_to_apply_includes_contact(self, tmp_path):
        """Test that how_to_apply includes contact information."""
        data = {
            "source": {
                "contact": {
                    "phone_display": "1-800-342-9647",
                }
            },
            "programs": [
                {
                    "name": "Test Program",
                    "how_to_apply": "Visit the website to apply.",
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        how_to_apply = resources[0].how_to_apply
        assert "website" in how_to_apply.lower()
        assert "1-800-342-9647" in how_to_apply

    def test_tags_include_eligibility_based_tags(self, tmp_path):
        """Test that tags are generated from eligibility."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test Program",
                    "category": "employment",
                    "who_qualifies": {
                        "active_duty": True,
                        "reserve": True,
                        "veterans_365_days": True,
                        "family": True,
                    },
                    "tags": ["transition", "career"],
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        tags = resources[0].tags
        assert "military-onesource" in tags
        assert "dod-program" in tags
        assert "free-service" in tags
        assert "active-duty" in tags
        assert "guard-reserve" in tags
        assert "transitioning-veterans" in tags
        assert "family-support" in tags
        assert "transition" in tags
        assert "career" in tags
        assert "employment" in tags

    def test_category_validation(self, tmp_path):
        """Test that invalid categories default to training."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test Program",
                    "category": "invalid_category",
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert resources[0].categories == ["training"]

    def test_program_without_name_skipped(self, tmp_path):
        """Test that programs without names are skipped."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "description": "A program without a name",
                },
                {
                    "name": "Valid Program",
                    "description": "A valid program",
                },
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].title == "Valid Program"

    def test_program_specific_source_url(self, tmp_path):
        """Test that program-specific source URLs are used."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "MilTax",
                    "source_url": "https://www.militaryonesource.mil/miltax",
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert resources[0].source_url == "https://www.militaryonesource.mil/miltax"

    def test_all_programs_are_national_scope(self, tmp_path):
        """Test that all programs have national scope."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {"name": "Program 1"},
                {"name": "Program 2"},
                {"name": "Program 3"},
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert all(r.scope == "national" for r in resources)
        assert all(r.states is None for r in resources)

    def test_raw_data_preserved(self, tmp_path):
        """Test that raw program data is preserved."""
        program_data = {
            "id": "test-id",
            "name": "Test Program",
            "category": "employment",
            "custom_field": "custom_value",
        }
        data = {
            "source": {"name": "Test"},
            "programs": [program_data],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert resources[0].raw_data["id"] == "test-id"
        assert resources[0].raw_data["custom_field"] == "custom_value"

    def test_context_manager(self, tmp_path):
        """Test connector works as context manager."""
        data = {
            "source": {"name": "Test"},
            "programs": [{"name": "Test"}],
        }
        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        with MilitaryOneSourceConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert len(resources) == 1

    def test_run_with_real_data(self):
        """Test run() with the actual data file if it exists."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "military_onesource.yaml"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("military_onesource.yaml not found in project")

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        # Should have multiple programs
        assert len(resources) >= 10

        # All should be national scope
        assert all(r.scope == "national" for r in resources)

        # All should have military-onesource tag
        assert all("military-onesource" in r.tags for r in resources)

        # All should have phone number
        assert all(r.phone == "1-800-342-9647" for r in resources)

        # Check categories are valid
        valid_categories = {"employment", "training", "housing", "legal"}
        for r in resources:
            assert all(c in valid_categories for c in r.categories)

        # Check that key programs exist
        titles = [r.title for r in resources]
        assert any("Transition" in t for t in titles)
        assert any("TAP" in t or "Transition Assistance" in t for t in titles)
        assert any("MilTax" in t for t in titles)

        # Check first resource structure
        first = resources[0]
        assert first.title
        assert first.description
        assert first.eligibility
        assert first.how_to_apply
        assert first.org_name == "Military OneSource"

    def test_multiline_description_cleaned(self, tmp_path):
        """Test that multiline YAML descriptions are properly cleaned."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test Program",
                    "description": """This is a multiline
                    description that spans
                    several lines.""",
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        # Description should be cleaned to single line
        desc = resources[0].description
        assert "\n" not in desc
        assert "multiline" in desc
        assert "several lines" in desc


class TestMilitaryOneSourceEligibility:
    """Tests specifically for eligibility text generation."""

    def test_single_eligibility_item(self, tmp_path):
        """Test single eligibility item is returned directly."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test",
                    "eligibility": ["Veterans only"],
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert resources[0].eligibility == "Veterans only"

    def test_default_eligibility(self, tmp_path):
        """Test default eligibility when none specified."""
        data = {
            "source": {"name": "Test"},
            "programs": [{"name": "Test"}],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert "Service members" in resources[0].eligibility


class TestMilitaryOneSourceTags:
    """Tests specifically for tag generation."""

    def test_retiree_tag(self, tmp_path):
        """Test retiree tag is added when eligible."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test",
                    "who_qualifies": {"retirees": True},
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        assert "retirees" in resources[0].tags

    def test_no_duplicate_tags(self, tmp_path):
        """Test that tags are deduplicated."""
        data = {
            "source": {"name": "Test"},
            "programs": [
                {
                    "name": "Test",
                    "tags": ["employment", "employment", "transition"],
                    "category": "employment",
                }
            ],
        }

        data_file = tmp_path / "test.yaml"
        with open(data_file, "w") as f:
            yaml.dump(data, f)

        connector = MilitaryOneSourceConnector(data_path=data_file)
        resources = connector.run()

        tags = resources[0].tags
        assert tags.count("employment") == 1
