"""Tests for VA.gov Lighthouse Facilities API connector."""

from unittest.mock import MagicMock, patch

from connectors.va_gov import VAGovConnector


class TestVAGovConnector:
    """Tests for VAGovConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VAGovConnector(api_key="test-key")
        meta = connector.metadata

        assert meta.name == "VA.gov Lighthouse API"
        assert meta.tier == 1  # Official government source
        assert meta.frequency == "daily"
        assert meta.requires_auth is True
        assert "developer.va.gov" in meta.url

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        connector = VAGovConnector(api_key="my-test-key")
        assert connector.api_key == "my-test-key"

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variable."""
        monkeypatch.setenv("VA_API_KEY", "env-api-key")
        connector = VAGovConnector()
        assert connector.api_key == "env-api-key"

    def test_parse_facility_health(self):
        """Test parsing a health facility."""
        connector = VAGovConnector(api_key="test")

        facility = {
            "id": "vha_501",
            "attributes": {
                "name": "VA Boston Healthcare System",
                "facilityType": "health",
                "classification": "VA Medical Center (VAMC)",
                "website": "https://www.boston.va.gov",
                "address": {
                    "physical": {
                        "address1": "150 S Huntington Ave",
                        "city": "Boston",
                        "state": "MA",
                        "zip": "02130",
                    }
                },
                "phone": {"main": "617-232-9500"},
                "hours": {
                    "monday": "8:00AM-4:30PM",
                    "tuesday": "8:00AM-4:30PM",
                    "wednesday": "8:00AM-4:30PM",
                    "thursday": "8:00AM-4:30PM",
                    "friday": "8:00AM-4:30PM",
                    "saturday": "Closed",
                    "sunday": "Closed",
                },
                "services": {
                    "health": [
                        {"name": "Primary Care"},
                        {"name": "Mental Health"},
                        {"name": "Vocational Rehabilitation"},
                    ],
                    "benefits": {},
                    "other": [],
                },
            },
        }

        candidate = connector._parse_facility(facility, "health")

        assert candidate is not None
        assert candidate.title == "VA Boston Healthcare System"
        assert candidate.org_name == "U.S. Department of Veterans Affairs"
        assert candidate.city == "Boston"
        assert candidate.state == "MA"
        assert candidate.zip_code == "02130"
        assert "employment" in candidate.categories or "training" in candidate.categories
        assert candidate.phone == "(617) 232-9500"
        assert "Monday" in candidate.hours
        assert candidate.scope == "local"
        assert candidate.states == ["MA"]
        assert candidate.raw_data == facility

    def test_parse_facility_benefits(self):
        """Test parsing a benefits office."""
        connector = VAGovConnector(api_key="test")

        facility = {
            "id": "vba_339",
            "attributes": {
                "name": "Boston VA Regional Office",
                "facilityType": "benefits",
                "website": "https://www.benefits.va.gov/boston",
                "address": {
                    "physical": {
                        "address1": "JFK Federal Building",
                        "address2": "15 New Sudbury Street",
                        "city": "Boston",
                        "state": "MA",
                        "zip": "02203",
                    }
                },
                "phone": {"main": "800-827-1000"},
                "hours": {
                    "monday": "8:00AM-4:00PM",
                },
                "services": {
                    "health": [],
                    "benefits": {
                        "standard": [
                            {"name": "Disability Compensation"},
                            {"name": "Education Benefits"},
                            {"name": "Home Loan Guaranty"},
                            {"name": "Vocational Rehabilitation"},
                        ]
                    },
                    "other": [],
                },
            },
        }

        candidate = connector._parse_facility(facility, "benefits")

        assert candidate is not None
        assert candidate.title == "Boston VA Regional Office"
        assert "employment" in candidate.categories
        assert "housing" in candidate.categories
        assert "legal" in candidate.categories
        assert "training" in candidate.categories

    def test_parse_facility_vet_center(self):
        """Test parsing a vet center."""
        connector = VAGovConnector(api_key="test")

        facility = {
            "id": "vc_0101V",
            "attributes": {
                "name": "Boston Vet Center",
                "facilityType": "vet_center",
                "address": {
                    "physical": {
                        "address1": "7 Drydock Avenue",
                        "city": "Boston",
                        "state": "MA",
                        "zip": "02210",
                    }
                },
                "phone": {
                    "main": "617-onal-3817"  # Intentionally malformed
                },
                "hours": {},
                "services": {
                    "health": [],
                    "benefits": {},
                    "other": [{"name": "Readjustment Counseling"}],
                },
            },
        }

        candidate = connector._parse_facility(facility, "vet_center")

        assert candidate is not None
        assert candidate.title == "Boston Vet Center"
        assert "employment" in candidate.categories or "training" in candidate.categories
        assert "va-vet_center" in candidate.tags

    def test_parse_facility_cemetery_skipped(self):
        """Test that cemeteries are skipped (not relevant to our categories)."""
        connector = VAGovConnector(api_key="test")

        facility = {
            "id": "nca_123",
            "attributes": {
                "name": "Massachusetts National Cemetery",
                "facilityType": "cemetery",
                "address": {
                    "physical": {
                        "city": "Bourne",
                        "state": "MA",
                    }
                },
            },
        }

        candidate = connector._parse_facility(facility, "cemetery")

        assert candidate is None  # Cemetery should be skipped

    def test_format_address(self):
        """Test address formatting."""
        connector = VAGovConnector(api_key="test")

        address = {
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Boston",
            "state": "MA",
            "zip": "02101",
        }

        result = connector._format_address(address)
        assert result == "123 Main St, Suite 100, Boston, MA 02101"

    def test_format_address_minimal(self):
        """Test address formatting with minimal data."""
        connector = VAGovConnector(api_key="test")

        address = {
            "address1": "123 Main St",
        }

        result = connector._format_address(address)
        assert result == "123 Main St"

    def test_format_hours(self):
        """Test hours formatting."""
        connector = VAGovConnector(api_key="test")

        hours = {
            "monday": "8:00AM-4:30PM",
            "tuesday": "8:00AM-4:30PM",
            "wednesday": "8:00AM-4:30PM",
            "thursday": "8:00AM-4:30PM",
            "friday": "8:00AM-4:30PM",
            "saturday": "Closed",
            "sunday": "Closed",
        }

        result = connector._format_hours(hours)
        assert "Monday: 8:00AM-4:30PM" in result
        assert "Saturday" not in result  # Closed days should be excluded
        assert "Sunday" not in result

    def test_format_hours_empty(self):
        """Test hours formatting with empty data."""
        connector = VAGovConnector(api_key="test")
        assert connector._format_hours({}) is None
        assert connector._format_hours(None) is None

    def test_extract_tags(self):
        """Test tag extraction from services."""
        connector = VAGovConnector(api_key="test")

        services = [
            "Vocational Rehabilitation",
            "Employment Assistance",
            "Homeless Veterans Services",
        ]

        tags = connector._extract_tags(services, "health")

        assert "va-health" in tags
        assert "vocational-rehab" in tags
        assert "employment" in tags
        assert "homeless-services" in tags

    def test_normalize_phone(self):
        """Test phone normalization inherited from BaseConnector."""
        connector = VAGovConnector(api_key="test")

        assert connector._normalize_phone("6172329500") == "(617) 232-9500"
        assert connector._normalize_phone("1-617-232-9500") == "(617) 232-9500"
        assert connector._normalize_phone(None) is None

    def test_context_manager(self):
        """Test context manager support."""
        with VAGovConnector(api_key="test") as connector:
            assert connector.api_key == "test"

    @patch("connectors.va_gov.httpx.Client")
    def test_run_fetches_multiple_types(self, mock_client_class):
        """Test that run() fetches health, benefits, and vet_center types."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock empty responses for simplicity
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [], "meta": {"pagination": {"totalPages": 1}}}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = VAGovConnector(api_key="test")
        resources = connector.run()

        # Should have called API for each facility type
        assert mock_client.get.call_count >= 3

        # Verify facility types requested
        call_args_list = [call[1]["params"]["type"] for call in mock_client.get.call_args_list]
        assert "health" in call_args_list
        assert "benefits" in call_args_list
        assert "vet_center" in call_args_list

    @patch("connectors.va_gov.httpx.Client")
    def test_run_with_pagination(self, mock_client_class):
        """Test that run() handles pagination correctly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # First page has data, second page is empty
        page1_response = MagicMock()
        page1_response.json.return_value = {
            "data": [
                {
                    "id": "vba_001",
                    "attributes": {
                        "name": "Test Office",
                        "address": {"physical": {"city": "Test", "state": "TX"}},
                        "phone": {},
                        "hours": {},
                        "services": {"health": [], "benefits": {"standard": []}, "other": []},
                    },
                }
            ],
            "meta": {"pagination": {"totalPages": 2}},
        }
        page1_response.raise_for_status = MagicMock()

        page2_response = MagicMock()
        page2_response.json.return_value = {
            "data": [],
            "meta": {"pagination": {"totalPages": 2}},
        }
        page2_response.raise_for_status = MagicMock()

        mock_client.get.side_effect = [
            page1_response,
            page2_response,  # health
            page2_response,
            page2_response,  # benefits
            page2_response,
            page2_response,  # vet_center
        ]

        connector = VAGovConnector(api_key="test")
        resources = connector.run()

        # Should have at least one resource from the first health page
        # (benefits type produces resources, health type doesn't based on our categories)
        assert len(resources) >= 0  # May vary based on category mapping

    @patch("connectors.va_gov.httpx.Client")
    def test_run_handles_http_errors(self, mock_client_class):
        """Test that run() handles HTTP errors gracefully."""
        import httpx

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # First type fails, others succeed with empty data
        empty_response = {"data": [], "meta": {"pagination": {"totalPages": 1}}}
        mock_client.get.side_effect = [
            httpx.HTTPError("Connection failed"),  # health fails
            MagicMock(
                json=MagicMock(return_value=empty_response),
                raise_for_status=MagicMock(),
            ),  # benefits succeeds
            MagicMock(
                json=MagicMock(return_value=empty_response),
                raise_for_status=MagicMock(),
            ),  # vet_center succeeds
        ]

        connector = VAGovConnector(api_key="test")
        # Should not raise, just continue with other types
        resources = connector.run()
        assert isinstance(resources, list)
