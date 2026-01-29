# Feeding America Food Bank Connector Specification

**Last Updated:** 2026-01-28
**Status:** RESEARCH COMPLETE - Ready for Implementation
**Tier:** 2 (Trusted Nonprofit Network)
**Category:** `food` (and potentially `supportServices`)

---

## Overview

Feeding America operates a network of 200+ member food banks across the United States. This specification documents multiple approaches to integrate food bank and food pantry data into Vibe4Vets, prioritized by reliability and legal/ethical compliance.

**Key Data Points:**
- Food bank locations (name, address, phone, website)
- Service coverage areas (states, counties, ZIP codes)
- Hours of operation
- Services offered (emergency food, meal programs, etc.)
- Contact information

---

## Implementation Priority

### 🟢 RECOMMENDED: Official SOAP Web Service (Tier 1)

**Status:** Publicly available, official API
**URL:** `http://ws.feedingamerica.org/FAWebService.asmx`

#### Endpoint Details

**Method:** SOAP/XML Web Service
**Base URL:** `http://ws.feedingamerica.org/FAWebService.asmx`

**Available Method:**
- `GetAllOrganizations` - Returns all food bank organizations in the Feeding America network

#### Request Format

**SOAP Request Example:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetAllOrganizations xmlns="http://ws.feedingamerica.org/">
    </GetAllOrganizations>
  </soap:Body>
</soap:Envelope>
```

**HTTP Details:**
- **Method:** POST
- **Content-Type:** `application/soap+xml; charset=utf-8`
- **Accept:** `application/xml` or `text/xml`

#### Response Format

**Response Type:** XML (SOAP Envelope)

**Response Structure:**
```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetAllOrganizationsResponse xmlns="http://ws.feedingamerica.org/">
      <GetAllOrganizationsResult>
        <Organization>
          <OrganizationID>12345</OrganizationID>
          <Name>Food Bank Name</Name>
          <StateAbbreviation>TX</StateAbbreviation>
          <Region>5</Region>
          <!-- Additional fields -->
        </Organization>
        <!-- More organizations -->
      </GetAllOrganizationsResult>
    </GetAllOrganizationsResponse>
  </soap:Body>
