#!/usr/bin/env python3
"""Scrape contact information from LSC grantee websites.

Extracts phone numbers and addresses from legal aid organization websites
to enhance the lsc_grantees.yaml data file.

Usage:
    python scripts/scrape_lsc_contacts.py [--limit N] [--dry-run]
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

import httpx
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Common phone number patterns
PHONE_PATTERNS = [
    # Standard formats: (123) 456-7890, 123-456-7890, 123.456.7890
    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    # Toll-free: 1-800-123-4567
    r"1[-.\s]?8[0-9]{2}[-.\s]?\d{3}[-.\s]?\d{4}",
]

# US state abbreviations for address detection
US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "PR",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "VI",
    "WA",
    "WV",
    "WI",
    "WY",
}

# Address pattern: street address, city, state zip
ADDRESS_PATTERN = re.compile(
    r"(\d+\s+[\w\s.,-]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Plaza|Place|Pl|Suite|Ste|Floor|Fl)?[\w\s.,-]*,?\s*"
    r"[\w\s]+,?\s*"
    r"(?:" + "|".join(US_STATES) + r")\s*"
    r"\d{5}(?:-\d{4})?)",
    re.IGNORECASE,
)


def normalize_phone(phone: str) -> str:
    """Normalize phone number to standard format."""
    # Extract digits only
    digits = re.sub(r"\D", "", phone)

    # Remove leading 1 for US numbers
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    return phone  # Return original if can't normalize


def extract_phones(text: str) -> list[str]:
    """Extract phone numbers from text."""
    phones = []
    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            normalized = normalize_phone(match)
            if normalized not in phones:
                phones.append(normalized)
    return phones


def extract_address(text: str) -> str | None:
    """Extract address from text."""
    match = ADDRESS_PATTERN.search(text)
    if match:
        address = match.group(1).strip()
        # Clean up extra whitespace
        address = re.sub(r"\s+", " ", address)
        return address
    return None


def clean_html_text(html: str) -> str:
    """Extract visible text from HTML."""
    # Remove script and style elements
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Decode common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text


async def fetch_page(client: httpx.AsyncClient, url: str, retries: int = 2) -> str | None:
    """Fetch a webpage and return its content."""
    for attempt in range(retries + 1):
        try:
            response = await client.get(url, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError:
            if attempt < retries:
                await asyncio.sleep(1)
                continue
            return None
        except Exception:
            if attempt < retries:
                await asyncio.sleep(1)
                continue
            return None
    return None


async def scrape_contact_info(
    client: httpx.AsyncClient,
    grantee: dict,
) -> dict:
    """Scrape contact info from a grantee's website."""
    result = {
        "name": grantee["name"],
        "phone": None,
        "address": None,
        "error": None,
    }

    website = grantee.get("website")
    if not website:
        result["error"] = "No website URL"
        return result

    try:
        # Wrap entire operation in timeout
        async with asyncio.timeout(30):
            # Try main page first
            html = await fetch_page(client, website)
            if not html:
                result["error"] = "Failed to fetch website"
                return result

            text = clean_html_text(html)

            # Extract phone numbers
            phones = extract_phones(text)
            if phones:
                # Prefer toll-free numbers
                toll_free = [p for p in phones if p.startswith("(8") or p.startswith("1-8")]
                result["phone"] = toll_free[0] if toll_free else phones[0]

            # Extract address
            address = extract_address(text)
            if address:
                result["address"] = address

            # If no phone found, try common contact page URLs
            if not result["phone"]:
                contact_paths = ["/contact", "/contact-us"]
                for path in contact_paths:
                    try:
                        contact_url = website.rstrip("/") + path
                        html = await fetch_page(client, contact_url)
                        if html:
                            text = clean_html_text(html)
                            phones = extract_phones(text)
                            if phones:
                                toll_free = [p for p in phones if p.startswith("(8") or p.startswith("1-8")]
                                result["phone"] = toll_free[0] if toll_free else phones[0]
                                break
                    except Exception:
                        continue
    except TimeoutError:
        result["error"] = "Timeout"

    return result


async def scrape_all_grantees(
    grantees: list[dict],
    limit: int | None = None,
) -> list[dict]:
    """Scrape contact info for all grantees."""
    if limit:
        grantees = grantees[:limit]

    results = []

    # Use semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(3)

    async def scrape_with_semaphore(client: httpx.AsyncClient, grantee: dict, idx: int) -> dict:
        async with semaphore:
            result = await scrape_contact_info(client, grantee)
            # Print progress immediately
            status = "✓" if result["phone"] else "✗"
            phone_info = result["phone"] or result["error"] or "No phone found"
            print(f"[{idx}/{len(grantees)}] {status} {result['name']}: {phone_info}", flush=True)
            return result

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [scrape_with_semaphore(client, g, i + 1) for i, g in enumerate(grantees)]
        results = await asyncio.gather(*tasks)

    return list(results)


def update_yaml_with_contacts(
    yaml_path: Path,
    contacts: list[dict],
    dry_run: bool = False,
) -> int:
    """Update YAML file with scraped contact info."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    # Build lookup by name
    contact_map = {c["name"]: c for c in contacts}

    updated_count = 0
    for grantee in data["grantees"]:
        name = grantee["name"]
        if name in contact_map:
            contact = contact_map[name]

            # Update phone if found and not already present
            if contact["phone"] and not grantee.get("phone"):
                grantee["phone"] = contact["phone"]
                updated_count += 1

            # Update address if found and not already present
            if contact["address"] and not grantee.get("address"):
                grantee["address"] = contact["address"]

    if not dry_run and updated_count > 0:
        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return updated_count


def main():
    parser = argparse.ArgumentParser(description="Scrape LSC grantee contact info")
    parser.add_argument("--limit", type=int, help="Limit number of sites to scrape")
    parser.add_argument("--skip", type=int, default=0, help="Skip first N sites")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    parser.add_argument("--output", type=str, help="Output results to JSON file")
    args = parser.parse_args()

    yaml_path = PROJECT_ROOT / "data/reference/lsc_grantees.yaml"

    if not yaml_path.exists():
        print(f"Error: YAML file not found: {yaml_path}")
        sys.exit(1)

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    grantees = data.get("grantees", [])

    # Filter to only those with websites
    grantees_with_websites = [g for g in grantees if g.get("website")]

    # Apply skip
    if args.skip:
        grantees_with_websites = grantees_with_websites[args.skip :]

    print(f"Found {len(grantees)} grantees, {len(grantees_with_websites)} with websites (after skip)")
    print()

    # Run scraper
    results = asyncio.run(scrape_all_grantees(grantees_with_websites, limit=args.limit))

    # Summary
    print()
    phones_found = sum(1 for r in results if r["phone"])
    addresses_found = sum(1 for r in results if r["address"])
    print(f"Results: {phones_found}/{len(results)} phones, {addresses_found}/{len(results)} addresses")

    # Save results to JSON if requested
    if args.output:
        import json

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")

    # Update YAML
    if not args.dry_run:
        updated = update_yaml_with_contacts(yaml_path, results, dry_run=args.dry_run)
        print(f"Updated {updated} entries in {yaml_path}")
    else:
        print("Dry run - no changes written")


if __name__ == "__main__":
    main()
