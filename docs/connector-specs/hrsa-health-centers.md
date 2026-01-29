# HRSA Health Center Finder Connector Specification

## Overview

This document specifies the implementation requirements for a Vibe4Vets connector to the Health Resources and Services Administration (HRSA) Health Center Program data. HRSA funds ~1,400 Federally Qualified Health Centers (FQHCs) operating 16,200+ service sites nationwide, providing affordable primary care to 32.4 million patients annually, with 90% at or below 200% of the Federal Poverty Level.

**Relevance to Veterans:** While HRSA health centers serve all underserved populations, they partner with VA through the Veterans Choice Program, allowing Veterans living >40 miles from a VA facility or facing >30-day wait times to access care at HRSA-funded providers.

---

## 1. Data Source Overview

### Source Characteristics

| Property | Value |
|----------|-------|
| **Source Name** | HRSA Health Center Program |
| **Source URL** | https://data.hrsa.gov/ |
| **Tier** | 1 (Federal government source) |
| **Update Frequency** | Annual (typically available by early fall) |
| **Data Scope** | Nationwide health centers with location, services, hours |
| **Authentication** | Required (Web token via registration) |
| **Terms of Service** | https://data.hrsa.gov/about/terms-conditions |

### Data Quality

- **Data Collection:** HRSA collects Uniform Data System (UDS) data in February for the previous calendar year
- **Verification:** Rigorous cleaning and verification process before publication
- **2024 Status:** Most recent data now available
- **Historical Data:** Annual UDS snapshots available by year
- **Completeness:** Mandatory reporting for all HRSA-funded grantees and look-alikes

---

## 2. API Access Options

HRSA provides **three primary access methods**, in order of preference:

### Option 1: CSV Data Download (Recommended for MVP)

**Advantages:**
- No authentication required
- Can be downloaded directly or via bulk export
- Daily refresh
- Schema is well-documented

**Disadvantages:**
- Not real-time
- Requires periodic re-download

**Primary File:**
- URL: `https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv`
- Size: Large (~50MB+)
- Format: CSV with 50+ columns
- Update: Daily

**Access Method:**
```bash
# Download via HTTP
curl -O https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv

# Or programmatically
import requests
url = "https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv"
response = requests.get(url, stream=True)
```

### Option 2: Web Services API (SOAP/XML)

**Advantages:**
- Official API with structured authentication
- Query-based (state, county, ZIP code)
- Lower bandwidth than full CSV
- Supports geographic filtering

**Disadvantages:**
- Requires token registration
- Uses SOAP/XML (not REST/JSON)
- Registration process requires approval
- More complex implementation

**Registration:**
1. Visit: https://data.hrsa.gov/data/services
2. Complete registration form providing:
   - Two points of contact (primary and alternate)
   - Domain(s) from which API calls will be executed
   - Organization and use case
3. Receive web token for authentication

**Endpoints:** (Via registered account)
- Health Center Data Service - Query health centers by state, county, or ZIP code
- Ryan White HIV/AIDS Service - Query HIV care providers by lat/long

**Documentation:**
- Developer Guide PDF: Available after registration at data.hrsa.gov/data/services
- Support: data@hrsa.gov

### Option 3: Data Explorer UI with Manual Export

**URL:** https://data.hrsa.gov/data/data-explorer

**Use Case:** Exploratory research, validation of specific centers

**Limitations:** Not suitable for automated connector implementation

---

## 3. CSV Data Schema

### Primary Dataset: Health Center Service Delivery and Look-Alike Sites

The CSV file contains health center and look-alike organization data with 50+ columns. Key fields for Vibe4Vets mapping:

#### Organization Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `Health Center Number` | external_id | String | Unique HRSA identifier (e.g., "H80CS28972") |
| `Health Center Name` | org_name | String | Organization name |
| `FQHC Flag` | tags | Boolean | Federally Qualified Health Center designation |
| `Look-Alike Flag` | tags | Boolean | Health Center Program look-alike status |
| `Address Line 1` | address | String | Street address |
| `Address Line 2` | address | String | Suite/apt (concatenate with Line 1) |
| `City` | city | String | City name |
| `State` | state | String | 2-letter state code |
| `ZIP Code` | zip_code | String | 5-digit ZIP code |
| `ZIP+4` | N/A | String | Extended ZIP (can append for geocoding) |
| `Latitude` | location.latitude | Float | WGS84 decimal degrees |
| `Longitude` | location.longitude | Float | WGS84 decimal degrees |
| `Phone` | phone | String | Main contact phone |
| `Website` | website | String | Organization website URL |

