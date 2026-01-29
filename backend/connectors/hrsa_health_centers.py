"""HRSA Health Centers connector.

Imports Federally Qualified Health Center (FQHC) data from the HRSA Data Warehouse.
Source: https://data.hrsa.gov/

HRSA-supported health centers provide comprehensive, culturally competent, quality
primary health care services to medically underserved communities and vulnerable
populations. Many health centers serve Veterans, including those without VA eligibility.

Data includes:
- ~15,000+ service delivery sites nationwide
- Name, address, phone, website, hours
- Health center type (FQHC, Look-Alike)
- Services and specializations
"""

import csv
import io
from datetime import UTC, datetime
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class HRSAHealthCentersConnector(BaseConnector):
    """Connector for HRSA Health Center Service Delivery Sites.

    Downloads and parses the Health Center Service Delivery and Look-Alike Sites
    CSV file from HRSA Data Warehouse. This includes Federally Qualified Health
    Centers (FQHCs) that provide affordable primary care.

    Veterans can access FQHCs regardless of VA eligibility, making these an
    important resource for Veterans who:
    - Have other-than-honorable discharges
    - Are not enrolled in VA healthcare
    - Need care in areas without nearby VA facilities
    - Need immediate care without VA appointment wait times
    """

    # Direct CSV download URL from HRSA Data Warehouse
    CSV_URL = "https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv"

    # Only include active sites
    ACTIVE_STATUS = "Active"

    def __init__(self, timeout: float = 60.0):
        """Initialize the connector.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="HRSA Health Center Service Delivery Sites",
            url="https://data.hrsa.gov/topics/health-centers",
            tier=1,  # Official federal government source (HHS/HRSA)
            frequency="daily",  # HRSA updates this data daily
            terms_url="https://data.hrsa.gov/about/terms-of-use",
            requires_auth=False,  # Public CSV download
        )

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    def run(self) -> list[ResourceCandidate]:
        """Fetch and parse HRSA Health Center data.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        resources: list[ResourceCandidate] = []
        try:
            client = self._get_client()

            # Download CSV
            response = client.get(self.CSV_URL)
            response.raise_for_status()

            # Parse CSV content
            content = response.text
            reader = csv.DictReader(io.StringIO(content))

            now = datetime.now(UTC)
            for row in reader:
                # Skip inactive sites
                if row.get("Site Status Description") != self.ACTIVE_STATUS:
                    continue

                candidate = self._parse_site(row, now)
                if candidate:
                    resources.append(candidate)

            return resources
        finally:
            self.close()

    def _parse_site(self, row: dict[str, Any], fetched_at: datetime) -> ResourceCandidate | None:
        """Parse a CSV row into a ResourceCandidate.

        Args:
            row: Dictionary from CSV DictReader
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate or None if data is invalid.
        """
        site_name = row.get("Site Name", "").strip()
        if not site_name:
            return None

        # Extract location data
        address = row.get("Site Address", "").strip()
        city = row.get("Site City", "").strip()
        state = row.get("Site State Abbreviation", "").strip()
        zip_code = row.get("Site Postal Code", "").strip()

        # Skip sites without valid location
        if not state:
            return None

        # Extract contact info
        phone = self._normalize_phone(row.get("Site Telephone Number", "").strip())
        website = row.get("Site Web Address", "").strip() or None

        # Extract health center info
        hc_name = row.get("Health Center Name", "").strip()
        hc_type = row.get("Health Center Type Description", "").strip()
        hc_type_code = row.get("Health Center Type", "").strip()
        location_type = row.get("Health Center Location Type Description", "").strip()
        location_setting = row.get("Health Center Service Delivery Site Location Setting Description", "").strip()

        # Extract hours
        hours_per_week = row.get("Operating Hours per Week", "").strip()
        hours = self._format_hours(hours_per_week)

        # Build title
        title = self._build_title(site_name, city, state)

        # Build description
        description = self._build_description(
            site_name=site_name,
            hc_name=hc_name,
            hc_type=hc_type,
            location_setting=location_setting,
            city=city,
            state=state,
            hours_per_week=hours_per_week,
        )

        # Determine organization
        org_name = hc_name if hc_name else site_name

        # Build source URL
        source_url = website if website else "https://findahealthcenter.hrsa.gov/"

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=source_url,
            org_name=org_name,
            org_website=website,
            address=address if address else None,
            city=city if city else None,
            state=self._normalize_state(state),
            zip_code=zip_code if zip_code else None,
            categories=["healthcare"],
            tags=self._build_tags(hc_type_code, location_type, location_setting),
            phone=phone,
            hours=hours,
            eligibility=self._build_eligibility(hc_type),
            how_to_apply=self._build_how_to_apply(site_name, phone),
            scope="local",  # Each site is a physical location
            states=[state] if state else None,
            raw_data={
                "health_center_number": row.get("Health Center Number", ""),
                "bhcmis_id": row.get("BHCMIS Organization Identification Number", ""),
                "npi": row.get("FQHC Site NPI Number", ""),
                "medicare_billing": row.get("FQHC Site Medicare Billing Number", ""),
                "location_id": row.get("Health Center Location Identification Number", ""),
                "operator_type": row.get("Health Center Operator Description", ""),
                "county": row.get("Complete County Name", ""),
                "hhs_region": row.get("HHS Region Code", ""),
                "congressional_district": row.get("Congressional District Code", ""),
                "latitude": row.get("Geocoding Artifact Address Primary Y Coordinate", ""),
                "longitude": row.get("Geocoding Artifact Address Primary X Coordinate", ""),
            },
            fetched_at=fetched_at,
        )

    def _build_title(self, site_name: str, city: str, state: str) -> str:
        """Build resource title.

        Args:
            site_name: Name of the health center site
            city: City name
            state: State abbreviation

        Returns:
            Formatted title string.
        """
        # Clean up the site name if it's very long
        if len(site_name) > 60:
            # Truncate and add location
            return f"{site_name[:57]}... ({state})"

        if city and state:
            return f"{site_name} - {city}, {state}"
        elif state:
            return f"{site_name} ({state})"
        return site_name

    def _build_description(
        self,
        site_name: str,
        hc_name: str,
        hc_type: str,
        location_setting: str,
        city: str,
        state: str,
        hours_per_week: str,
    ) -> str:
        """Build resource description.

        Args:
            site_name: Name of the health center site
            hc_name: Parent health center organization name
            hc_type: Type of health center (FQHC, Look-Alike)
            location_setting: Type of clinic setting
            city: City name
            state: State code
            hours_per_week: Operating hours per week

        Returns:
            Formatted description string.
        """
        parts = []

        # Main description based on type
        if "Federally Qualified Health Center" in hc_type:
            parts.append(
                f"{site_name} is a Federally Qualified Health Center (FQHC) "
                f"providing affordable, comprehensive primary health care."
            )
        elif "Look-Alike" in hc_type:
            parts.append(
                f"{site_name} is an FQHC Look-Alike providing affordable "
                f"primary health care services similar to federally funded health centers."
            )
        else:
            parts.append(f"{site_name} is an HRSA-supported health center providing primary health care services.")

        # Location info
        if city and state:
            parts.append(f"Located in {city}, {state}.")

        # Organization info
        if hc_name and hc_name != site_name:
            parts.append(f"Part of the {hc_name} health center network.")

        # Clinic type
        if location_setting and location_setting != "All Other Clinic Types":
            parts.append(f"Setting: {location_setting}.")

        # Hours
        if hours_per_week:
            try:
                hours_float = float(hours_per_week)
                if hours_float > 0:
                    parts.append(f"Open approximately {hours_float:.0f} hours per week.")
            except ValueError:
                pass

        # Veteran-specific info
        parts.append(
            "Health centers serve all patients regardless of ability to pay, "
            "using a sliding fee scale based on income. Veterans can access care here "
            "even without VA enrollment."
        )

        return " ".join(parts)

    def _build_eligibility(self, hc_type: str) -> str:
        """Build eligibility description.

        Args:
            hc_type: Type of health center

        Returns:
            Eligibility requirements string.
        """
        if "Look-Alike" in hc_type:
            return (
                "Open to all patients, including Veterans, regardless of insurance status "
                "or ability to pay. Uses a sliding fee scale based on income. "
                "Look-Alike health centers operate like FQHCs but may have different "
                "funding sources. Veterans do not need VA enrollment to receive care."
            )
        else:
            return (
                "Open to all patients, including Veterans, regardless of insurance status "
                "or ability to pay. Federally Qualified Health Centers use a sliding fee "
                "scale based on income - you will never be turned away. Veterans do not "
                "need VA enrollment to receive care at FQHCs."
            )

    def _build_how_to_apply(self, site_name: str, phone: str | None) -> str:
        """Build application instructions.

        Args:
            site_name: Name of the health center site
            phone: Phone number if available

        Returns:
            How to apply string.
        """
        parts = []

        if phone:
            parts.append(f"Call {site_name} at {phone} to schedule an appointment.")
        else:
            parts.append(f"Contact {site_name} to schedule an appointment.")

        parts.append(
            "Walk-ins may be accepted depending on availability. "
            "Bring proof of income for sliding fee scale eligibility. "
            "Most health centers accept Medicare, Medicaid, and private insurance, "
            "but will see patients without insurance."
        )

        return " ".join(parts)

    def _format_hours(self, hours_per_week: str) -> str | None:
        """Format hours information.

        Args:
            hours_per_week: Hours per week string from CSV

        Returns:
            Formatted hours string or None.
        """
        if not hours_per_week:
            return None

        try:
            hours_float = float(hours_per_week)
            if hours_float <= 0:
                return None

            # Estimate daily hours (assuming 5-6 day operation)
            if hours_float >= 60:
                return "Extended hours (60+ hours/week)"
            elif hours_float >= 45:
                return "Full-time hours (45-60 hours/week)"
            elif hours_float >= 30:
                return "Standard hours (30-45 hours/week)"
            else:
                return f"Limited hours (~{hours_float:.0f} hours/week)"
        except ValueError:
            return None

    def _build_tags(self, hc_type_code: str, location_type: str, location_setting: str) -> list[str]:
        """Build tags list.

        Args:
            hc_type_code: Health center type code
            location_type: Location type description
            location_setting: Location setting description

        Returns:
            List of tag strings.
        """
        tags = [
            "fqhc",
            "community-health-center",
            "primary-care",
            "sliding-fee-scale",
            "affordable-healthcare",
        ]

        # Add type-specific tags
        if "Federally Qualified Health Center" in hc_type_code:
            tags.append("federally-qualified")
        elif "Look-Alike" in hc_type_code:
            tags.append("fqhc-look-alike")

        # Add location type tags
        location_type_lower = location_type.lower() if location_type else ""
        if "permanent" in location_type_lower:
            tags.append("permanent-site")
        elif "seasonal" in location_type_lower:
            tags.append("seasonal-site")
        elif "mobile" in location_type_lower:
            tags.append("mobile-clinic")

        # Add setting-specific tags
        setting_lower = location_setting.lower() if location_setting else ""
        if "school" in setting_lower:
            tags.append("school-based")
        elif "homeless" in setting_lower:
            tags.append("homeless-services")
        elif "migrant" in setting_lower:
            tags.append("migrant-health")
        elif "public housing" in setting_lower:
            tags.append("public-housing")

        return tags

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
