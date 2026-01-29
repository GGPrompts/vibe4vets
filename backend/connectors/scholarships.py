"""Veteran Scholarships connector.

Imports curated data about scholarship programs for Veterans, service members,
and their families. Sources include Pat Tillman Foundation, Folds of Honor,
VFW, American Legion, DAV, and official VA education programs.

This connector provides comprehensive scholarship information including:
- Direct scholarship programs with application deadlines
- Award amounts and eligibility requirements
- Application instructions and websites
- Aggregator sites for additional scholarship searches
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class ScholarshipsConnector(BaseConnector):
    """Connector for Veteran scholarship program data.

    Parses the veteran_scholarships.json file containing curated information
    about scholarships for Veterans, active duty service members, military
    spouses, and military children.

    Data fields for scholarships:
        - name: Scholarship program name
        - organization: Sponsoring organization
        - amount: Award amount (may be a range)
        - deadline: Application deadline
        - eligibility: List of eligibility requirements
        - description: Program description
        - how_to_apply: Application instructions
        - website: Application or information URL
        - renewable: Whether scholarship can be renewed
        - notes: Additional context

    Data fields for aggregators:
        - name: Aggregator site name
        - description: Site description
        - website: URL to the aggregator
    """

    DEFAULT_DATA_PATH = "data/reference/veteran_scholarships.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
            current = Path(__file__).resolve().parent
            while current != current.parent:
                if (current / "data").is_dir():
                    break
                current = current.parent
            self.data_path = current / self.DEFAULT_DATA_PATH
        else:
            self.data_path = Path(data_path)

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Veteran Scholarships (Compiled)",
            url="https://www.va.gov/education/",
            tier=2,  # Established programs (major foundations, VA programs)
            frequency="monthly",
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse scholarship data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Veteran scholarships data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        # Process individual scholarship programs
        for scholarship in data.get("scholarships", []):
            candidate = self._parse_scholarship(scholarship, fetched_at=now)
            if candidate:
                resources.append(candidate)

        # Process aggregator sites
        for aggregator in data.get("aggregator_sites", []):
            candidate = self._parse_aggregator(aggregator, fetched_at=now)
            if candidate:
                resources.append(candidate)

        return resources

    def _parse_scholarship(
        self,
        scholarship: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse a scholarship entry into a ResourceCandidate.

        Args:
            scholarship: Scholarship data dictionary
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this scholarship or None if invalid.
        """
        name = scholarship.get("name")
        organization = scholarship.get("organization")

        if not name or not organization:
            return None

        amount = scholarship.get("amount", "Varies")
        deadline = scholarship.get("deadline", "Varies")
        eligibility_list = scholarship.get("eligibility", [])
        base_description = scholarship.get("description", "")
        how_to_apply = scholarship.get("how_to_apply", "")
        website = scholarship.get("website", "")
        renewable = scholarship.get("renewable", False)
        notes = scholarship.get("notes", "")

        title = name
        description = self._build_description(
            base_description=base_description,
            amount=amount,
            deadline=deadline,
            renewable=renewable,
            notes=notes,
        )

        eligibility = self._build_eligibility(eligibility_list)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.va.gov/education/",
            org_name=organization,
            org_website=website,
            categories=["education"],
            tags=self._build_tags(
                organization=organization,
                eligibility_list=eligibility_list,
                renewable=renewable,
                amount=amount,
            ),
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope="national",
            states=None,  # National scholarships
            raw_data=scholarship,
            fetched_at=fetched_at,
        )

    def _parse_aggregator(
        self,
        aggregator: dict[str, Any],
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse an aggregator site entry into a ResourceCandidate.

        Args:
            aggregator: Aggregator data dictionary
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this aggregator or None if invalid.
        """
        name = aggregator.get("name")
        website = aggregator.get("website")

        if not name or not website:
            return None

        description = aggregator.get("description", "")

        return ResourceCandidate(
            title=f"{name} - Scholarship Search Tool",
            description=(
                f"{description} Use this resource to search for additional Veteran "
                "scholarships beyond the major programs listed in our directory."
            ),
            source_url=website,
            org_name=name.split()[0] if name else "Scholarship Directory",
            org_website=website,
            categories=["education"],
            tags=[
                "scholarships",
                "education",
                "financial-aid",
                "scholarship-search",
                "veteran-education",
                "aggregator",
            ],
            eligibility=(
                "Open to all Veterans, service members, and military families "
                "searching for education funding."
            ),
            how_to_apply=(
                f"Visit {website} and use the search tools to find scholarships "
                "matching your eligibility and educational goals."
            ),
            scope="national",
            states=None,
            raw_data=aggregator,
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        base_description: str,
        amount: str,
        deadline: str,
        renewable: bool,
        notes: str,
    ) -> str:
        """Build resource description.

        Args:
            base_description: Base program description
            amount: Award amount
            deadline: Application deadline
            renewable: Whether scholarship is renewable
            notes: Additional notes

        Returns:
            Formatted description string.
        """
        parts = []

        # Start with base description
        if base_description:
            parts.append(base_description)

        # Add award information
        award_info = f"Award amount: {amount}."
        if renewable:
            award_info = f"Award amount: {amount} (renewable)."
        parts.append(award_info)

        # Add deadline
        if deadline:
            parts.append(f"Application deadline: {deadline}.")

        # Add notes
        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_eligibility(self, eligibility_list: list[str]) -> str:
        """Build eligibility description from list.

        Args:
            eligibility_list: List of eligibility requirements

        Returns:
            Formatted eligibility string.
        """
        if not eligibility_list:
            return (
                "Veterans and military community members. "
                "Check program requirements for specific eligibility criteria."
            )

        if len(eligibility_list) == 1:
            return f"Eligible: {eligibility_list[0]}. Check program website for complete eligibility requirements."

        formatted_list = "; ".join(eligibility_list)
        return (
            f"Eligible applicants include: {formatted_list}. "
            "Check program website for complete eligibility requirements."
        )

    def _build_tags(
        self,
        organization: str,
        eligibility_list: list[str],
        renewable: bool,
        amount: str,
    ) -> list[str]:
        """Build tags list for scholarship.

        Args:
            organization: Sponsoring organization
            eligibility_list: List of eligibility requirements
            renewable: Whether scholarship is renewable
            amount: Award amount

        Returns:
            List of tag strings.
        """
        tags = [
            "scholarships",
            "education",
            "financial-aid",
            "veteran-education",
        ]

        # Add organization-based tag
        org_lower = organization.lower()
        if "va" in org_lower or "veterans affairs" in org_lower:
            tags.append("va-program")
        if "vfw" in org_lower:
            tags.append("vfw")
        if "american legion" in org_lower:
            tags.append("american-legion")
        if "dav" in org_lower:
            tags.append("dav")
        if "tillman" in org_lower:
            tags.append("pat-tillman")
        if "folds of honor" in org_lower:
            tags.append("folds-of-honor")

        # Add eligibility-based tags
        elig_str = " ".join(eligibility_list).lower()
        if "spouse" in elig_str:
            tags.append("military-spouse")
        if "children" in elig_str or "dependents" in elig_str:
            tags.append("military-children")
        if "active duty" in elig_str:
            tags.append("active-duty")
        if "disabled" in elig_str:
            tags.append("disabled-veteran")
        if "fallen" in elig_str or "deceased" in elig_str or "died" in elig_str:
            tags.append("gold-star-family")
        if "stem" in elig_str:
            tags.append("stem")

        # Add branch-specific tags
        if "marine" in elig_str:
            tags.append("marines")
        if "army" in elig_str or "army women" in org_lower:
            tags.append("army")
        if "air force" in elig_str or "space force" in elig_str:
            tags.append("air-force")
        if "navy" in elig_str or "corpsmen" in elig_str:
            tags.append("navy")
        if "coast guard" in elig_str:
            tags.append("coast-guard")

        # Renewable tag
        if renewable:
            tags.append("renewable")

        # Amount-based tags
        amount_lower = amount.lower()
        if "$10,000" in amount or "$20,000" in amount or "$30,000" in amount:
            tags.append("high-value")
        if "full" in amount_lower and "tuition" in amount_lower:
            tags.append("full-tuition")

        return list(set(tags))  # Deduplicate