#### Service & Hours Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `Hours of Operation` | hours | String | Typical hours (may vary by site) |
| `Services Offered` | categories/description | Array/String | Comma-separated service list |
| `Primary Care` | categories | Boolean | Maps to "healthcare" |
| `Dental` | tags | Boolean | Add "dental" tag if available |
| `Mental Health Services` | categories | Boolean | Maps to "mentalHealth" |
| `Substance Abuse Services` | categories | Boolean | Maps to "mentalHealth" |
| `Behavioral Health` | categories | Boolean | Add "mentalHealth" category |
| `Sexual Health Services` | tags | String | Add relevant tags |
| `Family Planning` | categories | Boolean | Maps to "family" |
| `Preventive Care` | tags | String | Add "preventive" tag |
| `Chronic Disease Management` | tags | String | Add tags |
| `Health Education` | tags | String | Add "education" tag |

#### Accessibility & Language Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `Languages Offered` | languages | Array | Parse comma-separated language list |
| `Medicaid Accepted` | tags | Boolean | Add "medicaid" tag |
| `Medicare Accepted` | tags | Boolean | Add "medicare" tag |
| `CHIP Accepted` | tags | Boolean | Add "chip" tag |
| `Sliding Fee Scale` | cost | String | Set to "sliding scale" |
| `Accepts Uninsured` | cost | Boolean | Note in cost field |
| `Wheelchair Accessible` | tags | Boolean | Add accessibility tag |

#### Scope & Coverage Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `Service Area Description` | description | Text | Incorporates into resource description |
| `Patients Served - Adults` | description | Boolean | Note in description |
| `Patients Served - Pediatrics` | description | Boolean | Note in description |
| `Patients Served - Geriatric` | description | Boolean | Note in description |
| `Eligible for Veterans Choice` | tags | Boolean | Add "veterans-choice" if applicable |
| `Federally Qualified` | reliability_score | Boolean | Affects trust scoring (Tier 1) |

#### Program-Specific Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `340B Drug Program` | tags | Boolean | Add if applicable |
| `Health Center Type` | subcategories | String | Site type (e.g., "Primary Care", "Look-Alike") |
| `Section 330 Grant Number` | external_id | String | Additional identifier |

#### Data Quality Fields

| CSV Column | Vibe4Vets Field | Type | Notes |
|------------|-----------------|------|-------|
| `Last Updated` | last_verified | Date | Data freshness tracking |
| `Data Last Verified` | last_verified | Date | For trust scoring |
| `Record Status` | status | String | "Active" = ACTIVE, "Closed" = INACTIVE |

### Example Record Mapping

**CSV Input:**
```
Health Center Number,Health Center Name,Address Line 1,City,State,ZIP Code,Latitude,Longitude,Phone,Website,Hours of Operation,Services Offered,Mental Health Services,Dental,Medicaid Accepted,Medicare Accepted,Sliding Fee Scale,Last Updated
H80CS28972,Community Health Clinic,123 Main St,Austin,TX,78701,30.2672,-97.7431,(512) 555-0100,https://www.commhealth.org,Mon-Fri 8AM-5PM; Sat 9AM-1PM,Primary Care;Dental;Mental Health;Preventive Care,Yes,Yes,Yes,Yes,Yes,2024-01-15
```

**Vibe4Vets ResourceCandidate:**
```python
ResourceCandidate(
    title="Community Health Clinic - Austin",
    description="Federally Qualified Health Center providing primary care, dental, mental health, and preventive services to underserved populations. 90% of patients at or below 200% Federal Poverty Level.",
    org_name="Community Health Clinic",
    source_url="https://data.hrsa.gov/",
    address="123 Main St",
    city="Austin",
    state="TX",
    zip_code="78701",
    phone="(512) 555-0100",
    website="https://www.commhealth.org",
    hours="Mon-Fri 8AM-5PM; Sat 9AM-1PM",
    categories=["healthcare", "mentalHealth", "family"],
    tags=["fqhc", "sliding-scale", "medicaid", "medicare", "dental"],
    cost="sliding scale",
    scope="local",
    states=["TX"],
    fetched_at=datetime.utcnow(),
)
```

---

## 4. Category & Tag Mapping

### Categories (Primary Classification)

Health centers should be mapped to these Vibe4Vets categories based on services offered:

