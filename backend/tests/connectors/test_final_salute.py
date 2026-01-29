"""Tests for Final Salute Inc. women veterans housing connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.final_salute import FinalSaluteConnector


class TestFinalSaluteConnector:
    """Tests for FinalSaluteConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Final Salute Inc. Women Veterans Housing"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "finalsaluteinc.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = FinalSaluteConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = FinalSaluteConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_description(self):
        """Test description building."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        location = {
            "services": ["Transitional housing", "Case management", "Mentorship"],
            "coverage": {
                "primary_region": "DC/Northern Virginia/Southern Maryland",
                "national_reach": True,
            },
        }
        programs = [
            {"name": "H.O.M.E. Program"},
            {"name": "S.A.F.E. Program"},
            {"name": "Next Uniform"},
        ]

        desc = connector._build_description(location, programs, "(866) 472-5883")

        assert "women veterans" in desc.lower()
        assert "children" in desc.lower()
        assert "H.O.M.E. Program" in desc
        assert "S.A.F.E. Program" in desc
        assert "nationwide" in desc.lower()
        assert "(866) 472-5883" in desc

    def test_build_eligibility(self):
        """Test eligibility building."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        eligibility_data = {
            "gender": "Women veterans only",
            "housing_status": ["Currently homeless", "Facing homelessness"],
            "children_accepted": True,
            "notes": "Programs available nationwide",
        }

        elig = connector._build_eligibility(eligibility_data)

        assert "Women veterans only" in elig
        assert "homeless" in elig.lower()
        assert "Children are welcome" in elig
        assert "nationwide" in elig.lower()

    def test_build_eligibility_no_children(self):
        """Test eligibility when children not mentioned."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        eligibility_data = {
            "gender": "Women veterans only",
        }

        elig = connector._build_eligibility(eligibility_data)

        assert "Women veterans only" in elig
        assert "Children are welcome" not in elig

    def test_build_how_to_apply(self):
        """Test how to apply text."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        location = {
            "phone": "(703) 224-8843",
            "hours": "Monday - Friday: 8:00 AM - 5:00 PM EST",
        }

        how = connector._build_how_to_apply(location, "(866) 472-5883")

        assert "(703) 224-8843" in how
        assert "(866) 472-5883" in how
        assert "8:00 AM" in how
        assert "finalsaluteinc.org" in how

    def test_build_tags(self):
        """Test tag building."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        location = {
            "id": "final-salute-headquarters",
            "type": "headquarters",
            "coverage": {"national_reach": True},
            "services": ["Employment support", "Financial assistance"],
        }

        tags = connector._build_tags(location)

        assert "final-salute" in tags
        assert "women-veterans" in tags
        assert "transitional" in tags
        assert "families-with-children" in tags
        assert "homeless-services" in tags
        assert "mst-support" in tags
        assert "national-program" in tags
        assert "headquarters" in tags
        assert "employment-services" in tags
        assert "financial-assistance" in tags

    def test_build_tags_minimal(self):
        """Test tag building with minimal data."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")

        location = {}
        tags = connector._build_tags(location)

        # Should still have core tags
        assert "final-salute" in tags
        assert "women-veterans" in tags
        assert "transitional" in tags

    def test_parse_location(self):
        """Test parsing a location into ResourceCandidate."""
        connector = FinalSaluteConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        location = {
            "id": "final-salute-headquarters",
            "name": "Final Salute Inc. Headquarters",
            "type": "headquarters",
            "address": "2800 Eisenhower Ave, Suite 220",
            "city": "Alexandria",
            "state": "VA",
            "zip_code": "22314",
            "phone": "(703) 224-8843",
            "hours": "Monday - Friday: 8:00 AM - 5:00 PM EST",
            "services": ["Intake and referrals", "H.O.M.E. Program"],
            "coverage": {
                "primary_region": "DC/Northern Virginia/Southern Maryland",
                "national_reach": True,
            },
        }

        programs = [{"name": "H.O.M.E. Program"}]
        eligibility_data = {"gender": "Women veterans only", "children_accepted": True}

        candidate = connector._parse_location(
            location,
            "(866) 472-5883",
            programs,
            eligibility_data,
            now,
        )

        assert "Women Veterans Housing" in candidate.title
        assert candidate.org_name == "Final Salute Inc."
        assert candidate.city == "Alexandria"
        assert candidate.state == "VA"
        assert candidate.zip_code == "22314"
        assert candidate.phone == "(703) 224-8843"
        assert candidate.categories == ["housing"]
        assert candidate.scope == "national"
        assert "women-veterans" in candidate.tags
        assert "final-salute" in candidate.tags

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = FinalSaluteConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "Final Salute data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON correctly."""
        test_data = {
            "source": "Final Salute Inc.",
            "national_phone": "(866) 472-5883",
            "programs": [
                {"name": "H.O.M.E. Program"},
                {"name": "S.A.F.E. Program"},
            ],
            "eligibility": {
                "gender": "Women veterans only",
                "children_accepted": True,
            },
            "locations": [
                {
                    "id": "test-location",
                    "name": "Test Location",
                    "city": "Alexandria",
                    "state": "VA",
                    "zip_code": "22314",
                    "phone": "(703) 224-8843",
                    "coverage": {"national_reach": True},
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = FinalSaluteConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1

        resource = resources[0]
        assert "Women Veterans Housing" in resource.title
        assert resource.state == "VA"
        assert resource.scope == "national"
        assert "women-veterans" in resource.tags
        assert "housing" in resource.categories

    def test_run_with_real_data(self):
        """Test run() with the actual Final Salute data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "final_salute_locations.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("final_salute_locations.json not found in project")

        connector = FinalSaluteConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least 1 resource (headquarters)
        assert len(resources) >= 1

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have women-veterans tag
        assert all("women-veterans" in r.tags for r in resources)

        # Check first resource structure
        first = resources[0]
        assert "Women Veterans Housing" in first.title
        assert first.source_url == "https://www.finalsaluteinc.org/"
        assert first.org_name == "Final Salute Inc."
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert "final-salute" in first.tags

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with FinalSaluteConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "Final Salute Inc. Women Veterans Housing"

    def test_women_veterans_tags_present(self, tmp_path):
        """Test that women-veterans specific tags are always present."""
        test_data = {
            "national_phone": "(866) 472-5883",
            "programs": [],
            "eligibility": {},
            "locations": [
                {
                    "id": "test",
                    "name": "Test",
                    "city": "Test City",
                    "state": "VA",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = FinalSaluteConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        tags = resources[0].tags

        # These tags should always be present for Final Salute
        assert "women-veterans" in tags
        assert "transitional" in tags
        assert "families-with-children" in tags
        assert "mst-support" in tags

    def test_phone_normalization(self, tmp_path):
        """Test phone number normalization."""
        test_data = {
            "national_phone": "8664725883",  # No formatting
            "programs": [],
            "eligibility": {},
            "locations": [
                {
                    "id": "test",
                    "name": "Test",
                    "phone": "7032248843",  # No formatting
                    "city": "Alexandria",
                    "state": "VA",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = FinalSaluteConnector(data_path=test_file)
        resources = connector.run()

        # Phone should be normalized
        assert resources[0].phone == "(703) 224-8843"
