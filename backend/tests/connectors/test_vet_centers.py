"""Tests for the Vet Centers connector."""

from unittest.mock import MagicMock, patch

from connectors.vet_centers import VetCentersConnector


class TestVetCentersConnector:
    """Test suite for VetCentersConnector."""

    def test_metadata(self):
        """Test connector metadata is correct."""
        connector = VetCentersConnector()
        metadata = connector.metadata

        assert metadata.name == "VA Vet Centers (Lighthouse API)"
        assert metadata.tier == 1
        assert metadata.frequency == "weekly"
        assert metadata.requires_auth is True
        assert "vetcenter.va.gov" in metadata.url

    def test_parse_vet_center_basic(self):
        """Test parsing a basic Vet Center facility."""
        connector = VetCentersConnector()

        facility = {
            "id": "vc_123",
            "attributes": {
                "name": "Springfield Vet Center",
                "address": {
                    "physical": {
                        "address1": "123 Main St",
                        "city": "Springfield",
                        "state": "IL",
                        "zip": "62701",
                    }
                },
                "phone": {"main": "217-555-1234"},
                "hours": {
                    "monday": "8:00AM-4:30PM",
                    "tuesday": "8:00AM-4:30PM",
                    "wednesday": "8:00AM-4:30PM",
                    "thursday": "8:00AM-4:30PM",
                    "friday": "8:00AM-4:30PM",
                    "saturday": "Closed",
                    "sunday": "Closed",
                },
                "website": "https://www.va.gov/springfield-vet-center/",
                "services": {"health": [], "other": []},
            },
        }

        result = connector._parse_vet_center(facility)

        assert result is not None
        assert result.title == "Springfield Vet Center"
        assert result.city == "Springfield"
        assert result.state == "IL"
        assert result.zip_code == "62701"
        assert result.phone == "(217) 555-1234"
        assert "benefits" in result.categories
        assert "vet-center" in result.tags
        assert "confidential" in result.tags
        assert "combat veterans" in result.eligibility.lower() or "combat zone" in result.eligibility.lower()

    def test_parse_mobile_vet_center(self):
        """Test parsing a Mobile Vet Center."""
        connector = VetCentersConnector()

        facility = {
            "id": "mvc_456",
            "attributes": {
                "name": "Mobile Vet Center - Region 5",
                "address": {
                    "physical": {
                        "address1": "",
                        "city": "Chicago",
                        "state": "IL",
                        "zip": "",
                    }
                },
                "phone": {"main": "1-877-927-8387"},
                "hours": {},
                "services": {"health": [], "other": []},
            },
        }

        result = connector._parse_vet_center(facility)

        assert result is not None
        assert "Mobile Vet Center" in result.title
        assert "mobile-vet-center" in result.tags
        assert "Mobile Vet Center" in result.description
        assert "schedule" in result.how_to_apply.lower()

    def test_extract_services(self):
        """Test service extraction from facility attributes."""
        connector = VetCentersConnector()

        attrs = {
            "services": {
                "health": [
                    {"name": "Individual Counseling"},
                    {"name": "Group Counseling"},
                ],
                "other": [
                    {"name": "Benefits Referral"},
                ],
            }
        }

        services = connector._extract_services(attrs)

        assert "Individual Counseling" in services
        assert "Group Counseling" in services
        assert "Benefits Referral" in services

    def test_format_hours(self):
        """Test hours formatting."""
        connector = VetCentersConnector()

        hours_obj = {
            "monday": "8:00AM-4:30PM",
            "tuesday": "8:00AM-4:30PM",
            "wednesday": "8:00AM-7:00PM",
            "thursday": "8:00AM-4:30PM",
            "friday": "8:00AM-4:30PM",
            "saturday": "Closed",
            "sunday": "Closed",
        }

        result = connector._format_hours(hours_obj)

        assert "Monday: 8:00AM-4:30PM" in result
        assert "Wednesday: 8:00AM-7:00PM" in result
        assert "Saturday" not in result  # Closed days excluded

    def test_format_address_complete(self):
        """Test address formatting with complete data."""
        connector = VetCentersConnector()

        address_obj = {
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }

        result = connector._format_address(address_obj)

        assert "123 Main St" in result
        assert "Suite 100" in result
        assert "Springfield" in result
        assert "IL" in result
        assert "62701" in result

    def test_format_address_minimal(self):
        """Test address formatting with minimal data."""
        connector = VetCentersConnector()

        address_obj = {
            "address1": "456 Oak Ave",
            "city": "",
            "state": "",
        }

        result = connector._format_address(address_obj)

        assert result == "456 Oak Ave"

    def test_build_tags_standard(self):
        """Test tag building for standard Vet Center."""
        connector = VetCentersConnector()

        tags = connector._build_tags(
            services=["Individual Counseling", "Bereavement Services"],
            is_mobile=False,
            name="Test Vet Center",
        )

        assert "vet-center" in tags
        assert "counseling" in tags
        assert "ptsd" in tags
        assert "mst" in tags
        assert "bereavement" in tags
        assert "mobile-vet-center" not in tags

    def test_build_tags_mobile(self):
        """Test tag building for Mobile Vet Center."""
        connector = VetCentersConnector()

        tags = connector._build_tags(
            services=[],
            is_mobile=True,
            name="Mobile Vet Center",
        )

        assert "mobile-vet-center" in tags
        assert "outreach" in tags

    def test_eligibility_contains_key_groups(self):
        """Test that eligibility text covers all key eligible groups."""
        from connectors.vet_centers import VET_CENTER_ELIGIBILITY

        eligibility_lower = VET_CENTER_ELIGIBILITY.lower()

        # Combat veterans
        assert "combat" in eligibility_lower

        # MST survivors
        assert "mst" in eligibility_lower or "military sexual trauma" in eligibility_lower

        # Drone crews
        assert "drone" in eligibility_lower or "unmanned aerial vehicle" in eligibility_lower

        # Mortuary services
        assert "mortuary" in eligibility_lower

        # Family members
        assert "family" in eligibility_lower

        # National emergency responders
        assert "national emergency" in eligibility_lower or "disaster" in eligibility_lower

    def test_context_manager(self):
        """Test connector works as context manager."""
        with VetCentersConnector() as connector:
            assert connector is not None
            metadata = connector.metadata
            assert metadata.name is not None

    @patch("connectors.vet_centers.httpx.Client")
    def test_run_with_mocked_api(self, mock_client_class):
        """Test the run method with mocked API response."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "vc_001",
                    "attributes": {
                        "name": "Test Vet Center",
                        "address": {
                            "physical": {
                                "address1": "100 Test St",
                                "city": "Testville",
                                "state": "TX",
                                "zip": "75001",
                            }
                        },
                        "phone": {"main": "555-123-4567"},
                        "hours": {"monday": "8AM-5PM"},
                        "services": {"health": [], "other": []},
                    },
                }
            ],
            "meta": {"pagination": {"totalPages": 1}},
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = VetCentersConnector(api_key="test-key")
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].title == "Test Vet Center"
        assert resources[0].state == "TX"

    def test_normalize_phone(self):
        """Test phone number normalization."""
        connector = VetCentersConnector()

        # 10-digit phone
        assert connector._normalize_phone("5551234567") == "(555) 123-4567"

        # 11-digit with leading 1
        assert connector._normalize_phone("15551234567") == "(555) 123-4567"

        # Already formatted
        assert connector._normalize_phone("(555) 123-4567") == "(555) 123-4567"

        # None input
        assert connector._normalize_phone(None) is None

    def test_normalize_state(self):
        """Test state normalization."""
        connector = VetCentersConnector()

        assert connector._normalize_state("TX") == "TX"
        assert connector._normalize_state("tx") == "TX"
        assert connector._normalize_state("  TX  ") == "TX"
        assert connector._normalize_state(None) is None
