---
description: AI-powered discovery of hard-to-find veteran resources via web search
model: sonnet
allowed-tools:
  - WebSearch
  - Read
  - Write
  - Bash
  - Task
---

# /scan-resources - Veteran Resource Discovery

Discover and curate veteran resources from across the web that aren't in official databases.

## Usage

```
/scan-resources [category] [location]
```

**Examples:**
- `/scan-resources employment Texas` - Find employment resources in Texas
- `/scan-resources legal` - Find legal aid resources nationwide
- `/scan-resources housing "New York City"` - Find housing resources in NYC

## Discovery Workflow

### Step 1: Parse Arguments

Extract category and location from the command arguments:
- **category**: employment, training, housing, legal (optional, defaults to all)
- **location**: State name, city, or "nationwide" (optional)

### Step 2: Generate Search Queries

Based on the category and location, generate targeted search queries:

**Employment queries:**
- "veteran employment programs {location}"
- "veteran job placement services {location}"
- "veteran career counseling {location}"
- "veteran hiring initiative nonprofit"

**Training queries:**
- "veteran vocational training {location}"
- "veteran apprenticeship programs {location}"
- "veteran certification programs free"
- "GI Bill approved schools {location}"

**Housing queries:**
- "veteran housing assistance {location}"
- "veteran emergency shelter {location}"
- "SSVF provider {location}"
- "veteran transitional housing nonprofit"

**Legal queries:**
- "veteran legal aid {location}"
- "VA appeals assistance free"
- "veteran discharge upgrade help"
- "veterans treatment court {location}"

### Step 3: Execute Web Searches

Use the WebSearch tool to search for resources. For each query:

1. Execute the search with `WebSearch`
2. Extract URLs and snippets from results
3. Filter out:
   - VA.gov pages (already in Tier 1 sources)
   - Generic news articles
   - Paywalled content
   - Outdated pages (check for date indicators)

### Step 4: Analyze and Extract

For each promising result, analyze the content:

1. **Organization Info:**
   - Name of the organization
   - Website URL
   - Contact information (phone, email)

2. **Resource Details:**
   - Program/service name
   - Description of what they offer
   - Eligibility requirements
   - How to apply

3. **Location Info:**
   - Physical address if local
   - Service area (national, state, local)
   - States served

4. **Category Classification:**
   - Primary category: employment, training, housing, legal
   - Relevant subcategories from taxonomy

### Step 5: Score and Validate

Assign quality scores based on:

**Source Tier (suggested_tier):**
- Tier 2 (0.8): Major VSO, established nonprofit
- Tier 3 (0.6): State agency, regional organization
- Tier 4 (0.4): Community organization, local nonprofit

**Confidence Score (0.0-1.0):**
- +0.3 if has physical address
- +0.2 if has phone number
- +0.2 if has clear eligibility info
- +0.2 if has recent activity/updates
- +0.1 if has email contact

### Step 6: Check Duplicates

Before adding to results, check if resource might already exist:
- Compare organization name against existing records
- Compare address if available
- Flag potential duplicates with `is_duplicate: true`

### Step 7: Generate Output

Format discovered resources as JSON matching this schema:

```json
{
  "discovered": [
    {
      "title": "Veteran Career Services Program",
      "description": "Free career counseling and job placement for veterans",
      "source_url": "https://example.org/veterans",
      "org_name": "Example Veterans Foundation",
      "org_website": "https://example.org",
      "categories": ["employment"],
      "subcategories": ["career-counseling", "job-placement"],
      "address": "123 Main St",
      "city": "Austin",
      "state": "TX",
      "zip_code": "78701",
      "phone": "(512) 555-0100",
      "email": "contact@example.org",
      "eligibility": "All veterans with honorable or general discharge",
      "how_to_apply": "Call to schedule appointment or apply online",
      "scope": "state",
      "states": ["TX"],
      "suggested_tier": 3,
      "confidence": 0.85,
      "is_duplicate": false,
      "discovery_notes": "Found via web search, active program with recent testimonials"
    }
  ],
  "stats": {
    "queries_executed": 8,
    "total_results": 45,
    "after_filtering": 15,
    "duplicates_skipped": 3,
    "queued_for_review": 12
  },
  "queries_used": [
    "veteran employment programs Texas",
    "veteran job placement services Austin"
  ]
}
```

### Step 8: Save Results

Save the discovery results to a timestamped file:

```bash
# Create output directory if needed
mkdir -p backend/data/discoveries

# Save results
# File: backend/data/discoveries/scan-{category}-{location}-{timestamp}.json
```

### Step 9: Summarize

Provide a summary to the user:

```
## Discovery Complete

**Search:** {category} resources in {location}
**Queries executed:** {count}
**Resources found:** {total_found}
**After deduplication:** {unique_count}
**Ready for review:** {queued_count}

### Top Discoveries:
1. {org_name} - {title} (Confidence: {score})
2. ...

Results saved to: backend/data/discoveries/{filename}

To import to review queue:
  # Dry run first to preview
  python -m backend.scripts.import_discoveries --dry-run backend/data/discoveries/{filename}

  # Then import for real
  python -m backend.scripts.import_discoveries backend/data/discoveries/{filename}
```

## Valid Categories

From `backend/app/core/taxonomy.py`:
- **employment**: Job placement, career services, hiring programs
- **training**: Vocational rehab, certifications, education
- **housing**: HUD-VASH, SSVF, shelters, housing assistance
- **legal**: Legal aid, VA appeals, discharge upgrades

## Valid Subcategories

**Employment:**
- job-placement, career-counseling, veteran-preference, self-employment

**Training:**
- voc-rehab, certifications, apprenticeships, gi-bill

**Housing:**
- hud-vash, ssvf, emergency-shelter, home-repair

**Legal:**
- va-appeals, discharge-upgrade, legal-aid, veterans-court

## Notes

- Excludes VA.gov resources (already captured by va_gov connector)
- Prioritizes nonprofits and established VSOs
- Flags resources needing verification before going live
- All discovered resources go through human review queue