</soap:Envelope>
```

**Key Fields Returned:**
- `OrganizationID` - Unique identifier
- `Name` - Food bank name
- `StateAbbreviation` - Two-letter state code
- `Region` - Feeding America region number
- Additional program/service data

**Response Size:** ~50-100 KB (for full network dataset)

#### Rate Limiting

**Status:** Not documented publicly

**Assumptions:**
- No explicit rate limiting mentioned in available documentation
- Standard SOAP service practices suggest reasonable usage is acceptable
- Recommend: 1 call per daily refresh job cycle

#### Error Handling

**HTTP Status Codes:**
- `200 OK` - Successful request
- `500 Internal Server Error` - SOAP fault (malformed request, service error)

**SOAP Faults:** Check `<soap:Fault>` element in response

---

### 🟡 ALTERNATIVE: Feeding America Data Commons (Tier 1.5)

**Status:** New initiative, officially supported
**URL:** https://datacommons.feedingamerica.org

#### Overview

Feeding America Data Commons is a partnership with Google to provide open access to food security data and food bank locator information. Uses publicly accessible tools rather than direct API calls.

**Advantages:**
- Official partnership with Google
- Transparent data sourcing
- Publicly documented
- Free for non-commercial use

**Limitations:**
- May not be structured for programmatic bulk access
- Primarily designed for visualization/exploration
- Developer API not explicitly documented

#### Data Available

From Map the Meal Gap study and food bank network data:
- Food insecurity statistics by region
- Food bank locations
- Service area coverage
- Program information

#### Access Methods

**Interactive:** https://datacommons.feedingamerica.org
**Python Client Library:** [Google Data Commons Python client](https://developers.googleblog.com/en/pythondatacommons/)

#### Contact for Developer Access

**Email:** Check partnership inquiry form at https://www.feedingamerica.org/ways-to-give/corporate-and-foundations/partnership-inquiry

---

### 🟠 COMMUNITY: FreshTrak API (Tier 2)

**Status:** Regional food bank initiative
**URL:** https://github.com/feedingamerica/freshtrak-public
**Primary Users:** Mid-Ohio Foodbank, Can't Stop Columbus partnership

#### Overview

FreshTrak is a public API built as a partnership between Feeding America and regional food banks. Provides access to food pantry and service location data.

**Advantages:**
- Community-developed and maintained
- Open source on GitHub
- Real-world use case validation

**Limitations:**
- Only covers participating regional food banks
- May have institutional rate limiting
- Documentation limited to GitHub repository

#### Endpoints

**Repository:** https://github.com/feedingamerica/freshtrak-public
**API Flavor:** Ruby on Rails/Jets

**Key Repositories:**
- `freshtrak-pantry-finder-api` - Pantry search API
- `freshtrak-registration-api` - Pre-registration endpoints
- `freshtrak-infrastructure` - Deployment configuration

#### Contact

Create issue on GitHub repository or contact Mid-Ohio Foodbank

---

### 🔴 NOT RECOMMENDED: Web Scraping UI

**Status:** Fragile, legal risk
**URL:** https://www.feedingamerica.org/find-your-local-foodbank

#### Why Not Recommended

1. **UI-Dependent:** Uses client-side JavaScript for search, not a stable API
2. **Legal Risk:** Terms of service may prohibit automated access
3. **Maintenance Burden:** Layout changes break scraping logic
4. **Ethical Concerns:** Even public data scraping should respect ToS
5. **Unreliable:** JavaScript rendering requires headless browser

#### Frontend Architecture

- Zip code input form: `find-fb-search-form-zip`
- Dynamic results rendering (client-side)
- State-based filtering
- Backend API calls hidden in JavaScript bundles

**If investigating further:** Use browser DevTools Network tab to capture actual API calls during manual search

---

## Rate Limiting & Legal Considerations

### Rate Limiting

| Source | Documented Limit | Recommended Practice |
|--------|------------------|----------------------|
| SOAP Web Service | Not documented | 1 call/day refresh cycle |
| Data Commons | Not documented | Respect Google API limits (if used via Python client) |
| FreshTrak | Not documented | Check GitHub repo documentation |

### Terms of Service

**Feeding America Official Policy:**
- Privacy policy focuses on protecting supporter/donor information
- No explicit public ToS found restricting API access
- SOAP endpoint appears to be officially supported (public WSDL)

**Best Practice:**
1. Use official SOAP service - explicitly public endpoint
2. Document your intended use (educational, resource directory)
3. Contact Feeding America if planning high-volume access:
   - **Main Contact:** https://www.feedingamerica.org/contact
   - **Partnership Inquiry:** https://www.feedingamerica.org/ways-to-give/corporate-and-foundations/partnership-inquiry

### Responsible Access Guidelines

1. **Rate Limiting:** 1-2 refreshes per day maximum
2. **Caching:** Cache responses for 24 hours before re-fetching
3. **User-Agent:** Identify your service in HTTP headers
   ```python
   headers = {
       'User-Agent': 'Vibe4Vets/1.0 (Veteran Resource Directory; +https://vibe4vets.org)'
   }
   ```
4. **Error Handling:** Gracefully handle timeouts/failures without retry storms
5. **Data Attribution:** Always credit Feeding America as data source

---

## XML Feed Alternative (Legacy/Reference)

**URL:** `http://ws.feedingamerica.org/FAWebService.asmx/GetAllOrganizations`

**Note:** Direct URL access to the SOAP method may work but SOAP protocol is more stable.

**Community Project Reference:** https://github.com/apfister/feeding-america-foodbank-xml2geojson demonstrates converting this data to GeoJSON format.

---

## Implementation Roadmap

### Phase 1: SOAP Integration (Immediate)

**File:** `backend/connectors/feeding_america.py`

```python
from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

class FeedingAmericaConnector(BaseConnector):
    """Feeding America SOAP food bank locator connector"""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Feeding America",
            url="https://www.feedingamerica.org",
            tier=2,
            frequency="daily",
        )

    def run(self) -> list[ResourceCandidate]:
        # 1. Call GetAllOrganizations SOAP endpoint
        # 2. Parse XML response
        # 3. Map to ResourceCandidate objects
        # 4. Geocode addresses
        # 5. Return standardized resources
        pass
```

**Dependencies:**
- `zeep` - Python SOAP client library
- `requests` - HTTP requests
- Existing geocoding infrastructure

### Phase 2: Data Commons Partnership (Future)

**Investigation Needed:**
- Confirm bulk data export capability
- Test Google Data Commons Python client
- Evaluate completeness vs. SOAP endpoint

