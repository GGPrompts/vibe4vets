#!/usr/bin/env python3
"""
Enrich food resources from markdown collection with full contact details.

This script:
1. Parses the markdown collection file
2. Identifies resources not yet enriched
3. Outputs a list of resources needing enrichment for batch processing
"""

import json
import re
from pathlib import Path


def parse_markdown_resources(md_path: str) -> list[dict]:
    """Parse resources from markdown format."""
    with open(md_path) as f:
        content = f.read()

    # Pattern: "1. Name, City, Phone" or "  1. Name, City, Phone"
    pattern = r'^\s*\d+\.\s*([^,]+),\s*([^,]+),\s*(.+?)$'
    matches = re.findall(pattern, content, re.MULTILINE)

    resources = []
    for name, city, phone in matches:
        phone = phone.strip()
        # Normalize phone values
        if phone in ['null', 'N/A', '(none)', 'Contact via website', 'Contact through website']:
            phone = None
        resources.append({
            'name': name.strip(),
            'city': city.strip(),
            'phone': phone
        })

    return resources


def load_existing_resources(json_path: str) -> list[dict]:
    """Load existing enriched resources."""
    with open(json_path) as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    """Normalize resource name for comparison."""
    return name.lower().replace(' - ', ' ').replace('-', ' ').replace('  ', ' ').strip()


def find_missing_resources(md_resources: list[dict], existing_resources: list[dict]) -> list[dict]:
    """Find resources in markdown not yet enriched."""
    existing_normalized = {normalize_name(r['name']) for r in existing_resources}

    missing = []
    for res in md_resources:
        normalized = normalize_name(res['name'])
        # Check for fuzzy match
        found = False
        for existing in existing_normalized:
            if normalized in existing or existing in normalized:
                found = True
                break
        if not found:
            missing.append(res)

    return missing


def group_by_region(resources: list[dict]) -> dict[str, list[dict]]:
    """Group resources by region based on city/state patterns."""
    regions = {
        'northeast': [],
        'southeast': [],
        'west': []
    }

    # City to region mapping
    northeast_cities = {
        'worcester', 'revere', 'boston', 'gardner', 'devens', 'providence', 'johnston',
        'newark', 'lyons', 'east orange', 'west haven', 'hartford', 'cleveland',
        'chardon', 'columbus', 'grove city', 'detroit', 'tonawanda', 'buffalo',
        'cheektowaga', 'chicago', 'hines'
    }
    southeast_cities = {
        'miami', 'fort lauderdale', 'tampa', 'orlando', 'decatur', 'atlanta',
        'fairburn', 'charlotte', 'salisbury', 'houston', 'dallas', 'san antonio',
        'austin', 'nashville', 'antioch', 'memphis', 'new orleans', 'jacksonville',
        'atlantic beach'
    }
    # West cities: everything else

    for res in resources:
        city_lower = res['city'].lower()
        if any(c in city_lower for c in northeast_cities):
            regions['northeast'].append(res)
        elif any(c in city_lower for c in southeast_cities):
            regions['southeast'].append(res)
        else:
            regions['west'].append(res)

    return regions


def main():
    base_dir = Path(__file__).parent.parent / 'data' / 'food'
    md_path = base_dir / 'all-regions-collected.md'
    json_path = base_dir / 'food-national.json'

    print("Loading data...")
    md_resources = parse_markdown_resources(str(md_path))
    existing = load_existing_resources(str(json_path))

    print(f"Found {len(md_resources)} resources in markdown")
    print(f"Found {len(existing)} existing enriched resources")

    missing = find_missing_resources(md_resources, existing)
    print(f"Found {len(missing)} resources needing enrichment")

    regions = group_by_region(missing)
    print("\nBy region:")
    for region, res_list in regions.items():
        print(f"  {region}: {len(res_list)}")

    # Output missing resources for batch processing
    output_path = base_dir / 'resources-to-enrich.json'
    with open(output_path, 'w') as f:
        json.dump({
            'total': len(missing),
            'by_region': {
                region: [{'name': r['name'], 'city': r['city'], 'phone': r['phone']}
                        for r in res_list]
                for region, res_list in regions.items()
            }
        }, f, indent=2)

    print(f"\nWrote {output_path}")

    # Print resources for manual review
    print("\n" + "="*60)
    print("RESOURCES NEEDING ENRICHMENT")
    print("="*60)
    for region, res_list in regions.items():
        print(f"\n## {region.upper()} ({len(res_list)} resources)")
        for i, r in enumerate(res_list, 1):
            phone = r['phone'] or 'No phone'
            print(f"  {i}. {r['name']} | {r['city']} | {phone}")


if __name__ == '__main__':
    main()
