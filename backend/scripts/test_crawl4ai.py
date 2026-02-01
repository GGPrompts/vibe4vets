#!/usr/bin/env python3
"""Test Crawl4AI on veteran resource pages."""

import asyncio
import sys
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Test URLs - mix of static and JS-heavy sites
TEST_URLS = [
    # State VA page (often JS-rendered)
    "https://www.dva.wa.gov/veterans/veteran-services",
    # Nonprofit veteran org
    "https://www.dav.org/veterans/find-your-local-office/",
]


async def test_crawl(url: str) -> dict:
    """Crawl a URL and return results."""
    print(f"\n{'='*60}")
    print(f"Crawling: {url}")
    print("=" * 60)

    browser_config = BrowserConfig(
        headless=True,
        browser_type="firefox",  # Firefox works better in WSL2
    )

    run_config = CrawlerRunConfig(
        # Wait for content to load
        wait_until="networkidle",
        # Don't use LLM extraction (we'll use CLI instead)
        word_count_threshold=50,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if result.success:
            print(f"\n✓ Success!")
            print(f"  Title: {result.metadata.get('title', 'N/A')[:60]}")
            print(f"  Markdown length: {len(result.markdown):,} chars")
            print(f"  Links found: {len(result.links.get('internal', [])) + len(result.links.get('external', []))}")

            # Show first 2000 chars of markdown
            print(f"\n--- Markdown Preview (first 2000 chars) ---\n")
            print(result.markdown[:2000])
            print("\n--- End Preview ---")

            return {
                "url": url,
                "success": True,
                "title": result.metadata.get("title"),
                "markdown_length": len(result.markdown),
                "markdown": result.markdown,
            }
        else:
            print(f"\n✗ Failed: {result.error_message}")
            return {"url": url, "success": False, "error": result.error_message}


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else TEST_URLS[0]
    result = await test_crawl(url)

    if result["success"]:
        # Save full markdown to file for inspection
        output_file = "/tmp/crawl4ai_test.md"
        with open(output_file, "w") as f:
            f.write(f"# Crawled: {result['url']}\n\n")
            f.write(result["markdown"])
        print(f"\n📄 Full markdown saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
