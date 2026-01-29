"""Tests for the SVA Chapters connector."""

from unittest.mock import MagicMock, patch

from connectors.sva_chapters import SVAChaptersConnector, get_state_from_coords


class TestSVAChaptersConnector:
    """Test suite for SVAChaptersConnector."""

    def test_metadata(self):
        """Test connector metadata is correct."""
        connector = SVAChaptersConnector()
        metadata = connector.metadata

        assert metadata.name == "Student Veterans of America Chapters"
        assert metadata.tier == 2
        assert metadata.frequency == "monthly"
        assert metadata.requires_auth is False
        assert "studentveterans.org" in metadata.url

    def test_parse_chapter_basic(self):
        """Test parsing a basic chapter marker."""
        connector = SVAChaptersConnector()

        marker = {
            "id": "123",
            "map_id": "1",
            "title": "University of Texas at Austin",
            "description": "Longhorn Veterans",
            "lat": "30.2849",
            "lng": "-97.7341",
            "link": "https://example.com/longhorn-vets",
            "approved": "1",
        }

        result = connector._parse_chapter(marker)

        assert result is not None
        assert result.title == "SVA Chapter at University of Texas at Austin"
        assert result.state == "TX"
        assert result.categories == ["education"]
        assert "sva" in result.tags
        assert "student-veterans" in result.tags
        assert "peer-support" in result.tags
        assert "education" in result.tags
        assert result.scope == "local"
        assert result.org_name == "Student Veterans of America"

    def test_parse_chapter_without_link(self):
        """Test parsing a chapter without a website link."""
        connector = SVAChaptersConnector()

        marker = {
            "id": "456",
            "map_id": "1",
            "title": "Springfield College",
            "description": "Student Veterans of America",
            "lat": "42.1",
            "lng": "-72.5",
            "link": "",
            "approved": "1",
        }

        result = connector._parse_chapter(marker)

        assert result is not None
        assert result.source_url == connector.DIRECTORY_URL

    def test_parse_chapter_unapproved(self):
        """Test that unapproved markers are skipped in run()."""
        connector = SVAChaptersConnector()

        # Unapproved marker should still parse (run() filters them)
        marker = {
            "id": "789",
            "map_id": "1",
            "title": "Test College",
            "description": "Test Chapter",
            "lat": "40.0",
            "lng": "-74.0",
            "link": "",
            "approved": "0",
        }

        # The parse function doesn't check approved status
        result = connector._parse_chapter(marker)
        assert result is not None

    def test_parse_chapter_missing_title(self):
        """Test that markers without titles return None."""
        connector = SVAChaptersConnector()

        marker = {
            "id": "999",
            "title": "",
            "lat": "40.0",
            "lng": "-74.0",
            "approved": "1",
        }

        result = connector._parse_chapter(marker)
        assert result is None

    def test_build_description(self):
        """Test description building."""
        connector = SVAChaptersConnector()

        description = connector._build_description(
            school_name="State University",
            chapter_name="Veterans Alliance",
        )

        assert "Veterans Alliance" in description
        assert "State University" in description
        assert "peer support" in description.lower()
        assert "scholarships" in description.lower()

    def test_build_description_generic_chapter(self):
        """Test description when chapter name is generic."""
        connector = SVAChaptersConnector()

        description = connector._build_description(
            school_name="Community College",
            chapter_name="Student Veterans of America",
        )

        assert "Student Veterans of America chapter at Community College" in description

    def test_build_eligibility(self):
        """Test eligibility text includes key groups."""
        connector = SVAChaptersConnector()

        eligibility = connector._build_eligibility()

        # Veterans
        assert "veteran" in eligibility.lower()
        # Active duty
        assert "active duty" in eligibility.lower()
        # Guard/Reserve
        assert "guard" in eligibility.lower() or "reserve" in eligibility.lower()
        # Spouses
        assert "spouse" in eligibility.lower()
        # Supporters
        assert "supporter" in eligibility.lower()

    def test_build_how_to_apply_with_link(self):
        """Test application instructions with website link."""
        connector = SVAChaptersConnector()

        instructions = connector._build_how_to_apply(
            school_name="Test University",
            link="https://example.com/sva",
        )

        assert "Test University" in instructions
        assert "https://example.com/sva" in instructions
        assert "studentveterans.org" in instructions.lower()

    def test_build_how_to_apply_without_link(self):
        """Test application instructions without website link."""
        connector = SVAChaptersConnector()

        instructions = connector._build_how_to_apply(
            school_name="Test College",
            link="",
        )

        assert "Test College" in instructions
        assert "student organization directory" in instructions.lower()

    def test_build_tags_university(self):
        """Test tags for university chapter."""
        connector = SVAChaptersConnector()

        tags = connector._build_tags(
            school_name="State University",
            chapter_name="Veteran Club",
        )

        assert "sva" in tags
        assert "student-veterans" in tags
        assert "education" in tags
        assert "university" in tags
        assert "public-university" in tags

    def test_build_tags_community_college(self):
        """Test tags for community college chapter."""
        connector = SVAChaptersConnector()

        tags = connector._build_tags(
            school_name="City Community College",
            chapter_name="Vets Club",
        )

        assert "community-college" in tags
        assert "college" in tags

    def test_build_tags_technical_school(self):
        """Test tags for technical school chapter."""
        connector = SVAChaptersConnector()

        tags = connector._build_tags(
            school_name="Regional Technical Institute",
            chapter_name="Vets",
        )

        assert "technical-school" in tags

    def test_context_manager(self):
        """Test connector works as context manager."""
        with SVAChaptersConnector() as connector:
            assert connector is not None
            metadata = connector.metadata
            assert metadata.name is not None

    @patch("connectors.sva_chapters.httpx.Client")
    def test_run_with_mocked_api(self, mock_client_class):
        """Test the run method with mocked API response."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": "1",
                "map_id": "1",
                "title": "Test University",
                "description": "Test SVA Chapter",
                "lat": "39.7",
                "lng": "-104.9",
                "link": "https://example.com",
                "approved": "1",
            },
            {
                "id": "2",
                "map_id": "1",
                "title": "Test College",
                "description": "Another Chapter",
                "lat": "34.0",
                "lng": "-118.2",
                "link": "",
                "approved": "1",
            },
            {
                "id": "3",
                "map_id": "1",
                "title": "Unapproved School",
                "description": "Pending",
                "lat": "40.0",
                "lng": "-74.0",
                "link": "",
                "approved": "0",  # Should be filtered out
            },
        ]
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = SVAChaptersConnector()
        resources = connector.run()

        # Only 2 approved chapters should be returned
        assert len(resources) == 2
        assert "Test University" in resources[0].title
        assert resources[0].state == "CO"
        assert resources[1].state == "CA"

    @patch("connectors.sva_chapters.httpx.Client")
    def test_run_handles_nested_response(self, mock_client_class):
        """Test the run method handles nested API response format."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Some APIs return markers in a nested object
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "markers": [
                {
                    "id": "1",
                    "title": "Nested Test",
                    "lat": "42.0",
                    "lng": "-71.0",
                    "approved": "1",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response

        connector = SVAChaptersConnector()
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].state == "MA"

    @patch("connectors.sva_chapters.httpx.Client")
    def test_run_handles_http_error(self, mock_client_class):
        """Test the run method handles HTTP errors gracefully."""
        import httpx

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get.side_effect = httpx.HTTPError("Connection failed")

        connector = SVAChaptersConnector()
        resources = connector.run()

        # Should return empty list on error
        assert resources == []


class TestGetStateFromCoords:
    """Test suite for state detection from coordinates."""

    def test_texas(self):
        """Test Texas coordinates."""
        # Austin, TX
        assert get_state_from_coords(30.2672, -97.7431) == "TX"

    def test_california(self):
        """Test California coordinates."""
        # Los Angeles, CA
        assert get_state_from_coords(34.0522, -118.2437) == "CA"

    def test_new_york(self):
        """Test New York coordinates."""
        # Albany, NY (state capital - more clearly in NY)
        assert get_state_from_coords(42.6526, -73.7562) == "NY"

    def test_florida(self):
        """Test Florida coordinates."""
        # Miami, FL
        assert get_state_from_coords(25.7617, -80.1918) == "FL"

    def test_washington_dc(self):
        """Test DC coordinates."""
        # Washington, DC
        assert get_state_from_coords(38.9072, -77.0369) == "DC"

    def test_hawaii(self):
        """Test Hawaii coordinates."""
        # Honolulu, HI
        assert get_state_from_coords(21.3069, -157.8583) == "HI"

    def test_alaska(self):
        """Test Alaska coordinates."""
        # Anchorage, AK
        assert get_state_from_coords(61.2181, -149.9003) == "AK"

    def test_puerto_rico(self):
        """Test Puerto Rico coordinates."""
        # San Juan, PR
        assert get_state_from_coords(18.4655, -66.1057) == "PR"

    def test_invalid_coords(self):
        """Test coordinates outside US."""
        # London, UK
        assert get_state_from_coords(51.5074, -0.1278) is None

        # Pacific Ocean
        assert get_state_from_coords(0.0, -150.0) is None

    def test_zero_coords(self):
        """Test zero coordinates."""
        assert get_state_from_coords(0.0, 0.0) is None
