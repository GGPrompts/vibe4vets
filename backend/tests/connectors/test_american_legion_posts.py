"""Tests for American Legion posts connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.american_legion_posts import AmericanLegionPostsConnector


class TestAmericanLegionPostsConnector:
    """Tests for AmericanLegionPostsConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "American Legion Post Locator"
        assert meta.tier == 2  # Established nonprofit VSO
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "mylegion.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = AmericanLegionPostsConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = AmericanLegionPostsConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_with_name(self):
        """Test title building with post name."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        title = connector._build_title(
            post_number="43",
            post_name="Hollywood Post 43",
            city="Los Angeles",
            state="CA",
        )

        assert title == "American Legion Hollywood Post 43 (Los Angeles, CA)"

    def test_build_title_without_name(self):
        """Test title building without post name."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        title = connector._build_title(
            post_number="99",
            post_name=None,
            city="San Francisco",
            state="CA",
        )

        assert title == "American Legion Post 99 (San Francisco, CA)"

    def test_build_title_post_in_name(self):
        """Test title building when name already includes 'post'."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        title = connector._build_title(
            post_number="1",
            post_name="Paris Post 1",
            city="Paris",
            state="TX",
        )

        assert title == "American Legion Paris Post 1 (Paris, TX)"

    def test_build_title_no_city(self):
        """Test title building without city."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        title = connector._build_title(
            post_number="100",
            post_name=None,
            city=None,
            state="TX",
        )

        assert title == "American Legion Post 100 (TX)"

    def test_build_description_with_programs(self):
        """Test description building with programs."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        description = connector._build_description(
            post_number="43",
            post_name="Hollywood Post 43",
            city="Los Angeles",
            state_name="California",
            attributes=["Hall Rental"],
            programs=["Baseball", "Boys State", "Legion Riders"],
        )

        assert "American Legion Post 43 (Hollywood Post 43)" in description
        assert "Los Angeles, California" in description
        assert "American Legion Baseball" in description
        assert "Boys State" in description
        assert "American Legion Riders" in description
        assert "Hall Rental" in description

    def test_build_description_without_programs(self):
        """Test description building without programs."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        description = connector._build_description(
            post_number="99",
            post_name=None,
            city="San Francisco",
            state_name="California",
            attributes=[],
            programs=[],
        )

        assert "American Legion Post 99" in description
        assert "San Francisco, California" in description
        assert "largest wartime veterans service organization" in description

    def test_build_eligibility(self):
        """Test eligibility text."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility()

        assert "membership is open" in eligibility
        assert "December 7, 1941" in eligibility
        assert "honorably discharged" in eligibility
        assert "free VA claims assistance" in eligibility
        assert "regardless of Legion membership" in eligibility

    def test_build_how_to_apply_with_phone(self):
        """Test how to apply with phone."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            post_number="43",
            post_name="Hollywood Post 43",
            phone="(323) 851-3227",
            email="info@hollywoodlegion.com",
            website="https://hollywoodlegion.com",
        )

        assert "Call American Legion Hollywood Post 43" in how_to_apply
        assert "(323) 851-3227" in how_to_apply
        assert "Email: info@hollywoodlegion.com" in how_to_apply
        assert "https://hollywoodlegion.com" in how_to_apply
        assert "https://www.legion.org/join" in how_to_apply

    def test_build_how_to_apply_email_only(self):
        """Test how to apply with email only."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            post_number="99",
            post_name=None,
            phone=None,
            email="post99@legion.org",
            website=None,
        )

        assert "Email American Legion Post 99" in how_to_apply
        assert "post99@legion.org" in how_to_apply

    def test_build_how_to_apply_no_contact(self):
        """Test how to apply with no contact info."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            post_number="100",
            post_name=None,
            phone=None,
            email=None,
            website=None,
        )

        assert "Contact American Legion Post 100" in how_to_apply
        assert "https://www.legion.org/join" in how_to_apply

    def test_build_tags_basic(self):
        """Test basic tags."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="CA",
            attributes=[],
            programs=[],
        )

        assert "american-legion" in tags
        assert "vso" in tags
        assert "veterans-service-organization" in tags
        assert "community" in tags
        assert "peer-support" in tags
        assert "state-ca" in tags

    def test_build_tags_with_programs(self):
        """Test tags with programs."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="TX",
            attributes=["Canteen", "Hall Rental"],
            programs=["Baseball", "Boys State", "Girls State", "Legion Riders"],
        )

        assert "american-legion" in tags
        assert "state-tx" in tags
        assert "club-room" in tags
        assert "hall-rental" in tags
        assert "event-space" in tags
        assert "legion-baseball" in tags
        assert "boys-state" in tags
        assert "girls-state" in tags
        assert "legion-riders" in tags
        assert "youth-programs" in tags
        assert "motorcycle-group" in tags

    def test_build_tags_with_family_programs(self):
        """Test tags with family programs."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            state="VA",
            attributes=[],
            programs=["Sons of The American Legion", "American Legion Auxiliary"],
        )

        assert "sons-of-the-american-legion" in tags
        assert "american-legion-auxiliary" in tags
        assert "family-programs" in tags

    def test_parse_post_full_data(self, tmp_path):
        """Test parsing a post with full data."""
        test_data = {
            "posts": [
                {
                    "post_number": "43",
                    "post_name": "Hollywood Post 43",
                    "address": "2035 N Highland Ave",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip_code": "90068",
                    "phone": "(323) 851-3227",
                    "email": "info@hollywoodlegion.com",
                    "website": "https://hollywoodlegion.com",
                    "department": "California",
                    "attributes": ["Hall Rental"],
                    "programs": ["Baseball", "Boys State", "Legion Riders"],
                    "lat": 34.1054,
                    "lng": -118.3388,
                }
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        r = resources[0]

        assert r.title == "American Legion Hollywood Post 43 (Los Angeles, CA)"
        assert r.org_name == "American Legion Hollywood Post 43"
        assert r.address == "2035 N Highland Ave, Los Angeles, CA 90068"
        assert r.city == "Los Angeles"
        assert r.state == "CA"
        assert r.zip_code == "90068"
        assert r.phone == "(323) 851-3227"
        assert r.email == "info@hollywoodlegion.com"
        assert r.source_url == "https://hollywoodlegion.com"
        assert r.org_website == "https://hollywoodlegion.com"
        assert r.categories == ["benefits", "supportServices"]
        assert r.scope == "local"
        assert r.states == ["CA"]
        assert "american-legion" in r.tags
        assert "legion-baseball" in r.tags
        assert r.raw_data["post_number"] == "43"
        assert r.raw_data["lat"] == 34.1054

    def test_parse_post_minimal_data(self, tmp_path):
        """Test parsing a post with minimal data."""
        test_data = {
            "posts": [
                {
                    "post_number": "99",
                    "state": "CA",
                }
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        r = resources[0]

        assert r.title == "American Legion Post 99 (CA)"
        assert r.org_name == "American Legion Post 99"
        assert r.state == "CA"
        assert r.categories == ["benefits", "supportServices"]

    def test_parse_post_skip_missing_data(self, tmp_path):
        """Test that posts without required data are skipped."""
        test_data = {
            "posts": [
                {"post_number": "99"},  # Missing state
                {"state": "CA"},  # Missing post_number
                {"post_number": "100", "state": "TX"},  # Valid
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].raw_data["post_number"] == "100"

    def test_run_nonexistent_file(self, tmp_path):
        """Test running with nonexistent file."""
        connector = AmericanLegionPostsConnector(data_path=tmp_path / "nonexistent.json")
        resources = connector.run()

        assert resources == []

    def test_run_empty_posts(self, tmp_path):
        """Test running with empty posts array."""
        test_data = {"posts": []}
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert resources == []

    def test_context_manager(self, tmp_path):
        """Test connector context manager."""
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps({"posts": []}))

        with AmericanLegionPostsConnector(data_path=test_file) as connector:
            resources = connector.run()

        assert resources == []

    def test_phone_normalization(self, tmp_path):
        """Test phone number normalization."""
        test_data = {
            "posts": [
                {
                    "post_number": "1",
                    "state": "TX",
                    "phone": "9037856792",  # No formatting
                },
                {
                    "post_number": "2",
                    "state": "VA",
                    "phone": "1-571-312-6703",  # With country code
                },
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert resources[0].phone == "(903) 785-6792"
        assert resources[1].phone == "(571) 312-6703"

    def test_categories_are_benefits_and_support(self):
        """Test that categories are benefits and supportServices."""
        connector = AmericanLegionPostsConnector(data_path="/fake/path.json")
        # Access metadata to verify this is the expected pattern
        meta = connector.metadata
        assert meta.tier == 2

        # Test with actual resource

        now = datetime.now(UTC)
        resource = connector._parse_post(
            {"post_number": "1", "state": "TX"},
            fetched_at=now,
        )

        assert resource.categories == ["benefits", "supportServices"]

    def test_scope_is_local(self, tmp_path):
        """Test that all posts have local scope."""
        test_data = {
            "posts": [
                {"post_number": "1", "state": "TX"},
                {"post_number": "2", "state": "CA"},
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        for r in resources:
            assert r.scope == "local"

    def test_address_building_variations(self, tmp_path):
        """Test address building with various data combinations."""
        test_data = {
            "posts": [
                {
                    "post_number": "1",
                    "state": "TX",
                    "address": "123 Main St",
                    "city": "Dallas",
                    "zip_code": "75201",
                },
                {
                    "post_number": "2",
                    "state": "CA",
                    "address": "456 Oak Ave",
                    "city": "Los Angeles",
                    # No zip_code
                },
                {
                    "post_number": "3",
                    "state": "NY",
                    "address": "789 Pine Blvd",
                    # No city or zip
                },
            ]
        }
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = AmericanLegionPostsConnector(data_path=test_file)
        resources = connector.run()

        assert resources[0].address == "123 Main St, Dallas, TX 75201"
        assert resources[1].address == "456 Oak Ave, Los Angeles, CA"
        assert resources[2].address == "789 Pine Blvd"

    def test_with_real_data_file(self):
        """Test loading the actual reference data file."""
        connector = AmericanLegionPostsConnector()
        resources = connector.run()

        # Should have sample posts from the reference file
        assert len(resources) > 0

        # All should have required fields
        for r in resources:
            assert r.title
            assert r.description
            assert r.categories == ["benefits", "supportServices"]
            assert r.scope == "local"
            assert r.states
            assert "american-legion" in r.tags
