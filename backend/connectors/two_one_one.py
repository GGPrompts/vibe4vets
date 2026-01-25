"""211 National Resource Database connector.

Loads veteran resources from pre-fetched 211.org data files.
Data is organized by state in backend/data/211/{STATE}.json
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class TwoOneOneConnector(BaseConnector):
    """Connector for 211.org veteran resources.

    This connector loads pre-fetched veteran resource data from 211.org,
    the national information and referral service. Data covers housing,
    employment, food assistance, mental health, legal aid, and other
    veteran-specific services.

    Data files are stored in backend/data/211/{STATE}.json
    """

    # Map 211 service tags to vibe4vets categories
    SERVICE_CATEGORY_MAP: dict[str, str] = {
        # Housing
        "housing": "housing",
        "housing assistance": "housing",
        "transitional housing": "housing",
        "emergency housing": "housing",
        "permanent housing": "housing",
        "homelessness prevention": "housing",
        "rental assistance": "housing",
        "shelter": "housing",
        "HUD-VASH": "housing",
        "SSVF": "housing",
        # Employment
        "employment": "employment",
        "employment services": "employment",
        "job training": "employment",
        "job placement": "employment",
        "career development": "employment",
        "vocational rehabilitation": "employment",
        "workforce development": "employment",
        # Food
        "food": "food",
        "food assistance": "food",
        "food pantry": "food",
        "meals": "food",
        "SNAP": "food",
        # Healthcare
        "healthcare": "healthcare",
        "medical": "healthcare",
        "health services": "healthcare",
        "VA healthcare": "healthcare",
        # Mental Health
        "mental health": "mental_health",
        "mental_health": "mental_health",
        "mental health services": "mental_health",
        "mental health support": "mental_health",
        "PTSD": "mental_health",
        "PTSD support": "mental_health",
        "counseling": "mental_health",
        "crisis support": "mental_health",
        "suicide prevention": "mental_health",
        "substance abuse": "mental_health",
        "substance abuse treatment": "mental_health",
        "addiction": "mental_health",
        # Benefits
        "benefits": "benefits",
        "benefits assistance": "benefits",
        "benefits counseling": "benefits",
        "VA benefits": "benefits",
        "disability compensation": "benefits",
        "pension": "benefits",
        "claims assistance": "benefits",
        # Legal
        "legal": "legal",
        "legal aid": "legal",
        "legal assistance": "legal",
        "legal services": "legal",
        # Education
        "education": "education",
        "education benefits": "education",
        "GI Bill": "education",
        "vocational training": "education",
        # Financial
        "financial assistance": "financial",
        "financial_aid": "financial",
        "emergency assistance": "financial",
        "utility assistance": "financial",
        # Community/Support
        "case management": "support_services",
        "supportive services": "support_services",
        "peer support": "support_services",
        "family support": "support_services",
        "community_support": "support_services",
        "referral": "support_services",
        "information": "support_services",
    }

    # States with data files (all 50 states + DC)
    AVAILABLE_STATES = [
        "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL",
        "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA",
        "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",
        "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI",
        "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV",
        "WY",
    ]

    def __init__(
        self,
        data_dir: Path | str | None = None,
        states: list[str] | None = None,
    ):
        """Initialize the connector.

        Args:
            data_dir: Directory containing state JSON files.
                      Defaults to backend/data/211/
            states: List of state codes to load. Defaults to all available.
        """
        if data_dir is None:
            # Default to backend/data/211/ relative to this file
            self.data_dir = Path(__file__).parent.parent / "data" / "211"
        else:
            self.data_dir = Path(data_dir)

        self.states = states or self.AVAILABLE_STATES
        self._resources: list[ResourceCandidate] = []

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="211 National Resource Database",
            url="https://www.211.org",
            tier=2,  # Established nonprofit network
            frequency="monthly",
            terms_url="https://www.211.org/pages/api",
            requires_auth=False,  # Using pre-fetched data
        )

    def run(self) -> list[ResourceCandidate]:
        """Load and return normalized resources from all state files."""
        self._resources = []

        for state in self.states:
            state_file = self.data_dir / f"{state}.json"
            if state_file.exists():
                self._load_state_file(state_file, state)

        return self._resources

    def _load_state_file(self, file_path: Path, state: str) -> None:
        """Load resources from a single state JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            # Log error but continue with other states
            print(f"Warning: Failed to load {file_path}: {e}")
            return

        fetched_at = self._parse_timestamp(data.get("fetched_at"))

        for resource in data.get("resources", []):
            candidate = self._convert_resource(resource, state, fetched_at)
            if candidate:
                self._resources.append(candidate)

    def _convert_resource(
        self,
        resource: dict[str, Any],
        state: str,
        fetched_at: datetime | None,
    ) -> ResourceCandidate | None:
        """Convert a 211 resource to a ResourceCandidate."""
        name = resource.get("name", "").strip()
        if not name:
            return None

        # Map services to categories
        raw_services = resource.get("services", [])
        categories = self._map_categories(raw_services)

        # Build description
        description = resource.get("description", "")
        if not description and raw_services:
            description = f"Services: {', '.join(raw_services)}"

        # Handle phone (may have alt)
        phone = resource.get("phone")
        phone_alt = resource.get("phone_alt")
        normalized_phone = self._normalize_phone(phone)

        # Store alt phone in raw_data for reference
        raw_with_normalized = resource.copy()
        if phone_alt:
            raw_with_normalized["phone_alt_normalized"] = self._normalize_phone(phone_alt)

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=resource.get("source_url", resource.get("website", "")),
            org_name=name,
            org_website=resource.get("website"),
            address=resource.get("address"),
            city=resource.get("city"),
            state=state,
            zip_code=resource.get("zip_code"),
            categories=categories if categories else ["veteran_services"],
            tags=raw_services,  # Preserve original service tags
            phone=normalized_phone,
            email=resource.get("email"),
            hours=resource.get("hours"),
            scope="state",
            states=[state],
            raw_data=raw_with_normalized,
            fetched_at=fetched_at,
        )

    def _map_categories(self, services: list[str]) -> list[str]:
        """Map 211 service tags to vibe4vets categories."""
        categories = set()

        for service in services:
            service_lower = service.lower().strip()
            if service_lower in self.SERVICE_CATEGORY_MAP:
                categories.add(self.SERVICE_CATEGORY_MAP[service_lower])
            else:
                # Try partial matching for compound terms
                for key, category in self.SERVICE_CATEGORY_MAP.items():
                    if key in service_lower or service_lower in key:
                        categories.add(category)
                        break

        return sorted(categories) if categories else []

    def _parse_timestamp(self, ts: str | None) -> datetime | None:
        """Parse ISO timestamp string to datetime."""
        if not ts:
            return None
        try:
            # Handle various ISO formats
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            return datetime.fromisoformat(ts)
        except ValueError:
            return datetime.now(UTC)

    def get_resources_by_state(self, state: str) -> list[ResourceCandidate]:
        """Get resources for a specific state."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.state == state]

    def get_resources_by_category(self, category: str) -> list[ResourceCandidate]:
        """Get resources matching a category."""
        if not self._resources:
            self.run()
        return [
            r for r in self._resources
            if r.categories and category in r.categories
        ]

    def stats(self) -> dict[str, Any]:
        """Return statistics about loaded resources."""
        if not self._resources:
            self.run()

        by_state: dict[str, int] = {}
        by_category: dict[str, int] = {}

        for r in self._resources:
            # Count by state
            if r.state:
                by_state[r.state] = by_state.get(r.state, 0) + 1

            # Count by category
            for cat in r.categories or []:
                by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_resources": len(self._resources),
            "states_covered": len(by_state),
            "by_state": dict(sorted(by_state.items())),
            "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        }
