# State Open Data Portals - Veteran Resources Research

**Date:** January 28, 2026
**Issue:** V4V-1juq
**Purpose:** Identify state open data portals publishing veteran-related datasets

---

## Executive Summary

Research reveals that while most U.S. states maintain open data portals, **very few explicitly publish veteran-specific datasets**. The federal level (VA.gov) dominates veteran data publication. State open data portals primarily focus on general economic, demographic, and government operations data rather than veteran-specific resources.

**Key Finding:** Most veteran housing and employment program data is published by federal agencies (VA, HUD, DOL) rather than individual states.

---

## Federal Level Resources (Highest Priority for Integration)

### Department of Veterans Affairs (VA)

| Portal | URL | Veteran Datasets | Format | Frequency | Priority |
|--------|-----|------------------|--------|-----------|----------|
| VA Open Data Portal | https://www.data.va.gov/ | VetPop (population projections), disability compensation by state, VA facility data, benefits utilization | JSON, XML, CSV | Real-time API available | **HIGH** |
| VA API Platform | https://developer.va.gov/ | Facilities API, Benefits API, Health API, Community Care Eligibility | REST API | Continuous | **HIGH** |
| VA.gov Data Portal | https://www.va.gov/data/ | 1,943 published data assets, 217+ data stories | Multiple formats | Ongoing | **HIGH** |
| Data.gov (VA Organization) | https://catalog.data.gov/organization/va-gov | Comprehensive dataset catalog | CSV, JSON, API | Updated regularly | **HIGH** |

**Key Datasets Available:**
- Veteran Population Projection Model (VetPop2023) - state-level projections
- VA Disability Compensation Expenditures by State (FY 2024)
- VA Facility Information (locations, services, contact info)
- Veterans Analysis and Statistics reports
- State Summary Reports (all 50 states + territories)

**API Statistics:** 3.2M API reads, 2.2M page visits, 3.6M downloads (May 2019 - May 2025)

**Data Support:** Contact OITOpenData@va.gov for open data inquiries

---

## State Open Data Portals with Veteran Datasets

### States with Confirmed Veteran Data

