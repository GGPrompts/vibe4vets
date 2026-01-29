# 211.org / United Way API Integration Guide

**Status:** Research Complete
**Last Updated:** 2026-01-28
**Scope:** Vibe4Vets connector implementation for 211 National Data Platform

---

## Executive Summary

The 211 National Data Platform (NDP), managed by United Way Worldwide, provides access to community social and human service data across all 50 states and U.S. territories through standardized APIs. The platform currently aggregates resources from local 211 call centers using the **Open Referral Human Services Data Specification (HSDS)** standard.

**Key Finding:** API access is available through the 211 NDP, but individual state/local 211 organizations control authorization. We recommend starting with pilot states that have:
1. Highest Veteran populations (Texas, California, Florida, North Carolina, Georgia)
2. Proven API integrations (California, Colorado, Utah, San Diego)
3. Existing Veteran service programs (Nebraska, Iowa)

---

## 211 National Data Platform Overview

### Architecture

```
211 National Data Platform (United Way Worldwide)
│
├─ Search API          (keyword/guided search)
├─ Export API          (bulk data export)
├─ Resource API        (current placeholder)
│
└─ Local 211 Centers (50+ jurisdictions)
   ├─ VisionLink       (auto API integration)
   ├─ iCarol           (manual/scheduled export)
   ├─ OneDegree        (auto API integration)
   ├─ 211 San Diego    (auto API integration)
   └─ Custom Systems   (varies by state)
```

### Developer Portal

- **URL:** https://register.211.org/ and https://apiportal.211.org/
- **Status:** Production-ready
- **Documentation:** Publicly accessible
- **Support:** Contact through support ticket system on register.211.org

---

## API Access Tiers & Authentication

### Public Access (No Registration Required)

- View basic API documentation
- Browse available endpoints
- Access sample code and tools

### Developer Trial Access

- **Requirements:** Sign up for developer account on https://apiportal.211.org/
- **Authentication:** Username/password for external developers
- **Data Access:** Limited dataset for development/testing
- **Cost:** Free during trial period
- **Ideal For:** Proof of concept and connector development

### Production Access

- **Requirements:** Data sharing agreement with individual 211 organization
- **Authentication:**
  - 211 staff: Microsoft OAuth
  - External partners: Username/password + API key
- **Data Access:** Full dataset per 211's authorization
- **Cost:**
  - No cost to share data to platform
  - No cost for 211 internal use
  - Revenue-sharing: 5% if NDP generates revenue from data
- **Process:**
  1. Contact local 211 organization (state/county level)
  2. Complete API Request Form
  3. Sign data sharing agreement with United Way Worldwide
  4. Receive authorization keys and credentials

### Authentication Methods

| User Type | Method | Portal |
|-----------|--------|--------|
| 211 staff/organizations | Microsoft Azure AD | Developer Portal |
| External developers | Username/Password | API Management Portal |
| Automated connectors | API Key | Direct REST calls |

---

## Data Security & Compliance

### Transport Security
- **Protocol:** SSL/TLS encrypted
- **Key Size:** 2048-bit RSA encryption
- **Data Integrity:** HTTPS only

### Data at Rest
- **Encryption:** 256-bit AES encryption
- **Access Control:** Role-based access control (RBAC)
- **Authentication:** Strong password policies + optional MFA

### Data Sharing Agreement

All partners must execute a standard **Data Sharing Agreement** that:
- Defines data ownership (remains with individual 211)
- Specifies permitted uses
- Establishes compliance obligations
- Includes breach notification procedures
- Details revenue sharing (if applicable)

**Contact:** For agreement templates and requirements, see contact points below.

---

## Open Referral HSDS Standard

### Overview

**HSDS** is a machine-readable standard for publishing human services data developed by the Open Referral Initiative. All 211 NDP data conforms to HSDS v2.0.1 or v3.0+.

### Specification Resources

- **Official Docs:** https://docs.openreferral.org/en/v2.0.1/hsds/
- **GitHub:** https://github.com/openreferral/specification
- **API Spec:** https://openreferral.github.io/api-specification/
- **Data Transformer:** https://github.com/openreferral/hsds-transformer

### Core Entities

HSDS data model includes:

