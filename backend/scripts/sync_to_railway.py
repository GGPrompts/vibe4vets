#!/usr/bin/env python3
"""Efficient sync of local database changes to Railway.

Instead of pg_dump/pg_restore (which generates massive WAL), this script
syncs only the changed fields using UPDATE statements, minimizing storage bloat.

Usage:
    python scripts/sync_to_railway.py              # Sync all changed data
    python scripts/sync_to_railway.py --dry-run    # Show what would sync
    python scripts/sync_to_railway.py --table resources  # Sync specific table
"""

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_railway_url() -> str:
    """Get Railway database URL from CLI."""
    result = subprocess.run(
        ["railway", "variables", "--service", "Postgres", "--json"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get Railway URL: {result.stderr}")

    import json
    vars = json.loads(result.stdout)
    return vars.get("DATABASE_PUBLIC_URL") or vars.get("DATABASE_URL")


def run_psql(url: str, command: str, input_file: str | None = None) -> str:
    """Run psql command against a database."""
    cmd = ["docker", "exec"]
    if input_file:
        cmd.append("-i")
    cmd.extend(["vibe4vets-db-1", "psql", url, "-c", command])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        raise RuntimeError(f"psql error: {result.stderr}")
    return result.stdout


def run_psql_file(url: str, sql: str) -> str:
    """Run SQL from string against a database."""
    cmd = ["docker", "exec", "-i", "vibe4vets-db-1", "psql", url]
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if result.returncode != 0 and "ERROR" in result.stderr:
        raise RuntimeError(f"psql error: {result.stderr}")
    return result.stdout


def export_csv(local_url: str, query: str, output_path: str) -> int:
    """Export query results to CSV, return row count."""
    # Run inside docker container
    copy_cmd = f"\\COPY ({query}) TO '{output_path}' WITH CSV HEADER"
    result = subprocess.run(
        ["docker", "exec", "vibe4vets-db-1", "psql", local_url, "-c", copy_cmd],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Export failed: {result.stderr}")

    # Parse row count from "COPY N"
    for line in result.stdout.split("\n"):
        if line.startswith("COPY"):
            return int(line.split()[1])
    return 0


def import_and_update(railway_url: str, csv_path: str, table: str, columns: list[str], key: str = "id") -> int:
    """Import CSV to temp table and update target table."""
    columns_str = ", ".join(columns)
    set_clause = ", ".join(f"{col} = u.{col}" for col in columns if col != key)

    sql = f"""
-- Create temp table
CREATE TEMP TABLE {table}_updates AS
SELECT * FROM {table} WHERE 1=0;

-- Import data
\\COPY {table}_updates ({columns_str}) FROM '{csv_path}' WITH CSV HEADER

-- Update target table
UPDATE {table} t SET {set_clause}
FROM {table}_updates u
WHERE t.{key} = u.{key};

-- Report count
SELECT COUNT(*) as updated FROM {table}_updates;
"""

    result = subprocess.run(
        ["docker", "exec", "-i", "vibe4vets-db-1", "psql", railway_url],
        input=sql,
        capture_output=True,
        text=True,
    )

    # Parse updated count
    for line in result.stdout.split("\n"):
        if line.strip().isdigit():
            return int(line.strip())
    return 0


def sync_resources(local_url: str, railway_url: str, dry_run: bool = False) -> dict:
    """Sync resource link health, freshness, and status data."""
    print("Syncing resources...")

    # Fields that change from jobs
    columns = [
        "id",
        "link_health_score",
        "link_http_status",
        "link_checked_at",
        "link_flagged_reason",
        "freshness_score",
        "reliability_score",
        "status",
        "website",  # Include in case URLs were fixed
    ]

    query = f"SELECT {', '.join(columns)} FROM resources"
    csv_path = "/tmp/resources_sync.csv"

    # Export from local
    count = export_csv(local_url, query, csv_path)
    print(f"  Exported {count} resources from local")

    if dry_run:
        print(f"  [DRY RUN] Would sync {count} resources to Railway")
        return {"resources": count, "synced": 0}

    # Import and update on Railway
    updated = import_and_update(railway_url, csv_path, "resources", columns)
    print(f"  Updated {updated} resources on Railway")

    return {"resources": count, "synced": updated}


def sync_locations(local_url: str, railway_url: str, dry_run: bool = False) -> dict:
    """Sync location data."""
    print("Syncing locations...")

    # Get column list (exclude geog which Railway doesn't have)
    columns = [
        "id", "organization_id", "address", "city", "state", "zip_code",
        "latitude", "longitude", "service_area", "created_at",
    ]

    query = f"SELECT {', '.join(columns)} FROM locations"
    csv_path = "/tmp/locations_sync.csv"

    count = export_csv(local_url, query, csv_path)
    print(f"  Exported {count} locations from local")

    if dry_run:
        print(f"  [DRY RUN] Would sync {count} locations to Railway")
        return {"locations": count, "synced": 0}

    # For locations, we need to handle inserts too (new locations)
    # Use upsert pattern
    columns_str = ", ".join(columns)

    sql = f"""
CREATE TEMP TABLE locations_updates AS SELECT * FROM locations WHERE 1=0;
\\COPY locations_updates ({columns_str}) FROM '{csv_path}' WITH CSV HEADER

-- Upsert: insert new, update existing
INSERT INTO locations ({columns_str})
SELECT {columns_str} FROM locations_updates
ON CONFLICT (id) DO UPDATE SET
    address = EXCLUDED.address,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    zip_code = EXCLUDED.zip_code,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude;

SELECT COUNT(*) FROM locations_updates;
"""

    result = subprocess.run(
        ["docker", "exec", "-i", "vibe4vets-db-1", "psql", railway_url],
        input=sql,
        capture_output=True,
        text=True,
    )

    print(f"  Synced locations to Railway")
    return {"locations": count, "synced": count}


def verify_sync(local_url: str, railway_url: str) -> bool:
    """Verify sync by comparing counts."""
    print("\nVerifying sync...")

    local_count = run_psql(local_url, "SELECT COUNT(*) FROM resources WHERE status = 'ACTIVE';")
    railway_count = run_psql(railway_url, "SELECT COUNT(*) FROM resources WHERE status = 'ACTIVE';")

    # Parse counts
    local_n = int([l for l in local_count.split("\n") if l.strip().isdigit()][0])
    railway_n = int([l for l in railway_count.split("\n") if l.strip().isdigit()][0])

    print(f"  Local active resources:   {local_n}")
    print(f"  Railway active resources: {railway_n}")

    if local_n == railway_n:
        print("  ✓ Counts match!")
        return True
    else:
        print(f"  ✗ Count mismatch: {abs(local_n - railway_n)} difference")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync local database to Railway")
    parser.add_argument("--dry-run", action="store_true", help="Show what would sync without executing")
    parser.add_argument("--table", choices=["resources", "locations", "all"], default="all",
                        help="Which table to sync (default: all)")
    parser.add_argument("--skip-verify", action="store_true", help="Skip verification step")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Railway sync...")

    # Get database URLs
    local_url = "postgresql://vibe4vets:localdev@localhost:5432/vibe4vets"

    try:
        railway_url = get_railway_url()
        print(f"  Railway URL: {railway_url[:50]}...")
    except Exception as e:
        print(f"Error getting Railway URL: {e}")
        print("Make sure you're in the vibe4vets directory and Railway CLI is configured.")
        sys.exit(1)

    results = {}

    # Sync tables
    if args.table in ("resources", "all"):
        results.update(sync_resources(local_url, railway_url, args.dry_run))

    if args.table in ("locations", "all"):
        results.update(sync_locations(local_url, railway_url, args.dry_run))

    # Verify
    if not args.dry_run and not args.skip_verify:
        verify_sync(local_url, railway_url)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sync complete!")
    print(f"  Resources: {results.get('resources', 0)}")
    print(f"  Locations: {results.get('locations', 0)}")


if __name__ == "__main__":
    main()
