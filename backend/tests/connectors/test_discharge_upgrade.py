"""Tests for Discharge Upgrade connector."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from connectors.discharge_upgrade import DischargeUpgradeConnector


class TestDischargeUpgradeConnector:
    """Tests for DischargeUpgradeConnector."""

    def test_metadata(self):
        """Test connector metadata."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        meta = connector.metadata

        assert meta.name == "Discharge Upgrade Legal Resources"
        assert meta.tier == 2  # Established nonprofit/curated
        assert meta.frequency == "monthly"
        assert meta.requires_auth is False
        assert "vetsprobono.org" in meta.url

    def test_init_with_path(self, tmp_path):
        """Test initialization with explicit path."""
        test_file = tmp_path / "test.json"
        connector = DischargeUpgradeConnector(data_path=test_file)
        assert connector.data_path == test_file

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        test_file = str(tmp_path / "test.json")
        connector = DischargeUpgradeConnector(data_path=test_file)
        assert connector.data_path == Path(test_file)

    def test_build_title_legal_clinic(self):
        """Test title building for legal clinics."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="Veterans Consortium",
            resource_type="legal_clinic",
            state=None,
        )
        assert "Discharge Upgrade Legal Help" in title
        assert "Veterans Consortium" in title

    def test_build_title_with_state(self):
        """Test title building with state."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="Texas Veterans Legal",
            resource_type="legal_clinic",
            state="TX",
        )
        assert "Texas Veterans Legal" in title

    def test_build_title_educational(self):
        """Test title building for educational resources."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="Self-Help Guide",
            resource_type="educational_resource",
            state=None,
        )
        assert "Discharge Upgrade Guide" in title

    def test_build_title_directory(self):
        """Test title building for directories."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        title = connector._build_title(
            name="VA Accredited Search",
            resource_type="directory",
            state=None,
        )
        assert "Discharge Upgrade Directory" in title

    def test_build_description_free_clinic(self):
        """Test description building for free legal clinic."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Test Clinic",
            description="Provides legal help to veterans.",
            resource_type="legal_clinic",
            services=["drb-representation", "bcmr-representation", "pro-bono"],
            is_free=True,
            notes="Expert in PTSD cases.",
        )

        assert "Provides legal help to veterans" in desc
        assert "Discharge Review Board representation" in desc
        assert "Board for Correction of Military Records representation" in desc
        assert "free of charge" in desc
        assert "Expert in PTSD cases" in desc

    def test_build_description_paid_service(self):
        """Test description building for paid service."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        desc = connector._build_description(
            name="Private Attorney Network",
            description="Network of private attorneys.",
            resource_type="professional_organization",
            services=["referrals"],
            is_free=False,
            notes=None,
        )

        assert "may charge fees" in desc

    def test_build_eligibility_with_criteria(self):
        """Test eligibility text with specific criteria."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility(
            eligibility="Veterans with OTH discharge and PTSD diagnosis",
            is_free=True,
        )

        assert "Veterans with OTH discharge and PTSD diagnosis" in eligibility
        assert "free" in eligibility.lower()

    def test_build_eligibility_default(self):
        """Test eligibility text without specific criteria."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility(
            eligibility=None,
            is_free=True,
        )

        assert "Other Than Honorable" in eligibility
        assert "PTSD" in eligibility
        assert "free" in eligibility.lower()

    def test_build_eligibility_paid(self):
        """Test eligibility text for paid service."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        eligibility = connector._build_eligibility(
            eligibility="All veterans",
            is_free=False,
        )

        assert "may charge fees" in eligibility
        assert "Veterans Consortium or NVLSP" in eligibility

    def test_build_how_to_apply_full_contact(self):
        """Test how-to-apply with all contact info."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            name="Test Clinic",
            website="https://example.org",
            intake_url="https://example.org/apply",
            phone="555-123-4567",
            email="help@example.org",
        )

        assert "Contact Test Clinic" in how_to_apply
        assert "https://example.org/apply" in how_to_apply
        assert "555-123-4567" in how_to_apply
        assert "help@example.org" in how_to_apply
        assert "DD-214" in how_to_apply

    def test_build_how_to_apply_minimal(self):
        """Test how-to-apply with minimal info."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        how_to_apply = connector._build_how_to_apply(
            name="Test Clinic",
            website="https://example.org",
            intake_url=None,
            phone=None,
            email=None,
        )

        assert "Contact Test Clinic" in how_to_apply
        assert "https://example.org" in how_to_apply
        assert "DD-214" in how_to_apply

    def test_build_tags_free_clinic(self):
        """Test tag building for free legal clinic."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            resource_type="legal_clinic",
            services=["drb-representation", "bcmr-representation", "pro-bono"],
            scope="national",
            is_free=True,
            state=None,
        )

        assert "discharge-upgrade" in tags
        assert "military-law" in tags
        assert "legal" in tags
        assert "pro-bono" in tags
        assert "free-legal-services" in tags
        assert "legal-clinic" in tags
        assert "drb" in tags
        assert "bcmr" in tags
        assert "nationwide" in tags

    def test_build_tags_state_specific(self):
        """Test tag building with state."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            resource_type="legal_clinic",
            services=["discharge-upgrade", "va-benefits"],
            scope="state",
            is_free=True,
            state="TX",
        )

        assert "state-tx" in tags
        assert "va-benefits" in tags
        assert "nationwide" not in tags

    def test_build_tags_educational(self):
        """Test tag building for educational resource."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        tags = connector._build_tags(
            resource_type="educational_resource",
            services=["self-help", "educational"],
            scope="national",
            is_free=True,
            state=None,
        )

        assert "self-help" in tags
        assert "educational" in tags

    def test_parse_resource_legal_clinic(self):
        """Test parsing a legal clinic resource."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        resource = {
            "id": "test-clinic",
            "name": "Test Veterans Legal Clinic",
            "type": "legal_clinic",
            "description": "Provides free legal help for discharge upgrades.",
            "services": ["discharge-upgrade", "pro-bono", "drb-representation"],
            "eligibility": "Veterans with OTH discharge",
            "website": "https://testvlc.org",
            "intake_url": "https://testvlc.org/apply",
            "phone": "555-123-4567",
            "city": "San Francisco",
            "state": "CA",
            "scope": "local",
            "free": True,
            "notes": "Expert in PTSD cases",
        }

        candidate = connector._parse_resource(resource, fetched_at=now)

        assert "Test Veterans Legal Clinic" in candidate.title
        assert "discharge upgrades" in candidate.description
        assert candidate.org_name == "Test Veterans Legal Clinic"
        assert candidate.org_website == "https://testvlc.org"
        assert candidate.categories == ["legal"]
        assert candidate.scope == "local"
        assert candidate.states == ["CA"]
        assert candidate.state == "CA"
        assert candidate.city == "San Francisco"
        assert "discharge-upgrade" in candidate.tags
        assert "pro-bono" in candidate.tags
        assert "drb" in candidate.tags
        assert candidate.raw_data["resource_id"] == "test-clinic"
        assert candidate.raw_data["is_free"] is True

    def test_parse_resource_educational(self):
        """Test parsing an educational resource."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        resource = {
            "id": "self-help-guide",
            "name": "Discharge Upgrade Self-Help Guide",
            "type": "educational_resource",
            "description": "Step-by-step guide for discharge upgrade applications.",
            "services": ["educational", "self-help"],
            "website": "https://example.org/guide",
            "scope": "national",
            "free": True,
        }

        candidate = connector._parse_resource(resource, fetched_at=now)

        assert "Discharge Upgrade Guide" in candidate.title
        assert candidate.scope == "national"
        assert "self-help" in candidate.tags
        assert "educational" in candidate.tags
        assert "nationwide" in candidate.tags

    def test_run_file_not_found(self, tmp_path):
        """Test that run() raises FileNotFoundError for missing file."""
        connector = DischargeUpgradeConnector(data_path=tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError) as exc_info:
            connector.run()

        assert "Discharge upgrade data file not found" in str(exc_info.value)

    def test_run_parses_json(self, tmp_path):
        """Test that run() parses JSON correctly."""
        data = {
            "source": "Test source",
            "resources": [
                {
                    "id": "clinic1",
                    "name": "Veterans Consortium",
                    "type": "legal_clinic",
                    "description": "National pro bono program.",
                    "services": ["discharge-upgrade", "pro-bono"],
                    "website": "https://vetsprobono.org",
                    "scope": "national",
                    "free": True,
                },
                {
                    "id": "clinic2",
                    "name": "Texas Legal Aid",
                    "type": "legal_clinic",
                    "description": "Texas-based legal aid.",
                    "services": ["discharge-upgrade"],
                    "website": "https://texaslegal.org",
                    "state": "TX",
                    "scope": "state",
                    "free": True,
                },
            ],
        }

        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(data))

        connector = DischargeUpgradeConnector(data_path=test_file)
        resources = connector.run()

        assert len(resources) == 2

        # First resource (national)
        assert "Veterans Consortium" in resources[0].title
        assert resources[0].scope == "national"
        assert resources[0].states is None

        # Second resource (state-specific)
        assert "Texas Legal Aid" in resources[1].title
        assert resources[1].scope == "state"
        assert resources[1].states == ["TX"]
        assert "state-tx" in resources[1].tags

    def test_run_with_real_data(self):
        """Test run() with the actual discharge upgrade data file."""
        # Find the data file
        data_file: Path | None = None
        current = Path(__file__).resolve().parent
        while current != current.parent:
            candidate = current / "data" / "reference" / "discharge_upgrade_resources.json"
            if candidate.exists():
                data_file = candidate
                break
            current = current.parent

        if data_file is None:
            pytest.skip("discharge_upgrade_resources.json not found in project")
            return

        connector = DischargeUpgradeConnector(data_path=data_file)
        resources = connector.run()

        # Should have multiple resources
        assert len(resources) >= 10

        # All should be legal category
        for r in resources:
            assert r.categories is not None
            assert "legal" in r.categories

        # All should have discharge-upgrade tag
        for r in resources:
            assert r.tags is not None
            assert "discharge-upgrade" in r.tags

        # Check resource structure
        first = resources[0]
        assert first.title is not None
        assert first.description is not None
        assert first.eligibility is not None
        assert first.how_to_apply is not None

        # Should have mix of scopes
        scopes = {r.scope for r in resources}
        assert "national" in scopes

        # Check for key programs
        names = [r.org_name for r in resources]
        # Veterans Consortium should be present
        assert any("veterans consortium" in name.lower() for name in names)
        # NVLSP should be present
        assert any("nvlsp" in name.lower() for name in names)

    def test_phone_normalization(self):
        """Test that phone numbers are normalized."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        resource = {
            "id": "test",
            "name": "Test",
            "type": "legal_clinic",
            "description": "Test",
            "phone": "5551234567",
            "scope": "national",
            "free": True,
        }

        candidate = connector._parse_resource(resource, fetched_at=now)

        # Phone should be normalized to (555) 123-4567
        assert candidate.phone == "(555) 123-4567"

    def test_resource_types(self):
        """Test that all resource types are handled correctly."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")

        resource_types = [
            "legal_clinic",
            "referral_network",
            "online_resource",
            "directory",
            "professional_organization",
            "educational_resource",
            "grant_program",
            "va_program",
            "government_board",
        ]

        for rtype in resource_types:
            title = connector._build_title(
                name="Test Resource",
                resource_type=rtype,
                state=None,
            )
            assert title is not None
            assert len(title) > 0

    def test_empty_services_list(self):
        """Test handling of empty services list."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        resource = {
            "id": "test",
            "name": "Test Resource",
            "type": "educational_resource",
            "description": "Test description",
            "services": [],
            "scope": "national",
            "free": True,
        }

        candidate = connector._parse_resource(resource, fetched_at=now)

        # Should still have base tags
        assert "discharge-upgrade" in candidate.tags
        assert "military-law" in candidate.tags
        assert "legal" in candidate.tags

    def test_raw_data_contains_expected_fields(self):
        """Test that raw_data contains expected fields."""
        connector = DischargeUpgradeConnector(data_path="/fake/path.json")
        now = datetime.now(UTC)

        resource = {
            "id": "test-id",
            "name": "Test",
            "type": "legal_clinic",
            "description": "Test",
            "services": ["pro-bono"],
            "intake_url": "https://example.org/intake",
            "notes": "Test notes",
            "scope": "national",
            "free": True,
        }

        candidate = connector._parse_resource(resource, fetched_at=now)

        assert candidate.raw_data["resource_id"] == "test-id"
        assert candidate.raw_data["resource_type"] == "legal_clinic"
        assert candidate.raw_data["services"] == ["pro-bono"]
        assert candidate.raw_data["is_free"] is True
        assert candidate.raw_data["intake_url"] == "https://example.org/intake"
        assert candidate.raw_data["notes"] == "Test notes"
