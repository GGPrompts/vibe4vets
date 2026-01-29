"""211 National Resource Database connector.

Fetches Veteran resources from the 211 National Data Platform (NDP) API,
managed by United Way Worldwide. Uses the Open Referral HSDS standard.

API Documentation: https://apiportal.211.org/
Developer Portal: https://register.211.org/

When no API key is configured, falls back to loading pre-fetched data
from backend/data/211/{STATE}.json files.
"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

logger = logging.getLogger(__name__)


class TwoOneOneConnector(BaseConnector):
    """Connector for 211.org Veteran resources via NDP API.

    The 211 National Data Platform aggregates community social and human
    service data from local 211 call centers nationwide. Data follows the
    Open Referral Human Services Data Specification (HSDS).

    Modes:
        - API mode: When TWO_ONE_ONE_API_KEY is set, queries the NDP Search API
          for Veteran-relevant services using keyword searches.
        - File mode: Falls back to loading pre-fetched JSON files from
          backend/data/211/{STATE}.json when no API key is configured.

    Veteran Service Detection:
        Since HSDS doesn't have a dedicated Veteran flag, we identify
        Veteran-focused services by searching for keywords in descriptions,
        eligibility fields, and organization names.
    """

    # 211 NDP API base URL
    API_BASE_URL = "https://api.211.org"

    # Keywords to identify Veteran-focused services
    VETERAN_KEYWORDS = [
        "veteran",
        "veterans",
        "military",
        "armed forces",
        "service member",
        "servicemember",
        "active duty",
        "reserve",
        "national guard",
        "discharge",
        "vet center",
        "vso",
        "dav",
        "vfw",
        "american legion",
        "amvets",
        "purple heart",
        "wounded warrior",
        "gi bill",
        "va benefits",
        "va hospital",
        "va medical",
        "hud-vash",
        "ssvf",
        "stand down",
    ]

    # Map 211/HSDS taxonomy terms to Vibe4Vets categories
    # Based on Open Eligibility and 211HSIS taxonomies
    TAXONOMY_CATEGORY_MAP: dict[str, str] = {
        # Employment
        "employment": "employment",
        "employment services": "employment",
        "job training": "employment",
        "job placement": "employment",
        "career counseling": "employment",
        "career development": "employment",
        "vocational rehabilitation": "employment",
        "workforce development": "employment",
        "job search": "employment",
        "resume assistance": "employment",
        "interview preparation": "employment",
        "veteran employment": "employment",
        "military transition": "employment",
        # Training/Education
        "education": "education",
        "vocational training": "training",
        "job skills training": "training",
        "certification programs": "training",
        "apprenticeship": "training",
        "gi bill": "education",
        "college": "education",
        "scholarships": "education",
        # Housing
        "housing": "housing",
        "housing assistance": "housing",
        "transitional housing": "housing",
        "emergency housing": "housing",
        "permanent housing": "housing",
        "homelessness prevention": "housing",
        "rental assistance": "housing",
        "shelter": "housing",
        "hud-vash": "housing",
        "ssvf": "housing",
        "homeless services": "housing",
        "rapid rehousing": "housing",
        # Legal
        "legal": "legal",
        "legal aid": "legal",
        "legal assistance": "legal",
        "legal services": "legal",
        "va appeals": "legal",
        "discharge upgrade": "legal",
        "veterans court": "legal",
        # Food
        "food": "food",
        "food assistance": "food",
        "food pantry": "food",
        "food bank": "food",
        "meals": "food",
        "snap": "food",
        "nutrition": "food",
        # Benefits
        "benefits": "benefits",
        "benefits assistance": "benefits",
        "benefits counseling": "benefits",
        "va benefits": "benefits",
        "disability compensation": "benefits",
        "pension": "benefits",
        "claims assistance": "benefits",
        # Mental Health
        "mental health": "mentalHealth",
        "mental health services": "mentalHealth",
        "counseling": "mentalHealth",
        "ptsd": "mentalHealth",
        "ptsd support": "mentalHealth",
        "crisis support": "mentalHealth",
        "suicide prevention": "mentalHealth",
        "substance abuse": "mentalHealth",
        "substance abuse treatment": "mentalHealth",
        "addiction": "mentalHealth",
        "behavioral health": "mentalHealth",
        # Healthcare
        "healthcare": "healthcare",
        "medical": "healthcare",
        "health services": "healthcare",
        "health care": "healthcare",
        "primary care": "healthcare",
        "dental": "healthcare",
        "vision": "healthcare",
        # Financial
        "financial assistance": "financial",
        "emergency assistance": "financial",
        "utility assistance": "financial",
        "financial counseling": "financial",
        "financial literacy": "financial",
        # Support Services
        "case management": "supportServices",
        "supportive services": "supportServices",
        "peer support": "supportServices",
        "support services": "supportServices",
        "referral": "supportServices",
        "information": "supportServices",
        "community support": "supportServices",
        "advocacy": "supportServices",
        # Family
        "family support": "family",
        "caregiver support": "family",
        "childcare": "family",
        "military family": "family",
        "spouse support": "family",
        "dependent support": "family",
    }

    # Map service category names to Vibe4Vets categories (broader matching)
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
        "residential care": "housing",
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
        "skilled nursing care": "healthcare",
        "long-term care": "healthcare",
        "nursing home": "healthcare",
        # Mental Health
        "mental health": "mentalHealth",
        "mental_health": "mentalHealth",
        "mental health services": "mentalHealth",
        "mental health support": "mentalHealth",
        "PTSD": "mentalHealth",
        "PTSD support": "mentalHealth",
        "counseling": "mentalHealth",
        "crisis support": "mentalHealth",
        "suicide prevention": "mentalHealth",
        "substance abuse": "mentalHealth",
        "substance abuse treatment": "mentalHealth",
        "addiction": "mentalHealth",
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
        "vocational training": "training",
        # Financial
        "financial assistance": "financial",
        "financial_aid": "financial",
        "emergency assistance": "financial",
        "utility assistance": "financial",
        # Community/Support
        "case management": "supportServices",
        "supportive services": "supportServices",
        "peer support": "supportServices",
        "family support": "supportServices",
        "community_support": "supportServices",
        "referral": "supportServices",
        "information": "supportServices",
        "veteran support services": "supportServices",
        "advocacy": "supportServices",
        "member services": "supportServices",
        "community support": "supportServices",
        "disability support": "benefits",
        # Memorial/Cemetery
        "cemetery services": "supportServices",
        "burial services": "supportServices",
        "cemetery": "supportServices",
        "memorial services": "supportServices",
        # Business/Entrepreneurship
        "business development": "employment",
        "entrepreneurship support": "employment",
        "contract opportunities": "employment",
        "small business loans": "financial",
    }

    # States with data files (all 50 states + DC)
    AVAILABLE_STATES = [
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
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
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]

    def __init__(
        self,
        api_key: str | None = None,
        data_dir: Path | str | None = None,
        states: list[str] | None = None,
        timeout: float = 60.0,
        max_results_per_keyword: int = 500,
    ):
        """Initialize the connector.

        Args:
            api_key: 211 NDP API key. If not provided, reads from
                     TWO_ONE_ONE_API_KEY environment variable.
            data_dir: Directory containing state JSON files for fallback mode.
                      Defaults to backend/data/211/
            states: List of state codes to search/load. Defaults to all.
            timeout: HTTP request timeout in seconds.
            max_results_per_keyword: Maximum results to fetch per keyword search.
        """
        self.api_key = api_key or os.getenv("TWO_ONE_ONE_API_KEY")
        self.timeout = timeout
        self.max_results_per_keyword = max_results_per_keyword

        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent / "data" / "211"
        else:
            self.data_dir = Path(data_dir)

        self.states = states or self.AVAILABLE_STATES
        self._client: httpx.Client | None = None
        self._resources: list[ResourceCandidate] = []

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="211 National Resource Database",
            url="https://www.211.org",
            tier=4,  # Community directory tier
            frequency="daily",
            terms_url="https://www.211.org/pages/api",
            requires_auth=True,  # API requires key for full access
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
        """Fetch and return normalized Veteran resources.

        Returns:
            List of ResourceCandidate objects for Veteran-relevant services.
        """
        self._resources = []

        if self.api_key:
            logger.info("211 connector: Using API mode with configured key")
            try:
                self._fetch_from_api()
            except Exception as e:
                logger.warning(f"211 API fetch failed, falling back to files: {e}")
                self._load_from_files()
        else:
            logger.info("211 connector: No API key configured, using file mode")
            self._load_from_files()

        return self._resources

    def _fetch_from_api(self) -> None:
        """Fetch Veteran resources from 211 NDP Search API."""
        client = self._get_client()
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

        # Search for Veteran-relevant services using primary keywords
        # Use subset of most effective keywords to avoid API overload
        search_keywords = [
            "veteran",
            "veterans services",
            "military",
            "veteran housing",
            "veteran employment",
            "veteran benefits",
        ]

        seen_ids: set[str] = set()  # Track unique resources

        for keyword in search_keywords:
            logger.debug(f"211 API: Searching for '{keyword}'")

            try:
                results = self._search_api(client, headers, keyword)

                for result in results:
                    # Get unique identifier
                    result_id = self._get_result_id(result)
                    if result_id in seen_ids:
                        continue
                    seen_ids.add(result_id)

                    # Check if truly Veteran-relevant
                    if not self._is_veteran_service(result):
                        continue

                    candidate = self._parse_api_result(result)
                    if candidate:
                        self._resources.append(candidate)

            except httpx.HTTPStatusError as e:
                logger.warning(f"211 API search failed for '{keyword}': {e}")
            except Exception as e:
                logger.warning(f"211 API error for '{keyword}': {e}")

        logger.info(f"211 API: Found {len(self._resources)} Veteran resources")

    def _search_api(
        self,
        client: httpx.Client,
        headers: dict[str, str],
        query: str,
    ) -> list[dict[str, Any]]:
        """Query the 211 NDP Search API.

        Args:
            client: HTTP client
            headers: Request headers with API key
            query: Search query string

        Returns:
            List of search result dictionaries
        """
        all_results: list[dict[str, Any]] = []
        offset = 0
        limit = 100  # API page size

        while len(all_results) < self.max_results_per_keyword:
            params = {
                "query": query,
                "limit": limit,
                "offset": offset,
            }

            response = client.get(
                f"{self.API_BASE_URL}/api/v1/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            all_results.extend(results)
            offset += limit

            # Stop if we got fewer results than requested (no more pages)
            if len(results) < limit:
                break

        return all_results[: self.max_results_per_keyword]

    def _get_result_id(self, result: dict[str, Any]) -> str:
        """Get unique identifier for a search result."""
        # Try various ID fields that may be present in HSDS data
        if "id" in result:
            return str(result["id"])
        if "organization" in result and "id" in result["organization"]:
            return f"org-{result['organization']['id']}"
        if "service" in result and "id" in result["service"]:
            return f"svc-{result['service']['id']}"
        # Fallback to name-based hash
        name = result.get("name", result.get("organization", {}).get("name", ""))
        return f"hash-{hash(name)}"

    def _is_veteran_service(self, result: dict[str, Any]) -> bool:
        """Check if a search result is Veteran-relevant.

        Since HSDS doesn't have a dedicated Veteran flag, we check
        for Veteran-related keywords in key text fields.

        Args:
            result: API search result dictionary

        Returns:
            True if the service appears to be Veteran-focused
        """
        # Build searchable text from all relevant fields
        searchable_parts = []

        # Organization info
        org = result.get("organization", {})
        searchable_parts.append(org.get("name", ""))
        searchable_parts.append(org.get("description", ""))

        # Service info
        service = result.get("service", {})
        if isinstance(service, dict):
            searchable_parts.append(service.get("name", ""))
            searchable_parts.append(service.get("description", ""))
            searchable_parts.append(service.get("eligibility", ""))

        # Direct fields
        searchable_parts.append(result.get("name", ""))
        searchable_parts.append(result.get("description", ""))
        searchable_parts.append(result.get("eligibility", ""))

        # Taxonomy terms
        taxonomy = result.get("taxonomy", [])
        if isinstance(taxonomy, list):
            for term in taxonomy:
                if isinstance(term, dict):
                    searchable_parts.append(term.get("name", ""))
                elif isinstance(term, str):
                    searchable_parts.append(term)

        # Combine and lowercase for matching
        searchable_text = " ".join(str(p) for p in searchable_parts if p).lower()

        # Check for Veteran keywords
        return any(kw in searchable_text for kw in self.VETERAN_KEYWORDS)

    def _parse_api_result(self, result: dict[str, Any]) -> ResourceCandidate | None:
        """Parse an API search result into a ResourceCandidate.

        Maps HSDS data fields to Vibe4Vets ResourceCandidate format.

        Args:
            result: API search result dictionary

        Returns:
            ResourceCandidate or None if data is invalid
        """
        now = datetime.now(UTC)

        # Extract organization info
        org = result.get("organization", {})
        org_name = org.get("name", "") or result.get("name", "")
        if not org_name:
            return None

        # Extract service info
        service = result.get("service", {})
        if isinstance(service, dict):
            service_name = service.get("name", "")
            service_description = service.get("description", "")
            service_eligibility = service.get("eligibility", "")
        else:
            service_name = ""
            service_description = ""
            service_eligibility = ""

        # Build title - prefer service name if different from org
        title = f"{service_name} - {org_name}" if service_name and service_name != org_name else org_name

        # Build description
        description = (
            service_description
            or org.get("description", "")
            or result.get("description", "")
            or f"Community resource provided by {org_name}."
        )

        # Extract location info
        location = result.get("location", {})
        if isinstance(location, dict):
            address = location.get("address", "")
            city = location.get("city", "")
            state = location.get("state", "")
            zip_code = location.get("postal_code", location.get("zip", ""))
            latitude = location.get("latitude")
            longitude = location.get("longitude")
        else:
            address = ""
            city = ""
            state = ""
            zip_code = ""
            latitude = None
            longitude = None

        # Normalize state
        state = self._normalize_state(state) if state else None

        # Extract contact info
        contact = result.get("contact", {})
        if isinstance(contact, dict):
            phone = contact.get("phone", "")
            email = contact.get("email", "")
            website = contact.get("website", "") or org.get("website", "")
        else:
            phone = result.get("phone", "")
            email = result.get("email", "")
            website = org.get("website", "") or result.get("website", "")

        # Normalize phone
        phone = self._normalize_phone(phone) if phone else None

        # Map taxonomy to categories
        categories = self._extract_categories(result)
        if not categories:
            categories = ["supportServices"]  # Default category

        # Build eligibility text
        eligibility = service_eligibility or result.get("eligibility", "")
        if not eligibility:
            eligibility = (
                "Contact the organization directly for eligibility requirements. "
                "Many 211-listed services are available to Veterans and their families."
            )

        # Build source URL - use organization website or 211.org reference
        source_url = website or f"https://www.211.org/search?q={org_name.replace(' ', '+')}"

        # Build tags from taxonomy
        tags = self._extract_tags(result)

        return ResourceCandidate(
            title=title[:200],  # Truncate very long titles
            description=description[:2000],  # Truncate very long descriptions
            source_url=source_url,
            org_name=org_name,
            org_website=website if website else None,
            address=address if address else None,
            city=city if city else None,
            state=state,
            zip_code=zip_code if zip_code else None,
            categories=categories,
            tags=tags,
            phone=phone,
            email=email if email else None,
            eligibility=eligibility if eligibility else None,
            scope="local" if city or address else "state" if state else "national",
            states=[state] if state else None,
            raw_data={
                "source": "211_api",
                "result_id": self._get_result_id(result),
                "latitude": latitude,
                "longitude": longitude,
                "original": result,
            },
            fetched_at=now,
        )

    def _extract_categories(self, result: dict[str, Any]) -> list[str]:
        """Extract and map categories from API result."""
        categories: set[str] = set()

        # Check taxonomy terms
        taxonomy = result.get("taxonomy", [])
        if isinstance(taxonomy, list):
            for term in taxonomy:
                term_name = ""
                if isinstance(term, dict):
                    term_name = term.get("name", "").lower()
                elif isinstance(term, str):
                    term_name = term.lower()

                if term_name:
                    # Try exact match first
                    if term_name in self.TAXONOMY_CATEGORY_MAP:
                        categories.add(self.TAXONOMY_CATEGORY_MAP[term_name])
                    else:
                        # Try partial match
                        for key, category in self.TAXONOMY_CATEGORY_MAP.items():
                            if key in term_name or term_name in key:
                                categories.add(category)
                                break

        # Check service category if present
        service = result.get("service", {})
        if isinstance(service, dict):
            service_category = service.get("category", "").lower()
            if service_category in self.TAXONOMY_CATEGORY_MAP:
                categories.add(self.TAXONOMY_CATEGORY_MAP[service_category])

        # Infer from description keywords
        description = (result.get("description", "") + " " + result.get("service", {}).get("description", "")).lower()

        category_keywords = {
            "employment": ["job", "employment", "career", "hire", "work"],
            "housing": ["housing", "shelter", "homeless", "rent", "hud-vash", "ssvf"],
            "food": ["food", "meal", "pantry", "hunger", "nutrition"],
            "legal": ["legal", "attorney", "lawyer", "court", "appeals"],
            "mentalHealth": ["mental health", "counseling", "ptsd", "crisis", "suicide"],
            "healthcare": ["health", "medical", "clinic", "doctor", "hospital"],
            "benefits": ["benefits", "compensation", "pension", "claims", "va"],
            "financial": ["financial", "utility", "rent assistance", "emergency fund"],
        }

        for category, keywords in category_keywords.items():
            if any(kw in description for kw in keywords):
                categories.add(category)

        return sorted(categories) if categories else []

    def _extract_tags(self, result: dict[str, Any]) -> list[str]:
        """Extract tags from API result."""
        tags = ["211", "community-resource"]

        # Add taxonomy terms as tags
        taxonomy = result.get("taxonomy", [])
        if isinstance(taxonomy, list):
            for term in taxonomy:
                if isinstance(term, dict):
                    term_name = term.get("name", "")
                elif isinstance(term, str):
                    term_name = term
                else:
                    continue

                if term_name:
                    # Convert to tag format
                    tag = term_name.lower().replace(" ", "-")[:50]
                    if tag not in tags:
                        tags.append(tag)

        return tags[:20]  # Limit number of tags

    # -------------------------------------------------------------------------
    # File-based fallback methods (when no API key)
    # -------------------------------------------------------------------------

    def _load_from_files(self) -> None:
        """Load resources from pre-fetched state JSON files."""
        for state in self.states:
            state_file = self.data_dir / f"{state}.json"
            if state_file.exists():
                self._load_state_file(state_file, state)

        logger.info(f"211 files: Loaded {len(self._resources)} resources from {len(self.states)} states")

    def _load_state_file(self, file_path: Path, state: str) -> None:
        """Load resources from a single state JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load {file_path}: {e}")
            return

        fetched_at = self._parse_timestamp(data.get("fetched_at"))

        for resource in data.get("resources", []):
            candidate = self._convert_file_resource(resource, state, fetched_at)
            if candidate:
                self._resources.append(candidate)

    def _convert_file_resource(
        self,
        resource: dict[str, Any],
        state: str,
        fetched_at: datetime | None,
    ) -> ResourceCandidate | None:
        """Convert a file-based resource to a ResourceCandidate."""
        name = resource.get("name", "").strip()
        if not name:
            return None

        # Map services to categories
        raw_services = resource.get("services", [])
        categories = self._map_file_categories(raw_services)

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
        raw_with_normalized["source"] = "211_file"
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
            categories=categories if categories else ["supportServices"],
            tags=raw_services,
            phone=normalized_phone,
            email=resource.get("email"),
            hours=resource.get("hours"),
            scope="state",
            states=[state],
            raw_data=raw_with_normalized,
            fetched_at=fetched_at,
        )

    def _map_file_categories(self, services: list[str]) -> list[str]:
        """Map file-based service tags to Vibe4Vets categories."""
        categories: set[str] = set()

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
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            return datetime.fromisoformat(ts)
        except ValueError:
            return datetime.now(UTC)

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def get_resources_by_state(self, state: str) -> list[ResourceCandidate]:
        """Get resources for a specific state."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.state == state]

    def get_resources_by_category(self, category: str) -> list[ResourceCandidate]:
        """Get resources matching a category."""
        if not self._resources:
            self.run()
        return [r for r in self._resources if r.categories and category in r.categories]

    def stats(self) -> dict[str, Any]:
        """Return statistics about loaded resources."""
        if not self._resources:
            self.run()

        by_state: dict[str, int] = {}
        by_category: dict[str, int] = {}
        by_source: dict[str, int] = {"api": 0, "file": 0}

        for r in self._resources:
            # Count by state
            if r.state:
                by_state[r.state] = by_state.get(r.state, 0) + 1

            # Count by category
            for cat in r.categories or []:
                by_category[cat] = by_category.get(cat, 0) + 1

            # Count by source
            source = r.raw_data.get("source", "unknown") if r.raw_data else "unknown"
            if "api" in source:
                by_source["api"] += 1
            else:
                by_source["file"] += 1

        return {
            "total_resources": len(self._resources),
            "states_covered": len(by_state),
            "api_mode": bool(self.api_key),
            "by_source": by_source,
            "by_state": dict(sorted(by_state.items())),
            "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        }
