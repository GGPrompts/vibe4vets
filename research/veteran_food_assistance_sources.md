# Veteran Food Assistance Data Sources Research

**Date:** January 2026
**Issue:** V4V-yj1y
**Status:** Research Complete

---

## Executive Summary

This document provides a comprehensive list of organizations and programs providing food assistance to Veterans, with data availability, format, and integration priority ratings. Data sources range from official government APIs to nonprofit directories and regional programs.

---

## Primary Data Sources & Programs

### Tier 1: Official Government Programs & APIs

#### 1. VA Food Security Office (VHA)
- **Organization:** U.S. Department of Veterans Affairs
- **URL:** https://www.nutrition.va.gov/food_insecurity.asp
- **Data Format:** Web portal with referrals to local resources
- **Data Integration:** Limited - primarily informational; integrates with VA social worker network
- **Integration Priority:** HIGH
- **Notes:**
  - Integrated into VA healthcare delivery system
  - Veterans can discuss food insecurity with primary care providers
  - Social workers connect Veterans with VA and local resources
  - No public API available
  - **Potential Integration:** Could scrape VA facility locations and their food security partnerships

#### 2. USDA Food and Nutrition Service (FNS)
- **Organization:** U.S. Department of Agriculture
- **URL:** https://www.fns.usda.gov/military-veteran
- **Data Format:** Web resources, state directories, SNAP state contacts
- **Data Integration:** Limited API; FNS maintains state contact directories
- **Integration Priority:** HIGH
- **Notes:**
  - Operates SNAP (Supplemental Nutrition Assistance Program) outreach to Veterans
  - 1.2 million Veterans receive SNAP benefits
  - Military OneSource provides resource aggregation
  - Partners with VA Readjustment Counseling Service (300+ centers, 70 mobile centers)
  - **Potential Integration:** SNAP state directories, partner agency lists, food bank network partnerships

#### 3. USDA FoodData Central
- **Organization:** USDA National Agricultural Library
- **URL:** https://fdc.nal.usda.gov/
- **API Endpoint:** https://fdc.nal.usda.gov/api-guide/
- **Data Format:** REST API (JSON)
- **Integration Priority:** MEDIUM
- **Notes:**
  - Provides Standard Reference (SR) Legacy data and current branded foods database
  - Endpoints: Food Search, FDC Lists
  - Good for nutritional information but not Veteran-specific
  - **Use Case:** Enrichment data for food bank program nutritional content

#### 4. VA Developer API Platform
- **Organization:** U.S. Department of Veterans Affairs
- **URL:** https://developer.va.gov/
- **Data Format:** REST API (multiple endpoints)
- **Integration Priority:** MEDIUM
- **Current Capabilities:** Facilities, services, health information
- **Notes:**
  - Does NOT currently have dedicated food program endpoints documented
  - Food Security Office exists but no API endpoint yet
  - **Recommendation:** Contact VA developer relations for potential nutrition/food security API roadmap

---

### Tier 2: Major Nonprofit Networks & Directories

#### 5. Feeding America Network
- **Organization:** Feeding America
- **URLs:**
  - Main: https://www.feedingamerica.org/
  - Data Commons: https://datacommons.feedingamerica.org/
  - Find Food Bank: https://www.feedingamerica.org/find-your-local-foodbank
  - Veteran Resources: https://www.feedingamerica.org/hunger-in-america/food-insecurity-in-veterans
- **Network:** 200 food banks + 60,000+ food pantries (6.6B meals/year to 40M people)
- **Data Format:**
  - Web directory (searchable by ZIP code)
  - Data Commons platform with dashboards
  - GitHub repositories with API/data tools
- **Integration Priority:** HIGH
- **GitHub Repositories:**
  - FTF RE API: https://github.com/feedingamerica/ftf-re-api (Django/MySQL)
  - FreshTrak: https://github.com/feedingamerica/freshtrak-public (Food bank appointment system)
  - FreshTrak Registration API: https://github.com/feedingamerica/freshtrak-registration-api
- **Notes:**
  - Partners with VA on Veterans Pantry Pilot (VPP) program at VA Medical Centers
  - 3,000+ Veteran households served through VPP
  - 151,453+ lbs of food distributed through VPP pilot
  - Service Insights (SIMC) platform allows data export to Excel by partner food banks
  - **Potential Integration:**
    - Scrape "Find Your Local Food Bank" directory by state
    - Contact for Data Commons API access
    - Integrate GitHub-hosted FreshTrak data tools

