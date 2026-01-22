"""ETL Pipeline orchestrator.

Chains normalization, deduplication, enrichment, and loading
into a complete pipeline with error handling and statistics.

Supports idempotent operations via:
- ETLJobRun tracking for checkpoint/resume
- Batch transactions with rollback on failure
- Skip already-processed URLs on retry
"""

import uuid
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models import ETLJobRun, ETLJobStatus
from connectors.base import Connector
from etl.dedupe import Deduplicator
from etl.enrich import Enricher, GeocoderProtocol
from etl.loader import Loader
from etl.models import ETLError, ETLResult, ETLStats, NormalizedResource
from etl.normalize import Normalizer


class ETLPipeline:
    """Main ETL pipeline orchestrator.

    Runs the full ETL process:
    1. Extract - Run connectors to get ResourceCandidates
    2. Normalize - Validate and normalize data
    3. Deduplicate - Remove duplicates across sources
    4. Enrich - Add geocoding, tags, trust scores
    5. Load - Store in database with conflict handling

    Supports idempotent operations:
    - Create a job_run with start_job() to enable checkpointing
    - Resume from failure with resume_job()
    - Already-processed URLs are skipped on retry
    """

    def __init__(
        self,
        session: Session,
        geocoder: GeocoderProtocol | None = None,
        title_similarity_threshold: float = 0.85,
        job_run: ETLJobRun | None = None,
    ):
        """Initialize the pipeline.

        Args:
            session: Database session for loading.
            geocoder: Optional geocoding service.
            title_similarity_threshold: Threshold for deduplication.
            job_run: Optional ETLJobRun for checkpointing. Create with start_job().
        """
        self.session = session
        self.job_run = job_run
        self.normalizer = Normalizer()
        self.deduplicator = Deduplicator(title_threshold=title_similarity_threshold)
        self.enricher = Enricher(geocoder=geocoder)
        self.loader = Loader(session, job_run=job_run)

    def run(self, connectors: list[Connector]) -> ETLResult:
        """Run the full ETL pipeline for multiple connectors.

        This method is idempotent when job_run is set:
        - Already-processed URLs are skipped
        - Progress is checkpointed after each batch
        - Can be resumed from failure

        Args:
            connectors: List of data source connectors.

        Returns:
            ETLResult with statistics and errors.
        """
        started_at = datetime.now(UTC)
        stats = ETLStats()
        errors: list[ETLError] = []

        # Update job_run status if tracking
        if self.job_run:
            self.job_run.status = ETLJobStatus.RUNNING
            self.job_run.connector_names = [c.metadata.name for c in connectors]
            self.session.add(self.job_run)
            self.session.commit()

        # Collect all normalized resources from all connectors
        all_normalized: list[NormalizedResource] = []

        # Step 1: Extract and Normalize from each connector
        for connector_idx, connector in enumerate(connectors):
            source_name = connector.metadata.name
            source_tier = connector.metadata.tier

            try:
                # Extract using context manager to ensure HTTP client cleanup
                with connector:
                    candidates = connector.run()
                stats.extracted += len(candidates)

                # Normalize
                normalized, norm_errors = self.normalizer.normalize_batch(
                    candidates, source_name=source_name, source_tier=source_tier
                )

                stats.normalized += len(normalized)
                stats.normalized_failed += len(norm_errors)
                errors.extend(norm_errors)

                all_normalized.extend(normalized)

            except Exception as e:
                error = ETLError(
                    stage="extract",
                    message=f"Connector {source_name} failed: {str(e)}",
                    exception=type(e).__name__,
                )
                errors.append(error)

                # Update job_run with error info but continue with other connectors
                if self.job_run:
                    self.job_run.error_message = error.message
                    self.job_run.error_details = {
                        "connector": source_name,
                        "connector_idx": connector_idx,
                        "exception": type(e).__name__,
                    }
                    self.session.add(self.job_run)
                    self.session.commit()

        # Update job_run with extraction stats
        if self.job_run:
            self.job_run.total_extracted = stats.extracted
            self.session.add(self.job_run)
            self.session.commit()

        if not all_normalized:
            result = ETLResult(
                success=len(errors) == 0,
                stats=stats,
                errors=errors,
                started_at=started_at,
                completed_at=datetime.now(UTC),
            )
            self._finalize_job_run(result)
            return result

        # Step 2: Deduplicate across all sources
        deduplicated, num_removed = self.deduplicator.deduplicate(all_normalized)
        stats.deduplicated = num_removed

        # Step 3: Enrich
        enriched = self.enricher.enrich_batch(deduplicated)
        stats.enriched = len(enriched)

        # Step 4: Load (with batch transactions for idempotency)
        load_results, load_errors = self.loader.load_batch(enriched)
        errors.extend(load_errors)

        for result in load_results:
            if result.action == "created":
                stats.created += 1
            elif result.action == "updated":
                stats.updated += 1
            elif result.action == "skipped":
                stats.skipped += 1
            elif result.action == "failed":
                stats.failed += 1

        result = ETLResult(
            success=stats.failed == 0 and len([e for e in errors if e.stage == "extract"]) == 0,
            stats=stats,
            errors=errors,
            started_at=started_at,
            completed_at=datetime.now(UTC),
        )

        self._finalize_job_run(result)
        return result

    def _finalize_job_run(self, result: ETLResult) -> None:
        """Update job_run with final status and stats.

        Args:
            result: The ETLResult from the run.
        """
        if not self.job_run:
            return

        self.job_run.completed_at = result.completed_at
        self.job_run.total_processed = result.stats.total_processed
        self.job_run.total_created = result.stats.created
        self.job_run.total_updated = result.stats.updated
        self.job_run.total_skipped = result.stats.skipped
        self.job_run.total_failed = result.stats.failed

        if result.success:
            self.job_run.status = ETLJobStatus.COMPLETED
        elif result.stats.total_processed > 0:
            self.job_run.status = ETLJobStatus.PARTIALLY_COMPLETED
        else:
            self.job_run.status = ETLJobStatus.FAILED

        if result.errors:
            self.job_run.error_message = result.errors[0].message
            self.job_run.error_details = {
                "error_count": len(result.errors),
                "stages": list({e.stage for e in result.errors}),
            }

        self.session.add(self.job_run)
        self.session.commit()

    def run_single(self, connector: Connector) -> ETLResult:
        """Run the pipeline for a single connector.

        Convenience method for running one connector.

        Args:
            connector: Single data source connector.

        Returns:
            ETLResult with statistics and errors.
        """
        return self.run([connector])

    def normalize_only(self, connector: Connector) -> tuple[list[NormalizedResource], list[ETLError]]:
        """Run only the normalization step.

        Useful for testing connectors without loading to database.

        Args:
            connector: Data source connector.

        Returns:
            Tuple of (normalized resources, errors).
        """
        with connector:
            candidates = connector.run()
        return self.normalizer.normalize_batch(
            candidates,
            source_name=connector.metadata.name,
            source_tier=connector.metadata.tier,
        )

    def dry_run(self, connectors: list[Connector]) -> ETLResult:
        """Run the pipeline without loading to database.

        Useful for testing and previewing what would be loaded.

        Args:
            connectors: List of data source connectors.

        Returns:
            ETLResult with statistics (no database changes).
        """
        started_at = datetime.now(UTC)
        stats = ETLStats()
        errors: list[ETLError] = []

        all_normalized: list[NormalizedResource] = []

        # Extract and normalize
        for connector in connectors:
            source_name = connector.metadata.name
            source_tier = connector.metadata.tier

            try:
                # Extract using context manager to ensure HTTP client cleanup
                with connector:
                    candidates = connector.run()
                stats.extracted += len(candidates)

                normalized, norm_errors = self.normalizer.normalize_batch(
                    candidates, source_name=source_name, source_tier=source_tier
                )

                stats.normalized += len(normalized)
                stats.normalized_failed += len(norm_errors)
                errors.extend(norm_errors)
                all_normalized.extend(normalized)

            except Exception as e:
                errors.append(
                    ETLError(
                        stage="extract",
                        message=f"Connector {source_name} failed: {str(e)}",
                        exception=type(e).__name__,
                    )
                )

        if all_normalized:
            # Deduplicate
            deduplicated, num_removed = self.deduplicator.deduplicate(all_normalized)
            stats.deduplicated = num_removed

            # Enrich
            enriched = self.enricher.enrich_batch(deduplicated)
            stats.enriched = len(enriched)

            # In dry run, count all as would-be-created
            stats.created = len(enriched)

        return ETLResult(
            success=len(errors) == 0,
            stats=stats,
            errors=errors,
            started_at=started_at,
            completed_at=datetime.now(UTC),
        )


