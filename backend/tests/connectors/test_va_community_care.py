"""Tests for VA Community Care Network connector."""

import json
from pathlib import Path

import pytest

from connectors.va_community_care import CCN_REGIONS, TPA_CONTACTS, VACommunityConnector


class TestVACommunityConnector:
    """Tests for VACommunityConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = VACommunityConnector(data_path=tmp_path / "providers.json")
        meta = connector.metadata

        assert "Community Care" in meta.name
        assert meta.tier == 2
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "COMMUNITYCARE" in meta.url

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = VACommunityConnector(data_path=tmp_path / "nonexistent.json")

        resources = connector.run()
        assert resources == []

    def test_run_empty_providers(self, tmp_path):
        """Test that run() handles empty providers list."""
        data = {"metadata": {"source": "test"}, "providers": []}
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_parses_primary_care_provider(self, tmp_path):
        """Test parsing a primary care provider."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Family Health Center",
                    "org_name": "Family Health Center",
                    "specialty": "primary_care",
                    "specialties": ["primary_care"],
                    "address": "123 Main St",
                    "city": "Arlington",
                    "state": "VA",
                    "zip_code": "22201",
                    "phone": "703-555-1234",
                    "email": "info@familyhealth.com",
                    "website": "https://www.familyhealth.com/",
                    "network_status": "in_network",
                    "accepting_new_patients": True,
                    "hours": "Mon-Fri 8am-5pm",
                    "languages": ["English", "Spanish"],
                    "telehealth_available": True,
                    "wheelchair_accessible": True,
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "VA CCN" in resource.title
        assert "Family Health Center" in resource.title
        assert "Primary Care" in resource.title
        assert "(Arlington, VA)" in resource.title
        assert resource.org_name == "Family Health Center"
        assert resource.address == "123 Main St"
        assert resource.city == "Arlington"
        assert resource.state == "VA"
        assert resource.zip_code == "22201"
        assert resource.phone == "(703) 555-1234"
        assert resource.email == "info@familyhealth.com"
        assert "housing" in resource.categories
        assert "va-community-care" in resource.tags
        assert "ccn" in resource.tags
        assert "primary-care" in resource.tags
        assert "in-network" in resource.tags
        assert "accepting-patients" in resource.tags
        assert "telehealth" in resource.tags
        assert "spanish-speaking" in resource.tags
        assert resource.scope == "local"

    def test_run_parses_urgent_care_provider(self, tmp_path):
        """Test parsing an urgent care provider."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "QuickCare Urgent Care",
                    "org_name": "QuickCare",
                    "specialty": "urgent_care",
                    "address": "456 Oak Ave",
                    "city": "Phoenix",
                    "state": "AZ",
                    "zip_code": "85001",
                    "phone": "602-555-9876",
                    "network_status": "urgent_care",
                    "accepting_new_patients": True,
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Urgent Care" in resource.title
        assert "urgent-care" in resource.tags
        assert "no-referral-needed" in resource.tags
        assert "ccn-region-4" in resource.tags
        assert "triwest" in resource.tags
        assert "no va referral needed" in resource.eligibility.lower()
        assert "vhic" in resource.eligibility.lower()

    def test_run_parses_specialty_provider(self, tmp_path):
        """Test parsing a specialty care provider."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Heart & Vascular Institute",
                    "org_name": "Heart & Vascular Institute",
                    "specialty": "cardiology",
                    "specialties": ["cardiology"],
                    "address": "789 Medical Pkwy",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001",
                    "phone": "713-555-4321",
                    "network_status": "in_network",
                    "services": "Echocardiograms, stress tests, cardiac catheterization",
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Cardiology" in resource.title
        assert "cardiology" in resource.tags
        assert "ccn-region-3" in resource.tags
        assert "optum" in resource.tags
        assert "Echocardiograms" in resource.description

    def test_run_parses_mental_health_provider(self, tmp_path):
        """Test parsing a mental health provider."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Veterans Mental Health Associates",
                    "org_name": "VMHA",
                    "specialty": "mental_health",
                    "address": "321 Wellness Way",
                    "city": "San Diego",
                    "state": "CA",
                    "zip_code": "92101",
                    "phone": "619-555-8765",
                    "network_status": "in_network",
                    "telehealth_available": True,
                    "description": "Specialized PTSD and anxiety treatment for veterans.",
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Mental Health" in resource.title
        assert "mental-health" in resource.tags
        assert "telehealth" in resource.tags
        assert "ccn-region-5" in resource.tags
        assert "triwest" in resource.tags
        assert "PTSD" in resource.description

    def test_run_parses_multiple_specialties(self, tmp_path):
        """Test parsing provider with multiple specialties."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Comprehensive Care Center",
                    "org_name": "CCC",
                    "specialty": "orthopedics",
                    "specialties": ["orthopedics", "physical_therapy", "chiropractic"],
                    "address": "555 Health Blvd",
                    "city": "Denver",
                    "state": "CO",
                    "zip_code": "80201",
                    "phone": "303-555-2468",
                    "network_status": "in_network",
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "orthopedics" in resource.tags
        assert "physical-therapy" in resource.tags
        assert "chiropractic" in resource.tags
        assert "Physical Therapy" in resource.description
        assert "Chiropractic Care" in resource.description

    def test_build_title_variations(self, tmp_path):
        """Test title building with various inputs."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        # Full location
        title = connector._build_title("Test Provider", "primary_care", "Boston", "MA")
        assert title == "VA CCN: Test Provider - Primary Care (Boston, MA)"

        # State only
        title = connector._build_title("Test Provider", "cardiology", None, "TX")
        assert title == "VA CCN: Test Provider - Cardiology (TX)"

        # No location
        title = connector._build_title("Test Provider", "dental", None, None)
        assert title == "VA CCN: Test Provider - Dental Care"

    def test_format_specialty(self, tmp_path):
        """Test specialty formatting."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        assert connector._format_specialty("primary_care") == "Primary Care"
        assert connector._format_specialty("mental_health") == "Mental Health"
        assert connector._format_specialty("physical_therapy") == "Physical Therapy"
        assert connector._format_specialty("vision") == "Eye Care"
        assert connector._format_specialty("lab_services") == "Laboratory Services"
        assert connector._format_specialty("unknown_specialty") == "Unknown Specialty"

    def test_build_eligibility_standard(self, tmp_path):
        """Test eligibility building for standard in-network provider."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        provider = {"network_status": "in_network"}
        eligibility = connector._build_eligibility(provider)

        assert "VA Community Care" in eligibility
        assert "enrolled in VA health care" in eligibility
        assert "referral" in eligibility.lower()
        assert "IMPORTANT" in eligibility

    def test_build_eligibility_urgent_care(self, tmp_path):
        """Test eligibility building for urgent care provider."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        provider = {"network_status": "urgent_care"}
        eligibility = connector._build_eligibility(provider)

        assert "urgent care" in eligibility.lower()
        assert "No VA referral needed" in eligibility
        assert "VHIC" in eligibility

    def test_build_how_to_apply_with_contact(self, tmp_path):
        """Test how to apply building with contact info."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        provider = {
            "state": "VA",
            "phone": "703-555-1234",
            "email": "contact@provider.com",
            "hours": "Mon-Fri 9am-5pm",
            "network_status": "in_network",
        }
        how_to = connector._build_how_to_apply(provider)

        assert "Step 1:" in how_to
        assert "Step 2:" in how_to
        assert "(703) 555-1234" in how_to
        assert "contact@provider.com" in how_to
        assert "Mon-Fri 9am-5pm" in how_to
        assert "Optum" in how_to  # VA is in Region 1 (Optum)
        assert "877-881-7618" in how_to  # National contact center

    def test_build_how_to_apply_triwest_region(self, tmp_path):
        """Test how to apply for TriWest region provider."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        provider = {
            "state": "CA",
            "phone": "310-555-1234",
            "network_status": "in_network",
        }
        how_to = connector._build_how_to_apply(provider)

        assert "TriWest" in how_to
        assert "(877) 226-8749" in how_to

    def test_build_tags_comprehensive(self, tmp_path):
        """Test comprehensive tag building."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        provider = {
            "specialty": "mental_health",
            "specialties": ["mental_health", "primary_care"],
            "state": "NY",
            "network_status": "in_network",
            "accepting_new_patients": True,
            "languages": ["English", "Spanish", "Mandarin"],
            "telehealth_available": True,
            "wheelchair_accessible": True,
        }
        tags = connector._build_tags(provider)

        assert "va-community-care" in tags
        assert "ccn" in tags
        assert "veteran-healthcare" in tags
        assert "in-network" in tags
        assert "mental-health" in tags
        assert "primary-care" in tags
        assert "ccn-region-1" in tags
        assert "optum" in tags
        assert "accepting-patients" in tags
        assert "spanish-speaking" in tags
        assert "multilingual" in tags
        assert "telehealth" in tags

    def test_phone_normalization(self, tmp_path):
        """Test phone number normalization."""
        connector = VACommunityConnector(data_path=tmp_path / "test.json")

        assert connector._normalize_phone("7035551234") == "(703) 555-1234"
        assert connector._normalize_phone("1-703-555-1234") == "(703) 555-1234"
        assert connector._normalize_phone("(703) 555-1234") == "(703) 555-1234"
        assert connector._normalize_phone(None) is None

    def test_ccn_regions_mapping(self):
        """Test that CCN regions are correctly mapped."""
        # Optum regions (1, 2, 3)
        assert CCN_REGIONS["VA"] == 1  # Northeast
        assert CCN_REGIONS["FL"] == 2  # Southeast
        assert CCN_REGIONS["TX"] == 3  # Central

        # TriWest regions (4, 5)
        assert CCN_REGIONS["CO"] == 4  # Mountain
        assert CCN_REGIONS["CA"] == 5  # Pacific

        # Check all states are covered
        us_states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
        ]
        for state in us_states:
            assert state in CCN_REGIONS, f"State {state} not in CCN_REGIONS"

    def test_tpa_contacts(self):
        """Test TPA contact information structure."""
        assert "optum" in TPA_CONTACTS
        assert "triwest" in TPA_CONTACTS

        assert TPA_CONTACTS["optum"]["regions"] == [1, 2, 3]
        assert TPA_CONTACTS["triwest"]["regions"] == [4, 5]

        assert "phone" in TPA_CONTACTS["optum"]
        assert "phone" in TPA_CONTACTS["triwest"]

    def test_run_with_real_data(self):
        """Test run() with the actual providers data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "va_community_care_providers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("va_community_care_providers.json not found in project")

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        # Should have 10+ providers
        assert len(resources) >= 10

        # All should have va-community-care tag
        assert all("va-community-care" in r.tags for r in resources)

        # All should have location fields
        for resource in resources:
            assert resource.state is not None, f"Provider missing state: {resource.title}"
            assert resource.city is not None, f"Provider missing city: {resource.title}"
            assert resource.address is not None, f"Provider missing address: {resource.title}"
            assert resource.zip_code is not None, f"Provider missing zip_code: {resource.title}"

        # Should have variety of specialties
        specialties = set()
        for r in resources:
            raw = r.raw_data
            if raw and "specialty" in raw:
                specialties.add(raw["specialty"])
        assert len(specialties) >= 5, f"Expected 5+ specialties, got {len(specialties)}"

        # Check phone normalization
        for resource in resources:
            if resource.phone:
                # Should be normalized format
                assert "(" in resource.phone or resource.phone.startswith("8"), (
                    f"Phone not normalized: {resource.phone}"
                )

        # Check first resource structure
        first = resources[0]
        assert first.title is not None
        assert first.description is not None
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.categories is not None
        assert first.tags is not None
        assert first.scope == "local"

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        data = {"metadata": {"source": "test"}, "providers": []}
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        with VACommunityConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_description_includes_custom_description(self, tmp_path):
        """Test that custom descriptions are used when provided."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Veteran Wellness Center",
                    "org_name": "VWC",
                    "specialty": "mental_health",
                    "city": "Seattle",
                    "state": "WA",
                    "zip_code": "98101",
                    "address": "100 Main St",
                    "phone": "206-555-1234",
                    "network_status": "in_network",
                    "description": "Custom description for this specific provider with PTSD expertise.",
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        assert "Custom description" in resources[0].description
        assert "PTSD expertise" in resources[0].description

    def test_not_accepting_patients_note(self, tmp_path):
        """Test that not accepting patients flag is noted."""
        data = {
            "metadata": {"source": "test"},
            "providers": [
                {
                    "provider_name": "Busy Clinic",
                    "org_name": "Busy Clinic",
                    "specialty": "primary_care",
                    "city": "Boston",
                    "state": "MA",
                    "zip_code": "02101",
                    "address": "50 Beacon St",
                    "phone": "617-555-1234",
                    "network_status": "in_network",
                    "accepting_new_patients": False,
                }
            ],
        }
        data_file = tmp_path / "providers.json"
        data_file.write_text(json.dumps(data))

        connector = VACommunityConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        assert "not be accepting" in resources[0].description.lower()
        assert "accepting-patients" not in resources[0].tags
