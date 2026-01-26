"""GI Bill Schools (WEAMS) connector for approved education and training programs.

Fetches GI Bill approved schools and training programs from the VA's GI Bill
Comparison Tool API. This includes colleges, vocational schools, OJT programs,
apprenticeships, and flight training.

Data source: VA GI Bill Comparison Tool (https://www.va.gov/education/gi-bill-comparison-tool/)
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class GIBillSchoolsConnector(BaseConnector):
    """Connector for VA GI Bill approved schools and programs (WEAMS data).

    This connector fetches institution data from the VA's GI Bill Comparison Tool
    API, which aggregates WEAMS (Web Enabled Approval Management System) data
    including:
    - Colleges and universities
    - Vocational/technical schools
    - On-the-job training (OJT) programs
    - Apprenticeship programs
    - Flight training schools
    - Correspondence courses

    The API provides information about:
    - Institution name and address
    - Programs approved (degree, non-degree, OJT, apprenticeship)
    - Yellow Ribbon participation
    - Caution flags
    - Student veteran population
    - Accreditation status
    """

    # VA.gov API endpoint for GI Bill institution search
    # This is the public API endpoint used by the GI Bill Comparison Tool
    BASE_URL = "https://www.va.gov/gids/v1"
    SEARCH_ENDPOINT = "/institutions/search"

    DEFAULT_PAGE_SIZE = 100
    MAX_PAGES = 100  # Safety limit to prevent runaway pagination (10,000 institutions)

    # Institution types relevant to veterans
    INSTITUTION_TYPES = [
        "school",  # Colleges, universities, vocational schools
        "ojt",  # On-the-job training
        "employer",  # Employer OJT programs
    ]

    # All US states and territories for comprehensive fetching
    US_STATES = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "AS",
        "GU",
        "MP",
        "PR",
        "VI",
    ]

    def __init__(self, api_key: str | None = None):
        """Initialize the connector.

        Args:
            api_key: VA API key. Falls back to VA_API_KEY env var.
                     Note: The GI Bill Comparison Tool API may not require auth
                     for basic search functionality.
        """
        self.api_key = api_key or os.environ.get("VA_API_KEY")
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="VA GI Bill Comparison Tool (WEAMS)",
            url="https://www.va.gov/education/gi-bill-comparison-tool/",
            tier=1,  # Official VA government source
            frequency="weekly",
            terms_url="https://www.va.gov/webpolicylinks/",
            requires_auth=False,  # Public search API
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "Accept": "application/json",
                "User-Agent": "Vibe4Vets/1.0 (veteran-resource-aggregator)",
            }
            if self.api_key:
                headers["apikey"] = self.api_key
            self._client = httpx.Client(
                headers=headers,
                timeout=60.0,  # Longer timeout for large result sets
                follow_redirects=True,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch all GI Bill approved institutions from VA API.

        Fetches institutions by state to ensure comprehensive coverage.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        seen_ids: set[str] = set()  # Track unique institutions

        try:
            client = self._get_client()

            # Fetch institutions by state for comprehensive coverage
            for state in self.US_STATES:
                state_resources = self._fetch_institutions_by_state(client, state, seen_ids)
                resources.extend(state_resources)

            return resources
        finally:
            self.close()

    def _fetch_institutions_by_state(
        self,
        client: httpx.Client,
        state: str,
        seen_ids: set[str],
    ) -> list[ResourceCandidate]:
        """Fetch institutions for a specific state.

        Args:
            client: HTTP client
            state: Two-letter state code
            seen_ids: Set of already-seen facility codes to avoid duplicates

        Returns:
            List of ResourceCandidate objects for this state.
        """
        resources: list[ResourceCandidate] = []
        page = 1

        while page <= self.MAX_PAGES:
            try:
                response = client.get(
                    f"{self.BASE_URL}{self.SEARCH_ENDPOINT}",
                    params={
                        "state": state,
                        "page": page,
                        "per_page": self.DEFAULT_PAGE_SIZE,
                    },
                )

                # Handle API responses
                if response.status_code == 404:
                    # State has no institutions or API endpoint issue
                    break
                elif response.status_code == 403:
                    # API access restricted - try alternative endpoint
                    print(f"Access restricted for {state}, trying alternative approach")
                    break

                response.raise_for_status()
                data = response.json()

                # Extract institutions from response
                institutions = data.get("data", [])
                if not institutions:
                    break

                for institution in institutions:
                    # Get facility_code as unique identifier
                    attrs = institution.get("attributes", {})
                    facility_code = attrs.get("facility_code")

                    if not facility_code or facility_code in seen_ids:
                        continue
                    seen_ids.add(facility_code)

                    candidate = self._parse_institution(institution)
                    if candidate:
                        resources.append(candidate)

                # Check for more pages
                meta = data.get("meta", {})
                total_pages = meta.get("total_pages", 1)
                if page >= total_pages:
                    break

                page += 1

            except httpx.HTTPStatusError as e:
                print(f"HTTP error fetching institutions for {state}: {e.response.status_code}")
                break
            except httpx.HTTPError as e:
                print(f"Error fetching institutions for {state}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error for {state}: {e}")
                break

        return resources

    def _parse_institution(self, institution: dict[str, Any]) -> ResourceCandidate | None:
        """Parse an institution object into a ResourceCandidate.

        Args:
            institution: Raw institution data from API

        Returns:
            ResourceCandidate or None if not relevant.
        """
        attrs = institution.get("attributes", {})

        name = attrs.get("name")
        if not name:
            return None

        # Build description
        description = self._build_description(attrs)

        # Extract location info
        address = attrs.get("address_1")
        if attrs.get("address_2"):
            address = f"{address}, {attrs.get('address_2')}"
        if attrs.get("address_3"):
            address = f"{address}, {attrs.get('address_3')}"

        city = attrs.get("city")
        state = attrs.get("state")
        zip_code = attrs.get("zip")

        # Determine institution type for categorization
        inst_type = attrs.get("type", "school").lower()
        is_ojt = attrs.get("ojt_indicator") or inst_type in ["ojt", "employer"]
        is_flight = attrs.get("flight_indicator")
        is_correspondence = attrs.get("correspondence_indicator")

        # Build source URL - use school's website or GI Bill tool
        website = attrs.get("website")
        source_url = website if website else "https://www.va.gov/education/gi-bill-comparison-tool/"

        # Get GI Bill programs approved
        programs = self._get_approved_programs(attrs)

        # Build eligibility info
        eligibility = self._build_eligibility(attrs)

        # Determine scope
        scope = "local"
        if is_correspondence:
            scope = "national"  # Correspondence can be accessed from anywhere

        return ResourceCandidate(
            title=f"{name} - GI Bill Approved",
            description=description,
            source_url=source_url,
            org_name=name,
            org_website=website,
            address=address,
            city=city,
            state=self._normalize_state(state),
            zip_code=zip_code,
            categories=["training"],
            tags=self._extract_tags(attrs, is_ojt, is_flight, is_correspondence),
            phone=self._normalize_phone(attrs.get("phone")),
            email=attrs.get("email"),
            eligibility=eligibility,
            how_to_apply=self._build_how_to_apply(attrs, programs),
            scope=scope,
            states=[self._normalize_state(state)] if state else None,
            raw_data={
                "facility_code": attrs.get("facility_code"),
                "institution_id": institution.get("id"),
                "type": inst_type,
                "programs": programs,
                "yellow_ribbon": attrs.get("yellow_ribbon"),
                "caution_flags": attrs.get("caution_flags", []),
                "student_veteran_group": attrs.get("student_veteran_group"),
                "student_veteran": attrs.get("student_veteran"),
                "accredited": attrs.get("accredited"),
                "accreditation_type": attrs.get("accreditation_type"),
                "highest_degree": attrs.get("highest_degree"),
            },
            fetched_at=datetime.now(UTC),
        )

    def _build_description(self, attrs: dict[str, Any]) -> str:
        """Build a description from institution attributes.

        Args:
            attrs: Institution attributes

        Returns:
            Formatted description string.
        """
        parts = []

        # Institution type context
        inst_type = attrs.get("type", "school").lower()
        is_ojt = attrs.get("ojt_indicator")
        is_flight = attrs.get("flight_indicator")
        is_correspondence = attrs.get("correspondence_indicator")

        if is_ojt or inst_type in ["ojt", "employer"]:
            parts.append("On-the-job training (OJT) or apprenticeship program approved for GI Bill benefits.")
        elif is_flight:
            parts.append("Flight training school approved for GI Bill benefits.")
        elif is_correspondence:
            parts.append("Correspondence/distance learning program approved for GI Bill benefits.")
        else:
            highest_degree = attrs.get("highest_degree")
            if highest_degree:
                parts.append(
                    f"Educational institution offering up to {highest_degree} degrees, approved for GI Bill benefits."
                )
            else:
                parts.append("Educational institution approved for GI Bill benefits.")

        # Accreditation info
        if attrs.get("accredited"):
            accred_type = attrs.get("accreditation_type")
            if accred_type:
                parts.append(f"Accredited institution ({accred_type}).")
            else:
                parts.append("Accredited institution.")

        # Yellow Ribbon
        if attrs.get("yellow_ribbon"):
            parts.append("Participates in the Yellow Ribbon Program for additional tuition assistance.")

        # Student veteran presence
        student_count = attrs.get("student_veteran")
        if student_count and int(student_count) > 0:
            parts.append(f"Student veteran population: {int(student_count):,} veterans.")

        student_veteran_group = attrs.get("student_veteran_group")
        if student_veteran_group:
            parts.append("Has a student veterans group on campus.")

        # Caution flags
        caution_flags = attrs.get("caution_flags", [])
        if caution_flags:
            flag_count = len(caution_flags)
            if flag_count == 1:
                parts.append("Note: This institution has 1 caution flag. Review details before enrolling.")
            else:
                parts.append(f"Note: This institution has {flag_count} caution flags. Review details before enrolling.")

        return " ".join(parts)

    def _get_approved_programs(self, attrs: dict[str, Any]) -> list[str]:
        """Get list of approved program types.

        Args:
            attrs: Institution attributes

        Returns:
            List of approved program type strings.
        """
        programs = []

        if attrs.get("highest_degree"):
            programs.append(f"Degree programs (up to {attrs.get('highest_degree')})")

        if attrs.get("ojt_indicator"):
            programs.append("On-the-Job Training (OJT)")

        if attrs.get("flight_indicator"):
            programs.append("Flight Training")

        if attrs.get("correspondence_indicator"):
            programs.append("Correspondence/Distance Learning")

        # If it has SCOs, it likely has approved programs
        if attrs.get("school_certifying_officials") and not programs:
            programs.append("Approved education programs")

        return programs if programs else ["GI Bill approved programs"]

    def _build_eligibility(self, attrs: dict[str, Any]) -> str:
        """Build eligibility information.

        Args:
            attrs: Institution attributes

        Returns:
            Eligibility description string.
        """
        parts = ["Veterans with GI Bill benefits (Post-9/11 GI Bill, Montgomery GI Bill, VR&E, DEA)."]

        # Add Yellow Ribbon eligibility
        if attrs.get("yellow_ribbon"):
            parts.append(
                "Yellow Ribbon: Post-9/11 GI Bill recipients at 100% eligibility level may qualify "
                "for additional tuition coverage beyond the standard cap."
            )

        # OJT/Apprenticeship specific
        if attrs.get("ojt_indicator"):
            parts.append("OJT/Apprenticeship: Must be enrolled in a VA-approved training program with an employer.")

        return " ".join(parts)

    def _build_how_to_apply(self, attrs: dict[str, Any], programs: list[str]) -> str:
        """Build how to apply instructions.

        Args:
            attrs: Institution attributes
            programs: List of approved program types

        Returns:
            How to apply instructions string.
        """
        parts = []

        name = attrs.get("name", "the institution")

        parts.append(f"1. Apply to {name} directly.")
        parts.append("2. Apply for GI Bill benefits at va.gov/education/apply-for-education-benefits/.")
        parts.append("3. Submit your Certificate of Eligibility (COE) to the school's certifying official.")

        phone = attrs.get("phone")
        if phone:
            parts.append(f"Contact the school at {self._normalize_phone(phone)} for admissions info.")

        # Mention Yellow Ribbon if applicable
        if attrs.get("yellow_ribbon"):
            parts.append("For Yellow Ribbon: Ask the school about their Yellow Ribbon agreement and available slots.")

        return " ".join(parts)

    def _extract_tags(
        self,
        attrs: dict[str, Any],
        is_ojt: bool,
        is_flight: bool,
        is_correspondence: bool,
    ) -> list[str]:
        """Extract relevant tags from institution attributes.

        Args:
            attrs: Institution attributes
            is_ojt: Whether this is an OJT program
            is_flight: Whether this is a flight school
            is_correspondence: Whether this is correspondence school

        Returns:
            List of tag strings.
        """
        tags = ["gi-bill", "training", "education"]

        # Program type tags
        if is_ojt:
            tags.extend(["ojt", "apprenticeship", "on-the-job-training"])
        if is_flight:
            tags.extend(["flight-training", "aviation"])
        if is_correspondence:
            tags.extend(["correspondence", "distance-learning", "online"])

        # Benefit tags
        if attrs.get("yellow_ribbon"):
            tags.append("yellow-ribbon")

        # Institution characteristic tags
        if attrs.get("accredited"):
            tags.append("accredited")

        if attrs.get("student_veteran_group"):
            tags.append("student-veteran-group")

        # Degree level tags
        highest_degree = attrs.get("highest_degree")
        if highest_degree:
            degree_lower = highest_degree.lower()
            if "doctorate" in degree_lower or "doctoral" in degree_lower:
                tags.append("doctorate")
            if "master" in degree_lower:
                tags.append("masters")
            if "bachelor" in degree_lower:
                tags.append("bachelors")
            if "associate" in degree_lower:
                tags.append("associates")
            if "certificate" in degree_lower:
                tags.append("certificate")

        # Caution flag tag
        if attrs.get("caution_flags"):
            tags.append("caution-flag")

        return list(set(tags))  # Deduplicate

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> "GIBillSchoolsConnector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
