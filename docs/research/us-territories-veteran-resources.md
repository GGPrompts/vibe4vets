# US Territories Veteran Resources Research
## Data Collection & Integration Plan for Vibe4Vets

**Research Date:** January 2026
**Issue:** V4V-yl5i
**Status:** Completed

---

## Executive Summary

The US has 5 permanently inhabited territories with significant Veteran populations:
- **Puerto Rico**: ~61,000 enrolled Veterans (largest, only territory with VA Medical Center)
- **Guam**: ~5,700 enrolled Veterans
- **US Virgin Islands**: ~6,000+ enrolled Veterans (serves PR + USVI from San Juan)
- **Northern Mariana Islands**: ~1,000+ Veterans (no local VA facility)
- **American Samoa**: ~1,000 enrolled Veterans (unaccredited local hospital)

All territories face critical healthcare access challenges. This document maps data sources for integration into Vibe4Vets.

---

## TERRITORY 1: PUERTO RICO

### Overview
- **Population**: ~3.2 million
- **Enrolled VA Veterans**: ~61,000
- **Unique Challenge**: Most developed VA infrastructure, but severe staffing shortages and pay disparity
- **Integration Priority**: **HIGH** (largest Veteran population, established data sources)

### VA Facilities & Healthcare

#### San Juan VA Medical Center (VA Caribbean Healthcare System Headquarters)
- **Type**: VA Hospital + Specialty Care
- **Services**: Primary care, specialty services, full hospital care
- **Address**: VA Caribbean Healthcare System
- **Contact**: 1-800-827-1000
- **Status**: Only VA hospital in Caribbean region, operates 1 hospital + 10 outpatient clinics
- **Data Format**: VA directory (accessible via VA.gov API)

#### Outpatient Clinics
- **VA Ponce Outpatient Clinic**: Hours 7:30 AM - 4:00 PM
- **VA Mayagüez Outpatient Clinic**: Hours 7:30 AM - 4:00 PM
- **Community Based Outpatient Clinics (CBOCs)**: Multiple locations across island
- **Data Format**: VA directory listing (scrape from va.gov/directory/guide)

#### VA Cemeteries
- **Puerto Rico National Cemetery**: Eligible Veterans & families
- **Morovis National Cemetery**: Eligible Veterans & families
- **Data Format**: Static facility list

### Benefits Administration

#### San Juan VA Regional Benefit Office
- **Location**: 50 CARR 165, Guaynabo, PR 00968-8024
- **Services**:
  - Compensation & Pension
  - Education & Training
  - Insurance
  - Loan Guaranty
  - Military Sexual Trauma (MST) support
  - Veteran Readiness & Employment
- **Appointments**:
  - Phone: (787) 772-7371 or (787) 772-7398
  - Email: APPOINTMENTS.VBASAJ@va.gov
  - Virtual/In-person via VERA: https://va.my.site.com/VAVERA/s/
- **Coverage Area**: Puerto Rico + US Virgin Islands
- **Data Format**: Contact info (static), appointment system (closed/proprietary)

### Puerto Rico Government Veteran Benefits
- **Income tax exemption**: $1,500 for Veterans ($3,000 married)
- **Property tax exemption**: Partial/full on primary residence
- **Education**: Reduced/free tuition at University of Puerto Rico & public institutions for dependents
- **Employment**: 10-point hiring preference for government jobs
- **Data Format**: Territory government website (need to identify official source)

### Local Veteran Organizations

#### National Tier 2-3 Organizations Operating in PR:
| Organization | Type | Contact | Data Format |
|---|---|---|---|
| DAV (Disabled American Veterans) | Nonprofit VSO | (787) 772-7388/7313, dav.vbasaj@va.gov | Directory listing |
| VFW (Veterans of Foreign Wars) | Nonprofit VSO | (787) 772-7455, aruiz@vfw.org, tarteaga@vfw.org | Directory listing |
| American Legion | Nonprofit VSO | N/A (national directory) | Directory listing |
| Paralyzed Veterans of America - PR | Advocacy | N/A | Directory listing |
| Vietnam Veterans of America - Chapter 59 | Advocacy | N/A | Directory listing |

**Data Format**: VA Directory of veteran service organizations (va.gov/directory)
**URL**: https://www.benefits.va.gov/SanJuan/veterans-services-orgs.asp

### Homelessness & Housing Support

#### FY 2026 SSVF Grants
- **Recipient Organizations**: Multiple nonprofits (need to identify)
- **Total Funding**: ~$1.3 million
- **Program**: Supportive Services for Veteran Families (SSVF)
- **Coverage**: Homelessness prevention, outreach, case management
- **Data Format**: VA grant database (va.gov/homeless)

### Data Collection Strategy for Puerto Rico

