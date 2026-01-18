"""Tests for Legal Aid (LSC) connector."""

from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

import pytest

from connectors.legal_aid import LegalAidConnector


class TestLegalAidConnector:
    """Tests for LegalAidConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")
        meta = connector.metadata

        assert meta.name == "LSC Grantee Directory"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "yearly"
        assert meta.requires_auth is False
        assert "lsc.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.yaml"
        connector = LegalAidConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.yaml")
        connector = LegalAidConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_state_code_to_name(self):
        """Test state code to name conversion."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        assert connector._state_code_to_name("CA") == "California"
        assert connector._state_code_to_name("TX") == "Texas"
        assert connector._state_code_to_name("DC") == "District of Columbia"
        assert connector._state_code_to_name("PR") == "Puerto Rico"
        assert connector._state_code_to_name("VI") == "Virgin Islands"
        assert connector._state_code_to_name("XX") == "XX"  # Unknown returns code

    def test_build_description(self):
        """Test description building."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        desc = connector._build_description(
            org_name="Test Legal Aid",
            state_name="California",
            services=["benefits", "housing", "family"],
        )

        assert "Test Legal Aid provides free civil legal assistance" in desc
        assert "California" in desc
        assert "VA benefits appeals" in desc
        assert "housing issues" in desc
        assert "family law" in desc
        assert "LSC-funded" in desc

    def test_build_description_consumer_services(self):
        """Test description with consumer services."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        desc = connector._build_description(
            org_name="Test Legal Aid",
            state_name="Texas",
            services=["consumer", "civil"],
        )

        assert "consumer protection" in desc

    def test_build_eligibility(self):
        """Test eligibility text."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        eligibility = connector._build_eligibility()

        assert "125-200% of federal poverty level" in eligibility
        assert "Veterans are eligible" in eligibility
        assert "discharge status" in eligibility

    def test_build_how_to_apply(self):
        """Test how-to-apply text."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        how_to_apply = connector._build_how_to_apply(
            org_name="Test Legal Aid",
            website="https://example.org",
            phone="555-123-4567",
        )

        assert "Contact Test Legal Aid" in how_to_apply
        assert "https://example.org" in how_to_apply
        assert "555-123-4567" in how_to_apply
        assert "LawHelp.org" in how_to_apply

    def test_build_how_to_apply_no_contact(self):
        """Test how-to-apply text with no website or phone."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        how_to_apply = connector._build_how_to_apply(
            org_name="Test Legal Aid",
            website=None,
            phone=None,
        )

        assert "Contact Test Legal Aid" in how_to_apply
        assert "LawHelp.org" in how_to_apply

    def test_build_tags(self):
        """Test tag building."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        tags = connector._build_tags(
            services=["benefits", "housing", "family", "consumer"],
            state="CA",
        )

        assert "legal-aid" in tags
        assert "lsc-funded" in tags
        assert "free-legal-services" in tags
        assert "benefits-appeals" in tags
        assert "housing-legal" in tags
        assert "family-law" in tags
        assert "consumer-protection" in tags
        assert "state-ca" in tags

    def test_build_tags_with_immigration(self):
        """Test tag building with immigration services."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        tags = connector._build_tags(
            services=["immigration", "civil"],
            state="TX",
        )

        assert "immigration" in tags
        assert "state-tx" in tags

    def test_parse_grantee(self):
        """Test parsing a single grantee."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")
        now = datetime.now(UTC)

        grantee = {
            "name": "Bay Area Legal Aid",
            "state": "CA",
            "website": "https://www.baylegal.org",
            "services": ["civil", "housing", "family", "benefits"],
        }

        candidate = connector._parse_grantee(grantee, fetched_at=now)

        assert candidate.title == "Legal Aid - Bay Area Legal Aid"
        assert "Bay Area Legal Aid" in candidate.description
        assert "California" in candidate.description
        assert candidate.org_name == "Bay Area Legal Aid"
        assert candidate.org_website == "https://www.baylegal.org"
        assert candidate.categories == ["legal"]
        assert candidate.scope == "state"
        assert candidate.states == ["CA"]
        assert candidate.state == "CA"
        assert "lsc-funded" in candidate.tags
        assert candidate.raw_data["lsc_grantee"] is True

    def test_parse_grantee_no_website(self):
        """Test parsing a grantee without a website."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")
        now = datetime.now(UTC)

        grantee = {
            "name": "American Samoa Legal Aid",
            "state": "AS",
            "services": ["civil", "housing", "family"],
        }

        candidate = connector._parse_grantee(grantee, fetched_at=now)

        assert candidate.org_website is None
        assert "lsc.gov" in candidate.source_url  # Falls back to LSC directory

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = LegalAidConnector(data_path=tmp_path / "nonexistent.yaml")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "LSC grantee data file not found" in str(exc_info.value)

    def test_run_parses_yaml(self, tmp_path):
        """Test that run() parses YAML correctly."""
        yaml_content = dedent("""
            source:
              name: "LSC Grantee Directory"
              url: "https://www.lsc.gov"

            grantees:
              - name: "Legal Services Alabama"
                state: "AL"
                website: "https://www.legalservicesalabama.org"
                services: ["civil", "housing", "family", "benefits"]

              - name: "Alaska Legal Services Corporation"
                state: "AK"
                website: "https://www.alsc-law.org"
                services: ["civil", "housing", "family", "benefits"]

              - name: "Non-Relevant Org"
                state: "TX"
                services: ["unknown-service-only"]
        """)

        test_file = tmp_path / "test.yaml"
        test_file.write_text(yaml_content)

        connector = LegalAidConnector(data_path=test_file)
        resources = connector.run()

        # Should have 2 resources (third filtered out - no veteran-relevant services)
        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Legal Aid - Legal Services Alabama"
        assert resources[0].states is not None
        assert resources[0].states == ["AL"]

        # Second resource
        assert resources[1].title == "Legal Aid - Alaska Legal Services Corporation"
        assert resources[1].states is not None
        assert resources[1].states == ["AK"]

    def test_run_filters_non_veteran_services(self, tmp_path):
        """Test that run() filters out orgs without veteran-relevant services."""
        yaml_content = dedent("""
            grantees:
              - name: "Relevant Org"
                state: "CA"
                services: ["housing", "benefits"]

              - name: "Only Immigration"
                state: "TX"
                services: ["immigration-only"]
        """)

        test_file = tmp_path / "test.yaml"
        test_file.write_text(yaml_content)

        connector = LegalAidConnector(data_path=test_file)
        resources = connector.run()

        # Only the org with veteran-relevant services should be included
        assert len(resources) == 1
        assert resources[0].org_name == "Relevant Org"

    def test_run_with_real_data(self):
        """Test run() with the actual LSC grantee data file."""
        # Find the data file
        data_file: Path | None = None
        current = Path(__file__).resolve().parent
        while current != current.parent:
            candidate = current / "data" / "reference" / "lsc_grantees.yaml"
            if candidate.exists():
                data_file = candidate
                break
            current = current.parent

        if data_file is None:
            pytest.skip("lsc_grantees.yaml not found in project")
            return  # Make pyright happy

        connector = LegalAidConnector(data_path=data_file)
        resources = connector.run()

        # Should have most of the 129 grantees (all should have veteran-relevant services)
        assert len(resources) >= 100

        # All should be legal category
        for r in resources:
            assert r.categories is not None
            assert "legal" in r.categories

        # All should have lsc-funded tag
        for r in resources:
            assert r.tags is not None
            assert "lsc-funded" in r.tags

        # Check first resource structure
        first = resources[0]
        assert first.title.startswith("Legal Aid - ")
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.scope == "state"

        # Check for coverage across multiple states
        states: set[str] = set()
        for r in resources:
            if r.states:
                states.update(r.states)
        # Should have broad coverage
        assert len(states) >= 40  # Most states covered

    def test_veteran_relevant_services_filter(self):
        """Test that VETERAN_RELEVANT_SERVICES filter is correct."""
        connector = LegalAidConnector(data_path="/fake/path.yaml")

        # These should be included
        assert "benefits" in connector.VETERAN_RELEVANT_SERVICES
        assert "housing" in connector.VETERAN_RELEVANT_SERVICES
        assert "family" in connector.VETERAN_RELEVANT_SERVICES
        assert "employment" in connector.VETERAN_RELEVANT_SERVICES
        assert "civil" in connector.VETERAN_RELEVANT_SERVICES