| HRSA Service | Vibe4Vets Categories |
|--------------|----------------------|
| Primary Care | `healthcare` |
| Mental Health / Substance Abuse | `mentalHealth` |
| Dental | `healthcare` (tag: "dental") |
| Preventive Care | `healthcare` (tag: "preventive") |
| Sexual Health / Family Planning | `family` |
| Health Education | `education` |

**Default categories:** All HRSA health centers receive `["healthcare"]` minimum.

### Tags (Secondary Classification & Features)

```python
tags = [
    "fqhc",                    # Federally Qualified Health Center
    "look-alike",              # Look-alike program
    "primary-care",
    "dental",
    "mental-health",
    "substance-abuse",
    "sexual-health",
    "family-planning",
    "pediatric",
    "geriatric",
    "prenatal",
    "preventive",
    "sliding-scale",           # Fee structure
    "uninsured-welcome",
    "medicaid",
    "medicare",
    "chip",                    # Children's Health Insurance Program
    "340b-drug-program",
    "wheelchair-accessible",
    "veterans-choice",         # Eligible for VA Veterans Choice
    "english",
    "spanish",
    # (other languages as applicable)
]
```

---

## 5. Connector Implementation

### Base Connector Class Interface

```python
from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

class HRSAHealthCentersConnector(BaseConnector):
    """Connector for HRSA Health Center Program data."""
```

### Required Methods

#### 1. Metadata Property

```python
@property
def metadata(self) -> SourceMetadata:
    return SourceMetadata(
        name="HRSA Health Center Program",
        url="https://data.hrsa.gov/",
        tier=1,  # Federal government source
        frequency="annual",  # Primary annual update (typically August/September)
        terms_url="https://data.hrsa.gov/about/terms-conditions",
        requires_auth=False,  # CSV download requires no auth
    )
```

#### 2. Run Method

```python
def run(self) -> list[ResourceCandidate]:
    """Fetch and normalize HRSA health center data.

    Implementation options:
    1. Download full CSV (recommended for MVP)
    2. Query Web Services API (Phase 2)
    3. Hybrid: Fetch new/updated records via API, full sync via CSV
    """
```

### Implementation Strategy

#### Phase 1: CSV-Based Connector (MVP - Recommended)

**Advantages:**
- No authentication required
- Reliable and reproducible
- Comprehensive dataset
- Straightforward to implement

**Process:**
1. Download CSV from HRSA
2. Parse CSV (handle large file size efficiently)
3. Normalize each row to ResourceCandidate
4. Apply geolocation validation
5. Filter for Veteran-relevant services
6. Return normalized list

**Example Python Implementation:**

