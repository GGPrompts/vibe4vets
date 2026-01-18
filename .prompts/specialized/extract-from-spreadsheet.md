# Extract Resources from Spreadsheet/PDF Data

You are extracting structured resource data from a spreadsheet or PDF that contains veteran resource information (like the SSVF grantee list, HUD-VASH provider list, etc.).

## Source Data

```
{{RAW_DATA}}
```

## Source Metadata
- **Source name**: {{SOURCE_NAME}} (e.g., "VA SSVF FY26 Grantee List")
- **Source URL**: {{SOURCE_URL}}
- **Source tier**: {{TIER}} (1=official VA/federal, 2=major VSO, 3=state agency, 4=community)
- **Data date**: {{DATA_DATE}}

## Extraction Task

Convert each row/entry into a structured resource. The source data may have:
- Organization names
- Grant IDs or program codes
- Contact information
- Geographic coverage
- Award amounts or capacity info

## Output Format

For each entry, extract:

```json
{
  "name": "Program name (derived from org + program type)",
  "organization": "Official organization name",
  "category": "housing|employment|legal|training|financial",
  "subcategory": "ssvf|hud_vash|vboc|etc",
  "description": "Generated description based on program type",

  "coverage_area": {
    "states": ["VA", "MD"],
    "regions": ["VISN 6"],
    "notes": "Serves Richmond metro area"
  },

  "source": {
    "name": "{{SOURCE_NAME}}",
    "url": "{{SOURCE_URL}}",
    "tier": {{TIER}},
    "extracted_date": "{{DATA_DATE}}"
  },

  "raw_fields": {
    "grant_id": "...",
    "award_amount": "...",
    "other_field": "..."
  },

  "needs_enrichment": ["phone", "address", "website"],
  "confidence": 0.9,
  "notes": "Extracted from official VA data, needs contact info lookup"
}
```

## Enrichment Flags

Mark which fields need follow-up:
- `phone` - No phone number in source, needs lookup
- `address` - No address, needs geocoding
- `website` - No URL, needs search
- `eligibility` - Generic program eligibility, may need local specifics
- `hours` - Operating hours not included

## Category Mapping

Based on program type:
- SSVF → housing/ssvf
- HUD-VASH → housing/hud_vash
- VBOC → employment/entrepreneurship
- HVRP → employment/job_placement
- VRAP → training/vocational
- GPD → housing/transitional

## Quality Notes

- Preserve original data in `raw_fields` for audit trail
- Generate descriptions based on known program types
- Flag for enrichment rather than guessing contact info
- Set high confidence (0.85-0.95) for official source data
- Note any data quality issues (missing states, unclear org names)

## Batch Output

Return as array:
```json
{
  "source": "{{SOURCE_NAME}}",
  "extraction_date": "YYYY-MM-DD",
  "total_extracted": 123,
  "resources": [...],
  "extraction_notes": [
    "5 entries had unclear state coverage",
    "12 entries appear to be duplicates by grant ID"
  ]
}
```