| Source | URL | Format | Freshness | Notes |
|---|---|---|---|---|
| VA Facilities Directory | https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=PR | Web scrape | Monthly updates | Covers all hospitals, clinics |
| San Juan Regional Office | https://www.benefits.va.gov/SanJuan/ | Web scrape | Static + appointment system | Contact info, service descriptions |
| VSO Directory | https://www.benefits.va.gov/SanJuan/veterans-services-orgs.asp | Web scrape | Semi-annual | Contacts for DAV, VFW, Legion |
| Puerto Rico Government | myarmybenefits.us.army.mil (Territory Benefits) | Web scrape | Ad-hoc | PR-specific government benefits |
| VA Homeless Programs | va.gov/homeless (SSVF section) | API/Database | Updated frequently | Grant recipients, funding amounts |

---

## TERRITORY 2: GUAM

### Overview
- **Population**: ~168,000
- **Enrolled VA Veterans**: ~5,700
- **Unique Challenges**:
  - Only outpatient clinic (no hospital)
  - Prescription delays (mailed to post office, causes long wait times)
  - Controlled by VA Pacific Islands Health Care System (Honolulu-based)
- **Integration Priority**: **HIGH** (accessible data, growing VA presence)

### VA Facilities & Healthcare

#### Guam VA Clinic
- **Location**: 498 Chalan Palasyo, Agana Heights, GU 96910
- **Type**: Outpatient clinic + Community Based Outpatient Clinic (CBOC)
- **Services**: Primary care, limited specialty (southern and northern clinic extensions)
- **Data Format**: VA directory listing
- **Staffing**: Community care program for specialists not available locally

#### Guam Vet Center
- **Location**: Hagatna, Guam (exact address in VA directory)
- **Services**:
  - PTSD counseling
  - Depression support
  - Military Sexual Trauma (MST) counseling
  - Family & couples counseling
  - Crisis line: 988 + press 1 (24/7, free, confidential)
- **Data Format**: VA directory + vet center locator

### Benefits Administration