```python
import csv
import io
from datetime import datetime, UTC
import httpx
from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class HRSAHealthCentersConnector(BaseConnector):
    """HRSA Health Center Program connector - CSV-based."""

    CSV_URL = "https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv"
    TIMEOUT = 60.0

    # Service keywords that indicate Veteran-relevant services
    VETERAN_RELEVANT_SERVICES = {
        'mental health', 'behavioral health', 'substance abuse',
        'ptsd', 'counseling', 'primary care', 'preventive'
    }

    def __init__(self):
        self._client: httpx.Client | None = None

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="HRSA Health Center Program",
            url="https://data.hrsa.gov/",
            tier=1,
            frequency="annual",
            terms_url="https://data.hrsa.gov/about/terms-conditions",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Fetch and normalize health center data from HRSA CSV."""
        resources = []
        try:
            client = self._get_client()
            response = client.get(self.CSV_URL, timeout=self.TIMEOUT)
            response.raise_for_status()

            # Parse CSV from response content
            csv_text = response.text
            reader = csv.DictReader(io.StringIO(csv_text))

            for row in reader:
                candidate = self._parse_row(row)
                if candidate:
                    resources.append(candidate)

            return resources
        finally:
            self.close()

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.TIMEOUT)
        return self._client

    def _parse_row(self, row: dict) -> ResourceCandidate | None:
        """Parse CSV row to ResourceCandidate."""
        # Validate required fields
        if not row.get('Health Center Name') or not row.get('State'):
            return None

        # Extract data
        title = row.get('Health Center Name', '').strip()
        if row.get('City'):
            title = f"{title} - {row.get('City')}"

        # Build description from services
        services = row.get('Services Offered', '')
        description = (
            f"HRSA-funded Federally Qualified Health Center providing {services}. "
            f"Serves 90%+ of patients at or below 200% Federal Poverty Level."
        )

        # Determine categories and tags
        categories = ['healthcare']
        tags = ['fqhc'] if row.get('FQHC Flag') == 'Yes' else []
        tags.append('look-alike') if row.get('Look-Alike Flag') == 'Yes' else None

        if self._has_mental_health_services(row):
            categories.append('mentalHealth')
        if self._has_family_services(row):
            categories.append('family')

        # Fee structure
        cost = None
        if row.get('Sliding Fee Scale') == 'Yes':
            cost = 'sliding scale'
            tags.append('sliding-scale')

        # Insurance accepted
        if row.get('Medicaid Accepted') == 'Yes':
            tags.append('medicaid')
        if row.get('Medicare Accepted') == 'Yes':
            tags.append('medicare')

        # Languages
        languages = ['en']
        if row.get('Languages Offered'):
            # Parse comma-separated languages, add to tags
            lang_str = row.get('Languages Offered', '').lower()
            if 'spanish' in lang_str:
                languages.append('es')
                tags.append('spanish')
            # Add other languages as detected

        return ResourceCandidate(
            title=title,
            description=description,
            org_name=row.get('Health Center Name', '').strip(),
            source_url="https://data.hrsa.gov/",
            address=self._parse_address(row),
            city=row.get('City', '').strip(),
            state=self._normalize_state(row.get('State')),
            zip_code=row.get('ZIP Code', '').strip(),
            phone=self._normalize_phone(row.get('Phone')),
            website=row.get('Website'),
            hours=row.get('Hours of Operation'),
            categories=categories,
            tags=[t for t in tags if t],  # Remove None values
            cost=cost,
            scope='local',
            states=[self._normalize_state(row.get('State'))],
            fetched_at=datetime.now(UTC),
            raw_data=row,
        )

    def _parse_address(self, row: dict) -> str | None:
        """Combine address lines."""
        addr1 = row.get('Address Line 1', '').strip()
        addr2 = row.get('Address Line 2', '').strip()
        if addr1 and addr2:
            return f"{addr1}, {addr2}"
        return addr1 if addr1 else None

    def _has_mental_health_services(self, row: dict) -> bool:
        """Check if row indicates mental health services."""
        mental_health = row.get('Mental Health Services', 'No')
        behavioral = row.get('Behavioral Health', 'No')
        substance = row.get('Substance Abuse Services', 'No')
        return any(v == 'Yes' for v in [mental_health, behavioral, substance])

    def _has_family_services(self, row: dict) -> bool:
        """Check if row indicates family services."""
        return row.get('Family Planning', 'No') == 'Yes'

    def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            self._client.close()
```

#### Phase 2: Web Services API Integration (Future)

**When to Implement:**
- When incremental updates needed between annual CSV releases
- For real-time query capabilities by location
- When API registration approval obtained

**Implementation:**
```python
class HRSAWebServicesConnector(BaseConnector):
    """HRSA Health Center Program connector - SOAP Web Services API."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://data.hrsa.gov/services/..."  # From registered account

    def run(self) -> list[ResourceCandidate]:
        """Query health centers via SOAP API by state, county, ZIP."""
        # Implementation uses Web Services API
        # See registration documentation
        pass
```

---

## 6. Trust Scoring & Reliability

### Source Tier

- **Tier 1** (Score: 1.0): Official federal government source
- **Data Quality:** High - mandatory reporting, rigorous verification
- **Update Frequency:** Annual (typically August-September)

### Reliability Calculation

```python
reliability_score = 1.0  # Tier 1 federal source

# Freshness decay (example)
# Data from current year: 1.0
# Data from previous year: 0.8
# Data > 2 years old: 0.6

# Completeness factors:
# + Has verified address and phone: +0.1
# + Has website: +0.1
# + FQHC designation: +0.1
# - Missing hours of operation: -0.1
```

### Freshness Scoring

```python
# Annual refresh
# Typical data available: August/September
# Current year data (published Sep 2024): freshness = 1.0
# Previous year data (published Sep 2023): freshness = 0.8
# Older data: lower freshness scores

# Triggers human review:
# - Address changes
# - Phone number changes
# - Service offerings change significantly
```

---

## 7. Special Considerations for Veterans

### Veterans Choice Program Integration

HRSA health centers participate in the **VA Veterans Choice Program** if they:
- Are FQHC-certified
- Accept Medicaid/Medicare
- Serve geographies where Veterans have limited VA access

