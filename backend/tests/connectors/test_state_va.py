"""Tests for State VA agency connector."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.state_va import StateVAConnector


class TestStateVAConnector:
    """Tests for StateVAConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = StateVAConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "State VA Agencies (NASDVA)"
        assert meta.tier == 3  # State-level agencies
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "nasdva.us" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = StateVAConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = StateVAConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_agency(self):
        """Test parsing a state agency entry."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="TX",
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            director="Thomas Palladino",
            website="https://www.tvc.texas.gov/",
            fetched_at=now,
        )

        assert candidate.title == "Texas Veterans Commission"
        assert "Texas Veterans Commission" in candidate.description
        assert "Thomas Palladino" in candidate.description
        assert candidate.org_name == "Texas Veterans Commission"
        assert candidate.org_website == "https://www.tvc.texas.gov/"
        assert "employment" in candidate.categories
        assert "housing" in candidate.categories
        assert "legal" in candidate.categories
        assert "training" in candidate.categories
        assert candidate.scope == "state"
        assert candidate.states == ["TX"]
        assert "state-va" in candidate.tags
        assert "state-tx" in candidate.tags
        assert candidate.raw_data["director"] == "Thomas Palladino"

    def test_parse_agency_no_director(self):
        """Test parsing an agency without director info."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="CA",
            state_name="California",
            agency_name="California Department of Veterans Affairs",
            director=None,
            website="https://www.calvet.ca.gov/",
            fetched_at=now,
        )

        assert "Director" not in candidate.description
        assert candidate.raw_data["director"] is None

    def test_parse_agency_no_website(self):
        """Test parsing an agency without website."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="GU",
            state_name="Guam",
            agency_name="Guam Veterans Affairs Office",
            director="Jose San Agustin",
            website=None,
            fetched_at=now,
        )

        assert candidate.source_url == "https://nasdva.us/resources/"
        assert candidate.org_website is None

    def test_parse_agency_no_agency_name(self):
        """Test parsing an agency without agency name."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="XX",
            state_name="Test Territory",
            agency_name=None,
            director="Test Director",
            website=None,
            fetched_at=now,
        )

        assert candidate.title == "Test Territory Veterans Affairs"
        assert candidate.org_name == "Test Territory Veterans Affairs"

    def test_build_description(self):
        """Test description building."""
        connector = StateVAConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            director="Thomas Palladino",
        )

        assert "Texas Veterans Commission" in desc
        assert "official state agency" in desc
        assert "Texas" in desc
        assert "Thomas Palladino" in desc
        assert "field offices" in desc

    def test_build_description_no_director(self):
        """Test description building without director."""
        connector = StateVAConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            state_name="California",
            agency_name="California Department of Veterans Affairs",
            director=None,
        )

        assert "California" in desc
        assert "Director" not in desc

    def test_build_description_no_agency_name(self):
        """Test description building without agency name."""
        connector = StateVAConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            state_name="Oregon",
            agency_name=None,
            director="Test Director",
        )

        assert "Oregon" in desc
        assert "official state veteran affairs agency" in desc.lower()

    def test_build_tags(self):
        """Test tag building."""
        connector = StateVAConnector(data_path="/fake/path.json")

        tags = connector._build_tags(state="FL")

        assert "state-va" in tags
        assert "state-benefits" in tags
        assert "veteran-services" in tags
        assert "claims-assistance" in tags
        assert "nasdva" in tags
        assert "state-fl" in tags

    def test_build_tags_no_state(self):
        """Test tag building with no state."""
        connector = StateVAConnector(data_path="/fake/path.json")

        tags = connector._build_tags(state=None)

        assert "state-va" in tags
        excluded_prefixes = [
            t for t in tags
            if t.startswith("state-") and t not in ("state-va", "state-benefits")
        ]
        assert not excluded_prefixes

    def test_eligibility_text(self):
        """Test that eligibility text is present and accurate."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="TX",
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            director="Thomas Palladino",
            website="https://www.tvc.texas.gov/",
            fetched_at=now,
        )

        assert "Veterans residing in Texas" in candidate.eligibility
        assert "state benefits" in candidate.eligibility
        assert "federal VA benefits" in candidate.eligibility

    def test_how_to_apply_text(self):
        """Test that how_to_apply text includes website."""
        connector = StateVAConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_agency(
            state="TX",
            state_name="Texas",
            agency_name="Texas Veterans Commission",
            director="Thomas Palladino",
            website="https://www.tvc.texas.gov/",
            fetched_at=now,
        )

        assert "www.tvc.texas.gov" in candidate.how_to_apply
        assert "Texas Veterans Commission" in candidate.how_to_apply

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = StateVAConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "State VA data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        import json

        test_data = {
            "source": "Test",
            "agencies": [
                {
                    "state": "TX",
                    "state_name": "Texas",
                    "agency_name": "Texas Veterans Commission",
                    "director": "Thomas Palladino",
                    "website": "https://www.tvc.texas.gov/",
                },
                {
                    "state": "CA",
                    "state_name": "California",
                    "agency_name": "California Department of Veterans Affairs",
                    "director": "Lindsey Sin",
                    "website": "https://www.calvet.ca.gov/",
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = StateVAConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Texas Veterans Commission"
        assert resources[0].states == ["TX"]
        assert resources[0].scope == "state"

        # Second resource
        assert resources[1].title == "California Department of Veterans Affairs"
        assert resources[1].states == ["CA"]

    def test_run_with_real_data(self):
        """Test run() with the actual state VA agencies data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "state_va_agencies.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("state_va_agencies.json not found in project")

        connector = StateVAConnector(data_path=data_file)
        resources = connector.run()

        # Should have 50 states + DC + territories (56 total)
        assert len(resources) >= 50

        # All should be state scope
        assert all(r.scope == "state" for r in resources)

        # All should have state-va tag
        assert all("state-va" in r.tags for r in resources)

        # Check for expected states
        states = {r.state for r in resources}
        assert "TX" in states
        assert "CA" in states
        assert "NY" in states
        assert "FL" in states
        assert "DC" in states  # District of Columbia

        # Check for territories
        assert "PR" in states  # Puerto Rico
        assert "GU" in states  # Guam

        # Check resource structure
        first = resources[0]
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.categories == ["employment", "training", "housing", "legal"]

    def test_all_states_have_categories(self):
        """Test that all state VA resources cover all major categories."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "state_va_agencies.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("state_va_agencies.json not found in project")

        connector = StateVAConnector(data_path=data_file)
        resources = connector.run()

        expected_categories = {"employment", "training", "housing", "legal"}
        for resource in resources:
            assert set(resource.categories) == expected_categories
