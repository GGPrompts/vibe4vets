"""Military OneSource transition assistance connector.

Loads Military OneSource programs and services from reference data file.
Military OneSource is DoD's free, confidential counseling and transition
support program for service members, veterans (within 365 days), and families.

Source: https://www.militaryonesource.mil/
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class MilitaryOneSourceConnector(BaseConnector):
    """Connector for Military OneSource transition assistance resources.

    This connector loads curated Military OneSource program data from a YAML
    reference file. Programs include transition counseling, TAP support,
    career coaching, financial counseling, MilTax, and family support services.

    Eligibility varies by program but generally includes:
    - Active duty service members (all branches)
    - National Guard and Reserve members
    - Retirees
    - Veterans within 365 days of separation
    - Family members (for many programs)
    """

    # Default path to reference data file
    DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "reference" / "military_onesource.yaml"

    # Military OneSource main contact info
    PHONE = "1-800-342-9647"
    WEBSITE = "https://www.militaryonesource.mil/"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Optional path to YAML data file. Falls back to default location.
        """
        self.data_path = Path(data_path) if data_path else self.DEFAULT_DATA_PATH
        if not self.data_path.exists():
            # Try relative to environment variable if set
            env_data_dir = os.environ.get("VIBE4VETS_DATA_DIR")
            if env_data_dir:
                self.data_path = Path(env_data_dir) / "reference" / "military_onesource.yaml"

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Military OneSource",
            url="https://www.militaryonesource.mil/",
            tier=1,  # Official DoD program
            frequency="monthly",
            terms_url="https://www.militaryonesource.mil/about-us/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Load Military OneSource programs from reference data.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []

        if not self.data_path.exists():
            print(f"Warning: Military OneSource data file not found at {self.data_path}")
            return resources

        try:
            with open(self.data_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            programs = data.get("programs", [])
            source_info = data.get("source", {})

            for program in programs:
                candidate = self._parse_program(program, source_info)
                if candidate:
                    resources.append(candidate)

        except yaml.YAMLError as e:
            print(f"Error parsing Military OneSource YAML: {e}")
        except OSError as e:
            print(f"Error reading Military OneSource file: {e}")

        return resources

    def _parse_program(self, program: dict[str, Any], source_info: dict[str, Any]) -> ResourceCandidate | None:
        """Parse a program entry into a ResourceCandidate.

        Args:
            program: Program data from YAML file.
            source_info: Source metadata from YAML file.

        Returns:
            ResourceCandidate or None if required fields are missing.
        """
        name = program.get("name")
        if not name:
            return None

        # Build comprehensive description
        description = self._build_description(program)

        # Build eligibility text
        eligibility = self._build_eligibility(program)

        # Build how to apply text
        how_to_apply = self._build_how_to_apply(program, source_info)

        # Extract tags
        tags = self._extract_tags(program)

        # Determine category
        category = program.get("category", "training")
        if category not in ["employment", "training", "housing", "legal"]:
            category = "training"

        # Get source URL (program-specific or main site)
        source_url = program.get("source_url", self.WEBSITE)

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=source_url,
            org_name="Military OneSource",
            org_website=self.WEBSITE,
            # National program - no specific location
            address=None,
            city=None,
            state=None,
            zip_code=None,
            categories=[category],
            tags=tags,
            phone=self.PHONE,
            email=None,
            hours="24/7/365",
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=None,  # Available nationwide
            raw_data=program,
            fetched_at=datetime.now(UTC),
        )

    def _build_description(self, program: dict[str, Any]) -> str:
        """Build a comprehensive description from program data.

        Args:
            program: Program data dictionary.

        Returns:
            Formatted description string.
        """
        parts = []

        # Start with base description
        base_desc = program.get("description", "")
        if base_desc:
            # Clean up YAML multiline string formatting
            parts.append(base_desc.strip().replace("\n", " "))

        # Add organization context if not already mentioned
        if parts and "Military OneSource" not in parts[0]:
            parts.insert(
                0,
                "Military OneSource provides free, confidential support for military families.",
            )

        return " ".join(parts)

    def _build_eligibility(self, program: dict[str, Any]) -> str:
        """Build eligibility text from program data.

        Args:
            program: Program data dictionary.

        Returns:
            Eligibility description string.
        """
        eligibility_list = program.get("eligibility", [])
        who_qualifies = program.get("who_qualifies", {})

        if eligibility_list:
            # Use explicit eligibility list
            if len(eligibility_list) == 1:
                return eligibility_list[0]
            return " ".join(eligibility_list)

        # Build from who_qualifies flags
        if who_qualifies:
            groups = []
            if who_qualifies.get("active_duty"):
                groups.append("active duty service members (all branches)")
            if who_qualifies.get("reserve"):
                groups.append("Reserve component members")
            if who_qualifies.get("national_guard"):
                groups.append("National Guard members")
            if who_qualifies.get("retirees"):
                groups.append("military retirees")
            if who_qualifies.get("veterans_365_days"):
                groups.append("veterans within 365 days of separation")
            if who_qualifies.get("family"):
                groups.append("eligible family members")

            if groups:
                return f"Eligible: {', '.join(groups)}."

        return "Service members, veterans, and their families."

    def _build_how_to_apply(self, program: dict[str, Any], source_info: dict[str, Any]) -> str:
        """Build application instructions from program data.

        Args:
            program: Program data dictionary.
            source_info: Source contact information.

        Returns:
            Application instructions string.
        """
        parts = []

        # Add program-specific instructions if available
        how_to = program.get("how_to_apply")
        if how_to:
            parts.append(how_to.strip().replace("\n", " "))

        # Ensure contact info is included
        contact = source_info.get("contact", {})
        phone = contact.get("phone_display", self.PHONE)

        if parts and phone not in parts[0]:
            parts.append(f"Contact Military OneSource at {phone} (24/7/365).")
        elif not parts:
            parts.append(
                f"Call Military OneSource at {phone} available 24/7/365, "
                "or visit militaryonesource.mil for online resources."
            )

        return " ".join(parts)

    def _extract_tags(self, program: dict[str, Any]) -> list[str]:
        """Extract and normalize tags from program data.

        Args:
            program: Program data dictionary.

        Returns:
            List of tag strings.
        """
        tags = ["military-onesource", "dod-program", "free-service"]

        # Add custom tags from program
        program_tags = program.get("tags", [])
        tags.extend(program_tags)

        # Add category-based tag
        category = program.get("category", "")
        if category:
            tags.append(category)

        # Add eligibility-based tags
        who_qualifies = program.get("who_qualifies", {})
        if who_qualifies.get("active_duty"):
            tags.append("active-duty")
        if who_qualifies.get("reserve") or who_qualifies.get("national_guard"):
            tags.append("guard-reserve")
        if who_qualifies.get("veterans_365_days"):
            tags.append("transitioning-veterans")
        if who_qualifies.get("family"):
            tags.append("family-support")
        if who_qualifies.get("retirees"):
            tags.append("retirees")

        # Deduplicate and return
        return list(set(tags))

    def close(self) -> None:
        """Close any resources (no-op for file-based connector)."""
        pass

    def __enter__(self) -> "MilitaryOneSourceConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
