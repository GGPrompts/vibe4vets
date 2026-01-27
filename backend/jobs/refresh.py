"""Full resource refresh job.

Runs all registered connectors through the ETL pipeline to:
- Fetch fresh data from sources (VA.gov, CareerOneStop, etc.)
- Normalize and deduplicate resources
- Update database with new/changed resources
- Track statistics and errors
"""

from typing import Any

from sqlmodel import Session

from connectors import (
    ApprenticeshipConnector,
    CareerOneStopConnector,
    CertificationsConnector,
    CVSOConnector,
    GIBillSchoolsConnector,
    GPDConnector,
    HUDVASHConnector,
    LegalAidConnector,
    SkillBridgeConnector,
    SSVFConnector,
    StandDownEventsConnector,
    StateVAConnector,
    TwoOneOneConnector,
    UnitedWayConnector,
    VAGovConnector,
    VBOCConnector,
    VetCentersConnector,
    VeteranEmergencyAssistanceConnector,
    VeteranEmployersConnector,
    VeteransCourtConnector,
)
from connectors.base import BaseConnector
from etl import ETLPipeline
from jobs.base import BaseJob

# Registry of available connectors
# Grouped by category for clarity
CONNECTOR_REGISTRY: dict[str, type[BaseConnector]] = {
    # Tier 1: Official Federal APIs
    "va_gov": VAGovConnector,  # VA facilities
    "vet_centers": VetCentersConnector,  # VA Vet Centers (readjustment counseling)
    "careeronestop": CareerOneStopConnector,  # DOL American Job Centers
    "gi_bill_schools": GIBillSchoolsConnector,  # VA GIDS (GI Bill schools)
    "apprenticeship": ApprenticeshipConnector,  # DOL apprenticeship offices
    # Tier 1: Official Federal Data (file-based)
    "ssvf": SSVFConnector,  # SSVF grantees (housing)
    "hud_vash": HUDVASHConnector,  # HUD-VASH awards (housing)
    "gpd": GPDConnector,  # Grant and Per Diem (homeless shelters)
    "vboc": VBOCConnector,  # SBA Veterans Business Outreach Centers
    "skillbridge": SkillBridgeConnector,  # DOD SkillBridge partners
    "stand_down_events": StandDownEventsConnector,  # VA Stand Down outreach events
    # Tier 2: Established Nonprofits/Directories
    "legal_aid": LegalAidConnector,  # LSC-funded legal aid
    "veterans_court": VeteransCourtConnector,  # Veterans Treatment Courts
    "certifications": CertificationsConnector,  # Veteran certification programs
    "veteran_employers": VeteranEmployersConnector,  # Veteran-friendly employers
    "veteran_emergency_assistance": VeteranEmergencyAssistanceConnector,  # Emergency financial assistance
    # Tier 3: State/County Level
    "state_va": StateVAConnector,  # State VA agencies
    "cvso": CVSOConnector,  # County Veteran Service Officers
    # Tier 4: Community Directories
    "two_one_one": TwoOneOneConnector,  # 211 national database
    "united_way": UnitedWayConnector,  # United Way/Missions United
}


class RefreshJob(BaseJob):
    """Job to refresh resources from data sources.

    Runs connectors and processes through the ETL pipeline.
    Supports:
    - Running all connectors or specific ones
    - Dry-run mode for testing
    """

    @property
    def name(self) -> str:
        return "refresh"

    @property
    def description(self) -> str:
        return "Refresh resources from all data sources"

    def execute(
        self,
        session: Session,
        connector_name: str | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run the refresh job.

        Args:
            session: Database session.
            connector_name: Optional specific connector to run.
                           If None, runs all registered connectors.
            dry_run: If True, don't persist changes to database.
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary with counts.
        """
        # Build list of connectors to run
        connectors = self._get_connectors(connector_name)

        if not connectors:
            return {
                "error": "No connectors found" + (f" matching '{connector_name}'" if connector_name else ""),
                "connectors_run": 0,
            }

        self._log(f"Running {len(connectors)} connector(s)")

        # Create ETL pipeline
        pipeline = ETLPipeline(session=session)

        # Run pipeline
        if dry_run:
            self._log("Running in dry-run mode (no database changes)")
            result = pipeline.dry_run(connectors)
        else:
            result = pipeline.run(connectors)

        # Build stats from ETL result
        stats: dict[str, Any] = {
            "success": result.success,
            "connectors_run": len(connectors),
            "extracted": result.stats.extracted,
            "normalized": result.stats.normalized,
            "deduplicated": result.stats.deduplicated,
            "created": result.stats.created,
            "updated": result.stats.updated,
            "skipped": result.stats.skipped,
            "failed": result.stats.failed,
            "errors": len(result.errors),
            "duration_seconds": (
                (result.completed_at - result.started_at).total_seconds() if result.completed_at else None
            ),
        }

        # Log errors if any
        for error in result.errors:
            self._log(f"ETL error in {error.stage}: {error.message}", level="warning")

        return stats

    def _get_connectors(self, connector_name: str | None = None) -> list[BaseConnector]:
        """Get connector instances to run.

        Args:
            connector_name: Specific connector name or None for all.

        Returns:
            List of connector instances.
        """
        if connector_name:
            # Run specific connector
            connector_cls = CONNECTOR_REGISTRY.get(connector_name)
            if connector_cls:
                return [connector_cls()]
            return []

        # Run all connectors
        connectors: list[BaseConnector] = []
        for name, connector_cls in CONNECTOR_REGISTRY.items():
            try:
                connectors.append(connector_cls())
            except Exception as e:
                self._log(f"Failed to initialize connector {name}: {e}", level="warning")

        return connectors

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format refresh statistics into a message."""
        if not stats.get("success", False):
            return f"Refresh failed with {stats.get('errors', 0)} errors"

        created = stats.get("created", 0)
        updated = stats.get("updated", 0)
        skipped = stats.get("skipped", 0)

        return f"Refresh complete: {created} created, {updated} updated, {skipped} skipped"


def get_available_connectors() -> list[dict[str, Any]]:
    """Get list of available connectors with metadata.

    Returns:
        List of connector info dictionaries.
    """
    result: list[dict[str, Any]] = []

    for name, connector_cls in CONNECTOR_REGISTRY.items():
        try:
            connector = connector_cls()
            metadata = connector.metadata
            result.append(
                {
                    "name": name,
                    "display_name": metadata.name,
                    "url": metadata.url,
                    "tier": metadata.tier,
                    "frequency": metadata.frequency,
                    "requires_auth": metadata.requires_auth,
                }
            )
        except Exception:
            result.append(
                {
                    "name": name,
                    "display_name": name,
                    "error": "Failed to load metadata",
                }
            )

    return result