#### Guam Benefits Office (VA Intake Site)
- **Location**: 770 East Sunset Blvd., Suite 165, Tamuning, GU 96913
- **Services**: VA benefits counseling, claim filing
- **Data Format**: VA directory listing
- **Coverage**: Guam only (not US Virgin Islands - that's handled by San Juan)

#### Guam Territorial Veterans Affairs Office
- **Role**: Accredited VSO functions, assists with federal & local benefits
- **Programs**:
  - Home/hospital visits for incapacitated Veterans
  - Benefits counseling for Veterans with <$30K income (eligible for VA care)
  - Burial benefits administration
- **Data Format**: Territory government website
- **Cemetery**: Guam Veterans Cemetery (Veteran & eligible dependent burials)

### Guam Government Veteran Benefits
- **Vehicle tax exemption**: Special veteran license plates (free)
- **Employment**: Government hiring preferences
- **Data Format**: Territory government website (Territory of Guam benefits)

### Local Veteran Organizations

#### Tier 2-3 Organizations:
| Organization | Type | Location | Data Format |
|---|---|---|---|
| Military Order of the Purple Heart - Chapter 0787 | Advocacy | Hagatna, GU (founded 1960) | Directory listing |
| WestCare Pacific Islands, Inc. | Nonprofit (SSVF recipient) | Guam | VA grant database |

### Employment & Training

#### Disabled Veterans Outreach Program (DVOP)
- **Operator**: Government of Guam Department of Labor
- **Services**: Employment services for eligible Veterans
- **URL**: https://dol.guam.gov/employment-and-training/dvop/
- **Data Format**: Territory government website

### FY 2026 Homeless Veteran Support
- **Recipient**: WestCare Pacific Islands, Inc.
- **Funding**: $1,306,597
- **Program**: Therapeutic services, outdoor recreation, green jobs, community engagement
- **Data Format**: VA SSVF grant database

### Data Collection Strategy for Guam

| Source | URL | Format | Freshness | Notes |
|---|---|---|---|---|
| VA Facilities Directory | https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=GU | Web scrape | Monthly | Clinics, vet centers |
| Guam Vet Center | https://www.va.gov/guam-vet-center/ | Web scrape | Static | Counseling services, crisis support |
| Guam VA Clinic | https://www.va.gov/pacific-islands-health-care/locations/guam-va-clinic/ | Web scrape | Static | Location, hours, services |
| Guam Benefits Office | https://www.va.gov/directory/guide/facility.asp?ID=5942 | Web scrape | Monthly | Contact, hours, location |
| Guam Territory Benefits | myarmybenefits.us.army.mil (Guam) | Web scrape | Ad-hoc | Territorial veteran benefits |
| DVOP Program | dol.guam.gov/employment-and-training/dvop/ | Web scrape | Semi-annual | Employment services |
| VA SSVF Grants | va.gov/homeless/ssvf | Database query | Quarterly | Grant recipients, amounts |

---

## TERRITORY 3: US VIRGIN ISLANDS

### Overview
- **Population**: ~106,000 (split across St. Croix, St. Thomas, St. John)
- **Enrolled VA Veterans**: ~6,000+
- **Unique Challenges**:
  - No local VA hospital or clinic (served by San Juan, PR)
  - 100% flight reimbursement for medical appointments initiated by VA
  - Multi-island territory (transportation barriers)
- **Integration Priority**: **MEDIUM-HIGH** (strong territorial government programs, healthcare access barriers)

### VA Facilities & Healthcare

#### US Virgin Islands Vet Center
- **Type**: Counseling center (non-medical setting, confidential)
- **Services**:
  - PTSD counseling
  - Depression support
  - Military Sexual Trauma (MST) counseling
  - Family counseling
  - Satellite locations with select services
- **Crisis Line**: 988 + press 1 (24/7, free)
- **Data Format**: VA directory + vet center locator
- **URL**: https://www.va.gov/us-virgin-islands-vet-center/

#### Healthcare Access
- **Primary Care**: Via San Juan Regional Office (Puerto Rico-based)
- **Specialist Care**: Community Care Program (private providers)
- **Travel Reimbursement**: 100% flight reimbursement for VA-initiated appointments
- **Data Format**: San Juan Regional Office directory

### Benefits Administration

#### USVI Office of Veterans Affairs
- **Mission**: Advocate for Virgin Islands Veterans, ensure access to entitled services
- **Services**:
  - Benefits counseling & claims assistance
  - Outreach to homeless/at-risk Veterans
  - Information about VA health care & memorial benefits
- **Contact**:
  - St. Thomas: 340-774-8387
  - St. Croix: 340-773-8387
  - Email: info_va@va.vi.gov
  - Website: https://veterans.vi.gov/
- **Data Format**: Territorial government website + directory

### USVI Government Veteran Benefits

| Benefit | Description | Data Format |
|---|---|---|
| Tuition Assistance | University of the Virgin Islands (UVI CELL) - free courses for Veterans | Territory website |
| Driver's License | Free "Veteran" designation on USVI driver's license | Territory website |
| License Plates | 3 distinctive free veteran license plates | Territory website |
| Burial Assistance | Reimbursement for burial expenses | Territory website |
| Home/Land Loans | Discounted home and land loans for Veterans | Territory website |
| Employment Preference | Government hiring preference | Territory website |

### Local Veteran Organizations

#### Organizations in USVI:
| Organization | Type | Island | Data Format |
|---|---|---|---|
| Virgin Islands National Guard Association | Advocacy | Various | Directory listing |
| Fish with a Vet USVI | Community | Various | Social media/local |
| American Legion - Post 102 (Enrique Romero Nieves) | VSO | Various | VA directory |
| American Legion - Post 85 (Myron G Danielson) | VSO | Various | VA directory |
| MTOC | Nonprofit | St. Thomas | Local directory |

### Community Support

#### MTOC Programs
- **Services**: Support for homeless, low-income families, Veterans
- **Location**: St. Thomas
- **Data Format**: Local directory/website

### Data Collection Strategy for USVI

| Source | URL | Format | Freshness | Notes |
|---|---|---|---|---|
| USVI Office of Veterans Affairs | https://veterans.vi.gov/ | Web scrape | Static | Government benefits, contact info |
| US Virgin Islands Vet Center | https://www.va.gov/us-virgin-islands-vet-center/ | Web scrape | Static | Counseling services, crisis support |
| San Juan Regional Office (serves USVI) | https://www.benefits.va.gov/SanJuan/ | Web scrape | Static | Healthcare coordination, benefits |
| Territory Benefits | myairforcebenefits.us.af.mil (USVI) | Web scrape | Ad-hoc | USVI-specific veteran benefits |
| Local VSO Directory | VA directory + local sources | Web scrape/manual | Semi-annual | American Legion posts, local orgs |

---

## TERRITORY 4: NORTHERN MARIANA ISLANDS

### Overview
- **Population**: ~53,000 (Saipan, Rota, Tinian)
- **Enrolled VA Veterans**: ~1,000+
- **Unique Challenges**:
  - **NO local VA facility** (closest is Guam, 1+ hour flight away)
  - Only benefits counselor traveling monthly (Saipan, Rota, Tinian)
  - Tax benefits for VA compensation/disability payments
  - Part of VA Pacific Islands Health Care System (Honolulu-based)
- **Integration Priority**: **MEDIUM** (severe healthcare gaps, expanding territorial benefits)

### VA Facilities & Healthcare

#### Benefits Counseling
- **Provider**: Permanent Legal Administrative Specialist (PLAS)
- **Location**: Saipan (primary) + monthly travel to Rota & Tinian
- **Services**: Benefits counseling, claims assistance
- **Funding**: FY 2026 priority expansion to rural/tribal territories
- **Data Format**: VA directory + VISN 21 (Pacific Islands) coordination

#### Healthcare Access
- **Primary Model**: Telehealth + referral to Guam VA Clinic or Honolulu VA Medical Center
- **Specialist Care**: VA Community Care Program (private providers)
- **Telehealth**: Expanded under FY 2026 priority for territories
- **Data Format**: VA healthcare system documentation

### CNMI Government Veteran Benefits

| Benefit | Description | Status |
|---|---|---|
| Tax Exemption | Income derived from VA payments (Dependency & Indemnity Compensation, Military Retired Disability Pay, survivor plans) exempt from territory tax | Active |
| Vehicle License Plate | Special veteran license plate (free) | Active |
| Burial Benefits | Available through territory cemetery | Active |

**Data Format**: Territory government website (need to identify)

### Territorial Initiatives (FY 2026)

#### TRAVEL Act Advocacy
- **Bill**: Territorial Response and Access to Veterans' Essential Lifecare (TRAVEL) Act of 2025
- **Sponsor**: Delegate King-Hinds
- **Goal**: Assign traveling VA physicians to remote territories for up to 1 year
- **Status**: Proposed (in legislative process)
- **Data Format**: Congressional documentation

### Local Veteran Organizations
- **Status**: Limited information available
- **Data Format**: Likely found in VA directory + VISN 21 listings

### Data Collection Strategy for Northern Mariana Islands

| Source | URL | Format | Freshness | Notes |
|---|---|---|---|---|
| VA Benefits Counselor Directory | VISN 21 Pacific Islands listing | Directory | Semi-annual | Single PLAS for entire CNMI |
| Guam VA Clinic (referral hub) | https://www.va.gov/pacific-islands-health-care/ | Web scrape | Monthly | Closest physical facility |
| VISN 21 Resources | department.va.gov/integrated-service-networks/visn-21/ | Web scrape | Static | Pacific Islands VA organization |
| Territory Benefits | Territory of CNMI government | Web scrape | Ad-hoc | Need to identify official website |
| VA Telehealth Directory | va.gov (telehealth services) | Database | Updated | Remote care options |

---

## TERRITORY 5: AMERICAN SAMOA

### Overview
- **Population**: ~55,000
- **Enrolled VA Veterans**: ~1,000
- **Unique Challenges**:
  - **Unaccredited local hospital** (VA cannot refer or pay for care there)
  - Only primary care facilities in Pago Pago
  - Part of VA Pacific Islands Health Care System (Honolulu-based)
  - No territory-level veteran benefits (federally dependent)
- **Integration Priority**: **MEDIUM** (significant healthcare gaps, limited local resources)

### VA Facilities & Healthcare

#### Faleomavaega Eni Fa'aua'a Hunkin VA Clinic
- **Location**: Pago Pago, American Samoa
- **Type**: Primary care clinic
- **Services**: Basic primary care, blood tests, advanced testing (limited)
- **Data Format**: VA directory
- **URL**: https://www.va.gov/pacific-islands-health-care/locations/faleomavaega-eni-faauaa-hunkin-va-clinic/

#### American Samoa Vet Center
- **Type**: Counseling center (non-medical, confidential)
- **Services**:
  - PTSD counseling
  - Depression support
  - Military Sexual Trauma (MST) counseling
  - Family & couples counseling
  - Licensed Clinical Social Worker onsite
  - Talk therapy + recreational activities
- **Crisis Line**: 988 + press 1 (24/7, free)
- **Data Format**: VA directory + vet center locator
- **URL**: https://www.va.gov/american-samoa-vet-center/

### Benefits Administration

#### VA Pacific Islands Health Care System (Coordinating Authority)
- **Headquarters**: Honolulu, Hawaii
- **Service Area**: ~7,200 Veterans across Hawaii, Guam, American Samoa, Northern Mariana Islands
- **Staffing**: Honolulu-based with deployed providers
- **Data Format**: VA directory + VISN 21 listing

#### Benefits Counseling
- **Status**: Limited to telephone/remote consultation
- **Model**: Coordinate through Honolulu Regional Office (Veterans Benefits Administration)
- **Data Format**: VA directory

### American Samoa Government Benefits
- **Territory-level benefits**: **None** (American Samoa offers zero state-level veteran benefits)
- **Reliance**: Entirely on federal VA benefits
- **Data Format**: N/A (no territorial program data to collect)

### Critical Healthcare Challenge
- **Issue**: Local hospital is unaccredited, preventing VA referrals and payment
- **Impact**: All specialty care requires travel to Honolulu or Guam (800+ miles)
- **Research Context**: GAO report (2018) documented "significant gaps in VA health care" for Pacific Islands
- **FY 2026 Priority**: VA prioritizing territories for expanded services & funding

### Local Veteran Organizations
- **Limited presence**: Likely only VA-affiliated centers
- **Data Format**: VA directory

### Data Collection Strategy for American Samoa

| Source | URL | Format | Freshness | Notes |
|---|---|---|---|---|
| Faleomavaega Clinic | https://www.va.gov/pacific-islands-health-care/ | Web scrape | Monthly | Only primary care facility |
| American Samoa Vet Center | https://www.va.gov/american-samoa-vet-center/ | Web scrape | Static | Counseling services only |
| VISN 21 Coordination | department.va.gov/integrated-service-networks/visn-21/ | Web scrape | Static | Pacific Islands VA network |
| VA Honolulu Regional Office | va.gov (benefits admin) | Directory | Semi-annual | Remote benefits coordination |
| Healthcare Access Report | GAO-18-288 / GAO-24-106364 | Reference document | Static | Documents system challenges |

---

## CROSS-TERRITORY DATA SOURCES & APIs

### VA Directory API
- **Coverage**: All VA facilities, vet centers, regional offices
- **URL**: https://www.va.gov/directory/
- **Format**: Web scrape from facility listing pages
- **States/Territories**: PR, GU, VI, AS, MP (CNMI)
- **Freshness**: Monthly updates
- **Integration**: Should already be in Vibe4Vets VA.gov connector

### VA Homeless Prevention & SSVF Grants
- **Database**: https://va.gov/homeless/ssvf
- **Format**: Database query (may have API)
- **Coverage**: All 5 territories receive FY 2026 grants
- **Data Items**: Organization name, funding amount, services offered
- **Freshness**: Quarterly updates
- **Integration Priority**: HIGH (helps identify local nonprofits)

### VA Vet Center Locator
- **URL**: https://www.va.gov/vet-center/ (national locator)
- **Format**: Web scrape or API
- **Coverage**: All territories have at least 1 vet center
- **Data Items**: Location, phone, services, hours
- **Freshness**: Monthly updates
- **Integration**: Should be covered by VA directory

### Military.com Territory Benefits
- **URL**: https://military.com/benefits/veteran-state-benefits/
- **Format**: Web scrape (one page per territory)
- **Coverage**: PR, GU, VI, AS, CNMI
- **Data Items**: Territory-specific benefits, contacts, links
- **Freshness**: Ad-hoc (updated when territory laws change)
- **Integration Priority**: MEDIUM (supplement official territory websites)

### Military Benefits Websites (Army & Air Force)
- **URLs**:
  - https://myarmybenefits.us.army.mil/Benefit-Library/State/Territory-Benefits/
  - https://myairforcebenefits.us.af.mil/Benefit-Library/State/Territory-Benefits/
- **Format**: Web scrape
- **Coverage**: All 5 territories
- **Data Items**: Territory benefits summaries, links, contacts
- **Freshness**: Annual or as-needed
- **Integration**: Good reference source, but data lives on territory websites

### VA Career OneStop (Employment)
- **Coverage**: Guam DVOP program explicitly listed
- **Format**: API (may be available)
- **Integration**: Should be covered by CareerOneStop connector

### GAO Reports & Government Documentation
- **Key Documents**:
  - GAO-18-288: "Opportunities Exist for Improving Veterans' Access to Health Care Services in the Pacific Islands"
  - GAO-24-106364: "Veterans Affairs: Actions Needed to Improve Access to Care in the U.S."
  - Stars & Stripes Reporting: Ongoing coverage of territory healthcare gaps
- **Format**: Reference documents (not automated)
- **Use**: Context for "coverage gaps" annotations in Vibe4Vets

---

## TERRITORY-BY-TERRITORY INTEGRATION PRIORITIES

### Tier 1 - HIGH PRIORITY (Start Here)

#### Puerto Rico
- **Rationale**: 61,000 Veterans, established data sources, only Caribbean VA hospital
- **Quick Wins**:
  1. Add San Juan Regional Office to resources
  2. Scrape VA facility directory for PR
  3. Add PR government benefits (UPR tuition, tax exemptions, hiring preference)
  4. Integrate local VSO listings (DAV, VFW, American Legion PR)
  5. Add SSVF grant recipients (homelessness prevention)
- **API/Database**: VA directory (existing), SSVF grants (need to research)
- **Coverage Gap**: No travel assistance program documented (unlike USVI)
- **Estimated Resources**: 15-20 organizations + 11 facilities

#### US Virgin Islands
- **Rationale**: Strong government programs, unique travel reimbursement, clear contact points
- **Quick Wins**:
  1. Add USVI Office of Veterans Affairs as primary government resource
  2. Add Vet Center (counseling services)
  3. Add territorial benefits (tuition, license plates, burial)
  4. Add local VSO chapters
- **API/Database**: VA directory, USVI government website (veterans.vi.gov)
- **Unique Feature**: 100% flight reimbursement for VA-initiated medical appointments
- **Estimated Resources**: 8-12 organizations + 4 vet center locations

### Tier 2 - MEDIUM-HIGH PRIORITY (Phase 2)

#### Guam
- **Rationale**: Accessible data, 5,700 Veterans, growing VA presence
- **Quick Wins**:
  1. Add Guam VA Clinic + Vet Center
  2. Add Guam Benefits Office
  3. Add Guam territorial benefits (employment preference, vehicle plates)
  4. Add DVOP employment program
  5. Add Purple Heart chapter + SSVF recipients
- **API/Database**: VA directory, Guam government website
- **Coverage Gap**: Prescription delays (systemic issue, not a missing resource)
- **Estimated Resources**: 10-15 organizations + 3 facilities

#### Northern Mariana Islands
- **Rationale**: Severe access gaps, growing FY 2026 support, multi-island complexity
- **Quick Wins**:
  1. Add benefits counselor information (traveling PLAS)
  2. Add Guam VA Clinic as referral (closest facility)
  3. Add territorial tax benefits
  4. Add telehealth resources
- **API/Database**: VISN 21 directory, Territory government
- **Coverage Gap**: No local VA facility (entire archipelago relies on Guam/Honolulu)
- **Challenge**: Only 1 benefits counselor, limited organizations
- **Estimated Resources**: 5-8 organizations + telehealth listings

### Tier 3 - MEDIUM PRIORITY (Phase 3)

#### American Samoa
- **Rationale**: Unique challenges, smallest population, limited resources
- **Quick Wins**:
  1. Add Faleomavaega VA Clinic
  2. Add American Samoa Vet Center
  3. Document healthcare gap (unaccredited hospital)
  4. Add Honolulu VA coordination info
- **API/Database**: VA directory, VISN 21
- **Coverage Gap**: Hospital accreditation issue (systemic, not addressable with directory data)
- **Challenge**: No territorial veteran benefits; entirely federally dependent
- **Estimated Resources**: 3-5 organizations + 2 VA facilities

---

## DATA COLLECTION METHODOLOGY

### 1. VA Directory Scraping
**Current Status**: Should already be implemented (VA.gov connector exists)
**Action**: Verify states/territories parameter includes: PR, GU, VI, AS, MP (CNMI)

```bash
# Expected URLs to scrape:
https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=PR
https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=GU
https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=VI
https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=AS
https://www.va.gov/directory/guide/fac_list_by_state.cfm?State=MP
```

### 2. Territory Government Websites
**Status**: Need connectors for each territory

| Territory | Official Website | Veteran Programs | Data Format |
|---|---|---|---|
| Puerto Rico | (need to identify) | Tax exemptions, tuition, employment | Web scrape |
| Guam | gvao.guam.gov | Burial, benefits, employment | Web scrape |
| USVI | veterans.vi.gov | Tuition, license plates, burial | Web scrape |
| CNMI | (need to identify) | Tax exemption, license plates | Web scrape |
| American Samoa | (minimal programs) | Federated to VA only | Reference only |

### 3. VA Benefits Database
**Status**: May have API access
**Action**: Research SSVF grants database for territory recipients

```
https://va.gov/homeless/ssvf
# Need to extract: Organization names, award amounts, service descriptions, locations
```

### 4. Military Benefits Aggregators
**Status**: Reference sources (not primary data)
**Use**: Cross-reference & validate territory benefits

- https://military.com/benefits/veteran-state-benefits/
- https://myarmybenefits.us.army.mil/Benefit-Library/State/Territory-Benefits/
- https://myairforcebenefits.us.af.mil/Benefit-Library/State/Territory-Benefits/

### 5. Local VSO Directories
**Status**: VA directory covers most, manual research needed for gaps

**Approach**:
- Scrape VA's VSO directory: https://www.benefits.va.gov/[region]/veterans-services-orgs.asp
- Supplement with local searches for community organizations
- Research SSVF grant recipients (identified as local nonprofits)

---

## CONNECTOR IMPLEMENTATION ROADMAP

### Phase 1: Enhance Existing VA Connector
**Timeframe**: Immediate
**Action**: Verify territorial states are included in existing VA.gov/Lighthouse connector

```python
# Current connector (if not already global):
territories = ["PR", "GU", "VI", "AS", "MP"]

# Ensure va_gov_connector.py queries all territories
for territory in territories:
    resources += fetch_va_facilities(state=territory)
```

### Phase 2: Territory-Specific Connectors
**Timeframe**: Sprint 2-3
**Create New Connectors**:

1. **PuertoRicoGovernmentConnector** (Medium effort)
   - Source: Puerto Rico government website (need to identify official veteran benefits page)
   - Data: Tax exemptions, tuition assistance, employment preferences
   - Frequency: Quarterly (benefits rarely change)

2. **USVIGovernmentConnector** (Low-Medium effort)
   - Source: veterans.vi.gov
   - Data: Tuition (UVI CELL), license plates, burial assistance, home loans
   - Frequency: Quarterly
   - Note: Website is clean & structured

3. **GuamGovernmentConnector** (Low-Medium effort)
   - Source: gvao.guam.gov + dol.guam.gov
   - Data: Burial benefits, DVOP employment, territorial benefits
   - Frequency: Quarterly

4. **CNMIGovernmentConnector** (Low effort)
   - Source: Territory government website (need to identify)
   - Data: Tax exemptions, vehicle plates
   - Frequency: Annual (minimal changes)

5. **SVFGrantConnector** (Medium effort)
   - Source: va.gov/homeless/ssvf (database query or web scrape)
   - Data: Organization names, funding, service types, locations
   - Frequency: Quarterly
   - Coverage: All 5 territories
   - **Priority**: HIGH (identifies local nonprofits across all territories)

### Phase 3: Validation & Testing
- Test with real data (cross-reference military.com, official government sites)
- Validate facility data matches VA directory
- Ensure benefits data is current (contact official websites quarterly)
- Document coverage gaps for each territory

---

## COVERAGE GAPS & UNIQUE CHALLENGES

### Healthcare Access (System-Level)

| Territory | Challenge | Impact | Vibe4Vets Role |
|---|---|---|---|
| **Puerto Rico** | Chronic staffing shortages, pay disparity | Long wait times for appointments, specialist delays | Document in "coverage notes", link to San Juan RO contact |
| **Guam** | No hospital, prescription mail delays | Veterans wait weeks for medications | Document in CBOC resource notes |
| **USVI** | No local VA facility, must travel to PR | Medical appointments require flight | **Highlight**: 100% flight reimbursement policy (unique benefit) |
| **CNMI** | NO local VA facility, closest is Guam (1+ hr flight) | No access to in-person care; telehealth only | **Highlight**: Telehealth expansion (FY 2026), advocate for TRAVEL Act |
| **American Samoa** | Unaccredited local hospital, no VA referral capability | ALL specialty care requires travel to Honolulu/Guam | **Critical**: Mark as "high-risk" for healthcare coordination |

### Data Availability Gaps

| Territory | Missing Data | Workaround | Priority |
|---|---|---|---|
| Puerto Rico | Official government veteran benefits website | Use Military.com + official agency contacts | Medium |
| Guam | Nonprofit/community org database | SSVF grants + local searches | Medium |
| USVI | (Data available at veterans.vi.gov) | N/A | Low |
| CNMI | Government website for benefits | Contact territory directly | Medium |
| American Samoa | Territory veteran benefits | None (no territorial program) | Low |

### Annotation Strategy for Vibe4Vets

For each territory resource, add metadata:

```json
{
  "id": "...",
  "name": "VA Clinic in Guam",
  "state": "GU",
  "coverage_notes": [
    "Limited to outpatient care",
    "Prescriptions mailed, may experience delays",
    "Specialists via Community Care Program"
  ],
  "access_challenges": [
    "Island location may limit specialist access",
    "Telehealth available for remote consultation"
  ],
  "population_served": 5700,
  "trust_score": 1.0,
  "data_freshness": "2026-01-28",
  "territory_specific": true
}
```

---

## RECOMMENDATIONS FOR VIBE4VETS

### Immediate Actions (Week 1-2)

1. **Audit Existing Connectors**
   - Verify VA.gov connector includes all 5 territories
   - Check if territory abbreviations ("MP" for Northern Mariana, "AS" for American Samoa) are correctly handled

2. **Add Territory Identifier**
   - Add boolean field `is_territory: boolean` to Resource model
   - Use to tag all Puerto Rico, Guam, USVI, American Samoa, Northern Mariana Islands resources
   - Enables territory-specific filtering in frontend

3. **Document Coverage Gaps**
   - Create reference document of known gaps (per table above)
   - Use in customer support & public-facing transparency

### Short-Term (Sprint 2-4)

4. **Implement SSVF Grants Connector** (HIGHEST PRIORITY)
   - Covers all 5 territories
   - Identifies local nonprofit organizations
   - Data is clean & structured at va.gov/homeless

5. **Create Territory-Specific Connectors**
   - Start with Puerto Rico (largest population, clearest data)
   - Then USVI (cleanest government website)
   - Then Guam (established VA presence)

6. **Enhance Frontend**
   - Territory filter in search UI
   - Territory-specific "coverage notes" displayed with resources
   - Highlight unique benefits (e.g., USVI flight reimbursement)

### Medium-Term (Q2 2026)

7. **Community Research**
   - Contact territory veteran organizations for feedback
   - Identify missing local nonprofits
   - Validate accuracy of government benefit descriptions

8. **Healthcare Access Transparency**
   - Create in-app guide: "Healthcare in [Territory]"
   - Explain unique challenges (e.g., CNMI has no local facility)
   - Link to TRAVEL Act updates & advocacy

9. **Telehealth Promotion**
   - Highlight VA telehealth options for remote territories
   - Partner with VA to promote rural telehealth expansion

### Long-Term (Q3+ 2026)

10. **Partner with VA Innovation**
    - Advocate for territory healthcare solutions
    - Monitor TRAVEL Act progress (Delegate King-Hinds)
    - Potential collaboration: Help VA publicize new territory health initiatives

---

## REFERENCES & DATA SOURCES

### Official VA Resources
- VA Directory: https://www.va.gov/directory/
- VA Homeless/SSVF: https://va.gov/homeless/ssvf
- VA Vet Centers: https://www.va.gov/vet-center/
- VA Healthcare Systems:
  - Caribbean: https://www.va.gov/caribbean-health-care/
  - Pacific Islands: https://www.va.gov/pacific-islands-health-care/

### San Juan Regional Office (PR + USVI)
- Main: https://www.benefits.va.gov/SanJuan/
- VSO Directory: https://www.benefits.va.gov/SanJuan/veterans-services-orgs.asp
- Facilities: https://www.benefits.va.gov/sanjuan/other-va-facilities.asp
- Services: https://www.benefits.va.gov/ROSANJUAN/services-offered.asp

### Territory Government Websites
- **Puerto Rico**: (need to identify official veteran benefits source - government may not have dedicated site)
- **Guam**: https://gvao.guam.gov/
- **USVI**: https://veterans.vi.gov/
- **CNMI**: (need to identify)
- **American Samoa**: (minimal programs)

### Territory Benefits Aggregators
- Military.com: https://military.com/benefits/veteran-state-benefits/
- Army Benefits: https://myarmybenefits.us.army.mil/Benefit-Library/State/Territory-Benefits/
- Air Force Benefits: https://myairforcebenefits.us.af.mil/Benefit-Library/State/Territory-Benefits/

### Government Reports & Analysis
- [GAO-18-288](https://www.gao.gov/products/gao-18-288): Pacific Islands Healthcare Access (2018)
- [GAO-24-106364](https://www.gao.gov/assets/gao-24-106364.pdf): Recent VA Access Issues (2024)
- [Stars & Stripes](https://www.stripes.com/veterans/2024-05-28/overseas-territories-pacific-islands-health-care-14008604.html): Territory Healthcare Gaps (2024)
- Congressional TRAVEL Act proposal (Delegate King-Hinds)

### News & Research
- DAV Report: "The Patriots We Forget" (2023)
- CNAS: "State-Level Veteran Benefits in U.S. Territories"
- Rural Health Information Hub: Territory resources

---

## APPENDIX: Territory-at-a-Glance

| Metric | PR | GU | VI | CNMI | AS |
|---|---|---|---|---|---|
| **Population** | 3.2M | 168K | 106K | 53K | 55K |
| **Enrolled Veterans** | 61,000 | 5,700 | 6,000+ | 1,000+ | 1,000 |
| **VA Hospital** | ✅ Yes (only Caribbean) | ❌ No | ❌ No | ❌ No | ❌ No |
| **VA Clinic** | ✅ 10+ | ✅ 1 | ❌ No (San Juan) | ❌ No | ✅ 1 |
| **Vet Center** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Regional Office** | ✅ San Juan | ❌ (Intake site) | ✅ San Juan | ❌ Remote | ❌ Remote |
| **Territory VA Benefits** | ✅ Tax, tuition, employment | ✅ Burial, employment | ✅ Tuition, plates, loans | ✅ Tax, plates | ❌ None |
| **Gov Website** | 🔍 Need to find | ✅ gvao.guam.gov | ✅ veterans.vi.gov | 🔍 Need to find | 🔍 Minimal |
| **Healthcare System** | Caribbean HC | Pacific Islands HC | San Juan (PR) | Pacific Islands HC | Pacific Islands HC |
| **Key Challenge** | Staffing shortages | Prescription delays | No local facility | **NO facility** | Unaccredited hospital |
| **Travel Support** | (Unknown) | (Unknown) | ✅ 100% flight reimbursement | (Telehealth only) | (Unknown) |
| **Integration Priority** | **HIGH** | **HIGH** | **HIGH** | **MEDIUM** | **MEDIUM** |

---

## CONCLUSION

The five US territories collectively serve approximately 75,000+ Veterans with significant healthcare access challenges. Puerto Rico represents the most developed infrastructure (only Caribbean hospital), while Northern Mariana Islands faces the most acute gaps (no local VA facility).

Vibe4Vets can significantly improve Veteran resource access in territories by:

1. **Aggregating scattered territorial benefits** into searchable directory
2. **Documenting healthcare gaps** transparently (building trust)
3. **Connecting Veterans to local nonprofits** (via SSVF grants database)
4. **Highlighting unique benefits** (e.g., USVI flight reimbursement, CNMI tax exemptions)
5. **Advocating for territory solutions** (telehealth expansion, TRAVEL Act support)

**Data maturity is high** for VA facilities (existing connector), but **moderate for territorial government programs** (websites exist but require targeted scraping). **SSVF grants connector is the highest-value addition**, immediately identifying ~30-50 local nonprofits across all territories.

**Recommended start**: Validate existing VA connector covers all 5 territories, then implement SSVF connector to identify local nonprofits in each territory.
