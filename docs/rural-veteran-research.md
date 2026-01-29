# Rural Veteran Resources Research: Low-Population States

**Date:** January 2026
**Scope:** Wyoming, Montana, North Dakota, South Dakota, Vermont, Alaska, Maine, West Virginia

---

## Executive Summary

Eight rural/low-population states have identified significant coverage gaps in Veteran services, particularly in:

1. **Geographic isolation** - Alaska (no road system), Montana/WY (vast distances), Northern rural areas
2. **Limited telehealth infrastructure** - 27% of rural Veterans lack home internet; cellular coverage gaps
3. **Legal services deserts** - 79% of VA legal clinics in urban areas; limited pro bono capacity
4. **Housing assistance** - Thin HUD-VASH provider networks; limited affordable housing in rural areas
5. **Employment training** - Few VR&E specialists in rural areas; agricultural/forestry focus needed

**High-Value Integration Targets:**
- Alaska & Montana telehealth programs (established federal grants)
- State Veterans Commission data (all 8 states have formal agencies)
- Legal aid organizations (LSC-funded directory)
- Rural housing programs (HUD-VASH, SSVF, Veterans' Homes)

---

## By State: Programs, URLs, Data Formats & Integration Priority

### 1. WYOMING

**State Veterans Agencies:**
- **Wyoming Veterans Commission** - https://wyomingveteranscommission.com
- **Wyoming Department of Workforce Services (Veterans Program)** - https://dws.wyo.gov/dws-division/workforce-center-program-operations/programs/veterans-program/
- **Wyoming Military Department** - https://www.wyomilitary.wyo.gov/resources/veteran/veterans-commission/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| Property Tax Exemption | Housing | $3,000 exemption on primary residence assessed value |
| Veteran Disability Reduction | Housing | $6,000 reduction for 50%+ disabled, with Armed Forces Expeditionary Medal |
| Park Access | Recreation | Free lifetime day-use & camping pass for 50%+ disabled |
| Community College Tuition Waiver | Education | Up to 8 semesters for overseas combat Veterans |
| Workforce Priority Service | Employment | Priority access at 7 Workforce Centers statewide |
| DAV Transportation Grant | Healthcare | Rural county coverage: Big Horn, Carbon, Converse, Crook, Lincoln, Park, Sublette, Sweetwater, Teton, Weston |
| Oregon Trail State Veterans Cemetery | Burial | Free burial for all honorably discharged |

**Housing Resources:**
- **Veterans' Home of Wyoming** (Evansville) - https://health.wyo.gov/aging/veteranshome/ - 120-bed skilled nursing facility

**Rural Challenges:**
- Vast geographic distances (172,000 sq mi, 580k population)
- Limited mental health providers in rural counties
- Transportation grant covers only 10 specific counties

**Data Format Available:**
- Website/directory format; no published API
- Possible web scraping: Veterans Commission, DWS programs
- Contact: Wyoming Veterans Commission for direct data

**Integration Priority:** MEDIUM
- Solid state agency infrastructure
- Limited unique data (mostly federal programs)
- Transportation grant is state-specific, valuable for rural focus

---

### 2. MONTANA

**State Veterans Agencies:**
- **Montana Veterans Affairs Division** (MVAD) - https://dma.mt.gov/mvad/
- **Montana Department of Military Affairs** - https://dma.mt.gov/MVAD/AdministrativeOffice
- **Montana Job Service (Veteran Services)** - https://wsd.dli.mt.gov/job-seeker/veteran-services/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| VSO Network | Outreach | 9 regional offices serving 47+ communities (Belgrade, Billings, Butte, Great Falls, Havre, Helena, Kalispell, Miles City, Missoula) |
| DVOP/LVER Employment | Employment | Disabled Veteran Outreach Program at Job Service locations |
| HUD-VASH | Housing | Rental assistance + VA case management for homeless Veterans |
| HUD-VASH Project-Based | Housing | Freedom's Path at Fort Harrison (permanent supportive housing) |
| Veterans Home Loan Program | Housing | First mortgage funds for MT National Guard/armed forces service members (est. 2011) |
| Telehealth Network (FLEX Grant) | Healthcare | **$300k federal Flex Rural Veterans Health Access grant (3-year cycle)** - Telehealth in 7 rural SE Alaska communities; PTSD/TBI training |
| State Veterans Home | Long-term Care | State-operated facility for eligible Veterans |

**Telehealth Program Details:**
- Funded by VA through Flex Rural Veterans Health Access Program
- Serves Southeast Alaska communities (collaboration with Alaska)
- Trained 150+ community providers on military culture, PTSD, TBI, MST
- 19 providers completed VA-approved PTSD training
- VA digital divide tablet program: cellular-enabled devices for Veterans without internet access

**Rural Challenges:**
- 147,000 sq mi; 1.1M population; many communities lack road access
- Sparse rural mental health providers
- High Veteran population relative to services

**Data Format Available:**
- VSO office locations/contact data: potentially scrapeable from MVAD website
- Biennial reports: https://dma.mt.gov/mvad/biennial-report-2022.pdf
- No API identified; manual data entry or web scraping needed

**Integration Priority:** HIGH
- Established rural outreach network (47+ communities)
- Federal telehealth grant indicates institutional commitment
- Unique VSO collaboration model worth documenting

---

### 3. NORTH DAKOTA

**State Veterans Agencies:**
- **North Dakota Department of Veterans Affairs** - https://www.veterans.nd.gov/
- **ND Job Service (Veterans Resources)** - https://www.jobsnd.com/job-seeker/veterans/resources-veterans
- **Community Action Partnership of ND (SSVF)** - https://www.capnd.org/programsandinitiatives/statewideprograms/supportive-services-for-veteran-families/
- **Legal Services of North Dakota** - https://lsnd.org/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| VET Program | Education | Free Veteran Educational Training; open enrollment; individually tailored |
| Dependent Tuition | Education | Dependents of service members eligible; free tuition at state institutions (up to 45 months/10 semesters) |
| Property Tax Credit | Housing | 50%+ disabled: credit = disability % on first $9,000 property value |
| Service Dog Grant | Healthcare | PTSD-rated Veterans; requires doctor recommendation |
| SSVF (Supportive Services for Veteran Families) | Housing | Rental assistance, utilities, moving expenses, childcare through Community Action Partnership |
| HUD-VASH (Tribal) | Housing | Tribal HUD-VASH for Native American Veterans (homeless/at-risk) |
| Mortgage/Rent/Utilities Assistance | Housing | Multiple state programs (see https://www.veterans.nd.gov/mortgage-rent-utilities-assistance) |
| Legal Assistance | Legal | https://www.veterans.nd.gov/legal-assistance |

**Legal Aid:**
- **Legal Services of North Dakota** - Free legal help to low-income/elderly (60+); housing focus
- **Dakota Plains Legal Services** - Serves ND/SD + 9 tribal nations; free legal aid for low-income, elderly, Veterans

**Rural Challenges:**
- 70,500 sq mi; 750k population; significant rural population density
- Limited legal services in rural areas
- Geographic distance to state offices

**Data Format Available:**
- Website directory format
- Possible scraping: state programs, SSVF partner locations
- Contact legal aid providers directly for service areas

**Integration Priority:** MEDIUM-HIGH
- Solid state infrastructure
- Legal aid has multi-state coverage; valuable for data
- SSVF program data through Community Action Partnership could be integrated

---

### 4. SOUTH DAKOTA

**State Veterans Agencies:**
- **South Dakota Veterans' Programs** - https://dlr.sd.gov/veterans/ (likely state veterans office)
- **Michael J. Fitzmaurice South Dakota Veterans Home** (Hot Springs) - 100-bed facility
- **South Dakota Education Benefits** - https://dlr.sd.gov/veterans/education-benefits/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| Educational Benefits | Education | Free tuition for combat Veterans (1 month per month of qualifying service; min 1, max 4 years) |
| Veterans Upward Bound (VUB) | Education | Helps Veterans improve education skills; free supplies, materials, career/financial aid services |
| Veterans Home | Long-term Care | Michael J. Fitzmaurice Veterans Home (Hot Springs, 100 beds) |
| Upward Bound Program | Education | College preparation assistance |

**Rural Challenges:**
- 77,100 sq mi; 884k population
- Limited rural education access
- Single state Veterans Home may not serve all rural regions

**Data Format Available:**
- Website directory
- Likely scraping from state DLR veterans portal
- Limited unique data published

**Integration Priority:** MEDIUM
- Basic state infrastructure
- Few unique rural-specific programs
- Veterans Home location is useful reference data

---

### 5. VERMONT

**State Veterans Agencies:**
- **Vermont Office of Veterans Affairs** - https://veterans.vermont.gov/
  - Address: 118 State Street, Montpelier, VT 05620-4401
  - Phone: 802-828-3379 / 888-666-9844
- **Contact Info for Supporting Organizations** - https://veterans.vermont.gov/office-veterans-affairs/contact-information-organizations-help-veterans-and-their-families

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| Vermont Veteran Assistance Fund | Financial | One-time up to $500 emergency payment (housing, utilities, critical needs) |
| Property Tax Exemptions | Housing | State tax breaks for Veterans |
| State Employment Preference | Employment | Veteran hiring priority |
| Tuition Assistance | Education | Specialized aid programs |
| Veteran Service Officers | Outreach | Trained officers help apply for federal/state/local benefits |
| Vehicle Tags | Transportation | Veteran-specific license plates |
| Hunting/Fishing Privileges | Recreation | License privileges for Veterans |

**Rural Challenges:**
- 9,600 sq mi; 645k population
- Mountainous terrain isolates rural areas
- Limited urban service hubs (Montpelier, Burlington)
- No published rural-specific programs

**Data Format Available:**
- Website directory; contact information directory
- Possible scraping: office locations, benefit programs
- Email/phone for direct data access

**Integration Priority:** MEDIUM
- Comprehensive state agency
- Limited unique rural-specific programming
- Emergency assistance fund ($500) is niche offering

---

### 6. ALASKA

**State Veterans Agencies:**
- **Alaska Office of Veterans Affairs** - https://veterans.alaska.gov/
- **VA Alaska Health Care System** - https://www.va.gov/alaska-health-care/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| **FLEX Rural Veterans Health Access Grant** | Telehealth | **$300k federal grant (3-year cycle)** - Telehealth network in 7 rural/remote SE Alaska communities |
| Telehealth Training | Healthcare | 150+ community providers trained on military culture, PTSD, TBI, MST; 19 providers PTSD-certified |
| Digital Divide Program | Technology | Cellular-enabled tablets loaned to Veterans without internet access; dispatched to rural villages |
| Benefits Assistance | Outreach | Help filing education, medical, benefits claims; military award processing |
| Anchorage VA Regional Benefit Office | Benefits | https://www.va.gov/anchorage-va-regional-benefit-office-at-colonel-mary-louise-rasmuson-campus-of-the-alaska-va-healthcare-system/ |

**Telehealth Critical Challenges Addressed:**
- **No road system** - Most towns accessible only by boat, small aircraft, snowmobile, dogsled
- **Travel burden** - 1-hour medical visit required 3 days of travel due to airline schedules
- **Internet gaps** - Cellular tablets provided to overcome connectivity barriers
- **Provider shortage** - Rural mental health provider training essential

**Rural Challenges:**
- 665k sq mi (largest US state); 733k population; vast majority in remote villages
- **World-class telehealth challenges** - Geographic isolation unmatched by other states
- Limited internet infrastructure in villages
- High Veteran mental health needs (PTSD, substance use)

**Data Format Available:**
- Website directory; FLEX grant documentation
- Possible scraping: village-level service locations
- Contact Alaska Office Veterans Affairs for detailed service data

**Integration Priority:** VERY HIGH
- **Established telehealth model** for rural isolated communities
- Federal grant shows sustainability
- Unique digital divide solution (tablets) transferable to other states
- Rural challenge exemplar for underserved Veteran populations

---

### 7. MAINE

**State Veterans Agencies:**
- **Bureau of Maine Veterans' Services** - https://www.maine.gov/veterans/
- **Maine Outreach Efforts** - https://www.maine.gov/veterans/outreach-efforts
- **Maine AgrAbility (UM Extension)** - https://extension.umaine.edu/agrability/network-connections/veteran-resources/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| **FLEX Rural Veterans Health Access Grant** | Telehealth | $300k federal grant (shared with Alaska, Montana) - 3-year telehealth expansion cycle |
| Veteran Service Officers | Outreach | 6 field service offices statewide + main office |
| CB0Cs (Community-Based Outpatient Clinics) | Healthcare | 9 locations: Bangor, Calais, Caribou, Fort Kent, Houlton, Lewiston, Lincoln, Portland, Rumford |
| Vet Centers | Mental Health | 5 centers with multiple community access points (Springvale, Portland, Lewiston, Bangor, Caribou) |
| Monthly Podcast | Outreach | "Maine Veterans' Connection Podcast" - Monthly episodes on benefits, programs, employment, mental health |
| Monthly Newsletter | Outreach | Bureau newsletter with state/federal program updates, events, resources |
| Farmer Veteran Program | Agriculture | Maine AgrAbility Farmer Veteran Outreach Coordinator; farming/ag services statewide |
| Current Initiatives | Various | https://www.maine.gov/veterans/current-initiatives |

**Outreach Coverage:**
- 6 field service offices provide rural reach
- CBOCs in northern/coastal communities (Caribou, Fort Kent, Calais, Rumford)
- Farmer veteran focus aligns with rural Maine economy

**Rural Challenges:**
- 35,400 sq mi; 1.3M population; significant rural areas
- Northern/eastern Maine isolated from Portland metro
- Agricultural economy requires farmer-veteran focus
- Limited mental health specialists in rural areas

**Data Format Available:**
- Website directory; CBOC locations
- Podcast/newsletter - RSS feeds or direct listings
- Possible scraping: field office locations, outreach partners
- Contact: Bureau for detailed veteran service provider data

**Integration Priority:** HIGH
- **FLEX grant recipient** - Telehealth infrastructure exists
- **Rural outreach model** (6 field offices, CBOC network, farmer focus) is exemplary
- Podcast/newsletter shows ongoing engagement
- Coverage areas documented for integration

---

### 8. WEST VIRGINIA

**State Veterans Agencies:**
- **West Virginia Department of Veterans Assistance** - https://veterans.wv.gov/
- **West Virginia Veterans' Education & Training (SAA)** - https://www.cfwvconnect.com/veterans-education/

**Key Programs:**
| Program | Type | Details |
|---------|------|---------|
| Veterans Benefit Offices | Outreach | 16 benefit offices statewide; free staff assistance |
| In-State Tuition (GI Bill) | Education | All Veterans eligible for in-state tuition if using GI Bill (must enroll within 3 years of discharge) |
| Medal of Honor/Purple Heart Tuition Waiver | Education | Full tuition waiver for public higher ed institutions |
| Veteran Re-education Stipend | Education | Up to $500/semester for certified post-secondary enrollment |
| Military Incentive Program | Employment | Tax credit to private sector employers who hire Veterans |
| Military Connection Program | Employment | Partnership with Workforce WV + DOL for training/employment opportunities |
| Afghanistan War Bonus | Financial | Cash bonus for Veterans who served in Afghanistan |
| State Parks Discount | Recreation | 10% discount to Veterans at West Virginia State Parks |
| SSVF Program | Housing | Rapid re-housing for Veteran families; homelessness prevention assistance |
| Veterans Nursing Home | Long-term Care | 120,000 sq ft, 120-bed facility in Clarksburg (no Veteran turned away for finances) |

**Rural Network:**
- 16 benefit offices distributed across state
- Strong employment partnership model
- SSVF integrated with housing support

**Rural Challenges:**
- 24,200 sq mi; 1.7M population; Appalachian rural areas
- Limited urban centers (Charleston, Huntington)
- Economic challenges affect affordable housing
- Mental health provider shortage in rural counties

**Data Format Available:**
- Website directory; benefit office locations
- Possible scraping: 16 office locations, SSVF partner contact data
- Contact WV Department Veterans Assistance for program details

**Integration Priority:** MEDIUM
- Solid state infrastructure
- 16-office network provides rural reach
- SSVF integration useful for housing resources
- Limited unique state-specific programs

---

## Cross-State Patterns & Integration Insights

### High-Value Integration Targets

**1. Telehealth Programs (Alaska, Montana, Maine)**
- Federal FLEX Rural Veterans Health Access grant recipients
- Established infrastructure for rural isolation solutions
- Digital divide initiatives (tablets, internet access)
- **Data Approach:** Contact state offices + federal grant documentation

**2. State Veterans Commissions (All 8 States)**
- Formal agencies with mission to serve Veterans
- Likely have office directories, benefit summaries
- Possible web scraping or direct API/data export requests
- **Data Approach:** State website scraping + direct contact for bulk data

**3. Legal Aid Networks (All States)**
- Legal Services Corporation funded programs
- LSC directory: https://www.lsc.gov/
- Multi-state programs (Dakota Plains, Legal Services of ND)
- **Data Approach:** LSC directory + individual legal aid provider websites

**4. Housing Programs (All States)**
- HUD-VASH, SSVF, State Veterans Homes
- Mixed federal/state funding
- **Data Approach:** HUD.gov database + state veteran office directories

**5. Rural Employment/Training (All States)**
- DVOP/LVER programs (federal)
- State-specific vocational programs
- Agricultural focus (Maine AgrAbility model)
- **Data Approach:** State Job Service websites + direct contact

---

## Rural Veteran Challenges Summary

| Challenge | Scale | Affected States | Current Solutions |
|-----------|-------|-----------------|-------------------|
| **Geographic Isolation** | CRITICAL | Alaska, Montana, WY | Telehealth (AL, MT, ME FLEX grants); VSO travel (MT) |
| **Internet Access Gap** | HIGH | Alaska (27% rural lack internet) | Digital divide tablets (VA national program) |
| **Mental Health Shortage** | HIGH | All 8 states | Provider training programs (Alaska/Montana) |
| **Legal Services Desert** | HIGH | All 8 states | LSC-funded legal aid; limited rural capacity (79% clinics urban) |
| **Housing Affordability** | HIGH | All 8 states | HUD-VASH, SSVF, state assistance programs |
| **Employment/Training Access** | MEDIUM | All 8 states | Job Service partnerships; VR&E dispersal |
| **Transportation Costs** | MEDIUM | Alaska, MT, WY | Federal/state transportation assistance; limited |
| **Provider Cultural Competency** | MEDIUM | All 8 states | Training programs (PTSD, TBI, MST awareness) |

---

## Data Integration Strategy

### Priority 1: Web Scraping + Manual Entry
- State veteran office websites (all 8)
- Office location directories
- Benefit program summaries
- Contact information

### Priority 2: Direct Data Requests
- Montana VSO network details (47+ communities)
- Alaska telehealth partner locations
- Maine CBOC network
- West Virginia 16-office network
- Legal aid provider service areas

### Priority 3: Federal APIs + Directories
- VA Facilities API: https://catalog.data.gov/dataset/va-facilities-api
- VA Developer API: https://developer.va.gov/
- LSC Legal Aid Directory: https://www.lsc.gov/
- HUD-VASH Program listings: https://www.hud.gov/

### Priority 4: Specialized Scraping
- FLEX grant documentation (federal)
- State Veterans Home information
- Telehealth partner locations (Alaska, Montana, Maine)

---

## Data Formats Encountered

| Format | States | Approach |
|--------|--------|----------|
| Website Directory | All 8 | Web scraping + manual verification |
| PDF Reports | Montana, others | Manual extraction or OCR |
| Contact Lists | All 8 | Website scraping |
| No Published API | All 8 | Direct contact to state agencies |
| Federal APIs | Multi-state | VA API platform (developer.va.gov) |
| Legal Aid Directory | National (LSC) | LSC.gov database |

---

## Recommended Connector Implementation

1. **Create state veteran agency connectors** for each of 8 states
   - Tier: 3 (State-level authorities)
   - Data source: State websites + direct contact
   - Priority: Medium-High (foundational data)

2. **Create telehealth/rural-specific connector** (Alaska, Montana, Maine focus)
   - Tier: 2 (Federal grant programs with state implementation)
   - Data source: FLEX grant documentation + state health agencies
   - Priority: Very High (unique rural solution)

3. **Integrate legal aid data** via LSC directory + state legal aid websites
   - Tier: 2 (Non-profit legal services, LSC-funded)
   - Data source: LSC.gov + individual provider websites
   - Priority: High (critical gap identified)

4. **Append housing programs** to existing HUD-VASH/SSVF connectors
   - Data source: HUD.gov + state veteran housing offices
   - Priority: Medium (overlap with existing connectors)

---

## Key Sources for Further Research

**Federal:**
- VA Developer API: https://developer.va.gov/
- VA Facilities API: https://catalog.data.gov/dataset/va-facilities-api
- Legal Services Corporation: https://www.lsc.gov/
- HUD Veterans Programs: https://www.hud.gov/

**Telehealth (FLEX Grant):**
- VA Rural Health Resource Centers: https://www.ruralhealth.va.gov/aboutus/vrhrc.asp
- Alaska State Office of Rural Health (AK SORH) - $300k FLEX grant
- Montana Veterans Affairs Division: https://dma.mt.gov/mvad/
- Maine Bureau of Veterans' Services: https://www.maine.gov/veterans/

**State-Specific:**
- Wyoming Veterans Commission: https://wyomingveteranscommission.com
- Montana MVAD: https://dma.mt.gov/mvad/
- North Dakota Veterans Affairs: https://www.veterans.nd.gov/
- Vermont Office of Veterans Affairs: https://veterans.vermont.gov/
- West Virginia Veterans Assistance: https://veterans.wv.gov/

---

## Next Steps

1. **Contact state veteran affairs offices** directly for structured data exports (office locations, programs, contact info)
2. **Access FLEX grant documentation** from Alaska, Montana, Maine for telehealth partnership details
3. **Query LSC directory** for legal aid provider locations and service areas
4. **Build web scrapers** for each state's veteran office website
5. **Map rural Veteran populations** to identify true coverage gaps (geographic + demographic)
6. **Prioritize Alaska model** for documentation as exemplar of rural telehealth solutions

---

**Document Version:** 1.0
**Last Updated:** January 2026
**Prepared For:** Vibe4Vets Rural Veteran Coverage Initiative
