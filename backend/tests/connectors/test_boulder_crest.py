"""Tests for Boulder Crest Foundation PATHH program connector."""


from connectors.boulder_crest import (
    BOULDER_CREST_LOCATIONS,
    BoulderCrestConnector,
)


class TestBoulderCrestConnector:
    """Tests for BoulderCrestConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = BoulderCrestConnector()
        meta = connector.metadata

        assert meta.name == "Boulder Crest Foundation"
        assert "bouldercrest.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_both_locations(self):
        """Test that run() returns both VA and AZ locations."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        assert len(resources) == 2
        assert len(resources) == len(BOULDER_CREST_LOCATIONS)

    def test_run_all_have_mental_health_category(self):
        """Test that all locations have mentalHealth category."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "mentalHealth" in resource.categories

    def test_run_all_have_local_scope(self):
        """Test that all locations have local scope."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_run_all_have_address_info(self):
        """Test that all locations have complete address information."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert resource.zip_code is not None
            assert len(resource.state) == 2

    def test_run_all_have_phone(self):
        """Test that all locations have normalized phone numbers."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            # Phone should be normalized to (XXX) XXX-XXXX format
            assert "(" in resource.phone
            assert ")" in resource.phone
            assert "-" in resource.phone

    def test_run_all_have_states_served(self):
        """Test that all locations have states list."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert len(resource.states) >= 1

    def test_run_virginia_location(self):
        """Test Virginia location details."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        va_location = None
        for r in resources:
            if r.state == "VA":
                va_location = r
                break

        assert va_location is not None
        assert "Virginia" in va_location.title
        assert va_location.city == "Bluemont"
        assert va_location.zip_code == "20135"
        assert "VA" in va_location.states

    def test_run_arizona_location(self):
        """Test Arizona location details."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        az_location = None
        for r in resources:
            if r.state == "AZ":
                az_location = r
                break

        assert az_location is not None
        assert "Arizona" in az_location.title
        assert az_location.city == "Sonoita"
        assert az_location.zip_code == "85637"
        assert "AZ" in az_location.states

    def test_run_title_format(self):
        """Test location title format."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "Boulder Crest" in resource.title
            assert "Warrior PATHH" in resource.title
            assert "Free PTSD Treatment" in resource.title

    def test_run_description_mentions_pathh(self):
        """Test description includes PATHH program details."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention PATHH
            assert "pathh" in resource.description.lower()
            # Should mention posttraumatic growth
            assert "posttraumatic growth" in resource.description.lower()
            # Should mention free services
            assert "free" in resource.description.lower()
            # Should mention 90-day program
            assert "90" in resource.description

    def test_run_eligibility_mentions_combat_veterans(self):
        """Test eligibility mentions combat veterans."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "combat veteran" in resource.eligibility.lower()

    def test_run_eligibility_mentions_first_responders(self):
        """Test eligibility mentions first responders."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "first responder" in resource.eligibility.lower()

    def test_run_eligibility_mentions_free(self):
        """Test eligibility mentions free services."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "free" in resource.eligibility.lower()

    def test_run_how_to_apply(self):
        """Test how to apply information."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            # Should include a phone number
            assert "Call" in resource.how_to_apply
            assert any(c.isdigit() for c in resource.how_to_apply)
            # Should mention website
            assert "bouldercrest.org" in resource.how_to_apply

    def test_run_tags(self):
        """Test location tags."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        expected_tags = [
            "mental-health",
            "free-services",
            "ptsd",
            "ptsd-treatment",
            "posttraumatic-growth",
            "trauma-recovery",
            "residential-program",
            "combat-veterans",
            "first-responders",
            "warrior-pathh",
            "boulder-crest",
        ]

        for resource in resources:
            for tag in expected_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_state_tags(self):
        """Test that state tags are added."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            # Should have at least one state tag
            state_tags = [t for t in resource.tags if t.startswith("state-")]
            assert len(state_tags) >= 1

            # State tags should match states served
            for state in resource.states:
                assert f"state-{state.lower()}" in resource.tags

    def test_run_org_info(self):
        """Test organization information."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Boulder Crest Foundation"
            assert resource.org_website == "https://bouldercrest.org/"
            assert resource.source_url == "https://bouldercrest.org/"

    def test_run_raw_data(self):
        """Test raw data includes program information."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert "location_name" in resource.raw_data
            assert "serves_states" in resource.raw_data
            assert "national_phone" in resource.raw_data
            assert "program" in resource.raw_data
            assert resource.raw_data["program"] == "Warrior PATHH"

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with BoulderCrestConnector() as connector:
            resources = connector.run()
            assert len(resources) == 2

    def test_state_code_to_name(self):
        """Test state code to name conversion."""
        connector = BoulderCrestConnector()

        assert connector._state_code_to_name("VA") == "Virginia"
        assert connector._state_code_to_name("AZ") == "Arizona"
        assert connector._state_code_to_name("DC") == "District of Columbia"
        assert connector._state_code_to_name("XX") == "XX"  # Unknown returns as-is

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = BoulderCrestConnector()

        assert connector._normalize_phone("5405542727") == "(540) 554-2727"
        assert connector._normalize_phone("1-540-554-2727") == "(540) 554-2727"
        assert connector._normalize_phone("(540) 554-2727") == "(540) 554-2727"

    def test_both_states_covered(self):
        """Test that both VA and AZ locations are present."""
        connector = BoulderCrestConnector()
        resources = connector.run()

        states = {r.state for r in resources}
        assert "VA" in states
        assert "AZ" in states
