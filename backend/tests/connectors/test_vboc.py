"""Tests for SBA Veterans Business Outreach Center (VBOC) connector."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.vboc import VBOCConnector


class TestVBOCConnector:
    """Tests for VBOCConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VBOCConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "SBA Veterans Business Outreach Centers"
        assert meta.tier == 1  # Official federal government source
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "sba.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = VBOCConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = VBOCConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_single_state(self):
        """Test title building for single state."""
        connector = VBOCConnector(data_path="/fake/path.json")
        title = connector._build_title("Florida VBOC", ["FL"])
        assert title == "Florida VBOC (FL)"

    def test_build_title_two_states(self):
        """Test title building for two states."""
        connector = VBOCConnector(data_path="/fake/path.json")
        title = connector._build_title("Pacific Northwest VBOC", ["WA", "OR"])
        assert title == "Pacific Northwest VBOC (WA, OR)"

    def test_build_title_three_states(self):
        """Test title building for three states."""
        connector = VBOCConnector(data_path="/fake/path.json")
        title = connector._build_title("Great Lakes VBOC", ["IL", "MN", "WI"])
        assert title == "Great Lakes VBOC (IL, MN, WI)"

    def test_build_title_multi_state(self):
        """Test title building for many states."""
        connector = VBOCConnector(data_path="/fake/path.json")
        title = connector._build_title("New England VBOC", ["CT", "ME", "MA", "NH", "RI", "VT"])
        assert title == "New England VBOC (Multi-State)"

    def test_build_description_with_host_org(self):
        """Test description building with host organization."""
        connector = VBOCConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Texas VBOC",
            host_org="University of Texas",
            states_served=["TX"],
            region_description=None,
        )

        assert "Texas VBOC" in desc
        assert "University of Texas" in desc
        assert "SBA Veterans Business Outreach Center" in desc
        assert "business counseling" in desc
        assert "Boots to Business" in desc
        assert "Serves veterans in TX" in desc

    def test_build_description_with_region(self):
        """Test description building with regional description."""
        connector = VBOCConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="NorCal VBOC",
            host_org="Valley Sierra SBDC",
            states_served=["CA"],
            region_description="Northern California",
        )

        assert "NorCal VBOC" in desc
        assert "Serves Northern California" in desc

    def test_build_description_multi_state(self):
        """Test description building for multi-state coverage."""
        connector = VBOCConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Southeast VBOC",
            host_org="Mississippi State University",
            states_served=["AL", "LA", "MS"],
            region_description=None,
        )

        assert "Serves veterans across AL, LA, MS" in desc

    def test_build_tags(self):
        """Test tag building."""
        connector = VBOCConnector(data_path="/fake/path.json")

        tags = connector._build_tags({"name": "Test VBOC", "host_org": "Test Organization"})

        assert "vboc" in tags
        assert "sba" in tags
        assert "small-business" in tags
        assert "entrepreneurship" in tags
        assert "self-employment" in tags
        assert "boots-to-business" in tags

    def test_build_tags_university_partnership(self):
        """Test tag building for university-hosted VBOCs."""
        connector = VBOCConnector(data_path="/fake/path.json")

        tags = connector._build_tags({"name": "Test VBOC", "host_org": "University of Texas"})

        assert "university-partnership" in tags

    def test_build_tags_college_partnership(self):
        """Test tag building for college-hosted VBOCs."""
        connector = VBOCConnector(data_path="/fake/path.json")

        tags = connector._build_tags({"name": "Test VBOC", "host_org": "Gulf Coast State College"})

        assert "university-partnership" in tags

    def test_eligibility_text(self):
        """Test that eligibility text is present and accurate."""
        connector = VBOCConnector(data_path="/fake/path.json")
        eligibility = connector._get_eligibility()

        assert "Veterans" in eligibility
        assert "service members" in eligibility
        assert "military spouses" in eligibility
        assert "free" in eligibility
        assert "discharge status" in eligibility

    def test_how_to_apply_text(self):
        """Test that how_to_apply text includes contact info."""
        connector = VBOCConnector(data_path="/fake/path.json")

        how_to_apply = connector._get_how_to_apply({"website": "https://example.com/vboc"})

        assert "Contact the VBOC directly" in how_to_apply
        assert "https://example.com/vboc" in how_to_apply
        assert "sba.gov/vboc" in how_to_apply
        assert "1-800-827-5722" in how_to_apply

    def test_parse_center_single_state(self):
        """Test parsing a single-state center."""
        connector = VBOCConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        center = {
            "name": "Florida VBOC",
            "host_org": "Gulf Coast State College",
            "states_served": ["FL"],
            "address": "5230 US Hwy. 98",
            "city": "Panama City",
            "state": "FL",
            "zip": "32401",
            "phone": "850-769-1551",
            "email": "vboc@gulfcoast.edu",
            "website": "https://www.vboc.org",
        }

        candidate = connector._parse_center(center, fetched_at=now)

        assert candidate is not None
        assert candidate.title == "Florida VBOC (FL)"
        assert "Gulf Coast State College" in candidate.description
        assert candidate.org_name == "Gulf Coast State College"
        assert candidate.categories == ["employment"]
        assert candidate.scope == "state"
        assert candidate.states == ["FL"]
        assert "vboc" in candidate.tags
        assert "sba" in candidate.tags
        assert candidate.city == "Panama City"
        assert candidate.zip_code == "32401"
        assert candidate.phone == "(850) 769-1551"
        assert candidate.email == "vboc@gulfcoast.edu"

    def test_parse_center_multi_state(self):
        """Test parsing a multi-state center."""
        connector = VBOCConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        center = {
            "name": "New England VBOC",
            "host_org": "Center for Women & Enterprise",
            "states_served": ["CT", "ME", "MA", "NH", "RI", "VT"],
            "address": "69 Milk St. Suite 217",
            "city": "Westborough",
            "state": "MA",
            "zip": "01581",
            "phone": "844-582-2461",
            "email": "info@vbocnewengland.org",
            "website": "https://www.vbocnewengland.org",
        }

        candidate = connector._parse_center(center, fetched_at=now)

        assert candidate is not None
        assert candidate.title == "New England VBOC (Multi-State)"
        assert candidate.scope == "regional"
        assert candidate.states == ["CT", "ME", "MA", "NH", "RI", "VT"]
        assert "CT, ME, MA, NH, RI, VT" in candidate.description

    def test_parse_center_regional(self):
        """Test parsing a regional (2-3 state) center."""
        connector = VBOCConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        center = {
            "name": "Mid-Atlantic VBOC",
            "host_org": "University of Maryland",
            "states_served": ["DC", "MD", "DE"],
            "address": "4600 River Rd.",
            "city": "Riverdale",
            "state": "MD",
            "zip": "20737",
            "phone": "301-405-6071",
            "email": "veteranbusiness@umd.edu",
            "website": "https://www.midatlanticvboc.com",
        }

        candidate = connector._parse_center(center, fetched_at=now)

        assert candidate is not None
        assert candidate.title == "Mid-Atlantic VBOC (DC, MD, DE)"
        assert candidate.scope == "regional"
        assert candidate.states == ["DC", "MD", "DE"]

    def test_parse_center_missing_name(self):
        """Test parsing a center with missing name returns None."""
        connector = VBOCConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        center = {"host_org": "Some Organization", "states_served": ["TX"]}

        candidate = connector._parse_center(center, fetched_at=now)
        assert candidate is None

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = VBOCConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "VBOC data file not found" in str(exc_info.value)

    def test_run_with_mock_data(self, tmp_path):
        """Test that run() parses JSON correctly."""
        import json

        test_data = {
            "source": "SBA Veterans Business Outreach Centers",
            "centers": [
                {
                    "name": "Test VBOC 1",
                    "host_org": "Test Org 1",
                    "states_served": ["TX"],
                    "address": "123 Main St",
                    "city": "Austin",
                    "state": "TX",
                    "zip": "78701",
                    "phone": "512-555-1234",
                    "email": "test1@example.com",
                    "website": "https://test1.example.com",
                },
                {
                    "name": "Test VBOC 2",
                    "host_org": "Test Org 2",
                    "states_served": ["CA", "NV", "AZ"],
                    "address": "456 Oak Ave",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90001",
                    "phone": "213-555-5678",
                    "email": "test2@example.com",
                    "website": "https://test2.example.com",
                },
            ],
        }

        test_file = tmp_path / "test_vboc.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VBOCConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource - single state
        assert resources[0].title == "Test VBOC 1 (TX)"
        assert resources[0].states == ["TX"]
        assert resources[0].scope == "state"
        assert resources[0].categories == ["employment"]

        # Second resource - multi-state
        assert resources[1].title == "Test VBOC 2 (CA, NV, AZ)"
        assert resources[1].states == ["CA", "NV", "AZ"]
        assert resources[1].scope == "regional"

    def test_run_with_real_data(self):
        """Test run() with the actual VBOC data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vboc_centers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vboc_centers.json not found in project")

        connector = VBOCConnector(data_path=data_file)
        resources = connector.run()

        # Should have 31 VBOCs per SBA website
        assert len(resources) == 31

        # All should be employment category
        assert all("employment" in r.categories for r in resources)

        # All should have VBOC and SBA tags
        assert all("vboc" in r.tags for r in resources)
        assert all("sba" in r.tags for r in resources)

        # All should have self-employment tag
        assert all("self-employment" in r.tags for r in resources)

        # Check for multi-state coverage (we know there are some)
        multi_state = [r for r in resources if r.scope == "regional"]
        assert len(multi_state) > 0

        # Check first resource structure
        first = resources[0]
        assert first.title
        assert first.description
        assert first.source_url
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.org_name

        # Check that all resources have valid states
        for r in resources:
            if r.states:
                for state in r.states:
                    assert len(state) == 2  # All should be 2-letter codes

    def test_context_manager(self):
        """Test connector works as context manager."""
        with VBOCConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "SBA Veterans Business Outreach Centers"
