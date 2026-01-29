"""Tests for Swords to Plowshares veteran services connector."""

import pytest

from connectors.swords_to_plowshares import (
    SWORDS_TO_PLOWSHARES_LOCATIONS,
    SWORDS_TO_PLOWSHARES_PROGRAMS,
    SwordsToPlowsharesConnector,
)


class TestSwordsToPlowsharesConnector:
    """Tests for SwordsToPlowsharesConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = SwordsToPlowsharesConnector()
        meta = connector.metadata

        assert meta.name == "Swords to Plowshares"
        assert "swords-to-plowshares.org" in meta.url
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False

    def test_run_returns_all_programs(self):
        """Test that run() returns all program resources."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        assert len(resources) == 4  # housing, legal, employment, mentalHealth
        assert len(resources) == len(SWORDS_TO_PLOWSHARES_PROGRAMS)

    def test_run_all_have_correct_categories(self):
        """Test that each program has correct category."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        categories = [r.categories[0] for r in resources]
        assert "housing" in categories
        assert "legal" in categories
        assert "employment" in categories
        assert "mentalHealth" in categories

    def test_run_all_have_local_scope(self):
        """Test that all programs have local scope."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.scope == "local"

    def test_run_all_have_address_info(self):
        """Test that all programs have complete address information."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.address is not None
            assert resource.city == "San Francisco"
            assert resource.state == "CA"
            assert resource.zip_code == "94103"

    def test_run_all_have_phone(self):
        """Test that all programs have phone number."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.phone is not None
            assert "(415) 252-4788" in resource.phone

    def test_run_all_have_california_state(self):
        """Test that all programs have CA in states list."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.states is not None
            assert "CA" in resource.states

    def test_run_housing_program(self):
        """Test housing program resource."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        housing = None
        for r in resources:
            if "housing" in r.categories:
                housing = r
                break

        assert housing is not None
        assert "Housing" in housing.title
        assert "permanent supportive housing" in housing.description.lower()
        assert "500" in housing.description  # 500+ units
        assert "homeless" in housing.eligibility.lower()

    def test_run_legal_program(self):
        """Test legal services program resource."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        legal = None
        for r in resources:
            if "legal" in r.categories:
                legal = r
                break

        assert legal is not None
        assert "Legal" in legal.title
        assert "discharge upgrade" in legal.description.lower()
        assert "va benefits" in legal.description.lower()
        assert "pro bono" in legal.description.lower()

    def test_run_employment_program(self):
        """Test employment services program resource."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        employment = None
        for r in resources:
            if "employment" in r.categories:
                employment = r
                break

        assert employment is not None
        assert "Employment" in employment.title
        assert "job" in employment.description.lower()
        assert "career" in employment.description.lower()

    def test_run_mental_health_program(self):
        """Test mental health program resource."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        mental_health = None
        for r in resources:
            if "mentalHealth" in r.categories:
                mental_health = r
                break

        assert mental_health is not None
        assert "Mental Health" in mental_health.title
        assert "peer counseling" in mental_health.description.lower()
        assert "support group" in mental_health.description.lower()

    def test_run_title_format(self):
        """Test resource title format."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert "Swords to Plowshares" in resource.title
            assert " - " in resource.title

    def test_run_description_mentions_founding(self):
        """Test descriptions mention organization history."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert "1974" in resource.description
            assert "Vietnam" in resource.description

    def test_run_eligibility_present(self):
        """Test all programs have eligibility information."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.eligibility is not None
            assert len(resource.eligibility) > 20
            assert "Bay Area" in resource.eligibility

    def test_run_how_to_apply_present(self):
        """Test all programs have how to apply information."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.how_to_apply is not None
            # Should include phone number
            assert "(415) 252-4788" in resource.how_to_apply
            # Should include address
            assert "1060 Howard" in resource.how_to_apply

    def test_run_tags(self):
        """Test resource tags."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        expected_base_tags = [
            "swords-to-plowshares",
            "bay-area",
            "san-francisco",
            "veteran-services",
            "state-ca",
        ]

        for resource in resources:
            for tag in expected_base_tags:
                assert tag in resource.tags, f"Missing tag: {tag}"

    def test_run_housing_specific_tags(self):
        """Test housing program has specific tags."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        housing = next(r for r in resources if "housing" in r.categories)

        expected_tags = [
            "permanent-supportive-housing",
            "homeless-services",
            "housing-services",
        ]
        for tag in expected_tags:
            assert tag in housing.tags, f"Missing tag: {tag}"

    def test_run_legal_specific_tags(self):
        """Test legal program has specific tags."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        legal = next(r for r in resources if "legal" in r.categories)

        expected_tags = [
            "discharge-upgrade",
            "va-benefits",
            "legal-services",
            "pro-bono",
        ]
        for tag in expected_tags:
            assert tag in legal.tags, f"Missing tag: {tag}"

    def test_run_org_info(self):
        """Test organization information."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.org_name == "Swords to Plowshares"
            assert resource.org_website == "https://www.swords-to-plowshares.org/"
            assert resource.source_url == "https://www.swords-to-plowshares.org/"

    def test_run_raw_data(self):
        """Test raw data includes program details."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert "program_id" in resource.raw_data
            assert "program_name" in resource.raw_data
            assert "category" in resource.raw_data
            assert "services" in resource.raw_data
            assert "locations" in resource.raw_data
            assert "founded" in resource.raw_data
            assert resource.raw_data["founded"] == "1974"

    def test_run_raw_data_has_both_locations(self):
        """Test raw data includes both SF and Oakland locations."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            locations = resource.raw_data["locations"]
            assert "sf" in locations
            assert "oakland" in locations
            assert locations["sf"]["city"] == "San Francisco"
            assert locations["oakland"]["city"] == "Oakland"

    def test_run_fetched_at_timestamp(self):
        """Test that fetched_at timestamp is set."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.fetched_at is not None

    def test_run_hours_present(self):
        """Test that hours are present."""
        connector = SwordsToPlowsharesConnector()
        resources = connector.run()

        for resource in resources:
            assert resource.hours is not None
            assert "Mon" in resource.hours

    def test_context_manager(self):
        """Test that connector works as context manager."""
        with SwordsToPlowsharesConnector() as connector:
            resources = connector.run()
            assert len(resources) == 4

    def test_locations_data_structure(self):
        """Test SWORDS_TO_PLOWSHARES_LOCATIONS data structure."""
        assert "sf" in SWORDS_TO_PLOWSHARES_LOCATIONS
        assert "oakland" in SWORDS_TO_PLOWSHARES_LOCATIONS

        sf = SWORDS_TO_PLOWSHARES_LOCATIONS["sf"]
        assert sf["city"] == "San Francisco"
        assert sf["state"] == "CA"
        assert sf["zip_code"] == "94103"
        assert "(415)" in sf["phone"]

        oakland = SWORDS_TO_PLOWSHARES_LOCATIONS["oakland"]
        assert oakland["city"] == "Oakland"
        assert oakland["state"] == "CA"
        assert oakland["zip_code"] == "94607"
        assert "(510)" in oakland["phone"]

    def test_programs_data_structure(self):
        """Test SWORDS_TO_PLOWSHARES_PROGRAMS data structure."""
        assert len(SWORDS_TO_PLOWSHARES_PROGRAMS) == 4

        categories = [p["category"] for p in SWORDS_TO_PLOWSHARES_PROGRAMS]
        assert "housing" in categories
        assert "legal" in categories
        assert "employment" in categories
        assert "mentalHealth" in categories

        for program in SWORDS_TO_PLOWSHARES_PROGRAMS:
            assert "id" in program
            assert "name" in program
            assert "category" in program
            assert "description" in program
            assert "services" in program
            assert "eligibility" in program
            assert "how_to_apply" in program
            assert "tags" in program

    def test_unique_program_ids(self):
        """Test that all programs have unique IDs."""
        ids = [p["id"] for p in SWORDS_TO_PLOWSHARES_PROGRAMS]
        assert len(ids) == len(set(ids))
