"""Tests for GI Bill Schools (WEAMS) connector."""

from connectors.gi_bill_schools import GIBillSchoolsConnector


class TestGIBillSchoolsConnector:
    """Tests for GIBillSchoolsConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = GIBillSchoolsConnector()
        meta = connector.metadata

        assert meta.name == "VA GI Bill Comparison Tool (WEAMS)"
        assert meta.tier == 1  # Official VA source
        assert meta.requires_auth is False
        assert "va.gov" in meta.url

    def test_parse_institution_basic(self):
        """Test parsing a basic institution."""
        connector = GIBillSchoolsConnector()

        # Sample institution data structure from VA API
        institution = {
            "id": "12345",
            "attributes": {
                "facility_code": "21004113",
                "name": "University of Veterans Test",
                "type": "school",
                "city": "Arlington",
                "state": "VA",
                "zip": "22201",
                "address_1": "123 Main Street",
                "phone": "703-555-1234",
                "accredited": True,
                "accreditation_type": "regional",
                "highest_degree": "Bachelor",
                "yellow_ribbon": True,
                "student_veteran": 500,
                "student_veteran_group": True,
                "caution_flags": [],
                "website": "https://example.edu",
            },
        }

        candidate = connector._parse_institution(institution)

        assert candidate is not None
        assert candidate.title == "University of Veterans Test - GI Bill Approved"
        assert candidate.org_name == "University of Veterans Test"
        assert candidate.state == "VA"
        assert candidate.city == "Arlington"
        assert candidate.zip_code == "22201"
        assert "training" in candidate.categories
        assert "gi-bill" in candidate.tags
        assert "yellow-ribbon" in candidate.tags
        assert "accredited" in candidate.tags
        assert candidate.scope == "local"

    def test_parse_institution_ojt(self):
        """Test parsing an OJT program."""
        connector = GIBillSchoolsConnector()

        institution = {
            "id": "67890",
            "attributes": {
                "facility_code": "21004114",
                "name": "Veterans Construction Training",
                "type": "employer",
                "city": "Richmond",
                "state": "VA",
                "zip": "23220",
                "address_1": "456 Work Ave",
                "ojt_indicator": True,
                "accredited": False,
            },
        }

        candidate = connector._parse_institution(institution)

        assert candidate is not None
        assert "ojt" in candidate.tags
        assert "apprenticeship" in candidate.tags
        assert "OJT" in candidate.description or "On-the-job" in candidate.description

    def test_parse_institution_correspondence(self):
        """Test parsing a correspondence/distance learning program."""
        connector = GIBillSchoolsConnector()

        institution = {
            "id": "99999",
            "attributes": {
                "facility_code": "21004115",
                "name": "Online Veterans University",
                "type": "school",
                "city": "Phoenix",
                "state": "AZ",
                "zip": "85001",
                "address_1": "789 Digital Blvd",
                "correspondence_indicator": True,
                "accredited": True,
            },
        }

        candidate = connector._parse_institution(institution)

        assert candidate is not None
        assert candidate.scope == "national"  # Correspondence is national scope
        assert "correspondence" in candidate.tags or "distance-learning" in candidate.tags

    def test_parse_institution_with_caution_flags(self):
        """Test parsing institution with caution flags."""
        connector = GIBillSchoolsConnector()

        institution = {
            "id": "11111",
            "attributes": {
                "facility_code": "21004116",
                "name": "Caution College",
                "type": "school",
                "city": "Test City",
                "state": "CA",
                "zip": "90001",
                "address_1": "100 Warning Lane",
                "caution_flags": [
                    {"reason": "Under investigation"},
                    {"reason": "Accreditation issue"},
                ],
            },
        }

        candidate = connector._parse_institution(institution)

        assert candidate is not None
        assert "caution flags" in candidate.description.lower()
        assert "caution-flag" in candidate.tags

    def test_parse_institution_missing_name(self):
        """Test that institution without name returns None."""
        connector = GIBillSchoolsConnector()

        institution = {
            "id": "22222",
            "attributes": {
                "facility_code": "21004117",
                "city": "Unknown",
                "state": "TX",
            },
        }

        candidate = connector._parse_institution(institution)
        assert candidate is None

    def test_build_description_with_all_features(self):
        """Test description building with all features."""
        connector = GIBillSchoolsConnector()

        attrs = {
            "type": "school",
            "highest_degree": "Doctorate",
            "accredited": True,
            "accreditation_type": "Regional",
            "yellow_ribbon": True,
            "student_veteran": 1500,
            "student_veteran_group": True,
            "caution_flags": [{"reason": "Test"}],
        }

        description = connector._build_description(attrs)

        assert "Doctorate" in description
        assert "accredited" in description.lower()
        assert "Yellow Ribbon" in description
        assert "1,500" in description  # Student count formatted with comma
        assert "veteran" in description.lower()
        assert "caution" in description.lower()

    def test_extract_tags_degree_levels(self):
        """Test that degree level tags are properly extracted."""
        connector = GIBillSchoolsConnector()

        # Test doctorate
        attrs = {"highest_degree": "Doctorate"}
        tags = connector._extract_tags(attrs, False, False, False)
        assert "doctorate" in tags

        # Test bachelor
        attrs = {"highest_degree": "Bachelor"}
        tags = connector._extract_tags(attrs, False, False, False)
        assert "bachelors" in tags

        # Test associate
        attrs = {"highest_degree": "Associate"}
        tags = connector._extract_tags(attrs, False, False, False)
        assert "associates" in tags

    def test_get_approved_programs(self):
        """Test extracting approved program types."""
        connector = GIBillSchoolsConnector()

        # School with degree programs
        attrs = {
            "highest_degree": "Master",
            "ojt_indicator": False,
            "flight_indicator": False,
            "correspondence_indicator": False,
        }
        programs = connector._get_approved_programs(attrs)
        assert any("Degree" in p for p in programs)

        # OJT program
        attrs = {"ojt_indicator": True}
        programs = connector._get_approved_programs(attrs)
        assert any("OJT" in p for p in programs)

        # Flight school
        attrs = {"flight_indicator": True}
        programs = connector._get_approved_programs(attrs)
        assert any("Flight" in p for p in programs)

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with GIBillSchoolsConnector() as connector:
            assert connector is not None
            assert connector.metadata.name == "VA GI Bill Comparison Tool (WEAMS)"

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = GIBillSchoolsConnector()

        assert connector._normalize_phone("7035551234") == "(703) 555-1234"
        assert connector._normalize_phone("1-703-555-1234") == "(703) 555-1234"
        assert connector._normalize_phone(None) is None

    def test_state_normalization(self):
        """Test state code normalization."""
        connector = GIBillSchoolsConnector()

        assert connector._normalize_state("VA") == "VA"
        assert connector._normalize_state("va") == "VA"
        assert connector._normalize_state("Virginia") == "VI"  # First 2 chars
        assert connector._normalize_state(None) is None
