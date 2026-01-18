# Discover Housing Resources for Veterans

You are researching veteran housing resources for a specific geographic area. Find real, currently operating programs that help veterans with housing needs.

## Execution Strategy

**Use Haiku subagents in parallel to minimize token cost:**

1. Spawn 3-4 Haiku Explore agents simultaneously, each searching different query sets
2. Each agent handles 2-3 search queries and extracts results
3. Collect and merge results from all agents
4. Only use the main session for final deduplication and formatting

Example:
```
Agent 1: "[AREA] veteran emergency shelter", "[AREA] emergency housing veterans"
Agent 2: "[AREA] SSVF provider", "[AREA] HUD-VASH coordinator"
Agent 3: "[AREA] transitional housing veterans", "VA medical center [AREA] housing services"
```

## Target Area
{{AREA}} (e.g., "Richmond, Virginia" or "San Diego County, California")

## What to Find

Look for these types of resources:
1. **Emergency shelters** - Immediate overnight housing
2. **Transitional housing** - 30-90 day programs
3. **SSVF providers** - Supportive Services for Veteran Families (rapid rehousing, prevention)
4. **HUD-VASH contacts** - Local VA medical center housing coordinators
5. **Stand Down events** - Annual resource events for veterans experiencing homelessness
6. **Permanent supportive housing** - Long-term housing with services

## Search Strategy

Search for:
- "[AREA] veteran emergency shelter"
- "[AREA] SSVF provider"
- "[AREA] veteran housing assistance"
- "[AREA] HUD-VASH coordinator"
- "VA medical center [AREA] housing services"
- "[AREA] veteran transitional housing"

## Required Information

For each resource, extract:
- **Name**: Official program/organization name
- **Phone**: Direct number (not VA main line)
- **Address**: Physical location if applicable
- **Website**: Official URL
- **Eligibility**: Who qualifies (veteran status, income, housing status, etc.)
- **Services**: What specifically they provide
- **Hours**: If available (especially for shelters)

## Output Format

Return a JSON array of resources:

```json
[
  {
    "name": "Example Veteran Housing Program",
    "organization": "Parent Organization Name",
    "category": "housing",
    "subcategory": "emergency_shelter|transitional|ssvf|hud_vash|permanent_supportive",
    "description": "Brief description of services",
    "phone": "555-123-4567",
    "website": "https://example.org/veterans",
    "address": "123 Main St, City, ST 12345",
    "eligibility": ["veteran", "housing", "low_income"],
    "hours": "24/7" or "Mon-Fri 8am-5pm",
    "coverage_area": "City/County/Region",
    "source_url": "https://... where you found this",
    "confidence": 0.85,
    "notes": "Any additional context"
  }
]
```

## Quality Standards

- Only include resources you can verify exist
- Phone numbers must be specific to the program (not generic VA hotlines)
- Include source URL where you found the information
- Set confidence lower (0.5-0.7) if information seems outdated or incomplete
- Skip resources that are just links to VA.gov general pages

## Do NOT Include

- Generic VA.gov pages everyone already knows
- Resources that require calling a national hotline first
- Programs that have clearly shut down
- Resources outside the target area