| Entity | Description | Example |
|--------|-------------|---------|
| **Organization** | Parent entity providing services | VA Regional Office, United Way |
| **Location** | Physical address with geocoding | Office at 123 Main St, Austin TX |
| **Service** | Program/offering at a location | Job training, counseling |
| **Service Area** | Geographic coverage | Statewide, multi-county |
| **Contact** | Email, phone, website | 211 hotline number |
| **Eligibility** | Participant requirements | Must be Veteran, age 18+ |
| **Taxonomy** | Service classification system | Employment > Job Training |

### Flexible Taxonomy

**Important:** HSDS does NOT prescribe a specific taxonomy for service types. Instead:

- Each 211 can use their own taxonomy (often via their vendor system)
- Common taxonomies:
  - **Open Eligibility** (default open source taxonomy)
  - **211 HSIS** (Human Services Indexing System) - subscription required
  - Custom local taxonomies

**Veteran Services in Taxonomy:** No dedicated "Veteran" taxonomy exists in base HSDS. Services are identified as Veteran-focused through:
- Eligibility fields (e.g., `eligibility: "Veteran status required"`)
- Service description text (searchable)
- Organization attributes (e.g., VSO, DAV, VFW flag)
- Custom taxonomy tags

### 211HSIS (Human Services Indexing System)

The 211 Taxonomy has migrated to **211HSIS** (subscription-based):
- **Website:** https://211hsis.org
- **Contact:** 211hsis@211la.org (for access inquiries)
- **Status:** Legacy 211taxonomy.org sunset August 2024
- **Includes:** Hierarchical service categories, Veteran services codes
- **Format:** XML/JSON download available to licensees

---

## States with Confirmed API Access

### Tier 1: Automated API Integration

These states have direct API connections to the NDP (real-time data sync):

| State | 211 Organization | System | Contact | Veteran Pop |
|-------|-----------------|--------|---------|-------------|
| **California** | 211 California | VisionLink + OneDegree | https://211ca.org | ~1.5M |
| **Colorado** | 211 Colorado | Custom NDP API | register.211.org | ~350K |
| **Utah** | 211 Utah | Custom NDP API | register.211.org | ~110K |
| **San Diego County** | 211 San Diego | Custom API | register.211.org | (CA subset) |

### Tier 2: Manual/Scheduled Export

These states contribute data via scheduled file exports (near real-time):

| State | 211 Organization | System | Export Frequency | Veteran Pop |
|-------|-----------------|--------|------------------|-------------|
| **Texas** | Multiple regional 211s | iCarol / VisionLink | Daily/Weekly | ~1.5M |
| **Florida** | Multiple regional 211s | iCarol / VisionLink | Daily/Weekly | ~1.2M |
| **North Carolina** | 211 North Carolina | iCarol | Daily/Weekly | ~650K |
| **Georgia** | 211 Georgia | iCarol / VisionLink | Daily/Weekly | ~650K |
| **Virginia** | 211 Virginia | RTZ Systems | Daily/Weekly | ~600K |
| **Pennsylvania** | PA 211 | iCarol | Daily/Weekly | ~750K |
| **New York** | NY 211s (regional) | Various | Daily/Weekly | ~800K |
| **Louisiana** | Louisiana 211 | iCarol | Daily/Weekly | ~300K |
| **Maryland** | 211 Maryland | iCarol / VisionLink | Daily/Weekly | ~380K |
| **Wisconsin** | Multiple 211s | Various | Daily/Weekly | ~350K |
| **Nebraska** | Nebraska 211 | iCarol | Daily/Weekly | ~120K |
| **Iowa** | Iowa 211 | iCarol | Daily/Weekly | ~190K |

### Tier 3: National Data Platform (All States)

All states are represented through the 211 NDP with varying data completeness:

- **Full participation:** 50+ state/local 211 centers
- **Search API:** Available for all registered developers
- **Export API:** Available for authorized partners
- **Data freshness:** Varies by local 211 (daily to quarterly)

---

## Data Contribution Methods

### Method 1: Direct API Connection (Fastest)

**Used By:** VisionLink, OneDegree, 211 San Diego, custom integrations

**Process:**
1. 211 maps their data model to HSDS
2. Data vendor implements HSDS API endpoint
3. NDP pulls data automatically on schedule
4. Real-time or near-real-time sync (hourly to daily)

