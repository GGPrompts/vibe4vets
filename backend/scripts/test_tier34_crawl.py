#!/usr/bin/env python3
"""Test Crawl4AI on Tier 3-4 sources.

Tests crawling quality on:
- State VA agency pages (Tier 3)
- 211 directories (Tier 4)
- Community food banks
- Local veteran organizations

Run: python scripts/test_tier34_crawl.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Tier 3-4 test URLs - mix of static and JS-heavy sites
TEST_SOURCES = {
    # Tier 3: State VA agencies
    "California VA": "https://www.calvet.ca.gov/VetServices",
    "Texas VA": "https://www.tvc.texas.gov/grants/",
    "Florida VA": "https://floridavets.org/benefits-services/",
    # Tier 4: Community directories
    "211 LA": "https://211la.org/resources/category/veterans-services",
    "United Way": "https://www.unitedway.org/our-impact/featured-programs/211",
    # Nonprofit veteran orgs
    "Team Rubicon": "https://teamrubiconusa.org/programs/",
    "The Mission Continues": "https://missioncontinues.org/programs/",
    # Food resources
    "Feeding America": "https://www.feedingamerica.org/find-your-local-foodbank",
}


async def test_source(
    crawler: "AsyncWebCrawler",
    name: str,
    url: str,
    config: "CrawlerRunConfig",
) -> dict:
    """Test crawling a single source."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print("=" * 60)

    try:
        result = await crawler.arun(url=url, config=config)

        if result.success:
            # Analyze content quality
            markdown = result.markdown
            word_count = len(markdown.split())
            has_phone = any(
                pattern in markdown
                for pattern in ["(", ")", "-", "tel:", "phone", "call"]
            )
            has_address = any(
                pattern in markdown.lower()
                for pattern in ["street", "ave", "blvd", "suite", "address"]
            )
            has_lists = markdown.count("* ") + markdown.count("- ")

            print(f"✓ Success in {result.response_headers.get('x-crawl4ai-time', 'N/A')}")
            print(f"  Words: {word_count:,}")
            print(f"  Has phone patterns: {has_phone}")
            print(f"  Has address patterns: {has_address}")
            print(f"  List items: {has_lists}")
            print(f"\n  Preview (first 500 chars):")
            print(f"  {markdown[:500]}...")

            return {
                "name": name,
                "url": url,
                "success": True,
                "word_count": word_count,
                "markdown_length": len(markdown),
                "has_phone": has_phone,
                "has_address": has_address,
                "list_items": has_lists,
            }
        else:
            print(f"✗ Failed: {result.error_message}")
            return {
                "name": name,
                "url": url,
                "success": False,
                "error": result.error_message,
            }
    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            "name": name,
            "url": url,
            "success": False,
            "error": str(e),
        }


async def main():
    print("Testing Crawl4AI on Tier 3-4 Sources")
    print("=" * 60)

    browser_config = BrowserConfig(
        headless=True,
        browser_type="firefox",
    )

    run_config = CrawlerRunConfig(
        wait_until="networkidle",
        word_count_threshold=50,
    )

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for name, url in TEST_SOURCES.items():
            result = await test_source(crawler, name, url, run_config)
            results.append(result)
            # Be nice to servers
            await asyncio.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"  ✓ {r['name']}: {r['word_count']:,} words, {r['list_items']} lists")

    if failed:
        print(f"\nFailed: {len(failed)}/{len(results)}")
        for r in failed:
            print(f"  ✗ {r['name']}: {r.get('error', 'Unknown')[:50]}")

    # Quality metrics
    if successful:
        avg_words = sum(r["word_count"] for r in successful) / len(successful)
        with_phone = sum(1 for r in successful if r.get("has_phone"))
        with_address = sum(1 for r in successful if r.get("has_address"))

        print(f"\nContent Quality:")
        print(f"  Avg words per page: {avg_words:,.0f}")
        print(f"  Pages with phone patterns: {with_phone}/{len(successful)}")
        print(f"  Pages with address patterns: {with_address}/{len(successful)}")


if __name__ == "__main__":
    asyncio.run(main())
