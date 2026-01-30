# Missing Website URLs - Database Query Results

## Executive Summary

**Query Date:** 2026-01-29  
**Total Resources Missing Websites:** 8,167  
**Percentage of Database:** ~97% of resources (indicates this is a significant data enrichment opportunity)

## Status Breakdown

- **ACTIVE:** 8,164 resources
- **NEEDS_REVIEW:** 3 resources

## Category Distribution

The missing websites are heavily concentrated in employment and healthcare resources:

| Category | Count | % of Missing |
|----------|-------|------------|
| Employment | 7,960 | 97.5% |
| Healthcare | 7,955 | 97.4% |
| Training | 2,748 | 33.7% |
| Housing | 239 | 2.9% |
| Uncategorized | 204 | 2.5% |
| Legal | 81 | 1.0% |

**Note:** Resources can have multiple categories, so counts overlap.

## Geographic Concentration

The resources are spread across all 50 states, with California dominating:

| Rank | State | Count |
|------|-------|-------|
| 1 | CA | 1,292 |
| 2 | KY | 424 |
| 3 | NY | 400 |
| 4 | TX | 330 |
| 5 | IN | 284 |
| 6 | CT | 282 |
| 7 | NC | 266 |
| 8 | WV | 264 |
| 9 | MO | 250 |
| 10 | MI | 248 |

Full state distribution available in generated reports.

## Scope Breakdown

- **LOCAL:** 7,965 resources (97.5%)
- **NATIONAL:** 199 resources (2.4%)
- **STATE:** 3 resources (0.04%)

The overwhelming majority are local resources, making them ideal candidates for targeted web searches based on organization name + location.

## Data Files Generated

### 1. `missing_websites.csv`
**Location:** `/home/marci/projects/vibe4vets/missing_websites.csv`  
**Size:** 1.2 MB  
**Records:** 8,167 + 1 header row

**Format:**
```csv
id,title,organization,city,state,status,created_date
78a3b61e-fa24-44b8-b17a-c9211f6aa3d7,"HealthFirst Family Care Center-School-Based Health Center - Fall River, MA","HEALTHFIRST FAMILY CARE CENTER, INC.",Fall River,MA,ACTIVE,2026-01-29
```

**Columns:**
- `id` - Resource UUID (for database updates)
- `title` - Resource title/program name
- `organization` - Parent organization name
- `city` - City location
- `state` - State abbreviation (2 letters)
- `status` - Review status (ACTIVE, NEEDS_REVIEW)
- `created_date` - Date resource was added (YYYY-MM-DD)

### 2. `missing_websites_summary.json`
**Location:** `/home/marci/projects/vibe4vets/missing_websites_summary.json`

Contains JSON summary with totals and status counts.

### 3. `missing_websites_report.txt`
**Location:** `/home/marci/projects/vibe4vets/missing_websites_report.txt`

Full analysis report with all breakdown data.

## Next Steps for Web Search Phase

### Strategy
The CSV is optimized for systematic web searching:

1. **Organization + Location Search Pattern**
   ```
   "{organization}" "{city}" "{state}" website
   ```
   Example: "HEALTHFIRST FAMILY CARE CENTER" "Fall River" "MA" website

2. **Batch Processing Approach**
   - Group by state for efficiency (CA has 1,292 to process)
   - Use web search APIs (Google Custom Search, Bing, etc.)
   - Implement with confidence scoring (high/medium/low)
   - Store source URL for audit trail

3. **Validation Requirements**
   - Verify URL is active and accessible
   - Confirm organization match
   - Store HTTP status code
   - Add timestamp of discovery

### Database Update Process

Once URLs are discovered and validated:

```python
# Update Resource.website field with discovered URL
UPDATE resources
SET website = 'https://discovered-url.com'
WHERE id = '<resource-id>';

# Optionally track source of discovery
UPDATE resources
SET source_url = 'https://web-search-source.com'
WHERE id = '<resource-id>';
```

## Key Insights

1. **Employment + Healthcare Overlap:** Most resources appear in both categories (97.4-97.5%), suggesting many are multi-service centers.

2. **California Concentration:** 15.8% of all missing websites are in CA - highest priority for batch processing.

3. **Local Resource Advantage:** 97.5% are local, making them searchable via organization name + location.

4. **Fresh Data:** All entries created 2026-01-29, suggesting this is newly loaded/seeded data requiring enrichment.

5. **High Quality Opportunities:** Most are ACTIVE status (99.96%), indicating mature resources worth the effort to find URLs.

## Query Details

**SQL Query Used:**
```sql
SELECT 
  resources.id,
  resources.title,
  resources.status,
  organizations.name,
  locations.city,
  locations.state,
  resources.created_at
FROM resources
JOIN organizations ON resources.organization_id = organizations.id
LEFT OUTER JOIN locations ON resources.location_id = locations.id
WHERE resources.website IS NULL OR resources.website = ''
ORDER BY resources.created_at DESC;
```

**Database:** PostgreSQL (vibe4vets)  
**Tables:** resources, organizations, locations  
**Fields Queried:** website (filtered for NULL or empty string)

---

**Report Generated:** 2026-01-29 20:35:47 UTC