**Advantages:**
- Most current data
- Automated, no manual steps
- 2-way sync possible
- Best for high-volume/frequent updates

**Lead Time:** 4-8 weeks typical for API setup

---

### Method 2: Scheduled Export (Moderate Effort)

**Used By:** iCarol (primary), most 211 organizations

**Process:**
1. 211 extracts data from their system in HSDS format
2. File exported to SFTP or uploaded manually
3. NDP imports and validates
4. Export runs on schedule (daily/weekly)

**Advantages:**
- Works with any system
- Predictable update cycles
- Lower technical overhead
- Supported for legacy systems

**Cadence Options:**
- Daily (0100 UTC typical)
- Weekly (Sunday night)
- Manual on-demand

**Lead Time:** 2-4 weeks typical

---

### Method 3: Manual Bulk Upload

**Used By:** Small 211s, pilot projects

**Process:**
1. 211 creates CSV/JSON export
2. Manual upload to register.211.org
3. NDP validates and processes
4. Repeat as needed

**Advantages:**
- No technical setup required
- Good for testing
- Works immediately

**Disadvantages:**
- Not scalable for regular updates
- Manual effort required
- Not suitable for production

---

## API Endpoints (National Data Platform)

### Search API

**Purpose:** Keyword search across all participating 211s

```
GET /api/v1/search
Parameters:
  - query: string (required)
  - location: string (city, zip, state)
  - category: string (employment, housing, etc.)
  - limit: integer (default: 20)
  - offset: integer (pagination)
```

**Response:** Organizations, locations, services matching query

**Authentication:** API key (developer portal)

**Rate Limit:** Varies by tier (typically 100 req/min for trial)

### Export API

**Purpose:** Bulk data export for integration

```
GET /api/v1/export
Parameters:
  - state: string (e.g., "TX", "CA")
  - category: string (optional filter)
  - format: enum (json, csv)
```

**Response:** Complete HSDS datapackage (json or csv files)

**Authentication:** API key + authorization from state 211

**Rate Limit:** 1 request per hour (to prevent abuse)

---

## Recommended Pilot States

### Tier A: Highest Priority (Immediate)

| State | Reason | Veteran Pop | API Status | Contact |
|-------|--------|-------------|-----------|---------|
| **California** | Largest API-connected state, high Vet pop, proven integrations | 1.5M | ✅ API | https://211ca.org |
| **Texas** | Largest Vet population, multiple 211s, export-capable | 1.5M | ⚡ Export | Contact regional 211s |
| **Florida** | 2nd largest Vet pop, export-capable, strong military ties | 1.2M | ⚡ Export | https://floridavets.org |

### Tier B: Strategic (Phase 2)

| State | Reason | Veteran Pop | API Status | Contact |
|-------|--------|-------------|-----------|---------|
| **North Carolina** | NDP pilot participant, military installations | 650K | ⚡ Export | register.211.org |
| **Georgia** | Significant military presence, API-capable systems | 650K | ⚡ Export | register.211.org |
| **Virginia** | High Vet pop, integrated with NDP | 600K | ⚡ Export | register.211.org |
| **Pennsylvania** | Large Vet pop, export-capable | 750K | ⚡ Export | https://www.pa211.org |

### Tier C: Military-Focused (Partnership)

| State | Reason | Veteran Pop | API Status | Contact |
|-------|--------|-------------|-----------|---------|
| **Nebraska** | Military & Family Helpline partnership model | 120K | ⚡ Export | uwm211.org |
| **Iowa** | Military & Family Helpline partnership model | 190K | ⚡ Export | uwm211.org |
| **Colorado** | Custom API, smaller Vet pop | 350K | ✅ API | register.211.org |

---

## Contact Points for Data Partnerships

### National Level

**United Way Worldwide - 211 National Data Platform**
- **Portal:** https://register.211.org/
- **Developer Portal:** https://apiportal.211.org/
- **Support Ticket:** Create issue at register.211.org/support
- **Email for partnerships:** (Use support portal)
- **Data Sharing Agreement:** Available in 211 Toolkit at register.211.org

### State-Level 211 Organizations

