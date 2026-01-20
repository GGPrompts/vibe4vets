# Enrich SSVF FY26 Grantees with Contact Information

You are enriching SSVF (Supportive Services for Veteran Families) grantee data with contact information. The source spreadsheet has organization names and grant amounts, but lacks websites, phones, addresses, and intake processes.

## Source Data

File: `C:\Users\marci\Downloads\SSVF_FY26_Awards.xlsx`

Contains 235 grantees with:
- Organization Name
- Geographical Area Served (state)
- Grant ID
- Adjusted Awarded Amount
- VISN

## Execution Strategy

**Batch processing with parallel Haiku agents:**

1. Export grantees to JSON (if not already done)
2. Check progress file to see which are complete
3. Spawn 5-10 Haiku agents in parallel, each handling 5-10 grantees
4. Each agent searches and extracts contact info
5. Merge results, save progress
6. Repeat until all 235 are done

Example batch assignment:
```
Agent 1: Grantees 1-10 (AK, AL organizations)
Agent 2: Grantees 11-20 (AR, AZ organizations)
Agent 3: Grantees 21-30 (CA organizations)
...
```

## Per-Grantee Search Strategy

For each grantee, search:
- "[Organization Name] SSVF veteran housing"
- "[Organization Name] [state] veteran services"
- "[Organization Name] contact"

## Required Information Per Grantee

Extract:
- **Website**: Organization's main site or SSVF-specific page
- **Phone**: Direct intake/services line (not general switchboard)
- **Locations**: Physical office(s) with full address
  - City, State, ZIP for geocoding
  - Walk-in hours if available
  - Appointment required?
- **Service Area**: Counties or cities served
- **Intake Process**: How veterans apply (phone, walk-in, referral)
- **Mobile Outreach**: Do they come to clients? (critical for homeless vets)
- **Phone Intake**: Can veterans call to start the process?

## SSVF Eligibility (Same for All - Do Not Research)

All SSVF programs have the same federal eligibility:
- Veteran or veteran family member
- Served at least 1 day active duty (not dishonorable discharge)
- At or below 50% Area Median Income
- Homeless or at imminent risk of homelessness

Do NOT spend time researching eligibility - it's standardized.

## Output Format

For each grantee, output:

```json
{
  "grant_id": "12-AK-001",
  "org_name": "Catholic Social Services",
  "state": "AK",
  "website": "https://prior to url for ssvf contact",
  "phone": "907-222-7300",
  "locations": [
    {
      "address": "3710 E 20th Ave",
      "city": "Anchorage",
      "state": "AK",
      "zip": "99508",
      "is_main_office": true,
      "walk_in_hours": "Mon-Fri 9am-4pm",
      "by_appointment": true
    }
  ],
  "service_area": "Anchorage, Mat-Su Valley, Kenai Peninsula",
  "intake_process": "Call to schedule intake appointment. Walk-ins accepted Mon-Fri 9am-4pm.",
  "mobile_outreach": true,
  "phone_intake": true,
  "confidence": 0.9,
  "source_urls": ["https://..."],
  "not_found_reason": null
}
```

If information cannot be found:
```json
{
  "grant_id": "XX-XX-XXX",
  "org_name": "Unknown Organization",
  "state": "XX",
  "confidence": 0.0,
  "not_found_reason": "Organization website not found. May have changed name or merged."
}
```

## Progress Tracking

Save progress to: `backend/data/ssvf/enrichment-progress.json`

```json
{
  "total": 235,
  "completed": 47,
  "failed": 3,
  "last_updated": "2026-01-20T04:30:00Z",
  "completed_ids": ["12-AK-001", "20-AK-152", ...],
  "failed_ids": ["XX-XX-XXX"]
}
```

Save enriched data to: `backend/data/ssvf/enriched-grantees.json`

## Quality Standards

- Verify the organization actually provides SSVF services (not just any veteran program)
- Phone numbers should reach someone who can help with SSVF (not general info lines)
- Addresses must be complete enough to geocode
- Set confidence lower (0.5-0.7) if:
  - Website looks outdated
  - Phone number goes to general org line
  - Couldn't confirm SSVF-specific services
- Set confidence to 0 and provide `not_found_reason` if:
  - Organization appears defunct
  - No web presence found
  - Name may have changed

## Do NOT Include

- Generic VA.gov links
- National SSVF hotline (everyone knows that)
- Resources that aren't actually SSVF providers
- Guessed or fabricated contact information

## After Enrichment

Once all grantees are enriched:

1. Review the failed/low-confidence entries manually
2. Run the import script:
   ```bash
   python -m backend.scripts.import_ssvf_grantees backend/data/ssvf/enriched-grantees.json
   ```
3. Resources will be created with:
   - Standard SSVF eligibility template
   - Linked to "SSVF FY26 Grantee Data" source (Tier 1)
   - Category: housing
   - Subcategory: ssvf
   - Locations geocoded for zip code search
