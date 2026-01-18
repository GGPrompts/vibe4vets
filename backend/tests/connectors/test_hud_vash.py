"""Tests for HUD-VASH 2024 voucher awards data connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.hud_vash import HUDVASHConnector


class TestHUDVASHConnector:
    """Tests for HUDVASHConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "HUD-VASH 2024 Voucher Awards"
        assert meta.tier == 1  # Official HUD/VA program data
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "hud.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = HUDVASHConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = HUDVASHConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_extract_state_valid(self):
        """Test extracting state from valid PHA code."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        assert connector._extract_state("CA004") == "CA"
        assert connector._extract_state("TX901") == "TX"
        assert connector._extract_state("NY005") == "NY"

    def test_extract_state_guam(self):
        """Test extracting state from Guam PHA code."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        assert connector._extract_state("GQ901") == "GQ"

    def test_extract_state_invalid(self):
        """Test extracting state from invalid PHA codes."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        assert connector._extract_state(None) is None
        assert connector._extract_state("") is None
        assert connector._extract_state("X") is None
        assert connector._extract_state("ZZ999") is None  # Invalid state code

    def test_parse_vamc_standard(self):
        """Test parsing standard VAMC string."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        visn, name = connector._parse_vamc("V22/Phoenix")
        assert visn == "V22"
        assert name == "Phoenix"

    def test_parse_vamc_with_hcs(self):
        """Test parsing VAMC string with HCS suffix."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        visn, name = connector._parse_vamc("V21/Northern California HCS")
        assert visn == "V21"
        assert name == "Northern California HCS"

    def test_parse_vamc_none(self):
        """Test parsing None VAMC."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        visn, name = connector._parse_vamc(None)
        assert visn is None
        assert name is None

    def test_parse_vamc_no_slash(self):
        """Test parsing VAMC without slash."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        visn, name = connector._parse_vamc("Portland")
        assert visn is None
        assert name == "Portland"

    def test_build_title_with_vamc_and_state(self):
        """Test title building with VAMC name and state."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        title = connector._build_title(
            pha_name="Housing Authority of Los Angeles",
            vamc_name="Greater Los Angeles HCS",
            state="CA",
        )
        assert title == "HUD-VASH - Greater Los Angeles HCS (CA)"

    def test_build_title_with_pha_only(self):
        """Test title building with PHA name only."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        title = connector._build_title(
            pha_name="Phoenix Housing Authority",
            vamc_name=None,
            state="AZ",
        )
        assert title == "HUD-VASH - Phoenix Housing Authority (AZ)"

    def test_build_title_minimal(self):
        """Test title building with minimal info."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        title = connector._build_title(pha_name=None, vamc_name=None, state=None)
        assert title == "HUD-VASH Housing Voucher Program"

    def test_build_description(self):
        """Test description building."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        desc = connector._build_description(
            pha_name="Housing Authority of Los Angeles",
            vamc_name="Greater Los Angeles HCS",
            state="CA",
            vouchers=250,
            budget=3886200,
        )

        assert "HUD-VASH" in desc
        assert "California" in desc
        assert "Housing Authority of Los Angeles" in desc
        assert "Greater Los Angeles HCS" in desc
        assert "250" in desc
        assert "$3,886,200" in desc
        assert "case management" in desc

    def test_build_description_no_vouchers(self):
        """Test description building without voucher info."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        desc = connector._build_description(
            pha_name="Test PHA",
            vamc_name="Test VAMC",
            state="TX",
            vouchers=None,
            budget=None,
        )

        assert "HUD-VASH" in desc
        assert "Texas" in desc
        # No voucher count mentioned
        assert "award:" not in desc

    def test_build_tags(self):
        """Test tag building."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        tags = connector._build_tags(
            pha_code="CA004",
            visn="V22",
            vamc_name="Greater Los Angeles HCS",
        )

        assert "hud-vash" in tags
        assert "housing-voucher" in tags
        assert "housing" in tags
        assert "homeless-services" in tags
        assert "rental-assistance" in tags
        assert "pha-ca004" in tags
        assert "visn-22" in tags
        assert "vamc-greater-los-angeles-hcs" in tags

    def test_build_tags_minimal(self):
        """Test tag building with minimal info."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        tags = connector._build_tags(pha_code=None, visn=None, vamc_name=None)

        assert "hud-vash" in tags
        assert "housing-voucher" in tags
        assert not any(t.startswith("pha-") for t in tags)
        assert not any(t.startswith("visn-") for t in tags)
        assert not any(t.startswith("vamc-") for t in tags)

    def test_parse_award(self):
        """Test parsing a single award entry."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="CA004",
            pha_name="Housing Authority of the City of Los Angeles",
            vamc="V22/Greater Los Angeles HCS",
            vouchers=250,
            budget=3886200,
            fetched_at=now,
        )

        assert candidate.title == "HUD-VASH - Greater Los Angeles HCS (CA)"
        assert "Housing Authority of the City of Los Angeles" in candidate.description
        assert "$3,886,200" in candidate.description
        assert candidate.org_name == "Housing Authority of the City of Los Angeles"
        assert candidate.categories == ["housing"]
        assert candidate.scope == "local"
        assert candidate.state == "CA"
        assert candidate.states == ["CA"]
        assert "hud-vash" in candidate.tags
        assert "pha-ca004" in candidate.tags
        assert "visn-22" in candidate.tags
        assert candidate.raw_data["pha_code"] == "CA004"
        assert candidate.raw_data["vouchers"] == 250

    def test_eligibility_text(self):
        """Test that eligibility text is present and accurate."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="TX004",
            pha_name="Fort Worth Housing Solutions",
            vamc="V17/Dallas",
            vouchers=10,
            budget=95518,
            fetched_at=now,
        )

        assert "80% of Area Median Income" in candidate.eligibility
        assert "homeless veterans" in candidate.eligibility.lower()
        assert "VA health care" in candidate.eligibility

    def test_how_to_apply_text(self):
        """Test that how_to_apply text includes contact info."""
        connector = HUDVASHConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="FL002",
            pha_name="Housing Authority of St. Petersburg",
            vamc="V08/Bay Pines",
            vouchers=35,
            budget=424448,
            fetched_at=now,
        )

        assert "1-877-4AID-VET" in candidate.how_to_apply
        assert "1-877-424-3838" in candidate.how_to_apply
        assert "HUD-VASH coordinator" in candidate.how_to_apply
        assert "Public Housing Authority" in candidate.how_to_apply

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = HUDVASHConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "HUD-VASH data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON correctly."""
        test_data = {
            "metadata": {"source": "test"},
            "awards": [
                {
                    "pha_code": "CA004",
                    "pha_name": "Housing Authority of Los Angeles",
                    "vamc": "V22/Greater Los Angeles HCS",
                    "vouchers": 250,
                    "budget": 3886200,
                },
                {
                    "pha_code": "TX004",
                    "pha_name": "Fort Worth Housing Solutions",
                    "vamc": "V17/Dallas",
                    "vouchers": 10,
                    "budget": 95518,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = HUDVASHConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource - California
        assert resources[0].title == "HUD-VASH - Greater Los Angeles HCS (CA)"
        assert resources[0].state == "CA"
        assert resources[0].scope == "local"

        # Second resource - Texas
        assert resources[1].title == "HUD-VASH - Dallas (TX)"
        assert resources[1].state == "TX"

    def test_run_with_real_data(self):
        """Test run() with the actual HUD-VASH 2024 data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "HUD_VASH_2024_Awards.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("HUD_VASH_2024_Awards.json not found in project")

        connector = HUDVASHConnector(data_path=data_file)
        resources = connector.run()

        # Should have ~140+ resources (some PHAs have multiple VAMC partnerships)
        assert len(resources) >= 100

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have HUD-VASH tag
        assert all("hud-vash" in r.tags for r in resources)

        # All should have local scope
        assert all(r.scope == "local" for r in resources)

        # Check state coverage - should have multiple states represented
        states = {r.state for r in resources if r.state}
        assert len(states) >= 20  # Should cover most US states

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("HUD-VASH - ")
        assert "hud.gov" in first.source_url
        assert first.eligibility is not None
        assert first.how_to_apply is not None

    def test_multi_vamc_pha(self, tmp_path):
        """Test PHA with multiple VAMC partnerships (same PHA code, different VAMCs)."""
        test_data = {
            "metadata": {"source": "test"},
            "awards": [
                {
                    "pha_code": "MI901",
                    "pha_name": "Michigan State Housing Development Authority",
                    "vamc": "V10/Battle Creek",
                    "vouchers": 43,
                    "budget": 325952,
                },
                {
                    "pha_code": "MI901",
                    "pha_name": "Michigan State Housing Development Authority",
                    "vamc": "V10/Detroit",
                    "vouchers": 40,
                    "budget": 303211,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = HUDVASHConnector(data_path=test_file)
        resources = connector.run()

        # Should have 2 separate resources for different VAMC partnerships
        assert len(resources) == 2

        # Both should have same state but different VAMC names in title
        assert resources[0].state == "MI"
        assert resources[1].state == "MI"
        assert "Battle Creek" in resources[0].title
        assert "Detroit" in resources[1].title