#### 6. Meals on Wheels America
- **Organization:** Meals on Wheels America
- **URL:** https://www.mealsonwheelsamerica.org/
- **Program:** "Helping Homebound Heroes" - dedicated Veteran program
- **Data Format:** Directory of local franchises (searchable on website)
- **Integration Priority:** HIGH (for homebound/older Veterans)
- **Regional Programs with Veteran Focus:**
  - Meals On Wheels of Tarrant County (TX): https://mealsonwheels.org/veteran/
  - LifeCare Alliance (OH): VSC Meals program
  - Meals on Wheels Atlanta (GA): https://www.mowatl.org/veterans
- **Notes:**
  - 2,000+ Veterans served through "Helping Homebound Heroes"
  - Funded by The Home Depot Foundation
  - Focus on homebound and older Veterans
  - **Potential Integration:**
    - Aggregate state/regional programs
    - Map to VA facility locations for referral partnerships
    - No centralized API; requires state-level directory scraping

#### 7. 211.org (United Way Network)
- **Organization:** United Way (National Helpline)
- **URL:** https://211.org/
- **Data Format:** Community Resource Database (7,000+ agencies/services per state)
- **Integration Priority:** HIGH (multi-service directory)
- **Regional Instances:**
  - PA 211: https://www.pa211.org/get-help/veterans/
  - 211 Maryland: https://211md.org/resources/veterans/
  - 211 Texas: https://unitedwayhouston.org/what-we-do/211-texas-united-way-helpline/
  - Nevada 211: https://www.nevada211.org/food-services/
  - 211LA: https://211la.org/
- **Data Integration:** Limited - trained specialists provide referrals; no documented public API
- **Notes:**
  - Handles utility, housing, food, benefits assistance
  - Veteran-focused specialists in major states
  - ~40-50 state variations with different databases
  - **Recommendation:** Contact national office about data sharing/API access for food assistance records

---

### Tier 3: Veteran-Focused Food Programs

#### 8. Feed Our Vets
- **Organization:** Feed Our Veterans Inc. (501(c)(3))
- **URL:** https://feedourvets.org/
- **Contact:** 502 Broad St, Utica, NY 13501 | info@feedourvets.org
- **Coverage:** 43 states + DC + Puerto Rico
- **Data Format:** Web directory (no public API)
- **Integration Priority:** HIGH
- **Impact:** 75,000+ Veterans served since 2009
- **Notes:**
  - Provides free food assistance to Veterans and active-duty members
  - No documented API or data export capability
  - **Potential Integration:**
    - Contact for monthly distribution event locations/schedules
    - Regional program partnership data

#### 9. Meals for Vets
- **Organization:** Meals for Vets
- **URL:** https://mealsforvets.org/
- **Focus:** Texas Veterans under age 60
- **Contact:** info@mealsforvets.org | 830-992-3375
- **Data Format:** Web application with application portal
- **Integration Priority:** MEDIUM (regional)
- **Notes:**
  - Provides consistent access to healthy, nutritious meals
  - For Veterans struggling financially who don't qualify for other programs
  - No public API
  - **Potential Integration:**
    - Veteran eligibility program (Texas regional)
    - Contact for geographic coverage data

#### 10. Disabled Veterans National Foundation (DVNF)
- **Organization:** Disabled Veterans National Foundation
- **URL:** https://www.dvnf.org/veteran-food-assistance-program/
- **Program:** Veteran Food Assistance Program (VFAP)
- **Data Format:** Grant program (one-time food/household support)
- **Integration Priority:** MEDIUM
- **Notes:**
  - Provides one-time grant of essential food and household support
  - Grant-based program, not ongoing food assistance
  - **Potential Integration:**
    - Application/eligibility information for emergency food assistance

#### 11. Soldiers' Angels
- **Organization:** Soldiers' Angels
- **URL:** https://soldiersangels.org/get-support/food-assistance/
- **Data Format:** Event-based distribution directory
- **Integration Priority:** MEDIUM
- **Program:** Monthly drive-through food distribution events
- **Coverage Cities:** Atlanta, Charleston, Cincinnati, Dallas, Denver, Orlando, San Antonio, Washington DC
- **Event Format:** ~75 lbs of food per participant (fresh produce, meats, pantry items)
- **Notes:**
  - Event-based model; requires regular calendar updates
  - **Potential Integration:**
    - Event calendar scraping
    - Location-based food distribution finder

