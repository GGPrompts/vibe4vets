"""Database loader for ETL pipeline.

Handles creation and updates of Organization, Location, Resource,
and SourceRecord entities with conflict resolution.

Supports idempotent batch loading via:
- Batch transactions instead of per-resource commits
- Skip already-processed URLs when job_run provided
- Content hash-based duplicate detection
"""

import hashlib
import json
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models import (
    ChangeLog,
    ChangeType,
    ETLJobRun,
    HealthStatus,
    Location,
    Organization,
    Resource,
    ResourceScope,
    ResourceStatus,
    ReviewState,
    ReviewStatus,
    Source,
    SourceRecord,
    SourceType,
)
from app.services.trust import TrustService
from etl.models import ETLError, LoadResult, NormalizedResource


class Loader:
    """Loads normalized resources into the database.

    Supports two modes:
    1. Single-resource mode (load): Commits per resource, used for simple loads
    2. Batch mode (load_batch): Commits entire batch atomically, supports checkpointing

    For idempotent ETL, use load_batch with a job_run to:
    - Skip already-processed URLs on retry
    - Record processed URLs for checkpointing
    - Enable resume from failure
    """

    # Fields that trigger review when changed
    RISKY_FIELDS = {"phone", "website", "address", "eligibility", "how_to_apply", "cost"}

    # Default batch size for checkpointing
    DEFAULT_CHECKPOINT_BATCH_SIZE = 50

    def __init__(self, session: Session, job_run: ETLJobRun | None = None):
        """Initialize loader.

        Args:
            session: SQLModel database session.
            job_run: Optional ETLJobRun for checkpointing and idempotency.
                     When provided, processed URLs are tracked and skipped on retry.
        """
        self.session = session
        self.job_run = job_run
        self.trust_service = TrustService(session)

        # Cache for organizations and sources to avoid repeated lookups
        self._org_cache: dict[str, Organization] = {}
        self._source_cache: dict[str, Source] = {}

    def load(self, resource: NormalizedResource, commit: bool = True) -> LoadResult:
        """Load a single resource into the database.

        Creates or updates Organization, Location, and Resource as needed.

        Args:
            resource: Normalized resource to load.
            commit: Whether to commit after loading. Set to False for batch operations.

        Returns:
            LoadResult with action taken and IDs.
        """
        try:
            # Skip if already processed in this job run (idempotency)
            if self.job_run and self.job_run.is_url_processed(resource.source_url):
                return LoadResult(
                    action="skipped",
                    error="Already processed in this job run",
                )

            # 1. Find or create organization
            org = self._get_or_create_organization(resource)

            # 2. Find or create location (if address present)
            location = None
            if resource.has_location():
                location = self._get_or_create_location(resource, org)

            # 3. Find or create source
            source = None
            if resource.source_name:
                source = self._get_or_create_source(resource)

            # 4. Find existing resource by source_url
            existing = self._find_existing_resource(resource.source_url)

            if existing:
                # Update existing resource
                result = self._update_resource(existing, resource, org, location, source)
            else:
                # Create new resource
                result = self._create_resource(resource, org, location, source)

            # Mark as processed for idempotency
            if self.job_run:
                self.job_run.mark_url_processed(resource.source_url)

            if commit:
                self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            return LoadResult(
                action="failed",
                error=f"Database error: {str(e)}",
            )

    def load_batch(
        self,
        resources: list[NormalizedResource],
        checkpoint_batch_size: int | None = None,
    ) -> tuple[list[LoadResult], list[ETLError]]:
        """Load a batch of resources with atomic transactions and checkpointing.

        This method is idempotent when used with a job_run:
        - Resources with URLs already in job_run.processed_urls are skipped
        - Processed URLs are recorded in job_run for retry safety
        - Progress is checkpointed every checkpoint_batch_size resources

        Commits in batches rather than per-resource to balance:
        - Atomicity (smaller batches = less work lost on failure)
        - Performance (larger batches = fewer commits)

        Args:
            resources: List of normalized resources.
            checkpoint_batch_size: Number of resources to process before
                                   checkpointing. Defaults to DEFAULT_CHECKPOINT_BATCH_SIZE.

        Returns:
            Tuple of (load results, errors).
        """
        batch_size = checkpoint_batch_size or self.DEFAULT_CHECKPOINT_BATCH_SIZE
        results: list[LoadResult] = []
        errors: list[ETLError] = []
        pending_count = 0

        for i, resource in enumerate(resources):
            # Load without committing - we'll batch commits
            result = self.load(resource, commit=False)
            results.append(result)

            if result.action == "failed":
                errors.append(
                    ETLError(
                        stage="load",
                        message=result.error or "Unknown error",
                        resource_title=resource.title,
                        source_url=resource.source_url,
                    )
                )
            elif result.action != "skipped":
                pending_count += 1

            # Checkpoint: commit batch and update job_run progress
            if pending_count >= batch_size or i == len(resources) - 1:
                try:
                    # Update job_run checkpoint before committing
                    if self.job_run:
                        self.job_run.update_checkpoint(
                            connector_idx=0,  # Set by pipeline
                            resource_idx=i + 1,
                        )
                        self.session.add(self.job_run)

                    self.session.commit()
                    pending_count = 0
                except Exception as e:
                    # Rollback the failed batch
                    self.session.rollback()
                    # Mark remaining resources in this batch as failed
                    for j in range(max(0, i - batch_size + 1), i + 1):
                        if results[j].action not in ("failed", "skipped"):
                            results[j] = LoadResult(
                                action="failed",
                                error=f"Batch commit failed: {str(e)}",
                            )
                            errors.append(
                                ETLError(
                                    stage="load",
                                    message=f"Batch commit failed: {str(e)}",
                                    resource_title=resources[j].title,
                                    source_url=resources[j].source_url,
                                )
                            )

        return results, errors

    def _get_or_create_organization(self, resource: NormalizedResource) -> Organization:
        """Find existing organization or create new one."""
        org_key = resource.org_key()

        # Check cache first
        if org_key in self._org_cache:
            return self._org_cache[org_key]

        # Look up in database (case-insensitive)
        stmt = select(Organization).where(Organization.name.ilike(resource.org_name))
        org = self.session.exec(stmt).first()

        if org:
            # Update website if we have a better one
            if resource.org_website and not org.website:
                org.website = resource.org_website
                org.updated_at = datetime.now(UTC)
                self.session.add(org)
            self._org_cache[org_key] = org
            return org

        # Create new organization
        org = Organization(
            name=resource.org_name,
            website=resource.org_website,
        )
        self.session.add(org)
        self.session.flush()  # Get ID

        self._org_cache[org_key] = org
        return org

    def _get_or_create_location(self, resource: NormalizedResource, org: Organization) -> Location:
        """Find existing location or create new one."""
        # Look up existing location for this org with same address
        stmt = select(Location).where(
            Location.organization_id == org.id,
            Location.address == resource.address,
            Location.city == resource.city,
            Location.state == resource.state,
        )
        location = self.session.exec(stmt).first()

        if location:
            # Update geocoding if we have it now
            if resource.latitude and not location.latitude:
                location.latitude = resource.latitude
                location.longitude = resource.longitude
                self.session.add(location)
            return location

        # Create new location
        location = Location(
            organization_id=org.id,
            address=resource.address or "",
            city=resource.city or "",
            state=resource.state or "",
            zip_code=resource.zip_code or "",
            latitude=resource.latitude,
            longitude=resource.longitude,
        )
        self.session.add(location)
        self.session.flush()

        return location

    def _get_or_create_source(self, resource: NormalizedResource) -> Source:
        """Find existing source or create new one."""
        source_name = resource.source_name or "Unknown"

        # Check cache
        if source_name in self._source_cache:
            return self._source_cache[source_name]

        # Look up in database
        stmt = select(Source).where(Source.name == source_name)
        source = self.session.exec(stmt).first()

        if source:
            self._source_cache[source_name] = source
            return source

        # Create new source
        source = Source(
            name=source_name,
            url=resource.source_url,  # Use first URL from this source
            tier=resource.source_tier,
            source_type=SourceType.API if "api" in source_name.lower() else SourceType.SCRAPE,
        )
        self.session.add(source)
        self.session.flush()

        self._source_cache[source_name] = source
        return source

    def _find_existing_resource(self, source_url: str) -> Resource | None:
        """Find existing resource by source URL."""
        stmt = select(Resource).where(Resource.source_url == source_url)
        return self.session.exec(stmt).first()

    def _create_resource(
        self,
        normalized: NormalizedResource,
        org: Organization,
        location: Location | None,
        source: Source | None,
    ) -> LoadResult:
        """Create a new resource."""
        now = datetime.now(UTC)

        resource = Resource(
            organization_id=org.id,
            location_id=location.id if location else None,
            title=normalized.title,
            description=normalized.description,
            eligibility=normalized.eligibility,
            how_to_apply=normalized.how_to_apply,
            categories=normalized.categories,
            tags=normalized.tags,
            scope=ResourceScope(normalized.scope),
            states=normalized.states,
            website=normalized.org_website,
            phone=normalized.phone,
            hours=normalized.hours,
            source_id=source.id if source else None,
            source_url=normalized.source_url,
            last_scraped=normalized.fetched_at or now,
            last_verified=now,
            freshness_score=1.0,
            reliability_score=normalized.reliability_score,
            status=ResourceStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

        self.session.add(resource)
        self.session.flush()

        # Create source record for audit trail
        if source:
            self._create_source_record(resource, source, normalized)

        return LoadResult(
            resource_id=resource.id,
            organization_id=org.id,
            location_id=location.id if location else None,
            action="created",
        )

    def _update_resource(
        self,
        existing: Resource,
        normalized: NormalizedResource,
        org: Organization,
        location: Location | None,
        source: Source | None,
    ) -> LoadResult:
        """Update an existing resource, tracking changes."""
        changes: list[tuple[str, str | None, str | None]] = []
        needs_review = False

        # Track field changes
        field_updates = [
            ("title", existing.title, normalized.title),
            ("description", existing.description, normalized.description),
            ("eligibility", existing.eligibility, normalized.eligibility),
            ("how_to_apply", existing.how_to_apply, normalized.how_to_apply),
            ("phone", existing.phone, normalized.phone),
            ("website", existing.website, normalized.org_website),
            ("hours", existing.hours, normalized.hours),
        ]

        for field_name, old_val, new_val in field_updates:
            if old_val != new_val and new_val:
                changes.append((field_name, old_val, new_val))
                if field_name in self.RISKY_FIELDS:
                    needs_review = True
                setattr(existing, field_name, new_val)

        # Update lists (merge)
        if normalized.categories:
            new_cats = list(set(existing.categories) | set(normalized.categories))
            if new_cats != existing.categories:
                changes.append(("categories", str(existing.categories), str(new_cats)))
                existing.categories = new_cats

        if normalized.tags:
            new_tags = list(set(existing.tags) | set(normalized.tags))
            if new_tags != existing.tags:
                changes.append(("tags", str(existing.tags), str(new_tags)))
                existing.tags = new_tags

        # Update organization if needed
        if existing.organization_id != org.id:
            existing.organization_id = org.id

        # Update location
        if location:
            existing.location_id = location.id

        # Update source if better tier
        existing_tier = existing.source.tier if existing.source else 5
        if source and (not existing.source_id or source.tier < existing_tier):
            existing.source_id = source.id
            existing.reliability_score = normalized.reliability_score

        # Update timestamps
        now = datetime.now(UTC)
        existing.last_scraped = normalized.fetched_at or now
        existing.updated_at = now

        if not changes:
            return LoadResult(
                resource_id=existing.id,
                organization_id=org.id,
                location_id=location.id if location else None,
                action="skipped",
            )

        # Record changes
        for field_name, old_val, new_val in changes:
            change_type = ChangeType.RISKY_CHANGE if field_name in self.RISKY_FIELDS else ChangeType.UPDATE
            change_log = ChangeLog(
                resource_id=existing.id,
                field=field_name,
                old_value=str(old_val) if old_val else None,
                new_value=str(new_val) if new_val else None,
                change_type=change_type,
            )
            self.session.add(change_log)

        # Flag for review if risky changes
        if needs_review:
            existing.status = ResourceStatus.NEEDS_REVIEW
            review = ReviewState(
                resource_id=existing.id,
                status=ReviewStatus.PENDING,
                reason="Automated update changed sensitive fields",
            )
            self.session.add(review)

        self.session.add(existing)

        # Create source record
        if source:
            self._create_source_record(existing, source, normalized)

        return LoadResult(
            resource_id=existing.id,
            organization_id=org.id,
            location_id=location.id if location else None,
            action="updated",
        )

    def _create_source_record(
        self,
        resource: Resource,
        source: Source,
        normalized: NormalizedResource,
    ) -> None:
        """Create a source record for audit trail."""
        # Generate hash of raw data
        raw_content = json.dumps(normalized.raw_data or {}, sort_keys=True)
        raw_hash = hashlib.sha256(raw_content.encode()).hexdigest()

        record = SourceRecord(
            resource_id=resource.id,
            source_id=source.id,
            url=normalized.source_url,
            fetched_at=normalized.fetched_at or datetime.now(UTC),
            raw_hash=raw_hash,
        )
        self.session.add(record)

        # Update source health
        source.last_run = datetime.now(UTC)
        source.last_success = datetime.now(UTC)
        source.health_status = HealthStatus.HEALTHY
        source.error_count = 0
        self.session.add(source)
