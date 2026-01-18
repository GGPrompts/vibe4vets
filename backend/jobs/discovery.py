"""AI-powered resource discovery job.

Automates resource discovery using Claude:
1. Discovery (Haiku): Run discovery prompts to find resources
2. Validation (Sonnet): Validate each candidate's links, phones, eligibility
3. Routing: Auto-approve high confidence, queue medium, discard low
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlmodel import Session, select

from app.models import Organization, Resource, Source
from app.models.resource import ResourceScope, ResourceStatus
from app.models.review import ReviewState, ReviewStatus
from app.models.source import HealthStatus, SourceType
from jobs.base import BaseJob
from llm import ClaudeClient, ClaudeModel

# Confidence thresholds for routing
HIGH_CONFIDENCE_THRESHOLD = 0.9
MEDIUM_CONFIDENCE_THRESHOLD = 0.7


@dataclass
class DiscoveryStats:
    """Statistics from a discovery run."""

    prompts_run: int = 0
    candidates_found: int = 0
    validated: int = 0
    auto_approved: int = 0
    queued_for_review: int = 0
    discarded: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class ValidatedCandidate:
    """A resource candidate with validation results."""

    # Original discovery data
    data: dict[str, Any]

    # Validation results
    validation_status: str = "pending"  # valid, needs_review, invalid
    confidence: float = 0.5
    validation_notes: str = ""
    checks: dict[str, Any] = field(default_factory=dict)

    @property
    def should_auto_approve(self) -> bool:
        """Check if candidate should be auto-approved."""
        return self.validation_status == "valid" and self.confidence >= HIGH_CONFIDENCE_THRESHOLD

    @property
    def should_queue_for_review(self) -> bool:
        """Check if candidate should be queued for human review."""
        return (
            self.validation_status in ("valid", "needs_review")
            and MEDIUM_CONFIDENCE_THRESHOLD <= self.confidence < HIGH_CONFIDENCE_THRESHOLD
        ) or (
            self.validation_status == "needs_review"
            and self.confidence >= HIGH_CONFIDENCE_THRESHOLD
        )

    @property
    def should_discard(self) -> bool:
        """Check if candidate should be discarded."""
        return self.validation_status == "invalid" or self.confidence < MEDIUM_CONFIDENCE_THRESHOLD


class DiscoveryJob(BaseJob):
    """Job to discover and validate veteran resources using AI.

    Pipeline:
    1. Run discovery prompts with Haiku (fast, cheap)
    2. Validate each candidate with Sonnet (accurate)
    3. Route based on confidence scores

    Supports:
    - Running specific categories or regions
    - Dry-run mode for testing
    """

    # Base path for prompts
    PROMPTS_DIR = Path(__file__).parent.parent.parent / ".prompts"

    @property
    def name(self) -> str:
        return "discovery"

    @property
    def description(self) -> str:
        return "AI-powered resource discovery and validation"

    def execute(
        self,
        session: Session,
        category: str | None = None,
        region: str | None = None,
        dry_run: bool = False,
        skip_validation: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run the discovery job.

        Args:
            session: Database session.
            category: Optional category to discover (housing, employment, etc.).
                     If None, runs all discovery prompts.
            region: Optional region/area to focus on (e.g., "Virginia").
            dry_run: If True, don't persist changes to database.
            skip_validation: If True, skip the validation step (for testing).
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary with counts.
        """
        stats = DiscoveryStats()

        # Initialize Claude client
        try:
            claude = ClaudeClient()
        except ValueError as e:
            return {"error": str(e), "prompts_run": 0}

        # Get or create discovery source
        source = self._get_or_create_source(session, dry_run)

        # Find discovery prompts to run
        prompts = self._get_discovery_prompts(category)
        if not prompts:
            return {"error": "No discovery prompts found", "prompts_run": 0}

        self._log(f"Running {len(prompts)} discovery prompt(s)")

        # Stage 1: Discovery with Haiku
        all_candidates: list[dict[str, Any]] = []
        for prompt_path in prompts:
            try:
                candidates = self._run_discovery(claude, prompt_path, region or "nationwide", stats)
                all_candidates.extend(candidates)
                stats.prompts_run += 1
            except Exception as e:
                stats.errors.append(f"Discovery error ({prompt_path.name}): {str(e)}")
                self._log(f"Discovery failed for {prompt_path.name}: {e}", level="error")

        stats.candidates_found = len(all_candidates)
        self._log(f"Found {len(all_candidates)} candidates")

        if not all_candidates:
            return self._format_stats(stats)

        # Stage 2: Validation with Sonnet
        validated: list[ValidatedCandidate] = []
        if skip_validation:
            # Skip validation - use discovery confidence directly
            for candidate in all_candidates:
                validated.append(
                    ValidatedCandidate(
                        data=candidate,
                        validation_status="needs_review",
                        confidence=candidate.get("confidence", 0.7),
                        validation_notes="Validation skipped",
                    )
                )
        else:
            for candidate in all_candidates:
                try:
                    result = self._validate_candidate(claude, candidate, session, stats)
                    validated.append(result)
                    stats.validated += 1
                except Exception as e:
                    stats.errors.append(f"Validation error: {str(e)}")
                    # Still include with low confidence
                    validated.append(
                        ValidatedCandidate(
                            data=candidate,
                            validation_status="needs_review",
                            confidence=0.5,
                            validation_notes=f"Validation failed: {str(e)}",
                        )
                    )

        self._log(f"Validated {stats.validated} candidates")

        # Stage 3: Routing and import
        for candidate in validated:
            try:
                self._route_candidate(session, source, candidate, stats, dry_run)
            except Exception as e:
                stats.errors.append(f"Import error: {str(e)}")
                self._log(f"Import failed: {e}", level="error")

        if not dry_run:
            session.commit()

        self._log(
            f"Results: {stats.auto_approved} auto-approved, "
            f"{stats.queued_for_review} queued, {stats.discarded} discarded"
        )

        return self._format_stats(stats)

    def _get_discovery_prompts(self, category: str | None = None) -> list[Path]:
        """Get paths to discovery prompt files.

        Args:
            category: Optional category to filter by.

        Returns:
            List of prompt file paths.
        """
        discovery_dir = self.PROMPTS_DIR / "discovery"
        if not discovery_dir.exists():
            return []

        prompts = list(discovery_dir.glob("*.md"))

        if category:
            # Filter to matching category
            prompts = [p for p in prompts if category.lower() in p.stem.lower()]

        return prompts

    def _run_discovery(
        self,
        claude: ClaudeClient,
        prompt_path: Path,
        region: str,
        stats: DiscoveryStats,
    ) -> list[dict[str, Any]]:
        """Run a discovery prompt and extract candidates.

        Args:
            claude: Claude client.
            prompt_path: Path to the discovery prompt.
            region: Region/area to focus on.
            stats: Stats object to update token counts.

        Returns:
            List of discovered resource candidates.
        """
        self._log(f"Running discovery: {prompt_path.name} for {region}")

        # Load and fill template
        template = prompt_path.read_text()
        prompt = template.replace("{{AREA}}", region)

        # Use Haiku for discovery (fast, cheap)
        response = claude.complete(
            prompt=prompt,
            model=ClaudeModel.HAIKU,
            max_tokens=8192,
            temperature=0.2,  # Slight creativity for finding resources
        )

        stats.input_tokens += response.input_tokens
        stats.output_tokens += response.output_tokens

        # Parse JSON response
        try:
            candidates = response.json
            if not isinstance(candidates, list):
                candidates = [candidates]
            return candidates
        except json.JSONDecodeError as e:
            self._log(f"Failed to parse discovery response: {e}", level="warning")
            return []

    def _validate_candidate(
        self,
        claude: ClaudeClient,
        candidate: dict[str, Any],
        session: Session,
        stats: DiscoveryStats,
    ) -> ValidatedCandidate:
        """Validate a discovered candidate.

        Args:
            claude: Claude client.
            candidate: The candidate data to validate.
            session: Database session for duplicate checking.
            stats: Stats object to update token counts.

        Returns:
            ValidatedCandidate with validation results.
        """
        # Check for duplicates first
        is_duplicate = self._check_duplicate(session, candidate)
        if is_duplicate:
            stats.duplicates_skipped += 1
            return ValidatedCandidate(
                data=candidate,
                validation_status="invalid",
                confidence=0.0,
                validation_notes="Duplicate of existing resource",
            )

        # Load validation template
        validate_path = self.PROMPTS_DIR / "validation" / "validate-resource.md"
        if not validate_path.exists():
            # Fall back to discovery confidence
            return ValidatedCandidate(
                data=candidate,
                validation_status="needs_review",
                confidence=candidate.get("confidence", 0.7),
                validation_notes="No validation template found",
            )

        # Run validation with Sonnet (accurate)
        template = validate_path.read_text()
        prompt = template.replace("{{RESOURCE_JSON}}", json.dumps(candidate, indent=2))
        prompt = prompt.replace("{{ID}}", candidate.get("name", "unknown"))

        response = claude.complete(
            prompt=prompt,
            model=ClaudeModel.SONNET,
            max_tokens=4096,
            temperature=0.0,  # Deterministic for validation
        )

        stats.input_tokens += response.input_tokens
        stats.output_tokens += response.output_tokens

        # Parse validation result
        try:
            result = response.json
            return ValidatedCandidate(
                data=candidate,
                validation_status=result.get("validation_status", "needs_review"),
                confidence=result.get("overall_confidence", 0.7),
                validation_notes="; ".join(result.get("recommended_actions", [])),
                checks=result.get("checks", {}),
            )
        except json.JSONDecodeError:
            return ValidatedCandidate(
                data=candidate,
                validation_status="needs_review",
                confidence=candidate.get("confidence", 0.7),
                validation_notes="Failed to parse validation response",
            )

    def _check_duplicate(self, session: Session, candidate: dict[str, Any]) -> bool:
        """Check if a candidate is a duplicate of existing resources.

        Args:
            session: Database session.
            candidate: The candidate to check.

        Returns:
            True if this is a duplicate.
        """
        # Check by source URL
        source_url = candidate.get("source_url") or candidate.get("website")
        if source_url:
            stmt = select(Resource).where(Resource.source_url == source_url)
            if session.exec(stmt).first():
                return True

        # Check by name + organization
        name = candidate.get("name") or candidate.get("title")
        org = candidate.get("organization") or candidate.get("org_name")
        if name and org:
            # Simple name matching - could be enhanced with fuzzy matching
            stmt = select(Resource).where(Resource.title == name)
            for resource in session.exec(stmt):
                if resource.organization and resource.organization.name == org:
                    return True

        return False

    def _route_candidate(
        self,
        session: Session,
        source: Source,
        candidate: ValidatedCandidate,
        stats: DiscoveryStats,
        dry_run: bool,
    ) -> None:
        """Route a validated candidate based on confidence.

        Args:
            session: Database session.
            source: The discovery source.
            candidate: The validated candidate.
            stats: Stats object to update.
            dry_run: If True, don't persist changes.
        """
        data = candidate.data

        if candidate.should_discard:
            stats.discarded += 1
            self._log(
                f"Discarded: {data.get('name', 'unknown')} (confidence: {candidate.confidence:.2f})"
            )
            return

        if dry_run:
            if candidate.should_auto_approve:
                stats.auto_approved += 1
            else:
                stats.queued_for_review += 1
            return

        # Create organization if needed
        org = self._get_or_create_org(session, data)

        # Create resource
        resource = self._create_resource(session, source, org, data, candidate)

        if candidate.should_auto_approve:
            # Auto-approve: set status to active
            resource.status = ResourceStatus.ACTIVE
            stats.auto_approved += 1
            self._log(f"Auto-approved: {resource.title}")
        else:
            # Queue for review
            resource.status = ResourceStatus.NEEDS_REVIEW
            review = ReviewState(
                resource_id=resource.id,
                status=ReviewStatus.PENDING,
                reason=f"AI discovery (confidence: {candidate.confidence:.2f}). "
                + candidate.validation_notes,
            )
            session.add(review)
            stats.queued_for_review += 1
            self._log(f"Queued for review: {resource.title}")

    def _get_or_create_source(self, session: Session, dry_run: bool) -> Source:
        """Get or create the AI Discovery source.

        Args:
            session: Database session.
            dry_run: If True, don't create new source.

        Returns:
            The discovery Source entity.
        """
        stmt = select(Source).where(Source.name == "AI Discovery")
        source = session.exec(stmt).first()

        if source:
            return source

        if dry_run:
            # Return a mock source for dry run
            return Source(
                id=uuid4(),
                name="AI Discovery",
                url="https://vibe4vets.org/discovery",
                source_type=SourceType.MANUAL,
                tier=4,
            )

        source = Source(
            name="AI Discovery",
            url="https://vibe4vets.org/discovery",
            source_type=SourceType.MANUAL,
            tier=4,  # Community tier - validated individually
            health_status=HealthStatus.HEALTHY,
            last_success=datetime.now(UTC),
        )
        session.add(source)
        session.flush()
        return source

    def _get_or_create_org(self, session: Session, data: dict[str, Any]) -> Organization:
        """Get or create an organization.

        Args:
            session: Database session.
            data: Candidate data with org info.

        Returns:
            Organization entity.
        """
        org_name = data.get("organization") or data.get("org_name") or "Unknown"
        org_website = data.get("org_website") or data.get("website")

        # Try to find existing org by website
        if org_website:
            stmt = select(Organization).where(Organization.website == org_website)
            org = session.exec(stmt).first()
            if org:
                return org

        # Try to find by name
        stmt = select(Organization).where(Organization.name == org_name)
        org = session.exec(stmt).first()
        if org:
            return org

        # Create new org
        org = Organization(
            name=org_name,
            website=org_website,
            phones=[data.get("phone")] if data.get("phone") else [],
            emails=[data.get("email")] if data.get("email") else [],
        )
        session.add(org)
        session.flush()
        return org

    def _create_resource(
        self,
        session: Session,
        source: Source,
        org: Organization,
        data: dict[str, Any],
        candidate: ValidatedCandidate,
    ) -> Resource:
        """Create a resource from candidate data.

        Args:
            session: Database session.
            source: The discovery source.
            org: The parent organization.
            data: Candidate data.
            candidate: Validated candidate with confidence.

        Returns:
            Created Resource entity.
        """
        # Map categories
        categories = data.get("categories", [])
        if isinstance(categories, str):
            categories = [categories]
        if not categories and data.get("category"):
            categories = [data["category"]]

        subcategories = data.get("subcategories", [])
        if isinstance(subcategories, str):
            subcategories = [subcategories]
        if not subcategories and data.get("subcategory"):
            subcategories = [data["subcategory"]]

        # Map eligibility
        eligibility = data.get("eligibility")
        if isinstance(eligibility, list):
            eligibility_map = {
                "veteran": "Must be a veteran",
                "housing": "For veterans experiencing housing instability",
                "homeless": "For veterans experiencing homelessness",
                "at_risk_homeless": "For veterans at risk of housing instability",
                "low_income": "Income restrictions apply",
                "disabled_veteran": "For disabled veterans",
            }
            parts: list[str] = []
            for e in eligibility:
                mapped = eligibility_map.get(e)
                if mapped:
                    parts.append(mapped)
                else:
                    parts.append(e.replace("_", " ").title())
            eligibility = ". ".join(parts) + "." if parts else None

        # Map scope
        scope_str = data.get("scope", "national")
        scope = (
            ResourceScope.STATE
            if scope_str == "state"
            else (ResourceScope.LOCAL if scope_str == "local" else ResourceScope.NATIONAL)
        )

        states = data.get("states", [])
        if isinstance(states, str):
            states = [states]

        # Calculate reliability based on confidence
        reliability = min(candidate.confidence, 0.8)  # Cap at 0.8 for AI-discovered

        resource = Resource(
            organization_id=org.id,
            source_id=source.id,
            title=data.get("name") or data.get("title") or "Untitled Resource",
            description=data.get("description", ""),
            summary=data.get("notes") or data.get("description", "")[:200],
            eligibility=eligibility,
            how_to_apply=data.get("how_to_apply"),
            categories=categories,
            subcategories=subcategories,
            tags=data.get("eligibility", []) if isinstance(data.get("eligibility"), list) else [],
            scope=scope,
            states=states,
            website=data.get("website"),
            phone=data.get("phone"),
            hours=data.get("hours"),
            source_url=data.get("source_url") or data.get("website"),
            status=ResourceStatus.NEEDS_REVIEW,
            freshness_score=candidate.confidence,
            reliability_score=reliability,
        )
        session.add(resource)
        session.flush()
        return resource

    def _format_stats(self, stats: DiscoveryStats) -> dict[str, Any]:
        """Format stats for job result."""
        return {
            "prompts_run": stats.prompts_run,
            "candidates_found": stats.candidates_found,
            "validated": stats.validated,
            "auto_approved": stats.auto_approved,
            "queued_for_review": stats.queued_for_review,
            "discarded": stats.discarded,
            "duplicates_skipped": stats.duplicates_skipped,
            "errors": len(stats.errors),
            "error_messages": stats.errors[:5],  # First 5 errors
            "tokens_used": {
                "input": stats.input_tokens,
                "output": stats.output_tokens,
                "total": stats.input_tokens + stats.output_tokens,
            },
        }

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format discovery statistics into a message."""
        if stats.get("error"):
            return f"Discovery failed: {stats['error']}"

        return (
            f"Discovery complete: {stats.get('candidates_found', 0)} found, "
            f"{stats.get('auto_approved', 0)} approved, "
            f"{stats.get('queued_for_review', 0)} queued for review"
        )
