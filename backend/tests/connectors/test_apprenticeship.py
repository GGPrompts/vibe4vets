"""Tests for DOL Apprenticeship Office API connector."""

from unittest.mock import MagicMock, patch

from connectors.apprenticeship import ApprenticeshipConnector


class TestApprenticeshipConnector:
    """Tests for ApprenticeshipConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = ApprenticeshipConnector(api_key="test-key")
        meta = connector.metadata

        assert meta.name == "CareerOneStop Apprenticeship Offices"
        assert meta.tier == 1  # Official DOL government source
        assert meta.frequency == "monthly"
        assert meta.requires_auth is True
        assert "careeronestop.org" in meta.url

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        connector = ApprenticeshipConnector(api_key="my-test-key", user_id="my-user")
        assert connector.api_key == "my-test-key"
        assert connector.user_id == "my-user"

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variables."""
        monkeypatch.setenv("CAREERONESTOP_API_KEY", "env-api-key")
        monkeypatch.setenv("CAREERONESTOP_USER_ID", "env-user-id")
        connector = ApprenticeshipConnector()
        assert connector.api_key == "env-api-key"
        assert connector.user_id == "env-user-id"

    def test_init_default_user_id(self):
        """Test initialization uses default user ID when not provided."""
        connector = ApprenticeshipConnector(api_key="test")
        assert connector.user_id == "vibe4vets"

    def test_parse_office_basic(self):
        """Test parsing a basic apprenticeship office."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Texas Workforce Commission - Apprenticeship Division",
            "Address": "101 E 15th Street",
            "City": "Austin",
            "State": "TX",
            "Zip": "78778",
            "Phone": "512-463-2222",
            "Email": "apprenticeship@twc.texas.gov",
            "URL": "https://www.twc.texas.gov/apprenticeship",
        }

        candidate = connector._parse_office(office)

        assert candidate is not None
        assert "Apprenticeship Office - Texas Workforce Commission" in candidate.title
        assert candidate.org_name == "Texas Workforce Commission - Apprenticeship Division"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78778"
        assert candidate.categories == ["training"]
        assert candidate.phone == "(512) 463-2222"
        assert candidate.email == "apprenticeship@twc.texas.gov"
        assert candidate.scope == "state"
        assert candidate.states == ["TX"]
        assert candidate.raw_data == office

    def test_parse_office_alternate_field_names(self):
        """Test parsing an office with alternate field names."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "OfficeName": "California Division of Apprenticeship Standards",
            "Address1": "455 Golden Gate Avenue",
            "City": "San Francisco",
            "StateName": "CA",
            "ZipCode": "94102",
            "Telephone": "415-703-5900",
            "EmailAddress": "das@dir.ca.gov",
            "Website": "https://www.dir.ca.gov/das/",
            "OfficeType": "State Agency",
        }

        candidate = connector._parse_office(office)

        assert candidate is not None
        assert "California Division of Apprenticeship Standards" in candidate.title
        assert candidate.city == "San Francisco"
        assert candidate.state == "CA"
        assert candidate.zip_code == "94102"
        assert candidate.phone == "(415) 703-5900"
        assert candidate.email == "das@dir.ca.gov"
        assert "state-apprenticeship-agency" in candidate.tags

    def test_parse_office_minimal(self):
        """Test parsing an office with minimal data."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Basic Apprenticeship Office",
            "City": "Unknown City",
            "State": "CA",
        }

        candidate = connector._parse_office(office)

        assert candidate is not None
        assert "Basic Apprenticeship Office" in candidate.title
        assert candidate.address is None
        assert candidate.zip_code is None
        assert candidate.phone is None
        assert "careeronestop.org" in candidate.source_url

    def test_parse_office_no_name(self):
        """Test that offices without names are skipped."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Address": "123 Main St",
            "City": "Austin",
            "State": "TX",
        }

        candidate = connector._parse_office(office)

        assert candidate is None

    def test_build_description_state_office(self):
        """Test description building for state office."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Test Office",
            "OfficeType": "State Agency",
        }

        description = connector._build_description(office)

        assert "apprenticeship" in description.lower()
        assert "earn while you learn" in description.lower()
        assert "state office" in description.lower()
        assert "veterans" in description.lower()
        assert "gi bill" in description.lower()

    def test_build_description_federal_office(self):
        """Test description includes federal office context."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Test Office",
            "OfficeType": "Federal Regional Office",
        }

        description = connector._build_description(office)

        assert "federal office" in description.lower()

    def test_build_eligibility(self):
        """Test eligibility text includes veteran info."""
        connector = ApprenticeshipConnector(api_key="test")

        eligibility = connector._build_eligibility()

        assert "16 years or older" in eligibility
        assert "veterans" in eligibility.lower()
        assert "gi bill" in eligibility.lower()
        assert "priority" in eligibility.lower()

    def test_build_how_to_apply_with_contact(self):
        """Test how to apply with phone and email."""
        connector = ApprenticeshipConnector(api_key="test")

        how_to = connector._build_how_to_apply(
            office_name="Texas Apprenticeship Office",
            phone="(512) 555-1234",
            email="info@example.gov",
        )

        assert "Texas Apprenticeship Office" in how_to
        assert "(512) 555-1234" in how_to
        assert "info@example.gov" in how_to
        assert "apprenticeship.gov" in how_to.lower()

    def test_build_how_to_apply_minimal(self):
        """Test how to apply without contact info."""
        connector = ApprenticeshipConnector(api_key="test")

        how_to = connector._build_how_to_apply(
            office_name="Test Office",
            phone=None,
            email=None,
        )

        assert "Test Office" in how_to
        assert "apprenticeship.gov" in how_to.lower()

    def test_extract_tags_basic(self):
        """Test tag extraction for basic office."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Test Office",
        }

        tags = connector._extract_tags(office, "")

        assert "apprenticeship" in tags
        assert "apprenticeships" in tags
        assert "training" in tags
        assert "on-the-job-training" in tags
        assert "gi-bill-eligible" in tags
        assert "registered-apprenticeship" in tags

    def test_extract_tags_with_office_type(self):
        """Test tag extraction includes office type."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {"Name": "Test Office"}

        tags_state = connector._extract_tags(office, "State Agency")
        assert "state-apprenticeship-agency" in tags_state

        tags_federal = connector._extract_tags(office, "Federal Regional Office")
        assert "federal-apprenticeship-office" in tags_federal

    def test_extract_tags_with_industries(self):
        """Test tag extraction includes industry keywords."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Test Office",
            "Programs": "Construction, Electrical, HVAC, Manufacturing",
        }

        tags = connector._extract_tags(office, "")

        assert "construction-trades" in tags
        assert "electrical-trades" in tags
        assert "hvac-trades" in tags
        assert "manufacturing" in tags

    def test_create_office_id(self):
        """Test unique ID creation for deduplication."""
        connector = ApprenticeshipConnector(api_key="test")

        office1 = {
            "Name": "Test Office",
            "Address": "123 Main St",
            "City": "Austin",
            "State": "TX",
        }

        office2 = {
            "Name": "Test Office",
            "Address": "123 Main St",
            "City": "Austin",
            "State": "TX",
        }

        office3 = {
            "Name": "Different Office",
            "Address": "456 Oak Ave",
            "City": "Austin",
            "State": "TX",
        }

        id1 = connector._create_office_id(office1)
        id2 = connector._create_office_id(office2)
        id3 = connector._create_office_id(office3)

        assert id1 == id2  # Same office = same ID
        assert id1 != id3  # Different office = different ID

    def test_create_office_id_alternate_fields(self):
        """Test ID creation with alternate field names."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "OfficeName": "Test Office",
            "Address1": "123 Main St",
            "City": "Austin",
            "StateName": "TX",
        }

        office_id = connector._create_office_id(office)
        assert "test office" in office_id
        assert "123 main st" in office_id

    def test_normalize_phone(self):
        """Test phone normalization inherited from BaseConnector."""
        connector = ApprenticeshipConnector(api_key="test")

        assert connector._normalize_phone("5124632222") == "(512) 463-2222"
        assert connector._normalize_phone("1-512-463-2222") == "(512) 463-2222"
        assert connector._normalize_phone("(512) 463-2222") == "(512) 463-2222"
        assert connector._normalize_phone(None) is None

    def test_context_manager(self):
        """Test context manager support."""
        with ApprenticeshipConnector(api_key="test") as connector:
            assert connector.api_key == "test"

    @patch("connectors.apprenticeship.httpx.Client")
    def test_run_fetches_by_state(self, mock_client_class):
        """Test that run() fetches offices by state."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock response with one office
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ApprenticeshipOfficeList": [
                {
                    "Name": "Texas Apprenticeship Office",
                    "Address": "123 Main St",
                    "City": "Austin",
                    "State": "TX",
                    "Zip": "78701",
                    "Phone": "512-555-1234",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = ApprenticeshipConnector(api_key="test")
        resources = connector.run()

        # Should have called API for each state
        assert mock_client.get.call_count == len(connector.US_STATES)

    @patch("connectors.apprenticeship.httpx.Client")
    def test_run_deduplicates_offices(self, mock_client_class):
        """Test that run() deduplicates offices across states."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Same office returned for multiple states (regional offices)
        duplicate_office = {
            "Name": "Regional Apprenticeship Office",
            "Address": "123 Federal Way",
            "City": "Dallas",
            "State": "TX",
            "Zip": "75201",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {"ApprenticeshipOfficeList": [duplicate_office]}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = ApprenticeshipConnector(api_key="test")
        resources = connector.run()

        # Should only have one instance despite being returned multiple times
        assert len(resources) == 1

    @patch("connectors.apprenticeship.httpx.Client")
    def test_run_handles_http_errors(self, mock_client_class):
        """Test that run() handles HTTP errors gracefully."""
        import httpx

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # All requests fail
        mock_client.get.side_effect = httpx.HTTPError("Connection failed")

        connector = ApprenticeshipConnector(api_key="test")
        # Should not raise, just return empty list
        resources = connector.run()
        assert isinstance(resources, list)
        assert len(resources) == 0

    @patch("connectors.apprenticeship.httpx.Client")
    def test_run_handles_empty_response(self, mock_client_class):
        """Test that run() handles empty API responses."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"ApprenticeshipOfficeList": []}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = ApprenticeshipConnector(api_key="test")
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 0

    @patch("connectors.apprenticeship.httpx.Client")
    def test_run_handles_missing_list(self, mock_client_class):
        """Test that run() handles response without ApprenticeshipOfficeList."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {}  # No ApprenticeshipOfficeList key
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = ApprenticeshipConnector(api_key="test")
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 0

    def test_categories_are_training(self):
        """Test that all offices are categorized as training."""
        connector = ApprenticeshipConnector(api_key="test")

        office = {
            "Name": "Test Office",
            "City": "Austin",
            "State": "TX",
        }

        candidate = connector._parse_office(office)

        assert candidate is not None
        assert candidate.categories == ["training"]
