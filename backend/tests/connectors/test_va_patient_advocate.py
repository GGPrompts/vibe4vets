"""Tests for VA Patient Advocate connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.va_patient_advocate import VAPatientAdvocateConnector


class TestVAPatientAdvocateConnector:
    """Tests for VAPatientAdvocateConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "VA Patient Advocate Program"
        assert meta.tier == 1  # Official VA program
        assert meta.frequency == "quarterly"
        assert meta.requires_auth is False
        assert "va.gov" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = VAPatientAdvocateConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = VAPatientAdvocateConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title(self):
        """Test title building."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        title = connector._build_title(
            facility_name="VA Boston Healthcare System",
            state="MA",
        )

        assert title == "Patient Advocate - VA Boston Healthcare System"

    def test_build_title_no_state(self):
        """Test title building without state."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        title = connector._build_title(
            facility_name="VA Medical Center",
            state=None,
        )

        assert title == "Patient Advocate - VA Medical Center"

    def test_build_description(self):
        """Test description building."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            facility_name="VA Boston Healthcare System",
            city="Boston",
            state="MA",
        )

        assert "VA Boston Healthcare System" in desc
        assert "Boston, Massachusetts" in desc
        assert "Patient Advocates" in desc
        assert "resolve concerns" in desc

    def test_build_description_no_city(self):
        """Test description building without city."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            facility_name="VA Medical Center",
            city=None,
            state="TX",
        )

        assert "Texas" in desc

    def test_build_eligibility(self):
        """Test eligibility text."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")
        elig = connector._build_eligibility()

        assert "veterans" in elig.lower()
        assert "families" in elig.lower()
        assert "VA health care" in elig
        assert "No enrollment" in elig

    def test_build_how_to_apply_with_all_contacts(self):
        """Test how to apply with all contact info."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            facility_name="VA Boston Healthcare System",
            phone="857-364-4796",
            toll_free="800-865-3384",
            email="VABostonPatientAdvocate@va.gov",
            complaint_steps=[
                "Contact your Patient Advocate",
                "Explain your concern",
            ],
            escalation_contacts={
                "national_hotline": "1-800-827-1000",
                "white_house_hotline": "1-855-948-2311",
                "ask_va_portal": "https://ask.va.gov/",
            },
        )

        assert "857-364-4796" in how_to_apply
        assert "800-865-3384" in how_to_apply
        assert "VABostonPatientAdvocate@va.gov" in how_to_apply
        assert "Complaint Process" in how_to_apply
        assert "1. Contact your Patient Advocate" in how_to_apply
        assert "1-800-827-1000" in how_to_apply
        assert "White House VA Hotline" in how_to_apply

    def test_build_how_to_apply_minimal(self):
        """Test how to apply with minimal info."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            facility_name="VA Medical Center",
            phone=None,
            toll_free=None,
            email=None,
            complaint_steps=[],
            escalation_contacts={},
        )

        assert "VA Medical Center" in how_to_apply
        assert "business hours" in how_to_apply

    def test_build_tags(self):
        """Test tag building."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            {
                "facility_id": "vha_523",
                "visn": "1",
            }
        )

        assert "patient-advocate" in tags
        assert "complaints" in tags
        assert "va-health-care" in tags
        assert "facility-vha_523" in tags
        assert "visn-1" in tags

    def test_build_tags_no_ids(self):
        """Test tag building without facility/visn IDs."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")

        tags = connector._build_tags({})

        assert "patient-advocate" in tags
        assert "complaints" in tags
        # Should not have facility or visn tags
        assert not any(t.startswith("facility-") for t in tags)
        assert not any(t.startswith("visn-") for t in tags)

    def test_parse_advocate(self):
        """Test parsing an advocate entry."""
        connector = VAPatientAdvocateConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        candidate = connector._parse_advocate(
            advocate={
                "facility_name": "VA Boston Healthcare System",
                "facility_id": "vha_523",
                "state": "MA",
                "city": "Boston",
                "address": "1400 VFW Parkway",
                "zip_code": "02132",
                "phone": "857-364-4796",
                "toll_free": "800-865-3384",
                "email": "VABostonPatientAdvocate@va.gov",
                "hours": "Monday-Friday 8:00 AM - 4:30 PM",
                "visn": "1",
            },
            complaint_steps=["Step 1", "Step 2"],
            escalation_contacts={"national_hotline": "1-800-827-1000"},
            fetched_at=now,
        )

        assert "Patient Advocate" in candidate.title
        assert "VA Boston Healthcare System" in candidate.title
        assert candidate.org_name == "VA Boston Healthcare System"
        assert candidate.city == "Boston"
        assert candidate.state == "MA"
        assert candidate.zip_code == "02132"
        assert candidate.phone == "(857) 364-4796"
        assert candidate.email == "VABostonPatientAdvocate@va.gov"
        assert candidate.hours == "Monday-Friday 8:00 AM - 4:30 PM"
        assert candidate.categories == ["legal"]
        assert "patient-advocate" in candidate.tags
        assert candidate.scope == "local"
        assert candidate.states == ["MA"]
        assert candidate.raw_data["facility_id"] == "vha_523"

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = VAPatientAdvocateConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "VA Patient Advocate data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses the JSON correctly."""
        test_data = {
            "source": "VA Patient Advocate Program",
            "advocates": [
                {
                    "facility_name": "VA Boston Healthcare System",
                    "facility_id": "vha_523",
                    "state": "MA",
                    "city": "Boston",
                    "address": "1400 VFW Parkway",
                    "zip_code": "02132",
                    "phone": "857-364-4796",
                    "toll_free": "800-865-3384",
                    "email": "VABostonPatientAdvocate@va.gov",
                    "hours": "Monday-Friday 8:00 AM - 4:30 PM",
                    "visn": "1",
                },
                {
                    "facility_name": "VA Connecticut Healthcare System",
                    "facility_id": "vha_689",
                    "state": "CT",
                    "city": "West Haven",
                    "phone": "203-932-5711",
                    "visn": "1",
                },
            ],
            "complaint_process": {
                "steps": [
                    "Contact your Patient Advocate at your local VA Medical Center",
                    "Explain your concern",
                ],
                "escalation_contacts": {
                    "national_hotline": "1-800-827-1000",
                },
            },
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VAPatientAdvocateConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource
        assert "VA Boston Healthcare System" in resources[0].title
        assert resources[0].states == ["MA"]
        assert resources[0].phone == "(857) 364-4796"
        assert resources[0].email == "VABostonPatientAdvocate@va.gov"
        assert "patient-advocate" in resources[0].tags

        # Second resource
        assert "VA Connecticut Healthcare System" in resources[1].title
        assert resources[1].states == ["CT"]

    def test_run_with_real_data(self):
        """Test run() with the actual patient advocates data file."""
        # Find the data file
        current = Path(__file__).resolve().parent
        while current != current.parent:
            data_file = current / "data" / "reference" / "va_patient_advocates.json"
            if data_file.exists():
                break
            current = current.parent

        if not data_file.exists():
            pytest.skip("va_patient_advocates.json not found in project")

        connector = VAPatientAdvocateConnector(data_path=data_file)
        resources = connector.run()

        # Should have many patient advocate resources
        assert len(resources) >= 100  # We have ~170 in the data file

        # All should be in legal category (complaints/grievances)
        assert all("legal" in r.categories for r in resources)

        # All should have patient-advocate tag
        assert all("patient-advocate" in r.tags for r in resources)

        # Check that phone numbers are normalized
        for r in resources:
            if r.phone:
                # Should be formatted like (XXX) XXX-XXXX
                assert "(" in r.phone or r.phone.startswith("+")

        # Check that complaint process is in how_to_apply
        first = resources[0]
        assert "Complaint Process" in first.how_to_apply
        assert "VA National Hotline" in first.how_to_apply

    def test_context_manager(self):
        """Test connector can be used as context manager."""
        with VAPatientAdvocateConnector(data_path="/fake/path.json") as connector:
            assert connector.metadata.name == "VA Patient Advocate Program"

    def test_state_coverage(self, tmp_path):
        """Test that resources properly include state information."""
        test_data = {
            "advocates": [
                {
                    "facility_name": "Test VAMC",
                    "state": "TX",
                    "city": "Houston",
                },
            ],
            "complaint_process": {
                "steps": [],
                "escalation_contacts": {},
            },
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VAPatientAdvocateConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].state == "TX"
        assert resources[0].states == ["TX"]
        assert resources[0].scope == "local"

    def test_missing_optional_fields(self, tmp_path):
        """Test handling of missing optional fields."""
        test_data = {
            "advocates": [
                {
                    "facility_name": "Minimal VAMC",
                    # Missing: state, city, address, phone, email, hours
                },
            ],
            "complaint_process": {
                "steps": [],
                "escalation_contacts": {},
            },
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data))

        connector = VAPatientAdvocateConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 1
        assert resources[0].org_name == "Minimal VAMC"
        assert resources[0].state is None
        assert resources[0].phone is None
        assert resources[0].email is None