**How to Identify:**
1. Look for indicators in CSV (may include "Veterans Choice" flag or similar)
2. Cross-reference with VA facilities list (see VA.gov connector)
3. Filter by Medicaid/Medicare acceptance + accessible location

**Mapping:**
- Add tag: `"veterans-choice"` when applicable
- Include in description: "Eligible for VA Veterans Choice Program"
- Highlight in Vibe4Vets UI for Veterans >40 miles from VA

### Mental Health & Behavioral Services Focus

HRSA health centers often provide critical mental health services:
- Mental health counseling and treatment
- Substance use disorder services
- Trauma-informed care
- Integrated behavioral health

**Mapping Strategy:**
- Centers with mental health services → `categories: ['healthcare', 'mentalHealth']`
- Highlight these prominently in Vibe4Vets (Veterans have high mental health needs)

### Service Gaps & Eligibility

**Important Notes:**
- NOT all health centers serve all populations
- Some specialize in pediatrics, geriatrics, or specific groups
- Always verify hours and services before directing Veterans

**Vibe4Vets Best Practices:**
- Include population served in description (adults, children, seniors)
- Show hours clearly
- Direct Veterans to call ahead to confirm services
- Link to official health center website

---

## 8. Rate Limits & Performance Considerations

### CSV Download

| Limit | Value | Notes |
|-------|-------|-------|
| **File Size** | ~50-100 MB | Uncompressed CSV |
| **Records** | ~16,200+ | One row per service site |
| **Download Time** | 30-60 seconds | Over typical internet connection |
| **Rate Limit** | None documented | No authentication = no rate limiting |
| **Recommended Frequency** | Monthly or quarterly | Annual update cycle, but daily refresh available |

### Best Practices

```python
# 1. Use streaming downloads for large files
response = client.get(url, stream=True)
for chunk in response.iter_bytes():
    process_chunk(chunk)

# 2. Implement local caching
last_fetch_time = datetime.now()
if (datetime.now() - last_fetch_time).days < 30:
    use_cached_csv()  # Don't re-download if fresh

# 3. Parse incrementally to avoid memory issues
reader = csv.DictReader(file_handle)
for row in reader:  # Process one row at a time
    process_row(row)

# 4. Handle errors gracefully
try:
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    log_error(f"HRSA CSV download failed: {e}")
    # Retry with exponential backoff
```

### Update Frequency

| Schedule | Timing | Notes |
|----------|--------|-------|
| **CSV Refresh** | Daily | Full dataset re-published daily |
| **UDS Annual Data** | August-September | Previous year data finalized and published |
| **Real-time API** | N/A | Not currently available (use CSV or Web Services API) |
| **Recommended Sync** | Monthly or Quarterly | Cost-benefit: changes are relatively infrequent between annual UDS releases |

---

## 9. Data Quality & Validation

### Validation Rules

```python
def validate_resource(candidate: ResourceCandidate) -> bool:
    """Validate HRSA resource candidate."""

    # Required fields
    if not candidate.title or not candidate.org_name:
        return False

    # Address components
    if not (candidate.city and candidate.state and candidate.zip_code):
        return False

    # Geographic bounds (US only)
    if not is_valid_us_location(candidate.state):
        return False

    # Contact info
    if not (candidate.phone or candidate.website):
        return False

    # At least one category
    if not candidate.categories:
        return False

    return True
```

### Common Data Issues

| Issue | Solution |
|-------|----------|
| Incomplete addresses | Geocode or flag for manual review |
| Invalid phone numbers | Normalize and validate format |
| Missing hours | Note "Hours not available - call ahead" |
| Outdated website links | Link checker job flags for review |
| Special characters in names | Properly escape and normalize UTF-8 |
| Duplicate entries across years | Dedupe on health center number + address |

---

## 10. Example Implementation Plan

### Phase 1: MVP (Weeks 1-2)

- [ ] Create `backend/connectors/hrsa_health_centers.py`
- [ ] Implement CSV-based connector (parse, normalize, validate)
- [ ] Register in `backend/jobs/refresh.py` CONNECTOR_REGISTRY
- [ ] Write unit tests (`backend/tests/connectors/test_hrsa_health_centers.py`)
- [ ] Test with 100 sample records
- [ ] Dry-run ETL pipeline
- [ ] Document field mappings in this spec

### Phase 2: Production Deployment (Weeks 3-4)

