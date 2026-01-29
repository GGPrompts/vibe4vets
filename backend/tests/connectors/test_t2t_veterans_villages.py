"""Tests for Tunnel to Towers Veterans Villages connector."""


from connectors.t2t_veterans_villages import (
    T2T_VILLAGES,
    T2TVeteransVillagesConnector,
)


class TestT2TVeteransVillagesConnector:
    """Tests for T2TVeteransVillagesConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = T2TVeteransVillagesConnector()
        meta = connector.metadata

        assert meta.name == "Tunnel to Towers Veterans Villages"
        assert "t2t.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_all_villages(self):
        """Test that run() returns all operational village locations."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        # Should return 5 operational villages
        assert len(resources) == 5
        assert len(resources) == len(T2T_VILLAGES)

    def test_run_all_have_housing_category(self):
        """Test that all villages have housing category."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert "housing" in resource.categories

    def test_run_all_have_local_scope(self):
        """Test that all villages have local scope."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_run_all_have_address_info(self):
        """Test that all villages have complete address information."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert resource.zip_code is not None
            assert len(resource.state) == 2

    def test_run_all_have_phone(self):
        """Test that all villages have phone numbers."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            # Phone should be normalized to (XXX) XXX-XXXX format
            assert "(" in resource.phone
            assert ")" in resource.phone
            assert "-" in resource.phone

    def test_run_all_have_states_served(self):
        """Test that all villages have states list."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert len(resource.states) == 1  # Each village serves one state

    def test_run_village_title_format(self):
        """Test village title format."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert "Tunnel to Towers" in resource.title
            assert "Veteran Housing" in resource.title

    def test_run_village_description(self):
        """Test village description content."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention housing type
            desc_lower = resource.description.lower()
            assert any(
                term in desc_lower
                for term in ["permanent", "transitional", "housing", "supportive"]
            )
            # Should mention T2T
            assert "tunnel to towers" in desc_lower

    def test_run_village_eligibility(self):
        """Test eligibility information."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention veterans
            assert "veteran" in resource.eligibility.lower()
            # Should mention homelessness
            assert "homeless" in resource.eligibility.lower()

    def test_run_village_how_to_apply(self):
        """Test how to apply information."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            # Should include contact info
            how_to = resource.how_to_apply.lower()
            assert "contact" in how_to or "call" in how_to
            # Should have phone number somewhere
            assert any(c.isdigit() for c in resource.how_to_apply)

    def test_run_village_tags(self):
        """Test village tags."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        expected_tags = [
            "tunnel-to-towers",
            "t2t",
            "veterans-village",
            "homeless-services",
            "affordable-housing",
        ]

        for resource in resources:
            for tag in expected_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_village_state_tags(self):
        """Test that state tags are added."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            # Should have a state tag
            state_tags = [t for t in resource.tags if t.startswith("state-")]
            assert len(state_tags) == 1

            # State tag should match state served
            state = resource.state.lower()
            assert f"state-{state}" in resource.tags

    def test_run_org_info(self):
        """Test organization information."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Tunnel to Towers Foundation"
            assert resource.org_website == "https://t2t.org/"
            assert "t2t.org" in resource.source_url

    def test_run_raw_data(self):
        """Test raw data includes key fields."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert "id" in resource.raw_data
            assert "name" in resource.raw_data
            assert "housing_types" in resource.raw_data

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with T2TVeteransVillagesConnector() as connector:
            resources = connector.run()
            assert len(resources) == 5

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = T2TVeteransVillagesConnector()

        assert connector._normalize_phone("3478686561") == "(347) 868-6561"
        assert connector._normalize_phone("1-718-987-1931") == "(718) 987-1931"
        assert connector._normalize_phone("(951) 867-9691") == "(951) 867-9691"

    def test_villages_by_state(self):
        """Test that villages cover expected states."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        states = {r.state for r in resources}

        # Should cover TX, CA, AZ, GA
        assert "TX" in states  # Houston
        assert "CA" in states  # March/Riverside and West LA
        assert "AZ" in states  # Phoenix
        assert "GA" in states  # Atlanta/Mableton

    def test_california_has_two_villages(self):
        """Test that California has two village locations."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        ca_villages = [r for r in resources if r.state == "CA"]
        assert len(ca_villages) == 2  # March/Riverside and West LA

    def test_houston_village_details(self):
        """Test Houston Veterans Village specific details."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        houston = None
        for r in resources:
            if r.city == "Houston":
                houston = r
                break

        assert houston is not None
        assert "18818 Tomball Parkway" in houston.address
        assert houston.state == "TX"
        assert houston.zip_code == "77070"
        assert "t2t-houston" in houston.tags

    def test_march_veterans_village_details(self):
        """Test March Veterans Village specific details."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        march = None
        for r in resources:
            if "March" in r.title:
                march = r
                break

        assert march is not None
        assert "15305 6th Street" in march.address
        assert march.city == "Riverside"
        assert march.state == "CA"
        assert march.zip_code == "92518"
        assert "t2t-march-riverside" in march.tags

    def test_atlanta_mableton_village_details(self):
        """Test Atlanta Veterans Village in Mableton specific details."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        atlanta = None
        for r in resources:
            if "Atlanta" in r.title or r.city == "Mableton":
                atlanta = r
                break

        assert atlanta is not None
        assert "65 S. Service Road" in atlanta.address
        assert atlanta.city == "Mableton"
        assert atlanta.state == "GA"
        assert atlanta.zip_code == "30126"
        assert "t2t-atlanta-mableton" in atlanta.tags

    def test_housing_types_in_tags(self):
        """Test that housing type tags are included."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        # All villages should have at least one housing type tag
        housing_type_tags = [
            "permanent-supportive-housing",
            "transitional-housing",
            "emergency-shelter",
        ]

        for resource in resources:
            has_housing_type = any(tag in resource.tags for tag in housing_type_tags)
            assert has_housing_type, f"No housing type tag for {resource.title}"

    def test_us_vets_partner_tag(self):
        """Test that U.S.VETS partnership is tagged where applicable."""
        connector = T2TVeteransVillagesConnector()
        resources = connector.run()

        # Houston, March, West LA, and Phoenix are U.S.VETS partnerships
        us_vets_cities = {"Houston", "Riverside", "Los Angeles", "Phoenix"}

        for resource in resources:
            if resource.city in us_vets_cities:
                assert "us-vets" in resource.tags
                assert "housing-first" in resource.tags
