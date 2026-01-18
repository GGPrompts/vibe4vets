# Check for Duplicate Resources

You are checking if a newly discovered resource already exists in the database or is a duplicate/variant of an existing entry.

## New Resource

```json
{{NEW_RESOURCE}}
```

## Existing Resources to Compare

```json
{{EXISTING_RESOURCES}}
```

## Duplicate Detection Rules

### Definite Duplicate (same resource)
- Same organization AND same program name
- Same phone number
- Same address AND same service type
- Same website URL

### Likely Duplicate (probably same, needs review)
- Very similar names (typos, abbreviations)
- Same organization, overlapping services
- Same address, different program names (might be departments)
- Phone numbers differ by 1-2 digits

### Related But Distinct (keep both)
- Same organization, different locations
- Same organization, clearly different programs
- Similar services, different organizations
- Same building, different organizations

### Not Duplicates (clearly different)
- Different organizations
- Different locations (unless one is HQ)
- Different service categories

## Output Format

```json
{
  "new_resource_name": "...",
  "duplicate_status": "definite_duplicate|likely_duplicate|related|unique",

  "matches": [
    {
      "existing_id": "...",
      "existing_name": "...",
      "match_confidence": 0.0-1.0,
      "match_reasons": [
        "Same phone number",
        "Organization name matches",
        "Address within 0.1 miles"
      ],
      "differences": [
        "Website URL different",
        "Hours not listed in existing"
      ],
      "recommendation": "merge|keep_both|replace_existing|skip_new"
    }
  ],

  "recommended_action": "add_new|merge_with_ID|skip|review",
  "merge_strategy": null or {
    "target_id": "...",
    "fields_to_update": ["phone", "hours", "website"],
    "fields_to_keep": ["description", "eligibility"]
  },

  "notes": "Additional context..."
}
```

## Merge Strategies

### When to Merge
- New resource has more complete info than existing
- New resource has newer verification date
- Same resource, different data quality

### When to Keep Both
- Different locations of same org
- Different programs at same org
- Serves different eligibility groups

### When to Skip New
- Existing entry is more complete
- New entry has lower confidence
- New entry from less reliable source

## Comparison Helpers

Use fuzzy matching for:
- Organization names (ignore Inc, LLC, "The", etc.)
- Addresses (normalize street abbreviations)
- Phone numbers (ignore formatting)

Consider as same location if:
- Addresses within 0.1 miles
- Same zip code + similar street name