- [ ] Full dry-run on entire dataset (~16,200 records)
- [ ] Verify geocoding accuracy for edge cases
- [ ] Test deduplication logic (handle multiple sites per org)
- [ ] Run against staging database
- [ ] Deploy to production
- [ ] Monitor first sync for errors/warnings
- [ ] Set up scheduled job (monthly or quarterly refresh)

### Phase 3: Web Services API (Phase 2+)

- [ ] Register for HRSA Web Services token
- [ ] Implement `HRSAWebServicesConnector` class
- [ ] Support state/county/ZIP code queries
- [ ] Implement incremental sync
- [ ] Cache API responses

### Phase 4: Veteran-Specific Enhancements (Phase 3)

- [ ] Cross-reference with VA facilities (Veterans Choice eligibility)
- [ ] Add Veteran-specific filtering in UI
- [ ] Highlight mental health services
- [ ] Add behavioral health search filters

---

## 11. Helpful Resources

### Official HRSA Documentation

- **Main Portal:** https://data.hrsa.gov/
- **Health Centers Topic:** https://data.hrsa.gov/topics/health-centers
- **Data Downloads:** https://data.hrsa.gov/data/download
- **Data Explorer:** https://data.hrsa.gov/data/data-explorer
- **Web Services Registration:** https://data.hrsa.gov/data/services
- **Find a Health Center (UI):** https://findahealthcenter.hrsa.gov/
- **GeoCare Navigator:** https://geocarenavigator.hrsa.gov/
- **Bureau of Primary Health Care:** https://bphc.hrsa.gov/

### UDS & Program Documentation

- **UDS 2024 Manual:** https://bphc.hrsa.gov/sites/default/files/bphc/data-reporting/2024-uds-manual.pdf
- **Health Center Program Overview:** https://bphc.hrsa.gov/about-health-center-program
- **Eligibility Requirements:** https://bphc.hrsa.gov/compliance/compliance-manual/chapter1

### Related Vibe4Vets Connectors

- **VA Facilities:** `backend/connectors/va_gov.py` (reference for trust scoring)
- **Veterans Choice Program:** Check for cross-reference opportunities
- **Mental Health Services:** Leverage HRSA behavioral health data

### Support

- **HRSA Support Email:** data@hrsa.gov
- **Developer Guide:** Available after Web Services API registration

---

## 12. FAQ

**Q: Should we use CSV or Web Services API?**
A: Start with CSV for MVP (no auth needed, comprehensive data). Upgrade to Web Services API later if real-time capabilities needed.

**Q: How do we handle the large file size?**
A: Stream the CSV, parse one row at a time, don't load entire file into memory.

**Q: Are all health centers Veterans-relevant?**
A: Potentially - especially those with mental health services or those participating in Veterans Choice. But some specialize in pediatrics/other populations.

**Q: How often should we refresh the data?**
A: CSV updates daily, but meaningful changes occur annually. Monthly or quarterly refresh recommended.

**Q: Can we extract Veterans-specific indicators?**
A: Partially - look for Veterans Choice eligibility, mental health services, Medicaid/Medicare acceptance. Full indicator may require cross-referencing with VA data.

**Q: What's the data license?**
A: Public domain (federal government data). See https://data.hrsa.gov/about/terms-conditions

---

## Appendix: Sample API Calls

### CSV Download (cURL)

```bash
# Simple download
curl -O https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv

# With progress and timeout
curl --progress-bar \
     --max-time 120 \
     -O https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv
```

### CSV Download (Python)

```python
import requests
import csv
import io

url = "https://data.hrsa.gov/DataDownload/DD_Files/Health_Center_Service_Delivery_and_LookAlike_Sites.csv"

response = requests.get(url, stream=True, timeout=60)
response.raise_for_status()

# Parse streaming response
lines = response.iter_lines(decode_unicode=True)
reader = csv.DictReader(lines)

count = 0
for row in reader:
    # Process each row
    print(f"Processing {row['Health Center Name']}")
    count += 1
    if count >= 10:  # Limit for testing
        break
```

### Web Services API Call (After Registration)

```python
import requests
from zeep import Client as SoapClient

# (Example - requires actual endpoint URL and token)
# Would use SOAP/XML to query by state, county, or ZIP

# Pseudo-code for Web Services API
wsdl = "https://data.hrsa.gov/services/... (from registration)"
client = SoapClient(wsdl=wsdl)

# Example query (actual parameters depend on registered API)
result = client.service.GetHealthCenters(
    token="your_registered_token",
    state="TX",
    limit=100,
)
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-28
**Status:** Ready for Implementation
