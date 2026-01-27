"""Tests for Veterans Service Organization (VSO) Post Locator connector."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.vso_post_locator import VSOPostLocatorConnector


class TestVSOPostLocatorConnector:
    """Tests for VSOPostLocatorConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "VSO Post Locator (VFW, American Legion, DAV)"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "vfw.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = VSOPostLocatorConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = VSOPostLocatorConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_parse_post_vfw_full_data(self):
        """Test parsing a VFW post with all fields."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_post(
            organization="VFW",
            post_name="Post 76",
            post_number="76",
            address="401 Veterans Memorial Drive",
            city="Austin",
            state="TX",
            zip_code="78701",
            phone="(512) 472-1876",
            email="vfwpost76austin@gmail.com",
            website="https://www.vfwpost76.org",
            services=["VA claims assistance", "Service officer", "Community events"],
            meeting_schedule="First Tuesday of each month at 7:00 PM",
            hours="Wed-Sat 4:00 PM - 12:00 AM",
            fetched_at=now,
        )

        assert "VFW" in candidate.title
        assert "Post 76" in candidate.title
        assert "Austin" in candidate.title
        assert "TX" in candidate.title
        assert "peer support" in candidate.description.lower()
        assert "VFW" in candidate.description
        assert candidate.org_website == "https://www.vfwpost76.org"
        assert candidate.address == "401 Veterans Memorial Drive, Austin, TX 78701"
        assert candidate.city == "Austin"
        assert candidate.state == "TX"
        assert candidate.zip_code == "78701"
        assert candidate.phone == "(512) 472-1876"
        assert candidate.email == "vfwpost76austin@gmail.com"
        assert candidate.hours == "Wed-Sat 4:00 PM - 12:00 AM"
        assert candidate.categories == ["community"]
        assert candidate.scope == "local"
        assert candidate.states == ["TX"]
        assert "vso" in candidate.tags
        assert "vfw" in candidate.tags
        assert "peer-support" in candidate.tags
        assert candidate.raw_data["organization"] == "VFW"
        assert candidate.raw_data["post_number"] == "76"
        assert "First Tuesday" in candidate.raw_data["meeting_schedule"]

    def test_parse_post_american_legion(self):
        """Test parsing an American Legion post."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_post(
            organization="American Legion",
            post_name="Post 1",
            post_number="1",
            address="5400 E Yale Avenue",
            city="Denver",
            state="CO",
            zip_code="80222",
            phone="(303) 759-8801",
            email="legionpost1denver@comcast.net",
            website="https://post1denver.com",
            services=["VA claims assistance", "Boys State program", "Scholarship programs"],
            meeting_schedule="Second Thursday of each month at 7:00 PM",
            hours="Tue-Sun 11:00 AM - 10:00 PM",
            fetched_at=now,
        )

        assert "American Legion" in candidate.title
        assert "Post 1" in candidate.title
        assert "Denver" in candidate.title
        assert "The American Legion" in candidate.description
        assert "american-legion" in candidate.tags
        assert candidate.states == ["CO"]

    def test_parse_post_dav(self):
        """Test parsing a DAV chapter."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_post(
            organization="DAV",
            post_name="Chapter 5",
            post_number="5",
            address="6401 Wenzel Road",
            city="San Antonio",
            state="TX",
            zip_code="78233",
            phone="(210) 658-1234",
            email="davalamo5@gmail.com",
            website="https://davalamo5.org",
            services=["VA claims assistance", "Transportation to VA", "Peer support"],
            meeting_schedule="Third Friday of each month at 10:00 AM",
            hours="By appointment",
            fetched_at=now,
        )

        assert "DAV" in candidate.title
        assert "Chapter 5" in candidate.title
        assert "DAV" in candidate.description
        assert "dav" in candidate.tags
        assert "disabled-american-veterans" in candidate.tags
        assert "transportation-assistance" in candidate.tags

    def test_parse_post_minimal_data(self):
        """Test parsing a post with minimal data."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_post(
            organization="VFW",
            post_name=None,
            post_number="123",
            address=None,
            city=None,
            state="CA",
            zip_code=None,
            phone=None,
            email=None,
            website=None,
            services=[],
            meeting_schedule=None,
            hours=None,
            fetched_at=now,
        )

        assert "VFW" in candidate.title
        assert "Post 123" in candidate.title
        assert candidate.address is None
        assert candidate.phone is None
        assert "vso" in candidate.tags
        assert "vfw" in candidate.tags

    def test_parse_post_no_organization(self):
        """Test parsing a post without organization specified."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_post(
            organization=None,
            post_name="Test Post",
            post_number="999",
            address="123 Main St",
            city="Anytown",
            state="TX",
            zip_code="12345",
            phone="555-1234",
            email=None,
            website=None,
            services=[],
            meeting_schedule=None,
            hours=None,
            fetched_at=now,
        )

        # Without organization, falls back to generic title
        assert "Veterans Service Organization" in candidate.title or "Test Post" in candidate.org_name
        assert "vso" in candidate.tags

    def test_build_title_variations(self):
        """Test title building with various inputs."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        # VFW with post name
        title = connector._build_title(
            organization="VFW",
            post_name="Post 76",
            post_number="76",
            city="Austin",
            state="TX",
        )
        assert "VFW" in title
        assert "Post 76" in title
        assert "Austin" in title
        assert "TX" in title

        # American Legion without post name
        title = connector._build_title(
            organization="American Legion",
            post_name=None,
            post_number="123",
            city="Denver",
            state="CO",
        )
        assert "American Legion" in title
        assert "Post 123" in title

        # DAV chapter
        title = connector._build_title(
            organization="DAV",
            post_name=None,
            post_number="5",
            city="San Antonio",
            state="TX",
        )
        assert "DAV" in title
        assert "Chapter 5" in title

    def test_build_description(self):
        """Test description building."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        from connectors.vso_post_locator import VSO_ORGANIZATIONS

        desc = connector._build_description(
            organization="VFW",
            org_info=VSO_ORGANIZATIONS["VFW"],
            post_name="Post 76",
            post_number="76",
            city="Austin",
            state_name="Texas",
            services=["VA claims assistance", "Honor guard"],
            meeting_schedule="First Tuesday at 7 PM",
        )

        assert "Austin" in desc
        assert "Texas" in desc
        assert "VFW" in desc
        # Description includes the organization description which mentions VFW's purpose
        assert "largest" in desc or "oldest" in desc or "war veterans" in desc.lower()
        assert "VA claims assistance" in desc
        assert "Honor guard" in desc
        assert "First Tuesday at 7 PM" in desc

    def test_build_eligibility_vfw(self):
        """Test eligibility for VFW."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        from connectors.vso_post_locator import VSO_ORGANIZATIONS

        eligibility = connector._build_eligibility(
            organization="VFW",
            org_info=VSO_ORGANIZATIONS["VFW"],
            state_name="Texas",
        )

        assert "VFW" in eligibility
        assert "overseas" in eligibility.lower() or "foreign" in eligibility.lower()
        assert "all veterans" in eligibility.lower() or "regardless of membership" in eligibility.lower()

    def test_build_eligibility_dav(self):
        """Test eligibility for DAV."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")
        from connectors.vso_post_locator import VSO_ORGANIZATIONS

        eligibility = connector._build_eligibility(
            organization="DAV",
            org_info=VSO_ORGANIZATIONS["DAV"],
            state_name="California",
        )

        assert "DAV" in eligibility
        assert "service-connected" in eligibility.lower() or "disabled" in eligibility.lower()

    def test_build_how_to_apply_with_phone(self):
        """Test how_to_apply with phone number."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            organization="VFW",
            post_name="Post 76",
            phone="(512) 472-1876",
            email="vfw76@example.com",
            website="https://vfwpost76.org",
            meeting_schedule="First Tuesday at 7 PM",
        )

        assert "(512) 472-1876" in instructions
        assert "vfw76@example.com" in instructions
        assert "https://vfwpost76.org" in instructions
        assert "First Tuesday at 7 PM" in instructions

    def test_build_how_to_apply_email_only(self):
        """Test how_to_apply with email only."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            organization="American Legion",
            post_name="Post 1",
            phone=None,
            email="legion@example.com",
            website=None,
            meeting_schedule=None,
        )

        assert "Email" in instructions
        assert "legion@example.com" in instructions

    def test_build_how_to_apply_no_contact(self):
        """Test how_to_apply without contact info."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        instructions = connector._build_how_to_apply(
            organization="DAV",
            post_name=None,
            phone=None,
            email=None,
            website=None,
            meeting_schedule=None,
        )

        assert "Contact" in instructions

    def test_build_tags(self):
        """Test tag building."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="VFW",
            state="TX",
            services=["VA claims assistance", "Honor guard", "Scholarship programs"],
        )

        assert "vso" in tags
        assert "veterans-service-organization" in tags
        assert "vfw" in tags
        assert "veterans-of-foreign-wars" in tags
        assert "peer-support" in tags
        assert "state-tx" in tags
        assert "va-claims-assistance" in tags

    def test_build_tags_american_legion(self):
        """Test tag building for American Legion."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="American Legion",
            state="CO",
            services=["Employment assistance"],
        )

        assert "american-legion" in tags
        assert "employment-services" in tags

    def test_build_tags_dav(self):
        """Test tag building for DAV."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            organization="DAV",
            state="CA",
            services=["Transportation to VA", "Benefits counseling"],
        )

        assert "dav" in tags
        assert "disabled-american-veterans" in tags
        assert "transportation-assistance" in tags
        assert "benefits-assistance" in tags

    def test_normalize_phone(self):
        """Test phone number normalization."""
        connector = VSOPostLocatorConnector(data_path="/fake/path.json")

        # 10-digit phone
        assert connector._normalize_phone("5124721876") == "(512) 472-1876"

        # 11-digit with leading 1
        assert connector._normalize_phone("15124721876") == "(512) 472-1876"

        # Already formatted
        assert connector._normalize_phone("(512) 472-1876") == "(512) 472-1876"

        # With dashes
        assert connector._normalize_phone("512-472-1876") == "(512) 472-1876"

        # None
        assert connector._normalize_phone(None) is None

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = VSOPostLocatorConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "VSO posts data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON file correctly."""
        import json

        test_data = {
            "source": "Test",
            "posts": [
                {
                    "organization": "VFW",
                    "post_name": "Post 76",
                    "post_number": "76",
                    "address": "401 Veterans Memorial Drive",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78701",
                    "phone": "(512) 472-1876",
                    "email": "vfw76@example.com",
                    "website": "https://vfwpost76.org",
                    "services": ["VA claims assistance"],
                    "meeting_schedule": "First Tuesday at 7 PM",
                    "hours": "Wed-Sat 4 PM - 12 AM",
                },
                {
                    "organization": "American Legion",
                    "post_name": "Post 1",
                    "post_number": "1",
                    "address": "5400 E Yale Avenue",
                    "city": "Denver",
                    "state": "CO",
                    "zip_code": "80222",
                    "phone": "(303) 759-8801",
                    "email": None,
                    "website": None,
                    "services": ["Boys State program"],
                    "meeting_schedule": "Second Thursday at 7 PM",
                    "hours": None,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VSOPostLocatorConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource - VFW
        assert "VFW" in resources[0].title
        assert resources[0].states == ["TX"]
        assert resources[0].scope == "local"
        assert resources[0].city == "Austin"

        # Second resource - American Legion
        assert "American Legion" in resources[1].title
        assert resources[1].states == ["CO"]
        assert resources[1].city == "Denver"

    def test_run_with_real_data(self):
        """Test run() with the actual VSO posts data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vso_posts.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vso_posts.json not found in project")

        connector = VSOPostLocatorConnector(data_path=data_file)
        resources = connector.run()

        # Should have at least 10 posts (acceptance criteria)
        assert len(resources) >= 10

        # All should be local scope
        assert all(r.scope == "local" for r in resources)

        # All should have vso tag
        assert all("vso" in r.tags for r in resources)

        # All should have community category
        assert all(r.categories == ["community"] for r in resources)

        # Check for expected organizations
        orgs = {r.raw_data.get("organization") for r in resources}
        assert "VFW" in orgs
        assert "American Legion" in orgs
        assert "DAV" in orgs

        # Check resource structure
        first = resources[0]
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.state is not None

    def test_all_posts_have_community_category(self):
        """Test that all VSO post resources have community category."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vso_posts.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vso_posts.json not found in project")

        connector = VSOPostLocatorConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            assert resource.categories == ["community"]
            assert "vso" in resource.tags
            assert "peer-support" in resource.tags

    def test_phone_numbers_normalized(self):
        """Test that phone numbers are properly normalized."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vso_posts.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vso_posts.json not found in project")

        connector = VSOPostLocatorConnector(data_path=data_file)
        resources = connector.run()

        import re

        phone_pattern = re.compile(r"^\(\d{3}\) \d{3}-\d{4}$")

        for resource in resources:
            if resource.phone:
                assert phone_pattern.match(resource.phone), f"Phone not normalized: {resource.phone}"

    def test_websites_are_valid_urls(self):
        """Test that website URLs are valid."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vso_posts.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vso_posts.json not found in project")

        connector = VSOPostLocatorConnector(data_path=data_file)
        resources = connector.run()

        for resource in resources:
            if resource.org_website:
                assert resource.org_website.startswith(("http://", "https://")), f"Invalid URL: {resource.org_website}"

    def test_meeting_schedules_included(self):
        """Test that meeting schedules are included in raw data."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "vso_posts.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("vso_posts.json not found in project")

        connector = VSOPostLocatorConnector(data_path=data_file)
        resources = connector.run()

        # At least some posts should have meeting schedules
        posts_with_schedules = [r for r in resources if r.raw_data.get("meeting_schedule")]
        assert len(posts_with_schedules) > 0, "No posts have meeting schedules"

        # Check that schedules contain expected keywords
        for resource in posts_with_schedules:
            schedule = resource.raw_data["meeting_schedule"].lower()
            # Should mention day or frequency
            assert any(
                word in schedule
                for word in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "month"]
            ), f"Invalid meeting schedule format: {resource.raw_data['meeting_schedule']}"

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        import json

        test_data = {"posts": []}
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        with VSOPostLocatorConnector(data_path=test_file) as connector:
            resources = connector.run()
            assert resources == []