### Phase 3: FreshTrak Regional Integration (Optional)

**Scope:** Add regional food pantry data from FreshTrak
**Decision:** Only if SOAP data proves insufficient for regional coverage

---

## Data Mapping

### Resource Candidate to Database Mapping

| Feeding America Field | Vibe4Vets Field | Notes |
|----------------------|-----------------|-------|
| `Name` | `organization.name` | Food bank name |
| `StateAbbreviation` | `location.state` | 2-letter code |
| `Region` | (tags) | Feeding America region |
| Manual lookup: Address | `location.address` | May need separate API call |
| Manual lookup: Phone | `location.phone` | May need separate API call |
| Manual lookup: Website | `organization.url` | May need separate API call |

**Limitation:** SOAP endpoint may only return org name + state. Address/phone/hours may require:
- Secondary API call per food bank
- Manual supplementation from website
- Use of local food bank directory if available

### Categories

- Primary: `food` (food pantries, meal programs)
- Secondary: `supportServices` (case management, referral services if applicable)

---

## Testing Strategy

### Unit Tests

```python
def test_soap_request_format():
    """Verify SOAP envelope is properly formatted"""

def test_xml_response_parsing():
    """Parse sample SOAP response"""

def test_resource_candidate_creation():
    """Map XML data to ResourceCandidate"""

def test_error_handling():
    """Handle SOAP faults gracefully"""
```

### Integration Tests

```python
def test_live_endpoint_connectivity():
    """Can reach http://ws.feedingamerica.org/FAWebService.asmx"""

def test_full_pipeline():
    """End-to-end: fetch, parse, standardize, geocode"""
```

---

## Known Limitations & Gaps

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| SOAP endpoint may return limited fields | Missing address/phone/hours | Contact Feeding America for extended data or scrape food bank websites individually |
| No ZIP code lookup in SOAP | Cannot filter results by ZIP | Implement post-fetch filtering in Python |
| Rate limits not documented | Risk of throttling | Conservative refresh (1x/day) |
| Regional variation in data quality | Some food banks may have incomplete info | Flag for human review |
| Coverage gaps in rural areas | Sparse data for rural Veterans | Supplement with other sources (211, state agencies) |

---

## References & Resources

### Official

- **Feeding America Main Site:** https://www.feedingamerica.org
- **Food Bank Locator UI:** https://www.feedingamerica.org/find-your-local-foodbank
- **Contact/Partnerships:** https://www.feedingamerica.org/contact
- **Data Commons:** https://datacommons.feedingamerica.org

### Technical

- **SOAP Web Service:** http://ws.feedingamerica.org/FAWebService.asmx
- **Feeding America GitHub:** https://github.com/feedingamerica
- **FreshTrak Public Repo:** https://github.com/feedingamerica/freshtrak-public
- **Community XML-to-GeoJSON:** https://github.com/apfister/feeding-america-foodbank-xml2geojson

### Related

- **211 Integration:** See `211-integration.md` (complementary food resource directory)
- **USDA Food Data Central:** Official food program data
- **HUD-VASH & SSVF:** See main CLAUDE.md for housing-related food support

---

## Contact Information for Vibe4Vets Integration

**For Data Access Questions:**

Feeding America Main Office
161 N Clark St Ste 700
Chicago, IL 60601-3389

**Channels:**
1. General Contact: https://www.feedingamerica.org/contact
2. Partnership Inquiry: https://www.feedingamerica.org/ways-to-give/corporate-and-foundations/partnership-inquiry
3. GitHub Issues: https://github.com/feedingamerica (for open source projects)

---

## Summary

**Recommended Approach:** Implement connector using official SOAP web service (`http://ws.feedingamerica.org/FAWebService.asmx`).

**Key Advantages:**
- Official, stable endpoint with Tier 1 trust score
- No documented rate limiting concerns
- Returns nationwide food bank network data
- Complements other Feeding America resources (Data Commons for deeper analysis)

**Next Steps:**
1. ✅ Research complete (this document)
2. Implement `FeedingAmericaConnector` class with SOAP client
3. Test against live endpoint
4. Map response data to ResourceCandidate objects
5. Geocode and deduplicate with existing food resources
6. Evaluate secondary APIs for regional pantry details

**Status:** Ready for connector implementation. Contact Feeding America partnership team if bulk integration is needed.
