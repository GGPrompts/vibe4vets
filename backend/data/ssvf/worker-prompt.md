# SSVF Grantee Enrichment Worker

You are enriching SSVF grantee data with contact information. Your batch file has been assigned.

## Your Task

1. Read your assigned batch file from `backend/data/ssvf/grantees-batch-{N}.json`
2. For each grantee, spawn Haiku subagents (5 at a time) to search for contact info
3. Save enriched results to `backend/data/ssvf/enriched-batch-{N}.json`
4. Save progress after every 10 grantees

## Per-Grantee Search (Haiku subagent task)

For each grantee, search:
- "[Organization Name] SSVF veteran housing [state]"
- "[Organization Name] contact address phone"

Extract:
- Website URL
- Phone number (intake/services line)
- Address (full: street, city, state, zip)
- Service area
- Intake process (how to apply)
- Mobile outreach (yes/no)

## Output Format

```json
{
  "grant_id": "12-AK-001",
  "org_name": "Catholic Social Services",
  "state": "AK",
  "website": "https://...",
  "phone": "907-222-7300",
  "address": "3710 E 20th Ave, Anchorage, AK 99508",
  "city": "Anchorage",
  "zip": "99508",
  "service_area": "Anchorage, Mat-Su Valley",
  "intake_process": "Call to schedule appointment",
  "mobile_outreach": false,
  "confidence": 0.85,
  "source_url": "https://...",
  "enriched_at": "2026-01-20T05:30:00Z"
}
```

If not found, set confidence to 0 and add `"not_found_reason": "..."`

## DO NOT research eligibility - it's the same for all SSVF:
- Veteran or family member
- At or below 50% AMI
- Homeless or at risk

## Execution

1. Read batch file
2. Process in groups of 5 using parallel Haiku subagents
3. Merge results
4. Save to enriched-batch-{N}.json
5. Report completion summary

START NOW - read your batch file and begin enrichment.
