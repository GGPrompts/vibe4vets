# Discover Employment Resources for Veterans

You are researching veteran employment and career resources for a specific geographic area. Find real, currently operating programs that help veterans find jobs.

## Execution Strategy

**Use Haiku subagents in parallel to minimize token cost:**

1. Spawn 3-4 Haiku Explore agents simultaneously, each searching different query sets
2. Each agent handles 2-3 search queries and extracts results
3. Collect and merge results from all agents
4. Only use the main session for final deduplication and formatting

Example:
```
Agent 1: "[AREA] veteran job fair", "[AREA] DVOP disabled veteran outreach"
Agent 2: "[AREA] veteran employment representative", "[AREA] hire veterans program"
Agent 3: "[AREA] veteran career center", "[AREA] veteran apprenticeship"
```

## Target Area
{{AREA}} (e.g., "Austin, Texas" or "Chicago metropolitan area")

## What to Find

Look for these types of resources:
1. **Veteran employment representatives** - State workforce agency veteran staff (DVOP, LVER)
2. **Hiring programs** - Companies with veteran hiring initiatives
3. **Career centers** - VA Vocational Rehab offices, American Job Centers
4. **Nonprofit job programs** - Hire Heroes USA, American Corporate Partners, etc.
5. **Apprenticeships** - Veteran-specific apprenticeship programs
6. **Entrepreneurship** - Veteran small business support (VBOC, SBA resources)
7. **Resume/interview help** - Free career coaching for veterans

## Search Strategy

Search for:
- "[AREA] veteran job fair"
- "[AREA] DVOP disabled veteran outreach"
- "[AREA] veteran employment representative"
- "[AREA] hire veterans program"
- "[AREA] veteran career center"
- "American Job Center [AREA] veterans"
- "[AREA] veteran apprenticeship"
- "[AREA] veteran owned business support"

## Required Information

For each resource, extract:
- **Name**: Official program/organization name
- **Phone**: Direct contact number
- **Address**: Physical location
- **Website**: Official URL
- **Services**: Specific services (resume help, job placement, training, etc.)
- **Eligibility**: Any restrictions (disabled veterans, recently separated, etc.)
- **Cost**: Free or fee-based

## Output Format

Return a JSON array of resources:

```json
[
  {
    "name": "Example Veteran Career Program",
    "organization": "Parent Organization Name",
    "category": "employment",
    "subcategory": "job_placement|career_counseling|apprenticeship|entrepreneurship|job_fair",
    "description": "Brief description of services",
    "phone": "555-123-4567",
    "website": "https://example.org/veterans",
    "address": "123 Main St, City, ST 12345",
    "eligibility": ["veteran", "disabled_veteran", "transitioning"],
    "services": ["resume review", "job matching", "interview prep"],
    "cost": "free",
    "coverage_area": "City/County/Region",
    "source_url": "https://... where you found this",
    "confidence": 0.85,
    "notes": "Any additional context"
  }
]
```

## Quality Standards

- Prioritize resources with direct veteran staff/focus
- Include specific contact info, not just "call your local VA"
- Note if appointments are required
- Set lower confidence for resources found on outdated pages

## Do NOT Include

- Generic job boards (Indeed, LinkedIn) without veteran-specific programs
- Resources requiring VA healthcare enrollment to access
- National programs without local presence/contact
- Recruiting firms that charge veterans fees