def create_pipeline(
    session: Session,
    geocoder: GeocoderProtocol | None = None,
    job_run: ETLJobRun | None = None,
) -> ETLPipeline:
    """Factory function to create an ETL pipeline.

    Args:
        session: Database session.
        geocoder: Optional geocoding service.
        job_run: Optional ETLJobRun for checkpointing.

    Returns:
        Configured ETLPipeline instance.
    """
    return ETLPipeline(session=session, geocoder=geocoder, job_run=job_run)


def start_job(session: Session, job_name: str) -> ETLJobRun:
    """Create a new ETL job run for tracking.

    Use this to enable idempotent ETL operations:

        job_run = start_job(session, "full_refresh")
        pipeline = create_pipeline(session, job_run=job_run)
        result = pipeline.run(connectors)

    If the job fails and is re-run with the same job_run:
    - Already-processed URLs are skipped
    - Progress continues from the last checkpoint

    Args:
        session: Database session.
        job_name: Name of the job (e.g., "full_refresh", "va_gov_refresh").

    Returns:
        New ETLJobRun instance (already committed to database).
    """
    job_run = ETLJobRun(
        id=uuid.uuid4(),
        job_name=job_name,
        status=ETLJobStatus.PENDING,
    )
    session.add(job_run)
    session.commit()
    return job_run


def resume_job(session: Session, job_id: uuid.UUID) -> ETLJobRun | None:
    """Resume an existing ETL job run.

    Use this to resume a failed or partially completed job:

        job_run = resume_job(session, job_id)
        if job_run:
            pipeline = create_pipeline(session, job_run=job_run)
            result = pipeline.run(connectors)

    The job will skip all URLs that were already processed in the previous run.

    Args:
        session: Database session.
        job_id: UUID of the job run to resume.

    Returns:
        The ETLJobRun if found and resumable, None otherwise.
    """
    job_run = session.get(ETLJobRun, job_id)
    if not job_run:
        return None

    # Only resume jobs that aren't completed or still running
    if job_run.status in (ETLJobStatus.COMPLETED, ETLJobStatus.RUNNING):
        return None

    return job_run


def get_latest_job(session: Session, job_name: str) -> ETLJobRun | None:
    """Get the most recent job run for a given job name.

    Useful for checking if a job needs to be resumed.

    Args:
        session: Database session.
        job_name: Name of the job.

    Returns:
        The most recent ETLJobRun for this job name, or None.
    """
    stmt = (
        select(ETLJobRun)
        .where(ETLJobRun.job_name == job_name)
        .order_by(ETLJobRun.started_at.desc())  # type: ignore[union-attr]
        .limit(1)
    )
    return session.exec(stmt).first()
