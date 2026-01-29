"""DAV (Disabled American Veterans) chapters connector.

Imports DAV chapter and National Service Office data from curated reference data.
DAV is the leading nonprofit empowering disabled veterans through free benefits
assistance, advocacy, and education.

DAV locations include:
- ~1,900 local chapters providing peer support and community
- 88 National Service Offices with VA-certified claims assistance
- 38 Transition Service Offices at military installations
- 198 Hospital Service Coordinator Offices at VA medical centers
- DAV Transportation Network providing free rides to VA appointments

Sources:
- DAV Chapter Locator: https://locators.dav.org/ChapterUnitLocator
- DAV NSO Locator: https://locators.dav.org/NsoLocator
- DAV Transportation: https://www.dav.org/get-help-now/dav-transportation-network/
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# State code to name mapping
STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "PR": "Puerto Rico",
    "GU": "Guam",
    "VI": "Virgin Islands",
    "AS": "American Samoa",
}


class DAVChaptersConnector(BaseConnector):
    """Connector for DAV (Disabled American Veterans) chapter and office data.

    Parses the dav_chapters.json file containing:
    - Local DAV chapters providing peer support and community
    - National Service Offices (NSOs) with VA-certified claims representatives
    - Transportation network locations offering free rides to VA appointments

    DAV is unique among VSOs for:
    - Service-connected disability requirement for membership
    - Free VA claims assistance regardless of membership
    - Extensive transportation network (235,000+ rides annually)
    - Hospital Service Coordinators at VA medical centers

    Data fields:
        - location_type: chapter, nso, tso, hsc, or transportation
        - chapter_number: Chapter/office number (if applicable)
        - name: Location name
        - address, city, state, zip_code: Location address
        - phone: Contact phone number
        - email: Contact email (if available)
        - website: Location website (if available)
        - services: List of services offered
        - meeting_schedule: Meeting schedule (chapters only)
        - hours: Operating hours
        - contact_name: Primary contact person
        - has_transportation: Whether this location offers DAV rides
        - va_facility_served: VA facility served (for transportation)
    """

    DEFAULT_DATA_PATH = "data/reference/dav_chapters.json"

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
            name="DAV Chapters and National Service Offices",
            url="https://locators.dav.org/ChapterUnitLocator",
            tier=2,  # Established nonprofit VSO
            frequency="quarterly",  # Chapters change infrequently
            terms_url="https://www.dav.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse DAV location data from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"DAV chapters data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for location in data.get("locations", []):
            candidate = self._parse_location(
                location_type=location.get("location_type", "chapter"),
                chapter_number=location.get("chapter_number"),
                name=location.get("name"),
                address=location.get("address"),
                city=location.get("city"),
                state=location.get("state"),
                zip_code=location.get("zip_code"),
                phone=location.get("phone"),
                email=location.get("email"),
                website=location.get("website"),
                services=location.get("services", []),
                meeting_schedule=location.get("meeting_schedule"),
                hours=location.get("hours"),
                contact_name=location.get("contact_name"),
                has_transportation=location.get("has_transportation", False),
                va_facility_served=location.get("va_facility_served"),
                fetched_at=now,
            )
            resources.append(candidate)

        return resources

    def _parse_location(
        self,
        location_type: str,
        chapter_number: str | None,
        name: str | None,
        address: str | None,
        city: str | None,
        state: str | None,
        zip_code: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
        services: list[str],
        meeting_schedule: str | None,
        hours: str | None,
        contact_name: str | None,
        has_transportation: bool,
        va_facility_served: str | None,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a DAV location entry into a ResourceCandidate.

        Args:
            location_type: Type of location (chapter, nso, tso, hsc, transportation)
            chapter_number: Chapter/office number
            name: Location name
            address: Street address
            city: City name
            state: Two-letter state code
            zip_code: ZIP code
            phone: Contact phone number
            email: Contact email address
            website: Location website
            services: List of services offered
            meeting_schedule: Meeting schedule information
            hours: Operating hours
            contact_name: Primary contact person
            has_transportation: Whether transportation is offered
            va_facility_served: VA facility served by transportation
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this DAV location.
        """
        state_name = STATE_NAMES.get(state) if state else None

        title = self._build_title(location_type, chapter_number, name, city, state)
        description = self._build_description(
            location_type,
            name,
            city,
            state_name,
            services,
            meeting_schedule,
            has_transportation,
            va_facility_served,
        )

        # Build full address string
        full_address = None
        if address:
            full_address = address
            if city and state and zip_code:
                full_address = f"{address}, {city}, {state} {zip_code}"
            elif city and state:
                full_address = f"{address}, {city}, {state}"

        # Build source URL based on location type
        source_url = website or self._get_locator_url(location_type)

        # Organization name for display
        org_name = self._build_org_name(location_type, chapter_number, name)

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=org_name,
            org_website=website or "https://www.dav.org",
            address=full_address,
            city=city,
            state=state,
            zip_code=zip_code,
            categories=["benefits", "supportServices"],
            tags=self._build_tags(location_type, state, services, has_transportation),
            phone=self._normalize_phone(phone),
            email=email,
            hours=hours,
            eligibility=self._build_eligibility(location_type),
            how_to_apply=self._build_how_to_apply(location_type, name, phone, email, website, meeting_schedule),
            scope="local",
            states=[state] if state else None,
            raw_data={
                "location_type": location_type,
                "chapter_number": chapter_number,
                "name": name,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "phone": phone,
                "email": email,
                "website": website,
                "services": services,
                "meeting_schedule": meeting_schedule,
                "hours": hours,
                "contact_name": contact_name,
                "has_transportation": has_transportation,
                "va_facility_served": va_facility_served,
            },
            fetched_at=fetched_at,
        )

    def _get_locator_url(self, location_type: str) -> str:
        """Get the appropriate DAV locator URL for a location type.

        Args:
            location_type: Type of DAV location

        Returns:
            URL for the relevant DAV locator.
        """
        locator_urls = {
            "chapter": "https://locators.dav.org/ChapterUnitLocator",
            "nso": "https://locators.dav.org/NsoLocator",
            "tso": "https://locators.dav.org/NsoLocator",
            "hsc": "https://locators.dav.org/NsoLocator",
            "transportation": "https://www.dav.org/get-help-now/dav-transportation-network/",
        }
        return locator_urls.get(location_type, "https://www.dav.org/find-your-local-office/")

    def _build_org_name(
        self,
        location_type: str,
        chapter_number: str | None,
        name: str | None,
    ) -> str:
        """Build organization name for display.

        Args:
            location_type: Type of DAV location
            chapter_number: Chapter/office number
            name: Location name

        Returns:
            Formatted organization name.
        """
        if name:
            if "dav" in name.lower():
                return name
            return f"DAV {name}"

        type_names = {
            "chapter": f"DAV Chapter {chapter_number}" if chapter_number else "DAV Chapter",
            "nso": "DAV National Service Office",
            "tso": "DAV Transition Service Office",
            "hsc": "DAV Hospital Service Coordinator",
            "transportation": "DAV Transportation Network",
        }
        return type_names.get(location_type, "Disabled American Veterans")

    def _build_title(
        self,
        location_type: str,
        chapter_number: str | None,
        name: str | None,
        city: str | None,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            location_type: Type of DAV location
            chapter_number: Chapter/office number
            name: Location name
            city: City name
            state: State code

        Returns:
            Formatted title string.
        """
        location = f"({city}, {state})" if city and state else f"({state})" if state else ""

        if location_type == "chapter":
            if name:
                return f"DAV {name} {location}".strip()
            elif chapter_number:
                return f"DAV Chapter {chapter_number} {location}".strip()
            return f"DAV Chapter {location}".strip()

        elif location_type == "nso":
            return f"DAV National Service Office {location}".strip()

        elif location_type == "tso":
            if name:
                return f"DAV Transition Services - {name} {location}".strip()
            return f"DAV Transition Service Office {location}".strip()

        elif location_type == "hsc":
            if name:
                return f"DAV Hospital Service Coordinator - {name} {location}".strip()
            return f"DAV Hospital Service Coordinator {location}".strip()

        elif location_type == "transportation":
            if name:
                return f"DAV Transportation - {name} {location}".strip()
            return f"DAV Transportation Network {location}".strip()

        return f"DAV Location {location}".strip()

    def _build_description(
        self,
        location_type: str,
        name: str | None,
        city: str | None,
        state_name: str | None,
        services: list[str],
        meeting_schedule: str | None,
        has_transportation: bool,
        va_facility_served: str | None,
    ) -> str:
        """Build resource description.

        Args:
            location_type: Type of DAV location
            name: Location name
            city: City name
            state_name: Full state name
            services: List of services offered
            meeting_schedule: Meeting schedule information
            has_transportation: Whether transportation is offered
            va_facility_served: VA facility served by transportation

        Returns:
            Formatted description string.
        """
        parts = []
        location_str = f"in {city}, {state_name}" if city and state_name else ""

        if location_type == "chapter":
            parts.append(
                f"DAV (Disabled American Veterans) Chapter {location_str} provides "
                "peer support, service assistance, and community for disabled veterans.".strip()
            )
            parts.append(
                "DAV is dedicated to empowering veterans to lead high-quality lives "
                "with respect and dignity through free benefits assistance, advocacy, "
                "and education."
            )

        elif location_type == "nso":
            parts.append(
                f"DAV National Service Office {location_str} provides free, professional "
                "assistance with VA disability claims and benefits.".strip()
            )
            parts.append(
                "DAV National Service Officers are VA-certified representatives who "
                "help veterans file and appeal claims at no cost. They are among the "
                "most experienced claims advocates in the nation."
            )

        elif location_type == "tso":
            parts.append(
                f"DAV Transition Service Office {location_str} helps transitioning "
                "service members prepare for civilian life.".strip()
            )
            parts.append(
                "Transition Service Officers provide free one-on-one benefits counseling, "
                "help with VA registration, and guidance on education, employment, and "
                "healthcare benefits before separation from military service."
            )

        elif location_type == "hsc":
            parts.append(
                f"DAV Hospital Service Coordinator {location_str} assists veterans at VA medical facilities.".strip()
            )
            parts.append(
                "Hospital Service Coordinators help veterans navigate the VA healthcare "
                "system, connect with benefits, and access support services while "
                "receiving medical care."
            )

        elif location_type == "transportation":
            parts.append(
                f"DAV Transportation Network {location_str} provides free rides for "
                "veterans to VA medical appointments.".strip()
            )
            if va_facility_served:
                parts.append(f"Serves veterans with appointments at {va_facility_served}.")
            parts.append(
                "The DAV Transportation Network is the nation's largest voluntary "
                "network of free transportation for veterans, providing over 235,000 "
                "rides annually to VA medical appointments."
            )

        # Services offered
        if services:
            services_text = ", ".join(services[:6])
            if len(services) > 6:
                services_text += f", and {len(services) - 6} more"
            parts.append(f"Services include: {services_text}.")

        # Transportation note for chapters
        if has_transportation and location_type == "chapter":
            parts.append(
                "This chapter participates in the DAV Transportation Network, "
                "providing free rides to VA medical appointments."
            )

        # Meeting schedule for chapters
        if meeting_schedule and location_type == "chapter":
            parts.append(f"Meeting schedule: {meeting_schedule}")

        return " ".join(parts)

    def _build_eligibility(self, location_type: str) -> str:
        """Build eligibility description.

        Args:
            location_type: Type of DAV location

        Returns:
            Eligibility description string.
        """
        eligibility_map = {
            "chapter": (
                "DAV membership is open to men and women who were wounded, injured, "
                "or became ill while serving in the U.S. Armed Forces during wartime "
                "or peacetime and have an honorable discharge. Service-connected "
                "disability is required for membership. However, DAV chapters provide "
                "claims assistance and referrals to ALL veterans regardless of "
                "membership status or disability rating."
            ),
            "nso": (
                "DAV National Service Officers provide FREE claims assistance to ALL "
                "veterans, regardless of DAV membership status. No service-connected "
                "disability is required to receive help with VA claims. NSOs can help "
                "with initial claims, appeals, and accessing other VA benefits."
            ),
            "tso": (
                "DAV Transition Service Officers assist service members who are "
                "separating or retiring from military service. Available at military "
                "installations, TSOs provide benefits briefings and one-on-one "
                "counseling to help with the transition to civilian life."
            ),
            "hsc": (
                "DAV Hospital Service Coordinators assist any veteran receiving care "
                "at VA medical facilities. No membership or disability rating is "
                "required to receive assistance navigating VA healthcare services."
            ),
            "transportation": (
                "DAV Transportation is available to any veteran with an appointment "
                "at a VA medical facility. No membership, disability rating, or "
                "income requirement is needed. Rides are provided free of charge "
                "by volunteer drivers."
            ),
        }
        return eligibility_map.get(
            location_type,
            "DAV provides free assistance to all veterans regardless of membership "
            "status. Contact this location for specific eligibility information.",
        )

    def _build_how_to_apply(
        self,
        location_type: str,
        name: str | None,
        phone: str | None,
        email: str | None,
        website: str | None,
        meeting_schedule: str | None,
    ) -> str:
        """Build how to apply/contact instructions.

        Args:
            location_type: Type of DAV location
            name: Location name
            phone: Contact phone number
            email: Contact email address
            website: Location website
            meeting_schedule: Meeting schedule information

        Returns:
            How to apply instructions string.
        """
        parts = []
        location_display = name or f"this DAV {location_type}"

        if location_type == "transportation":
            parts.append(
                "To schedule a free ride to your VA appointment, call DAV at "
                "1-877-426-2838 (1-877-I AM A VET) or contact the VA medical "
                "facility where you have an appointment."
            )
            if phone:
                parts.append(f"Local transportation coordinator: {phone}")

        elif location_type in ("nso", "tso", "hsc"):
            if phone:
                parts.append(
                    f"Call {location_display} at {phone} for a free appointment to discuss your VA benefits and claims."
                )
            else:
                parts.append(
                    f"Contact {location_display} for a free appointment to discuss your VA benefits and claims."
                )
            parts.append(
                "No appointment is necessary for walk-ins, but calling ahead ensures "
                "a representative is available to assist you."
            )

        else:  # chapter
            if phone:
                parts.append(f"Call {location_display} at {phone} to inquire about services or membership.")
            elif email:
                parts.append(f"Email {location_display} at {email} to inquire about services or membership.")
            else:
                parts.append(f"Contact {location_display} to inquire about services or membership.")

            if meeting_schedule:
                parts.append(f"Veterans are welcome to attend chapter meetings: {meeting_schedule}")

        # Additional contact methods
        if email and phone:
            parts.append(f"Email: {email}")
        if website:
            parts.append(f"Website: {website}")

        # National DAV contact
        parts.append("For general DAV assistance, call the national helpline at 1-877-426-2838 (1-877-I AM A VET).")

        return " ".join(parts)

    def _build_tags(
        self,
        location_type: str,
        state: str | None,
        services: list[str],
        has_transportation: bool,
    ) -> list[str]:
        """Build tags list.

        Args:
            location_type: Type of DAV location
            state: Two-letter state code
            services: List of services offered
            has_transportation: Whether transportation is offered

        Returns:
            List of tag strings.
        """
        tags = [
            "dav",
            "disabled-american-veterans",
            "vso",
            "veterans-service-organization",
            "disability",
        ]

        # Location type tags
        type_tags = {
            "chapter": ["dav-chapter", "peer-support", "community"],
            "nso": ["national-service-office", "va-claims-assistance", "benefits-advocacy"],
            "tso": ["transition-services", "military-transition", "separation-benefits"],
            "hsc": ["hospital-services", "va-healthcare", "patient-advocacy"],
            "transportation": ["transportation", "free-rides", "medical-appointments"],
        }
        tags.extend(type_tags.get(location_type, []))

        # Transportation tag
        if has_transportation:
            tags.append("dav-transportation")
            tags.append("free-rides")

        if state:
            tags.append(f"state-{state.lower()}")

        # Service-based tags
        services_lower = " ".join(services).lower()
        service_tag_map = {
            "claims": "va-claims-assistance",
            "benefits": "benefits-assistance",
            "transportation": "transportation-assistance",
            "employment": "employment-services",
            "housing": "housing-assistance",
            "peer support": "peer-support",
            "counseling": "counseling-services",
        }

        for keyword, tag in service_tag_map.items():
            if keyword in services_lower and tag not in tags:
                tags.append(tag)

        return list(set(tags))  # Deduplicate
