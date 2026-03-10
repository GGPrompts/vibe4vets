#!/usr/bin/env python3
"""Backup Railway production database before running jobs.

Creates timestamped pg_dump backups in backend/backups/.
Keeps the last 5 backups by default.

Usage:
    python scripts/backup_production.py              # Full backup
    python scripts/backup_production.py --tables     # Data tables only (faster)
    python scripts/backup_production.py --keep 10    # Keep last 10 backups
    python scripts/backup_production.py --list       # List existing backups
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path(__file__).parent.parent / "backups"


def get_railway_url() -> str:
    """Get Railway database public URL from CLI."""
    result = subprocess.run(
        ["railway", "variables", "--service", "Postgres", "--json"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get Railway URL: {result.stderr}")

    variables = json.loads(result.stdout)
    url = variables.get("DATABASE_PUBLIC_URL") or variables.get("DATABASE_URL")
    if not url:
        raise RuntimeError("No DATABASE_PUBLIC_URL or DATABASE_URL found in Railway variables")
    return url


def list_backups():
    """List existing backups with sizes."""
    if not BACKUP_DIR.exists():
        print("No backups directory found.")
        return

    backups = sorted(BACKUP_DIR.glob("vibe4vets_*.dump"), reverse=True)
    if not backups:
        print("No backups found.")
        return

    print(f"Backups in {BACKUP_DIR}/:\n")
    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {backup.name:45s}  {size_mb:6.1f} MB  {mtime:%Y-%m-%d %H:%M}")

    total_mb = sum(b.stat().st_size for b in backups) / (1024 * 1024)
    print(f"\n  {len(backups)} backups, {total_mb:.1f} MB total")


def cleanup_old_backups(keep: int):
    """Remove old backups, keeping the most recent N."""
    if not BACKUP_DIR.exists():
        return

    backups = sorted(BACKUP_DIR.glob("vibe4vets_*.dump"), reverse=True)
    for old_backup in backups[keep:]:
        old_backup.unlink()
        print(f"  Removed old backup: {old_backup.name}")


def run_backup(tables_only: bool = False, keep: int = 5) -> Path:
    """Run pg_dump against Railway and save locally."""
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_tables" if tables_only else "_full"
    backup_file = BACKUP_DIR / f"vibe4vets_{timestamp}{suffix}.dump"

    print(f"[{datetime.now():%H:%M:%S}] Starting production backup...")

    # Get Railway URL
    try:
        railway_url = get_railway_url()
        # Mask password in output
        masked = railway_url.split("@")[-1] if "@" in railway_url else "***"
        print(f"  Target: {masked}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Build pg_dump command
    cmd = ["pg_dump", "-Fc"]  # Custom format (compressed)

    if tables_only:
        # Only data tables, skip system/audit tables for speed
        for table in [
            "organizations",
            "locations",
            "resources",
            "sources",
            "source_records",
        ]:
            cmd.extend(["-t", table])

    cmd.extend(["-f", str(backup_file), railway_url])

    print(f"  Dumping {'data tables' if tables_only else 'full database'}...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        backup_file.unlink(missing_ok=True)
        sys.exit(1)

    size_mb = backup_file.stat().st_size / (1024 * 1024)
    print(f"  Saved: {backup_file.name} ({size_mb:.1f} MB)")

    # Cleanup old backups
    cleanup_old_backups(keep)

    print(f"[{datetime.now():%H:%M:%S}] Backup complete!")
    print(f"\n  To restore: pg_restore -d <DATABASE_URL> {backup_file}")

    return backup_file


def main():
    parser = argparse.ArgumentParser(description="Backup Railway production database")
    parser.add_argument("--tables", action="store_true", help="Backup data tables only (faster)")
    parser.add_argument("--keep", type=int, default=5, help="Number of backups to keep (default: 5)")
    parser.add_argument("--list", action="store_true", help="List existing backups")
    args = parser.parse_args()

    if args.list:
        list_backups()
        return

    run_backup(tables_only=args.tables, keep=args.keep)


if __name__ == "__main__":
    main()
