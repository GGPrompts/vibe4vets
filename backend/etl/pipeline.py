"""ETL Pipeline orchestrator.

Chains normalization, deduplication, enrichment, and loading
into a complete pipeline with error handling and statistics.
"""

from datetime import datetime
from typing import Protocol

from sqlmodel import Session

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
    """

    def __init__(
        self,
        session: Session,
        geocoder: GeocoderProtocol | None = None,
        title_similarity_threshold: float = 0.85,
    ):
        """Initialize the pipeline.

        Args:
            session: Database session for loading.
            geocoder: Optional geocoding service.
            title_similarity_threshold: Threshold for deduplication.
        """
        self.session = session
        self.normalizer = Normalizer()
        self.deduplicator = Deduplicator(title_threshold=title_similarity_threshold)
        self.enricher = Enricher(geocoder=geocoder)
        self.loader = Loader(session)

    def run(self, connectors: list[Connector]) -> ETLResult:
        """Run the full ETL pipeline for multiple connectors.

        Args:
            connectors: List of data source connectors.

        Returns:
            ETLResult with statistics and errors.
        """
        started_at = datetime.utcnow()
        stats = ETLStats()
        errors: list[ETLError] = []

        # Collect all normalized resources from all connectors
        all_normalized: list[NormalizedResource] = []

        # Step 1: Extract and Normalize from each connector
        for connector in connectors:
            source_name = connector.metadata.name
            source_tier = connector.metadata.tier

            try:
                # Extract
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
                errors.append(
                    ETLError(
                        stage="extract",
                        message=f"Connector {source_name} failed: {str(e)}",
                        exception=type(e).__name__,
                    )
                )

        if not all_normalized:
            return ETLResult(
                success=len(errors) == 0,
                stats=stats,
                errors=errors,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        # Step 2: Deduplicate across all sources
        deduplicated, num_removed = self.deduplicator.deduplicate(all_normalized)
        stats.deduplicated = num_removed

        # Step 3: Enrich
        enriched = self.enricher.enrich_batch(deduplicated)
        stats.enriched = len(enriched)

        # Step 4: Load
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

        return ETLResult(
            success=stats.failed == 0 and len([e for e in errors if e.stage == "extract"]) == 0,
            stats=stats,
            errors=errors,
            started_at=started_at,
            completed_at=datetime.utcnow(),
        )

    def run_single(self, connector: Connector) -> ETLResult:
        """Run the pipeline for a single connector.

        Convenience method for running one connector.

        Args:
            connector: Single data source connector.

        Returns:
            ETLResult with statistics and errors.
        """
        return self.run([connector])

    def normalize_only(
        self, connector: Connector
    ) -> tuple[list[NormalizedResource], list[ETLError]]:
        """Run only the normalization step.

        Useful for testing connectors without loading to database.

        Args:
            connector: Data source connector.

        Returns:
            Tuple of (normalized resources, errors).
        """
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
        started_at = datetime.utcnow()
        stats = ETLStats()
        errors: list[ETLError] = []

        all_normalized: list[NormalizedResource] = []

        # Extract and normalize
        for connector in connectors:
            source_name = connector.metadata.name
            source_tier = connector.metadata.tier

            try:
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
            completed_at=datetime.utcnow(),
        )


def create_pipeline(
    session: Session,
    geocoder: GeocoderProtocol | None = None,
) -> ETLPipeline:
    """Factory function to create an ETL pipeline.

    Args:
        session: Database session.
        geocoder: Optional geocoding service.

    Returns:
        Configured ETLPipeline instance.
    """
    return ETLPipeline(session=session, geocoder=geocoder)
