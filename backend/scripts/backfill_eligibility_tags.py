#!/usr/bin/env python3
"""Backfill eligibility tags on existing resources (V4V-stm9).

Analyzes resource data (title, description, categories, subcategories) and assigns
appropriate eligibility tags from the taxonomy. Runs idempotently - can be run
multiple times safely.

Usage:
    python scripts/backfill_eligibility_tags.py [--dry-run]
"""

import argparse
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select

from app.core.taxonomy import ELIGIBILITY_TAGS, is_valid_eligibility_tag
from app.models import Resource


@dataclass
class TagRule:
    """Rule for inferring a tag from resource data."""

    tag: str
    patterns: list[str]  # Regex patterns to match
    categories: list[str] | None = None  # Only apply if resource has these categories
    subcategories: list[str] | None = None  # Only apply if resource has these subcategories


# Build a flat set of all valid tags for validation
ALL_VALID_TAGS: set[str] = set()
for category_tags in ELIGIBILITY_TAGS.values():
    for group_tags in category_tags.values():
        ALL_VALID_TAGS.update(group_tags)


# Tag inference rules organized by category
# Each rule has: tag to assign, patterns to match, optional category/subcategory filters
TAG_RULES: list[TagRule] = [
    # === HOUSING TAGS ===
    # Voucher programs
    TagRule(
        tag="hud-vash",
        patterns=[r"\bhud[-\s]?vash\b", r"\bvash\b", r"\bhud.+veteran.+supportive\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="ssvf",
        patterns=[r"\bssvf\b", r"\bsupportive\s+services\s+for\s+veteran\s+famil"],
        categories=["housing"],
    ),
    TagRule(
        tag="section-8",
        patterns=[r"\bsection[-\s]?8\b", r"\bhousing\s+choice\s+voucher\b"],
        categories=["housing"],
    ),
    # Housing types
    TagRule(
        tag="emergency-shelter",
        patterns=[r"\bemergency\s+shelter\b", r"\bcrisis\s+shelter\b", r"\bovernight\s+shelter\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="transitional",
        patterns=[r"\btransitional\s+housing\b", r"\btransitional\s+living\b", r"\bgpd\b", r"\bgrant\s+and\s+per\s+diem\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="permanent",
        patterns=[r"\bpermanent\s+supportive\s+housing\b", r"\bpsh\b", r"\bpermanent\s+housing\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="rapid-rehousing",
        patterns=[r"\brapid\s+re[-\s]?housing\b", r"\brrh\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="rental_assistance",
        patterns=[r"\brental?\s+assistance\b", r"\brent\s+relief\b", r"\brent\s+help\b", r"\bemergency\s+rent\b"],
        categories=["housing"],
    ),
    # Housing eligibility
    TagRule(
        tag="families",
        patterns=[r"\bfamil(?:y|ies)\b", r"\bchildren\b", r"\bdependents?\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="veterans-only",
        patterns=[r"\bveterans?\s+only\b", r"\bexclusively\s+(?:for\s+)?veterans?\b"],
        categories=["housing"],
    ),
    TagRule(
        tag="low-income",
        patterns=[r"\blow[-\s]?income\b", r"\bami\b", r"\bbelow\s+\d+%?\s+(?:of\s+)?(?:area\s+)?median"],
        categories=["housing"],
    ),
    # Housing support
    TagRule(
        tag="case-management",
        patterns=[r"\bcase\s+management\b", r"\bcase\s+manager\b", r"\bwraparound\s+services\b"],
    ),
    TagRule(
        tag="substance-abuse",
        patterns=[r"\bsubstance\s+abuse\b", r"\baddiction\b", r"\brecovery\s+support\b", r"\bsober\s+living\b"],
    ),
    # === EMPLOYMENT TAGS ===
    TagRule(
        tag="job-placement",
        patterns=[r"\bjob\s+placement\b", r"\bplacement\s+services?\b", r"\bjob\s+matching\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="resume-help",
        patterns=[r"\bresume\b", r"\bcv\s+(?:help|writing|assistance)\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="interview-prep",
        patterns=[r"\binterview\s+prep\b", r"\binterview\s+training\b", r"\bmock\s+interview\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="career-counseling",
        patterns=[r"\bcareer\s+counsel(?:ing|or)\b", r"\bcareer\s+guidance\b", r"\bcareer\s+coach\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="veteran-friendly",
        patterns=[r"\bveteran[-\s]?friendly\b", r"\bhires?\s+veterans?\b", r"\bveteran\s+hiring\b", r"\bmilitary[-\s]?friendly\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="federal-jobs",
        patterns=[r"\bfederal\s+jobs?\b", r"\bfederal\s+employment\b", r"\busajobs\b", r"\bgovernment\s+jobs?\b"],
        categories=["employment"],
    ),
    TagRule(
        tag="remote",
        patterns=[r"\bremote\s+work\b", r"\bwork\s+from\s+home\b", r"\bremote\s+opportunit"],
        categories=["employment"],
    ),
    TagRule(
        tag="skilled-trades",
        patterns=[r"\bskilled\s+trades?\b", r"\btrade\s+(?:jobs?|work)\b", r"\belectrician\b", r"\bplumber\b", r"\bweld(?:er|ing)\b"],
        categories=["employment"],
    ),
    # === LEGAL TAGS ===
    TagRule(
        tag="discharge-upgrade",
        patterns=[r"\bdischarge\s+upgrade\b", r"\bupgrade\s+(?:your\s+)?discharge\b", r"\bcharacterization\s+(?:of\s+)?(?:service|discharge)\b"],
        categories=["legal"],
    ),
    TagRule(
        tag="va-appeals",
        patterns=[r"\bva\s+appeal\b", r"\bappeal(?:s|ing)?\s+(?:your\s+)?(?:va|claim)\b", r"\bbva\b", r"\bboard\s+of\s+veterans?\s+appeals?\b"],
        categories=["legal"],
    ),
    TagRule(
        tag="free-legal-aid",
        patterns=[r"\bfree\s+legal\b", r"\blegal\s+aid\b", r"\blegal\s+assistance\b", r"\blegal\s+services?\s+corporation\b"],
        categories=["legal"],
    ),
    TagRule(
        tag="pro-bono",
        patterns=[r"\bpro[-\s]?bono\b", r"\bno[-\s]?cost\s+legal\b", r"\bvolunteer\s+(?:attorney|lawyer)\b"],
        categories=["legal"],
    ),
    TagRule(
        tag="claims-help",
        patterns=[r"\bclaims?\s+(?:help|assistance|support)\b", r"\bfile\s+(?:a\s+)?claim\b"],
        categories=["legal", "benefits"],
    ),
    TagRule(
        tag="attorney",
        patterns=[r"\battorney\b", r"\blawyer\b", r"\blegal\s+representation\b"],
        categories=["legal"],
    ),
    TagRule(
        tag="vso-representative",
        patterns=[r"\bvso\b", r"\bveterans?\s+service\s+organi[sz]ation\b", r"\baccredited\s+representative\b"],
        categories=["legal", "benefits"],
    ),
    # === MENTAL HEALTH TAGS ===
    TagRule(
        tag="ptsd-treatment",
        patterns=[r"\bptsd\b", r"\bpost[-\s]?traumatic\s+stress\b", r"\bcombat\s+(?:stress|trauma)\b"],
        categories=["mentalHealth"],
    ),
    TagRule(
        tag="counseling",
        patterns=[r"\bcounseling\b", r"\btherapy\b", r"\btherapist\b", r"\bmental\s+health\s+services?\b"],
        categories=["mentalHealth"],
    ),
    TagRule(
        tag="crisis-services",
        patterns=[r"\bcrisis\s+(?:line|services?|intervention|support)\b", r"\bsuicide\s+prevention\b", r"\b988\b", r"\bveterans?\s+crisis\s+line\b"],
        categories=["mentalHealth"],
    ),
    TagRule(
        tag="peer-support",
        patterns=[r"\bpeer\s+support\b", r"\bpeer\s+mentor\b", r"\bpeer[-\s]?to[-\s]?peer\b", r"\bveteran\s+mentor\b"],
        categories=["mentalHealth", "supportServices"],
    ),
    TagRule(
        tag="telehealth",
        patterns=[r"\btelehealth\b", r"\btelemed(?:icine)?\b", r"\bvirtual\s+(?:care|therapy|counseling|appointment)\b", r"\bonline\s+therapy\b"],
        categories=["mentalHealth", "healthcare"],
    ),
    TagRule(
        tag="group-therapy",
        patterns=[r"\bgroup\s+therap(?:y|ies)\b", r"\bsupport\s+group\b", r"\bgroup\s+counseling\b"],
        categories=["mentalHealth"],
    ),
    TagRule(
        tag="mst",
        patterns=[r"\bmst\b", r"\bmilitary\s+sexual\s+trauma\b"],
        categories=["mentalHealth"],
    ),
    # === TRAINING TAGS ===
    TagRule(
        tag="voc-rehab",
        patterns=[r"\bvoc(?:ational)?\s+rehab\b", r"\bvr&?e\b", r"\bchapter\s+31\b"],
        categories=["training"],
    ),
    TagRule(
        tag="gi-bill-approved",
        patterns=[r"\bgi\s+bill\b", r"\bchapter\s+33\b", r"\bpost[-\s]?9/?11\s+gi\b"],
        categories=["training", "education"],
    ),
    TagRule(
        tag="apprenticeship",
        patterns=[r"\bapprenticeship\b", r"\bon[-\s]?the[-\s]?job\s+training\b", r"\bojt\b"],
        categories=["training"],
    ),
    TagRule(
        tag="certifications",
        patterns=[r"\bcertification\b", r"\bcertified\b", r"\blicense\s+(?:program|training)\b"],
        categories=["training"],
    ),
    TagRule(
        tag="online",
        patterns=[r"\bonline\s+(?:course|training|learning|program)\b", r"\be[-\s]?learning\b", r"\bself[-\s]?paced\b"],
        categories=["training"],
    ),
    TagRule(
        tag="free",
        patterns=[r"\bfree\s+(?:training|course|program|certification)\b", r"\bno[-\s]?cost\s+(?:training|education)\b"],
        categories=["training"],
    ),
    TagRule(
        tag="bootcamp",
        patterns=[r"\bbootcamp\b", r"\bcoding\s+(?:school|program)\b", r"\bintensive\s+program\b"],
        categories=["training"],
    ),
    # === BENEFITS TAGS ===
    TagRule(
        tag="disability-claims",
        patterns=[r"\bdisability\s+claim\b", r"\bservice[-\s]?connected\s+disability\b", r"\bva\s+disability\b"],
        categories=["benefits"],
    ),
    TagRule(
        tag="pension",
        patterns=[r"\bva\s+pension\b", r"\baid\s+(?:and|&)\s+attendance\b", r"\bwartime\s+pension\b"],
        categories=["benefits"],
    ),
    TagRule(
        tag="healthcare-enrollment",
        patterns=[r"\bva\s+healthcare?\s+enrollment\b", r"\benroll\s+in\s+va\s+health\b"],
        categories=["benefits", "healthcare"],
    ),
    TagRule(
        tag="vso",
        patterns=[r"\bvso\b", r"\bveterans?\s+service\s+organi[sz]ation\b"],
        categories=["benefits"],
    ),
    TagRule(
        tag="cvso",
        patterns=[r"\bcvso\b", r"\bcounty\s+veteran\s+service\s+officer\b"],
        categories=["benefits"],
    ),
    # === FOOD TAGS ===
    TagRule(
        tag="food-pantry",
        patterns=[r"\bfood\s+pantr(?:y|ies)\b", r"\bfood\s+bank\b", r"\bgrocery\s+(?:distribution|pickup)\b"],
        categories=["food"],
    ),
    TagRule(
        tag="meal-program",
        patterns=[r"\bmeal\s+program\b", r"\bhot\s+meals?\b", r"\bcommunity\s+(?:meal|kitchen)\b", r"\bsoup\s+kitchen\b"],
        categories=["food"],
    ),
    TagRule(
        tag="mobile-distribution",
        patterns=[r"\bmobile\s+(?:food|pantr)\b", r"\bpop[-\s]?up\s+(?:food|distribution)\b"],
        categories=["food"],
    ),
    TagRule(
        tag="no-id-required",
        patterns=[r"\bno\s+id\s+required\b", r"\bno\s+documentation\s+(?:needed|required)\b"],
        categories=["food"],
    ),
    # === HEALTHCARE TAGS ===
    TagRule(
        tag="primary-care",
        patterns=[r"\bprimary\s+care\b", r"\bfamily\s+medicine\b", r"\bgeneral\s+practitioner\b"],
        categories=["healthcare"],
    ),
    TagRule(
        tag="dental",
        patterns=[r"\bdental\b", r"\bdentist\b", r"\boral\s+health\b"],
        categories=["healthcare"],
    ),
    TagRule(
        tag="vision",
        patterns=[r"\bvision\b", r"\beye\s+(?:care|exam)\b", r"\boptometr(?:y|ist)\b"],
        categories=["healthcare"],
    ),
    TagRule(
        tag="va-enrolled",
        patterns=[r"\bva[-\s]?enrolled\b", r"\benrolled\s+(?:in\s+)?va\b", r"\bmust\s+be\s+va\s+eligible\b"],
        categories=["healthcare"],
    ),
    TagRule(
        tag="community-care",
        patterns=[r"\bcommunity\s+care\b", r"\bnon[-\s]?va\s+provider\b", r"\bchoice\s+program\b"],
        categories=["healthcare"],
    ),
    TagRule(
        tag="walk-in",
        patterns=[r"\bwalk[-\s]?in\b", r"\bno\s+appointment\s+(?:needed|required)\b"],
        categories=["healthcare", "food"],
    ),
    # === FINANCIAL TAGS ===
    TagRule(
        tag="emergency-assistance",
        patterns=[r"\bemergency\s+(?:assistance|funds?|relief|aid)\b", r"\bcrisis\s+assistance\b"],
        categories=["financial"],
    ),
    TagRule(
        tag="debt-counseling",
        patterns=[r"\bdebt\s+counsel(?:ing|or)\b", r"\bfinancial\s+counsel(?:ing|or)\b", r"\bbudget(?:ing)?\s+help\b"],
        categories=["financial"],
    ),
    TagRule(
        tag="tax-prep",
        patterns=[r"\btax\s+prep(?:aration)?\b", r"\bfree\s+tax\b", r"\bvita\b", r"\btax\s+assistance\b"],
        categories=["financial"],
    ),
    # === SUPPORT SERVICES TAGS ===
    TagRule(
        tag="transportation",
        patterns=[r"\btransportation\b", r"\bride\s+service\b", r"\bvan\s+service\b", r"\bdat\b"],
        categories=["supportServices"],
    ),
    TagRule(
        tag="clothing",
        patterns=[r"\bclothing\b", r"\bclothes\b", r"\binterview\s+attire\b", r"\bprofessional\s+dress\b"],
        categories=["supportServices"],
    ),
    TagRule(
        tag="homeless-veterans",
        patterns=[r"\bhomeless\s+veteran\b", r"\bveteran(?:s)?\s+experiencing\s+homelessness\b", r"\bunhoused\s+veteran\b"],
        categories=["supportServices", "housing"],
    ),
    TagRule(
        tag="female-veterans",
        patterns=[r"\bwomen?\s+veteran\b", r"\bfemale\s+veteran\b", r"\blady\s+veteran\b"],
        categories=["supportServices", "housing"],
    ),
    # === FAMILY TAGS ===
    TagRule(
        tag="childcare",
        patterns=[r"\bchildcare\b", r"\bchild\s+care\b", r"\bdaycare\b"],
        categories=["family"],
    ),
    TagRule(
        tag="military-spouse",
        patterns=[r"\bmilitary\s+spouse\b", r"\bspouse\s+(?:support|resources?)\b"],
        categories=["family"],
    ),
    TagRule(
        tag="caregiver",
        patterns=[r"\bcaregiver\b", r"\bcare[-\s]?giver\b"],
        categories=["family"],
    ),
    TagRule(
        tag="survivor",
        patterns=[r"\bsurvivo(?:r|rs)\b", r"\bdic\b", r"\bdependency\s+(?:and|&)\s+indemnity\b"],
        categories=["family", "benefits"],
    ),
]


def get_searchable_text(resource: Resource) -> str:
    """Combine resource fields into searchable text."""
    parts = [
        resource.title or "",
        resource.description or "",
        resource.summary or "",
        resource.eligibility or "",
        resource.how_to_apply or "",
    ]
    # Also include subcategories as they often contain program names
    if resource.subcategories:
        parts.extend(resource.subcategories)
    return " ".join(parts).lower()


def infer_tags_for_resource(resource: Resource) -> set[str]:
    """Infer eligibility tags for a resource based on its content.

    Returns a set of valid tags from the taxonomy.
    """
    inferred_tags: set[str] = set()
    text = get_searchable_text(resource)
    resource_categories = set(resource.categories or [])
    resource_subcategories = set(resource.subcategories or [])

    for rule in TAG_RULES:
        # Check category filter if specified
        if rule.categories:
            if not resource_categories.intersection(rule.categories):
                continue

        # Check subcategory filter if specified
        if rule.subcategories:
            if not resource_subcategories.intersection(rule.subcategories):
                continue

        # Check if any pattern matches
        for pattern in rule.patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Validate the tag is in our taxonomy
                if is_valid_eligibility_tag(rule.tag):
                    inferred_tags.add(rule.tag)
                break

    # Add tags based on subcategories directly (many subcategories map to tags)
    subcategory_to_tag_map = {
        "hud_vash": "hud-vash",
        "hud-vash": "hud-vash",
        "ssvf": "ssvf",
        "emergency_shelter": "emergency-shelter",
        "emergency-shelter": "emergency-shelter",
        "transitional_housing": "transitional",
        "transitional-housing": "transitional",
        "rapid_rehousing": "rapid-rehousing",
        "rapid-rehousing": "rapid-rehousing",
        "housing_first": "permanent",
        "voucher": "hud-vash",
        "gpd": "transitional",
        "women_veterans": "female-veterans",
        "women-veterans": "female-veterans",
        "rental_assistance": "rental_assistance",
        "rental-assistance": "rental_assistance",
        "job-placement": "job-placement",
        "career-counseling": "career-counseling",
        "va-appeals": "va-appeals",
        "discharge-upgrade": "discharge-upgrade",
        "legal-aid": "free-legal-aid",
        "food-pantry": "food-pantry",
        "meal-program": "meal-program",
        "mobile-distribution": "mobile-distribution",
        "disability-claims": "disability-claims",
        "pension-claims": "pension",
        "vso-services": "vso",
        "cvso": "cvso",
        "voc-rehab": "voc-rehab",
        "certifications": "certifications",
        "apprenticeships": "apprenticeship",
        "gi-bill": "gi-bill-approved",
    }

    for subcat in resource_subcategories:
        if subcat in subcategory_to_tag_map:
            tag = subcategory_to_tag_map[subcat]
            if is_valid_eligibility_tag(tag):
                inferred_tags.add(tag)

    return inferred_tags


def backfill_eligibility_tags(database_url: str, dry_run: bool = False) -> dict:
    """Backfill eligibility tags for all resources.

    Args:
        database_url: Database connection URL
        dry_run: If True, don't commit changes

    Returns:
        Dict with stats about the backfill operation
    """
    engine = create_engine(database_url, echo=False)

    stats = {
        "total_resources": 0,
        "resources_with_existing_tags": 0,
        "resources_updated": 0,
        "resources_unchanged": 0,
        "tags_added": Counter(),
        "resources_with_tags_after": 0,
    }

    with Session(engine) as session:
        # Get all resources
        statement = select(Resource)
        resources = session.exec(statement).all()
        stats["total_resources"] = len(resources)

        for resource in resources:
            existing_tags = set(resource.tags or [])
            if existing_tags:
                stats["resources_with_existing_tags"] += 1

            # Infer new tags
            inferred_tags = infer_tags_for_resource(resource)

            # Combine existing and inferred tags (preserving existing)
            new_tags = existing_tags | inferred_tags
            new_tags_added = inferred_tags - existing_tags

            if new_tags_added:
                # Update the resource
                resource.tags = sorted(new_tags)
                resource.updated_at = datetime.now(UTC)
                session.add(resource)
                stats["resources_updated"] += 1

                # Track which tags were added
                for tag in new_tags_added:
                    stats["tags_added"][tag] += 1
            else:
                stats["resources_unchanged"] += 1

            # Track resources with tags after
            if new_tags:
                stats["resources_with_tags_after"] += 1

        if not dry_run:
            session.commit()

    return stats


def print_stats(stats: dict, dry_run: bool = False) -> None:
    """Print statistics from the backfill operation."""
    print("\n" + "=" * 60)
    print("Eligibility Tags Backfill Results" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 60)

    total = stats["total_resources"]
    print(f"\nTotal resources: {total}")
    print(f"Resources with existing tags: {stats['resources_with_existing_tags']}")
    print(f"Resources updated: {stats['resources_updated']}")
    print(f"Resources unchanged: {stats['resources_unchanged']}")

    # Coverage stats
    before_coverage = stats["resources_with_existing_tags"] / total * 100 if total else 0
    after_coverage = stats["resources_with_tags_after"] / total * 100 if total else 0
    print(f"\nTag coverage BEFORE: {before_coverage:.1f}% ({stats['resources_with_existing_tags']}/{total})")
    print(f"Tag coverage AFTER:  {after_coverage:.1f}% ({stats['resources_with_tags_after']}/{total})")

    if stats["tags_added"]:
        print("\nMost commonly added tags:")
        for tag, count in stats["tags_added"].most_common(20):
            print(f"  {tag}: {count}")

    print("\n" + "=" * 60)

    # Check if we hit the 50% target
    if after_coverage >= 50:
        print(f"SUCCESS: Tag coverage is {after_coverage:.1f}% (target: 50%)")
    else:
        print(f"WARNING: Tag coverage is {after_coverage:.1f}% (target: 50%)")
        print("Consider adding more tag rules to improve coverage.")

    print("=" * 60)


def validate_all_tags_in_taxonomy() -> None:
    """Validate that all tags in TAG_RULES exist in the taxonomy."""
    invalid_tags = []
    for rule in TAG_RULES:
        if not is_valid_eligibility_tag(rule.tag):
            invalid_tags.append(rule.tag)

    if invalid_tags:
        print(f"WARNING: The following tags are not in the taxonomy: {invalid_tags}")
        print("These tags will be skipped during backfill.")


def main():
    parser = argparse.ArgumentParser(description="Backfill eligibility tags on resources")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/vibe4vets")

    print("Validating tag rules against taxonomy...")
    validate_all_tags_in_taxonomy()

    print(f"\nRunning eligibility tag backfill{'  (DRY RUN)' if args.dry_run else ''}...")

    stats = backfill_eligibility_tags(database_url, dry_run=args.dry_run)
    print_stats(stats, dry_run=args.dry_run)

    if args.dry_run:
        print("\nTo apply changes, run without --dry-run flag.")


if __name__ == "__main__":
    main()
