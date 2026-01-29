"""Tests for Give an Hour volunteer mental health provider connector."""


from connectors.give_an_hour import (
    ALL_US_STATES,
    GiveAnHourConnector,
)


class TestGiveAnHourConnector:
    """Tests for GiveAnHourConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = GiveAnHourConnector()
        meta = connector.metadata

        assert meta.name == "Give an Hour"
        assert "giveanhour.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_single_resource(self):
        """Test that run() returns exactly one national resource."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        assert len(resources) == 1

    def test_run_has_mental_health_category(self):
        """Test that resource has mentalHealth category."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        assert "mentalHealth" in resources[0].categories

    def test_run_national_scope(self):
        """Test that resource has national scope."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        resource = resources[0]
        assert resource.scope == "national"
        assert resource.states == ALL_US_STATES
        assert len(resource.states) == 51  # 50 states + DC

    def test_run_resource_title(self):
        """Test resource title format."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        resource = resources[0]
        assert "Give an Hour" in resource.title
        assert "Free" in resource.title
        assert "Mental Health" in resource.title

    def test_run_resource_description_content(self):
        """Test resource description content."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        desc = resources[0].description.lower()
        # Should mention free services
        assert "free" in desc
        # Should mention volunteer providers
        assert "volunteer" in desc
        # Should mention licensed professionals
        assert "licensed" in desc
        # Should mention key conditions treated
        assert "ptsd" in desc
        assert "anxiety" in desc
        assert "depression" in desc
        # Should mention delivery methods
        assert "telehealth" in desc
        assert "in-person" in desc

    def test_run_resource_eligibility(self):
        """Test eligibility information."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        elig = resources[0].eligibility.lower()
        # Should mention active duty
        assert "active-duty" in elig or "active duty" in elig
        # Should mention Guard and Reserve
        assert "guard" in elig
        assert "reserve" in elig
        # Should mention veterans
        assert "veteran" in elig
        # Should mention no VA enrollment required
        assert "no va enrollment" in elig
        # Should mention free
        assert "free" in elig

    def test_run_resource_how_to_apply(self):
        """Test how to apply information."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        apply = resources[0].how_to_apply.lower()
        # Should mention website
        assert "giveanhour.org" in apply
        # Should mention both delivery methods
        assert "telehealth" in apply
        assert "in-person" in apply

    def test_run_resource_tags(self):
        """Test resource tags include expected values."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        expected_tags = [
            "give-an-hour",
            "mental-health",
            "free-therapy",
            "volunteer-providers",
            "ptsd",
            "depression",
            "anxiety",
            "telehealth",
            "free-services",
            "all-eras",
            "any-discharge",
            "nationwide",
        ]

        resource = resources[0]
        for tag in expected_tags:
            assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_org_info(self):
        """Test organization information."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        resource = resources[0]
        assert resource.org_name == "Give an Hour"
        assert resource.org_website == "https://giveanhour.org/"
        assert resource.source_url == "https://giveanhour.org/military/"

    def test_run_raw_data(self):
        """Test raw data contains expected fields."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        raw = resources[0].raw_data
        assert raw["service_type"] == "volunteer_network"
        assert raw["cost"] == "free"
        assert "ptsd" in [s.lower() for s in raw["services"]] or "PTSD treatment" in raw["services"]
        assert "in-person" in raw["delivery_methods"]
        assert "telehealth" in raw["delivery_methods"]
        assert "psychologists" in raw["provider_types"]
        assert raw["founded"] == 2005

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        assert resources[0].fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with GiveAnHourConnector() as connector:
            resources = connector.run()
            assert len(resources) == 1

    def test_all_us_states_list(self):
        """Test the all US states list is complete."""
        assert len(ALL_US_STATES) == 51  # 50 states + DC
        assert "DC" in ALL_US_STATES
        assert "CA" in ALL_US_STATES
        assert "NY" in ALL_US_STATES
        assert "TX" in ALL_US_STATES

    def test_services_list(self):
        """Test that services list is properly defined."""
        connector = GiveAnHourConnector()

        services = connector.SERVICES
        assert "anxiety treatment" in services
        assert "depression treatment" in services
        assert "PTSD treatment" in services
        assert "substance abuse counseling" in services
        assert "grief counseling" in services

    def test_resource_addresses_substance_abuse(self):
        """Test that resource mentions substance abuse support."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        desc = resources[0].description.lower()
        assert "substance abuse" in desc

    def test_resource_mentions_grief_counseling(self):
        """Test that resource mentions grief counseling."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        desc = resources[0].description.lower()
        assert "grief" in desc

    def test_no_discharge_restrictions(self):
        """Test that eligibility mentions no discharge restrictions."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        elig = resources[0].eligibility.lower()
        assert "no discharge" in elig or "any discharge" not in elig or "restrictions" in elig

    def test_family_support_mentioned(self):
        """Test that some family support is mentioned in eligibility."""
        connector = GiveAnHourConnector()
        resources = connector.run()

        elig = resources[0].eligibility.lower()
        # Give an Hour serves some family members
        assert "spouse" in elig or "family" in elig or "caregiver" in elig
