"""Tests for SSVF FY26 grantee data connector."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from connectors.ssvf import SSVFConnector


class TestSSVFConnector:
    """Tests for SSVFConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        meta = connector.metadata

        assert meta.name == "SSVF FY26 Grantee Data"
        assert meta.tier == 1  # Official VA program data
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "va.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.xlsx"
        connector = SSVFConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.xlsx")
        connector = SSVFConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_states_single(self):
        """Test parsing a single state."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        states = connector._parse_states("TX")
        assert states == ["TX"]

    def test_parse_states_multiple(self):
        """Test parsing multiple states (semicolon-separated)."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        states = connector._parse_states("AL;FL")
        assert states == ["AL", "FL"]

    def test_parse_states_three(self):
        """Test parsing three states."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        states = connector._parse_states("CA;NV;AZ")
        assert states == ["CA", "NV", "AZ"]

    def test_parse_states_empty(self):
        """Test parsing empty/None states."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        assert connector._parse_states(None) == []
        assert connector._parse_states("") == []

    def test_parse_grantee_single_state(self):
        """Test parsing a single-state grantee."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw="TX",
            grant_id="12-TX-001",
            org_name="Texas Veterans Housing",
            award_amount=1500000,
            visn="VISN 17: VA Heart of Texas Network",
            fetched_at=now,
        )

        assert candidate.title == "SSVF - Texas Veterans Housing (TX)"
        assert "Texas Veterans Housing" in candidate.description
        assert "$1,500,000" in candidate.description
        assert candidate.org_name == "Texas Veterans Housing"
        assert candidate.categories == ["housing"]
        assert candidate.scope == "state"
        assert candidate.states == ["TX"]
        assert "ssvf" in candidate.tags
        assert "grant-12-TX-001" in candidate.tags
        assert "visn-17" in candidate.tags
        assert candidate.raw_data["grant_id"] == "12-TX-001"
        assert candidate.raw_data["award_amount"] == 1500000

    def test_parse_grantee_multi_state(self):
        """Test parsing a multi-state grantee."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw="AL;FL",
            grant_id="14-ZZ-153",
            org_name="United Way of Central Alabama",
            award_amount=7905048,
            visn="VISN 7: VA Southeast Network;VISN 16: South Central VA Health Care Network",
            fetched_at=now,
        )

        assert candidate.title == "SSVF - United Way of Central Alabama (Multi-State)"
        assert "AL, FL" in candidate.description
        assert "$7,905,048" in candidate.description
        assert candidate.scope == "regional"
        assert candidate.states == ["AL", "FL"]

    def test_parse_grantee_no_state(self):
        """Test parsing a grantee with no state (should be national scope)."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw=None,
            grant_id="12-XX-001",
            org_name="National Veterans Org",
            award_amount=2000000,
            visn=None,
            fetched_at=now,
        )

        assert candidate.title == "SSVF - National Veterans Org"
        assert candidate.scope == "national"
        assert candidate.states is None

    def test_parse_grantee_no_award_amount(self):
        """Test parsing a grantee with no award amount."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw="CA",
            grant_id="12-CA-001",
            org_name="California Veterans Services",
            award_amount=None,
            visn="VISN 21: Sierra Pacific Network",
            fetched_at=now,
        )

        assert "Undisclosed" in candidate.description

    def test_build_description_single_state(self):
        """Test description building for single state."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")

        desc = connector._build_description(
            org_name="Test Org",
            states=["TX"],
            award_str="$1,000,000",
        )

        assert "Test Org is an SSVF" in desc
        assert "Serves veterans in TX" in desc
        assert "rapid re-housing" in desc
        assert "$1,000,000" in desc

    def test_build_description_multi_state(self):
        """Test description building for multiple states."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")

        desc = connector._build_description(
            org_name="Regional Org",
            states=["VA", "MD", "DC"],
            award_str="$5,000,000",
        )

        assert "Regional Org" in desc
        assert "Serves veterans across VA, MD, DC" in desc

    def test_build_description_no_state(self):
        """Test description building with no state."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")

        desc = connector._build_description(
            org_name="National Org",
            states=[],
            award_str="$10,000,000",
        )

        assert "National Org" in desc
        # No state-specific message
        assert "Serves veterans in" not in desc
        assert "Serves veterans across" not in desc

    def test_build_tags(self):
        """Test tag building."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")

        tags = connector._build_tags(
            grant_id="12-TX-001",
            visn="VISN 17: VA Heart of Texas Network",
        )

        assert "ssvf" in tags
        assert "housing" in tags
        assert "homeless-services" in tags
        assert "rapid-rehousing" in tags
        assert "veteran-families" in tags
        assert "grant-12-TX-001" in tags
        assert "visn-17" in tags

    def test_build_tags_no_grant_id(self):
        """Test tag building with no grant ID."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")

        tags = connector._build_tags(grant_id=None, visn=None)

        assert "ssvf" in tags
        assert not any(t.startswith("grant-") for t in tags)
        assert not any(t.startswith("visn-") for t in tags)

    def test_eligibility_text(self):
        """Test that eligibility text is present and accurate."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw="TX",
            grant_id="12-TX-001",
            org_name="Test Org",
            award_amount=1000000,
            visn=None,
            fetched_at=now,
        )

        assert "50% of Area Median Income" in candidate.eligibility
        assert "veteran families" in candidate.eligibility
        assert "homeless" in candidate.eligibility

    def test_how_to_apply_text(self):
        """Test that how_to_apply text includes contact info."""
        connector = SSVFConnector(data_path="/fake/path.xlsx")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            states_raw="TX",
            grant_id="12-TX-001",
            org_name="Test Org",
            award_amount=1000000,
            visn=None,
            fetched_at=now,
        )

        assert "1-877-4AID-VET" in candidate.how_to_apply
        assert "1-877-424-3838" in candidate.how_to_apply

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = SSVFConnector(data_path=tmp_path / "nonexistent.xlsx")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "SSVF data file not found" in str(exc_info.value)

    @patch("connectors.ssvf.openpyxl")
    def test_run_parses_spreadsheet(self, mock_openpyxl, tmp_path):
        """Test that run() parses the spreadsheet correctly."""
        # Create mock workbook and sheet
        mock_sheet = MagicMock()
        mock_sheet.iter_rows.return_value = [
            ("AK", "12-AK-001", "Catholic Social Services", 1780844, "VISN 20: Northwest Network"),
            ("AL;FL", "14-ZZ-153", "United Way", 7905048, "VISN 7;VISN 16"),
            (None, None, None, None, None),  # Empty row to skip
        ]

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet
        mock_openpyxl.load_workbook.return_value = mock_workbook

        # Create a dummy file so exists() passes
        test_file = tmp_path / "test.xlsx"
        test_file.touch()

        connector = SSVFConnector(data_path=test_file)
        resources = connector.run()

        # Should have 2 resources (empty row skipped)
        assert len(resources) == 2

        # First resource - single state
        assert resources[0].title == "SSVF - Catholic Social Services (AK)"
        assert resources[0].states == ["AK"]
        assert resources[0].scope == "state"

        # Second resource - multi-state
        assert resources[1].title == "SSVF - United Way (Multi-State)"
        assert resources[1].states == ["AL", "FL"]
        assert resources[1].scope == "regional"

        # Verify workbook was closed
        mock_workbook.close.assert_called_once()

    def test_run_with_real_data(self):
        """Test run() with the actual SSVF FY26 data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "SSVF_FY26_Awards.xlsx"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("SSVF_FY26_Awards.xlsx not found in project")

        connector = SSVFConnector(data_path=data_file)
        resources = connector.run()

        # Should have 235 resources based on issue description
        assert len(resources) >= 200  # Allow some flexibility

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have SSVF tag
        assert all("ssvf" in r.tags for r in resources)

        # Check for multi-state grantees (we know there are some)
        multi_state = [r for r in resources if r.scope == "regional"]
        assert len(multi_state) > 0

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("SSVF - ")
        assert first.source_url == "https://www.va.gov/homeless/ssvf/"
        assert first.eligibility is not None
        assert first.how_to_apply is not None
