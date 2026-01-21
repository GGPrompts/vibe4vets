#!/usr/bin/env python3
"""
Merge newly enriched food resources with existing food-national.json.

This script:
1. Loads existing food-national.json
2. Loads new enriched JSON files (northeast-new.json, southeast-new.json, west-new.json)
3. Deduplicates by name
4. Validates JSON schema
5. Outputs merged food-national.json
"""

import json
from pathlib import Path


def normalize_name(name: str) -> str:
    """Normalize resource name for deduplication."""
    return name.lower().replace(' - ', ' ').replace('-', ' ').replace('  ', ' ').strip()


def load_json_safe(path: Path) -> list[dict]:
    """Load JSON file, return empty list if missing or invalid."""
    if not path.exists():
        print(f"  Warning: {path.name} not found")
        return []
    try:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            print(f"  Warning: {path.name} is not a list")
            return []
    except json.JSONDecodeError as e:
        print(f"  Error: {path.name} has invalid JSON: {e}")
        return []


def validate_resource(resource: dict) -> tuple[bool, list[str]]:
    """Validate resource has required fields."""
    errors = []
    required = ['name', 'city', 'state', 'category']
    for field in required:
        if not resource.get(field):
            errors.append(f"Missing {field}")

    # Check phone or website exists
    if not resource.get('phone') and not resource.get('website'):
        errors.append("Missing both phone and website")

    return len(errors) == 0, errors


def merge_resources(existing: list[dict], *new_lists: list[dict]) -> list[dict]:
    """Merge resource lists, deduplicating by normalized name."""
    seen = {}

    # Add existing first (they take precedence)
    for resource in existing:
        name = normalize_name(resource.get('name', ''))
        if name:
            seen[name] = resource

    # Add new resources (only if not already present)
    for new_list in new_lists:
        for resource in new_list:
            name = normalize_name(resource.get('name', ''))
            if name and name not in seen:
                seen[name] = resource

    return list(seen.values())


def compute_stats(resources: list[dict]) -> dict:
    """Compute statistics about the resources."""
    stats = {
        'total': len(resources),
        'with_website': 0,
        'with_phone': 0,
        'with_schedule': 0,
        'with_source_url': 0,
        'by_state': {},
        'by_subcategory': {},
        'valid': 0,
        'invalid': 0,
    }

    for r in resources:
        if r.get('website'):
            stats['with_website'] += 1
        if r.get('phone'):
            stats['with_phone'] += 1
        if r.get('food_details', {}).get('distribution_schedule'):
            stats['with_schedule'] += 1
        if r.get('source_url'):
            stats['with_source_url'] += 1

        state = r.get('state', 'Unknown')
        stats['by_state'][state] = stats['by_state'].get(state, 0) + 1

        subcat = r.get('subcategory', 'unknown')
        stats['by_subcategory'][subcat] = stats['by_subcategory'].get(subcat, 0) + 1

        valid, _ = validate_resource(r)
        if valid:
            stats['valid'] += 1
        else:
            stats['invalid'] += 1

    return stats


def main():
    base_dir = Path(__file__).parent.parent / 'data' / 'food'

    print("Loading existing food-national.json...")
    existing = load_json_safe(base_dir / 'food-national.json')
    print(f"  Loaded {len(existing)} existing resources")

    print("\nLoading new enriched files...")
    northeast = load_json_safe(base_dir / 'northeast-new.json')
    print(f"  Northeast: {len(northeast)} resources")
    southeast = load_json_safe(base_dir / 'southeast-new.json')
    print(f"  Southeast: {len(southeast)} resources")
    west = load_json_safe(base_dir / 'west-new.json')
    print(f"  West: {len(west)} resources")

    print("\nMerging resources...")
    merged = merge_resources(existing, northeast, southeast, west)
    print(f"  Total after merge: {len(merged)} resources")

    print("\nComputing statistics...")
    stats = compute_stats(merged)

    print(f"\n{'='*50}")
    print("MERGE STATISTICS")
    print(f"{'='*50}")
    print(f"Total resources: {stats['total']}")
    print(f"Valid resources: {stats['valid']}")
    print(f"Invalid resources: {stats['invalid']}")
    print(f"\nWith website: {stats['with_website']} ({100*stats['with_website']/stats['total']:.1f}%)")
    print(f"With phone: {stats['with_phone']} ({100*stats['with_phone']/stats['total']:.1f}%)")
    print(f"With schedule: {stats['with_schedule']} ({100*stats['with_schedule']/stats['total']:.1f}%)")
    print(f"With source_url: {stats['with_source_url']} ({100*stats['with_source_url']/stats['total']:.1f}%)")

    print(f"\nBy state:")
    for state, count in sorted(stats['by_state'].items(), key=lambda x: -x[1]):
        print(f"  {state}: {count}")

    print(f"\nBy subcategory:")
    for subcat, count in sorted(stats['by_subcategory'].items(), key=lambda x: -x[1]):
        print(f"  {subcat}: {count}")

    # Write merged output
    output_path = base_dir / 'food-national.json'
    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)
    print(f"\nWrote {len(merged)} resources to {output_path}")

    # Check acceptance criteria
    print(f"\n{'='*50}")
    print("ACCEPTANCE CRITERIA CHECK")
    print(f"{'='*50}")

    has_contact = stats['with_website'] + stats['with_phone'] - sum(1 for r in merged if r.get('website') and r.get('phone'))
    contact_pct = 100 * has_contact / stats['total']
    schedule_pct = 100 * stats['with_schedule'] / stats['total']
    source_pct = 100 * stats['with_source_url'] / stats['total']

    criteria = [
        (f"80%+ have website or phone: {contact_pct:.1f}%", contact_pct >= 80),
        (f"60%+ have distribution_schedule: {schedule_pct:.1f}%", schedule_pct >= 60),
        (f"All have source_url: {source_pct:.1f}%", source_pct >= 95),
        (f"Valid JSON: {stats['valid']} valid, {stats['invalid']} invalid", stats['invalid'] == 0),
    ]

    all_pass = True
    for desc, passed in criteria:
        status = "✓" if passed else "✗"
        print(f"  {status} {desc}")
        all_pass = all_pass and passed

    return 0 if all_pass else 1


if __name__ == '__main__':
    exit(main())
