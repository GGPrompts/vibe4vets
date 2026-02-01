#!/usr/bin/env python3
"""Recheck HTTP 403 URLs with proper User-Agent header."""

import asyncio
import sys
from datetime import datetime

import httpx
from sqlmodel import Session, select

sys.path.insert(0, "/home/marci/projects/vibe4vets/backend")

from app.database import engine
from app.models.resource import Resource, ResourceStatus

# Browser-like User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

MAX_CONCURRENT = 30
TIMEOUT = 20.0


async def check_url(client: httpx.AsyncClient, url: str) -> dict:
    """Check a single URL with browser headers."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        response = await client.get(url, follow_redirects=True)
        return {"status_code": response.status_code}
    except Exception as e:
        return {"status_code": None, "error": str(e)[:50]}


async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Rechecking HTTP 403 URLs with browser User-Agent...")

    # Get 403 resources
    with Session(engine) as session:
        stmt = select(Resource.id, Resource.website).where(Resource.link_flagged_reason == "HTTP 403")
        resources = [(r.id, r.website) for r in session.exec(stmt).all()]

    total = len(resources)
    print(f"Found {total} resources with HTTP 403 to recheck")

    if total == 0:
        return

    # Setup client with browser headers
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    fixed = 0
    still_broken = 0

    async with httpx.AsyncClient(timeout=TIMEOUT, headers=headers) as client:

        async def check_with_semaphore(rid, url):
            async with semaphore:
                return (rid, await check_url(client, url))

        # Process in batches
        batch_size = 500
        for i in range(0, total, batch_size):
            batch = resources[i : i + batch_size]
            tasks = [check_with_semaphore(rid, url) for rid, url in batch]
            results = await asyncio.gather(*tasks)

            # Update database
            with Session(engine) as session:
                for resource_id, result in results:
                    resource = session.get(Resource, resource_id)
                    if not resource:
                        continue

                    status_code = result.get("status_code")

                    if status_code and status_code < 400:
                        # Now healthy!
                        resource.link_http_status = status_code
                        resource.link_health_score = 1.0
                        resource.link_flagged_reason = None
                        resource.status = ResourceStatus.ACTIVE
                        fixed += 1
                    else:
                        # Still broken
                        still_broken += 1

                    session.add(resource)

                session.commit()

            pct = ((i + len(batch)) / total) * 100
            ts = datetime.now().strftime("%H:%M:%S")
            done = i + len(batch)
            print(f"[{ts}] Progress: {done}/{total} ({pct:.1f}%) - Fixed: {fixed}, Still broken: {still_broken}")

    print("\n=== COMPLETE ===")
    print(f"Fixed (now healthy): {fixed}")
    print(f"Still broken: {still_broken}")


if __name__ == "__main__":
    asyncio.run(main())
