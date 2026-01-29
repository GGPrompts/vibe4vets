# Cohen Veterans Network Connector Specification

## Overview

The Cohen Veterans Network (CVN) is a national network providing **mental health services to post-9/11 Veterans and military families**. As of 2024, they operate **22 clinics across 21 states** offering in-person therapy and telehealth services.

**Organization:** Steven A. Cohen Foundation (via partner organizations)
**National Contact:** 844-336-4226
**Crisis Line:** Dial 988, then press 1
**Website:** https://www.cohenveteransnetwork.org/

---

## Data Collection Strategy

### Primary Data Source

**Clinic Directory:** https://www.cohenveteransnetwork.org/clinic-list/

The website maintains an interactive clinic locator with:
- Complete listing of all 22 clinic locations
- Structured data for each clinic (address, phone, email)
- State-by-state organization
- Geographic coverage indicators

### Scraping Approach

**Method 1: Direct HTML Scraping (Recommended)**
- Target: Clinic list page table/grid layout
- Extract from structured HTML table with clinic rows
- Fields: state, city, address, phone number
- Frequency: Weekly (growth is ongoing; monitor for new locations)
- Backup: Parse interactive map JSON if available

**Method 2: Partner Organization Pages**
- Each clinic is operated by a local partner organization
- Partner pages may have extended information (hours, staff, insurance details)
- Examples: Metro Care Services (Dallas), Endeavors (multiple locations), Easterseals (DC area)
- Challenge: Inconsistent formatting across partners; recommend secondary enrichment only

**Method 3: API (if available)**
- Check if CVN publishes clinic data via API endpoint
- Not currently documented; may exist at `/api/clinics` or similar
- Fallback to HTML scraping if not found

### Data Fields Available Per Clinic

| Field | Type | Example | Requirement |
|-------|------|---------|------------|
| **Clinic Name** | String | "Steven A. Cohen Military Family Clinic at Endeavors, Dallas" | Required |
| **City** | String | "Dallas" | Required |
| **State** | String | "TX" | Required |
| **Address** | String | "9696 Skillman St. #170, Dallas, TX 75243" | Required |
| **Phone** | String | "469-680-3500" | Required |
| **Email** | String | clinic@example.org | Optional |
| **Website** | URL | https://partner-org.org/cohen-clinic | Optional |
| **Telehealth Available** | Boolean | true | Inferred from page status |
| **Service Delivery** | Enum | "In-Person & Telehealth" or "Telehealth Only" | Inferred |
| **Partner Organization** | String | "Endeavors" or "Metro Care Services" | Optional |
| **CARF Accredited** | Boolean | true/false | Optional |

### 22 Clinic Locations (Current Inventory)

| # | State | City | Address | Phone |
|---|-------|------|---------|-------|
| 1 | AK | Fairbanks | 926 Aspen Street, AK 99709 | 907-762-8668 |
| 2 | AK | Anchorage | 1450 Muldoon Road #111, AK 99504 | 907-762-8668 |
| 3 | CA | San Diego | 8885 Rio San Diego Drive #301, CA 92108 | 619-345-4611 |
| 4 | CA | Oceanside | 3609 Ocean Ranch Blvd #120, CA 92056 | 760-418-4611 |
| 5 | CA | Torrance | 20800 Madrona Avenue C-100, CA 90503 | 213-642-4611 |
| 6 | CO | Colorado Springs | 1915 Aerotech Drive #114, CO 80916 | 719-370-5141 |
| 7 | FL | Jacksonville | 7011 A.C. Skinner Parkway, FL 32256 | 877-463-6505 |
| 8 | FL | Tampa | 4520 Oak Fair Blvd #100, FL 33610 | 813-542-5500 |
| 9 | GA | Hinesville | 345 W. Memorial Drive, GA 31313 | 912-456-2010 |
| 10 | HI | Mililani | 95-1091 ʻĀinamakua Drive, HI 96789 | 808-204-4020 |
| 11 | MD | Silver Spring | 1420 Spring St #300, MD 20910 | 240-847-7500 |
| 12 | NC | Jacksonville | 3245 Henderson Drive, NC 28546 | 910-388-5232 |
| 13 | NC | Fayetteville | 3505 Village Drive, NC 28304 | 877-463-6505 |
| 14 | OK | Oklahoma City | 1500 SW 104th Street, OK 73159 | 405-635-3888 |
| 15 | OK | Lawton | 4202 S.W. Lee Blvd, OK 73505 | 580-771-2662 |
| 16 | TN | Clarksville | 775 Weatherly Drive, TN 37043 | 877-463-6505 |
| 17 | TX | Dallas | 9696 Skillman St. #170, TX 75243 | 469-680-3500 |
| 18 | TX | San Antonio | 6333 De Zavala Rd B101, TX 78249 | 210-399-4838 |
| 19 | TX | Killeen | 1103 West Stan Schlueter Loop A-100, TX 76549 | 254-213-7847 |
| 20 | TX | El Paso | 12135 Pebble Hills Blvd #110, TX 79936 | 915-320-1390 |
| 21 | VA | Virginia Beach | 828 Healthy Way #105, VA 23462 | 757-965-8686 |
| 22 | WA | Lakewood | 6103 Mt. Tacoma Drive, WA 98499 | 253-215-7070 |

