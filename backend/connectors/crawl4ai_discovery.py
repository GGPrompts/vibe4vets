"""Crawl4AI-powered resource discovery connector.

Uses Crawl4AI to crawl websites. Extraction is done externally via parallel
haiku subagents in Claude Code sessions (10-20x faster and cheaper than CLI).

Workflow:
1. crawl_urls() fetches pages → {url: markdown} dict
2. Claude Code launches parallel haiku subagents for extraction
3. parse_extracted() converts JSON → ResourceCandidate objects
4. ETL pipeline loads to database
"""

import asyncio
from datetime import UTC, datetime

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Check if crawl4ai is available
try:
    import crawl4ai  # noqa: F401

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


# Extraction prompt template for haiku subagents
EXTRACTION_PROMPT = """Extract veteran resources from this webpage content.

Return a JSON array of resources. For each resource found, include:
- name: Resource/program name
- description: What the resource provides (1-2 sentences)
- url: Direct link to the resource (if available)
- phone: Contact phone number (if available)
- address: Physical address (if available)
- city: City (if available)
- state: State abbreviation (if available)
- zip_code: ZIP code (if available)
- categories: Array from: employment, training, housing, legal, food, benefits,
  mentalHealth, supportServices, healthcare, education, financial, family
- eligibility: Who can access this resource (if mentioned)
- org_name: Organization providing the resource

Only include actual veteran resources/services, not:
- Navigation links
- Footer content
- Cookie notices
- Promotional content

If no veteran resources are found, return an empty array: []

Webpage content:
{content}
"""


def get_extraction_prompt(content: str) -> str:
    """Get the extraction prompt with content inserted.

    Use this to build prompts for haiku subagents.
    """
    return EXTRACTION_PROMPT.format(content=content)


