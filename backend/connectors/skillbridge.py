"""DOD SkillBridge program connector.

Imports SkillBridge partner data from CSV export of the official DOD SkillBridge
partner directory. SkillBridge allows transitioning service members to do
civilian job training during their last 180 days of service.

Data source: skillbridge.osd.mil (via community-maintained CSV export)
"""

import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class SkillBridgeConnector(BaseConnector):
    """Connector for DOD SkillBridge partner directory.

    SkillBridge is a DOD program that allows service members to participate
    in civilian job training, employment skills training, apprenticeships,
    and internships during their last 180 days of military service.

    This connector can either:
    1. Load from a local CSV file (for offline/cached data)
    2. Fetch fresh data from the community-maintained Google Sheets export

    The data originates from the official DOD SkillBridge website but is
    accessed via a community export since DOD does not provide a public API.

    Columns in the data:
        - Partner/Program: Organization name (MOU holder)
        - Partner/Program - Sub: Specific program/position
        - Service: Military branches accepted (All Services, Army, Navy, etc.)
        - City: Training location city
        - State: Training location state
        - Duration of Training: Program length (e.g., "151 - 180 days")
        - Employer POC: Point of contact name
        - POC Email: Contact email
        - Closest Installation: Nearest military installation
        - Locations of Prospective Jobs by State: Job location states
        - Delivery Method: In-person, Online, or Hybrid
        - Target MOCs: Military Occupational Codes targeted
        - Other Eligibility Factors: Additional requirements
        - Other: Additional notes
        - Job Description: Detailed job description
        - Summary Description: Program summary
        - Job Family: Career field category
        - MOU Organization: Parent organization with MOU
    """

    # Google Sheets export URL for SkillBridge data
    SHEETS_EXPORT_URL = (
        "https://docs.google.com/spreadsheets/d/1mckuio6U-LlIc1r4yN9-vx99igc1kipQGMtlk8WkNRY/export?format=csv"
    )

    # Path to local cached data file
    DEFAULT_DATA_PATH = "data/reference/skillbridge_partners.csv"

    # Column indices (0-based)
    COL_PARTNER = 0
    COL_PROGRAM = 1
    COL_SERVICE = 2
    COL_CITY = 3
    COL_STATE = 4
    COL_DURATION = 5
    COL_POC_NAME = 6
    COL_POC_EMAIL = 7
    COL_INSTALLATION = 8
    COL_JOB_STATES = 9
    COL_DELIVERY = 10
    COL_MOCS = 11
    COL_ELIGIBILITY = 12
    COL_OTHER = 13
    COL_JOB_DESC = 14
    COL_SUMMARY = 15
    COL_JOB_FAMILY = 16
    COL_MOU_ORG = 17

    # Duration categories for filtering
    DURATION_MAP = {
        "1 - 30 days": 30,
        "31 - 60 days": 60,
        "61 - 90 days": 90,
        "91 - 120 days": 120,
        "121 - 150 days": 150,
        "151 - 180 days": 180,
    }

    def __init__(
        self,
        data_path: str | Path | None = None,
        fetch_fresh: bool = False,
    ):
        """Initialize the connector.

        Args:
            data_path: Path to local CSV file. Falls back to DEFAULT_DATA_PATH.
            fetch_fresh: If True, always fetch fresh data from Google Sheets.
                        If False, use local file if available.
        """
        self.fetch_fresh = fetch_fresh
        self._client: httpx.Client | None = None

        if data_path is None:
            # Find project root (directory containing 'data' folder)
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
            name="DOD SkillBridge Partner Directory",
            url="https://skillbridge.osd.mil/locations.htm",
            tier=1,  # Official DOD program data
            frequency="weekly",
            terms_url="https://skillbridge.osd.mil/",
            requires_auth=False,
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=60.0,
                follow_redirects=True,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch SkillBridge partner data.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        try:
            # Decide whether to use local file or fetch fresh
            if self.fetch_fresh or not self.data_path.exists():
                csv_data = self._fetch_from_sheets()
            else:
                csv_data = self._load_from_file()

            return self._parse_csv_data(csv_data)
        finally:
            self.close()

    def _fetch_from_sheets(self) -> str:
        """Fetch fresh data from Google Sheets export.

        Returns:
            CSV data as string.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        client = self._get_client()
        response = client.get(self.SHEETS_EXPORT_URL)
        response.raise_for_status()
        return response.text

    def _load_from_file(self) -> str:
        """Load data from local CSV file.

        Returns:
            CSV data as string.

        Raises:
            FileNotFoundError: If local file doesn't exist.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"SkillBridge data file not found: {self.data_path}")
        return self.data_path.read_text(encoding="utf-8")

    def _parse_csv_data(self, csv_data: str) -> list[ResourceCandidate]:
        """Parse CSV data into ResourceCandidate objects.

        Args:
            csv_data: Raw CSV string data.

        Returns:
            List of ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        seen_ids: set[str] = set()
        now = datetime.now(UTC)

        reader = csv.reader(csv_data.splitlines())

        # Skip header row
        next(reader, None)

        current_org = None

        for row in reader:
            # Skip empty rows or rows that don't have enough columns
            if len(row) < 16:
                continue

            # Track parent organization from "Partner/Program" column
            # Rows with org name in first column are parent org headers
            # Rows with empty first column are actual programs under that org
            partner = self._clean_text(row[self.COL_PARTNER])
            program = self._clean_text(row[self.COL_PROGRAM])

            if partner and not program:
                # This is an organization header row, save org name for children
                current_org = partner
                continue

            if not program:
                # Skip rows without program info
                continue

            # Use the program row's MOU Organization or fall back to tracked org
            mou_org = self._clean_text(row[self.COL_MOU_ORG]) if len(row) > self.COL_MOU_ORG else None
            org_name = mou_org or current_org or partner or "Unknown Organization"

            # Create unique ID to avoid duplicates
            unique_id = self._create_unique_id(row, org_name)
            if unique_id in seen_ids:
                continue
            seen_ids.add(unique_id)

            candidate = self._parse_row(row, org_name, now)
            if candidate:
                resources.append(candidate)

        return resources

    def _create_unique_id(self, row: list[str], org_name: str) -> str:
        """Create a unique identifier for deduplication.

        Args:
            row: CSV row data.
            org_name: Organization name.

        Returns:
            Unique string identifier.
        """
        program = self._clean_text(row[self.COL_PROGRAM])
        city = self._clean_text(row[self.COL_CITY])
        state = self._clean_text(row[self.COL_STATE])
        return f"{org_name}|{program}|{city}|{state}".lower()

    def _parse_row(
        self,
        row: list[str],
        org_name: str,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Parse a CSV row into a ResourceCandidate.

        Args:
            row: CSV row data.
            org_name: Organization name (from parent or MOU column).
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate or None if row is invalid.
        """
        program = self._clean_text(row[self.COL_PROGRAM])
        if not program:
            return None

        city = self._clean_text(row[self.COL_CITY])
        state = self._clean_text(row[self.COL_STATE])
        duration = self._clean_text(row[self.COL_DURATION])
        poc_name = self._clean_text(row[self.COL_POC_NAME])
        poc_email = self._clean_text(row[self.COL_POC_EMAIL])
        installation = self._clean_text(row[self.COL_INSTALLATION])
        job_states = self._clean_text(row[self.COL_JOB_STATES])
        delivery = self._clean_text(row[self.COL_DELIVERY])
        mocs = self._clean_text(row[self.COL_MOCS])
        eligibility_factors = self._clean_text(row[self.COL_ELIGIBILITY])
        other = self._clean_text(row[self.COL_OTHER])
        job_desc = self._clean_text(row[self.COL_JOB_DESC])
        summary = self._clean_text(row[self.COL_SUMMARY])
        job_family = self._clean_text(row[self.COL_JOB_FAMILY])
        service = self._clean_text(row[self.COL_SERVICE])

        # Build title
        title = self._build_title(program, city, state, delivery)

        # Build description
        description = self._build_description(
            program=program,
            summary=summary,
            job_desc=job_desc,
            duration=duration,
            job_family=job_family,
            delivery=delivery,
        )

        # Parse states for scope
        states = self._parse_job_states(job_states, state)
        scope = self._determine_scope(states, delivery)

        # Build eligibility text
        eligibility = self._build_eligibility(service, mocs, eligibility_factors, other)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(poc_name, poc_email)

        # Build tags
        tags = self._build_tags(
            job_family=job_family,
            delivery=delivery,
            duration=duration,
            service=service,
            mocs=mocs,
        )

        return ResourceCandidate(
            title=title,
            description=description,
            source_url="https://skillbridge.osd.mil/locations.htm",
            org_name=org_name,
            org_website=None,  # Not provided in data
            city=city if city else None,
            state=self._normalize_state(state) if state else None,
            categories=["employment", "training"],
            tags=tags,
            email=poc_email if poc_email else None,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=scope,
            states=states if states else None,
            raw_data={
                "program": program,
                "service": service,
                "duration": duration,
                "poc_name": poc_name,
                "poc_email": poc_email,
                "installation": installation,
                "job_states": job_states,
                "delivery": delivery,
                "mocs": mocs,
                "eligibility_factors": eligibility_factors,
                "job_family": job_family,
                "summary": summary,
            },
            fetched_at=fetched_at,
        )

    def _clean_text(self, text: str | None) -> str:
        """Clean and normalize text field.

        Args:
            text: Raw text value.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ""
        # Replace double spaces with single, strip whitespace
        cleaned = " ".join(text.split())
        return cleaned.strip()

    def _build_title(
        self,
        program: str,
        city: str,
        state: str,
        delivery: str,
    ) -> str:
        """Build resource title.

        Args:
            program: Program/position name.
            city: Training city.
            state: Training state.
            delivery: Delivery method.

        Returns:
            Formatted title string.
        """
        parts = [f"SkillBridge: {program}"]

        delivery_lower = delivery.lower() if delivery else ""
        is_purely_online = "online" in delivery_lower and "in-person" not in delivery_lower

        if is_purely_online:
            parts.append("(Online)")
        elif city and state:
            parts.append(f"({city}, {state})")
        elif state:
            parts.append(f"({state})")

        return " ".join(parts)

    def _build_description(
        self,
        program: str,
        summary: str,
        job_desc: str,
        duration: str,
        job_family: str,
        delivery: str,
    ) -> str:
        """Build resource description.

        Args:
            program: Program name.
            summary: Program summary.
            job_desc: Job description.
            duration: Training duration.
            job_family: Job category.
            delivery: Delivery method.

        Returns:
            Formatted description string.
        """
        parts = [
            "DOD SkillBridge program offering civilian job training for "
            "transitioning service members during their last 180 days of service."
        ]

        if summary:
            parts.append(summary)
        elif job_desc:
            # Use first 500 chars of job description if no summary
            desc = job_desc[:500]
            if len(job_desc) > 500:
                desc += "..."
            parts.append(desc)

        details = []
        if duration:
            details.append(f"Duration: {duration}")
        if job_family:
            details.append(f"Career Field: {job_family}")
        if delivery:
            details.append(f"Format: {delivery}")

        if details:
            parts.append(" | ".join(details))

        return " ".join(parts)

    def _parse_job_states(self, job_states: str, training_state: str) -> list[str]:
        """Parse job location states.

        Args:
            job_states: Raw job states string (may contain "Nationwide", state list, etc.).
            training_state: Training location state as fallback.

        Returns:
            List of normalized state codes.
        """
        states: list[str] = []

        if not job_states:
            if training_state:
                normalized = self._normalize_state(training_state)
                if normalized:
                    return [normalized]
            return []

        # Check for nationwide
        job_states_lower = job_states.lower()
        if "nationwide" in job_states_lower or "all states" in job_states_lower:
            return []  # Empty list indicates national scope

        # Parse state list - could be comma or semicolon separated
        raw_states = job_states.replace(";", ",").split(",")
        for raw in raw_states:
            normalized = self._normalize_state(raw)
            if normalized:
                states.append(normalized)

        return list(set(states))  # Deduplicate

    def _determine_scope(self, states: list[str], delivery: str) -> str:
        """Determine resource scope.

        Args:
            states: List of state codes.
            delivery: Delivery method.

        Returns:
            Scope string: "national", "regional", "state", or "local".
        """
        # Online programs are effectively national
        if delivery and "online" in delivery.lower():
            return "national"

        if not states:
            return "national"
        elif len(states) == 1:
            return "state"
        elif len(states) <= 5:
            return "regional"
        else:
            return "national"

    def _build_eligibility(
        self,
        service: str,
        mocs: str,
        eligibility_factors: str,
        other: str,
    ) -> str:
        """Build eligibility description.

        Args:
            service: Military branches accepted.
            mocs: Target Military Occupational Codes.
            eligibility_factors: Other eligibility requirements.
            other: Additional notes.

        Returns:
            Formatted eligibility string.
        """
        parts = ["Active duty service members within 180 days of separation/retirement."]

        if service and service.lower() != "all services":
            parts.append(f"Open to: {service}.")
        else:
            parts.append("Open to all military branches.")

        if mocs and mocs.lower() != "all mocs" and mocs.lower() != "all":
            parts.append(f"Target MOCs: {mocs}.")

        if eligibility_factors:
            parts.append(f"Requirements: {eligibility_factors}")

        if other:
            parts.append(other)

        return " ".join(parts)

    def _build_how_to_apply(self, poc_name: str, poc_email: str) -> str:
        """Build application instructions.

        Args:
            poc_name: Point of contact name.
            poc_email: Point of contact email.

        Returns:
            Formatted how-to-apply string.
        """
        parts = [
            "1. Confirm eligibility with your command and Education Services Officer.",
            "2. Get command approval using DD Form 2648.",
        ]

        if poc_name and poc_email:
            parts.append(f"3. Contact {poc_name} at {poc_email} to apply.")
        elif poc_email:
            parts.append(f"3. Contact the employer at {poc_email} to apply.")
        else:
            parts.append("3. Contact the employer through the SkillBridge website to apply.")

        parts.append("More info: https://skillbridge.osd.mil/")

        return " ".join(parts)

    def _build_tags(
        self,
        job_family: str,
        delivery: str,
        duration: str,
        service: str,
        mocs: str,
    ) -> list[str]:
        """Build tags list.

        Args:
            job_family: Career field category.
            delivery: Delivery method.
            duration: Program duration.
            service: Military branches.
            mocs: Target MOCs.

        Returns:
            List of tag strings.
        """
        tags = [
            "skillbridge",
            "dod",
            "transition",
            "employment",
            "training",
            "apprenticeship",
        ]

        # Add delivery method tag
        if delivery:
            delivery_lower = delivery.lower()
            # Check for hybrid first since it may contain "online" and "in-person"
            if "hybrid" in delivery_lower:
                tags.append("hybrid")
            elif "online" in delivery_lower:
                tags.append("online")
            elif "in-person" in delivery_lower:
                tags.append("in-person")

        # Add job family as tag
        if job_family:
            # Convert "Sales and Related" to "sales-and-related"
            family_tag = job_family.lower().replace(" ", "-").replace("/", "-")
            # Clean up multiple dashes
            while "--" in family_tag:
                family_tag = family_tag.replace("--", "-")
            tags.append(family_tag)

        # Add service branch tags
        if service:
            service_lower = service.lower()
            if "army" in service_lower:
                tags.append("army")
            if "navy" in service_lower:
                tags.append("navy")
            if "air force" in service_lower:
                tags.append("air-force")
            if "marine" in service_lower:
                tags.append("marine-corps")
            if "coast guard" in service_lower:
                tags.append("coast-guard")
            if "space force" in service_lower:
                tags.append("space-force")
            if "all services" in service_lower:
                tags.append("all-branches")

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "SkillBridgeConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
