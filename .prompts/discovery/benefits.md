# Discover Benefits Consultation Resources for Veterans

You are researching benefits consultation and claims assistance resources for veterans in a specific geographic area. Find real, currently operating programs that help veterans navigate VA benefits, file claims, and get the benefits they've earned.

## Execution Strategy

**Use Haiku subagents in parallel to minimize token cost:**

1. Spawn 3-4 Haiku Explore agents simultaneously, each searching different query sets
2. Each agent handles 2-3 search queries and extracts results
3. Collect and merge results from all agents
4. Only use the main session for final deduplication and formatting

Example:
```
Agent 1: "[AREA] veteran service officer", "[AREA] DAV claims assistance"
Agent 2: "[AREA] VFW benefits help", "[AREA] American Legion service officer"
Agent 3: "[AREA] county veteran services", "[AREA] VA benefits counseling"
```

## Target Area
{{AREA}} (e.g., "Phoenix, Arizona" or "Miami-Dade County, Florida")

## What to Find

Look for these types of resources:
1. **VSO Service Offices** - DAV, VFW, American Legion, AMVETS accredited representatives
2. **County/State Veteran Services** - Local government veteran service officers
3. **VA Regional Office** - Benefits assistance at VA facilities
4. **Legal Aid for Appeals** - Attorneys/nonprofits helping with VA appeals
5. **Pension Management** - Help with VA pension applications
6. **Survivor Benefits** - DIC, burial benefits assistance
7. **State Veteran Benefits** - State-specific benefits (property tax exemptions, education, etc.)

## Search Strategy

Search for:
- "[AREA] veteran service officer"
- "[AREA] DAV claims assistance"
- "[AREA] VFW benefits help"
- "[AREA] American Legion service officer"
- "[AREA] county veteran services"
- "[AREA] VA benefits counseling"
- "[AREA] veteran disability claims help"
- "[STATE] veteran benefits office"
- "[AREA] veteran pension assistance"

## Required Information

For each resource, extract:
- **Name**: Official program/organization name
- **Phone**: Contact number (CRITICAL - veterans often need to call)
- **Address**: Physical location for in-person appointments
- **Hours**: Operating hours (many VSOs have limited hours)
- **Services**: What types of claims/benefits they help with
- **Cost**: Should be FREE for accredited VSOs
- **Appointment**: Walk-in or appointment required

## Output Format

Return a JSON array of resources:

```json
[
  {
    "name": "DAV Service Office - Phoenix",
    "organization": "Disabled American Veterans",
    "category": "benefits",
    "subcategory": "vso-services|disability-claims|pension|survivor-benefits|appeals|state-benefits",
    "description": "Free claims assistance from accredited DAV National Service Officers",
    "phone": "555-123-4567",
    "website": "https://example.org/veterans",
    "address": "123 Main St, City, ST 12345",
    "city": "Phoenix",
    "state": "AZ",
    "eligibility": {
      "veteran_status_required": true,
      "family_eligible": true,
      "docs_required": ["DD-214", "Medical records", "Photo ID"]
    },
    "services": ["Disability compensation", "Pension claims", "Appeals", "DIC claims"],
    "hours": "Monday-Friday 8am-4pm",
    "appointment_required": true,
    "cost": "Free",
    "coverage_area": "Maricopa County",
    "source_url": "https://... where you found this",
    "confidence": 0.85,
    "notes": "Located inside VA Regional Office, Building A"
  }
]
```

## Quality Standards

- **Phone is critical** - Veterans often need to call for appointments
- **Verify it's FREE** - Accredited VSOs don't charge for claims help
- **Note if accredited** - VA-accredited representatives are important
- **Include hours** - Many VSOs have limited walk-in hours
- **Services offered** - Be specific about what claims they help with
- **Appointment info** - Note if walk-in or appointment needed

## Key Organizations to Search For

- **Disabled American Veterans (DAV)** - Major VSO with service officers
- **Veterans of Foreign Wars (VFW)** - Service officers at many posts
- **American Legion** - Service officers for claims assistance
- **AMVETS** - Accredited service representatives
- **County Veteran Service Officers** - Every county has one (often free)
- **State Department of Veterans Affairs** - State-level benefits offices
- **National Veterans Legal Services Program (NVLSP)** - Appeals assistance
- **Legal Aid** - Some legal aid orgs help with VA appeals

## Do NOT Include

- Paid claims agents or attorneys (unless specifically for appeals after denial)
- Resources that charge upfront fees for benefits help
- Generic VA.gov links without local contact info
- Outdated offices that have closed
- Resources outside the target geographic area
