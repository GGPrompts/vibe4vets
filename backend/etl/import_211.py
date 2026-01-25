#!/usr/bin/env python
"""ETL import pipeline for 211 veteran resources.

Usage:
    python -m etl.import_211              # Import all states
    python -m etl.import_211 --dry-run    # Preview only
    python -m etl.import_211 --state CA   # Import specific state
    python -m etl.import_211 --state CA --state TX  # Multiple states
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.database import engine
from app.models import Location, Organization, Resource
from connectors.base import ResourceCandidate
from connectors.two_one_one import TwoOneOneConnector


@dataclass
class ImportStats:
    """Statistics for the 211 import run."""

    extracted: int = 0
    new: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    by_state: dict[str, int] = field(default_factory=dict)
    error_messages: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        """Total successfully processed records."""
        return self.new + self.updated + self.skipped

    def summary(self) -> str:
        """Return human-readable summary."""
        lines = [
            f"Extracted: {self.extracted}",
            f"New:       {self.new}",
            f"Updated:   {self.updated}",
            f"Skipped:   {self.skipped}",
            f"Errors:    {self.errors}",
        ]
        if self.by_state:
            lines.append("\nBy state:")
            for state, count in sorted(self.by_state.items()):
                lines.append(f"  {state}: {count}")
        if self.error_messages:
            lines.append("\nErrors:")
            for msg in self.error_messages[:10]:  # Limit to first 10
                lines.append(f"  - {msg}")
            if len(self.error_messages) > 10:
                lines.append(f"  ... and {len(self.error_messages) - 10} more")
        return "\n".join(lines)


class TwoOneOneImporter:
    """Import pipeline for 211 veteran resources."""

    def __init__(
        self,
        session: Session,
        states: list[str] | None = None,
        dry_run: bool = False,
    ):
        """Initialize the importer.

        Args:
            session: Database session.
            states: List of state codes to import. Defaults to all available.
            dry_run: If True, preview changes without committing.
        """
        self.session = session
        self.connector = TwoOneOneConnector(states=states)
        self.dry_run = dry_run
        self.stats = ImportStats()

        # Cache for organizations to avoid repeated lookups
        self._org_cache: dict[str, Organization] = {}

    def run(self) -> ImportStats:
        """Run the import pipeline.

        Returns:
            ImportStats with results.
        """
        print(f"Starting 211 import (dry_run={self.dry_run})...")
        print(f"States: {', '.join(self.connector.states)}")
        print()

        # Extract resources from connector
        candidates = self.connector.run()
        self.stats.extracted = len(candidates)
        print(f"Extracted {len(candidates)} resources from 211 data files")

        # In dry-run mode without DB, just show what would be imported
        if self.dry_run and not self._db_available():
            print("(Database not available - showing extraction stats only)")
            for candidate in candidates:
                state = candidate.state or "UNKNOWN"
                if state not in self.stats.by_state:
                    self.stats.by_state[state] = 0
                self.stats.by_state[state] += 1
                # In dry-run without DB, assume all are new
                self.stats.new += 1
            return self.stats

        # Process each candidate
        for candidate in candidates:
            try:
                action = self._process_candidate(candidate)
                state = candidate.state or "UNKNOWN"

                # Track by state
                if state not in self.stats.by_state:
                    self.stats.by_state[state] = 0
                self.stats.by_state[state] += 1

                if action == "new":
                    self.stats.new += 1
                elif action == "updated":
                    self.stats.updated += 1
                else:
                    self.stats.skipped += 1

            except Exception as e:
                self.stats.errors += 1
                self.stats.error_messages.append(f"{candidate.title}: {str(e)}")

        # Commit if not dry run
        if not self.dry_run:
            try:
                self.session.commit()
                print("Changes committed to database")
            except Exception as e:
                self.session.rollback()
                print(f"Error committing: {e}")
                self.stats.errors += 1
                self.stats.error_messages.append(f"Commit failed: {str(e)}")

        return self.stats

    def _db_available(self) -> bool:
        """Check if database connection is available."""
        try:
            # Try a simple query
            self.session.exec(select(Resource).limit(1))
            return True
        except Exception:
            return False

    def _process_candidate(self, candidate: ResourceCandidate) -> str:
        """Process a single resource candidate.

        Args:
            candidate: The resource candidate to process.

        Returns:
            Action taken: "new", "updated", or "skipped"
        """
        # Check for duplicates by name + state + phone
        existing = self._find_duplicate(candidate)

        if existing:
            # Check if update is needed
            if self._needs_update(existing, candidate):
                if not self.dry_run:
                    self._update_resource(existing, candidate)
                return "updated"
            return "skipped"

        # Create new resource
        if not self.dry_run:
            self._create_resource(candidate)
        return "new"

    def _find_duplicate(self, candidate: ResourceCandidate) -> Resource | None:
        """Find existing resource by name + state + phone.

        This is the deduplication key for 211 resources.
        """
        # Normalize for comparison
        name = (candidate.org_name or candidate.title or "").strip().lower()
        state = (candidate.state or "").strip().upper()
        phone = self._normalize_phone_for_compare(candidate.phone)

        if not name:
            return None

        # Query for potential duplicates
        # First try exact match on all three
        stmt = (
            select(Resource)
            .join(Organization)
            .where(
                Organization.name.ilike(name),
                Resource.states.contains([state]) if state else True,
            )
        )

        results = self.session.exec(stmt).all()

        # Filter by phone if present
        for resource in results:
            resource_phone = self._normalize_phone_for_compare(resource.phone)
            # Match if phones match OR if one is missing
            if phone and resource_phone:
                if phone == resource_phone:
                    return resource
            elif not phone or not resource_phone:
                # If phone is missing from one, match on name + state only
                return resource

        return None

    def _normalize_phone_for_compare(self, phone: str | None) -> str | None:
        """Normalize phone for comparison (digits only)."""
        if not phone:
            return None
        digits = "".join(c for c in phone if c.isdigit())
        # Handle 1- prefix
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        return digits if len(digits) == 10 else None

    def _needs_update(self, existing: Resource, candidate: ResourceCandidate) -> bool:
        """Check if existing resource needs updating."""
        # Compare key fields
        if candidate.description and candidate.description != existing.description:
            return True
        if candidate.phone and candidate.phone != existing.phone:
            return True
        if candidate.email and candidate.hours != existing.hours:
            return True
        # Check if categories expanded
        new_cats = set(candidate.categories or [])
        existing_cats = set(existing.categories or [])
        return bool(new_cats - existing_cats)  # True if new categories to add

    def _get_or_create_organization(self, candidate: ResourceCandidate) -> Organization:
        """Find existing organization or create new one."""
        org_name = candidate.org_name or candidate.title
        org_key = org_name.lower().strip()

        # Check cache
        if org_key in self._org_cache:
            return self._org_cache[org_key]

        # Look up in database (case-insensitive)
        stmt = select(Organization).where(Organization.name.ilike(org_name))
        org = self.session.exec(stmt).first()

        if org:
            # Update website if we have a better one
            if candidate.org_website and not org.website:
                org.website = candidate.org_website
                org.updated_at = datetime.now(UTC)
                self.session.add(org)
            self._org_cache[org_key] = org
            return org

        # Create new organization
        org = Organization(
            name=org_name,
            website=candidate.org_website,
        )
        self.session.add(org)
        self.session.flush()  # Get ID

        self._org_cache[org_key] = org
        return org

    def _get_or_create_location(self, candidate: ResourceCandidate, org: Organization) -> Location | None:
        """Find existing location or create new one."""
        if not (candidate.address and candidate.city and candidate.state):
            return None

        # Look up existing location for this org with same address
        stmt = select(Location).where(
            Location.organization_id == org.id,
            Location.address == candidate.address,
            Location.city == candidate.city,
            Location.state == candidate.state,
        )
        location = self.session.exec(stmt).first()

        if location:
            return location

        # Create new location
        location = Location(
            organization_id=org.id,
            address=candidate.address,
            city=candidate.city,
            state=candidate.state,
            zip_code=candidate.zip_code or "",
        )
        self.session.add(location)
        self.session.flush()

        return location

    def _create_resource(self, candidate: ResourceCandidate) -> Resource:
        """Create a new resource from candidate."""
        now = datetime.now(UTC)

        # Get or create organization
        org = self._get_or_create_organization(candidate)

        # Get or create location
        location = self._get_or_create_location(candidate, org)

        # Map scope
        scope = candidate.scope or "state"

        resource = Resource(
            organization_id=org.id,
            location_id=location.id if location else None,
            title=candidate.title,
            description=candidate.description or "",
            eligibility=candidate.eligibility,
            how_to_apply=candidate.how_to_apply,
            categories=candidate.categories or [],
            tags=candidate.tags or [],
            scope=scope,
            states=candidate.states or ([candidate.state] if candidate.state else []),
            website=candidate.org_website,
            phone=candidate.phone,
            hours=candidate.hours,
            source_url=candidate.source_url,
            last_scraped=candidate.fetched_at or now,
            last_verified=now,
            freshness_score=1.0,
            reliability_score=0.7,  # 211 is tier 2 - established nonprofit
            created_at=now,
            updated_at=now,
        )

        self.session.add(resource)
        self.session.flush()

        return resource

    def _update_resource(self, existing: Resource, candidate: ResourceCandidate) -> None:
        """Update an existing resource with new data."""
        now = datetime.now(UTC)

        # Update fields if candidate has better data
        if candidate.description and len(candidate.description) > len(existing.description or ""):
            existing.description = candidate.description

        if candidate.phone and not existing.phone:
            existing.phone = candidate.phone

        if candidate.hours and not existing.hours:
            existing.hours = candidate.hours

        if candidate.eligibility and not existing.eligibility:
            existing.eligibility = candidate.eligibility

        if candidate.how_to_apply and not existing.how_to_apply:
            existing.how_to_apply = candidate.how_to_apply

        # Merge categories
        if candidate.categories:
            new_cats = list(set(existing.categories or []) | set(candidate.categories))
            existing.categories = new_cats

        # Merge tags
        if candidate.tags:
            new_tags = list(set(existing.tags or []) | set(candidate.tags))
            existing.tags = new_tags

        # Update timestamps
        existing.last_scraped = candidate.fetched_at or now
        existing.updated_at = now

        self.session.add(existing)


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Import 211 veteran resources into the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m etl.import_211              # Import all states
    python -m etl.import_211 --dry-run    # Preview only
    python -m etl.import_211 --state CA   # Import specific state
    python -m etl.import_211 --state CA --state TX  # Multiple states
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without committing to database",
    )

    parser.add_argument(
        "--state",
        action="append",
        dest="states",
        metavar="STATE",
        help="State code to import (can be specified multiple times)",
    )

    args = parser.parse_args()

    # Validate states if provided
    available_states = TwoOneOneConnector.AVAILABLE_STATES
    if args.states:
        invalid = [s for s in args.states if s.upper() not in available_states]
        if invalid:
            print(f"Error: Invalid state codes: {', '.join(invalid)}")
            print(f"Available states: {', '.join(available_states)}")
            return 1
        # Normalize to uppercase
        args.states = [s.upper() for s in args.states]

    # Run import
    try:
        with Session(engine) as session:
            importer = TwoOneOneImporter(
                session=session,
                states=args.states,
                dry_run=args.dry_run,
            )
            stats = importer.run()

            print()
            print("=" * 40)
            print("IMPORT RESULTS")
            print("=" * 40)
            print(stats.summary())

            if args.dry_run:
                print()
                print("DRY RUN - No changes committed")

            return 0 if stats.errors == 0 else 1

    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
