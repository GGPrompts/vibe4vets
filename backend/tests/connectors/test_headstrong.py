"""Tests for The Headstrong Project PTSD treatment connector."""


from connectors.headstrong import (
    ALL_US_STATES,
    HEADSTRONG_IN_PERSON_STATES,
    HeadstrongConnector,
)


class TestHeadstrongConnector:
    """Tests for HeadstrongConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = HeadstrongConnector()
        meta = connector.metadata

        assert meta.name == "The Headstrong Project"
        assert "theheadstrongproject.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_expected_resource_count(self):
        """Test that run() returns 1 national + 15 state resources."""
        connector = HeadstrongConnector()
        resources = connector.run()

        # 1 national telehealth + 15 in-person states
        expected_count = 1 + len(HEADSTRONG_IN_PERSON_STATES)
        assert len(resources) == expected_count
        assert len(resources) == 16

    def test_run_all_have_mental_health_category(self):
        """Test that all resources have mentalHealth category."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            assert "mentalHealth" in resource.categories

    def test_run_national_telehealth_resource(self):
        """Test the national telehealth resource."""
        connector = HeadstrongConnector()
        resources = connector.run()

        # First resource should be the national telehealth one
        telehealth = resources[0]

        assert "Nationwide Telehealth" in telehealth.title
        assert telehealth.scope == "national"
        assert telehealth.states == ALL_US_STATES
        assert len(telehealth.states) == 51  # 50 states + DC

    def test_run_state_resources_have_correct_scope(self):
        """Test that state resources have state scope."""
        connector = HeadstrongConnector()
        resources = connector.run()

        # Skip the first telehealth resource
        state_resources = resources[1:]

        for resource in state_resources:
            assert resource.scope == "state"
            assert len(resource.states) == 1

    def test_run_covers_expected_states(self):
        """Test that in-person resources cover expected states."""
        connector = HeadstrongConnector()
        resources = connector.run()

        # Get state codes from state resources
        state_resources = [r for r in resources if r.scope == "state"]
        covered_states = [r.states[0] for r in state_resources]

        # Should cover all expected in-person states
        assert set(covered_states) == set(HEADSTRONG_IN_PERSON_STATES)

        # Verify specific states from research
        expected_states = ["AZ", "CA", "CO", "DC", "FL", "GA", "ID", "IL",
                          "MD", "NJ", "NY", "NC", "OR", "PA", "TX"]
        for state in expected_states:
            assert state in covered_states

    def test_run_resource_title_format(self):
        """Test resource title format."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            assert "Headstrong Project" in resource.title
            assert "Free PTSD Treatment" in resource.title

    def test_run_resource_description_content(self):
        """Test resource description content."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            desc = resource.description.lower()
            # Should mention free services
            assert "free" in desc
            # Should mention 30 sessions
            assert "30" in desc
            # Should mention evidence-based therapies
            assert "cpt" in desc or "cognitive processing" in desc
            # Should mention Veterans
            assert "veteran" in desc

    def test_run_resource_eligibility(self):
        """Test eligibility information."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            elig = resource.eligibility.lower()
            # Should mention all eras
            assert "all eras" in elig
            # Should mention any discharge status
            assert "any discharge" in elig or "other-than-honorable" in elig
            # Should mention no VA enrollment required
            assert "no va enrollment" in elig
            # Should mention family members
            assert "family" in elig

    def test_run_resource_how_to_apply(self):
        """Test how to apply information."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            apply = resource.how_to_apply.lower()
            # Should mention website
            assert "theheadstrongproject.org" in apply
            # Should mention 2 business days
            assert "2 business days" in apply
            # Should mention 2 weeks
            assert "2 weeks" in apply

    def test_run_resource_tags(self):
        """Test resource tags include expected values."""
        connector = HeadstrongConnector()
        resources = connector.run()

        expected_tags = [
            "headstrong",
            "ptsd",
            "free-therapy",
            "cpt",
            "emdr",
            "telehealth",
            "mental-health",
            "free-services",
            "all-eras",
            "any-discharge",
            "family-support",
        ]

        for resource in resources:
            for tag in expected_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_telehealth_has_nationwide_tag(self):
        """Test that telehealth resource has nationwide tag."""
        connector = HeadstrongConnector()
        resources = connector.run()

        telehealth = resources[0]
        assert "nationwide" in telehealth.tags

    def test_run_state_resources_have_in_person_tag(self):
        """Test that state resources have in-person tag."""
        connector = HeadstrongConnector()
        resources = connector.run()

        state_resources = resources[1:]
        for resource in state_resources:
            assert "in-person" in resource.tags

    def test_run_state_resources_have_state_tags(self):
        """Test that state resources have state-specific tags."""
        connector = HeadstrongConnector()
        resources = connector.run()

        state_resources = resources[1:]
        for resource in state_resources:
            state = resource.states[0]
            expected_tag = f"state-{state.lower()}"
            assert expected_tag in resource.tags

    def test_run_org_info(self):
        """Test organization information."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "The Headstrong Project"
            assert resource.org_website == "https://theheadstrongproject.org/"
            assert resource.source_url == "https://theheadstrongproject.org/get-help/"

    def test_run_raw_data_telehealth(self):
        """Test raw data for telehealth resource."""
        connector = HeadstrongConnector()
        resources = connector.run()

        telehealth = resources[0]
        raw = telehealth.raw_data

        assert raw["service_type"] == "telehealth"
        assert raw["sessions_offered"] == 30
        assert raw["cost"] == "free"
        assert "CPT" in str(raw["treatment_modalities"])
        assert "EMDR" in str(raw["treatment_modalities"])
        assert raw["response_time"] == "2 business days"
        assert raw["first_session"] == "within 2 weeks"

    def test_run_raw_data_state(self):
        """Test raw data for state resources."""
        connector = HeadstrongConnector()
        resources = connector.run()

        state_resource = resources[1]
        raw = state_resource.raw_data

        assert raw["service_type"] == "in-person"
        assert raw["telehealth_available"] is True
        assert raw["sessions_offered"] == 30
        assert raw["cost"] == "free"

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = HeadstrongConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with HeadstrongConnector() as connector:
            resources = connector.run()
            assert len(resources) == 16

    def test_state_code_to_name(self):
        """Test state code to name conversion."""
        connector = HeadstrongConnector()

        assert connector._state_code_to_name("CA") == "California"
        assert connector._state_code_to_name("TX") == "Texas"
        assert connector._state_code_to_name("DC") == "District of Columbia"
        assert connector._state_code_to_name("NY") == "New York"
        assert connector._state_code_to_name("XX") == "XX"  # Unknown returns as-is

    def test_in_person_states_list(self):
        """Test the in-person states list matches documentation."""
        # From research: AZ, CA, CO, FL, GA, ID, IL, MD, NJ, NY, NC, OR, PA, TX, DC
        expected = {
            "AZ", "CA", "CO", "DC", "FL", "GA", "ID", "IL",
            "MD", "NJ", "NY", "NC", "OR", "PA", "TX"
        }
        assert set(HEADSTRONG_IN_PERSON_STATES) == expected
        assert len(HEADSTRONG_IN_PERSON_STATES) == 15

    def test_all_us_states_list(self):
        """Test the all US states list is complete."""
        assert len(ALL_US_STATES) == 51  # 50 states + DC
        assert "DC" in ALL_US_STATES
        assert "CA" in ALL_US_STATES
        assert "NY" in ALL_US_STATES
        assert "TX" in ALL_US_STATES

    def test_treatment_modalities_documented(self):
        """Test that treatment modalities are properly documented."""
        connector = HeadstrongConnector()

        modalities = connector.TREATMENT_MODALITIES
        assert "CPT" in str(modalities) or "Cognitive Processing" in str(modalities)
        assert "EMDR" in str(modalities)
        assert "Prolonged Exposure" in str(modalities)

    def test_state_title_includes_state_name(self):
        """Test that state resource titles include the state name."""
        connector = HeadstrongConnector()
        resources = connector.run()

        # Check California resource
        ca_resources = [r for r in resources if r.states == ["CA"]]
        assert len(ca_resources) == 1
        assert "California" in ca_resources[0].title

        # Check Texas resource
        tx_resources = [r for r in resources if r.states == ["TX"]]
        assert len(tx_resources) == 1
        assert "Texas" in tx_resources[0].title

        # Check DC resource
        dc_resources = [r for r in resources if r.states == ["DC"]]
        assert len(dc_resources) == 1
        assert "District of Columbia" in dc_resources[0].title
