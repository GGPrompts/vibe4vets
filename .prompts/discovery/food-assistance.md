# Discover Food Assistance Resources for Veterans

You are researching food assistance resources for veterans in a specific geographic area. Find real, currently operating programs that help veterans access food.

## Execution Strategy

**Use Haiku subagents in parallel to minimize token cost:**

1. Spawn 3-4 Haiku Explore agents simultaneously, each searching different query sets
2. Each agent handles 2-3 search queries and extracts results
3. Collect and merge results from all agents
4. Only use the main session for final deduplication and formatting

Example:
```
Agent 1: "[AREA] veteran food pantry", "[AREA] VFW food bank"
Agent 2: "[AREA] American Legion food assistance", "VA medical center [AREA] food pantry"
Agent 3: "[AREA] veteran meal program", "[AREA] food bank veterans"
```

## Target Area
{{AREA}} (e.g., "Phoenix, Arizona" or "Miami-Dade County, Florida")

## What to Find

Look for these types of resources:
1. **Veteran-specific food pantries** - VFW, American Legion, DAV food programs
2. **VA medical center food assistance** - Some VAMCs have food pantries
3. **Community food banks** - That serve veterans (note if veteran-priority)
4. **Mobile food distributions** - Regular food truck/distribution events
5. **Meal programs** - Hot meal sites, veteran meal delivery
6. **SNAP/food stamp assistance** - Help applying for benefits
7. **Emergency food boxes** - One-time emergency food assistance

## Search Strategy

Search for:
- "[AREA] veteran food pantry"
- "[AREA] VFW food bank"
- "[AREA] American Legion food assistance"
- "VA medical center [AREA] food pantry"
- "[AREA] veteran meal program"
- "[AREA] food bank veterans"
- "Feeding America [AREA] veterans"

## Required Information

For each resource, extract:
- **Name**: Official program/organization name
- **Phone**: Contact number
- **Address**: Physical location
- **Hours**: Operating hours/distribution times (CRITICAL for food banks)
- **Eligibility**: Requirements (veteran ID, income limits, etc.)
- **What's provided**: Food box, hot meals, groceries, etc.
- **Frequency**: How often can someone access (weekly, monthly, etc.)

## Output Format

Return a JSON array of resources:

```json
[
  {
    "name": "Example Veteran Food Pantry",
    "organization": "Parent Organization Name",
    "category": "food_assistance",
    "subcategory": "food_pantry|meal_program|mobile_distribution|snap_assistance",
    "description": "Brief description of what's provided",
    "phone": "555-123-4567",
    "website": "https://example.org/food",
    "address": "123 Main St, City, ST 12345",
    "eligibility": ["veteran", "low_income", "family"],
    "hours": "Tuesdays 10am-2pm, Thursdays 4pm-7pm",
    "frequency": "Once per week",
    "what_provided": "Groceries for 3-5 days",
    "requirements": "Veteran ID or DD-214, proof of address",
    "coverage_area": "City/County",
    "source_url": "https://... where you found this",
    "confidence": 0.85,
    "notes": "Call ahead to confirm hours"
  }
]
```

## Quality Standards

- **Hours are critical** - Food banks have limited hours, include them
- **Frequency matters** - Note how often veterans can access
- **Requirements** - What ID/documentation is needed
- Include if appointment is required vs walk-in
- Note if they serve families or just individuals

## Do NOT Include

- Resources that are clearly outdated (COVID-era programs that ended)
- National hotlines without local distribution info
- Programs requiring extensive application processes for emergency food
- Resources that charge fees for food assistance