#### California
- **Website:** https://211ca.org/
- **Data Inquiry:** info@211ca.org
- **API Status:** Fully connected via VisionLink/OneDegree
- **Notes:** Covers 211 San Diego, 211 Los Angeles, 211 San Francisco Bay, statewide

#### Texas
- **Structure:** Multiple regional 211s (no single state entity)
- **Major Centers:**
  - 211 San Antonio: https://www.uwsatx.org/resources/individuals/2-1-1/
  - 211 Houston: Contact via local United Way
  - 211 Dallas: Contact via local United Way
- **Data Inquiry:** Contact regional United Way office
- **Notes:** Each region manages independently; coordinate through NDP

#### Florida
- **Website:** Multiple regional 211s; no single state portal
- **Resources:**
  - Florida Veterans Support Line: https://www.unitedwaynwfl.org/veteran
  - Mission United: https://www.hfuw.org/get-help/veterans-assistance/
- **Data Inquiry:** Contact regional United Way office
- **Notes:** Coordinate through Florida 211 network

#### Louisiana
- **Website:** https://www.louisiana211.org/
- **Data Inquiry:** Contact form at louisiana211.org
- **Data Available:** Statewide contacts dataset
- **Notes:** Good starting point for pilot

#### Maryland
- **Website:** https://211md.org/
- **Contact:** https://211md.org/contact-us/
- **Data Inquiry:** Available through contact form
- **Services:** Food, housing, mental health, Veteran services

#### Pennsylvania
- **Website:** https://www.pa211.org/
- **Contact:** https://www.pa211.org/help-contacting-pa211/
- **Data Inquiry:** Use contact form for API/data inquiries
- **Notes:** iCarol-based, export-capable

#### Nebraska / Iowa
- **Program:** Military and Family Helpline
- **Website:** https://uwm211.org/militaryfamilyhelpline/
- **Contact:** uwm211.org
- **Model:** Offutt Air Force Base partnership (June 2024)
- **Value:** Proven military Veteran integration

#### 211 Colorado & 211 Utah
- **Status:** Custom NDP API implementations
- **Portal:** register.211.org (no separate websites)
- **Contact:** Through NDP support

---

## Veteran Services Taxonomy & Codes

### 211HSIS (Recommended)

The 211 Human Services Indexing System (HSIS) is the primary taxonomy for 211 organizations:

**URL:** https://211hsis.org
**Contact:** 211hsis@211la.org
**Status:** Subscription-based (moved from legacy 211taxonomy.org)

**Common Veteran Service Categories:**
- Military/Veteran Services (top-level)
  - Veteran Support Services
  - Military/Veteran Employment
  - Veteran Benefits/Eligibility
  - Veteran Housing
  - Military/Veteran Health Services
  - Veteran Crisis/Mental Health
  - Veteran Peer Support/Social Services

**Access:** Requires subscription; XML/JSON formats available

### Open Eligibility (Open Source Alternative)

**URL:** https://openeligibility.org/
**Status:** Free, community-driven taxonomy

**Relevant Categories:**
- Employment & Jobs
  - Job Training & Counseling
  - Veterans Employment Programs
- Housing & Shelter
  - Emergency Shelter
  - Supportive Housing
  - Housing Assistance
- Legal Services
  - Legal Aid
  - Veterans Benefits Appeals
- Healthcare
  - Mental Health Services
  - Counseling/Crisis Services

---

## Implementation Roadmap

### Phase 1: Setup & Authorization (Weeks 1-2)

**Actions:**
1. Register developer account on https://apiportal.211.org/
2. Subscribe to Trial product (free)
3. Review API documentation and sample code
4. Build connector skeleton using Search API
5. Test against trial data

**Deliverable:** Working connector against NDP Search API (read-only)

---

### Phase 2: State Partnerships (Weeks 3-6)

**Actions (for each pilot state):**
1. Identify primary 211 organization contact (see Contact Points)
2. Request API/export access
3. Complete API Request Form
4. Sign Data Sharing Agreement
5. Receive authentication credentials

