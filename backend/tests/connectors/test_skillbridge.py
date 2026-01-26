"""Tests for DOD SkillBridge connector."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from connectors.skillbridge import SkillBridgeConnector


class TestSkillBridgeConnector:
    """Tests for SkillBridgeConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")
        meta = connector.metadata

        assert meta.name == "DOD SkillBridge Partner Directory"
        assert meta.tier == 1  # Official DOD program data
        assert meta.frequency == "weekly"
        assert meta.requires_auth is False
        assert "skillbridge.osd.mil" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.csv"
        connector = SkillBridgeConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.csv")
        connector = SkillBridgeConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_init_fetch_fresh_default(self):
        """Test fetch_fresh defaults to False."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")
        assert connector.fetch_fresh is False

    def test_init_fetch_fresh_true(self):
        """Test fetch_fresh can be set to True."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv", fetch_fresh=True)
        assert connector.fetch_fresh is True

    def test_clean_text(self):
        """Test text cleaning."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        assert connector._clean_text("  hello  world  ") == "hello world"
        assert connector._clean_text(None) == ""
        assert connector._clean_text("") == ""
        assert connector._clean_text("normal text") == "normal text"

    def test_build_title_online(self):
        """Test title building for online programs."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        title = connector._build_title(
            program="Test Program",
            city="New York",
            state="NY",
            delivery="Online",
        )

        assert title == "SkillBridge: Test Program (Online)"

    def test_build_title_hybrid(self):
        """Test title building for hybrid programs shows location, not Online."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        title = connector._build_title(
            program="Test Program",
            city="New York",
            state="NY",
            delivery="Hybrid (In-Person and Online)",
        )

        assert title == "SkillBridge: Test Program (New York, NY)"

    def test_build_title_in_person(self):
        """Test title building for in-person programs."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        title = connector._build_title(
            program="Test Program",
            city="Austin",
            state="TX",
            delivery="In-person",
        )

        assert title == "SkillBridge: Test Program (Austin, TX)"

    def test_build_title_state_only(self):
        """Test title building when only state is provided."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        title = connector._build_title(
            program="Test Program",
            city="",
            state="CA",
            delivery="In-person",
        )

        assert title == "SkillBridge: Test Program (CA)"

    def test_build_description_with_summary(self):
        """Test description building with summary."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        desc = connector._build_description(
            program="Test Program",
            summary="This is a test summary.",
            job_desc="Detailed job description here.",
            duration="91 - 120 days",
            job_family="Technology",
            delivery="In-person",
        )

        assert "DOD SkillBridge program" in desc
        assert "This is a test summary." in desc
        assert "Duration: 91 - 120 days" in desc
        assert "Career Field: Technology" in desc
        assert "Format: In-person" in desc

    def test_build_description_fallback_to_job_desc(self):
        """Test description falls back to job_desc when no summary."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        desc = connector._build_description(
            program="Test Program",
            summary="",
            job_desc="This is the job description.",
            duration="151 - 180 days",
            job_family="Healthcare",
            delivery="Online",
        )

        assert "This is the job description." in desc

    def test_parse_job_states_nationwide(self):
        """Test parsing nationwide job states."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        # Nationwide returns empty list (indicating national scope)
        states = connector._parse_job_states("Nationwide (All States)", "TX")
        assert states == []

    def test_parse_job_states_list(self):
        """Test parsing comma-separated states."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        states = connector._parse_job_states("VA, MD, DC", "")
        assert "VA" in states
        assert "MD" in states
        assert "DC" in states

    def test_parse_job_states_fallback(self):
        """Test fallback to training state when no job states."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        states = connector._parse_job_states("", "TX")
        assert states == ["TX"]

    def test_determine_scope_online(self):
        """Test scope determination for online programs."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        scope = connector._determine_scope(["TX"], "Online")
        assert scope == "national"

    def test_determine_scope_single_state(self):
        """Test scope determination for single state."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        scope = connector._determine_scope(["TX"], "In-person")
        assert scope == "state"

    def test_determine_scope_regional(self):
        """Test scope determination for regional (2-5 states)."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        scope = connector._determine_scope(["VA", "MD", "DC"], "In-person")
        assert scope == "regional"

    def test_determine_scope_national(self):
        """Test scope determination for national (many states or empty)."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        scope = connector._determine_scope([], "In-person")
        assert scope == "national"

    def test_build_eligibility_all_services(self):
        """Test eligibility text for all services."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        eligibility = connector._build_eligibility(
            service="All Services",
            mocs="All MOCs",
            eligibility_factors="",
            other="",
        )

        assert "180 days of separation" in eligibility
        assert "Open to all military branches" in eligibility

    def test_build_eligibility_specific_service(self):
        """Test eligibility text for specific service."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        eligibility = connector._build_eligibility(
            service="Army, Navy",
            mocs="11B, 25B",
            eligibility_factors="Security clearance required",
            other="Additional info",
        )

        assert "Open to: Army, Navy" in eligibility
        assert "Target MOCs: 11B, 25B" in eligibility
        assert "Security clearance required" in eligibility
        assert "Additional info" in eligibility

    def test_build_how_to_apply_with_poc(self):
        """Test how to apply with POC info."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        how_to = connector._build_how_to_apply(
            poc_name="John Smith",
            poc_email="john@example.com",
        )

        assert "Education Services Officer" in how_to
        assert "DD Form 2648" in how_to
        assert "John Smith" in how_to
        assert "john@example.com" in how_to
        assert "skillbridge.osd.mil" in how_to

    def test_build_how_to_apply_email_only(self):
        """Test how to apply with email only."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        how_to = connector._build_how_to_apply(
            poc_name="",
            poc_email="contact@example.com",
        )

        assert "contact@example.com" in how_to

    def test_build_tags_basic(self):
        """Test basic tag building."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        tags = connector._build_tags(
            job_family="Technology",
            delivery="In-person",
            duration="151 - 180 days",
            service="All Services",
            mocs="All MOCs",
        )

        assert "skillbridge" in tags
        assert "dod" in tags
        assert "transition" in tags
        assert "employment" in tags
        assert "training" in tags
        assert "in-person" in tags
        assert "technology" in tags
        assert "all-branches" in tags

    def test_build_tags_with_specific_branches(self):
        """Test tag building with specific military branches."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        tags = connector._build_tags(
            job_family="Healthcare",
            delivery="Online",
            duration="91 - 120 days",
            service="Army, Air Force, Marine Corps",
            mocs="68W",
        )

        assert "online" in tags
        assert "healthcare" in tags
        assert "army" in tags
        assert "air-force" in tags
        assert "marine-corps" in tags

    def test_build_tags_hybrid_delivery(self):
        """Test tag building with hybrid delivery."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        tags = connector._build_tags(
            job_family="Construction",
            delivery="Hybrid (In-Person and Online)",
            duration="61 - 90 days",
            service="Navy",
            mocs="",
        )

        assert "hybrid" in tags
        assert "navy" in tags

    def test_parse_row_basic(self):
        """Test parsing a basic row."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")
        now = datetime.now(UTC)

        # Create a row with all required columns
        row = [
            "",  # Partner/Program
            "Test Program Name",  # Partner/Program - Sub
            "All Services",  # Service
            "Austin",  # City
            "TX",  # State
            "151 - 180 days",  # Duration
            "John Smith",  # POC Name
            "john@example.com",  # POC Email
            "Fort Hood",  # Closest Installation
            "TX",  # Job States
            "In-person",  # Delivery Method
            "All MOCs",  # Target MOCs
            "No prerequisites",  # Other Eligibility
            "Additional notes",  # Other
            "This is the job description",  # Job Description
            "Summary of the program",  # Summary
            "Technology",  # Job Family
            "Test Organization",  # MOU Organization
        ]

        candidate = connector._parse_row(row, "Test Organization", now)

        assert candidate is not None
        assert candidate.title == "SkillBridge: Test Program Name (Austin, TX)"
        assert candidate.org_name == "Test Organization"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.categories == ["employment", "training"]
        assert "skillbridge" in candidate.tags
        assert candidate.scope == "state"
        assert candidate.states == ["TX"]
        assert candidate.email == "john@example.com"
        assert "Summary of the program" in candidate.description

    def test_parse_row_no_program(self):
        """Test parsing returns None for row without program."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")
        now = datetime.now(UTC)

        # Row with empty program
        row = [
            "",  # Partner/Program
            "",  # Partner/Program - Sub (empty)
            "All Services",
            "Austin",
            "TX",
            "151 - 180 days",
            "",
            "",
            "",
            "TX",
            "In-person",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]

        candidate = connector._parse_row(row, "Test Org", now)
        assert candidate is None

    def test_create_unique_id(self):
        """Test unique ID creation for deduplication."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        row = [
            "",
            "Test Program",
            "",
            "Austin",
            "TX",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]

        unique_id = connector._create_unique_id(row, "Test Org")
        assert unique_id == "test org|test program|austin|tx"

    def test_context_manager(self):
        """Test context manager properly closes resources."""
        with SkillBridgeConnector(data_path="/fake/path.csv") as connector:
            # Access the client to create it
            connector._get_client()
            assert connector._client is not None

        # After context exit, client should be closed
        assert connector._client is None

    @patch("connectors.skillbridge.httpx.Client")
    def test_fetch_from_sheets(self, mock_client_class):
        """Test fetching data from Google Sheets."""
        mock_client = mock_client_class.return_value
        mock_response = mock_client.get.return_value
        mock_response.text = "Header1,Header2\nValue1,Value2"
        mock_response.raise_for_status.return_value = None

        connector = SkillBridgeConnector(data_path="/fake/path.csv")
        csv_data = connector._fetch_from_sheets()

        assert "Header1" in csv_data
        mock_client.get.assert_called_once()

    def test_load_from_file(self, tmp_path):
        """Test loading data from local file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("Header1,Header2\nValue1,Value2")

        connector = SkillBridgeConnector(data_path=test_file)
        csv_data = connector._load_from_file()

        assert "Header1" in csv_data
        assert "Value1" in csv_data

    def test_load_from_file_not_found(self):
        """Test FileNotFoundError for missing file."""
        connector = SkillBridgeConnector(data_path="/nonexistent/path.csv")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector._load_from_file()

        assert "SkillBridge data file not found" in str(exc_info.value)

    def test_parse_csv_data(self):
        """Test parsing CSV data."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        # Build CSV with line continuations for readability
        header = (
            "Partner/Program,Partner/Program - Sub,Service,City,State,"
            "Duration of Training,Employer POC,POC Email,Closest Installation,"
            "Locations of Prospective Jobs by State,Delivery Method,Target MOCs,"
            "Other Eligibility Factors,Other,Job Description,Summary Description,"
            "Job Family,MOU Organization,"
        )
        org_row = "Test Org,,,,,,,,,,,,,,,,,,"
        prog_row = (
            ",Test Program,All Services,Austin,TX,151 - 180 days,John Smith,"
            "john@example.com,,TX,In-person,All MOCs,,,Job desc,Summary,"
            "Technology,Test Org,"
        )
        csv_data = f"{header}\n{org_row}\n{prog_row}"

        resources = connector._parse_csv_data(csv_data)

        assert len(resources) == 1
        assert resources[0].title == "SkillBridge: Test Program (Austin, TX)"
        assert resources[0].org_name == "Test Org"

    def test_parse_csv_data_deduplication(self):
        """Test that duplicate rows are deduplicated."""
        connector = SkillBridgeConnector(data_path="/fake/path.csv")

        # Build CSV with line continuations for readability
        header = (
            "Partner/Program,Partner/Program - Sub,Service,City,State,"
            "Duration of Training,Employer POC,POC Email,Closest Installation,"
            "Locations of Prospective Jobs by State,Delivery Method,Target MOCs,"
            "Other Eligibility Factors,Other,Job Description,Summary Description,"
            "Job Family,MOU Organization,"
        )
        org_row = "Test Org,,,,,,,,,,,,,,,,,,"
        prog_row = (
            ",Test Program,All Services,Austin,TX,151 - 180 days,John Smith,"
            "john@example.com,,TX,In-person,All MOCs,,,Job desc,Summary,"
            "Technology,Test Org,"
        )
        csv_data = f"{header}\n{org_row}\n{prog_row}\n{prog_row}"

        resources = connector._parse_csv_data(csv_data)

        # Should only have 1 resource despite 2 identical rows
        assert len(resources) == 1

    def test_run_with_real_data(self):
        """Test run() with the actual SkillBridge data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "skillbridge_partners.csv"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("skillbridge_partners.csv not found in project")

        connector = SkillBridgeConnector(data_path=data_file)
        resources = connector.run()

        # Should have thousands of resources
        assert len(resources) >= 1000

        # All should be employment/training category
        assert all("employment" in r.categories for r in resources)
        assert all("training" in r.categories for r in resources)

        # All should have skillbridge tag
        assert all("skillbridge" in r.tags for r in resources)

        # Check delivery method variety
        online = [r for r in resources if "online" in r.tags]
        in_person = [r for r in resources if "in-person" in r.tags]
        hybrid = [r for r in resources if "hybrid" in r.tags]
        assert len(online) > 0
        assert len(in_person) > 0
        assert len(hybrid) > 0

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("SkillBridge: ")
        assert first.source_url == "https://skillbridge.osd.mil/locations.htm"
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert "180 days" in first.eligibility
