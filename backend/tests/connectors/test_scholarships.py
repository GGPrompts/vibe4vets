"""Tests for Veteran Scholarships connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.scholarships import ScholarshipsConnector


class TestScholarshipsConnector:
    """Tests for ScholarshipsConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Veteran Scholarships (Compiled)"
        assert meta.tier == 2  # Established programs
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "va.gov/education" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = ScholarshipsConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = ScholarshipsConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_scholarship_basic(self):
        """Test parsing a basic scholarship entry."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        scholarship = {
            "name": "Test Scholarship",
            "organization": "Test Foundation",
            "amount": "$5,000",
            "deadline": "March 15 (annual)",
            "eligibility": ["Veterans of all branches", "Active duty service members"],
            "description": "Provides educational funding for Veterans.",
            "how_to_apply": "Apply online through the foundation website.",
            "website": "https://example.com/scholarships",
            "renewable": True,
            "notes": "Highly competitive scholarship.",
        }

        candidate = connector._parse_scholarship(scholarship, fetched_at=now)

        assert candidate.title == "Test Scholarship"
        assert "Test Foundation" in candidate.org_name
        assert "education" in candidate.categories
        assert "scholarships" in candidate.tags
        assert "renewable" in candidate.tags
        assert candidate.scope == "national"
        assert candidate.raw_data == scholarship

    def test_parse_scholarship_minimal(self):
        """Test parsing a scholarship with minimal data."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        scholarship = {
            "name": "Simple Grant",
            "organization": "Simple Org",
            "amount": "Varies",
        }

        candidate = connector._parse_scholarship(scholarship, fetched_at=now)

        assert candidate.title == "Simple Grant"
        assert candidate.org_name == "Simple Org"
        assert "scholarships" in candidate.tags
        assert "renewable" not in candidate.tags

    def test_parse_scholarship_no_name(self):
        """Test parsing a scholarship without name returns None."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        scholarship = {
            "organization": "Test Org",
            "amount": "$1,000",
        }

        candidate = connector._parse_scholarship(scholarship, fetched_at=now)
        assert candidate is None

    def test_parse_scholarship_no_organization(self):
        """Test parsing a scholarship without organization returns None."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        scholarship = {
            "name": "Test Scholarship",
            "amount": "$1,000",
        }

        candidate = connector._parse_scholarship(scholarship, fetched_at=now)
        assert candidate is None

    def test_parse_aggregator_basic(self):
        """Test parsing an aggregator site entry."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        aggregator = {
            "name": "Military Scholarship Finder",
            "description": "Search database of military scholarships.",
            "website": "https://example.com/search",
        }

        candidate = connector._parse_aggregator(aggregator, fetched_at=now)

        assert "Scholarship Search Tool" in candidate.title
        assert "aggregator" in candidate.tags
        assert "scholarship-search" in candidate.tags
        assert candidate.source_url == "https://example.com/search"

    def test_parse_aggregator_no_name(self):
        """Test parsing an aggregator without name returns None."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        aggregator = {
            "description": "A description",
            "website": "https://example.com",
        }

        candidate = connector._parse_aggregator(aggregator, fetched_at=now)
        assert candidate is None

    def test_parse_aggregator_no_website(self):
        """Test parsing an aggregator without website returns None."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        aggregator = {
            "name": "Test Finder",
            "description": "A description",
        }

        candidate = connector._parse_aggregator(aggregator, fetched_at=now)
        assert candidate is None

    def test_build_description_full(self):
        """Test description building with all fields."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            base_description="A great scholarship for Veterans.",
            amount="Up to $10,000 per year",
            deadline="February (annual)",
            renewable=True,
            notes="Highly prestigious program.",
        )

        assert "A great scholarship for Veterans" in desc
        assert "Up to $10,000 per year" in desc
        assert "(renewable)" in desc
        assert "February (annual)" in desc
        assert "Highly prestigious program" in desc

    def test_build_description_minimal(self):
        """Test description building with minimal fields."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            base_description="",
            amount="$500",
            deadline="",
            renewable=False,
            notes="",
        )

        assert "$500" in desc
        assert "(renewable)" not in desc

    def test_build_eligibility_single(self):
        """Test eligibility text with single requirement."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility(["Veterans of all branches"])

        assert "Veterans of all branches" in elig
        assert "complete eligibility requirements" in elig

    def test_build_eligibility_multiple(self):
        """Test eligibility text with multiple requirements."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility(
            [
                "Veterans of all branches",
                "Active duty service members",
                "Spouses of Veterans",
            ]
        )

        assert "Veterans of all branches" in elig
        assert "Active duty service members" in elig
        assert "Spouses of Veterans" in elig

    def test_build_eligibility_empty(self):
        """Test eligibility text with no requirements."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        elig = connector._build_eligibility([])

        assert "Veterans and military community members" in elig

    def test_build_tags_va_program(self):
        """Test tags for VA programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="U.S. Department of Veterans Affairs",
            eligibility_list=["Veterans"],
            renewable=False,
            amount="$5,000",
        )

        assert "va-program" in tags
        assert "scholarships" in tags
        assert "education" in tags

    def test_build_tags_vfw(self):
        """Test tags for VFW programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="VFW (Veterans of Foreign Wars)",
            eligibility_list=["Combat Veterans"],
            renewable=False,
            amount="$5,000",
        )

        assert "vfw" in tags

    def test_build_tags_american_legion(self):
        """Test tags for American Legion programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="The American Legion",
            eligibility_list=["Children of Veterans"],
            renewable=True,
            amount="$20,000",
        )

        assert "american-legion" in tags
        assert "renewable" in tags
        assert "high-value" in tags
        assert "military-children" in tags

    def test_build_tags_dav(self):
        """Test tags for DAV programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="Disabled American Veterans (DAV)",
            eligibility_list=["Disabled Veterans"],
            renewable=False,
            amount="$3,000",
        )

        assert "dav" in tags
        assert "disabled-veteran" in tags

    def test_build_tags_pat_tillman(self):
        """Test tags for Pat Tillman programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="Pat Tillman Foundation",
            eligibility_list=["Veterans", "Spouses"],
            renewable=True,
            amount="$10,000",
        )

        assert "pat-tillman" in tags
        assert "renewable" in tags
        assert "high-value" in tags
        assert "military-spouse" in tags

    def test_build_tags_folds_of_honor(self):
        """Test tags for Folds of Honor programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="Folds of Honor",
            eligibility_list=["Spouses and children of fallen service members"],
            renewable=True,
            amount="$5,000",
        )

        assert "folds-of-honor" in tags
        assert "gold-star-family" in tags
        assert "military-children" in tags
        assert "military-spouse" in tags

    def test_build_tags_stem(self):
        """Test tags for STEM programs."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="VA",
            eligibility_list=["Veterans in STEM programs"],
            renewable=False,
            amount="$30,000",
        )

        assert "stem" in tags
        assert "high-value" in tags

    def test_build_tags_branch_specific(self):
        """Test branch-specific tags."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        # Marine Corps
        tags = connector._build_tags(
            organization="Marine Corps Scholarship Foundation",
            eligibility_list=["Children of Marines and Navy Corpsmen"],
            renewable=True,
            amount="$5,000",
        )
        assert "marines" in tags
        assert "navy" in tags

        # Army
        tags = connector._build_tags(
            organization="Army Women's Foundation",
            eligibility_list=["Women who served in Army"],
            renewable=False,
            amount="$2,000",
        )
        assert "army" in tags

        # Air Force
        tags = connector._build_tags(
            organization="Air Force Aid Society",
            eligibility_list=["Dependents of Air Force members"],
            renewable=True,
            amount="$3,000",
        )
        assert "air-force" in tags

        # Coast Guard
        tags = connector._build_tags(
            organization="Coast Guard Foundation",
            eligibility_list=["Children of Coast Guard members"],
            renewable=True,
            amount="$3,000",
        )
        assert "coast-guard" in tags

    def test_build_tags_active_duty(self):
        """Test active duty tags."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="Test Foundation",
            eligibility_list=["Active duty service members"],
            renewable=False,
            amount="$5,000",
        )

        assert "active-duty" in tags

    def test_build_tags_no_duplicates(self):
        """Test that tags list has no duplicates."""
        connector = ScholarshipsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="VA Program",
            eligibility_list=["Veterans", "Veterans of all branches"],
            renewable=True,
            amount="$10,000",
        )

        assert len(tags) == len(set(tags))

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = ScholarshipsConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "Veteran scholarships data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        test_data = {
            "source": "Test",
            "scholarships": [
                {
                    "name": "Test Scholarship A",
                    "organization": "Org A",
                    "amount": "$5,000",
                    "deadline": "March 15",
                    "eligibility": ["Veterans"],
                    "description": "Test description",
                    "website": "https://a.com",
                    "renewable": True,
                },
                {
                    "name": "Test Scholarship B",
                    "organization": "Org B",
                    "amount": "$1,000",
                    "eligibility": ["Active duty"],
                    "website": "https://b.com",
                    "renewable": False,
                },
            ],
            "aggregator_sites": [
                {
                    "name": "Test Finder",
                    "description": "Find scholarships",
                    "website": "https://finder.com",
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = ScholarshipsConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 3  # 2 scholarships + 1 aggregator

        # First scholarship
        assert resources[0].title == "Test Scholarship A"
        assert "education" in resources[0].categories
        assert "renewable" in resources[0].tags

        # Second scholarship
        assert resources[1].title == "Test Scholarship B"
        assert "renewable" not in resources[1].tags

        # Aggregator
        assert "Scholarship Search Tool" in resources[2].title
        assert "aggregator" in resources[2].tags

    def test_run_skips_invalid_entries(self, tmp_path):
        """Test that run() skips entries without required fields."""
        test_data = {
            "scholarships": [
                {"name": "Valid Scholarship", "organization": "Valid Org"},
                {"name": "No Org"},  # Missing organization
                {"organization": "No Name"},  # Missing name
                {"name": "Also Valid", "organization": "Also Valid Org"},
            ],
            "aggregator_sites": [
                {"name": "Valid Finder", "website": "https://finder.com"},
                {"name": "No Website"},  # Missing website
                {"website": "https://no-name.com"},  # Missing name
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = ScholarshipsConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 3  # 2 valid scholarships + 1 valid aggregator
        titles = [r.title for r in resources]
        assert "Valid Scholarship" in titles
        assert "Also Valid" in titles

    def test_run_with_real_data(self):
        """Test run() with the actual veteran scholarships data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        # Should have multiple scholarships and aggregators
        assert len(resources) >= 20

        # All should be education category
        assert all("education" in r.categories for r in resources)

        # All should have scholarships tag
        assert all("scholarships" in r.tags for r in resources)

        # Check for expected scholarships
        titles = {r.title for r in resources}
        assert "Pat Tillman Foundation Scholars Program" in titles
        assert "Folds of Honor Scholarship" in titles
        assert "VFW Sport Clips Help A Hero Scholarship" in titles
        assert "American Legion Legacy Scholarship" in titles
        assert "Edith Nourse Rogers STEM Scholarship" in titles

        # Check resource structure
        first = resources[0]
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.scope == "national"

    def test_categories_are_education(self):
        """Test that all scholarship resources are education category."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.categories == ["education"]

    def test_all_have_scholarships_tag(self):
        """Test that all resources have scholarships tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert "scholarships" in resource.tags, f"{resource.title} missing scholarships tag"

    def test_aggregators_have_aggregator_tag(self):
        """Test that aggregator resources have aggregator tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        aggregators = [r for r in resources if "Search Tool" in r.title]
        assert len(aggregators) >= 1

        for agg in aggregators:
            assert "aggregator" in agg.tags
            assert "scholarship-search" in agg.tags

    def test_renewable_scholarships_have_tag(self):
        """Test that renewable scholarships have the tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            raw = resource.raw_data
            if raw and raw.get("renewable", False):
                assert "renewable" in resource.tags, f"{resource.title} missing renewable tag"

    def test_high_value_scholarships_have_tag(self):
        """Test that high value scholarships have the tag."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "veteran_scholarships.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("veteran_scholarships.json not found in project")

        connector = ScholarshipsConnector(data_path=data_file)
        resources = connector.run()

        # Find high-value scholarships (>=$10K)
        high_value_names = [
            "Pat Tillman Foundation Scholars Program",
            "American Legion Legacy Scholarship",
            "Edith Nourse Rogers STEM Scholarship",
        ]

        for resource in resources:
            if resource.title in high_value_names:
                assert "high-value" in resource.tags, f"{resource.title} missing high-value tag"
