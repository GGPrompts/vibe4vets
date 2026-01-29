"""Tests for Veterans Community Project (VCP) tiny home village connector."""

from pathlib import Path

import pytest

from connectors.vcp import VCPConnector


class TestVCPConnector:
    """Tests for VCPConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VCPConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Veterans Community Project Villages"
        assert "vcp.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = VCPConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = VCPConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = VCPConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "VCP data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        import json

        test_data = {
            "source": "Veterans Community Project",
            "success_rate": "85% transition to permanent housing",
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "MO",
                    "address": "123 Test St",
                    "zip_code": "12345",
                    "phone": "(816) 912-8406",
                    "status": "operational",
                    "homes": 25,
                    "services": ["Case management", "Mental health support"],
                    "features": ["Pet-friendly", "All utilities included"],
                },
                {
                    "id": "vcp-construction",
                    "name": "VCP Village Construction",
                    "city": "Build City",
                    "state": "AZ",
                    "address": "456 Build Ave",
                    "zip_code": "67890",
                    "phone": "(816) 912-8406",
                    "status": "under-construction",
                    "planned_homes": 40,
                    "services": ["Case management (planned)"],
                    "features": ["Pet-friendly (planned)"],
                },
            ],
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        # Should have 2 resources
        assert len(resources) == 2

        # First resource - operational
        assert "VCP Village Test" in resources[0].title
        assert "Tiny Home Village for Veterans" in resources[0].title
        assert resources[0].state == "MO"
        assert resources[0].scope == "local"

        # Second resource - under construction
        assert "VCP Village Construction" in resources[1].title
        assert "Under Construction" in resources[1].title
        assert resources[1].state == "AZ"

    def test_run_with_real_data(self):
        """Test run() with the actual VCP villages data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found in project")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        # Should have 6 villages based on data
        assert len(resources) >= 4  # At least 4 operational/under construction

        # All should be housing category
        assert all("housing" in r.categories for r in resources)

        # All should have VCP tag
        assert all("vcp" in r.tags for r in resources)

        # Check for operational villages
        operational = [r for r in resources if "under-construction" not in r.tags]
        assert len(operational) >= 4  # Kansas City, Longmont, St. Louis, Sioux Falls

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("VCP Village")
        assert "vcp.org" in first.source_url
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.org_name == "Veterans Community Project"

    def test_all_have_housing_category(self):
        """Test that all villages have housing category."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert "housing" in resource.categories

    def test_all_have_local_scope(self):
        """Test that all villages have local scope."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_all_have_address_info(self):
        """Test that all villages have address information."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert len(resource.state) == 2

    def test_all_have_phone(self):
        """Test that all villages have phone numbers."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            # Phone should be normalized
            assert "(" in resource.phone
            assert ")" in resource.phone

    def test_all_have_states_served(self):
        """Test that all villages have states list."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert len(resource.states) == 1  # Each village serves one state

    def test_village_title_format_operational(self, tmp_path):
        """Test village title format for operational villages."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "MO",
                    "status": "operational",
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "Tiny Home Village for Veterans" in resources[0].title
        assert "Under Construction" not in resources[0].title

    def test_village_title_format_construction(self, tmp_path):
        """Test village title format for villages under construction."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "AZ",
                    "status": "under-construction",
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "Under Construction" in resources[0].title

    def test_village_description_includes_homes(self, tmp_path):
        """Test village description includes home count."""
        import json

        test_data = {
            "success_rate": "85% transition",
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "MO",
                    "status": "operational",
                    "homes": 49,
                    "home_sizes": "240-320 sq ft",
                }
            ],
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "49" in resources[0].description
        assert "240-320 sq ft" in resources[0].description

    def test_village_description_includes_family_homes(self, tmp_path):
        """Test village description includes family home count."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "SD",
                    "status": "operational",
                    "homes": 25,
                    "family_homes": 10,
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "10 family" in resources[0].description

    def test_village_eligibility(self, tmp_path):
        """Test eligibility information."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "MO",
                    "features": ["Pet-friendly"],
                    "family_homes": 5,
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        # Should mention veterans
        assert "veteran" in resources[0].eligibility.lower()
        # Should mention homeless
        assert "homeless" in resources[0].eligibility.lower()
        # Should mention family housing
        assert "family" in resources[0].eligibility.lower()
        # Should mention pet-friendly
        assert "pet" in resources[0].eligibility.lower()

    def test_village_how_to_apply_operational(self, tmp_path):
        """Test how to apply for operational villages."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Kansas City",
                    "state": "MO",
                    "phone": "(816) 912-8406",
                    "status": "operational",
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "(816) 912-8406" in resources[0].how_to_apply
        assert "Kansas City" in resources[0].how_to_apply
        assert "vcp.org" in resources[0].how_to_apply

    def test_village_how_to_apply_construction(self, tmp_path):
        """Test how to apply for villages under construction."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Glendale",
                    "state": "AZ",
                    "phone": "(816) 912-8406",
                    "status": "under-construction",
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "under construction" in resources[0].how_to_apply.lower()
        assert "Glendale" in resources[0].how_to_apply

    def test_village_tags(self, tmp_path):
        """Test village tags."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-kansas-city",
                    "name": "VCP Village Kansas City",
                    "city": "Kansas City",
                    "state": "MO",
                    "status": "operational",
                    "family_homes": 0,
                    "features": ["Pet-friendly"],
                    "services": ["Mental health support", "Employment assistance"],
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        expected_tags = [
            "vcp",
            "veterans-community-project",
            "tiny-homes",
            "homeless-services",
            "transitional-housing",
            "housing-first",
            "operational",
            "pet-friendly",
            "mental-health",
            "employment-services",
            "vcp-kansas-city",
            "state-mo",
        ]

        for tag in expected_tags:
            assert tag in resources[0].tags, f"Missing tag: {tag}"

    def test_village_tags_family_housing(self, tmp_path):
        """Test family housing tags."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "SD",
                    "family_homes": 10,
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "family-housing" in resources[0].tags
        assert "veterans-with-children" in resources[0].tags

    def test_village_tags_under_construction(self, tmp_path):
        """Test under construction tag."""
        import json

        test_data = {
            "villages": [
                {
                    "id": "vcp-test",
                    "name": "VCP Village Test",
                    "city": "Test City",
                    "state": "AZ",
                    "status": "under-construction",
                }
            ]
        }

        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = VCPConnector(data_path=test_file)
        resources = connector.run()

        assert "under-construction" in resources[0].tags
        assert "operational" not in resources[0].tags

    def test_org_info(self):
        """Test organization information."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Veterans Community Project"
            assert resource.org_website == "https://vcp.org/"
            assert "vcp.org" in resource.source_url

    def test_raw_data(self):
        """Test raw data includes village details."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert "id" in resource.raw_data
            assert "name" in resource.raw_data
            assert "city" in resource.raw_data
            assert "state" in resource.raw_data

    def test_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        with VCPConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert len(resources) >= 4

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = VCPConnector(data_path="/fake/path.json")

        assert connector._normalize_phone("8169128406") == "(816) 912-8406"
        assert connector._normalize_phone("1-816-912-8406") == "(816) 912-8406"
        assert connector._normalize_phone("(816) 912-8406") == "(816) 912-8406"

    def test_kansas_city_village(self):
        """Test Kansas City village details."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        # Find Kansas City village
        kc_village = None
        for r in resources:
            if "Kansas City" in r.title:
                kc_village = r
                break

        assert kc_village is not None
        assert kc_village.state == "MO"
        assert kc_village.city == "Kansas City"
        assert "49" in kc_village.description  # 49 homes
        assert "vcp-kansas-city" in kc_village.tags

    def test_state_coverage(self):
        """Test that villages cover expected states."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vcp_villages.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vcp_villages.json not found")

        connector = VCPConnector(data_path=data_file)
        resources = connector.run()

        # Collect all states
        all_states = set()
        for resource in resources:
            all_states.update(resource.states)

        # Should cover these states
        assert "MO" in all_states  # Kansas City, St. Louis
        assert "CO" in all_states  # Longmont
        assert "SD" in all_states  # Sioux Falls
        assert "AZ" in all_states  # Glendale
        assert "WI" in all_states  # Milwaukee
