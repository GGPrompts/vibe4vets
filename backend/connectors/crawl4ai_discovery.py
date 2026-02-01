"""Crawl4AI-powered resource discovery connector.

Uses Crawl4AI to crawl websites and Claude CLI (Max subscription) to extract
structured resource data. No API fees - uses flat-rate CLI subscription.

Workflow:
1. Crawl4AI fetches page → clean markdown (free)
2. Claude CLI extracts resources → JSON (Max subscription flat fee)
3. Parse JSON → ResourceCandidate objects
"""

import asyncio
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Try to import crawl4ai - graceful fallback if not installed
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


# Default extraction prompt for Claude CLI
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


class Crawl4AIDiscoveryConnector(BaseConnector):
    """Discover veteran resources using Crawl4AI + Claude CLI.

    This connector crawls specified URLs using Crawl4AI (handles JS rendering,
    bot detection avoidance) and uses Claude CLI for extraction (uses Max
    subscription flat fee instead of per-API-call pricing).

    Usage:
        connector = Crawl4AIDiscoveryConnector(
            urls=["https://state-va.gov/resources"],
            source_name="State VA Discovery",
            tier=3,
        )
        resources = connector.run()
    """

    def __init__(
        self,
        urls: list[str],
        source_name: str = "Crawl4AI Discovery",
        source_url: str = "https://crawl4ai.com",
        tier: int = 4,
        frequency: str = "weekly",
        max_content_length: int = 50000,
        cli_timeout: int = 120,
    ):
        """Initialize the connector.

        Args:
            urls: List of URLs to crawl and extract resources from.
            source_name: Name for this data source.
            source_url: Base URL for the source.
            tier: Trust tier (1-4, default 4 for discovered content).
            frequency: How often to run (daily, weekly, monthly).
            max_content_length: Max chars to send to CLI (truncates if longer).
            cli_timeout: Timeout in seconds for Claude CLI calls.
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
        self.cli_timeout = cli_timeout

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
        """Crawl URLs and extract resources.

        Returns:
            List of ResourceCandidate objects from all crawled pages.
        """
        return asyncio.run(self._run_async())

    async def _run_async(self) -> list[ResourceCandidate]:
        """Async implementation of crawl and extract."""
        all_resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

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
                    resources = await self._crawl_and_extract(crawler, url, run_config, now)
                    all_resources.extend(resources)
                except Exception as e:
                    print(f"Error crawling {url}: {e}")
                    continue

        return all_resources

    async def _crawl_and_extract(
        self,
        crawler: "AsyncWebCrawler",
        url: str,
        config: "CrawlerRunConfig",
        fetched_at: datetime,
    ) -> list[ResourceCandidate]:
        """Crawl a single URL and extract resources.

        Args:
            crawler: The AsyncWebCrawler instance.
            url: URL to crawl.
            config: Crawler run configuration.
            fetched_at: Timestamp for the fetch.

        Returns:
            List of ResourceCandidate objects from this page.
        """
        print(f"Crawling: {url}")

        result = await crawler.arun(url=url, config=config)

        if not result.success:
            print(f"  Failed: {result.error_message}")
            return []

        markdown = result.markdown
        print(f"  Got {len(markdown):,} chars of markdown")

        # Truncate if too long
        if len(markdown) > self.max_content_length:
            markdown = markdown[: self.max_content_length]
            print(f"  Truncated to {self.max_content_length:,} chars")

        # Extract using Claude CLI
        extracted = self._extract_with_cli(markdown, url)

        if not extracted:
            print("  No resources extracted")
            return []

        print(f"  Extracted {len(extracted)} resources")

        # Convert to ResourceCandidate objects
        resources = []
        for item in extracted:
            candidate = self._to_candidate(item, url, fetched_at)
            if candidate:
                resources.append(candidate)

        return resources

    def _extract_with_cli(self, markdown: str, source_url: str) -> list[dict]:
        """Use Claude CLI to extract resources from markdown.

        Args:
            markdown: The crawled page content as markdown.
            source_url: URL of the crawled page (for context).

        Returns:
            List of extracted resource dictionaries.
        """
        prompt = EXTRACTION_PROMPT.format(content=markdown)

        # Write prompt to temp file (avoids shell escaping issues)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            # Call Claude CLI
            result = subprocess.run(
                [
                    "claude",
                    "-p",
                    f"$(cat {prompt_file})",
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=self.cli_timeout,
                shell=True,  # Need shell for $() expansion
            )

            if result.returncode != 0:
                # Try alternative: pipe content directly
                result = subprocess.run(
                    ["claude", "-p", prompt, "--output-format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=self.cli_timeout,
                )

            if result.returncode != 0:
                print(f"  CLI error: {result.stderr[:200]}")
                return []

            # Parse JSON output
            output = result.stdout.strip()
            if not output:
                return []

            # Handle potential markdown code blocks in output
            if output.startswith("```"):
                lines = output.split("\n")
                output = "\n".join(lines[1:-1])

            data = json.loads(output)

            # Handle both direct array and wrapped response
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "resources" in data:
                return data["resources"]
            elif isinstance(data, dict) and "result" in data:
                return data["result"] if isinstance(data["result"], list) else []

            return []

        except subprocess.TimeoutExpired:
            print(f"  CLI timeout after {self.cli_timeout}s")
            return []
        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
            return []
        except Exception as e:
            print(f"  Extraction error: {e}")
            return []
        finally:
            # Clean up temp file
            Path(prompt_file).unlink(missing_ok=True)

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
async def crawl_and_extract(url: str) -> list[dict]:
    """Crawl a single URL and extract resources.

    Convenience function for testing or one-off extractions.

    Args:
        url: URL to crawl.

    Returns:
        List of extracted resource dictionaries.
    """
    connector = Crawl4AIDiscoveryConnector(urls=[url])
    return connector.run()
