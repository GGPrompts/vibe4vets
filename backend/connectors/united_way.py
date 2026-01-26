"""United Way connector for regional veteran resources and Missions United programs.

United Way chapters operate regional nonprofit directories, often integrated with 211.
Many chapters run Missions United, a veteran-focused initiative providing employment,
housing, and support services to veterans and military families.

This connector loads pre-fetched data from regional United Way directories.
Data is organized by region in backend/data/united_way/{REGION}.json
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class UnitedWayConnector(BaseConnector):
    """Connector for United Way regional veteran resources.

    This connector loads pre-fetched veteran resource data from regional
    United Way chapters, with a focus on Missions United programs and
    other veteran-specific initiatives.

    Regional chapters covered:
    - DMV (DC/MD/VA) - United Way National Capital Area
    - South Florida - Multiple chapters with strong Missions United presence
    - Texas - Multiple regional chapters
    - California - Regional chapters

    Data files are stored in backend/data/united_way/{REGION}.json
    """

    # Map United Way service categories to vibe4vets categories
    SERVICE_CATEGORY_MAP: dict[str, str] = {
        # Missions United core services
        "missions united": "employment",
        "veteran employment": "employment",
        "career coaching": "employment",
        "job readiness": "employment",
        "resume assistance": "employment",
        "interview preparation": "employment",
        "job placement": "employment",
        "career transition": "employment",
        "workforce development": "employment",
        "job training": "employment",
        "vocational training": "employment",
        # Housing
        "housing assistance": "housing",
        "housing stability": "housing",
        "rental assistance": "housing",
        "emergency housing": "housing",
        "homelessness prevention": "housing",
        "transitional housing": "housing",
        "permanent supportive housing": "housing",
        "HUD-VASH": "housing",
        "SSVF": "housing",
        # Financial
        "financial coaching": "financial",
        "financial assistance": "financial",
        "emergency financial aid": "financial",
        "utility assistance": "financial",
        "financial literacy": "financial",
        "budget counseling": "financial",
        "tax preparation": "financial",
        "VITA": "financial",
        # Benefits
        "benefits navigation": "benefits",
        "benefits counseling": "benefits",
        "VA benefits": "benefits",
        "claims assistance": "benefits",
        "disability compensation": "benefits",
        # Mental Health
        "mental health": "mental_health",
        "counseling": "mental_health",
        "PTSD support": "mental_health",
        "peer support": "mental_health",
        "crisis intervention": "mental_health",
        "substance abuse": "mental_health",
        # Legal
        "legal assistance": "legal",
        "legal aid": "legal",
        "legal services": "legal",
        # Education
        "education assistance": "education",
        "GI Bill assistance": "education",
        "education benefits": "education",
        "college readiness": "education",
        # Healthcare
        "healthcare navigation": "healthcare",
        "health services": "healthcare",
        "medical assistance": "healthcare",
        # Family Services
        "family support": "support_services",
        "caregiver support": "support_services",
        "childcare assistance": "support_services",
        "military family support": "support_services",
        # Case Management
        "case management": "support_services",
        "resource navigation": "support_services",
        "referral services": "support_services",
        "veteran services": "support_services",
    }

    # United Way regions with data files
    # Key: region code, Value: (states covered, description)
    REGIONS: dict[str, tuple[list[str], str]] = {
        "dmv": (["DC", "MD", "VA"], "National Capital Area"),
        "south_florida": (["FL"], "South Florida / Broward / Miami / Palm Beach"),
        "central_florida": (["FL"], "Central Florida / Heart of Florida"),
        "texas_tarrant": (["TX"], "Tarrant County / Fort Worth"),
        "texas_houston": (["TX"], "Greater Houston"),
        "california_bay": (["CA"], "Bay Area"),
        "california_la": (["CA"], "Greater Los Angeles"),
        "georgia": (["GA"], "Metro Atlanta / Central Georgia"),
        "ohio": (["OH"], "Columbus / Central Ohio"),
        "north_carolina": (["NC"], "Central Carolinas / Charlotte"),
        "long_island": (["NY"], "Long Island"),
        "lake_sumter": (["FL"], "Lake and Sumter Counties"),
    }

    def __init__(
        self,
        data_dir: Path | str | None = None,
        regions: list[str] | None = None,
    ):
        """Initialize the connector.

        Args:
            data_dir: Directory containing region JSON files.
                      Defaults to backend/data/united_way/
            regions: List of region codes to load. Defaults to all available.
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent / "data" / "united_way"
        else:
            self.data_dir = Path(data_dir)

        self.regions = regions or list(self.REGIONS.keys())
        self._resources: list[ResourceCandidate] = []

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="United Way Regional Directories",
            url="https://www.unitedway.org/local/united-states",
            tier=2,  # Established nonprofit network
            frequency="monthly",
            terms_url="https://www.unitedway.org/privacy-policy",
            requires_auth=False,  # Using pre-fetched data
        )

    def run(self) -> list[ResourceCandidate]:
        """Load and return normalized resources from all region files."""
        self._resources = []

        for region in self.regions:
            region_file = self.data_dir / f"{region}.json"
            if region_file.exists():
                self._load_region_file(region_file, region)

        return self._resources

    def _load_region_file(self, file_path: Path, region: str) -> None:
        """Load resources from a single region JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load {file_path}: {e}")
            return

        fetched_at = self._parse_timestamp(data.get("fetched_at"))
        region_info = self.REGIONS.get(region, ([], region))

        for resource in data.get("resources", []):
            candidate = self._convert_resource(resource, region, region_info, fetched_at)
            if candidate:
                self._resources.append(candidate)

    def _convert_resource(
        self,
        resource: dict[str, Any],
        region: str,
        region_info: tuple[list[str], str],
        fetched_at: datetime | None,
    ) -> ResourceCandidate | None:
        """Convert a United Way resource to a ResourceCandidate."""
        name = resource.get("name", "").strip()
        if not name:
            return None

        states, region_name = region_info
        raw_services = resource.get("services", [])
        categories = self._map_categories(raw_services)

        # Build description
        description = resource.get("description", "")
        if not description:
            if raw_services:
                description = f"United Way {region_name} program. Services: {', '.join(raw_services)}"
            else:
                description = f"United Way {region_name} veteran resource."

        # Determine state - prefer explicit state, fall back to region's primary state
        state = resource.get("state")
        if not state and states:
            # Use city to guess state if available
            city = resource.get("city", "").lower()
            if "washington" in city or "arlington" in city or "alexandria" in city:
                state = "DC" if "washington" in city else "VA"
            elif city:
                state = states[0]  # Default to first state in region

        # Normalize state
        if state:
            state = self._normalize_state(state)

        # Check if this is a Missions United program
        is_missions_united = self._is_missions_united(resource)

        # Phone handling
        phone = resource.get("phone")
        normalized_phone = self._normalize_phone(phone)

        # Build tags
        tags = self._build_tags(resource, is_missions_united, region)

        # Determine scope
        scope = resource.get("scope", "local")
        if len(states) > 1:
            scope = "regional"

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=resource.get("source_url", resource.get("website", "")),
            org_name=resource.get("org_name", "United Way"),
            org_website=resource.get("website"),
            address=resource.get("address"),
            city=resource.get("city"),
            state=state,
            zip_code=resource.get("zip_code"),
            categories=categories if categories else ["support_services"],
            tags=tags,
            phone=normalized_phone,
            email=resource.get("email"),
            hours=resource.get("hours"),
            eligibility=resource.get("eligibility", self._default_eligibility(is_missions_united)),
            how_to_apply=resource.get("how_to_apply", self._default_how_to_apply()),
            scope=scope,
            states=states if states else None,
            raw_data=resource,
            fetched_at=fetched_at,
        )

    def _map_categories(self, services: list[str]) -> list[str]:
        """Map United Way service tags to vibe4vets categories."""
        categories = set()

        for service in services:
            service_lower = service.lower().strip()
            if service_lower in self.SERVICE_CATEGORY_MAP:
                categories.add(self.SERVICE_CATEGORY_MAP[service_lower])
            else:
                # Try partial matching
                for key, category in self.SERVICE_CATEGORY_MAP.items():
                    if key in service_lower or service_lower in key:
                        categories.add(category)
                        break

        return sorted(categories) if categories else []

    def _is_missions_united(self, resource: dict[str, Any]) -> bool:
        """Check if resource is a Missions United program."""
        name = resource.get("name", "").lower()
        description = resource.get("description", "").lower()
        services = [s.lower() for s in resource.get("services", [])]

        missions_terms = ["missions united", "mission united", "missions-united"]

        for term in missions_terms:
            if term in name or term in description:
                return True
            for service in services:
                if term in service:
                    return True

        return resource.get("is_missions_united", False)

    def _build_tags(
        self,
        resource: dict[str, Any],
        is_missions_united: bool,
        region: str,
    ) -> list[str]:
        """Build tags list for a resource."""
        tags = ["united-way"]

        if is_missions_united:
            tags.append("missions-united")
            tags.append("veteran-employment")

        # Add original service tags
        tags.extend(resource.get("services", []))

        # Add region tag
        tags.append(f"uw-{region}")

        # Add program type if specified
        program_type = resource.get("program_type")
        if program_type:
            tags.append(program_type.lower().replace(" ", "-"))

        return list(dict.fromkeys(tags))  # Dedupe while preserving order

    def _default_eligibility(self, is_missions_united: bool) -> str:
        """Return default eligibility text."""
        if is_missions_united:
            return (
                "Veterans, active-duty service members, National Guard, Reservists, "
                "and their families. Some programs may have additional income or "
                "service requirements."
            )
        return (
            "Eligibility varies by program. Many United Way veteran programs "
            "serve all veterans and their families. Contact the program directly "
            "for specific eligibility requirements."
        )

    def _default_how_to_apply(self) -> str:
        """Return default application instructions."""
        return (
            "Contact the program directly by phone or visit their website. "
            "You can also dial 211 for referral assistance."
        )

    def _parse_timestamp(self, ts: str | None) -> datetime | None:
        """Parse ISO timestamp string to datetime."""
        if not ts:
            return None
        try:
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            return datetime.fromisoformat(ts)
        except ValueError:
            return datetime.now(UTC)

    def get_resources_by_region(self, region: str) -> list[ResourceCandidate]:
        """Get resources for a specific region."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.raw_data and r.raw_data.get("region") == region]

    def get_resources_by_state(self, state: str) -> list[ResourceCandidate]:
        """Get resources for a specific state."""
        if not self._resources:
            self.run()
        state = self._normalize_state(state) or state
        return [r for r in self._resources if r.state == state]

    def get_missions_united_resources(self) -> list[ResourceCandidate]:
        """Get all Missions United program resources."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.tags and "missions-united" in r.tags]

    def get_resources_by_category(self, category: str) -> list[ResourceCandidate]:
        """Get resources matching a category."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.categories and category in r.categories]

    def stats(self) -> dict[str, Any]:
        """Return statistics about loaded resources."""
        if not self._resources:
            self.run()

        by_region: dict[str, int] = {}
        by_state: dict[str, int] = {}
        by_category: dict[str, int] = {}
        missions_united_count = 0

        for r in self._resources:
            # Count by state
            if r.state:
                by_state[r.state] = by_state.get(r.state, 0) + 1

            # Count Missions United
            if r.tags and "missions-united" in r.tags:
                missions_united_count += 1

            # Count by category
            for cat in r.categories or []:
                by_category[cat] = by_category.get(cat, 0) + 1

        # Count regions from raw_data or infer from file
        for region in self.regions:
            region_file = self.data_dir / f"{region}.json"
            if region_file.exists():
                count = len([r for r in self._resources if f"uw-{region}" in (r.tags or [])])
                if count > 0:
                    by_region[region] = count

        return {
            "total_resources": len(self._resources),
            "missions_united_programs": missions_united_count,
            "regions_covered": len(by_region),
            "states_covered": len(by_state),
            "by_region": dict(sorted(by_region.items())),
            "by_state": dict(sorted(by_state.items())),
            "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        }
