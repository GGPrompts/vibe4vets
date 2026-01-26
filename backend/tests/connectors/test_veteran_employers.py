"""Tests for Veteran Employers connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.veteran_employers import VeteranEmployersConnector


class TestVeteranEmployersConnector:
    """Tests for VeteranEmployersConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Veteran Employers (Compiled)"
        assert meta.tier == 2  # Established sources
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "veteranjobsmission.com" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = VeteranEmployersConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = VeteranEmployersConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_employer_basic(self):
        """Test parsing a basic employer entry."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        employer = {
            "name": "Test Corp",
            "industry": "Technology",
            "programs": ["SkillBridge", "Veteran Jobs Mission Member"],
            "has_erg": True,
            "erg_name": "Test Veterans ERG",
            "skills_translator": True,
            "careers_url": "https://example.com/careers",
            "scope": "national",
            "hire_vets_medallion": True,
            "notes": "Great employer for veterans.",
        }

        candidate = connector._parse_employer(employer, fetched_at=now)

        assert candidate.title == "Test Corp - Veteran Hiring Program"
        assert "Test Corp" in candidate.description
        assert "Technology" in candidate.description
        assert candidate.org_name == "Test Corp"
        assert candidate.org_website == "https://example.com/careers"
        assert "employment" in candidate.categories
        assert "veteran-employer" in candidate.tags
        assert "veteran-preference" in candidate.tags
        assert "skillbridge" in candidate.tags
        assert "hire-vets-medallion" in candidate.tags
        assert "veteran-erg" in candidate.tags
        assert "skills-translator" in candidate.tags
        assert candidate.scope == "national"
        assert candidate.raw_data == employer

    def test_parse_employer_minimal(self):
        """Test parsing an employer with minimal data."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        employer = {
            "name": "Simple Inc",
            "industry": "Retail",
            "programs": [],
            "has_erg": False,
            "skills_translator": False,
            "careers_url": "",
            "hire_vets_medallion": False,
        }

        candidate = connector._parse_employer(employer, fetched_at=now)

        assert candidate.title == "Simple Inc - Veteran Hiring Program"
        assert candidate.source_url == "https://veteranjobsmission.com/"
        assert "veteran-employer" in candidate.tags
        assert "hire-vets-medallion" not in candidate.tags
        assert "veteran-erg" not in candidate.tags

    def test_parse_employer_no_name(self):
        """Test parsing an employer without name returns None."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        employer = {
            "industry": "Technology",
            "programs": ["SkillBridge"],
        }

        candidate = connector._parse_employer(employer, fetched_at=now)
        assert candidate is None

    def test_build_description_full(self):
        """Test description building with all fields."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Test Corp",
            industry="Financial Services",
            programs=["SkillBridge", "Veteran Jobs Mission Member", "Hiring Our Heroes"],
            has_erg=True,
            erg_name="Veterans Network",
            skills_translator=True,
            hire_vets_medallion=True,
            notes="Hired over 10,000 veterans.",
        )

        assert "Test Corp" in desc
        assert "Financial Services" in desc
        assert "DOL HIRE Vets Medallion" in desc
        assert "Veteran Jobs Mission" in desc
        assert "Hiring Our Heroes" in desc
        assert "Veterans Network" in desc
        assert "military skills translator" in desc
        assert "Hired over 10,000 veterans" in desc

    def test_build_description_minimal(self):
        """Test description building with minimal fields."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Basic Corp",
            industry="",
            programs=[],
            has_erg=False,
            erg_name=None,
            skills_translator=False,
            hire_vets_medallion=False,
            notes="",
        )

        assert "Basic Corp" in desc
        assert "commitment to hiring veterans" in desc

    def test_build_eligibility_with_skillbridge(self):
        """Test eligibility text includes SkillBridge info."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility(programs=["SkillBridge Program"])

        assert "Veterans of all branches" in elig
        assert "SkillBridge" in elig
        assert "180 days" in elig
        assert "Military spouses" in elig

    def test_build_eligibility_with_fellowship(self):
        """Test eligibility text includes fellowship info."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility(programs=["Corporate Fellowship Program"])

        assert "Fellowship" in elig

    def test_build_eligibility_basic(self):
        """Test eligibility text for basic employer."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility(programs=["General Hiring"])

        assert "Veterans of all branches" in elig
        assert "Military spouses" in elig
        assert "SkillBridge" not in elig

    def test_build_how_to_apply_with_url(self):
        """Test how to apply includes careers URL."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        apply = connector._build_how_to_apply(
            name="Test Corp",
            careers_url="https://example.com/careers",
            programs=["General"],
        )

        assert "https://example.com/careers" in apply
        assert "Test Corp" in apply
        assert "veteran careers page" in apply

    def test_build_how_to_apply_without_url(self):
        """Test how to apply without careers URL."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        apply = connector._build_how_to_apply(
            name="Test Corp",
            careers_url="",
            programs=["General"],
        )

        assert "Search for Test Corp veteran careers" in apply
        assert "company website" in apply

    def test_build_how_to_apply_with_skillbridge(self):
        """Test how to apply includes SkillBridge instructions."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        apply = connector._build_how_to_apply(
            name="Test Corp",
            careers_url="https://example.com/careers",
            programs=["SkillBridge"],
        )

        assert "transition office" in apply
        assert "SkillBridge" in apply

    def test_build_tags_basic(self):
        """Test tag building with basic fields."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            industry="Technology",
            programs=[],
            has_erg=False,
            skills_translator=False,
            hire_vets_medallion=False,
        )

        assert "veteran-employer" in tags
        assert "veteran-preference" in tags
        assert "veteran-hiring" in tags
        assert "industry-technology" in tags

    def test_build_tags_full(self):
        """Test tag building with all features."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            industry="Financial Services",
            programs=["SkillBridge", "Apprenticeship", "Veteran Jobs Mission", "Hiring Our Heroes Fellowship"],
            has_erg=True,
            skills_translator=True,
            hire_vets_medallion=True,
        )

        assert "veteran-employer" in tags
        assert "industry-financial-services" in tags
        assert "skillbridge" in tags
        assert "apprenticeship" in tags
        assert "fellowship" in tags
        assert "veteran-jobs-mission" in tags
        assert "hiring-our-heroes" in tags
        assert "veteran-erg" in tags
        assert "skills-translator" in tags
        assert "hire-vets-medallion" in tags

    def test_build_tags_no_duplicates(self):
        """Test that tags list has no duplicates."""
        connector = VeteranEmployersConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            industry="Tech",
            programs=["SkillBridge", "SkillBridge Program"],  # Duplicate program
            has_erg=True,
            skills_translator=True,
            hire_vets_medallion=True,
        )

        # Should have no duplicates
        assert len(tags) == len(set(tags))

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = VeteranEmployersConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "Veteran employers data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        test_data = {
            "source": "Test",
            "employers": [
                {
                    "name": "Company A",
                    "industry": "Technology",
                    "programs": ["SkillBridge"],
                    "has_erg": True,
                    "erg_name": "Veterans@A",
                    "skills_translator": True,
                    "careers_url": "https://a.com/careers",
                    "scope": "national",
                    "hire_vets_medallion": True,
                    "notes": "Good company.",
                },
                {
                    "name": "Company B",
                    "industry": "Retail",
                    "programs": [],
                    "has_erg": False,
                    "skills_translator": False,
                    "careers_url": "https://b.com/careers",
                    "scope": "national",
                    "hire_vets_medallion": False,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VeteranEmployersConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert resources[0].title == "Company A - Veteran Hiring Program"
        assert "employment" in resources[0].categories
        assert "skillbridge" in resources[0].tags

        # Second resource
        assert resources[1].title == "Company B - Veteran Hiring Program"
        assert "skillbridge" not in resources[1].tags

    def test_run_skips_invalid_entries(self, tmp_path):
        """Test that run() skips entries without name."""
        test_data = {
            "employers": [
                {"name": "Valid Corp", "industry": "Tech"},
                {"industry": "Invalid - no name"},  # Missing name
                {"name": "Also Valid", "industry": "Finance"},
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VeteranEmployersConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2
        names = [r.org_name for r in resources]
        assert "Valid Corp" in names
        assert "Also Valid" in names

    def test_run_with_real_data(self):
        """Test run() with the actual veteran employers data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_employers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_employers.json not found in project")

        connector = VeteranEmployersConnector(data_path=data_file)
        resources = connector.run()

        # Should have multiple employers
        assert len(resources) >= 50

        # All should be employment category
        assert all("employment" in r.categories for r in resources)

        # All should have veteran-employer tag
        assert all("veteran-employer" in r.tags for r in resources)

        # All should have veteran-preference tag
        assert all("veteran-preference" in r.tags for r in resources)

        # Check for expected employers
        names = {r.org_name for r in resources}
        assert "JPMorgan Chase" in names
        assert "Amazon" in names
        assert "USAA" in names
        assert "Lockheed Martin" in names

        # Check resource structure
        first = resources[0]
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.scope == "national"

    def test_categories_are_employment(self):
        """Test that all employer resources are employment category."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_employers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_employers.json not found in project")

        connector = VeteranEmployersConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.categories == ["employment"]

    def test_all_have_veteran_preference_tag(self):
        """Test that all employers have veteran-preference subcategory tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_employers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_employers.json not found in project")

        connector = VeteranEmployersConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert "veteran-preference" in resource.tags, f"{resource.org_name} missing veteran-preference tag"

    def test_skillbridge_employers_have_tag(self):
        """Test that employers with SkillBridge programs have the tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_employers.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_employers.json not found in project")

        connector = VeteranEmployersConnector(data_path=data_file)
        resources = connector.run()

        # Find employers with SkillBridge in programs
        for resource in resources:
            raw = resource.raw_data
            programs = raw.get("programs", [])
            has_skillbridge = any("SkillBridge" in p for p in programs)
            if has_skillbridge:
                assert "skillbridge" in resource.tags, f"{resource.org_name} missing skillbridge tag"
