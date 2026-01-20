"""Tests for HUD-VASH multi-year voucher awards data connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.hud_vash import HUDVASHConnector


class TestHUDVASHConnector:
    """Tests for HUDVASHConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        meta = connector.metadata

        assert "HUD-VASH" in meta.name
        assert "2020-2024" in meta.name
        assert meta.tier == 1  # Official HUD/VA program data
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "hud.gov" in meta.url

    def test_extract_state_valid(self, tmp_path):
        """Test extracting state from valid PHA code."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        assert connector._extract_state("CA004") == "CA"
        assert connector._extract_state("TX901") == "TX"
        assert connector._extract_state("NY005") == "NY"

    def test_extract_state_guam(self, tmp_path):
        """Test extracting state from Guam PHA code."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        assert connector._extract_state("GQ901") == "GQ"

    def test_extract_state_invalid(self, tmp_path):
        """Test extracting state from invalid PHA codes."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        assert connector._extract_state(None) is None
        assert connector._extract_state("") is None
        assert connector._extract_state("X") is None
        assert connector._extract_state("ZZ999") is None  # Invalid state code

    def test_parse_vamc_standard(self, tmp_path):
        """Test parsing standard VAMC string."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        visn, name = connector._parse_vamc("V22/Phoenix")
        assert visn == "V22"
        assert name == "Phoenix"

    def test_parse_vamc_with_hcs(self, tmp_path):
        """Test parsing VAMC string with HCS suffix."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        visn, name = connector._parse_vamc("V21/Northern California HCS")
        assert visn == "V21"
        assert name == "Northern California HCS"

    def test_parse_vamc_none(self, tmp_path):
        """Test parsing None VAMC."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        visn, name = connector._parse_vamc(None)
        assert visn is None
        assert name is None

    def test_parse_vamc_no_slash(self, tmp_path):
        """Test parsing VAMC without slash."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        visn, name = connector._parse_vamc("Portland")
        assert visn is None
        assert name == "Portland"

    def test_build_title_with_vamc_and_state(self, tmp_path):
        """Test title building with VAMC name and state."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        title = connector._build_title(
            pha_name="Housing Authority of Los Angeles",
            vamc_name="Greater Los Angeles HCS",
            state="CA",
        )
        assert title == "HUD-VASH - Greater Los Angeles HCS (CA)"

    def test_build_title_with_pha_only(self, tmp_path):
        """Test title building with PHA name only."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        title = connector._build_title(
            pha_name="Phoenix Housing Authority",
            vamc_name=None,
            state="AZ",
        )
        assert title == "HUD-VASH - Phoenix Housing Authority (AZ)"

    def test_build_title_minimal(self, tmp_path):
        """Test title building with minimal info."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        title = connector._build_title(pha_name=None, vamc_name=None, state=None)
        assert title == "HUD-VASH Housing Voucher Program"

    def test_build_description_single_year(self, tmp_path):
        """Test description building with single year data."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        desc = connector._build_description(
            pha_name="Housing Authority of Los Angeles",
            vamc_name="Greater Los Angeles HCS",
            state="CA",
            awards_by_year={"2024": 250},
            total_vouchers=250,
            budget=3886200,
        )

        assert "HUD-VASH" in desc
        assert "California" in desc
        assert "Housing Authority of Los Angeles" in desc
        assert "Greater Los Angeles HCS" in desc
        assert "250" in desc
        assert "$3,886,200" in desc
        assert "case management" in desc

    def test_build_description_multi_year(self, tmp_path):
        """Test description building with multi-year data."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        desc = connector._build_description(
            pha_name="Alaska Housing Finance Corporation",
            vamc_name=None,
            state="AK",
            awards_by_year={"2020": 17, "2021": 22, "2023": 20},
            total_vouchers=59,
            budget=None,
        )

        assert "HUD-VASH" in desc
        assert "Alaska" in desc
        assert "Recent awards:" in desc
        assert "FY2023" in desc
        assert "FY2021" in desc
        assert "FY2020" in desc

    def test_build_description_no_vouchers(self, tmp_path):
        """Test description building without voucher info."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        desc = connector._build_description(
            pha_name="Test PHA",
            vamc_name="Test VAMC",
            state="TX",
            awards_by_year={},
            total_vouchers=0,
            budget=None,
        )

        assert "HUD-VASH" in desc
        assert "Texas" in desc
        # No voucher count mentioned
        assert "award:" not in desc.lower()

    def test_build_tags(self, tmp_path):
        """Test tag building."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        tags = connector._build_tags(
            pha_code="CA004",
            visn="V22",
            vamc_name="Greater Los Angeles HCS",
            awards_by_year={"2024": 250},
        )

        assert "hud-vash" in tags
        assert "housing-voucher" in tags
        assert "housing" in tags
        assert "homeless-services" in tags
        assert "rental-assistance" in tags
        assert "pha-ca004" in tags
        assert "visn-22" in tags
        assert "vamc-greater-los-angeles-hcs" in tags
        assert "fy2024" in tags

    def test_build_tags_multi_year(self, tmp_path):
        """Test tag building with multi-year data."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        tags = connector._build_tags(
            pha_code="AK901",
            visn=None,
            vamc_name=None,
            awards_by_year={"2020": 17, "2021": 22, "2023": 20},
        )

        assert "hud-vash" in tags
        assert "pha-ak901" in tags
        assert "fy2023" in tags
        assert "fy2021" in tags
        assert "fy2020" in tags

    def test_build_tags_minimal(self, tmp_path):
        """Test tag building with minimal info."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        tags = connector._build_tags(pha_code=None, visn=None, vamc_name=None, awards_by_year={})

        assert "hud-vash" in tags
        assert "housing-voucher" in tags
        assert not any(t.startswith("pha-") for t in tags)
        assert not any(t.startswith("visn-") for t in tags)
        assert not any(t.startswith("vamc-") for t in tags)
        assert not any(t.startswith("fy") for t in tags)

    def test_parse_award(self, tmp_path):
        """Test parsing a single award entry."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="CA004",
            pha_name="Housing Authority of the City of Los Angeles",
            awards_by_year={"2024": 250},
            total_vouchers=250,
            vamc="V22/Greater Los Angeles HCS",
            budget=3886200,
            contact={},  # No contact info
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
        assert "fy2024" in candidate.tags
        assert candidate.raw_data["pha_code"] == "CA004"
        assert candidate.raw_data["total_vouchers"] == 250

    def test_eligibility_text(self, tmp_path):
        """Test that eligibility text is present and accurate."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="TX004",
            pha_name="Fort Worth Housing Solutions",
            awards_by_year={"2024": 10},
            total_vouchers=10,
            vamc="V17/Dallas",
            budget=95518,
            contact={},  # No contact info
            fetched_at=now,
        )

        assert "80% of Area Median Income" in candidate.eligibility
        assert "homeless veterans" in candidate.eligibility.lower()
        assert "VA health care" in candidate.eligibility

    def test_how_to_apply_text(self, tmp_path):
        """Test that how_to_apply text includes contact info."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        now = datetime.now(UTC)

        # Test without contact info
        candidate = connector._parse_award(
            pha_code="FL002",
            pha_name="Housing Authority of St. Petersburg",
            awards_by_year={"2024": 35},
            total_vouchers=35,
            vamc="V08/Bay Pines",
            budget=424448,
            contact={},  # No contact info
            fetched_at=now,
        )

        assert "1-877-4AID-VET" in candidate.how_to_apply
        assert "1-877-424-3838" in candidate.how_to_apply
        assert "HUD-VASH coordinator" in candidate.how_to_apply

    def test_how_to_apply_with_contact(self, tmp_path):
        """Test that how_to_apply text includes PHA phone number when available."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "multiyear.json",
            single_year_path=tmp_path / "single.json",
        )
        now = datetime.now(UTC)

        candidate = connector._parse_award(
            pha_code="FL002",
            pha_name="Housing Authority of St. Petersburg",
            awards_by_year={"2024": 35},
            total_vouchers=35,
            vamc="V08/Bay Pines",
            budget=424448,
            contact={
                "phone": "(727) 555-1234",
                "email": "info@stpeteha.org",
                "address": "123 Main St",
                "city": "St. Petersburg",
                "state": "FL",
                "zip_code": "33701",
            },
            fetched_at=now,
        )

        # Should include the PHA phone number prominently
        assert "(727) 555-1234" in candidate.how_to_apply
        assert "Housing Authority of St. Petersburg" in candidate.how_to_apply
        # Should still include national hotline as backup
        assert "1-877-4AID-VET" in candidate.how_to_apply
        # Contact info should be in raw_data
        assert candidate.raw_data["contact"]["phone"] == "(727) 555-1234"

    def test_run_no_files(self, tmp_path):
        """Test that run() returns empty list when no data files exist."""
        connector = HUDVASHConnector(
            multiyear_path=tmp_path / "nonexistent.json",
            single_year_path=tmp_path / "also_nonexistent.json",
        )

        resources = connector.run()
        assert resources == []

    def test_run_with_multiyear_data(self, tmp_path):
        """Test that run() parses multi-year JSON correctly."""
        multiyear_data = {
            "metadata": {"source": "test"},
            "awards": [
                {
                    "pha_code": "CA004",
                    "pha_name": "Housing Authority of Los Angeles",
                    "awards_by_year": {"2023": 200, "2024": 250},
                    "total_vouchers": 450,
                },
                {
                    "pha_code": "TX004",
                    "pha_name": "Fort Worth Housing Solutions",
                    "awards_by_year": {"2024": 10},
                    "total_vouchers": 10,
                },
            ],
        }

        multiyear_file = tmp_path / "multiyear.json"
        multiyear_file.write_text(json.dumps(multiyear_data))

        connector = HUDVASHConnector(
            multiyear_path=multiyear_file,
            single_year_path=tmp_path / "single.json",
        )
        resources = connector.run()

        assert len(resources) == 2

        # First resource - California
        assert resources[0].title == "HUD-VASH - Housing Authority of Los Angeles (CA)"
        assert resources[0].state == "CA"
        assert resources[0].scope == "local"
        assert "fy2024" in resources[0].tags
        assert "fy2023" in resources[0].tags

        # Second resource - Texas
        assert resources[1].title == "HUD-VASH - Fort Worth Housing Solutions (TX)"
        assert resources[1].state == "TX"

    def test_run_merges_single_year_details(self, tmp_path):
        """Test that run() merges VAMC/budget details from single-year data."""
        multiyear_data = {
            "metadata": {"source": "test"},
            "awards": [
                {
                    "pha_code": "CA004",
                    "pha_name": "Housing Authority of Los Angeles",
                    "awards_by_year": {"2024": 250},
                    "total_vouchers": 250,
                },
            ],
        }

        single_year_data = {
            "metadata": {"source": "test"},
            "awards": [
                {
                    "pha_code": "CA004",
                    "pha_name": "Housing Authority of Los Angeles",
                    "vamc": "V22/Greater Los Angeles HCS",
                    "vouchers": 250,
                    "budget": 3886200,
                },
            ],
        }

        multiyear_file = tmp_path / "multiyear.json"
        multiyear_file.write_text(json.dumps(multiyear_data))
        single_year_file = tmp_path / "single.json"
        single_year_file.write_text(json.dumps(single_year_data))

        connector = HUDVASHConnector(
            multiyear_path=multiyear_file,
            single_year_path=single_year_file,
        )
        resources = connector.run()

        assert len(resources) == 1

        # Should have VAMC from single-year data
        assert resources[0].title == "HUD-VASH - Greater Los Angeles HCS (CA)"
        assert "visn-22" in resources[0].tags
        assert "$3,886,200" in resources[0].description
        assert resources[0].raw_data["vamc"] == "V22/Greater Los Angeles HCS"
        assert resources[0].raw_data["budget"] == 3886200

    def test_run_with_real_data(self):
        """Test run() with the actual HUD-VASH data files."""
        # Find the data files
        current = Path(__file__).resolve().parent
        while current != current.parent:
            multiyear_file = current / "data" / "reference" / "HUD_VASH_All_Years.json"
            single_year_file = current / "data" / "reference" / "HUD_VASH_2024_Awards.json"
            if multiyear_file.exists():
                break
            current = current.parent

        if not multiyear_file.exists():
            pytest.skip("HUD_VASH_All_Years.json not found in project")

        connector = HUDVASHConnector(
            multiyear_path=multiyear_file,
            single_year_path=single_year_file,
        )
        resources = connector.run()

        # Should have ~421 resources (from multi-year data)
        assert len(resources) >= 400

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have HUD-VASH tag
        assert all("hud-vash" in r.tags for r in resources)

        # All should have local scope
        assert all(r.scope == "local" for r in resources)

        # Check state coverage - should have 46+ states
        states = {r.state for r in resources if r.state}
        assert len(states) >= 40

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("HUD-VASH - ")
        assert "hud.gov" in first.source_url
        assert first.eligibility is not None
        assert first.how_to_apply is not None
