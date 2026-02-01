#!/usr/bin/env python3
"""Seed production database with resources from all connectors.

This script runs all connectors in sequence to populate the database.
It's designed to be run locally with the DATABASE_URL pointing to production.

Usage:
    cd backend
    source .venv/bin/activate
    DATABASE_URL="postgresql://..." python scripts/seed_production.py
"""

import logging
import sys
from datetime import datetime

from sqlmodel import Session

from app.database import engine
from connectors.base import BaseConnector
from etl import ETLPipeline
from jobs.refresh import CONNECTOR_REGISTRY

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def run_connector(session: Session, name: str, connector_cls: type[BaseConnector]) -> dict:
    """Run a single connector and return stats."""
    try:
        logger.info(f"Starting: {name}")
        connector = connector_cls()
        pipeline = ETLPipeline(session=session)
        result = pipeline.run([connector])

        stats = {
            "name": name,
            "success": result.success,
            "created": result.stats.created,
            "updated": result.stats.updated,
            "errors": len(result.errors),
        }

        if result.errors:
            for e in result.errors[:3]:  # Show first 3 errors
                logger.warning(f"  {name} error: {e.message}")

        logger.info(f"Completed: {name} - created={result.stats.created}, updated={result.stats.updated}")
        return stats

    except Exception as e:
        logger.error(f"Failed: {name} - {e}")
        return {
            "name": name,
            "success": False,
            "error": str(e),
            "created": 0,
            "updated": 0,
        }


def main():
    """Run all connectors."""
    start = datetime.now()
    logger.info(f"Starting production seed at {start}")
    logger.info(f"Found {len(CONNECTOR_REGISTRY)} connectors")

    # Priority order - run important connectors first
    priority_connectors = [
        # Tier 1 Federal (most important)
        "va_gov",
        "vet_centers",
        "careeronestop",
        "gi_bill_schools",
        "ssvf",
        "hud_vash",
        "gpd",
        "vboc",
        "skillbridge",
        "apprenticeship",
        "hrsa_health_centers",
        # Tier 2 Major nonprofits
        "legal_aid",
        "mental_health",
        "fisher_house",
        "veterans_court",
        "feeding_america",
        # Tier 2 VSO posts
        "vfw_posts",
        "american_legion_posts",
        "dav_chapters",
        # Tier 2 Additional
        "certifications",
        "veteran_employers",
        "scholarships",
        "state_va",
        "state_va_offices",
        "cvso",
    ]

    # Add any remaining connectors
    remaining = [n for n in CONNECTOR_REGISTRY if n not in priority_connectors]
    all_connectors = priority_connectors + remaining

    results = []
    total_created = 0
    total_updated = 0
    failed = []

    with Session(engine) as session:
        for name in all_connectors:
            if name not in CONNECTOR_REGISTRY:
                logger.warning(f"Connector not found: {name}")
                continue

            connector_cls = CONNECTOR_REGISTRY[name]
            result = run_connector(session, name, connector_cls)
            results.append(result)

            if result.get("success"):
                total_created += result.get("created", 0)
                total_updated += result.get("updated", 0)
            else:
                failed.append(name)

    duration = datetime.now() - start

    # Summary
    logger.info("=" * 60)
    logger.info(f"SEED COMPLETE in {duration}")
    logger.info(f"Total created: {total_created}")
    logger.info(f"Total updated: {total_updated}")
    logger.info(f"Successful: {len(results) - len(failed)}/{len(results)}")

    if failed:
        logger.warning(f"Failed connectors: {', '.join(failed)}")

    # Return exit code
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
