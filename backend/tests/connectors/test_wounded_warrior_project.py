"""Tests for Wounded Warrior Project connector."""

from connectors.wounded_warrior_project import (
    WARRIOR_CARE_NETWORK_CENTERS,
    WoundedWarriorProjectConnector,
)


class TestWoundedWarriorProjectConnector:
    """Tests for WoundedWarriorProjectConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = WoundedWarriorProjectConnector()
        meta = connector.metadata

        assert meta.name == "Wounded Warrior Project"
        assert "woundedwarriorproject.org" in meta.url
        assert meta.tier == 1  # Major national nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_expected_resource_count(self):
        """Test that run() returns correct number of resources."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        # 4 Warrior Care Network centers + 1 Project Odyssey + 1 WWP Talk
        expected_count = len(WARRIOR_CARE_NETWORK_CENTERS) + 2
        assert len(resources) == expected_count
        assert len(resources) == 6

    def test_run_all_have_mental_health_category(self):
        """Test that all resources have mentalHealth category."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            assert "mentalHealth" in resource.categories

    def test_warrior_care_network_centers_count(self):
        """Test that there are exactly 4 Warrior Care Network centers."""
        assert len(WARRIOR_CARE_NETWORK_CENTERS) == 4

    def test_warrior_care_network_center_names(self):
        """Test that all 4 expected academic medical centers are present."""
        center_names = [c["name"] for c in WARRIOR_CARE_NETWORK_CENTERS]

        assert any("Emory" in name for name in center_names)
        assert any("Massachusetts General" in name or "Mass" in name for name in center_names)
        assert any("Rush" in name for name in center_names)
        assert any("UCLA" in name for name in center_names)

    def test_warrior_care_network_center_states(self):
        """Test that centers are in expected states."""
        states = [c["state"] for c in WARRIOR_CARE_NETWORK_CENTERS]

        assert "GA" in states  # Emory - Atlanta
        assert "MA" in states  # MGH - Boston
        assert "IL" in states  # Rush - Chicago
        assert "CA" in states  # UCLA - Los Angeles

    def test_run_wcn_resources_have_addresses(self):
        """Test that Warrior Care Network resources have addresses."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        wcn_resources = [r for r in resources if "Warrior Care Network" in r.title]
        assert len(wcn_resources) == 4

        for resource in wcn_resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert resource.zip_code is not None

    def test_run_wcn_resources_scope(self):
        """Test that WCN resources have national scope (accepts veterans nationwide)."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        wcn_resources = [r for r in resources if "Warrior Care Network" in r.title]

        for resource in wcn_resources:
            # Centers accept veterans from all states
            assert resource.scope == "national"

    def test_run_project_odyssey_resource(self):
        """Test the Project Odyssey resource."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        odyssey = [r for r in resources if "Project Odyssey" in r.title]
        assert len(odyssey) == 1

        resource = odyssey[0]
        assert "12-Week" in resource.title or "12 week" in resource.description.lower()
        assert resource.scope == "national"
        assert "project-odyssey" in resource.tags

    def test_run_wwp_talk_resource(self):
        """Test the WWP Talk resource."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        talk = [r for r in resources if "WWP Talk" in r.title]
        assert len(talk) == 1

        resource = talk[0]
        assert "peer support" in resource.title.lower() or "peer support" in resource.description.lower()
        assert resource.scope == "national"
        assert "wwp-talk" in resource.tags

    def test_run_all_have_post_911_eligibility(self):
        """Test that all resources mention Post-9/11 eligibility."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            elig = resource.eligibility.lower()
            assert "post-9/11" in elig or "september 11" in elig or "9/11" in elig

    def test_run_all_have_free_services(self):
        """Test that all resources are free."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            # Check description or eligibility mentions free
            text = (resource.description + resource.eligibility).lower()
            assert "free" in text

    def test_run_wcn_description_mentions_key_features(self):
        """Test WCN descriptions mention key program features."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        wcn_resources = [r for r in resources if "Warrior Care Network" in r.title]

        for resource in wcn_resources:
            desc = resource.description.lower()
            # Should mention 2-week program
            assert "2-week" in desc or "two-week" in desc or "two week" in desc
            # Should mention 50+ hours
            assert "50" in desc
            # Should mention PTSD, TBI, or MST
            assert any(term in desc for term in ["ptsd", "tbi", "mst", "traumatic"])

    def test_run_project_odyssey_mentions_adventure(self):
        """Test Project Odyssey mentions adventure-based learning."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        odyssey = [r for r in resources if "Project Odyssey" in r.title][0]
        desc = odyssey.description.lower()

        assert "adventure" in desc
        # Should mention some activities
        assert any(act in desc for act in ["hiking", "climbing", "skiing", "rafting"])

    def test_run_wwp_talk_mentions_non_clinical(self):
        """Test WWP Talk mentions it is non-clinical."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        talk = [r for r in resources if "WWP Talk" in r.title][0]

        assert "non-clinical" in talk.title.lower() or "non-clinical" in talk.description.lower()

    def test_run_org_info(self):
        """Test organization information is consistent."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Wounded Warrior Project"
            assert "woundedwarriorproject.org" in resource.org_website

    def test_run_contact_info(self):
        """Test contact information is present."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            assert resource.email is not None
            assert "woundedwarriorproject.org" in resource.email

    def test_run_how_to_apply(self):
        """Test how to apply information is present."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            apply = resource.how_to_apply.lower()
            # Should mention registration
            assert "registration" in apply or "register" in apply
            # Should have contact method
            assert "call" in apply or "email" in apply or "contact" in apply

    def test_run_tags_include_expected_values(self):
        """Test resources have expected tags."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        expected_base_tags = [
            "mental-health",
            "free-services",
            "post-9/11",
            "wounded-warrior-project",
        ]

        for resource in resources:
            for tag in expected_base_tags:
                assert tag in resource.tags, f"Missing tag: {tag} in {resource.title}"

    def test_run_wcn_tags_include_conditions(self):
        """Test WCN resources have condition-specific tags."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        wcn_resources = [r for r in resources if "Warrior Care Network" in r.title]

        for resource in wcn_resources:
            assert "ptsd" in resource.tags
            assert "tbi" in resource.tags
            assert "mst" in resource.tags

    def test_run_raw_data_wcn(self):
        """Test raw data for WCN resources."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        wcn_resources = [r for r in resources if "Warrior Care Network" in r.title]

        for resource in wcn_resources:
            raw = resource.raw_data
            assert raw["program"] == "Warrior Care Network"
            assert raw["duration"] == "2 weeks"
            assert "50" in raw["treatment_hours"]
            assert "PTSD" in raw["conditions_treated"]
            assert "TBI" in raw["conditions_treated"]
            assert "MST" in raw["conditions_treated"]

    def test_run_raw_data_odyssey(self):
        """Test raw data for Project Odyssey resource."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        odyssey = [r for r in resources if "Project Odyssey" in r.title][0]
        raw = odyssey.raw_data

        assert raw["program"] == "Project Odyssey"
        assert raw["duration"] == "12 weeks"
        assert raw["retreat_length"] == "5 days"
        assert "free" in raw["cost"]
        assert "hiking" in raw["activities"]

    def test_run_raw_data_talk(self):
        """Test raw data for WWP Talk resource."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        talk = [r for r in resources if "WWP Talk" in r.title][0]
        raw = talk.raw_data

        assert raw["program"] == "WWP Talk"
        assert raw["call_frequency"] == "weekly"
        assert raw["is_clinical"] is False
        assert raw["is_crisis_line"] is False

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with WoundedWarriorProjectConnector() as connector:
            resources = connector.run()
            assert len(resources) == 6

    def test_wcn_centers_have_all_required_fields(self):
        """Test that WCN center data has all required fields."""
        required_fields = ["name", "partner", "address", "city", "state", "zip_code", "phone", "website"]

        for center in WARRIOR_CARE_NETWORK_CENTERS:
            for field in required_fields:
                assert field in center, f"Missing field: {field}"
                assert center[field], f"Empty field: {field}"

    def test_phone_number_normalization(self):
        """Test that phone numbers are normalized."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            if resource.phone:
                # Should be in format (XXX) XXX-XXXX
                assert "(" in resource.phone
                assert ")" in resource.phone
                assert "-" in resource.phone

    def test_source_urls_are_valid(self):
        """Test that source URLs point to WWP website."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        for resource in resources:
            assert "woundedwarriorproject.org" in resource.source_url

    def test_wwp_talk_not_crisis_line_warning(self):
        """Test that WWP Talk eligibility warns it's not a crisis line."""
        connector = WoundedWarriorProjectConnector()
        resources = connector.run()

        talk = [r for r in resources if "WWP Talk" in r.title][0]
        elig = talk.eligibility.lower()

        # Should mention it's not a crisis line
        assert "not" in elig and "crisis" in elig
        # Should mention Veterans Crisis Line
        assert "988" in elig
