#!/usr/bin/env python3
"""Fast parallel link checker using asyncio.

Checks all resource URLs concurrently for faster processing.
"""

import asyncio
import sys
from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlmodel import Session, select

# Add backend to path
sys.path.insert(0, "/home/marci/projects/vibe4vets/backend")

from app.database import engine
from app.models.resource import Resource, ResourceStatus

# Concurrency settings
MAX_CONCURRENT = 50  # Max simultaneous requests
TIMEOUT = 15.0  # Seconds per request
BATCH_COMMIT_SIZE = 500  # Commit to DB every N resources


async def check_url(client: httpx.AsyncClient, url: str) -> dict:
    """Check a single URL and return status."""
    if not url:
        return {"status_code": None, "error": "no_url"}

    # Ensure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Skip obviously bad URLs
    if url in ("https://n/a", "https://N/A", "http://n/a"):
        return {"status_code": None, "error": "invalid_url"}

    try:
        response = await client.get(url, follow_redirects=True)
        return {
            "status_code": response.status_code,
            "final_url": str(response.url),
        }
    except httpx.TimeoutException:
        return {"status_code": None, "error": "timeout"}
    except httpx.TooManyRedirects:
        return {"status_code": None, "error": "too_many_redirects"}
    except httpx.ConnectError:
        return {"status_code": None, "error": "connection_failed"}
    except Exception as e:
        return {"status_code": None, "error": str(e)[:50]}


async def check_batch(resources: list[tuple[UUID, str]], semaphore: asyncio.Semaphore) -> list[tuple[UUID, dict]]:
    """Check a batch of URLs concurrently."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        async def check_with_semaphore(resource_id: UUID, url: str):
            async with semaphore:
                result = await check_url(client, url)
                return (resource_id, result)

        tasks = [check_with_semaphore(rid, url) for rid, url in resources]
        return await asyncio.gather(*tasks)


def update_resources(session: Session, results: list[tuple[UUID, dict]]) -> dict:
    """Update resources with check results."""
    stats = {"healthy": 0, "broken": 0}

    for resource_id, result in results:
        resource = session.get(Resource, resource_id)
        if not resource:
            continue

        resource.link_checked_at = datetime.now(UTC)

        status_code = result.get("status_code")
        error = result.get("error")

        if status_code and status_code < 400:
            # Healthy
            resource.link_http_status = status_code
            resource.link_health_score = 1.0
            resource.link_flagged_reason = None
            stats["healthy"] += 1
        elif status_code and status_code >= 400:
            # HTTP error
            resource.link_http_status = status_code
            resource.link_health_score = 0.0
            resource.link_flagged_reason = f"HTTP {status_code}"
            resource.status = ResourceStatus.NEEDS_REVIEW
            stats["broken"] += 1
        elif error:
            # Connection error
            resource.link_health_score = 0.0
            resource.link_flagged_reason = error
            resource.status = ResourceStatus.NEEDS_REVIEW
            stats["broken"] += 1

        session.add(resource)

    session.commit()
    return stats


async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting parallel link checker...")
    print(f"Concurrency: {MAX_CONCURRENT} simultaneous requests")

    # Get all resources with URLs that need checking
    with Session(engine) as session:
        stmt = (
            select(Resource.id, Resource.website)
            .where(Resource.website.isnot(None))
            .where(Resource.status == ResourceStatus.ACTIVE)
            .order_by(Resource.link_checked_at.asc().nullsfirst())
        )
        resources = [(r.id, r.website) for r in session.exec(stmt).all()]

    total = len(resources)
    print(f"Found {total} resources with URLs to check")

    if total == 0:
        print("No resources to check!")
        return

    # Process in batches
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    total_healthy = 0
    total_broken = 0
    checked = 0

    for i in range(0, total, BATCH_COMMIT_SIZE):
        batch = resources[i : i + BATCH_COMMIT_SIZE]

        # Check URLs
        results = await check_batch(batch, semaphore)

        # Update database
        with Session(engine) as session:
            stats = update_resources(session, results)
            total_healthy += stats["healthy"]
            total_broken += stats["broken"]

        checked += len(batch)
        pct = (checked / total) * 100
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] Progress: {checked}/{total} ({pct:.1f}%) - Healthy: {total_healthy}, Broken: {total_broken}")

    print("\n=== COMPLETE ===")
    print(f"Total checked: {checked}")
    print(f"Healthy: {total_healthy} ({total_healthy / checked * 100:.1f}%)")
    print(f"Broken: {total_broken} ({total_broken / checked * 100:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
