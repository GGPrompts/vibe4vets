"""Tests for County Veteran Service Officer (CVSO) connector."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.cvso import CVSOConnector


class TestCVSOConnector:
    """Tests for CVSOConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = CVSOConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "County Veteran Service Officers (CVSO)"
        assert meta.tier == 3  # County/state-level
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "nacvso.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = CVSOConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = CVSOConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_cvso_full_data(self):
        """Test parsing a CVSO entry with all fields."""
        connector = CVSOConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_cvso(
            state="TX",
            county="Travis",
            office_name="Travis County Veterans Services",
            officer_name="Roger Stacy",
            address="5501 Airport Blvd, Suite 302",
            city="Austin",
            zip_code="78751",
            phone="(512) 854-9457",
            email="veterans.services@traviscountytx.gov",
            hours="Monday-Friday 8:00 AM - 5:00 PM",
            website="https://www.traviscountytx.gov/veterans-services",
            services=["VA disability claims", "Pension claims", "Healthcare enrollment"],
            fetched_at=now,
        )

        assert candidate.title == "Travis County CVSO (TX)"
        assert "Travis County" in candidate.description
        assert "Roger Stacy" in candidate.description
        assert candidate.org_name == "Travis County Veterans Services"
        assert candidate.org_website == "https://www.traviscountytx.gov/veterans-services"
        assert candidate.address == "5501 Airport Blvd, Suite 302, Austin, TX 78751"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78751"
        assert candidate.phone == "(512) 854-9457"
        assert candidate.email == "veterans.services@traviscountytx.gov"
        assert candidate.hours == "Monday-Friday 8:00 AM - 5:00 PM"
        assert candidate.categories == ["benefits"]
        assert candidate.scope == "local"
        assert candidate.states == ["TX"]
        assert "cvso" in candidate.tags
        assert "county-travis" in candidate.tags
        assert "state-tx" in candidate.tags
        assert candidate.raw_data["county"] == "Travis"
        assert candidate.raw_data["officer_name"] == "Roger Stacy"

    def test_parse_cvso_minimal_data(self):
        """Test parsing a CVSO with minimal data."""
        connector = CVSOConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_cvso(
            state="CA",
            county="Los Angeles",
            office_name=None,
            officer_name=None,
            address=None,
            city=None,
            zip_code=None,
            phone=None,
            email=None,
            hours=None,
            website=None,
            services=[],
            fetched_at=now,
        )

        assert candidate.title == "Los Angeles County Veterans Service Office (CA)"
        assert candidate.org_name == "Los Angeles County Veterans Service Office"
        assert candidate.address is None
        assert candidate.phone is None
        assert "Officer" not in candidate.description  # No vacant officer mentioned
        assert candidate.source_url == "https://www.nacvso.org/county-veterans-service-officers"

    def test_parse_cvso_vacant_officer(self):
        """Test parsing a CVSO with vacant officer position."""
        connector = CVSOConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_cvso(
            state="TX",
            county="Franklin",
            office_name="Franklin County Veterans Service Office",
            officer_name="Vacant",
            address="100 Main St",
            city="Mount Vernon",
            zip_code="75457",
            phone="(903) 537-4252",
            email=None,
            hours=None,
            website=None,
            services=[],
            fetched_at=now,
        )

        # Vacant officer should not be mentioned in description
        assert "Vacant" not in candidate.description
        assert "Current County Veteran Service Officer" not in candidate.description

    def test_build_title_variations(self):
        """Test title building with various inputs."""
        connector = CVSOConnector(data_path="/fake/path.json")

        # With all data
        title = connector._build_title(
            county="Harris",
            state="TX",
            office_name="Harris County Veterans Service Office",
        )
        assert title == "Harris County CVSO (TX)"

        # Without office name
        title = connector._build_title(
            county="Bexar",
            state="TX",
            office_name=None,
        )
        assert title == "Bexar County Veterans Service Office (TX)"

        # Without state
        title = connector._build_title(
            county="Dallas",
            state=None,
            office_name="Dallas County Veterans Office",
        )
        assert "Dallas County" in title

    def test_build_description(self):
        """Test description building."""
        connector = CVSOConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            county="Travis",
            state_name="Texas",
            office_name="Travis County Veterans Services",
            officer_name="Roger Stacy",
            services=["VA disability claims", "Pension claims"],
        )

        assert "Travis County" in desc
        assert "Texas" in desc
        assert "Roger Stacy" in desc
        assert "free assistance" in desc
        assert "VA disability claims" in desc
        assert "Pension claims" in desc

    def test_build_description_no_officer(self):
        """Test description building without officer name."""
        connector = CVSOConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            county="Harris",
            state_name="Texas",
            office_name="Harris County Veterans Services",
            officer_name=None,
            services=[],
        )

        assert "Harris County" in desc
        assert "Current County Veteran Service Officer" not in desc

    def test_build_eligibility(self):
        """Test eligibility text building."""
        connector = CVSOConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility(
            state_name="Texas",
            county="Travis",
        )

        assert "Travis County, Texas" in eligibility
        assert "Veterans" in eligibility
        assert "dependents" in eligibility
        assert "discharge characterization" in eligibility

    def test_build_how_to_apply_with_phone(self):
        """Test how_to_apply with phone number."""
        connector = CVSOConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            county="Travis",
            office_name="Travis County Veterans Services",
            phone="(512) 854-9457",
            email="vets@example.com",
            website="https://example.com",
        )

        assert "(512) 854-9457" in instructions
        assert "schedule an appointment" in instructions
        assert "vets@example.com" in instructions
        assert "https://example.com" in instructions
        assert "DD-214" in instructions

    def test_build_how_to_apply_email_only(self):
        """Test how_to_apply with email only."""
        connector = CVSOConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            county="Harris",
            office_name="Harris County Veterans Services",
            phone=None,
            email="vets@harris.gov",
            website=None,
        )

        assert "Email" in instructions
        assert "vets@harris.gov" in instructions

    def test_build_how_to_apply_no_contact(self):
        """Test how_to_apply without contact info."""
        connector = CVSOConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            county="Dallas",
            office_name=None,
            phone=None,
            email=None,
            website=None,
        )

        assert "Contact" in instructions
        assert "schedule an appointment" in instructions

    def test_build_tags(self):
        """Test tag building."""
        connector = CVSOConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="TX",
            county="Travis",
            services=["VA disability claims", "Pension claims", "Healthcare enrollment"],
        )

        assert "cvso" in tags
        assert "county-veteran-service-officer" in tags
        assert "benefits-assistance" in tags
        assert "va-claims" in tags
        assert "state-tx" in tags
        assert "county-travis" in tags
        assert "disability-claims" in tags
        assert "pension-claims" in tags
        assert "healthcare-enrollment" in tags

    def test_build_tags_no_state(self):
        """Test tag building without state."""
        connector = CVSOConnector(data_path="/fake/path.json")

        tags = connector._build_tags(state=None, county="Test", services=[])

        assert "cvso" in tags
        # No state-specific tag
        state_tags = [t for t in tags if t.startswith("state-")]
        assert not state_tags

    def test_build_tags_county_with_spaces(self):
        """Test tag building with county name containing spaces."""
        connector = CVSOConnector(data_path="/fake/path.json")

        tags = connector._build_tags(state="CA", county="Los Angeles", services=[])

        assert "county-los-angeles" in tags

    def test_get_state_name(self):
        """Test state code to name conversion."""
        connector = CVSOConnector(data_path="/fake/path.json")

        assert connector._get_state_name("TX") == "Texas"
        assert connector._get_state_name("CA") == "California"
        assert connector._get_state_name("NY") == "New York"
        assert connector._get_state_name("DC") == "District of Columbia"
        assert connector._get_state_name(None) is None
        assert connector._get_state_name("XX") is None  # Invalid state

    def test_normalize_phone(self):
        """Test phone number normalization."""
        connector = CVSOConnector(data_path="/fake/path.json")

        # 10-digit phone
        assert connector._normalize_phone("5128549457") == "(512) 854-9457"

        # 11-digit with leading 1
        assert connector._normalize_phone("15128549457") == "(512) 854-9457"

        # Already formatted
        assert connector._normalize_phone("(512) 854-9457") == "(512) 854-9457"

        # With dashes
        assert connector._normalize_phone("512-854-9457") == "(512) 854-9457"

        # None
        assert connector._normalize_phone(None) is None

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = CVSOConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "CVSO data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        import json

        test_data = {
            "source": "Test",
            "cvsos": [
                {
                    "state": "TX",
                    "county": "Travis",
                    "office_name": "Travis County Veterans Services",
                    "officer_name": "Roger Stacy",
                    "address": "5501 Airport Blvd",
                    "city": "Austin",
                    "zip_code": "78751",
                    "phone": "(512) 854-9457",
                    "email": "vets@travis.gov",
                    "hours": "Mon-Fri 8-5",
                    "website": "https://travis.gov/vets",
                    "services": ["VA claims", "Pension"],
                },
                {
                    "state": "CA",
                    "county": "Los Angeles",
                    "office_name": "LA County DMVA",
                    "officer_name": "Ruth Wong",
                    "address": "1816 S Figueroa St",
                    "city": "Los Angeles",
                    "zip_code": "90015",
                    "phone": "(213) 765-9680",
                    "email": None,
                    "hours": "Mon-Fri 8-5",
                    "website": None,
                    "services": ["VA claims"],
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = CVSOConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Travis County CVSO (TX)"
        assert resources[0].states == ["TX"]
        assert resources[0].scope == "local"
        assert resources[0].city == "Austin"

        # Second resource
        assert resources[1].title == "Los Angeles County CVSO (CA)"
        assert resources[1].states == ["CA"]
        assert resources[1].city == "Los Angeles"

    def test_run_with_real_data(self):
        """Test run() with the actual CVSO directory data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "cvso_directory.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("cvso_directory.json not found in project")

        connector = CVSOConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least the seed data (20 CVSOs)
        assert len(resources) >= 20

        # All should be local scope
        assert all(r.scope == "local" for r in resources)

        # All should have cvso tag
        assert all("cvso" in r.tags for r in resources)

        # All should have benefits category
        assert all(r.categories == ["benefits"] for r in resources)

        # Check for expected states in seed data
        states = {r.state for r in resources}
        assert "TX" in states  # Texas has multiple CVSOs
        assert "CA" in states  # California has multiple CVSOs
        assert "OH" in states  # Ohio has multiple CVSOs

        # Check resource structure
        first = resources[0]
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.city is not None
        assert first.state is not None

    def test_all_cvsos_have_benefits_category(self):
        """Test that all CVSO resources have benefits category."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "cvso_directory.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("cvso_directory.json not found in project")

        connector = CVSOConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.categories == ["benefits"]
            assert "cvso" in resource.tags
            assert "benefits-assistance" in resource.tags

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        import json

        test_data = {"cvsos": []}
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        with CVSOConnector(data_path=test_file) as connector:
            resources = connector.run()
            assert resources == []
