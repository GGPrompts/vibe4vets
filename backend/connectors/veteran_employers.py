"""Veteran Employers connector.

Imports curated data about employers with veteran hiring programs, pledges, and
commitments. Sources include Veteran Jobs Mission, HIRE Vets Medallion,
Hiring Our Heroes, ESGR awards, and MSEP partners.

Data sources:
    - Veteran Jobs Mission (300+ member companies)
    - HIRE Vets Medallion Award recipients (DOL)
    - Hiring Our Heroes (U.S. Chamber of Commerce Foundation)
    - ESGR Freedom Award winners
    - Military Spouse Employment Partnership (MSEP)
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class VeteranEmployersConnector(BaseConnector):
    """Connector for veteran employer hiring program data.

    Parses the veteran_employers.json file containing curated information
    about employers with demonstrated commitment to hiring veterans through
    formal programs, pledges, awards, and employee resource groups.

    Data fields:
        - name: Company name
        - industry: Industry sector
        - programs: List of veteran hiring programs (e.g., SkillBridge, fellowships)
        - has_erg: Whether company has a veteran employee resource group
        - erg_name: Name of the veteran ERG if present
        - skills_translator: Whether company offers military skills translator
        - careers_url: URL for veteran careers page
        - scope: Geographic scope (national, regional, local)
        - hire_vets_medallion: Whether awarded DOL HIRE Vets Medallion
        - notes: Additional context about veteran hiring commitment
    """

    DEFAULT_DATA_PATH = "data/reference/veteran_employers.json"

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
            name="Veteran Employers (Compiled)",
            url="https://veteranjobsmission.com/",
            tier=2,  # Established sources (VJM, DOL HIRE Vets, HOH)
            frequency="quarterly",
            terms_url="https://www.hirevets.gov/about",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse veteran employer data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Veteran employers data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for employer in data.get("employers", []):
            candidate = self._parse_employer(employer, fetched_at=now)
            if candidate:
                resources.append(candidate)

        return resources

    def _parse_employer(
        self,
        employer: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse an employer entry into a ResourceCandidate.

        Args:
            employer: Employer data dictionary
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this employer or None if invalid.
        """
        name = employer.get("name")
        if not name:
            return None

        industry = employer.get("industry", "")
        programs = employer.get("programs", [])
        has_erg = employer.get("has_erg", False)
        erg_name = employer.get("erg_name")
        skills_translator = employer.get("skills_translator", False)
        careers_url = employer.get("careers_url", "")
        scope = employer.get("scope", "national")
        hire_vets_medallion = employer.get("hire_vets_medallion", False)
        notes = employer.get("notes", "")

        title = f"{name} - Veteran Hiring Program"
        description = self._build_description(
            name=name,
            industry=industry,
            programs=programs,
            has_erg=has_erg,
            erg_name=erg_name,
            skills_translator=skills_translator,
            hire_vets_medallion=hire_vets_medallion,
            notes=notes,
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=careers_url or "https://veteranjobsmission.com/",
            org_name=name,
            org_website=careers_url,
            categories=["employment"],
            tags=self._build_tags(
                industry=industry,
                programs=programs,
                has_erg=has_erg,
                skills_translator=skills_translator,
                hire_vets_medallion=hire_vets_medallion,
            ),
            eligibility=self._build_eligibility(programs),
            how_to_apply=self._build_how_to_apply(name, careers_url, programs),
            scope=scope,
            states=None,  # National employers
            raw_data=employer,
            fetched_at=fetched_at,
        )

    def _build_description(
        self,
        name: str,
        industry: str,
        programs: list[str],
        has_erg: bool,
        erg_name: str | None,
        skills_translator: bool,
        hire_vets_medallion: bool,
        notes: str,
    ) -> str:
        """Build resource description.

        Args:
            name: Company name
            industry: Industry sector
            programs: List of veteran hiring programs
            has_erg: Whether company has veteran ERG
            erg_name: Name of veteran ERG
            skills_translator: Whether offers skills translator
            hire_vets_medallion: Whether HIRE Vets Medallion recipient
            notes: Additional context

        Returns:
            Formatted description string.
        """
        parts = []

        # Opening line with industry
        if industry:
            parts.append(f"{name} is a {industry} company with a demonstrated commitment to hiring veterans.")
        else:
            parts.append(f"{name} has a demonstrated commitment to hiring veterans.")

        # Awards and recognition
        recognitions = []
        if hire_vets_medallion:
            recognitions.append("DOL HIRE Vets Medallion Award recipient")
        if "Veteran Jobs Mission" in " ".join(programs):
            recognitions.append("Veteran Jobs Mission coalition member")
        if "Hiring Our Heroes" in " ".join(programs):
            recognitions.append("Hiring Our Heroes partner")

        if recognitions:
            parts.append(f"Recognition: {', '.join(recognitions)}.")

        # Programs offered
        if programs:
            program_str = ", ".join(programs)
            parts.append(f"Programs: {program_str}.")

        # ERG info
        if has_erg and erg_name:
            parts.append(f"Veteran Employee Resource Group: {erg_name}.")
        elif has_erg:
            parts.append("Has an active veteran employee resource group.")

        # Skills translator
        if skills_translator:
            parts.append(
                "Offers a military skills translator to match military experience with civilian job requirements."
            )

        # Additional notes
        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_eligibility(self, programs: list[str]) -> str:
        """Build eligibility description.

        Args:
            programs: List of veteran hiring programs

        Returns:
            Eligibility description string.
        """
        parts = ["Veterans of all branches and service eras are encouraged to apply."]

        has_skillbridge = any("SkillBridge" in p for p in programs)
        has_fellowship = any("Fellowship" in p for p in programs)

        if has_skillbridge:
            parts.append("SkillBridge program available for active duty service members within 180 days of separation.")

        if has_fellowship:
            parts.append("Fellowship or internship programs may be available for transitioning service members.")

        parts.append("Military spouses may also be eligible for hiring programs at this employer.")

        return " ".join(parts)

    def _build_how_to_apply(
        self,
        name: str,
        careers_url: str,
        programs: list[str],
    ) -> str:
        """Build how to apply instructions.

        Args:
            name: Company name
            careers_url: URL for careers page
            programs: List of veteran hiring programs

        Returns:
            Application instructions string.
        """
        parts = []

        if careers_url:
            parts.append(f"Visit {name}'s veteran careers page at {careers_url}.")
        else:
            parts.append(f"Search for {name} veteran careers on their company website.")

        parts.append(
            "Look for positions tagged as military-friendly or veteran preferred. "
            "Many employers accept applications through standard job portals but have "
            "dedicated veteran recruiters who can assist with the process."
        )

        has_skillbridge = any("SkillBridge" in p for p in programs)
        if has_skillbridge:
            parts.append(
                "For SkillBridge opportunities, coordinate with your transition "
                "office and reach out to the company's military recruiting team."
            )

        return " ".join(parts)

    def _build_tags(
        self,
        industry: str,
        programs: list[str],
        has_erg: bool,
        skills_translator: bool,
        hire_vets_medallion: bool,
    ) -> list[str]:
        """Build tags list.

        Args:
            industry: Industry sector
            programs: List of veteran hiring programs
            has_erg: Whether company has veteran ERG
            skills_translator: Whether offers skills translator
            hire_vets_medallion: Whether HIRE Vets Medallion recipient

        Returns:
            List of tag strings.
        """
        tags = [
            "veteran-employer",
            "veteran-preference",
            "veteran-hiring",
        ]

        # Add industry tag
        if industry:
            industry_tag = industry.lower().replace(" ", "-").replace("/", "-")
            tags.append(f"industry-{industry_tag}")

        # Program-specific tags
        program_str = " ".join(programs).lower()
        if "skillbridge" in program_str:
            tags.append("skillbridge")
        if "fellowship" in program_str:
            tags.append("fellowship")
        if "apprentice" in program_str:
            tags.append("apprenticeship")
        if "veteran jobs mission" in program_str:
            tags.append("veteran-jobs-mission")
        if "hiring our heroes" in program_str:
            tags.append("hiring-our-heroes")

        # Feature tags
        if has_erg:
            tags.append("veteran-erg")
        if skills_translator:
            tags.append("skills-translator")
        if hire_vets_medallion:
            tags.append("hire-vets-medallion")

        return list(set(tags))  # Deduplicate