#### NEW YORK (Primary State Example)
| Aspect | Details |
|--------|---------|
| Portal | [data.ny.gov](https://data.ny.gov/) |
| Veteran Datasets | • NYC Department of Veterans' Services (DVS) client demographics<br/>• Veteran-Owned Businesses directory<br/>• VetConnect service request cases<br/>• Demographics: gender, race, ethnicity, military affiliation, branch, discharge type |
| Data Format | CSV (available on data.ny.gov) |
| Update Frequency | Annual (calendar year) |
| Coverage | NYC primarily; disaggregated by borough |
| Integration Priority | **MEDIUM** |
| Contact | NYC Department of Veterans' Services |
| Notes | Includes: demographics, income, marital status, postal code; segregated by borough where available |

**Population Context:** 580,856 veterans in NY State (2022)

#### CALIFORNIA (Primary State Example)
| Aspect | Details |
|--------|---------|
| Portal | [data.ca.gov](https://data.ca.gov/) |
| Veteran Datasets | • California Veterans Workforce 2024 report<br/>• Labor market statistics for veterans<br/>• Career resources dashboard<br/>• Housing programs (CalVet data)<br/>• Employment Development Department (EDD) data |
| Data Format | CSV, Excel, API access via EDD |
| Update Frequency | Annual (workforce data), ongoing (programs) |
| Coverage | Statewide |
| Integration Priority | **MEDIUM** |
| Contact | California Employment Development Department (EDD)<br/>California Department of Veterans Affairs (CalVet) |
| Key Programs | • CalVet Residential Enriched Neighborhood (CREN) program<br/>• HUD-VASH partnerships<br/>• Permanent loan financing data<br/>• Career Resource Zone (employment services) |

**Population Context:** ~1.9 million veterans in California

**Housing Data Available:**
- CalVet permanent loan financing ($580.5M awarded to 99 projects)
- 6,561 units of affordable housing (completed/in-process)
- HUD-VASH program partnerships

---

#### VIRGINIA (Confirmed Open Data Portal)
| Aspect | Details |
|--------|---------|
| Portal | [data.virginia.gov](https://data.virginia.gov/) |
| Features | • 31,000+ Commonwealth datasets<br/>• API access available<br/>• REST API for web/mobile applications |
| Veteran Datasets | Limited explicit veteran datasets found; primarily general state data |
| Integration Priority | **LOW-MEDIUM** |
| Notes | Portal infrastructure strong; veteran-specific datasets need verification |

---

#### WASHINGTON STATE (Confirmed Open Data Portal)
| Aspect | Details |
|--------|---------|
| Portal | [data.wa.gov](https://data.wa.gov/) |
| Geo Data Portal | [geo.wa.gov](https://geo.wa.gov/) |
| Features | • Tabular data, visualizations, API access<br/>• Geospatial data via Geo.wa.gov |
| Veteran Datasets | Limited veteran-specific datasets found; general state data available |
| Integration Priority | **LOW-MEDIUM** |

---

#### ILLINOIS (Confirmed Open Data Portal)
| Aspect | Details |
|--------|---------|
| Portal | [data.illinois.gov](https://data.illinois.gov/) |
| Veteran Datasets | Department of Veterans Affairs reference datasets |
| Data Format | API available |
| Integration Priority | **LOW-MEDIUM** |
| Notes | Requires direct portal search for specific veteran datasets |

---

#### PENNSYLVANIA (Confirmed Open Data Portal)
| Aspect | Details |
|--------|---------|
| Portal | [data.pa.gov](https://data.pa.gov/) |
| Features | • Developer resources<br/>• Data API access |
| Veteran Datasets | Not confirmed in research |
| Integration Priority | **LOW** |
| Notes | Portal exists; specific veteran datasets need verification |

---

### States with Confirmed Agencies (Data Availability Uncertain)

| State | Agency | Website | Data Status | Priority |
|-------|--------|---------|-------------|----------|
| North Carolina | Department of Military & Veterans Affairs (DMVA) | [milvets.nc.gov](https://milvets.nc.gov/) | Database exists; CSV/JSON format unknown | **MEDIUM** |
| North Carolina | DHHS Veterans' Services | [ncdhhs.gov/assistance/veterans-services](https://www.ncdhhs.gov/assistance/veterans-services) | Services directory; no confirmed open data | LOW |
| Georgia | Department of Veterans Service | Contact state directly | Likely limited open data | **MEDIUM** |
| Texas | Texas Veterans Commission | [texas.gov](https://www.texas.gov/texas-open-data-portal/) | State open data portal exists; veteran data not confirmed | LOW-MEDIUM |
| Florida | Multiple veteran agencies | Contact state directly | No confirmed veteran open data | LOW |
| Oregon | State veteran agencies | Contact state directly | Oregon data available via VA.gov state summary | LOW |
| Maryland | State veteran agencies | Contact state directly | No confirmed veteran open data | LOW |
| Arizona | State veteran agencies | Contact state directly | No confirmed veteran open data | LOW |
| Massachusetts | State veteran agencies | Contact state directly | No confirmed veteran open data | LOW |

---

## Alternative Federal Data Sources for State-Level Veteran Data

### National Center for Veterans Analysis and Statistics (NCVAS)
- **Portal:** https://www.va.gov/vetdata/
- **Data:** State Summary Reports for all 50 states + territories
- **Format:** PDF reports, statistical tables
- **Frequency:** Updated annually
- **Includes:** Veteran population, demographics, benefits utilization, employment statistics
- **Priority:** **HIGH** (complementary to direct state data)

### Census Bureau - American Community Survey (ACS)
- **Datasets:** Veteran population, demographics, employment, income, disability
- **Granularity:** State, county, metro area levels
- **Format:** API, downloadable data files
- **Frequency:** Annually (rolling data)
- **Priority:** **HIGH** (demographics & economic indicators)

### HUD Veterans Data Central
- **Portal:** https://veteransdata.info/
- **Data:** Social, economic, and housing characteristics by state
- **Format:** Interactive dashboards, downloadable reports
- **Coverage:** All U.S. states
- **Priority:** **HIGH** (housing-focused)

### RAND Veterans Data Hub
- **Portal:** https://www.rand.org/education-employment-infrastructure/centers/veterans-policy-research/research/data-hub.html
- **Data:** National datasets with veteran indicators
- **Format:** Codebooks, downloadable datasets
- **Priority:** **MEDIUM** (research-focused, less current)

### HUD-VASH Program Data
- **Source:** HUD.gov / VA.gov
- **Data:** HUD-VASH award winners by state, housing support numbers
- **Format:** Reports, public databases
- **Frequency:** Updated as awards change
- **Priority:** **MEDIUM** (housing-specific)

### Department of Labor (DOL)
- **CareerOneStop API:** https://www.careeronestop.org/Developers/WebAPI/web-api.aspx
- **Data:** Veteran employment resources, training programs by state
- **Format:** REST API, JSON
- **Priority:** **HIGH** (employment & training focus)

---

## Data Integration Recommendations

### Tier 1: Implement Immediately (Federal Level)
1. **VA.gov Open Data Portal** - Core veteran statistics, facilities data
2. **VA API Platform** - Real-time facility and benefits data
3. **Census ACS** - Demographic baseline data
4. **DOL CareerOneStop API** - Employment/training resources

### Tier 2: Pursue State Partnerships
1. **New York (data.ny.gov)** - NYC DVS client demographics, VetConnect cases
2. **California (data.ca.gov)** - Workforce statistics, housing program data
3. **North Carolina (milvets.nc.gov)** - Contact for data access agreements
4. **Other major states** - Contact veteran agencies directly for API/CSV access

### Tier 3: Indirect Integration
1. **HUD Veterans Data Central** - Housing characteristic data
2. **NCVAS State Summaries** - Population and benefits data
3. **State open data portals** - Monitor for new veteran datasets

---

## Barriers to State-Level Veteran Data Publication

### Key Findings:
1. **Limited explicit publication:** Most states lack dedicated veteran data APIs
2. **Fragmented governance:** Veteran services split between multiple agencies (VA, DHHS, workforce boards)
3. **Privacy concerns:** Client-level data often restricted
4. **Format inconsistency:** No standardized state data formats
5. **API rarity:** Few states expose veteran data via REST APIs
6. **Manual export required:** Most state data requires direct contact and CSV export negotiation

### Recommendation:
**Focus on federal APIs first, then contact state veteran agencies directly for data sharing agreements.**

---

## Research Findings Summary Table

| Data Source | Type | Scope | Format | API | Difficulty | Priority |
|-------------|------|-------|--------|-----|-----------|----------|
| VA.gov Open Data | Federal | Population, benefits, facilities | JSON, CSV, XML | Yes | Easy | **HIGH** |
| VA Developer API | Federal | Facilities, benefits, health | REST API | Yes | Easy | **HIGH** |
| DOL CareerOneStop | Federal | Employment, training, occupations | REST API | Yes | Easy | **HIGH** |
| Census ACS | Federal | Demographics, employment, income | API, CSV | Yes | Moderate | **HIGH** |
| HUD Veterans Data Central | Federal | Housing, social services | Dashboard, reports | Limited | Moderate | **MEDIUM** |
| data.ny.gov (NYC DVS) | State | Veterans demographics, business directory | CSV | No | Moderate | **MEDIUM** |
| data.ca.gov (CalVet/EDD) | State | Workforce, housing, employment | CSV, partial API | Limited | Moderate | **MEDIUM** |
| data.virginia.gov | State | General state data (veteran subset unknown) | API, CSV | Yes | High | LOW-MEDIUM |
| State veteran agencies (direct) | State | Varies by agency | Usually CSV | Rare | High | **MEDIUM** |
| NCVAS State Summaries | Federal | Population, benefits (state-level) | PDF, tables | No | Moderate | **MEDIUM** |

---

## Next Steps for Vibe4Vets

1. **Implement federal APIs first:**
   - VA.gov data import (high reliability, Tier 1 source)
   - DOL CareerOneStop connector (employment/training focus)
   - Census ACS demographics (population baseline)

2. **Contact high-priority states:**
   - NYC Department of Veterans' Services (for client demographics/data sharing)
   - California CalVet & EDD (for housing/workforce programs)
   - North Carolina DMVA (for state-level program data)

3. **Monitor state portals:**
   - data.ny.gov, data.ca.gov, data.virginia.gov, data.wa.gov, data.illinois.gov, data.pa.gov
   - Subscribe to updates for new veteran datasets

4. **Establish data sharing agreements:**
   - Contact state veteran affairs agencies directly
   - Request CSV/JSON exports of program directories
   - Negotiate update frequencies

---

## Sources

- [Department of Veterans Affairs Open Data Portal](https://www.data.va.gov/)
- [VA Developer API](https://developer.va.gov/)
- [Data.gov VA Datasets](https://catalog.data.gov/organization/va-gov)
- [National Center for Veterans Analysis and Statistics](https://www.va.gov/vetdata/)
- [New York Data Portal](https://data.ny.gov/)
- [California Data Portal](https://data.ca.gov/)
- [Virginia Open Data Portal](https://data.virginia.gov/)
- [Washington State Open Data Portal](https://data.wa.gov/)
- [Illinois Open Data](https://data.illinois.gov/)
- [Pennsylvania Open Data Portal](https://data.pa.gov/)
- [HUD Veterans Data Central](https://veteransdata.info/)
- [RAND Veterans Data Hub](https://www.rand.org/education-employment-infrastructure/centers/veterans-policy-research/research/data-hub.html)
- [DOL CareerOneStop API](https://www.careeronestop.org/Developers/WebAPI/web-api.aspx)
- [North Carolina DMVA](https://www.milvets.nc.gov/)
- [Census Bureau - American Community Survey](https://www.census.gov/)
- [HAC Veterans Data Central - State Summaries](https://veteransdata.info/)