---

## Services & Conditions Taxonomy

### Services Offered

CVN clinics provide:
- **Individual therapy** (evidence-based, client-centered)
- **Telehealth** (face-to-face video sessions)
- **Marriage and relationship counseling**
- **Family therapy** (including children's behavioral health)
- **Case management** (employment, housing, finance assistance)

### Conditions Treated (Primary Categories)

```
mentalHealth:
  - PTSD (posttraumatic stress disorder)
  - Depression
  - Anxiety
  - Grief and loss
  - Anger management
  - Adjustment issues
  - Relationship problems
  - Transition challenges
  - Children's behavioral problems
```

### Service Delivery Modes

| Mode | Availability |
|------|--------------|
| **In-Person** | All 22 clinics |
| **Telehealth** | All 22 clinics (nationwide coverage) |
| **Same-Day Crisis** | Available for urgent cases |

### Service Hours & Access

- **Routine Appointments:** 87% report obtaining first appointment as soon as wanted
- **Crisis Care:** Same-day assistance available
- **Appointment Process:** Call clinic directly or contact national hotline (844-336-4226)

---

## Eligibility & Scope

### Eligible Populations

| Population | Eligible? | Notes |
|-----------|-----------|-------|
| **Post-9/11 Veterans** | ✅ Yes | Regardless of discharge status or service length |
| **Active Duty Service Members** | ✅ Yes | All branches (Army, Navy, Air Force, Marines, Coast Guard, Space Force) |
| **National Guard/Reserves** | ✅ Yes | Regardless of activation status |
| **Military Spouses/Partners** | ✅ Yes | Of post-9/11 service members |
| **Children** | ✅ Yes | Of post-9/11 service members (behavioral health supported) |
| **Parents/Siblings** | ✅ Yes | Of post-9/11 service members |
| **Military Caregivers** | ✅ Yes | Family members providing care |
| **Military Widows** | ✅ Yes | Families of deceased service members |
| **Families of Choice** | ✅ Yes | Extended family networks |

### Key Eligibility Principles

1. **No discharge status barrier** - Honorable, general, other-than-honorable all welcome
2. **Cost is never a barrier** - Sliding scale; most major insurances accepted (including TRICARE)
3. **Confidential services** - HIPAA-compliant; information not shared with VA/other agencies without legal requirement
4. **Post-9/11 focus** - Organization specifically serves post-September 11, 2001 cohort

### Insurance

- Accepts **most major insurances** including **TRICARE**
- Sliding scale fees based on income
- No one denied care due to inability to pay

---

## Vibe4Vets Integration

### Category Mapping

| Vibe4Vets Category | CVN Match | Notes |
|-------------------|-----------|-------|
| **mentalHealth** | Primary | Core mission: mental health therapy, PTSD, counseling |
| **supportServices** | Secondary | Case management, crisis support |
| **family** | Secondary | Services for spouses, children, caregivers |

### Resource Type

```json
{
  "organization": "Steven A. Cohen Foundation",
  "categories": ["mentalHealth"],
  "serviceScopeType": "national",
  "serviceScopeDetails": "22 clinics + national telehealth",
  "targetPopulations": ["post9_11_veterans", "active_duty", "military_families"],
  "eligibilityNotes": "Post-9/11 Veterans and military families. Regardless of discharge status.",
  "trustScoreTier": 2,
  "trustScoreRationale": "Major nonprofit organization with government recognition; 22 established clinics"
}
```

### Sub-Categories in Vibe4Vets Taxonomy

- **mentalHealth → Therapy & Counseling:** Individual, family, couples therapy
- **mentalHealth → Crisis Services:** Same-day crisis support
- **mentalHealth → Specialized Treatment:** PTSD-focused evidence-based care

---

## Scraping Implementation Notes

### Page Structure Analysis

1. **Homepage** (https://www.cohenveteransnetwork.org/):
   - Interactive US map showing all clinic locations
   - "View All Clinics" button → links to clinic-list

2. **Clinic List Page** (https://www.cohenveteransnetwork.org/clinic-list/):
   - HTML table with columns: State | City | Address | Phone
   - Geographic markers (red = in-person + telehealth; pink = telehealth only)
   - Email and website links per clinic

3. **Services/Eligibility Pages**:
   - https://www.cohenveteransnetwork.org/our-care/ → services taxonomy
   - https://www.cohenveteransnetwork.org/active-duty/ → active duty eligibility
   - https://www.cohenveteransnetwork.org/faqs/ → FAQs on hours, insurance, access

### Extraction Strategy

**Step 1: Parse clinic-list page HTML**
```
for each <tr> in clinic table:
  extract: state, city, address, phone, email, website_url
  normalize address (geocoding required)
```

**Step 2: Enrich from services pages**
```
Extract from /our-care/:
  - conditions_treated: [PTSD, depression, anxiety, ...]
  - delivery_modes: [in-person, telehealth]
  - service_types: [individual_therapy, couples, family, case_management]

Extract from eligibility pages:
  - eligible_populations: [post9_11_veterans, active_duty, military_families]
  - insurance_notes: [accepts TRICARE, sliding scale]
```

**Step 3: Create Resource records**
```
1 clinic = Multiple Resource records (if offering distinct programs)
Or:
1 clinic = 1 Organization record with 1 Location + 1 Resource record (recommended)
```

### Frequency & Monitoring

- **Refresh Frequency:** Weekly (organization continuously evaluates growth opportunities)
- **Change Detection:** Monitor for new clinic openings, location closures
- **Data Validation:** Validate phone numbers and addresses via test calls
- **Trust Scoring:** Tier 2 (major nonprofit with government recognition)

---

## Known Limitations

1. **Email Addresses:** Not consistently available on public pages; may require partner organization contact
2. **Operating Hours:** Not standardized across clinics; partner organization pages differ
3. **Clinician Details:** No individual therapist listings on directory pages
4. **Wait Times:** Only survey data (87% metric); specific wait times not published
5. **Languages Offered:** Not documented in public directory
6. **Specific PTSD Protocols:** Doesn't specify which evidence-based models (CBT, PE, EMDR, etc.)

---

## Additional Resources

- **Main Website:** https://www.cohenveteransnetwork.org/
- **Clinic Locator:** https://www.cohenveteransnetwork.org/clinic-list/
- **Services Info:** https://www.cohenveteransnetwork.org/our-care/
- **FAQ:** https://www.cohenveteransnetwork.org/faqs/
- **Partner Organizations:**
  - Endeavors (multiple states)
  - Metro Care Services (Dallas)
  - Easterseals (DC, Maryland area)
  - Veterans Village of San Diego
  - And others (varies by location)

---

## Sources

- [Cohen Veterans Network Homepage](https://www.cohenveteransnetwork.org/)
- [Clinic List and Locator](https://www.cohenveteransnetwork.org/clinic-list/)
- [Our Care - Services](https://www.cohenveteransnetwork.org/our-care/)
- [FAQs](https://www.cohenveteransnetwork.org/faqs/)
- [News.va.gov - CVN Article](https://news.va.gov/76869/cohen-veterans-network-mental-health-veterans-military/)
