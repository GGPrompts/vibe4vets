"""Veteran Certification Programs connector.

Loads curated certification programs from reference data file.
These are industry certification programs specifically targeting veterans.
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class CertificationsConnector(BaseConnector):
    """Connector for veteran certification programs.

    This connector loads curated certification program data from a YAML reference file.
    Programs include Microsoft MSSA, AWS re/Start, Salesforce Military, Google Career
    Certificates, Cisco CyberVets, CompTIA programs, and more.

    These programs offer veterans free or subsidized training leading to industry-recognized
    certifications in technology fields.
    """

    # Default path to reference data file
    DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "reference" / "veteran_certifications.yaml"

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
                self.data_path = Path(env_data_dir) / "reference" / "veteran_certifications.yaml"

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Veteran Certification Programs",
            url="https://www.va.gov/education/about-gi-bill-benefits/how-to-use-benefits/non-college-degree-programs/",
            tier=2,  # Curated from established industry programs
            frequency="monthly",
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Load certification programs from reference data.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []

        if not self.data_path.exists():
            print(f"Warning: Certification data file not found at {self.data_path}")
            return resources

        try:
            with open(self.data_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            programs = data.get("programs", [])

            for program in programs:
                candidate = self._parse_program(program)
                if candidate:
                    resources.append(candidate)

        except yaml.YAMLError as e:
            print(f"Error parsing certification YAML: {e}")
        except OSError as e:
            print(f"Error reading certification file: {e}")

        return resources

    def _parse_program(self, program: dict[str, Any]) -> ResourceCandidate | None:
        """Parse a program entry into a ResourceCandidate.

        Args:
            program: Program data from YAML file

        Returns:
            ResourceCandidate or None if required fields are missing.
        """
        name = program.get("name")
        provider = program.get("provider")

        if not name or not provider:
            return None

        # Build comprehensive description
        description = self._build_description(program)

        # Build eligibility text
        eligibility = self._build_eligibility(program)

        # Build how to apply text
        how_to_apply = self._build_how_to_apply(program)

        # Extract tags
        tags = self._extract_tags(program)

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=program.get("website", ""),
            org_name=provider,
            org_website=program.get("website"),
            # Most certification programs are online/national
            address=None,
            city=None,
            state=None,
            zip_code=None,
            categories=["training"],
            tags=tags,
            phone=None,
            email=program.get("contact_email"),
            hours=None,
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
            program: Program data dictionary

        Returns:
            Formatted description string.
        """
        parts = []

        # Start with base description
        base_desc = program.get("description", "")
        if base_desc:
            parts.append(base_desc.strip())

        # Add certifications offered
        certs = program.get("certifications", [])
        if certs:
            cert_list = ", ".join(certs[:5])
            if len(certs) > 5:
                cert_list += f", and {len(certs) - 5} more"
            parts.append(f"Certifications: {cert_list}.")

        # Add learning tracks
        tracks = program.get("learning_tracks", [])
        if tracks:
            track_list = ", ".join(tracks)
            parts.append(f"Learning tracks: {track_list}.")

        # Add duration and format
        duration = program.get("duration")
        format_type = program.get("format")
        if duration:
            format_str = f" ({format_type})" if format_type else ""
            parts.append(f"Duration: {duration}{format_str}.")

        # Add cost information
        cost = program.get("cost", "").lower()
        gi_bill = program.get("gi_bill_eligible", False)
        gi_bill_note = program.get("gi_bill_note", "")

        if cost == "free":
            parts.append("Cost: FREE for veterans.")
        elif gi_bill:
            parts.append(f"Cost: {cost}. GI Bill eligible.")
        elif gi_bill_note:
            parts.append(f"Cost: {cost}. {gi_bill_note}")

        # Add career outcomes
        outcomes = program.get("career_outcomes", [])
        if outcomes and len(outcomes) > 0:
            outcome_text = outcomes[0] if isinstance(outcomes[0], str) else str(outcomes[0])
            parts.append(f"Career outcomes: {outcome_text}")

        return " ".join(parts)

    def _build_eligibility(self, program: dict[str, Any]) -> str:
        """Build eligibility text from program data.

        Args:
            program: Program data dictionary

        Returns:
            Eligibility description string.
        """
        eligibility_list = program.get("eligibility", [])

        if not eligibility_list:
            return "Veterans and military community members."

        # Format eligibility requirements
        if len(eligibility_list) == 1:
            return eligibility_list[0]

        # Multiple requirements
        requirements = ", ".join(eligibility_list[:-1])
        requirements += f", and {eligibility_list[-1]}"

        return f"Eligible: {requirements}."

    def _build_how_to_apply(self, program: dict[str, Any]) -> str:
        """Build application instructions from program data.

        Args:
            program: Program data dictionary

        Returns:
            Application instructions string.
        """
        parts = []

        # Add application process if available
        process = program.get("application_process")
        if process:
            parts.append(process)

        # Add website
        website = program.get("website")
        if website:
            parts.append(f"Visit {website} for more information.")

        # Add contact email if available
        email = program.get("contact_email")
        if email:
            parts.append(f"Contact: {email}")

        if not parts:
            return "Visit program website to apply."

        return " ".join(parts)

    def _extract_tags(self, program: dict[str, Any]) -> list[str]:
        """Extract and normalize tags from program data.

        Args:
            program: Program data dictionary

        Returns:
            List of tag strings.
        """
        tags = ["certifications", "veteran-program"]

        # Add custom tags from program
        program_tags = program.get("tags", [])
        tags.extend(program_tags)

        # Add provider-based tag
        provider = program.get("provider", "").lower().replace(" ", "-")
        if provider:
            tags.append(provider)

        # Add GI Bill tag if eligible
        if program.get("gi_bill_eligible"):
            tags.append("gi-bill-eligible")

        # Add free tag if applicable
        cost = program.get("cost", "").lower()
        if cost == "free":
            tags.append("free-program")

        # Add format tag
        format_type = program.get("format", "").lower()
        if format_type:
            tags.append(format_type)

        # Deduplicate and return
        return list(set(tags))

    def close(self) -> None:
        """Close any resources (no-op for file-based connector)."""
        pass

    def __enter__(self) -> "CertificationsConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
