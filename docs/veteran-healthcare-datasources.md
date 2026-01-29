# Veteran Healthcare Data Sources (Beyond VA)

Research compiled for Vibe4Vets resource directory - Community health centers, telehealth programs, dental/vision, and veteran-focused clinics serving Veterans nationwide.

**Date:** January 28, 2026
**Issue:** V4V-ccfa

---

## Table of Contents

1. [Tier 1: Official Government APIs & Databases](#tier-1-official-government-apis--databases)
2. [Tier 2: Community Health Networks](#tier-2-community-health-networks)
3. [Tier 3: Nonprofit Mental Health Programs](#tier-3-nonprofit-mental-health-programs)
4. [Tier 4: Dental & Vision Programs](#tier-4-dental--vision-programs)
5. [Tier 5: Mobile Health & Rural Access](#tier-5-mobile-health--rural-access)
6. [Integration Notes](#integration-notes)

---

## Tier 1: Official Government APIs & Databases

### VA Facilities API (Lighthouse)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration (VA) |
| **URL** | https://developer.va.gov/ |
| **Data Format** | RESTful API |
| **Key Dataset** | VA Facilities Directory with contact, location, hours, services, wait times, patient satisfaction |
| **VAST Database** | Official repository of VHA healthcare delivery sites (medical centers, hospitals, CBOCs, Vet Centers) |
| **Integration Priority** | **HIGH** - Official government source, Tier 1 trust scoring |
| **Documentation** | https://developer.va.gov/ (Lighthouse API platform) |
| **Coverage** | 21 VISN regions, 300+ Vet Centers, 200+ dental locations nationwide |
| **Notes** | STA_NO field identifies facility hierarchy (3-char parent, 5-char CBOC, 7-char satellite). Requires API token registration. |

### HRSA Data Warehouse & Health Center Finder
| Property | Value |
|----------|-------|
| **Organization** | Health Resources & Services Administration (HRSA) |
| **URL** | https://data.hrsa.gov/ |
| **Finder Tool** | https://findahealthcenter.hrsa.gov/ |
| **Data Format** | RESTful API + Web Services |
| **Key Datasets** | Federally Qualified Health Centers (FQHCs), Health Centers, NHSC sites |
| **Integration Priority** | **HIGH** - Tier 1 trust scoring, comprehensive community health coverage |
| **Requirements** | API token registration required via Developer Guide |
| **Query Methods** | Search by state, county, ZIP code |
| **Features** | GIS portal with MapServer REST endpoints, embedded widgets available |
| **Related Resources** | NHSC Site Reference Guide for eligible site types |
| **Notes** | 50,000+ resources in comprehensive health services database |

### CMS Provider Data
| Property | Value |
|----------|-------|
| **Organization** | Centers for Medicare & Medicaid Services (CMS) |
| **URL** | https://data.cms.gov/provider-data/dataset/uyx4-5s7f |
| **Data Format** | Dataset query + API |
| **Coverage** | Veterans Health Administration Provider Level Data |
| **Integration Priority** | **MEDIUM-HIGH** - Official government source |
| **Notes** | Includes VHA provider metrics and performance data |

### National Health Service Corps (NHSC) Eligibility Database
| Property | Value |
|----------|-------|
| **Organization** | Health Resources & Services Administration (HRSA) |
| **URL** | https://nhsc.hrsa.gov/ |
| **Data Format** | Web database + site eligibility requirements |
| **Coverage** | Loan repayment program sites, mobile units, clinics in HPSAs |
| **Integration Priority** | **MEDIUM** - Identifies underserved areas with veteran populations |
| **Key Insight** | Mobile units eligible if >50% service time in HPSA; Note: VHA medical centers not NHSC-eligible |

### Open Data - GIS Portals
| Property | Value |
|----------|-------|
| **VHA Facilities GIS Layer** | https://gisportal.hrsa.gov/server/rest/services/HealthCareFacilities/VHAFacilities_FS/MapServer/0 |
| **Veteran Medical Facilities** | https://services2.arcgis.com/VFLAJVozK0rtzQmT/arcgis/rest/services/Veterans_Health_Administration_Medical_Facilities/FeatureServer |
| **Data.gov** | https://catalog.data.gov/organization/va-gov |
| **HIFLD OpenData** | https://hifld-geoplatform.opendata.arcgis.com/datasets/f11d7d153bfb408f85bd029b2dac9298_0 |
| **Data Format** | GIS MapServer/FeatureServer REST API |
| **Integration Priority** | **MEDIUM-HIGH** - Geospatial search for veteran facilities |

### VA Community Care Network (CCN)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Affairs Community Care |
| **Primary URL** | https://www.va.gov/communitycare/ |
| **Provider Network Portal** | https://vacommunitycare.com/ |
| **VACCN Portal** | https://vaccn.triwest.com/ |
| **Data Format** | Provider portal + scheduling system (EPS - External Provider Scheduling) |
| **Regional Coverage** | 5-6 regions (Optum Serve: Regions 1-3; TriWest: Regions 4-5) |
| **Integration Priority** | **HIGH** - Primary VA referral network for community providers |
| **Services** | Medical, behavioral health, dental, surgical, CIHS (complementary/integrative health) |
| **TPAs** | Optum Serve (UnitedHealth Group) & TriWest Healthcare Alliance |
| **Contact for API** | Contact individual TPAs directly for API documentation |
| **Notes** | Direct health info sharing between VA and community providers; quality metrics monitoring |

---

## Tier 2: Community Health Networks

### 211.org (United Way 211)
| Property | Value |
|----------|-------|
| **Organization** | United Way 211 (nationwide) |
| **URL** | https://register.211.org/ |
| **State Resources** | https://211md.org/, https://211la.org/, https://www.pa211.org/ |
| **Data Format** | **API available** - Cloud-based resource database; Open Referral compliant (Human Service Data Specification) |
| **Coverage** | 7,500+ resources (Maryland); 50,000+ resources (LA County); national coverage |
| **Integration Priority** | **MEDIUM-HIGH** - Comprehensive social services directory with veteran services |
| **Integration Method** | API designed to be software agnostic; used with Salesforce, call centers |
| **Search** | Query 211 Community Resource Database for Veteran-specific resources |
| **Data Standard** | Open Referral HSDS format (standardized, reusable) |
| **Services** | Health, human services, benefits counseling, crisis resources |

### HRSA Find a Health Center Tool
| Property | Value |
|----------|-------|
| **URL** | https://findahealthcenter.hrsa.gov/ |
| **Data Format** | Web search + API |
| **Coverage** | Federally Qualified Health Centers (FQHCs) nationwide |
| **Integration Priority** | **MEDIUM-HIGH** - FQHCs serve medically underserved, uninsured/underinsured Veterans |
| **Features** | Search by address, state, or county; multi-state search available |
| **Services** | Primary care, preventive care, dental, mental health (many locations) |

### National Resource Directory
| Property | Value |
|----------|-------|
| **Organization** | Partnership: DoD, DoL, VA |
| **URL** | See nonprofit directory resources below |
| **Data Format** | Web directory + referral system |
| **Coverage** | Services for wounded, ill, injured service members, Veterans, families |
| **Integration Priority** | **MEDIUM** - Official multi-agency resource hub |

---

## Tier 3: Nonprofit Mental Health Programs

### Cohen Veterans Network
| Property | Value |
|----------|-------|
| **Organization** | Cohen Veterans Network (CVN) |
| **URL** | https://www.cohenveteransnetwork.org/ |
| **Data Format** | Clinic directory with downloadable resources |
| **Clinic Count** | 22 clinics across 21 states |
| **Integration Priority** | **HIGH** - Specialized mental health, post-9/11 Veterans focus |
| **Services** | PTSD, depression, anxiety, relationship counseling, case management, benefits referrals |
| **Eligibility** | All post-9/11 Veterans (regardless of discharge status), active duty, military families |
| **Cost Model** | Free care (accepts most insurance including TRICARE) |
| **Locations** | San Diego, metro areas nationwide |
| **Referral** | Comprehensive case management for housing, employment, legal issues |

### Stop Soldier Suicide (ROGER Wellness Service)
| Property | Value |
|----------|-------|
| **Organization** | Stop Soldier Suicide (founded 2010) |
| **URL** | https://stopsoldiersuicide.org/ |
| **Telehealth Service** | ROGER Wellness Program |
| **Data Format** | Telehealth provider roster (contact via hotline) |
| **Coverage** | All U.S. Veterans and service members (all branches, generations) |
| **Integration Priority** | **HIGH** - Specialized suicide prevention, no discharge barriers |
| **Services** | Virtual mental health counseling, crisis intervention, safety planning |
| **Cost** | 100% free (donor-funded) |
| **Clinical Approach** | CAMS (Collaborative Assessment & Management of Suicidality), BCBT-SP (Brief Cognitive Behavioral Therapy for Suicide Prevention) |
| **Contact** | 984-207-3260 (24/7) |
| **Notes** | No proof of service required; confidential, personalized care |

### Wounded Warrior Project
| Property | Value |
|----------|-------|
| **Organization** | Wounded Warrior Project (WWP) |
| **URL** | https://www.woundedwarriorproject.org/ |
| **Programs** | Mental Wellness, Veteran Training programs |
| **Data Format** | Program directory + referral |
| **Integration Priority** | **MEDIUM** - Multi-service Veteran organization |
| **Services** | Mental health support, peer connections, employment training |

### Veterans Crisis Line
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **URL** | https://www.veteranscrisisline.net/ |
| **Data Format** | Crisis hotline + telehealth screening |
| **Coverage** | All Veterans, service members, families |
| **Integration Priority** | **HIGH** - Critical mental health access, crisis intervention |
| **Contact** | Call/text 988 then press 1 |

### Returning Veterans Project (RVP)
| Property | Value |
|----------|-------|
| **Organization** | Returning Veterans Project (community-based nonprofit) |
| **Region** | Oregon & SW Washington |
| **URL** | https://returningveterans.org/ |
| **Services** | Free, confidential health services for Veterans, active duty, families |
| **Integration Priority** | **MEDIUM** - Regional model (replicable for other regions) |

---

## Tier 4: Dental & Vision Programs

### VA Dental Care Program
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **URL** | https://www.va.gov/health-care/about-va-health-benefits/dental-care/ |
| **Portal** | https://www.va.gov/dental/ |
| **Data Format** | Facility locator + eligibility criteria |
| **Coverage** | 200+ VA dental locations; ~888,000 Veterans (FY 2025) |
| **Integration Priority** | **HIGH** - Official government dental program |
| **Eligibility** | Recent discharge (180 days free), Veterans Readiness & Employment participants, service-connected |
| **Services** | Cleanings, x-rays, fillings, crowns, bridges, dentures, oral surgery |
| **Access** | VA Locations Finder tool |
| **Accessibility Issue** | 85% of Veterans ineligible for VA dental coverage |

### VA Dental Insurance Program (VADIP)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **Partners** | Delta Dental, MetLife |
| **Data Format** | Insurance plan directory |
| **Cost** | Reduced rates for enrolled VA healthcare Veterans |
| **Integration Priority** | **MEDIUM-HIGH** - Addresses gap for ineligible Veterans |
| **Services** | Preventive, diagnostic, restorative, surgical dental |

### Community Care Network - Dental Coverage
| Property | Value |
|----------|-------|
| **Organization** | VA Community Care Network (TPAs: Optum, TriWest) |
| **Provider Network** | Delta Dental (primary), other in-network providers |
| **Data Format** | Provider portal + claims |
| **Eligibility** | Veterans unable to access VA dental facilities |
| **Integration Priority** | **MEDIUM-HIGH** - Secondary dental access pathway |

### VA Vision Care
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **Services** | Eye exams, glasses, contact lenses |
| **Coverage** | Service-connected eye conditions, recent discharge |
| **Integration Priority** | **MEDIUM** - Limited VA vision coverage; Community Care referrals recommended |

### Smiles for Veterans
| Property | Value |
|----------|-------|
| **Organization** | Smiles for Veterans (nonprofit) |
| **URL** | https://smilesforveterans.org/ |
| **Focus** | Bridge the 85% gap of Veterans ineligible for VA dental |
| **Services** | Dental care at reduced/no cost |
| **Data Format** | Program directory |
| **Integration Priority** | **MEDIUM** - Addresses critical access gap |

### State Dental Programs
| Property | Value |
|----------|-------|
| **Example** | Florida Veterans Foundation Statewide Dental Program |
| **URL** | https://www.floridavets.org/ |
| **Model** | State-level veteran dental initiatives |
| **Integration Priority** | **MEDIUM** - Variable by state; check state VA websites |

---

## Tier 5: Mobile Health & Rural Access

### VA Mobile Medical Units (MMU)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **Program** | National Mobile Medical Unit Program |
| **URL** | https://mobile.va.gov/about |
| **Deployment** | 25 units deployed nationwide (fully operational) |
| **Data Format** | Unit location/schedule data (contact VA for specific locations) |
| **Integration Priority** | **MEDIUM-HIGH** - Expands access for homeless, at-risk Veterans |
| **Services** | Primary care, mental health, specialty care (adapted to local needs) |
| **Model** | HPACT (Health Promotion, Access, Care, Training) |
| **Eligibility** | Medically eligible Veterans experiencing homelessness or at-risk (enrolled/non-enrolled accepted) |

### VA Telehealth Services (Connected Care)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **Primary URL** | https://telehealth.va.gov/ |
| **Platforms** | VA Video Connect, My HealtheVet |
| **Data Format** | Telehealth provider directory + appointment system |
| **Integration Priority** | **HIGH** - Comprehensive Veterans telehealth infrastructure |
| **Specialties** | 50+ specialty areas (primary care, mental health, cardiology, pain management) |
| **Access Points** | Home, community clinics, hospitals |

### ATLAS Program (Accessing Telehealth at Local Area Stations)
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration + Community Partners |
| **Partners** | American Legion, VFW, Walmart, nonprofit organizations |
| **Purpose** | Provide telehealth access locations for Veterans without home internet |
| **Data Format** | Site directory (contact VA or partner organizations) |
| **Integration Priority** | **MEDIUM-HIGH** - Addresses digital divide |
| **Services** | Video visits with VA providers from secure community locations |
| **Model** | Pilot program expanding to select communities |

### VA Connected Devices Program
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration |
| **Benefit** | Free internet-connected tablets for eligible Veterans |
| **Support** | 24/7 tech support for VA-loaned devices |
| **Data Format** | Eligibility & enrollment system |
| **Integration Priority** | **MEDIUM** - Enables digital access for underserved Veterans |

### VA Clinical Resource Hubs
| Property | Value |
|----------|-------|
| **Organization** | Veterans Health Administration (18 VISN networks) |
| **Purpose** | Expand telehealth access in underserved/rural areas |
| **Services** | Primary care, mental health, specialty care via telehealth to community-based outpatient clinics |
| **Data Format** | Hub location directory (contact regional VISN) |
| **Integration Priority** | **MEDIUM-HIGH** - Rural veteran healthcare expansion |

### VA Rural Health Programs & Partnerships
| Property | Value |
|----------|-------|
| **Organization** | VA Office of Rural Health + Veterans Rural Health Resource Centers |
| **URL** | https://www.ruralhealth.va.gov/aboutus/vrhrc.asp |
| **Partnerships** | Community Health Centers (RHCs), area hospitals, CBOC clinics |
| **Services** | Telehealth delivery, mobile VA clinics, Community Based Outpatient Clinics (CBOCs) |
| **Integration Priority** | **MEDIUM-HIGH** - Systematic rural access strategy |
| **Regional Coverage** | Varies by VISN |

---

## Tier 6: Community-Based Veteran Organizations

### Team Red, White & Blue (Team RWB)
| Property | Value |
|----------|-------|
| **Organization** | Team Red, White & Blue (501(c)(3) nonprofit, founded 2010) |
| **URL** | https://teamrwb.org/programs |
| **Headquarters** | Ann Arbor, Michigan |
| **Data Format** | Event directory + program listings |
| **Integration Priority** | **MEDIUM** - Health-enriching community engagement model |
| **Focus Areas** | Physical health, mental health, purpose, relationships |
| **Activities** | Local physical events, social activities, service opportunities (virtual & in-person) |
| **Reach** | ~100,000 Veterans & service members (2020 check-in data) |
| **Model** | Community-based social support with health outcomes |

### Operation Homefront
| Property | Value |
|----------|-------|
| **Organization** | Operation Homefront (501(c)(3), founded 2002) |
| **URL** | https://operationhomefront.org/ |
| **Headquarters** | San Antonio, TX & Arlington, VA |
| **Data Format** | Program directory + referral |
| **Integration Priority** | **MEDIUM** - Multi-service veteran/military family support |
| **Services** | Food assistance, auto/home repair, vision care, travel/transport, housing (rent-free for wounded) |
| **Efficiency** | 92% of expenditures to direct programs |
| **Target** | Ill/injured Veterans and military families |

### Veteran Health & Wellness Foundation (VHWF)
| Property | Value |
|----------|-------|
| **Organization** | VHWF (501(c)(3) nonprofit) |
| **URL** | https://myvhwf.org/ |
| **Focus** | Health, wellness, healthcare delivery intersection with social determinants |
| **Founded** | By military Veterans with healthcare expertise |
| **Integration Priority** | **MEDIUM** - Specialized health-social integration model |

### National Resource Directory (Veterans.com / Military Veteran Project)
| Property | Value |
|----------|-------|
| **URL** | https://www.militaryveteranproject.org/militaryresources.html |
| **Data Format** | Nonprofit resource directory with database |
| **Coverage** | Military charities, government contacts, resource listings |
| **Integration Priority** | **MEDIUM** - Aggregated Veteran resources database |

### Veteran Service Organizations (VSOs)
| Property | Value |
|----------|-------|
| **Examples** | DAV (Disabled American Veterans), VFW (Veterans of Foreign Wars), American Legion |
| **URL** | https://www.dav.org/, VFW.org, americanlegion.org |
| **Data Format** | Local chapter directories + service listings |
| **Integration Priority** | **MEDIUM** - Tier 2 trust scoring; established community networks |
| **Services** | Benefits counseling, community programs, advocacy |

---

## Integration Notes

### Data Quality & Trust Scoring

| Tier | Trust Score | Examples |
|------|-------------|----------|
| 1 | 1.0 | VA.gov API, HRSA, HUD, DOD official data |
| 2 | 0.8 | 211.org (Open Referral standard), established VSOs (DAV, VFW, Legion) |
| 3 | 0.6 | State Veteran agencies, established nonprofits (Cohen CVN, Operation Homefront) |
| 4 | 0.4 | Community clinic networks, smaller nonprofits |

### Recommended Integration Priority for V4V

**Phase 1 (Immediate High Priority):**
- VA Facilities API (Lighthouse) - comprehensive VHA coverage
- HRSA Health Center Finder API - community health centers
- 211.org API - Open Referral standardized social services
- VA Community Care Network - primary referral pathway

**Phase 2 (Medium Priority):**
- Cohen Veterans Network mental health clinics
- Stop Soldier Suicide ROGER telehealth
- State veteran agency dental/vision programs
- VA Mobile Medical Units

**Phase 3 (Lower Priority - Potential):**
- Team RWB event directory (engagement model)
- Operation Homefront (multi-service family support)
- Community-based nonprofit directories

### API & Data Format Standards

**Preferred Formats (in order):**
1. RESTful API with JSON response
2. Open Referral HSDS standardized format
3. GIS/MapServer REST endpoints
4. CSV export capability
5. Web directory (last resort - requires scraping)

**Key Metadata to Capture:**
- Organization name & type
- Service categories (mental health, dental, housing, etc.)
- Geographic coverage (state/county/zip)
- Veteran eligibility criteria
- Telehealth/remote availability
- Cost model (free, insurance, sliding scale)
- Last data verification date

### Known Gaps

1. **Comprehensive Dental Directory** - No single database; scattered across VA, state programs, nonprofits
2. **Vision Care Options** - Limited VA coverage; Community Care referral pathway unclear
3. **Telehealth Provider Roster** - Many providers listed on platforms but no exportable database
4. **Community Clinic Veteran-Specific Flags** - FQHCs don't tag veteran patients; requires inference from data
5. **Provider Performance Metrics** - Quality data scattered across VA, CMS, TPAs

---

## Key Contact Information for Data Access

| Organization | Contact Method | Purpose |
|--------------|----------------|---------|
| VA Developer API | https://developer.va.gov/ | Register for API token, Facilities/Facilities+ API |
| HRSA Data Warehouse | https://data.hrsa.gov/tools/web-services | Developer Guide, API token, Health Center data |
| TriWest Healthcare Alliance | https://www.triwest.com/en/provider/ | CCN Region 4-5 provider data, API inquiry |
| Optum Serve | Contact via VA.gov | CCN Region 1-3 provider data, API inquiry |
| 211 United Way | State-specific (e.g., 211md.org) | Resource API integration, data licensing |
| Cohen Veterans Network | https://www.cohenveteransnetwork.org/ | Clinic directory, data for referral integration |

---

## Sources

- [VA Telehealth Services](https://telehealth.va.gov/)
- [VA Community Care](https://www.va.gov/communitycare/)
- [HRSA Data Warehouse](https://data.hrsa.gov/)
- [HRSA Find a Health Center](https://findahealthcenter.hrsa.gov/)
- [VA Developer API Platform](https://developer.va.gov/)
- [VA Facilities API (Data.gov)](https://catalog.data.gov/dataset/va-facilities-api)
- [VHA Medical Facilities (ArcGIS)](https://services2.arcgis.com/VFLAJVozK0rtzQmT/arcgis/rest/services/Veterans_Health_Administration_Medical_Facilities/FeatureServer)
- [211.org United Way](https://register.211.org/)
- [Cohen Veterans Network](https://www.cohenveteransnetwork.org/)
- [Stop Soldier Suicide - ROGER](https://stopsoldiersuicide.org/roger/)
- [Veterans Crisis Line](https://www.veteranscrisisline.net/)
- [VA Dental Care](https://www.va.gov/dental/)
- [VA Mobile Medical Units](https://mobile.va.gov/about)
- [VA Mobile Medical Unit Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC11851793/)
- [Team Red, White & Blue](https://teamrwb.org/)
- [Operation Homefront](https://operationhomefront.org/)
- [NHSC - National Health Service Corps](https://nhsc.hrsa.gov/)
- [VA Vet Centers](https://www.vetcenter.va.gov/)
- [Smiles for Veterans](https://smilesforveterans.org/)
