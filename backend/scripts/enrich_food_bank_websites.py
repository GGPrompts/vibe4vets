#!/usr/bin/env python3
"""Enrich Feeding America food bank resources with official website URLs.

This script matches food bank resources from the database with their
official websites from a curated mapping file.

Usage:
    python scripts/enrich_food_bank_websites.py          # Generate enrichment file
    python scripts/enrich_food_bank_websites.py --verify # Verify URLs are accessible
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_food_bank_mapping() -> dict:
    """Load the curated food bank to website mapping."""
    mapping_path = Path(__file__).parent.parent / "data" / "feeding_america_websites.json"
    with open(mapping_path) as f:
        data = json.load(f)
    return data["food_banks"]


def load_missing_resources() -> list[dict]:
    """Load the resources that are missing websites."""
    data_path = Path(__file__).parent.parent / "data" / "food_bank_missing_websites.json"
    with open(data_path) as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    """Normalize food bank name for matching."""
    if not name:
        return ""
    # Remove common prefixes/suffixes and normalize
    normalized = name.lower()
    # Remove "the " prefix
    if normalized.startswith("the "):
        normalized = normalized[4:]
    # Remove common suffixes
    for suffix in [", inc", ", inc.", " inc", " inc."]:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    return normalized


def find_best_match(org_name: str, mapping: dict) -> tuple[str | None, str]:
    """Find the best matching website for an organization name.

    Returns (url, confidence) where confidence is HIGH, MEDIUM, or LOW.
    """
    if not org_name:
        return None, "NOT_FOUND"

    normalized_org = normalize_name(org_name)

    # Try exact match first
    for food_bank, url in mapping.items():
        if normalize_name(food_bank) == normalized_org:
            return url, "HIGH"

    # Try contains match
    for food_bank, url in mapping.items():
        normalized_fb = normalize_name(food_bank)
        if normalized_fb in normalized_org or normalized_org in normalized_fb:
            return url, "MEDIUM"

    # Try word overlap match
    org_words = set(normalized_org.split())
    best_match = None
    best_overlap = 0

    for food_bank, url in mapping.items():
        fb_words = set(normalize_name(food_bank).split())
        # Remove common words
        common_words = {"food", "bank", "of", "the", "area", "regional", "community"}
        org_significant = org_words - common_words
        fb_significant = fb_words - common_words

        overlap = len(org_significant & fb_significant)
        if overlap > best_overlap and overlap >= 2:
            best_overlap = overlap
            best_match = url

    if best_match:
        return best_match, "LOW"

    return None, "NOT_FOUND"


def main():
    verify = "--verify" in sys.argv

    # Load data
    mapping = load_food_bank_mapping()
    resources = load_missing_resources()

    print(f"{'=' * 60}")
    print("Food Bank Website Enrichment")
    print(f"{'=' * 60}\n")

    print(f"Food banks in mapping: {len(mapping)}")
    print(f"Resources to enrich: {len(resources)}")
    print()

    # Match resources to websites
    enrichment_results = []
    stats = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NOT_FOUND": 0}

    for resource in resources:
        org_name = resource.get("org_name", "")
        url, confidence = find_best_match(org_name, mapping)

        result = {
            "id": resource["id"],
            "title": resource["title"],
            "org_name": org_name,
            "url": url,
            "confidence": confidence,
        }
        enrichment_results.append(result)
        stats[confidence] += 1

        # Print progress for non-matches
        if confidence == "NOT_FOUND":
            print(f"  NOT FOUND: {org_name}")

    # Save results
    output_path = Path(__file__).parent.parent / "data" / "food_bank_website_enrichment.json"
    with open(output_path, "w") as f:
        json.dump(enrichment_results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  HIGH confidence:   {stats['HIGH']}")
    print(f"  MEDIUM confidence: {stats['MEDIUM']}")
    print(f"  LOW confidence:    {stats['LOW']}")
    print(f"  NOT FOUND:         {stats['NOT_FOUND']}")
    print()

    total_found = stats["HIGH"] + stats["MEDIUM"] + stats["LOW"]
    total = len(resources)
    success_rate = (total_found / total * 100) if total > 0 else 0
    print(f"Total found: {total_found}/{total} ({success_rate:.1f}%)")

    if verify:
        print("\nVerifying URLs (this may take a while)...")
        import urllib.request
        import urllib.error

        verified = 0
        failed = []
        for result in enrichment_results:
            if result["url"]:
                try:
                    req = urllib.request.Request(
                        result["url"],
                        headers={"User-Agent": "Mozilla/5.0 (compatible; VetRD/1.0)"},
                    )
                    urllib.request.urlopen(req, timeout=10)
                    verified += 1
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    failed.append((result["org_name"], result["url"], str(e)))

        print(f"\nVerified: {verified}/{total_found}")
        if failed:
            print(f"Failed ({len(failed)}):")
            for org, url, err in failed[:10]:
                print(f"  {org}: {url} - {err}")


if __name__ == "__main__":
    main()
