"""Tests for Cohen Veterans Network mental health clinic connector."""


from connectors.cohen_veterans_network import (
    COHEN_CLINICS,
    CohenVeteransNetworkConnector,
)


class TestCohenVeteransNetworkConnector:
    """Tests for CohenVeteransNetworkConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = CohenVeteransNetworkConnector()
        meta = connector.metadata

        assert meta.name == "Cohen Veterans Network"
        assert "cohenveteransnetwork.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_all_clinics(self):
        """Test that run() returns all 22 clinic locations."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        assert len(resources) == 22
        assert len(resources) == len(COHEN_CLINICS)

    def test_run_all_have_mental_health_category(self):
        """Test that all clinics have mentalHealth category."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert "mentalHealth" in resource.categories

    def test_run_all_have_local_scope(self):
        """Test that all clinics have local scope."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_run_all_have_address_info(self):
        """Test that all clinics have complete address information."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city is not None
            assert resource.state is not None
            assert resource.zip_code is not None
            assert len(resource.state) == 2

    def test_run_all_have_phone(self):
        """Test that all clinics have normalized phone numbers."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            # Phone should be normalized to (XXX) XXX-XXXX format
            assert "(" in resource.phone
            assert ")" in resource.phone
            assert "-" in resource.phone

    def test_run_all_have_states_served(self):
        """Test that all clinics have states list."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert len(resource.states) >= 1

    def test_run_multi_state_clinic(self):
        """Test that Easterseals clinic serves multiple states."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        # Find the Easterseals clinic (Silver Spring, MD)
        easterseals = None
        for r in resources:
            if "Easterseals" in r.title:
                easterseals = r
                break

        assert easterseals is not None
        assert len(easterseals.states) == 7
        assert "MD" in easterseals.states
        assert "DC" in easterseals.states
        assert "VA" in easterseals.states
        assert "DE" in easterseals.states
        assert "PA" in easterseals.states
        assert "NJ" in easterseals.states
        assert "WV" in easterseals.states

    def test_run_clinic_title_format(self):
        """Test clinic title format."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert "Cohen Clinic" in resource.title
            assert "Free Mental Health Care" in resource.title

    def test_run_clinic_description(self):
        """Test clinic description content."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention post-9/11 Veterans
            assert "post-9/11" in resource.description.lower()
            # Should mention free services
            assert "free" in resource.description.lower()
            # Should mention families
            assert "famil" in resource.description.lower()

    def test_run_clinic_eligibility(self):
        """Test eligibility information."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            # Should mention post-9/11
            assert "post-9/11" in resource.eligibility.lower()
            # Should mention no VA enrollment required
            assert "no va enrollment" in resource.eligibility.lower()
            # Should mention free
            assert "free" in resource.eligibility.lower()
            # Should mention family
            assert "family" in resource.eligibility.lower()

    def test_run_clinic_how_to_apply(self):
        """Test how to apply information."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            # Should include a phone number (may be raw or normalized format)
            assert "Call" in resource.how_to_apply
            assert any(c.isdigit() for c in resource.how_to_apply)
            # Should mention national line
            assert "844-336-4226" in resource.how_to_apply

    def test_run_clinic_tags(self):
        """Test clinic tags."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        expected_tags = [
            "mental-health",
            "free-services",
            "post-9/11",
            "ptsd",
            "depression",
            "anxiety",
            "family-support",
            "no-va-enrollment",
            "cohen-veterans-network",
            "telehealth",
            "cohen-clinic",
        ]

        for resource in resources:
            for tag in expected_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_clinic_state_tags(self):
        """Test that state tags are added."""
        connector = CohenVeteransNetworkConnector()
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
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Cohen Veterans Network"
            assert resource.org_website == "https://www.cohenveteransnetwork.org/"
            assert resource.source_url == "https://www.cohenveteransnetwork.org/clinics/"

    def test_run_raw_data(self):
        """Test raw data includes partner organization."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        partner_orgs = set()
        for resource in resources:
            assert "clinic_name" in resource.raw_data
            assert "partner_org" in resource.raw_data
            assert "serves_states" in resource.raw_data
            assert "national_phone" in resource.raw_data
            partner_orgs.add(resource.raw_data["partner_org"])

        # Should have multiple partner organizations
        assert len(partner_orgs) > 5
        assert "Centerstone" in partner_orgs
        assert "Endeavors" in partner_orgs
        assert "Red Rock" in partner_orgs

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with CohenVeteransNetworkConnector() as connector:
            resources = connector.run()
            assert len(resources) == 22

    def test_state_code_to_name(self):
        """Test state code to name conversion."""
        connector = CohenVeteransNetworkConnector()

        assert connector._state_code_to_name("CA") == "California"
        assert connector._state_code_to_name("TX") == "Texas"
        assert connector._state_code_to_name("DC") == "District of Columbia"
        assert connector._state_code_to_name("XX") == "XX"  # Unknown returns as-is

    def test_phone_normalization(self):
        """Test phone number normalization."""
        connector = CohenVeteransNetworkConnector()

        assert connector._normalize_phone("9077628668") == "(907) 762-8668"
        assert connector._normalize_phone("1-907-762-8668") == "(907) 762-8668"
        assert connector._normalize_phone("(907) 762-8668") == "(907) 762-8668"

    def test_clinic_coverage_by_state(self):
        """Test that clinics cover expected states."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        # Collect all states served
        all_states = set()
        for resource in resources:
            all_states.update(resource.states)

        # Should cover many states
        assert len(all_states) >= 20

        # Key military state coverage
        assert "TX" in all_states  # Multiple bases
        assert "CA" in all_states  # Multiple bases
        assert "NC" in all_states  # Fort Liberty, Camp Lejeune
        assert "VA" in all_states  # Pentagon, Norfolk
        assert "FL" in all_states  # Multiple bases
        assert "AK" in all_states  # JBER
        assert "HI" in all_states  # Pearl Harbor
        assert "WA" in all_states  # JBLM
        assert "OK" in all_states  # Fort Sill

    def test_texas_has_multiple_clinics(self):
        """Test that Texas has multiple clinic locations."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        texas_clinics = [r for r in resources if r.state == "TX"]
        assert len(texas_clinics) == 4  # Dallas, San Antonio, Killeen, El Paso

    def test_california_has_multiple_clinics(self):
        """Test that California has multiple clinic locations."""
        connector = CohenVeteransNetworkConnector()
        resources = connector.run()

        ca_clinics = [r for r in resources if r.state == "CA"]
        assert len(ca_clinics) == 3  # San Diego, Oceanside, Los Angeles/Torrance
