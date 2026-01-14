"""Tests for CareerOneStop American Job Center API connector."""

from unittest.mock import MagicMock, patch

from connectors.careeronestop import CareerOneStopConnector


class TestCareerOneStopConnector:
    """Tests for CareerOneStopConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = CareerOneStopConnector(api_key="test-key")
        meta = connector.metadata

        assert meta.name == "CareerOneStop American Job Centers"
        assert meta.tier == 1  # Official DOL government source
        assert meta.frequency == "weekly"
        assert meta.requires_auth is True
        assert "careeronestop.org" in meta.url

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        connector = CareerOneStopConnector(api_key="my-test-key", user_id="my-user")
        assert connector.api_key == "my-test-key"
        assert connector.user_id == "my-user"

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment variables."""
        monkeypatch.setenv("CAREERONESTOP_API_KEY", "env-api-key")
        monkeypatch.setenv("CAREERONESTOP_USER_ID", "env-user-id")
        connector = CareerOneStopConnector()
        assert connector.api_key == "env-api-key"
        assert connector.user_id == "env-user-id"

    def test_init_default_user_id(self):
        """Test initialization uses default user ID when not provided."""
        connector = CareerOneStopConnector(api_key="test")
        assert connector.user_id == "vibe4vets"

    def test_parse_center_basic(self):
        """Test parsing a basic American Job Center."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Austin Workforce Solutions",
            "Address": "6505 Airport Blvd",
            "City": "Austin",
            "StateName": "TX",
            "Zip": "78752",
            "Phone": "512-223-7400",
            "Email": "info@workforcesolutions.com",
            "URL": "https://www.workforcesolutionscapitalarea.com",
            "Hours": "Monday-Friday 8:00AM-5:00PM",
        }

        candidate = connector._parse_center(center)

        assert candidate is not None
        assert candidate.title == "Austin Workforce Solutions"
        assert candidate.org_name == "American Job Center"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78752"
        assert "employment" in candidate.categories
        assert "training" in candidate.categories
        assert candidate.phone == "(512) 223-7400"
        assert candidate.email == "info@workforcesolutions.com"
        assert "Monday-Friday" in candidate.hours
        assert candidate.scope == "local"
        assert candidate.states == ["TX"]
        assert candidate.raw_data == center

    def test_parse_center_with_veteran_rep(self):
        """Test parsing a center with veteran representative info."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Texas Workforce Commission",
            "Address": "101 Main St",
            "City": "Dallas",
            "StateName": "TX",
            "Zip": "75201",
            "Phone": "214-555-1234",
            "VeteranRepName": "John Smith",
            "VeteranRepPhone": "214-555-4321",
            "VeteranRepEmail": "john.smith@twc.texas.gov",
        }

        candidate = connector._parse_center(center)

        assert candidate is not None
        assert "veterans representative" in candidate.description.lower()
        assert "John Smith" in candidate.description
        assert "veteran-priority" in candidate.tags
        assert "veteran-representative" in candidate.tags

    def test_parse_center_minimal(self):
        """Test parsing a center with minimal data."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Basic Job Center",
            "City": "Unknown City",
            "StateName": "CA",
        }

        candidate = connector._parse_center(center)

        assert candidate is not None
        assert candidate.title == "Basic Job Center"
        assert candidate.address is None
        assert candidate.zip_code is None
        assert candidate.phone is None
        assert "careeronestop.org" in candidate.source_url

    def test_parse_center_no_name(self):
        """Test that centers without names are skipped."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Address": "123 Main St",
            "City": "Austin",
            "StateName": "TX",
        }

        candidate = connector._parse_center(center)

        assert candidate is None

    def test_build_description_basic(self):
        """Test description building without veteran rep."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "Services": "Resume Writing, Job Matching, Training Referrals",
        }

        description = connector._build_description(center)

        assert "American Job Center" in description
        assert "employment" in description.lower()
        assert "Resume Writing, Job Matching" in description

    def test_build_description_with_veteran_rep(self):
        """Test description includes veteran representative info."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "VeteranRepName": "Jane Doe",
            "VeteranRepPhone": "555-123-4567",
            "VeteranRepEmail": "jane@example.gov",
        }

        description = connector._build_description(center)

        assert "veterans representative" in description.lower()
        assert "Jane Doe" in description
        assert "555-123-4567" in description
        assert "jane@example.gov" in description

    def test_format_hours_string(self):
        """Test hours formatting from string field."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Hours": "Mon-Fri 8AM-5PM",
        }

        hours = connector._format_hours(center)
        assert hours == "Mon-Fri 8AM-5PM"

    def test_format_hours_empty(self):
        """Test hours formatting with no data."""
        connector = CareerOneStopConnector(api_key="test")

        center = {}
        hours = connector._format_hours(center)
        assert hours is None

    def test_extract_tags_basic(self):
        """Test tag extraction for basic center."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
        }

        tags = connector._extract_tags(center)

        assert "american-job-center" in tags
        assert "employment" in tags
        assert "training" in tags
        assert "career-services" in tags

    def test_extract_tags_with_veteran_rep(self):
        """Test tag extraction includes veteran tags when rep present."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "VeteranRepName": "John Doe",
        }

        tags = connector._extract_tags(center)

        assert "veteran-priority" in tags
        assert "veteran-representative" in tags

    def test_extract_tags_with_center_type(self):
        """Test tag extraction includes center type."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "CenterType": "Comprehensive",
        }

        tags = connector._extract_tags(center)

        assert "ajc-comprehensive" in tags

    def test_create_center_id(self):
        """Test unique ID creation for deduplication."""
        connector = CareerOneStopConnector(api_key="test")

        center1 = {
            "Name": "Test Center",
            "Address": "123 Main St",
            "City": "Austin",
            "StateName": "TX",
        }

        center2 = {
            "Name": "Test Center",
            "Address": "123 Main St",
            "City": "Austin",
            "StateName": "TX",
        }

        center3 = {
            "Name": "Different Center",
            "Address": "456 Oak Ave",
            "City": "Austin",
            "StateName": "TX",
        }

        id1 = connector._create_center_id(center1)
        id2 = connector._create_center_id(center2)
        id3 = connector._create_center_id(center3)

        assert id1 == id2  # Same center = same ID
        assert id1 != id3  # Different center = different ID

    def test_normalize_phone(self):
        """Test phone normalization inherited from BaseConnector."""
        connector = CareerOneStopConnector(api_key="test")

        assert connector._normalize_phone("5122237400") == "(512) 223-7400"
        assert connector._normalize_phone("1-512-223-7400") == "(512) 223-7400"
        assert connector._normalize_phone("(512) 223-7400") == "(512) 223-7400"
        assert connector._normalize_phone(None) is None

    def test_context_manager(self):
        """Test context manager support."""
        with CareerOneStopConnector(api_key="test") as connector:
            assert connector.api_key == "test"

    @patch("connectors.careeronestop.httpx.Client")
    def test_run_fetches_by_state(self, mock_client_class):
        """Test that run() fetches AJCs by state."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock response with one center
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "OneStopCenterList": [
                {
                    "Name": "Texas Job Center",
                    "Address": "123 Main St",
                    "City": "Austin",
                    "StateName": "TX",
                    "Zip": "78701",
                    "Phone": "512-555-1234",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = CareerOneStopConnector(api_key="test")
        resources = connector.run()

        # Should have called API for each state
        assert mock_client.get.call_count == len(connector.US_STATES)

    @patch("connectors.careeronestop.httpx.Client")
    def test_run_deduplicates_centers(self, mock_client_class):
        """Test that run() deduplicates centers across states."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Same center returned for multiple states (edge case at state borders)
        duplicate_center = {
            "Name": "Border Job Center",
            "Address": "123 Border St",
            "City": "Texarkana",
            "StateName": "TX",
            "Zip": "75501",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {"OneStopCenterList": [duplicate_center]}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = CareerOneStopConnector(api_key="test")
        resources = connector.run()

        # Should only have one instance despite being returned multiple times
        assert len(resources) == 1

    @patch("connectors.careeronestop.httpx.Client")
    def test_run_handles_http_errors(self, mock_client_class):
        """Test that run() handles HTTP errors gracefully."""
        import httpx

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # All requests fail
        mock_client.get.side_effect = httpx.HTTPError("Connection failed")

        connector = CareerOneStopConnector(api_key="test")
        # Should not raise, just return empty list
        resources = connector.run()
        assert isinstance(resources, list)
        assert len(resources) == 0

    @patch("connectors.careeronestop.httpx.Client")
    def test_run_handles_empty_response(self, mock_client_class):
        """Test that run() handles empty API responses."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {"OneStopCenterList": []}
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = CareerOneStopConnector(api_key="test")
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 0

    @patch("connectors.careeronestop.httpx.Client")
    def test_run_handles_missing_list(self, mock_client_class):
        """Test that run() handles response without OneStopCenterList."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.json.return_value = {}  # No OneStopCenterList key
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = CareerOneStopConnector(api_key="test")
        resources = connector.run()

        assert isinstance(resources, list)
        assert len(resources) == 0

    def test_eligibility_mentions_veteran_priority(self):
        """Test that eligibility mentions veteran priority of service."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "City": "Austin",
            "StateName": "TX",
        }

        candidate = connector._parse_center(center)

        assert candidate is not None
        assert "veteran" in candidate.eligibility.lower()
        assert "priority" in candidate.eligibility.lower()

    def test_categories_include_employment_and_training(self):
        """Test that all centers are categorized as employment and training."""
        connector = CareerOneStopConnector(api_key="test")

        center = {
            "Name": "Test Center",
            "City": "Austin",
            "StateName": "TX",
        }

        candidate = connector._parse_center(center)

        assert candidate is not None
        assert candidate.categories == ["employment", "training"]