#### 12. Bob Woodruff Foundation
- **Organization:** Bob Woodruff Foundation
- **Program:** Food Help NYC
- **URL:** https://bobwoodrufffoundation.org/our-veterans-nyc/food-help-nyc/
- **Data Format:** NYC-specific resource aggregation
- **Integration Priority:** LOW (regional NYC focus)
- **Notes:**
  - Provides free food locations including food pantries and soup kitchens
  - Searchable by ZIP code
  - NYC-regional only

---

### Tier 4: Regional Food Bank Programs with Veteran Focus

#### 13. Regional Food Bank Programs (State Networks)
- **General URL Pattern:** State food bank networks
- **Data Format:** State-specific directories and programs
- **Integration Priority:** MEDIUM-HIGH (scales with state population)
- **Examples:**

| Food Bank | State | Veteran Program | URL |
|-----------|-------|-----------------|-----|
| Arizona Food Bank Network | AZ | Military Hunger | https://azfoodbanks.org/military-hunger/ |
| Community Harvest Food Bank | IL | Hope for Heroes | https://www.communityharvest.org/about-us/programs/hope-for-heroes/ |
| Central Pennsylvania Food Bank | PA | MilitaryShare | https://www.centralpafoodbank.org/who-we-are/our-programs/militaryshare/ |
| Central Texas Food Bank | TX | Veteran Partnerships | https://www.centraltexasfoodbank.org/news/new-partnership-feeds-veterans |
| Los Angeles Food Bank | CA | VA Health System Pantries | Food pantries at VA Greater Los Angeles health care |
| North Country Food Bank | NY | Partner Agency Network | https://www.northcountryfoodbank.org/partner-agency-resource-hub/ |
| Capital Area Food Bank | DC | Data Tools | https://www.capitalareafoodbank.org/partners/partner-resources/data-collection-tools-and-resources/ |

- **Notes:**
  - Most state food banks have dedicated Veteran programs
  - Data quality varies by state
  - Some provide spreadsheet exports via Service Insights (Feeding America SIMC)
  - **Potential Integration:**
    - Federated model: contact all state food bank networks
    - Service Insights data export (requires partner status with Feeding America)

---

### Tier 5: Supporting Resources & Reference Data

#### 14. Rock and Wrap It Up
- **Organization:** Rock and Wrap It Up
- **Program:** Feed the Veterans
- **URL:** https://www.rockandwrapitup.org/feed-the-veterans
- **Data Format:** Non-profit partnership directory
- **Integration Priority:** LOW
- **Notes:** Celebrity-driven Veteran food assistance initiative; limited structural data

#### 15. Blue Star Families
- **Organization:** Blue Star Families
- **URL:** https://bluestarfam.org/food-insecurity-resources/
- **Data Format:** Aggregated resources for military families
- **Integration Priority:** LOW
- **Notes:** Focuses on active-duty and military families (broader than Veterans)

#### 16. Military OneSource
- **Organization:** U.S. Department of Defense
- **URL:** https://www.militaryonesource.mil/resources/millife-guides/food-security-resources-and-support-programs/
- **Data Format:** Resource guide for food security
- **Integration Priority:** MEDIUM (for active-duty transition)
- **Notes:** Good for Veterans transitioning from active duty

---

## API & Data Integration Opportunities

### High-Priority Integrations

| Priority | Source | Integration Method | Effort | Notes |
|----------|--------|-------------------|--------|-------|
| **HIGH** | Feeding America Directory | Web scraping by ZIP | Low | Direct scrape of state/region listings |
| **HIGH** | Feeding America Data Commons | API (contact) | Medium | Request data access to veteran program metrics |
| **HIGH** | VA Food Security Office | Facility reference data | Low | VA facility locations + food security partnerships |
| **HIGH** | USDA FNS State Contacts | Directory scraping | Low | SNAP outreach program locations by state |
| **HIGH** | Feed Our Vets | Monthly event schedule | Low | Contact for event location/date data |
| **MEDIUM** | Regional Food Bank Networks | Federated state scraping | Medium | 50+ state networks; coordinate outreach |
| **MEDIUM** | 211.org Network | State API access | High | Request food assistance database access (varies by state) |
| **MEDIUM** | Meals on Wheels America | State franchise directory | Medium | Regional program aggregation |
| **MEDIUM** | Soldiers' Angels Events | Calendar/event data | Low | Maintain event distribution calendar |
| **LOW** | USDA FoodData Central | Enrichment API | Low | Supplement with nutritional data (if needed) |

