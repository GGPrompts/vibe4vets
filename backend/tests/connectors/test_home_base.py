"""Tests for Home Base veteran mental health program connector."""

from connectors.home_base import (
    HOME_BASE_LOCATIONS,
    HomeBaseConnector,
)


class TestHomeBaseConnector:
    """Tests for HomeBaseConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = HomeBaseConnector()
        meta = connector.metadata

        assert meta.name == "Home Base"
        assert "homebase.org" in meta.url
        assert meta.tier == 2  # Established nonprofit/hospital partnership
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_all_locations(self):
        """Test that run() returns all locations."""
        connector = HomeBaseConnector()
        resources = connector.run()

        assert len(resources) == 3
        assert len(resources) == len(HOME_BASE_LOCATIONS)

    def test_run_all_have_mental_health_category(self):
        """Test that all locations have mentalHealth category."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "mentalHealth" in resource.categories

    def test_run_all_have_local_scope(self):
        """Test that all locations have local scope."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_run_all_have_address_info(self):
        """Test that all locations have complete address information."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert resource.zip_code is not None
            assert len(resource.state) == 2

    def test_run_all_have_phone(self):
        """Test that all locations have normalized phone numbers."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            # Phone should be normalized to (XXX) XXX-XXXX format
            assert "(" in resource.phone
            assert ")" in resource.phone
            assert "-" in resource.phone

    def test_run_all_have_email(self):
        """Test that all locations have email addresses."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.email is not None
            assert "@" in resource.email

    def test_run_all_have_states_served(self):
        """Test that all locations have states list."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert len(resource.states) >= 1

    def test_run_massachusetts_headquarters(self):
        """Test Massachusetts headquarters location details."""
        connector = HomeBaseConnector()
        resources = connector.run()

        ma_location = None
        for r in resources:
            if r.state == "MA":
                ma_location = r
                break

        assert ma_location is not None
        assert "National Center" in ma_location.title
        assert ma_location.city == "Charlestown"
        assert ma_location.zip_code == "02129"
        assert "MA" in ma_location.states
        # Should serve New England states
        assert len(ma_location.states) >= 6
        assert "headquarters" in ma_location.tags

    def test_run_florida_location(self):
        """Test Florida location details."""
        connector = HomeBaseConnector()
        resources = connector.run()

        fl_location = None
        for r in resources:
            if r.state == "FL":
                fl_location = r
                break

        assert fl_location is not None
        assert "Florida" in fl_location.title
        assert fl_location.city == "Fort Myers"
        assert "FL" in fl_location.states

    def test_run_arizona_location(self):
        """Test Arizona location details."""
        connector = HomeBaseConnector()
        resources = connector.run()

        az_location = None
        for r in resources:
            if r.state == "AZ":
                az_location = r
                break

        assert az_location is not None
        assert "Arizona" in az_location.title
        assert az_location.city == "Phoenix"
        assert "AZ" in az_location.states

    def test_run_title_format(self):
        """Test location title format."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "Home Base" in resource.title
            assert "Free Veteran Mental Health Care" in resource.title

    def test_run_description_mentions_mgh_partnership(self):
        """Test description mentions MGH and Red Sox Foundation partnership."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "massachusetts general" in resource.description.lower()
            assert "red sox foundation" in resource.description.lower()

    def test_run_description_mentions_intensive_program(self):
        """Test description mentions 2-week intensive program."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention intensive program
            assert "intensive" in resource.description.lower()
            # Should mention 2-week duration
            assert "2-week" in resource.description.lower()

    def test_run_description_mentions_post_911(self):
        """Test description mentions post-9/11 eligibility."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "post-9/11" in resource.description.lower()

    def test_run_description_mentions_free(self):
        """Test description mentions free services."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "no out-of-pocket cost" in resource.description.lower()

    def test_run_eligibility_mentions_post_911(self):
        """Test eligibility mentions post-9/11 veterans."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "post-9/11" in resource.eligibility.lower()

    def test_run_eligibility_mentions_no_va_enrollment(self):
        """Test eligibility mentions no VA enrollment required."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "no va enrollment" in resource.eligibility.lower()

    def test_run_eligibility_mentions_families(self):
        """Test eligibility mentions family members."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "family" in resource.eligibility.lower()

    def test_run_eligibility_mentions_free(self):
        """Test eligibility mentions free services."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "no out-of-pocket cost" in resource.eligibility.lower()

    def test_run_how_to_apply(self):
        """Test how to apply information."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            # Should include a phone number
            assert "Call" in resource.how_to_apply
            assert any(c.isdigit() for c in resource.how_to_apply)
            # Should mention email
            assert "email" in resource.how_to_apply.lower()
            # Should mention website
            assert "homebase.org" in resource.how_to_apply
            # Should mention crisis line
            assert "988" in resource.how_to_apply

    def test_run_tags(self):
        """Test location tags."""
        connector = HomeBaseConnector()
        resources = connector.run()

        expected_tags = [
            "mental-health",
            "free-services",
            "post-9/11",
            "ptsd",
            "tbi",
            "family-support",
            "no-va-enrollment",
            "home-base",
            "mass-general",
            "red-sox-foundation",
            "intensive-program",
            "warrior-care-network",
        ]

        for resource in resources:
            for tag in expected_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_state_tags(self):
        """Test that state tags are added."""
        connector = HomeBaseConnector()
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
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Home Base (MGH/Red Sox Foundation)"
            assert resource.org_website == "https://homebase.org/"
            assert resource.source_url == "https://homebase.org/"

    def test_run_raw_data(self):
        """Test raw data includes program information."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert "location_name" in resource.raw_data
            assert "serves_states" in resource.raw_data
            assert "national_phone" in resource.raw_data
            assert "email" in resource.raw_data
            assert "is_headquarters" in resource.raw_data
            assert "programs" in resource.raw_data
            assert len(resource.raw_data["programs"]) >= 6

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = HomeBaseConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with HomeBaseConnector() as connector:
            resources = connector.run()
            assert len(resources) == 3

    def test_state_code_to_name(self):
        """Test state code to name conversion."""
        connector = HomeBaseConnector()

        assert connector._state_code_to_name("MA") == "Massachusetts"
        assert connector._state_code_to_name("FL") == "Florida"
        assert connector._state_code_to_name("AZ") == "Arizona"
        assert connector._state_code_to_name("XX") == "XX"  # Unknown returns as-is

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = HomeBaseConnector()

        assert connector._normalize_phone("6177245202") == "(617) 724-5202"
        assert connector._normalize_phone("1-617-724-5202") == "(617) 724-5202"
        assert connector._normalize_phone("(617) 724-5202") == "(617) 724-5202"

    def test_all_states_covered(self):
        """Test that MA, FL, and AZ locations are present."""
        connector = HomeBaseConnector()
        resources = connector.run()

        states = {r.state for r in resources}
        assert "MA" in states
        assert "FL" in states
        assert "AZ" in states

    def test_new_england_coverage(self):
        """Test that Massachusetts location covers New England."""
        connector = HomeBaseConnector()
        resources = connector.run()

        ma_location = None
        for r in resources:
            if r.state == "MA":
                ma_location = r
                break

        assert ma_location is not None
        # Should serve all New England states
        new_england = {"MA", "ME", "NH", "VT", "RI", "CT"}
        served_states = set(ma_location.states)
        assert new_england.issubset(served_states)
