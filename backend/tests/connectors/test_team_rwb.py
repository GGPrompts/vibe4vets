"""Tests for Team Red White & Blue chapters connector."""

import json
from pathlib import Path

import pytest

from connectors.team_rwb import TeamRWBConnector


class TestTeamRWBConnector:
    """Tests for TeamRWBConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = TeamRWBConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Team Red White & Blue Chapters"
        assert meta.tier == 2  # Established nonprofit
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "teamrwb.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = TeamRWBConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = TeamRWBConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_chapter(self):
        """Test title building for chapter."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="Austin",
            chapter_type="chapter",
            city="Austin",
            state="TX",
        )

        assert "Team RWB" in title
        assert "Austin" in title
        assert "Chapter" in title

    def test_build_title_chapter_different_name(self):
        """Test title building for chapter with name different from city."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="Huntsville / Redstone Arsenal",
            chapter_type="chapter",
            city="Huntsville / Redstone Arsenal",
            state="AL",
        )

        assert "Team RWB" in title
        assert "Huntsville" in title
        assert "Chapter" in title

    def test_build_title_state_group(self):
        """Test title building for state group."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="TX",
            chapter_type="state",
            city=None,
            state="TX",
        )

        assert "Team RWB" in title
        assert "Texas" in title

    def test_build_description_chapter(self):
        """Test description building for chapter."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        description = connector._build_description(
            name="Austin",
            chapter_type="chapter",
            city="Austin",
            state_name="Texas",
            api_description="Welcome to Austin chapter!",
        )

        assert "Austin" in description
        assert "Texas" in description
        assert "fitness" in description.lower()
        assert "community" in description.lower()
        assert "free" in description.lower()

    def test_build_description_state(self):
        """Test description building for state group."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        description = connector._build_description(
            name="TX",
            chapter_type="state",
            city=None,
            state_name="Texas",
            api_description="Welcome to Texas!",
        )

        assert "Texas" in description
        assert "fitness" in description.lower() or "activities" in description.lower()

    def test_build_eligibility(self):
        """Test eligibility description."""
        connector = TeamRWBConnector(data_path="/fake/path.json")
        eligibility = connector._build_eligibility()

        assert "veteran" in eligibility.lower()
        assert "free" in eligibility.lower()
        assert "service member" in eligibility.lower()
        assert "family" in eligibility.lower()

    def test_build_how_to_apply_with_email(self):
        """Test how to apply with email contact."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            name="Austin",
            email="austin@teamrwb.org",
            website="https://members.teamrwb.org/groups/12345",
        )

        assert "austin@teamrwb.org" in how_to_apply
        assert "members.teamrwb.org" in how_to_apply
        assert "app" in how_to_apply.lower()

    def test_build_how_to_apply_no_contact(self):
        """Test how to apply without email."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            name="Test Chapter",
            email=None,
            website=None,
        )

        assert "teamrwb.org" in how_to_apply
        assert "app" in how_to_apply.lower()

    def test_build_tags_chapter(self):
        """Test tag building for chapter."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        tags = connector._build_tags(chapter_type="chapter", state="TX")

        assert "team-rwb" in tags
        assert "peer-support" in tags
        assert "fitness" in tags
        assert "community" in tags
        assert "local-chapter" in tags
        assert "state-tx" in tags
        assert "running" in tags

    def test_build_tags_state(self):
        """Test tag building for state group."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        tags = connector._build_tags(chapter_type="state", state="CA")

        assert "team-rwb" in tags
        assert "state-coordination" in tags
        assert "state-ca" in tags
        assert "local-chapter" not in tags

    def test_run_with_sample_data(self, tmp_path):
        """Test running connector with sample data."""
        test_data = {
            "source": "Team Red White & Blue",
            "chapters": [
                {
                    "storepoint_id": 12345,
                    "name": "Austin",
                    "chapter_type": "chapter",
                    "city": "Austin",
                    "state": "TX",
                    "zip_code": "78701",
                    "latitude": 30.267,
                    "longitude": -97.743,
                    "email": "austin@teamrwb.org",
                    "phone": None,
                    "website": "https://members.teamrwb.org/groups/8549",
                    "description": "Welcome to Team RWB Austin!",
                },
                {
                    "storepoint_id": 12346,
                    "name": "TX",
                    "chapter_type": "state",
                    "city": None,
                    "state": "TX",
                    "zip_code": "78701",
                    "latitude": 30.267,
                    "longitude": -97.743,
                    "email": "texas@teamrwb.org",
                    "phone": None,
                    "website": "https://members.teamrwb.org/groups/texas",
                    "description": "Welcome to Team RWB Texas!",
                },
            ],
        }

        test_file = tmp_path / "team_rwb_chapters.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = TeamRWBConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # Check chapter
        chapter = resources[0]
        assert "Austin" in chapter.title
        assert chapter.city == "Austin"
        assert chapter.state == "TX"
        assert chapter.email == "austin@teamrwb.org"
        assert chapter.categories == ["supportServices", "mentalHealth"]
        assert chapter.scope == "local"
        assert chapter.states == ["TX"]
        assert "team-rwb" in chapter.tags

        # Check state group
        state_group = resources[1]
        assert "Texas" in state_group.title
        assert state_group.state == "TX"
        assert "state-coordination" in state_group.tags

    def test_run_all_have_required_fields(self, tmp_path):
        """Test that all resources have required fields."""
        test_data = {
            "source": "Team Red White & Blue",
            "chapters": [
                {
                    "storepoint_id": i,
                    "name": f"Chapter {i}",
                    "chapter_type": "chapter",
                    "city": f"City {i}",
                    "state": "CA",
                    "zip_code": "90001",
                    "latitude": 34.0,
                    "longitude": -118.0,
                    "email": f"chapter{i}@teamrwb.org",
                    "phone": None,
                    "website": f"https://members.teamrwb.org/groups/{i}",
                    "description": f"Welcome to Chapter {i}!",
                }
                for i in range(5)
            ],
        }

        test_file = tmp_path / "team_rwb_chapters.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = TeamRWBConnector(data_path=test_file)
        resources = connector.run()

        for r in resources:
            assert r.title, "Title is required"
            assert r.description, "Description is required"
            assert r.source_url, "Source URL is required"
            assert r.org_name, "Org name is required"
            assert r.categories, "Categories are required"
            assert r.tags, "Tags are required"
            assert r.eligibility, "Eligibility is required"
            assert r.how_to_apply, "How to apply is required"
            assert r.fetched_at, "Fetched at is required"

    def test_run_categories_correct(self, tmp_path):
        """Test that categories are supportServices and mentalHealth."""
        test_data = {
            "source": "Team Red White & Blue",
            "chapters": [
                {
                    "storepoint_id": 1,
                    "name": "Test Chapter",
                    "chapter_type": "chapter",
                    "city": "Test City",
                    "state": "TX",
                    "zip_code": "78701",
                    "latitude": 30.0,
                    "longitude": -97.0,
                    "email": "test@teamrwb.org",
                    "phone": None,
                    "website": "https://members.teamrwb.org/groups/1",
                    "description": "Welcome!",
                },
            ],
        }

        test_file = tmp_path / "team_rwb_chapters.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        connector = TeamRWBConnector(data_path=test_file)
        resources = connector.run()

        assert resources[0].categories == ["supportServices", "mentalHealth"]

    def test_run_file_not_found(self, tmp_path):
        """Test error when data file not found."""
        connector = TeamRWBConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError):
            connector.run()

    def test_context_manager(self, tmp_path):
        """Test context manager usage."""
        test_data = {"source": "Test", "chapters": []}
        test_file = tmp_path / "test.json"
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        with TeamRWBConnector(data_path=test_file) as connector:
            resources = connector.run()
            assert resources == []

    def test_org_name_building(self):
        """Test organization name building variations."""
        connector = TeamRWBConnector(data_path="/fake/path.json")

        # Chapter with name
        org_name = connector._build_org_name(
            name="Austin",
            chapter_type="chapter",
            city="Austin",
            state="TX",
        )
        assert org_name == "Team RWB Austin"

        # State group
        org_name = connector._build_org_name(
            name="TX",
            chapter_type="state",
            city=None,
            state="TX",
        )
        assert org_name == "Team RWB Texas"

        # Fallback to city
        org_name = connector._build_org_name(
            name=None,
            chapter_type="chapter",
            city="Houston",
            state="TX",
        )
        assert org_name == "Team RWB Houston"

    def test_run_with_production_data(self):
        """Test running connector with actual production data file."""
        connector = TeamRWBConnector()  # Uses default path

        # Skip if file doesn't exist (e.g., CI environment)
        if not connector.data_path.exists():
            pytest.skip("Production data file not available")

        resources = connector.run()

        # Should have 150+ chapters based on research
        assert len(resources) >= 150

        # All should have proper categories
        for r in resources:
            assert "supportServices" in r.categories
            assert "mentalHealth" in r.categories
            assert "team-rwb" in r.tags

        # Should have mix of chapters and state groups
        chapters = [r for r in resources if r.raw_data.get("chapter_type") == "chapter"]
        states = [r for r in resources if r.raw_data.get("chapter_type") == "state"]

        assert len(chapters) >= 100, "Should have at least 100 local chapters"
        assert len(states) >= 30, "Should have at least 30 state groups"
