"""Resource discovery service for AI-powered web search and curation.

Discovers veteran resources from web searches and normalizes them
to ResourceCandidate format for review queue integration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.taxonomy import CATEGORIES, SUBCATEGORIES
from app.models import Organization, Resource
from connectors.base import ResourceCandidate


@dataclass
class DiscoveredResource:
    """A resource discovered via web search."""

    # Core fields (map to ResourceCandidate)
    title: str
    description: str
    source_url: str
    org_name: str
    org_website: str | None = None

    # Location
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    # Classification
    categories: list[str] = field(default_factory=list)
    subcategories: list[str] = field(default_factory=list)

    # Contact
    phone: str | None = None
    email: str | None = None
    hours: str | None = None

    # Content
    eligibility: str | None = None
    how_to_apply: str | None = None

    # Scope
    scope: str = "national"
    states: list[str] = field(default_factory=list)

    # Discovery metadata
    suggested_tier: int = 4
    confidence: float = 0.5
    is_duplicate: bool = False
    duplicate_of: UUID | None = None
    discovery_notes: str | None = None

    def to_resource_candidate(self) -> ResourceCandidate:
        """Convert to ResourceCandidate for ETL pipeline."""
        return ResourceCandidate(
            title=self.title,
            description=self.description,
            source_url=self.source_url,
            org_name=self.org_name,
            org_website=self.org_website,
            address=self.address,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            categories=self.categories,
            tags=self.subcategories,
            phone=self.phone,
            email=self.email,
            hours=self.hours,
            eligibility=self.eligibility,
            how_to_apply=self.how_to_apply,
            scope=self.scope,
            states=self.states,
            fetched_at=datetime.utcnow(),
        )


@dataclass
class DiscoveryStats:
    """Statistics from a discovery run."""

    queries_executed: int = 0
    total_results: int = 0
    after_filtering: int = 0
    duplicates_skipped: int = 0
    queued_for_review: int = 0


@dataclass
class DiscoveryResult:
    """Result of a discovery operation."""

    discovered: list[DiscoveredResource] = field(default_factory=list)
    stats: DiscoveryStats = field(default_factory=DiscoveryStats)
    queries_used: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "discovered": [
                {
                    "title": r.title,
                    "description": r.description,
                    "source_url": r.source_url,
                    "org_name": r.org_name,
                    "org_website": r.org_website,
                    "address": r.address,
                    "city": r.city,
                    "state": r.state,
                    "zip_code": r.zip_code,
                    "categories": r.categories,
                    "subcategories": r.subcategories,
                    "phone": r.phone,
                    "email": r.email,
                    "hours": r.hours,
                    "eligibility": r.eligibility,
                    "how_to_apply": r.how_to_apply,
                    "scope": r.scope,
                    "states": r.states,
                    "suggested_tier": r.suggested_tier,
                    "confidence": r.confidence,
                    "is_duplicate": r.is_duplicate,
                    "duplicate_of": str(r.duplicate_of) if r.duplicate_of else None,
                    "discovery_notes": r.discovery_notes,
                }
                for r in self.discovered
            ],
            "stats": {
                "queries_executed": self.stats.queries_executed,
                "total_results": self.stats.total_results,
                "after_filtering": self.stats.after_filtering,
                "duplicates_skipped": self.stats.duplicates_skipped,
                "queued_for_review": self.stats.queued_for_review,
            },
            "queries_used": self.queries_used,
            "errors": self.errors,
        }


class DiscoveryService:
    """Service for discovering veteran resources via web search."""

    # Domains to exclude (already have connectors or not useful)
    EXCLUDED_DOMAINS = [
        "va.gov",
        "benefits.va.gov",
        "facebook.com",
        "twitter.com",
        "linkedin.com",
        "youtube.com",
        "instagram.com",
        "reddit.com",
        "wikipedia.org",
        "yelp.com",
    ]

    # Keywords indicating official/established organizations
    TIER_2_KEYWORDS = [
        "dav",
        "disabled american veterans",
        "vfw",
        "veterans of foreign wars",
        "american legion",
        "paralyzed veterans",
        "wounded warrior",
        "team rubicon",
        "hire heroes",
    ]

    # Keywords indicating state-level organizations
    TIER_3_KEYWORDS = [
        "state veteran",
        "department of veteran",
        "veterans affairs",
        "state dva",
        "veterans commission",
    ]

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the discovery service.

        Args:
            session: Optional database session for duplicate checking.
        """
        self.session = session

    def generate_queries(
        self,
        category: str | None = None,
        location: str | None = None,
    ) -> list[str]:
        """Generate search queries for resource discovery.

        Args:
            category: Optional category filter (employment, training, housing, legal).
            location: Optional location filter (state, city, or nationwide).

        Returns:
            List of search queries to execute.
        """
        queries = []
        location_str = location or ""

        # Define query templates by category
        query_templates = {
            "employment": [
                f"veteran employment programs {location_str}".strip(),
                f"veteran job placement services {location_str}".strip(),
                f"veteran career counseling nonprofit {location_str}".strip(),
                f"veteran hiring initiative {location_str}".strip(),
                f"veteran workforce development {location_str}".strip(),
            ],
            "training": [
                f"veteran vocational training {location_str}".strip(),
                f"veteran apprenticeship programs {location_str}".strip(),
                f"veteran certification programs free {location_str}".strip(),
                f"veteran skills training nonprofit {location_str}".strip(),
                f"GI Bill approved programs {location_str}".strip(),
            ],
            "housing": [
                f"veteran housing assistance {location_str}".strip(),
                f"veteran emergency shelter {location_str}".strip(),
                f"SSVF provider {location_str}".strip(),
                f"veteran transitional housing {location_str}".strip(),
                f"HUD-VASH {location_str}".strip(),
            ],
            "legal": [
                f"veteran legal aid free {location_str}".strip(),
                f"VA appeals assistance {location_str}".strip(),
                f"veteran discharge upgrade help {location_str}".strip(),
                f"veterans treatment court {location_str}".strip(),
                f"veteran benefits claim help {location_str}".strip(),
            ],
        }

        if category and category in query_templates:
            queries.extend(query_templates[category])
        else:
            # Generate queries for all categories
            for cat_queries in query_templates.values():
                queries.extend(cat_queries)

        return queries

    def is_excluded_domain(self, url: str) -> bool:
        """Check if URL is from an excluded domain.

        Args:
            url: URL to check.

        Returns:
            True if domain should be excluded.
        """
        url_lower = url.lower()
        for domain in self.EXCLUDED_DOMAINS:
            if domain in url_lower:
                return True
        return False

    def suggest_tier(self, org_name: str, url: str) -> int:
        """Suggest a source tier based on organization signals.

        Args:
            org_name: Name of the organization.
            url: URL of the resource.

        Returns:
            Suggested tier (2, 3, or 4).
        """
        combined = f"{org_name} {url}".lower()

        # Check for Tier 2 signals (major VSOs)
        for keyword in self.TIER_2_KEYWORDS:
            if keyword in combined:
                return 2

        # Check for Tier 3 signals (state agencies)
        for keyword in self.TIER_3_KEYWORDS:
            if keyword in combined:
                return 3

        # Check for .gov domains (state/local government)
        if ".gov" in url.lower() and "va.gov" not in url.lower():
            return 3

        # Check for .org (nonprofits)
        if ".org" in url.lower():
            return 3

        # Default to community tier
        return 4

    def calculate_confidence(self, resource: DiscoveredResource) -> float:
        """Calculate confidence score for a discovered resource.

        Args:
            resource: The discovered resource.

        Returns:
            Confidence score from 0.0 to 1.0.
        """
        score = 0.0

        # Has physical address
        if resource.address and resource.city and resource.state:
            score += 0.25

        # Has phone number
        if resource.phone:
            score += 0.2

        # Has email
        if resource.email:
            score += 0.1

        # Has eligibility info
        if resource.eligibility:
            score += 0.2

        # Has how to apply
        if resource.how_to_apply:
            score += 0.15

        # Has description of reasonable length
        if resource.description and len(resource.description) > 100:
            score += 0.1

        return min(score, 1.0)

    def classify_categories(
        self,
        title: str,
        description: str,
    ) -> tuple[list[str], list[str]]:
        """Classify resource into categories and subcategories.

        Args:
            title: Resource title.
            description: Resource description.

        Returns:
            Tuple of (categories, subcategories).
        """
        combined = f"{title} {description}".lower()
        categories = []
        subcategories = []

        # Employment signals
        employment_signals = [
            "job",
            "employment",
            "career",
            "hiring",
            "workforce",
            "resume",
            "interview",
        ]
        if any(sig in combined for sig in employment_signals):
            categories.append("employment")
            if "placement" in combined or "hiring" in combined:
                subcategories.append("job-placement")
            if "career" in combined or "counsel" in combined:
                subcategories.append("career-counseling")
            if "business" in combined or "entrepreneur" in combined:
                subcategories.append("self-employment")

        # Training signals
        training_signals = [
            "training",
            "education",
            "certification",
            "apprentice",
            "vocational",
            "gi bill",
            "school",
        ]
        if any(sig in combined for sig in training_signals):
            categories.append("training")
            if "vocational" in combined or "rehab" in combined:
                subcategories.append("voc-rehab")
            if "certif" in combined or "license" in combined:
                subcategories.append("certifications")
            if "apprentice" in combined:
                subcategories.append("apprenticeships")
            if "gi bill" in combined:
                subcategories.append("gi-bill")

        # Housing signals
        housing_signals = [
            "housing",
            "shelter",
            "homeless",
            "ssvf",
            "hud-vash",
            "transitional",
            "home",
        ]
        if any(sig in combined for sig in housing_signals):
            categories.append("housing")
            if "hud-vash" in combined or "hud vash" in combined:
                subcategories.append("hud-vash")
            if "ssvf" in combined:
                subcategories.append("ssvf")
            if "shelter" in combined or "emergency" in combined:
                subcategories.append("emergency-shelter")
            if "repair" in combined or "modif" in combined:
                subcategories.append("home-repair")

        # Legal signals
        legal_signals = [
            "legal",
            "attorney",
            "lawyer",
            "appeal",
            "claim",
            "discharge",
            "court",
        ]
        if any(sig in combined for sig in legal_signals):
            categories.append("legal")
            if "appeal" in combined or "claim" in combined:
                subcategories.append("va-appeals")
            if "discharge" in combined:
                subcategories.append("discharge-upgrade")
            if "legal aid" in combined or "free legal" in combined:
                subcategories.append("legal-aid")
            if "court" in combined:
                subcategories.append("veterans-court")

        # Validate against taxonomy
        categories = [c for c in categories if c in CATEGORIES]
        subcategories = [s for s in subcategories if s in SUBCATEGORIES]

        return categories, subcategories

    def find_duplicates(
        self,
        resource: DiscoveredResource,
    ) -> tuple[bool, UUID | None]:
        """Check if a resource might be a duplicate of existing records.

        Args:
            resource: The discovered resource to check.

        Returns:
            Tuple of (is_duplicate, duplicate_id).
        """
        if not self.session:
            return False, None

        # Query existing organizations with similar names
        org_name_lower = resource.org_name.lower().strip()

        stmt = select(Organization)
        existing_orgs = self.session.exec(stmt).all()

        for org in existing_orgs:
            existing_name = org.name.lower().strip()

            # Check name similarity
            similarity = SequenceMatcher(None, org_name_lower, existing_name).ratio()
            if similarity >= 0.85:
                # Check if they have resources in same category
                resource_stmt = select(Resource).where(
                    Resource.organization_id == org.id
                )
                org_resources = self.session.exec(resource_stmt).all()

                for existing_resource in org_resources:
                    # Compare titles
                    title_similarity = SequenceMatcher(
                        None,
                        resource.title.lower().strip(),
                        existing_resource.title.lower().strip(),
                    ).ratio()

                    if title_similarity >= 0.85:
                        return True, existing_resource.id

        return False, None

    def process_search_result(
        self,
        url: str,
        title: str,
        snippet: str,
        org_name: str | None = None,
    ) -> DiscoveredResource | None:
        """Process a single search result into a DiscoveredResource.

        Args:
            url: URL from search result.
            title: Title from search result.
            snippet: Snippet/description from search result.
            org_name: Optional organization name if extracted.

        Returns:
            DiscoveredResource or None if should be filtered.
        """
        # Filter excluded domains
        if self.is_excluded_domain(url):
            return None

        # Extract org name from URL if not provided
        if not org_name:
            # Simple extraction from domain
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain_parts = parsed.netloc.replace("www.", "").split(".")
            org_name = domain_parts[0].replace("-", " ").title()

        # Classify categories
        categories, subcategories = self.classify_categories(title, snippet)

        # Create resource
        resource = DiscoveredResource(
            title=title,
            description=snippet,
            source_url=url,
            org_name=org_name,
            org_website=f"https://{urlparse(url).netloc}" if url else None,
            categories=categories,
            subcategories=subcategories,
        )

        # Suggest tier
        resource.suggested_tier = self.suggest_tier(org_name, url)

        # Calculate confidence
        resource.confidence = self.calculate_confidence(resource)

        # Check for duplicates
        is_dup, dup_id = self.find_duplicates(resource)
        resource.is_duplicate = is_dup
        resource.duplicate_of = dup_id

        return resource

    def filter_and_score(
        self,
        resources: list[DiscoveredResource],
        min_confidence: float = 0.3,
    ) -> list[DiscoveredResource]:
        """Filter and score discovered resources.

        Args:
            resources: List of discovered resources.
            min_confidence: Minimum confidence score to include.

        Returns:
            Filtered and scored resources.
        """
        filtered = []

        for resource in resources:
            # Skip low confidence
            if resource.confidence < min_confidence:
                continue

            # Skip resources with no categories
            if not resource.categories:
                continue

            filtered.append(resource)

        # Sort by confidence (highest first)
        filtered.sort(key=lambda r: r.confidence, reverse=True)

        return filtered


def create_discovery_service(session: Session | None = None) -> DiscoveryService:
    """Factory function to create a DiscoveryService.

    Args:
        session: Optional database session.

    Returns:
        Configured DiscoveryService instance.
    """
    return DiscoveryService(session=session)
