"""Tests for DAV (Disabled American Veterans) chapters connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.dav_chapters import DAVChaptersConnector


class TestDAVChaptersConnector:
    """Tests for DAVChaptersConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "DAV Chapters and National Service Offices"
        assert meta.tier == 2  # Established nonprofit VSO
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "locators.dav.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = DAVChaptersConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = DAVChaptersConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_chapter(self):
        """Test title building for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        title = connector._build_title(
            location_type="chapter",
            chapter_number="17",
            name="Chapter 17",
            city="Austin",
            state="TX",
        )

        assert title == "DAV Chapter 17 (Austin, TX)"

    def test_build_title_chapter_with_name(self):
        """Test title building for chapter with custom name."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        title = connector._build_title(
            location_type="chapter",
            chapter_number="5",
            name="Alamo Chapter 5",
            city="San Antonio",
            state="TX",
        )

        assert title == "DAV Alamo Chapter 5 (San Antonio, TX)"

    def test_build_title_nso(self):
        """Test title building for National Service Office."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        title = connector._build_title(
            location_type="nso",
            chapter_number=None,
            name="Houston Regional Office",
            city="Houston",
            state="TX",
        )

        assert title == "DAV National Service Office (Houston, TX)"

    def test_build_title_tso(self):
        """Test title building for Transition Service Office."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        title = connector._build_title(
            location_type="tso",
            chapter_number=None,
            name="Fort Bragg Transition Office",
            city="Fort Liberty",
            state="NC",
        )

        assert title == "DAV Transition Services - Fort Bragg Transition Office (Fort Liberty, NC)"

    def test_build_title_transportation(self):
        """Test title building for transportation network."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        title = connector._build_title(
            location_type="transportation",
            chapter_number=None,
            name="Erie VA Transportation Network",
            city="Erie",
            state="PA",
        )

        assert title == "DAV Transportation - Erie VA Transportation Network (Erie, PA)"

    def test_build_description_chapter(self):
        """Test description building for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            location_type="chapter",
            name="Chapter 17",
            city="Austin",
            state_name="Texas",
            services=["VA claims assistance", "Peer support", "Transportation to VA"],
            meeting_schedule="Second Saturday of each month at 10:00 AM",
            has_transportation=True,
            va_facility_served="Austin VA Outpatient Clinic",
        )

        assert "DAV" in desc
        assert "Disabled American Veterans" in desc
        assert "Austin" in desc
        assert "Texas" in desc
        assert "peer support" in desc.lower()
        assert "VA claims assistance" in desc
        assert "Transportation Network" in desc
        assert "Second Saturday" in desc

    def test_build_description_nso(self):
        """Test description building for NSO."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            location_type="nso",
            name="Houston Regional Office",
            city="Houston",
            state_name="Texas",
            services=["VA claims assistance", "Appeals representation"],
            meeting_schedule=None,
            has_transportation=False,
            va_facility_served=None,
        )

        assert "National Service Office" in desc
        assert "free, professional" in desc.lower()
        assert "VA-certified" in desc
        assert "claims" in desc.lower()

    def test_build_description_transportation(self):
        """Test description building for transportation."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            location_type="transportation",
            name="Erie VA Transportation Network",
            city="Erie",
            state_name="Pennsylvania",
            services=["Free rides to VA appointments"],
            meeting_schedule=None,
            has_transportation=True,
            va_facility_served="Erie VA Medical Center",
        )

        assert "Transportation Network" in desc
        assert "free rides" in desc.lower()
        assert "Erie VA Medical Center" in desc
        assert "235,000" in desc

    def test_build_eligibility_chapter(self):
        """Test eligibility for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility(location_type="chapter")

        assert "service-connected disability" in elig.lower()
        assert "membership" in elig.lower()
        assert "ALL veterans" in elig

    def test_build_eligibility_nso(self):
        """Test eligibility for NSO."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility(location_type="nso")

        assert "FREE" in elig
        assert "ALL veterans" in elig
        assert "regardless of DAV membership" in elig

    def test_build_eligibility_transportation(self):
        """Test eligibility for transportation."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility(location_type="transportation")

        assert "any veteran" in elig.lower()
        assert "VA medical facility" in elig
        assert "No membership" in elig
        assert "free of charge" in elig.lower()

    def test_build_how_to_apply_chapter(self):
        """Test how to apply for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        how = connector._build_how_to_apply(
            location_type="chapter",
            name="Chapter 17",
            phone="(512) 339-0015",
            email="davchapter17austin@gmail.com",
            website=None,
            meeting_schedule="Second Saturday of each month",
        )

        assert "Chapter 17" in how
        assert "(512) 339-0015" in how
        assert "1-877-426-2838" in how
        assert "I AM A VET" in how
        assert "Second Saturday" in how

    def test_build_how_to_apply_transportation(self):
        """Test how to apply for transportation."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        how = connector._build_how_to_apply(
            location_type="transportation",
            name="Erie Transportation",
            phone="(814) 860-2576",
            email=None,
            website=None,
            meeting_schedule=None,
        )

        assert "schedule a free ride" in how.lower()
        assert "1-877-426-2838" in how
        assert "(814) 860-2576" in how

    def test_build_tags_chapter(self):
        """Test tag building for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            location_type="chapter",
            state="TX",
            services=["VA claims assistance", "Transportation to VA"],
            has_transportation=True,
        )

        assert "dav" in tags
        assert "disabled-american-veterans" in tags
        assert "vso" in tags
        assert "dav-chapter" in tags
        assert "peer-support" in tags
        assert "dav-transportation" in tags
        assert "free-rides" in tags
        assert "state-tx" in tags
        assert "va-claims-assistance" in tags

    def test_build_tags_nso(self):
        """Test tag building for NSO."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            location_type="nso",
            state="DC",
            services=["VA claims assistance", "Appeals representation"],
            has_transportation=False,
        )

        assert "national-service-office" in tags
        assert "va-claims-assistance" in tags
        assert "benefits-advocacy" in tags
        assert "state-dc" in tags

    def test_build_tags_transportation(self):
        """Test tag building for transportation."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            location_type="transportation",
            state="PA",
            services=["Free rides to VA appointments"],
            has_transportation=True,
        )

        assert "transportation" in tags
        assert "free-rides" in tags
        assert "medical-appointments" in tags

    def test_build_org_name_chapter(self):
        """Test org name building for chapter."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        org_name = connector._build_org_name(
            location_type="chapter",
            chapter_number="17",
            name=None,
        )

        assert org_name == "DAV Chapter 17"

    def test_build_org_name_with_dav_in_name(self):
        """Test org name building when DAV is already in name."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        org_name = connector._build_org_name(
            location_type="chapter",
            chapter_number="17",
            name="DAV Austin Chapter 17",
        )

        # Should not duplicate "DAV"
        assert org_name == "DAV Austin Chapter 17"

    def test_get_locator_url(self):
        """Test locator URL for different location types."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        assert "ChapterUnitLocator" in connector._get_locator_url("chapter")
        assert "NsoLocator" in connector._get_locator_url("nso")
        assert "NsoLocator" in connector._get_locator_url("tso")
        assert "transportation-network" in connector._get_locator_url("transportation")

    def test_parse_location_chapter(self):
        """Test parsing a chapter location."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_location(
            location_type="chapter",
            chapter_number="17",
            name="Chapter 17",
            address="2741 Brockton Drive",
            city="Austin",
            state="TX",
            zip_code="78758",
            phone="(512) 339-0015",
            email="davchapter17austin@gmail.com",
            website=None,
            services=["VA claims assistance", "Benefits counseling"],
            meeting_schedule="Second Saturday at 10:00 AM",
            hours="By appointment",
            contact_name=None,
            has_transportation=False,
            va_facility_served=None,
            fetched_at=now,
        )

        assert candidate.title == "DAV Chapter 17 (Austin, TX)"
        assert candidate.categories == ["benefits", "supportServices"]
        assert "dav" in candidate.tags
        assert "dav-chapter" in candidate.tags
        assert candidate.scope == "local"
        assert candidate.states == ["TX"]
        assert candidate.phone == "(512) 339-0015"
        assert candidate.raw_data["location_type"] == "chapter"
        assert candidate.raw_data["chapter_number"] == "17"

    def test_parse_location_nso(self):
        """Test parsing an NSO location."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_location(
            location_type="nso",
            chapter_number=None,
            name="Houston Regional Office",
            address="6900 Almeda Road",
            city="Houston",
            state="TX",
            zip_code="77021",
            phone="(713) 383-2727",
            email="houstonnso@dav.org",
            website="https://www.dav.org",
            services=["VA claims assistance", "Appeals representation"],
            meeting_schedule=None,
            hours="Mon-Fri 8:00 AM - 4:30 PM",
            contact_name=None,
            has_transportation=False,
            va_facility_served=None,
            fetched_at=now,
        )

        assert "National Service Office" in candidate.title
        assert candidate.categories == ["benefits", "supportServices"]
        assert "national-service-office" in candidate.tags
        assert candidate.hours == "Mon-Fri 8:00 AM - 4:30 PM"

    def test_parse_location_transportation(self):
        """Test parsing a transportation location."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_location(
            location_type="transportation",
            chapter_number=None,
            name="Erie VA Transportation Network",
            address="135 E 38th Street",
            city="Erie",
            state="PA",
            zip_code="16504",
            phone="(814) 860-2576",
            email=None,
            website="https://www.dav.org/get-help-now/dav-transportation-network/",
            services=["Free rides to VA appointments"],
            meeting_schedule=None,
            hours="Mon-Fri 6:00 AM - 5:00 PM",
            contact_name=None,
            has_transportation=True,
            va_facility_served="Erie VA Medical Center",
            fetched_at=now,
        )

        assert "Transportation" in candidate.title
        assert "transportation" in candidate.tags
        assert "free-rides" in candidate.tags
        assert candidate.raw_data["va_facility_served"] == "Erie VA Medical Center"

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = DAVChaptersConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "DAV chapters data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON correctly."""
        test_data = {
            "source": "DAV locators",
            "locations": [
                {
                    "location_type": "chapter",
                    "chapter_number": "17",
                    "name": "Chapter 17",
                    "address": "2741 Brockton Drive",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78758",
                    "phone": "(512) 339-0015",
                    "email": "davchapter17@gmail.com",
                    "website": None,
                    "services": ["VA claims assistance"],
                    "meeting_schedule": "Second Saturday at 10:00 AM",
                    "hours": "By appointment",
                    "contact_name": None,
                    "has_transportation": False,
                    "va_facility_served": None,
                },
                {
                    "location_type": "nso",
                    "chapter_number": None,
                    "name": "Houston Regional Office",
                    "address": "6900 Almeda Road",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77021",
                    "phone": "(713) 383-2727",
                    "email": "houstonnso@dav.org",
                    "website": "https://www.dav.org",
                    "services": ["VA claims assistance", "Appeals representation"],
                    "meeting_schedule": None,
                    "hours": "Mon-Fri 8:00 AM - 4:30 PM",
                    "contact_name": None,
                    "has_transportation": False,
                    "va_facility_served": None,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = DAVChaptersConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource - chapter
        assert "Chapter 17" in resources[0].title
        assert resources[0].states == ["TX"]
        assert "dav-chapter" in resources[0].tags

        # Second resource - NSO
        assert "National Service Office" in resources[1].title
        assert "national-service-office" in resources[1].tags

    def test_run_with_real_data(self):
        """Test run() with the actual DAV chapters data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "dav_chapters.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("dav_chapters.json not found in project")

        connector = DAVChaptersConnector(data_path=data_file)
        resources = connector.run()

        # Should have multiple resources
        assert len(resources) >= 10

        # All should have benefits and supportServices categories
        assert all("benefits" in r.categories for r in resources)
        assert all("supportServices" in r.categories for r in resources)

        # All should have DAV tag
        assert all("dav" in r.tags for r in resources)

        # Check for different location types
        location_types = {r.raw_data.get("location_type") for r in resources}
        assert "chapter" in location_types
        assert "nso" in location_types

        # Check first resource structure
        first = resources[0]
        assert "DAV" in first.title
        assert first.eligibility is not None
        assert first.how_to_apply is not None

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with DAVChaptersConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "DAV Chapters and National Service Offices"

    def test_normalize_phone(self):
        """Test phone number normalization."""
        connector = DAVChaptersConnector(data_path="/fake/path.json")

        assert connector._normalize_phone("5123390015") == "(512) 339-0015"
        assert connector._normalize_phone("15123390015") == "(512) 339-0015"
        assert connector._normalize_phone("(512) 339-0015") == "(512) 339-0015"
        assert connector._normalize_phone(None) is None
