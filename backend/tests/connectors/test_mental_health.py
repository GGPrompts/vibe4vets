"""Tests for Mental Health Resources connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.mental_health import MentalHealthConnector


class TestMentalHealthConnector:
    """Tests for MentalHealthConnector."""

    def test_metadata(self, tmp_path):
        """Test connector metadata."""
        connector = MentalHealthConnector(data_path=tmp_path / "mental_health.json")
        meta = connector.metadata

        assert "Mental Health" in meta.name
        assert meta.tier == 2
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "mentalhealth.va.gov" in meta.url

    def test_run_no_file(self, tmp_path):
        """Test that run() returns empty list when no data file exists."""
        connector = MentalHealthConnector(data_path=tmp_path / "nonexistent.json")

        resources = connector.run()
        assert resources == []

    def test_run_empty_resources(self, tmp_path):
        """Test that run() handles empty resources list."""
        data = {"metadata": {"source": "test"}, "resources": []}
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        assert resources == []

    def test_run_parses_crisis_resource(self, tmp_path):
        """Test parsing a crisis line resource."""
        data = {
            "metadata": {"source": "test"},
            "resources": [
                {
                    "org_name": "Veterans Crisis Line",
                    "program_name": "24/7 Crisis Support",
                    "service_type": "crisis",
                    "website": "https://www.veteranscrisisline.net/",
                    "phone": "988",
                    "phone_instructions": "Dial 988, then press 1",
                    "text": "838255",
                    "description": "The Veterans Crisis Line connects veterans in crisis.",
                    "hours": "24/7/365",
                    "cost": "free",
                    "delivery": ["phone", "text", "chat"],
                    "specialties": ["suicide-prevention", "crisis-intervention"],
                    "eligibility": {
                        "summary": "All veterans and service members",
                        "enrollment_required": False,
                        "service_era": "any",
                    },
                    "how_to_access": "Call 988 and press 1.",
                }
            ],
        }
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert resource.title == "Veterans Crisis Line - 24/7 Crisis Support"
        assert resource.org_name == "Veterans Crisis Line"
        assert "veterans in crisis" in resource.description.lower()
        assert resource.phone == "988"
        assert "housing" in resource.categories
        assert "crisis" in resource.tags
        assert "suicide-prevention" in resource.tags
        assert "24-7" in resource.tags
        assert "free" in resource.tags
        assert resource.scope == "national"

    def test_run_parses_therapy_resource(self, tmp_path):
        """Test parsing a therapy provider resource."""
        data = {
            "metadata": {"source": "test"},
            "resources": [
                {
                    "org_name": "The Headstrong Project",
                    "program_name": "Veteran Mental Health Treatment",
                    "service_type": "therapy",
                    "website": "https://theheadstrongproject.org/",
                    "description": "Confidential, barrier-free PTSD treatment.",
                    "cost": "free",
                    "cost_notes": "30 cost-free sessions per trauma type",
                    "delivery": ["in-person", "telehealth"],
                    "states_in_person": ["CA", "NY", "TX"],
                    "specialties": ["ptsd", "depression", "anxiety", "trauma"],
                    "therapies_offered": ["CPT", "EMDR", "Prolonged Exposure"],
                    "eligibility": {
                        "summary": "Veterans of all eras regardless of discharge status",
                        "enrollment_required": False,
                        "service_era": "any",
                    },
                    "how_to_access": "Fill out a form at theheadstrongproject.org.",
                    "impact": "44,000+ free sessions in 2024",
                }
            ],
        }
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert resource.title == "The Headstrong Project - Veteran Mental Health Treatment"
        assert "PTSD treatment" in resource.description
        assert "30 cost-free sessions" in resource.description
        assert "therapy" in resource.tags
        assert "ptsd" in resource.tags
        assert "telehealth" in resource.tags
        assert "free" in resource.tags
        assert "headstrong" in resource.tags
        assert "cpt" in resource.tags
        assert "emdr" in resource.tags
        assert resource.states == ["CA", "NY", "TX"]

    def test_run_parses_peer_support_resource(self, tmp_path):
        """Test parsing a peer support resource."""
        data = {
            "metadata": {"source": "test"},
            "resources": [
                {
                    "org_name": "Wounded Warrior Project",
                    "program_name": "WWP Talk",
                    "service_type": "peer-support",
                    "website": "https://www.woundedwarriorproject.org/programs/wwp-talk",
                    "phone": "888-997-2586",
                    "description": "Non-clinical goal-setting program via weekly phone calls.",
                    "cost": "free",
                    "delivery": ["phone"],
                    "specialties": ["emotional-support", "goal-setting"],
                    "eligibility": {
                        "summary": "Post-9/11 wounded veterans and family members",
                        "service_era": "post-9/11",
                    },
                    "how_to_access": "Contact WWP Resource Center.",
                }
            ],
        }
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "WWP" in resource.title
        assert resource.phone == "(888) 997-2586"  # Normalized
        assert "peer-support" in resource.tags
        assert "post-9/11" in resource.tags
        assert "family-support" in resource.tags
        assert "wwp" in resource.tags

    def test_run_parses_recreation_resource(self, tmp_path):
        """Test parsing a recreation/wellness resource."""
        data = {
            "metadata": {"source": "test"},
            "resources": [
                {
                    "org_name": "Team Red, White & Blue",
                    "program_name": "Chapter and Community Program",
                    "service_type": "recreation",
                    "website": "https://teamrwb.org/",
                    "description": "Veterans unite through fitness and social events.",
                    "cost": "free",
                    "delivery": ["in-person"],
                    "location_count": 200,
                    "specialties": ["fitness", "social-connection", "community"],
                    "eligibility": {
                        "summary": "Open to all veterans, service members, and supporters",
                        "enrollment_required": False,
                    },
                    "how_to_access": "Download the Team RWB app.",
                }
            ],
        }
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        assert len(resources) == 1
        resource = resources[0]

        assert "Team RWB" in resource.title
        assert "recreation" in resource.tags
        assert "fitness" in resource.tags
        assert "social-connection" in resource.tags
        assert "team-rwb" in resource.tags
        assert resource.scope == "national"

    def test_build_title_abbreviations(self, tmp_path):
        """Test that organization names are abbreviated correctly."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        # Wounded Warrior Project -> WWP
        title = connector._build_title("Wounded Warrior Project", "Project Odyssey")
        assert title == "WWP - Project Odyssey"

        # Team Red, White & Blue -> Team RWB
        title = connector._build_title("Team Red, White & Blue", "Chapter Program")
        assert title == "Team RWB - Chapter Program"

        # VA Mental Health Services -> VA
        title = connector._build_title("VA Mental Health Services", "PTSD Treatment")
        assert title == "VA - PTSD Treatment"

        # Unknown org stays as-is
        title = connector._build_title("Some Other Org", "Some Program")
        assert title == "Some Other Org - Some Program"

    def test_build_description_with_cost(self, tmp_path):
        """Test description building includes cost information."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        # Free service
        resource = {
            "description": "Base description.",
            "cost": "free",
            "delivery": ["in-person"],
        }
        desc = connector._build_description(resource)
        assert "no cost" in desc.lower()

        # Sliding scale
        resource = {
            "description": "Base description.",
            "cost": "sliding-scale",
            "delivery": ["in-person"],
        }
        desc = connector._build_description(resource)
        assert "sliding scale" in desc.lower()

    def test_build_description_with_delivery(self, tmp_path):
        """Test description includes delivery methods."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {
            "description": "Base description.",
            "delivery": ["in-person", "telehealth", "phone"],
        }
        desc = connector._build_description(resource)
        assert "in-person" in desc
        assert "telehealth" in desc.lower() or "video" in desc.lower()
        assert "phone" in desc

    def test_build_eligibility_complete(self, tmp_path):
        """Test building eligibility with all fields."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {
            "eligibility": {
                "summary": "Post-9/11 veterans",
                "service_era": "post-9/11",
                "enrollment_required": False,
                "disability_required": True,
                "disability_notes": "Must have combat injury",
            }
        }
        elig = connector._build_eligibility(resource)

        assert "Post-9/11 veterans" in elig
        assert "post-9/11" in elig.lower()
        assert "No VA enrollment" in elig
        assert "combat injury" in elig

    def test_build_eligibility_minimal(self, tmp_path):
        """Test building eligibility with minimal data."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {}
        elig = connector._build_eligibility(resource)

        assert "Contact the organization" in elig

    def test_build_how_to_apply(self, tmp_path):
        """Test building how to apply instructions."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {
            "how_to_access": "Call our hotline to get started.",
            "phone": "1-800-555-1234",
            "text": "12345",
            "hours": "24/7",
            "response_time": "Calls answered immediately",
        }
        how_to = connector._build_how_to_apply(resource)

        assert "Call our hotline" in how_to
        assert "Response time:" in how_to
        assert "Text: 12345" in how_to
        assert "Hours: 24/7" in how_to

    def test_build_tags_comprehensive(self, tmp_path):
        """Test comprehensive tag building."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {
            "service_type": "therapy",
            "cost": "free",
            "delivery": ["telehealth", "residential"],
            "hours": "24/7/365",
            "program_format": "2-week intensive residential retreat",
            "specialties": ["ptsd", "tbi", "mst"],
            "therapies_offered": ["CPT", "EMDR"],
            "eligibility": {
                "summary": "Post-9/11 veterans and family members",
                "service_era": "post-9/11",
                "disability_required": True,
            },
            "org_name": "Wounded Warrior Project",
        }
        tags = connector._build_tags(resource)

        assert "mental-health" in tags
        assert "therapy" in tags
        assert "free" in tags
        assert "telehealth" in tags
        assert "24-7" in tags
        assert "intensive-program" in tags
        assert "residential" in tags
        assert "retreat" in tags
        assert "ptsd" in tags
        assert "tbi" in tags
        assert "mst" in tags
        assert "cpt" in tags
        assert "emdr" in tags
        assert "post-9/11" in tags
        assert "disabled-veterans" in tags
        assert "family-support" in tags
        assert "wwp" in tags

    def test_determine_scope_national(self, tmp_path):
        """Test scope determination for national resources."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        # Phone-based national service
        resource = {"delivery": ["phone"], "location_notes": "Available nationwide"}
        assert connector._determine_scope(resource) == "national"

        # Many locations
        resource = {"location_count": 200}
        assert connector._determine_scope(resource) == "national"

    def test_determine_scope_with_states(self, tmp_path):
        """Test scope determination when states are specified."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        resource = {"states_in_person": ["CA", "NY", "TX"]}
        assert connector._determine_scope(resource) == "state"

    def test_phone_normalization(self, tmp_path):
        """Test phone number normalization."""
        connector = MentalHealthConnector(data_path=tmp_path / "test.json")

        # Regular phone number should be normalized
        assert connector._normalize_phone("8889972586") == "(888) 997-2586"
        assert connector._normalize_phone("1-888-997-2586") == "(888) 997-2586"

        # 988 should stay as-is (handled in _parse_resource)
        # The connector preserves 988 without normalization

    def test_run_with_real_data(self):
        """Test run() with the actual mental health resources data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "mental_health_resources.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("mental_health_resources.json not found in project")

        connector = MentalHealthConnector(data_path=data_file)
        resources = connector.run()

        # Should have 20+ resources from 6+ organizations
        assert len(resources) >= 20

        # All should have mental-health tag
        assert all("mental-health" in r.tags for r in resources)

        # Should have variety of service types
        service_types = {r.raw_data.get("service_type") for r in resources}
        assert "crisis" in service_types
        assert "therapy" in service_types
        assert "peer-support" in service_types
        assert "recreation" in service_types

        # Check required orgs are represented
        org_names = {r.org_name for r in resources}
        assert "Veterans Crisis Line" in org_names
        assert "Cohen Veterans Network" in org_names
        assert "Wounded Warrior Project" in org_names
        assert "Team Red, White & Blue" in org_names

        # Check first resource structure
        first = resources[0]
        assert first.title is not None
        assert first.description is not None
        assert first.source_url is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None
        assert first.categories is not None
        assert first.tags is not None

    def test_context_manager(self, tmp_path):
        """Test that connector works as context manager."""
        data = {"metadata": {"source": "test"}, "resources": []}
        data_file = tmp_path / "mental_health.json"
        data_file.write_text(json.dumps(data))

        with MentalHealthConnector(data_path=data_file) as connector:
            resources = connector.run()
            assert resources == []
