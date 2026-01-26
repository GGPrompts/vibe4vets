"""Tests for United Way regional veteran resources connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.united_way import UnitedWayConnector


@pytest.fixture
def sample_dmv_data():
    """Sample DMV region data matching expected format."""
    return {
        "region": "dmv",
        "region_name": "National Capital Area",
        "fetched_at": "2026-01-25T00:00:00Z",
        "source": "United Way National Capital Area",
        "resources": [
            {
                "name": "Mission United - National Capital Area",
                "org_name": "United Way National Capital Area",
                "phone": "1-703-246-8800",
                "address": "8401 Greensboro Dr Suite 150",
                "city": "McLean",
                "state": "VA",
                "zip_code": "22102",
                "email": "missionunited@uwnca.org",
                "description": "Comprehensive veteran services including career coaching, "
                "housing stability, and benefits navigation for veterans and military families.",
                "services": [
                    "missions united",
                    "veteran employment",
                    "career coaching",
                    "housing assistance",
                    "benefits navigation",
                ],
                "website": "https://uwnca.org/mission-united",
                "source_url": "https://uwnca.org/mission-united",
                "hours": "Mon-Fri 9am-5pm",
                "is_missions_united": True,
            },
            {
                "name": "Veteran Career Services",
                "org_name": "United Way NCA",
                "phone": "(202) 555-1234",
                "city": "Washington",
                "state": "DC",
                "description": "Job readiness and placement services",
                "services": ["job readiness", "resume assistance", "interview preparation"],
                "website": "https://uwnca.org/careers",
            },
            {
                "name": "Military Family Support",
                "org_name": "United Way NCA",
                "phone": "301-555-4567",
                "city": "Bethesda",
                "state": "MD",
                "description": "Support services for military families",
                "services": ["family support", "childcare assistance", "caregiver support"],
                "website": "https://uwnca.org/family",
            },
        ],
    }


@pytest.fixture
def sample_florida_data():
    """Sample South Florida region data."""
    return {
        "region": "south_florida",
        "region_name": "South Florida",
        "fetched_at": "2026-01-24T00:00:00Z",
        "resources": [
            {
                "name": "Mission United Miami",
                "org_name": "United Way Miami",
                "phone": "305-646-7000",
                "city": "Miami",
                "state": "FL",
                "description": "Comprehensive veteran support in South Florida",
                "services": ["missions united", "veteran employment", "housing stability"],
                "website": "https://unitedwaymiami.org/mission-united",
                "is_missions_united": True,
            },
            {
                "name": "Veterans Emergency Fund",
                "org_name": "United Way Broward",
                "city": "Fort Lauderdale",
                "state": "FL",
                "description": "Emergency financial assistance for veterans",
                "services": ["emergency financial aid", "utility assistance"],
                "website": "https://unitedwaybroward.org",
            },
        ],
    }


@pytest.fixture
def test_data_dir(tmp_path, sample_dmv_data, sample_florida_data):
    """Create test data directory with sample files."""
    data_dir = tmp_path / "test_united_way"
    data_dir.mkdir()

    # Write DMV data
    dmv_file = data_dir / "dmv.json"
    with open(dmv_file, "w") as f:
        json.dump(sample_dmv_data, f)

    # Write South Florida data
    fl_file = data_dir / "south_florida.json"
    with open(fl_file, "w") as f:
        json.dump(sample_florida_data, f)

    return data_dir


@pytest.fixture
def connector(test_data_dir):
    """Create connector instance with test data."""
    return UnitedWayConnector(data_dir=test_data_dir, regions=["dmv", "south_florida"])


class TestUnitedWayConnector:
    """Tests for UnitedWayConnector."""

    def test_metadata(self, connector):
        """Test connector metadata."""
        meta = connector.metadata

        assert meta.name == "United Way Regional Directories"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "unitedway.org" in meta.url

    def test_init_default_regions(self):
        """Test initialization with default regions."""
        connector = UnitedWayConnector(data_dir="/fake/path")
        assert len(connector.regions) == len(UnitedWayConnector.REGIONS)

    def test_init_custom_regions(self, test_data_dir):
        """Test initialization with custom regions list."""
        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["dmv"])
        assert connector.regions == ["dmv"]

    def test_init_string_path(self, test_data_dir):
        """Test initialization with string path."""
        connector = UnitedWayConnector(data_dir=str(test_data_dir))
        assert connector.data_dir == Path(test_data_dir)

    def test_load_resources(self, connector):
        """Test run() returns ResourceCandidate list."""
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 5  # 3 from DMV + 2 from Florida

        # Check first resource (Missions United NCA)
        r = resources[0]
        assert r.title == "Mission United - National Capital Area"
        assert r.org_name == "United Way National Capital Area"
        assert "career coaching" in r.description.lower()
        assert r.state == "VA"
        assert r.city == "McLean"
        assert r.zip_code == "22102"
        assert r.address == "8401 Greensboro Dr Suite 150"
        assert r.email == "missionunited@uwnca.org"
        assert r.hours == "Mon-Fri 9am-5pm"
        assert r.phone == "(703) 246-8800"
        assert r.org_website == "https://uwnca.org/mission-united"

    def test_missions_united_detection(self, connector):
        """Test Missions United programs are tagged correctly."""
        resources = connector.run()

        missions_united = [r for r in resources if r.tags and "missions-united" in r.tags]
        assert len(missions_united) == 2  # NCA + Miami

        # Verify correct programs identified
        names = [r.title for r in missions_united]
        assert "Mission United - National Capital Area" in names
        assert "Mission United Miami" in names

    def test_category_mapping(self, connector):
        """Test SERVICE_CATEGORY_MAP correctly maps services."""
        resources = connector.run()

        # Test Missions United has employment category
        nca = [r for r in resources if "National Capital Area" in r.title][0]
        assert "employment" in nca.categories
        assert "housing" in nca.categories
        assert "benefits" in nca.categories

        # Test career services has employment
        career = [r for r in resources if "Career Services" in r.title][0]
        assert "employment" in career.categories

        # Test family support has support_services
        family = [r for r in resources if "Family Support" in r.title][0]
        assert "support_services" in family.categories

        # Test emergency fund has financial
        emergency = [r for r in resources if "Emergency Fund" in r.title][0]
        assert "financial" in emergency.categories

    def test_phone_normalization(self, connector):
        """Test various phone formats are normalized correctly."""
        assert connector._normalize_phone("1-703-246-8800") == "(703) 246-8800"
        assert connector._normalize_phone("(202) 555-1234") == "(202) 555-1234"
        assert connector._normalize_phone("301-555-4567") == "(301) 555-4567"
        assert connector._normalize_phone("305-646-7000") == "(305) 646-7000"
        assert connector._normalize_phone(None) is None

    def test_state_detection_from_city(self, test_data_dir):
        """Test state is inferred from city when not provided."""
        data = {
            "region": "dmv",
            "resources": [
                {
                    "name": "DC Resource",
                    "city": "Washington",
                    "services": ["housing"],
                },
                {
                    "name": "VA Resource",
                    "city": "Arlington",
                    "services": ["employment"],
                },
            ],
        }

        dmv_file = test_data_dir / "dmv.json"
        with open(dmv_file, "w") as f:
            json.dump(data, f)

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["dmv"])
        resources = connector.run()

        dc_resource = [r for r in resources if r.title == "DC Resource"][0]
        assert dc_resource.state == "DC"

        va_resource = [r for r in resources if r.title == "VA Resource"][0]
        assert va_resource.state == "VA"

    def test_get_resources_by_state(self, connector):
        """Test filter by state works."""
        connector.run()

        va_resources = connector.get_resources_by_state("VA")
        assert len(va_resources) == 1
        assert va_resources[0].state == "VA"

        dc_resources = connector.get_resources_by_state("DC")
        assert len(dc_resources) == 1
        assert dc_resources[0].state == "DC"

        fl_resources = connector.get_resources_by_state("FL")
        assert len(fl_resources) == 2
        assert all(r.state == "FL" for r in fl_resources)

    def test_get_missions_united_resources(self, connector):
        """Test filtering for Missions United programs."""
        connector.run()

        missions = connector.get_missions_united_resources()
        assert len(missions) == 2
        assert all("missions-united" in (r.tags or []) for r in missions)

    def test_get_resources_by_category(self, connector):
        """Test filter by category works."""
        connector.run()

        employment = connector.get_resources_by_category("employment")
        assert len(employment) >= 2  # NCA, Career Services, Miami

        financial = connector.get_resources_by_category("financial")
        assert len(financial) >= 1  # Emergency Fund

    def test_stats(self, connector):
        """Test stats output structure."""
        stats = connector.stats()

        assert "total_resources" in stats
        assert stats["total_resources"] == 5

        assert "missions_united_programs" in stats
        assert stats["missions_united_programs"] == 2

        assert "states_covered" in stats
        assert stats["states_covered"] == 4  # DC, MD, VA, FL

        assert "by_state" in stats
        assert "FL" in stats["by_state"]
        assert stats["by_state"]["FL"] == 2

        assert "by_category" in stats
        assert "employment" in stats["by_category"]

    def test_missing_file_handling(self, test_data_dir):
        """Test graceful handling of missing region files."""
        connector = UnitedWayConnector(
            data_dir=test_data_dir,
            regions=["dmv", "texas_tarrant", "california_la"],  # Only DMV exists
        )

        resources = connector.run()

        # Should only load DMV resources without error
        assert len(resources) == 3
        assert all(r.state in ["DC", "MD", "VA"] for r in resources)

    def test_malformed_json(self, test_data_dir):
        """Test graceful handling of bad JSON."""
        bad_file = test_data_dir / "texas_tarrant.json"
        with open(bad_file, "w") as f:
            f.write("{invalid json content")

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["dmv", "texas_tarrant"])

        # Should load DMV successfully and skip Texas
        resources = connector.run()
        assert len(resources) == 3  # Only DMV resources

    def test_empty_json_file(self, test_data_dir):
        """Test handling of empty/minimal JSON file."""
        empty_file = test_data_dir / "ohio.json"
        with open(empty_file, "w") as f:
            json.dump({"region": "ohio", "resources": []}, f)

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["ohio"])

        resources = connector.run()
        assert len(resources) == 0

    def test_missing_name_skipped(self, test_data_dir):
        """Test resources without names are skipped."""
        data = {
            "region": "ohio",
            "resources": [
                {"name": "", "services": ["housing"]},
                {"services": ["food"]},  # Missing name
                {"name": "Valid Resource", "services": ["employment"]},
            ],
        }

        ohio_file = test_data_dir / "ohio.json"
        with open(ohio_file, "w") as f:
            json.dump(data, f)

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["ohio"])
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].title == "Valid Resource"

    def test_tags_include_region(self, connector):
        """Test region tags are included."""
        resources = connector.run()

        dmv_resources = [r for r in resources if "uw-dmv" in (r.tags or [])]
        assert len(dmv_resources) == 3

        fl_resources = [r for r in resources if "uw-south_florida" in (r.tags or [])]
        assert len(fl_resources) == 2

    def test_default_eligibility_missions_united(self, connector):
        """Test default eligibility for Missions United programs."""
        resources = connector.run()

        missions = connector.get_missions_united_resources()
        for m in missions:
            assert "Veterans" in m.eligibility or "veterans" in m.eligibility.lower()
            # Check that families are mentioned (default says "their families")
            assert "families" in m.eligibility.lower()

    def test_default_eligibility_non_missions(self, connector):
        """Test default eligibility for non-Missions programs."""
        resources = connector.run()

        # Get a non-Missions United resource
        non_missions = [r for r in resources if "missions-united" not in (r.tags or [])]
        for r in non_missions:
            if r.eligibility:
                assert "Contact" in r.eligibility or "eligibility" in r.eligibility.lower()

    def test_context_manager(self, connector):
        """Test connector works as context manager."""
        with connector as c:
            resources = c.run()
            assert len(resources) > 0

        # close() should work without error
        connector.close()

    def test_raw_data_preserved(self, connector):
        """Test raw_data field preserves original resource data."""
        resources = connector.run()

        nca = [r for r in resources if "National Capital Area" in r.title][0]

        assert nca.raw_data is not None
        assert nca.raw_data["name"] == "Mission United - National Capital Area"
        assert "missions united" in nca.raw_data["services"]

    def test_multiple_runs_clear_previous(self, connector):
        """Test calling run() multiple times clears previous resources."""
        resources1 = connector.run()
        count1 = len(resources1)

        resources2 = connector.run()
        count2 = len(resources2)

        assert count1 == count2
        assert count1 == 5

    def test_service_category_map_coverage(self):
        """Test SERVICE_CATEGORY_MAP has expected coverage."""
        map_dict = UnitedWayConnector.SERVICE_CATEGORY_MAP

        # Verify key Missions United categories
        assert "missions united" in map_dict
        assert map_dict["missions united"] == "employment"
        assert "veteran employment" in map_dict
        assert "career coaching" in map_dict

        # Verify housing
        assert "housing stability" in map_dict
        assert map_dict["housing stability"] == "housing"

        # Verify financial
        assert "financial coaching" in map_dict
        assert map_dict["financial coaching"] == "financial"

        # Verify benefits
        assert "benefits navigation" in map_dict
        assert map_dict["benefits navigation"] == "benefits"

    def test_regions_configuration(self):
        """Test REGIONS dict has expected structure."""
        regions = UnitedWayConnector.REGIONS

        # Verify DMV region
        assert "dmv" in regions
        states, name = regions["dmv"]
        assert "DC" in states
        assert "MD" in states
        assert "VA" in states

        # Verify Florida regions
        assert "south_florida" in regions
        assert "central_florida" in regions

        # Verify Texas regions
        assert "texas_tarrant" in regions
        assert "texas_houston" in regions

    def test_missions_united_detection_from_name(self, test_data_dir):
        """Test Missions United is detected from name."""
        data = {
            "region": "test",
            "resources": [
                {
                    "name": "Missions-United Program",
                    "services": ["veteran support"],
                }
            ],
        }

        test_file = test_data_dir / "test.json"
        with open(test_file, "w") as f:
            json.dump(data, f)

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["test"])
        resources = connector.run()

        assert len(resources) == 1
        assert "missions-united" in resources[0].tags

    def test_missions_united_detection_from_description(self, test_data_dir):
        """Test Missions United is detected from description."""
        data = {
            "region": "test",
            "resources": [
                {
                    "name": "Veteran Program",
                    "description": "Part of the Mission United initiative",
                    "services": ["employment"],
                }
            ],
        }

        test_file = test_data_dir / "test.json"
        with open(test_file, "w") as f:
            json.dump(data, f)

        connector = UnitedWayConnector(data_dir=test_data_dir, regions=["test"])
        resources = connector.run()

        assert len(resources) == 1
        assert "missions-united" in resources[0].tags

    def test_how_to_apply_default(self, connector):
        """Test default how_to_apply is set."""
        resources = connector.run()

        for r in resources:
            assert r.how_to_apply is not None
            assert "211" in r.how_to_apply or "phone" in r.how_to_apply.lower()

    def test_fetched_at_timestamp(self, connector):
        """Test fetched_at timestamp is parsed correctly."""
        resources = connector.run()

        # DMV resources should have 2026-01-25 timestamp
        dmv_resource = [r for r in resources if r.state == "VA"][0]
        assert dmv_resource.fetched_at is not None
        assert dmv_resource.fetched_at.year == 2026
        assert dmv_resource.fetched_at.month == 1
        assert dmv_resource.fetched_at.day == 25

    def test_parse_timestamp_formats(self):
        """Test various timestamp formats are handled."""
        connector = UnitedWayConnector(data_dir="/fake")

        ts1 = connector._parse_timestamp("2026-01-25T00:00:00Z")
        assert ts1.year == 2026

        ts2 = connector._parse_timestamp("2026-01-25T00:00:00+00:00")
        assert ts2.year == 2026

        ts3 = connector._parse_timestamp(None)
        assert ts3 is None

        ts4 = connector._parse_timestamp("invalid")
        assert ts4.year == datetime.now(UTC).year
