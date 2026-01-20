# SSVF Grantee Enrichment - Batch 2 (Grantees 79-156)

You are a coordinator enriching SSVF grantee data. Your job is to find contact information for 78 organizations.

## Your Batch

Read: `backend/data/ssvf/grantees-batch-2.json`
Save results to: `backend/data/ssvf/enriched-batch-2.json`

## Execution Pattern

**Use 5 Haiku subagents in parallel** to search for contact info. Process the list in groups:

1. Take grantees 1-5, spawn 5 parallel Haiku agents (one per grantee)
2. Collect results, append to output file
3. Take grantees 6-10, spawn 5 more parallel agents
4. Repeat until all 78 are done

Each Haiku subagent searches for ONE grantee:
- Search: "[Org Name] SSVF veteran housing [state]"
- Search: "[Org Name] homeless veterans contact"
- Extract: website, phone, address, intake process
- Return structured JSON

## Subagent Prompt Template

For each grantee, give the subagent this task:

```
Search for contact information for this SSVF provider:
- Organization: {org_name}
- State: {state}
- Grant ID: {grant_id}

Search the web for their SSVF program contact info. Find:
1. Website URL (their site, not VA.gov)
2. Phone number (intake/services line)
3. Full address (street, city, state, zip)
4. How veterans apply (walk-in, call, referral?)
5. Service area (what counties/cities they cover)

Return JSON:
{
  "grant_id": "{grant_id}",
  "org_name": "{org_name}",
  "website": "https://...",
  "phone": "XXX-XXX-XXXX",
  "address": "full street address",
  "city": "...",
  "state": "XX",
  "zip": "XXXXX",
  "intake_process": "how to apply",
  "service_area": "counties/cities served",
  "confidence": 0.0-1.0,
  "source_url": "where you found this"
}

If not found, return confidence: 0 and not_found_reason.
```

## Output Format

After each batch of 5, append results to `enriched-batch-2.json`:

```json
[
  { "grant_id": "12-AK-001", "org_name": "...", ... },
  { "grant_id": "20-AK-152", "org_name": "...", ... },
  ...
]
```

## Progress Tracking

After every 10 grantees, print:
```
Progress: 10/78 complete (12.8%)
```

## DO NOT research eligibility - same for all SSVF providers.

## START NOW

1. Read `backend/data/ssvf/grantees-batch-2.json`
2. Process grantees 1-5 with 5 parallel Haiku agents
3. Save results
4. Continue with 6-10, 11-15, etc.
5. Keep going until all 78 are enriched