---

## Data Collection Recommendations

### Phase 1: Quick Wins (Week 1)
1. **Scrape Feeding America ZIP-code lookup** - Build automated scraper for local food bank directory
2. **VA facility + food security partnerships** - Map VA Medical Centers with food security services
3. **SNAP state directory aggregation** - Collect state SNAP office contacts and hours
4. **Feed Our Vets event calendar** - Monthly distribution events by city

### Phase 2: Medium Effort (Week 2-3)
1. **Contact Feeding America Data Commons** - Request data access agreement for Veteran program metrics
2. **Regional food bank network outreach** - Coordinate with major state networks (TX, CA, NY, PA, etc.)
3. **211.org national office engagement** - Explore food assistance database data sharing
4. **Regional Meals on Wheels aggregation** - Compile Veteran-focused franchises by state

### Phase 3: Ongoing Maintenance
1. **Monthly event updates** - Soldiers' Angels and other event-based programs
2. **State contact directory sync** - USDA FNS, SNAP office changes
3. **Food bank partnership monitoring** - New Veteran programs, program changes
4. **Data freshness tracking** - Monitor source reliability, track verification dates

---

## Data Quality & Trust Scoring

### Source Tier Recommendations

| Tier | Score | Examples | Rationale |
|------|-------|----------|-----------|
| **1 (Tier 1)** | 1.0 | VA.gov, USDA FNS, Feeding America | Official government + largest nonprofit network |
| **2 (Tier 2)** | 0.85 | Regional food banks (state networks), Meals on Wheels | Established nonprofits, state-recognized |
| **3 (Tier 3)** | 0.7 | Regional Veteran programs, Feed Our Vets | Specialized Veteran focus but smaller reach |
| **4 (Tier 4)** | 0.6 | Event-based programs, local initiatives | Limited geographic scope, event-driven |

---

## Next Steps

### Recommended Connector Development

1. **Create `veteran_food_programs.py` Connector** (High Priority)
   - Scrapes Feeding America ZIP lookup
   - Aggregates regional food bank Veteran programs
   - Tracks Soldiers' Angels events
   - Integrates SNAP outreach locations

2. **Reach out to Data Partners** (Medium Priority)
   - Feeding America Data Commons - request API access
   - 211.org national office - explore food assistance data sharing
   - Regional food bank networks - request bulk program data

3. **Build VA Health Integration** (Medium Priority)
   - Reference VA Medical Center locations with food security services
   - Create location-based referral for food insecurity screening

4. **SNAP Outreach Program** (High Priority)
   - Collect state SNAP office information
   - Cross-reference with Veteran populations by state
   - Integrate eligibility determination

---

## References

### Official Government Resources
- [VA Food Security Office](https://www.nutrition.va.gov/food_insecurity.asp)
- [USDA FNS Military & Veterans](https://www.fns.usda.gov/military-veteran)
- [USDA FoodData Central API](https://fdc.nal.usda.gov/api-guide/)
- [VA Developer API Platform](https://developer.va.gov/)

### Major Nonprofit Networks
- [Feeding America](https://www.feedingamerica.org/)
- [Feeding America Data Commons](https://datacommons.feedingamerica.org/)
- [Feeding America GitHub](https://github.com/feedingamerica)
- [Meals on Wheels America](https://www.mealsonwheelsamerica.org/)
- [211.org](https://211.org/)

### Veteran-Focused Programs
- [Feed Our Vets](https://feedourvets.org/)
- [Meals for Vets](https://mealsforvets.org/)
- [Disabled Veterans National Foundation](https://www.dvnf.org/)
- [Soldiers' Angels](https://soldiersangels.org/)
- [Bob Woodruff Foundation](https://bobwoodrufffoundation.org/)

### Research & Data
- [RAND: Food Insecurity Among Veterans](https://www.rand.org/pubs/research_reports/RRA1363-2.html)
- [Center on Budget & Policy Priorities: SNAP & Veterans](https://www.cbpp.org/research/food-assistance/snap-helps-12-million-veterans-with-low-incomes-including-thousands-in)

---

**Document prepared:** January 28, 2026
**Research conducted using:** Web search, API documentation review, organizational website analysis
**Status:** Ready for connector development and data integration planning