class Crawl4AIDiscoveryConnector(BaseConnector):
    """Discover veteran resources using Crawl4AI + parallel haiku subagents.

    This connector crawls specified URLs using Crawl4AI (handles JS rendering,
    bot detection avoidance). Extraction is done via parallel haiku subagents
    in Claude Code sessions - 10-20x faster and cheaper than CLI.

    Usage (in Claude Code session):
        # Step 1: Crawl URLs
        connector = Crawl4AIDiscoveryConnector(
            urls=["https://state-va.gov/resources"],
            source_name="State VA Discovery",
            tier=3,
        )
        crawled = connector.crawl_urls()  # Returns {url: markdown}

        # Step 2: Launch parallel haiku subagents for extraction
        # (Done in Claude Code using Task tool with model="haiku")

        # Step 3: Parse extracted JSON to ResourceCandidates
        resources = connector.parse_extracted(extracted_json, url)
    """

    def __init__(
        self,
        urls: list[str],
        source_name: str = "Crawl4AI Discovery",
        source_url: str = "https://crawl4ai.com",
        tier: int = 4,
        frequency: str = "weekly",
        max_content_length: int = 30000,
    ):
        """Initialize the connector.

        Args:
            urls: List of URLs to crawl and extract resources from.
            source_name: Name for this data source.
            source_url: Base URL for the source.
            tier: Trust tier (1-4, default 4 for discovered content).
            frequency: How often to run (daily, weekly, monthly).
            max_content_length: Max chars per page (truncates if longer).
        """
        if not CRAWL4AI_AVAILABLE:
            raise ImportError(
                "crawl4ai not installed. Run: uv pip install crawl4ai && python -m playwright install firefox"
            )

        self.urls = urls
        self.source_name = source_name
        self.source_url = source_url
        self.tier = tier
        self.frequency = frequency
        self.max_content_length = max_content_length

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name=self.source_name,
            url=self.source_url,
            tier=self.tier,
            frequency=self.frequency,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Legacy method - use crawl_urls() + haiku subagents instead.

        This method is kept for interface compatibility but should not be used.
        The new workflow is:
        1. crawl_urls() to get markdown
        2. Parallel haiku subagents for extraction (in Claude Code)
        3. parse_extracted() to convert to ResourceCandidates
        """
        raise NotImplementedError(
            "Use crawl_urls() + parallel haiku subagents instead. "
            "See /run-jobs crawl4ai_discovery for the new workflow."
        )

    def crawl_urls(self) -> dict[str, str]:
        """Crawl all URLs and return markdown content.

        Returns:
            Dict mapping URL to markdown content.
        """
        return asyncio.run(self._crawl_urls_async())

    async def _crawl_urls_async(self) -> dict[str, str]:
        """Async implementation of URL crawling."""
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

        results: dict[str, str] = {}

        browser_config = BrowserConfig(
            headless=True,
            browser_type="firefox",  # Firefox works better in WSL2
        )

        run_config = CrawlerRunConfig(
            wait_until="networkidle",
            word_count_threshold=50,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for url in self.urls:
                try:
                    print(f"Crawling: {url}")
                    result = await crawler.arun(url=url, config=run_config)

                    if result.success:
                        markdown = result.markdown
                        # Truncate if too long
                        if len(markdown) > self.max_content_length:
                            markdown = markdown[: self.max_content_length]
                            print(f"  Got {len(markdown):,} chars (truncated)")
                        else:
                            print(f"  Got {len(markdown):,} chars")
                        results[url] = markdown
                    else:
                        print(f"  Failed: {result.error_message}")
                except Exception as e:
                    print(f"  Error: {e}")
                    continue

        return results

    def parse_extracted(
        self,
        extracted: list[dict],
        source_url: str,
        fetched_at: datetime | None = None,
    ) -> list[ResourceCandidate]:
        """Convert extracted JSON from haiku to ResourceCandidates.

        Args:
            extracted: List of resource dicts from haiku extraction.
            source_url: URL where resources were found.
            fetched_at: Timestamp of extraction (defaults to now).

        Returns:
            List of ResourceCandidate objects.
        """
        if fetched_at is None:
            fetched_at = datetime.now(UTC)

        resources = []
        for item in extracted:
            candidate = self._to_candidate(item, source_url, fetched_at)
            if candidate:
                resources.append(candidate)
        return resources

    def _to_candidate(
        self,
        item: dict,
        source_url: str,
        fetched_at: datetime,
    ) -> ResourceCandidate | None:
        """Convert extracted item to ResourceCandidate.

        Args:
            item: Extracted resource dictionary.
            source_url: URL where resource was found.
            fetched_at: Timestamp of extraction.

        Returns:
            ResourceCandidate or None if invalid.
        """
        name = item.get("name") or item.get("title")
        if not name:
            return None

        description = item.get("description", "")
        if not description:
            description = f"Veteran resource: {name}"

        # Determine scope from state info
        state = item.get("state")
        states = [state] if state else None
        scope = "state" if state else "national"

        # Get or infer org name
        org_name = item.get("org_name") or name

        # Normalize categories
        categories = item.get("categories", [])
        if isinstance(categories, str):
            categories = [categories]

        return ResourceCandidate(
            title=name,
            description=description,
            source_url=item.get("url") or source_url,
            org_name=org_name,
            org_website=item.get("url"),
            address=item.get("address"),
            city=item.get("city"),
            state=state,
            zip_code=item.get("zip_code"),
            categories=categories if categories else ["supportServices"],
            tags=["crawl4ai-discovered"],
            phone=self._normalize_phone(item.get("phone")),
            email=item.get("email"),
            eligibility=item.get("eligibility"),
            scope=scope,
            states=states,
            raw_data=item,
            fetched_at=fetched_at,
        )


# Convenience function for one-off crawls
def crawl_url(url: str) -> str | None:
    """Crawl a single URL and return markdown.

    Convenience function for testing.

    Args:
        url: URL to crawl.

    Returns:
        Markdown content or None if failed.
    """
    connector = Crawl4AIDiscoveryConnector(urls=[url])
    results = connector.crawl_urls()
    return results.get(url)


def crawl_urls(urls: list[str], max_content_length: int = 30000) -> dict[str, str]:
    """Crawl multiple URLs and return markdown.

    Convenience function for batch crawling.

    Args:
        urls: List of URLs to crawl.
        max_content_length: Max chars per page.

    Returns:
        Dict mapping URL to markdown content.
    """
    connector = Crawl4AIDiscoveryConnector(
        urls=urls,
        max_content_length=max_content_length,
    )
    return connector.crawl_urls()