**States to Contact (in order):**
1. California (https://211ca.org/) - fastest path to API
2. Texas (regional 211s) - largest Vet population
3. Louisiana (https://louisiana211.org/) - smallest lift for initial export
4. Florida (regional 211s) - strategic Vet concentration

**Deliverable:** Authorized access to 4 state 211s

---

### Phase 3: Connector Development (Weeks 7-12)

**Actions:**
1. Implement state-specific connector class for each approved 211
2. Map 211 HSDS data to Vibe4Vets Resource schema
3. Handle eligibility field parsing (extract Veteran flags)
4. Implement service category mapping to Vibe4Vets taxonomy
5. Add geolocation parsing and validation
6. Write connector tests with sample data

**Deliverable:** 4 working connectors (CA, TX, LA, FL)

---

### Phase 4: Production Deployment (Week 13+)

**Actions:**
1. Deploy connectors to production scheduler
2. Configure refresh schedule (daily/weekly per 211 cadence)
3. Set up health monitoring and alerts
4. Monitor data quality and update freshness
5. Handle partnership agreement renewals
6. Add additional states incrementally

**Deliverable:** Live 211 data in Vibe4Vets resource database

---

## Connector Implementation Notes

### Data Mapping: 211 HSDS → Vibe4Vets

| HSDS Field | Vibe4Vets Field | Notes |
|-----------|-----------------|-------|
| `organization.name` | `resource.title` | - |
| `location.address` | `resource.address` | Parse street, city, state, zip |
| `location.latitude` + `longitude` | `location.geo_point` | May need geocoding if missing |
| `contact.phone` | `resource.phone` | Normalize format |
| `contact.website` | `resource.url` | - |
| `service.description` | `resource.description` | - |
| `service.eligibility` | `resource.eligibility` + infer Veteran flag | Parse for "Veteran", "military" keywords |
| `organization.description` | Identify source org type | VSO, government, nonprofit, etc. |
| `taxonomy_term.name` | `resource.categories` | Map to Vibe4Vets categories (employment, housing, legal, etc.) |

### Extracting Veteran Intent

Since HSDS doesn't have a Veteran flag, use:

```python
def is_veteran_service(service_data):
    keywords = [
        "veteran", "military", "armed forces", "service member",
        "active duty", "reserve", "guard", "discharge",
        "vet center", "VSO", "DAV", "VFW", "American Legion"
    ]

    searchable_text = " ".join([
        service_data.get("description", ""),
        service_data.get("eligibility", ""),
        service_data.get("organization", {}).get("description", ""),
    ]).lower()

    return any(kw in searchable_text for kw in keywords)
```

### Sample Connector Structure

```python
# backend/connectors/211_connector.py

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata
from app.models.resource import Category
import requests

class TwoOneOneConnector(BaseConnector):
    """National 211 Data Platform connector (United Way)"""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="211 - United Way Nationwide",
            url="https://211.org",
            tier=4,  # Community directory tier
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        candidates = []

        # Search API for Veteran services
        results = self._search_api("veteran")

        for org in results:
            candidate = self._normalize_org(org)
            if candidate:
                candidates.append(candidate)

        return candidates

    def _search_api(self, query):
        """Query 211 Search API"""
        headers = {"X-API-Key": self.config["api_key"]}
        params = {
            "query": query,
            "limit": 1000,
        }

        resp = requests.get(
            "https://api.211.org/search",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def _normalize_org(self, org_data) -> ResourceCandidate | None:
        """Convert HSDS org to ResourceCandidate"""
        # Implementation: map HSDS to ResourceCandidate
        pass
```

---

## Known Limitations & Considerations

### Data Quality Issues

1. **Incomplete Addresses:** Many records missing zip codes; geocoding needed
2. **Missing Eligibility:** Not all services specify Veteran eligibility; keyword-based detection has false positives
3. **Outdated Contacts:** Phone numbers and emails sometimes stale; verify before use
4. **Duplicate Organizations:** Same org appears in multiple 211s with variations in naming
5. **Service Scope Ambiguity:** "Serves Veteran services" doesn't always mean Veteran-exclusive

### Coverage Gaps

- **Rural Areas:** Less represented in 211 data; focus on urban centers
- **Native American Services:** Often under-represented
- **Prison/Reentry Services:** Limited availability in some states
- **Specialized Niches:** Transgender Veteran services, women Veteran focus, often sparse

### Performance Considerations

- **Large Exports:** California and Texas exports can be 10K+ records; implement pagination
- **Real-time Sync:** If using API, implement backoff/retry logic
- **Deduplication:** Use title fuzzy matching (85%+ threshold) when merging across multiple 211 sources
- **Freshness:** Some 211s update quarterly; document last-updated date per source

---

## Alternative/Complementary Data Sources

While building 211 connector, also consider:

| Source | Type | Veteran Focus | API | Contact |
|--------|------|---------------|-----|---------|
| **VA.gov Facilities** | Official | ✅ High | ✅ Yes | developer.va.gov |
| **CareerOneStop** | Job services | ✅ High | ✅ Yes | careeronestop.org/Developers |
| **HUD-VASH** | Housing | ✅ High | ✅ CSV | hud.gov |
| **SSVF** | Housing | ✅ High | ✅ CSV | hud.gov |
| **Legal Aid** | Legal services | ⚠️ Some | ✅ CSV | lawhelp.org |
| **Vet Centers** | Mental health | ✅ High | ✅ API | va.gov |

**Note:** VA.gov and VA Lighthouse APIs (Tier 1) should remain primary sources. Use 211 as complementary layer for community programs and local nonprofits.

---

## References & Resources

### Official Documentation

- [211 National Data Platform](https://register.211.org/)
- [API Developer Portal](https://apiportal.211.org/)
- [Open Referral HSDS Specification v2.0.1](https://docs.openreferral.org/en/v2.0.1/hsds/)
- [Open Referral API Specification](https://openreferral.github.io/api-specification/)
- [211HSIS (Taxonomy)](https://211hsis.org)

### United Way Resources

- [211 National Impact](https://www.unitedway.org/our-impact/community-resiliency/211-connecting-people-to-local-resources)
- [Military & Family Helpline](https://uwm211.org/militaryfamilyhelpline/)
- [Data Sharing Agreement Templates](https://register.211.org/Home/Toolkit)

### Implementation Guides

- [iCarol 211 Solutions](https://www.icarol.com/solutions-by-industry/211-software/)
- [VisionLink 211 Platform](https://www.visionlink.org/211/)
- [OneDegree API Integration](https://onedegree.org/)

### Veteran Population Data

- [VA Veteran Statistics by State](https://www.va.gov/vetdata/veteran_population.asp)
- [Statista Veteran Population by State 2022](https://www.statista.com/statistics/250329/number-of-us-veterans-by-state/)

---

## Questions & Next Steps

### For Vibe4Vets Development Team

1. **API Key Management:** How will we securely store individual state 211 API keys and credentials?
2. **Freshness Strategy:** Given varying update cadences (daily vs. quarterly), how should we weight 211 trust scores?
3. **Deduplication:** How aggressively should we merge 211 records that also appear in VA.gov data?
4. **Eligibility Parsing:** Should we build a more sophisticated NLP model for detecting Veteran eligibility?
5. **User Feedback:** Should we tag resources as "via 211" to help Veterans distinguish local community programs from official VA resources?

### For Business/Partnerships

1. **State Contact Strategy:** Begin with California (API-ready) or Louisiana (lowest barrier to entry)?
2. **Timeline:** How many states can we realistically onboard in Phase 1?
3. **Data Attribution:** How will we credit individual 211 organizations in the UI?
4. **Sustainability:** Which states offer the best long-term partnership potential?

---

## Appendix: State 211 Contact Summary

```
Quick reference table for partnership outreach:

IMMEDIATE (API-Ready):
  □ California    → https://211ca.org → info@211ca.org
  □ Colorado      → register.211.org  → Support ticket
  □ Utah          → register.211.org  → Support ticket

PRIORITY (Export-Ready, High Vet Pop):
  □ Texas         → Contact regional United Way + NDP
  □ Florida       → Contact regional United Way + NDP
  □ Louisiana     → https://louisiana211.org
  □ Pennsylvania  → https://www.pa211.org
  □ North Carolina→ register.211.org  → Support ticket

STRATEGIC (Military Programs):
  □ Nebraska      → https://uwm211.org (Military Family Helpline)
  □ Iowa          → https://uwm211.org (Military Family Helpline)

All states: Start with https://register.211.org/Home/FAQs
Contact: Support form at register.211.org
```
