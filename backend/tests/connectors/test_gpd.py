"""Tests for GPD (Grant and Per Diem) transitional housing connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.gpd import GPDConnector


class TestGPDConnector:
    """Tests for GPDConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = GPDConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "VA GPD FY24 Grantee Data"
        assert meta.tier == 1  # Official VA program data
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "va.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = GPDConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = GPDConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_transitional_housing(self):
        """Test title building for transitional housing."""
        connector = GPDConnector(data_path="/fake/path.json")

        title = connector._build_title(
            org_name="Veterans Housing Inc.",
            state="TX",
            is_service_center=False,
        )

        assert title == "GPD Transitional Housing - Veterans Housing Inc. (TX)"

    def test_build_title_service_center(self):
        """Test title building for service center."""
        connector = GPDConnector(data_path="/fake/path.json")

        title = connector._build_title(
            org_name="Veterans Support Center",
            state="CA",
            is_service_center=True,
        )

        assert title == "GPD Service Center - Veterans Support Center (CA)"

    def test_build_title_no_state(self):
        """Test title building without state."""
        connector = GPDConnector(data_path="/fake/path.json")

        title = connector._build_title(
            org_name="Veterans Housing",
            state=None,
            is_service_center=False,
        )

        assert title == "GPD Transitional Housing - Veterans Housing"

    def test_build_description_transitional_housing(self):
        """Test description building for transitional housing."""
        connector = GPDConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            org_name="Harbor Homes, Inc.",
            state="NH",
            total_beds=75,
            is_service_center=False,
            bed_types={
                "hospital_to_housing": 8,
                "clinical_treatment": 28,
                "intensive": 39,
            },
        )

        assert "Harbor Homes, Inc." in desc
        assert "GPD" in desc
        assert "transitional housing" in desc
        assert "NH" in desc
        assert "75 transitional housing beds" in desc
        assert "8 hospital-to-housing beds" in desc
        assert "28 clinical treatment beds" in desc
        assert "39 intensive services beds" in desc

    def test_build_description_service_center(self):
        """Test description building for service center."""
        connector = GPDConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            org_name="Veterans Support Center",
            state="CA",
            total_beds=0,
            is_service_center=True,
            bed_types={},
        )

        assert "Veterans Support Center" in desc
        assert "Service Center" in desc
        assert "daytime support services" in desc
        assert "CA" in desc
        assert "beds" not in desc.lower() or "without requiring overnight" in desc.lower()

    def test_build_description_with_all_bed_types(self):
        """Test description with all bed types."""
        connector = GPDConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            org_name="Full Service Housing",
            state="TX",
            total_beds=100,
            is_service_center=False,
            bed_types={
                "bridge_housing": 10,
                "low_demand": 15,
                "hospital_to_housing": 20,
                "clinical_treatment": 25,
                "intensive": 20,
                "minor_dependents": 10,
            },
        )

        assert "bridge housing" in desc
        assert "low-demand/harm reduction" in desc
        assert "hospital-to-housing" in desc
        assert "clinical treatment" in desc
        assert "intensive services" in desc
        assert "veterans with children" in desc

    def test_describe_bed_types(self):
        """Test bed type description formatting."""
        connector = GPDConnector(data_path="/fake/path.json")

        desc = connector._describe_bed_types(
            {
                "bridge_housing": 5,
                "low_demand": 10,
                "hospital_to_housing": 0,  # Should be skipped
                "clinical_treatment": 15,
            }
        )

        assert "5 bridge housing beds" in desc
        assert "10 low-demand/harm reduction beds" in desc
        assert "15 clinical treatment beds" in desc
        assert "hospital-to-housing" not in desc  # 0 beds, should be skipped

    def test_describe_bed_types_empty(self):
        """Test bed type description with empty dict."""
        connector = GPDConnector(data_path="/fake/path.json")
        desc = connector._describe_bed_types({})
        assert desc == ""

    def test_build_eligibility_transitional_housing(self):
        """Test eligibility for transitional housing."""
        connector = GPDConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility(is_service_center=False)

        assert "Veterans experiencing homelessness" in elig
        assert "VA health care" in elig
        assert "24 months" in elig

    def test_build_eligibility_service_center(self):
        """Test eligibility for service center."""
        connector = GPDConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility(is_service_center=True)

        assert "homelessness" in elig
        assert "overnight stays" in elig

    def test_build_how_to_apply(self):
        """Test how to apply text."""
        connector = GPDConnector(data_path="/fake/path.json")
        how = connector._build_how_to_apply("Harbor Homes, Inc.")

        assert "Harbor Homes, Inc." in how
        assert "1-877-4AID-VET" in how
        assert "1-877-424-3838" in how
        assert "Homeless Veteran Coordinator" in how

    def test_build_tags_transitional_housing(self):
        """Test tag building for transitional housing."""
        connector = GPDConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            grant_id="HARB932-3381-608-PD-24",
            visn="1",
            is_service_center=False,
            bed_types={"bridge_housing": 5, "low_demand": 10},
        )

        assert "gpd" in tags
        assert "housing" in tags
        assert "homeless-services" in tags
        assert "transitional-housing" in tags
        assert "residential" in tags
        assert "bridge-housing" in tags
        assert "low-demand" in tags
        assert "harm-reduction" in tags
        assert "grant-HARB932-3381-608-PD-24" in tags
        assert "visn-1" in tags

    def test_build_tags_service_center(self):
        """Test tag building for service center."""
        connector = GPDConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            grant_id="TEST123",
            visn="5",
            is_service_center=True,
            bed_types={},
        )

        assert "service-center" in tags
        assert "residential" not in tags

    def test_build_tags_families_with_children(self):
        """Test tag for families with children."""
        connector = GPDConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            grant_id="TEST123",
            visn="1",
            is_service_center=False,
            bed_types={"minor_dependents": 5},
        )

        assert "families-with-children" in tags

    def test_parse_grantee_transitional_housing(self):
        """Test parsing a transitional housing grantee."""
        connector = GPDConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            visn="1",
            station="608",
            org_name="Harbor Homes, Inc.",
            grant_id="HARB932-3381-608-PD-24",
            total_beds=75,
            is_service_center=False,
            state="NH",
            bed_types={
                "hospital_to_housing": 8,
                "clinical_treatment": 28,
                "intensive": 39,
            },
            fetched_at=now,
        )

        assert candidate.title == "GPD Transitional Housing - Harbor Homes, Inc. (NH)"
        assert "Harbor Homes, Inc." in candidate.description
        assert "75 transitional housing beds" in candidate.description
        assert candidate.org_name == "Harbor Homes, Inc."
        assert candidate.categories == ["housing"]
        assert candidate.scope == "state"
        assert candidate.states == ["NH"]
        assert "gpd" in candidate.tags
        assert "grant-HARB932-3381-608-PD-24" in candidate.tags
        assert candidate.raw_data["grant_id"] == "HARB932-3381-608-PD-24"
        assert candidate.raw_data["total_beds"] == 75

    def test_parse_grantee_service_center(self):
        """Test parsing a service center."""
        connector = GPDConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            visn="1",
            station="523",
            org_name="Vietnam Veterans Workshop, Inc.",
            grant_id="VVWN211-3545-523-PD-24",
            total_beds=0,
            is_service_center=True,
            state="MA",
            bed_types={},
            fetched_at=now,
        )

        assert "Service Center" in candidate.title
        assert candidate.raw_data["is_service_center"] is True
        assert "service-center" in candidate.tags

    def test_parse_grantee_no_state(self):
        """Test parsing a grantee with no state."""
        connector = GPDConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            visn="1",
            station="608",
            org_name="Unknown Location Housing",
            grant_id="TEST123",
            total_beds=20,
            is_service_center=False,
            state=None,
            bed_types={},
            fetched_at=now,
        )

        assert "Unknown Location Housing" in candidate.title
        assert candidate.scope == "local"
        assert candidate.states is None

    def test_parse_grantee_no_org_name(self):
        """Test parsing a grantee with no org name."""
        connector = GPDConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_grantee(
            visn="1",
            station="608",
            org_name=None,
            grant_id="TEST123",
            total_beds=20,
            is_service_center=False,
            state="TX",
            bed_types={},
            fetched_at=now,
        )

        assert candidate.org_name == "Unknown Organization"

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = GPDConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "GPD data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON correctly."""
        test_data = {
            "source": "VA GPD Program",
            "awards": [
                {
                    "visn": "1",
                    "station": "608",
                    "organization": "Harbor Homes, Inc.",
                    "grant_id": "HARB932-3381-608-PD-24",
                    "total_beds": 75,
                    "is_service_center": False,
                    "state": "NH",
                    "bed_types": {
                        "hospital_to_housing": 8,
                        "clinical_treatment": 28,
                        "intensive": 39,
                    },
                },
                {
                    "visn": "1",
                    "station": "523",
                    "organization": "Veterans Service Center",
                    "grant_id": "TEST-SC",
                    "total_beds": 0,
                    "is_service_center": True,
                    "state": "MA",
                    "bed_types": {},
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = GPDConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource - transitional housing
        assert resources[0].title == "GPD Transitional Housing - Harbor Homes, Inc. (NH)"
        assert resources[0].states == ["NH"]
        assert resources[0].scope == "state"
        assert "residential" in resources[0].tags

        # Second resource - service center
        assert "Service Center" in resources[1].title
        assert "service-center" in resources[1].tags

    def test_run_with_real_data(self):
        """Test run() with the actual GPD FY24 data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "GPD_FY24_Awards.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("GPD_FY24_Awards.json not found in project")

        connector = GPDConnector(data_path=data_file)
        resources = connector.run()

        # Should have ~295 resources based on extracted data
        assert len(resources) >= 250  # Allow some flexibility

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have GPD tag
        assert all("gpd" in r.tags for r in resources)

        # Check for service centers
        service_centers = [r for r in resources if r.raw_data.get("is_service_center")]
        transitional = [r for r in resources if not r.raw_data.get("is_service_center")]

        assert len(service_centers) > 0
        assert len(transitional) > 0

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("GPD ")
        assert first.source_url == "https://www.va.gov/homeless/gpd.asp"
        assert first.eligibility is not None
        assert first.how_to_apply is not None

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with GPDConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "VA GPD FY24 Grantee Data"

    def test_total_beds_calculation(self, tmp_path):
        """Test that total beds are correctly summed."""
        test_data = {
            "awards": [
                {
                    "visn": "1",
                    "station": "608",
                    "organization": "Org 1",
                    "grant_id": "TEST1",
                    "total_beds": 50,
                    "is_service_center": False,
                    "state": "TX",
                    "bed_types": {},
                },
                {
                    "visn": "2",
                    "station": "630",
                    "organization": "Org 2",
                    "grant_id": "TEST2",
                    "total_beds": 30,
                    "is_service_center": False,
                    "state": "NY",
                    "bed_types": {},
                },
                {
                    "visn": "3",
                    "station": "523",
                    "organization": "Service Center",
                    "grant_id": "TEST3",
                    "total_beds": 0,
                    "is_service_center": True,
                    "state": "MA",
                    "bed_types": {},
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = GPDConnector(data_path=test_file)
        resources = connector.run()

        total_beds = sum(r.raw_data.get("total_beds", 0) for r in resources)
        assert total_beds == 80  # 50 + 30 + 0
