# Faith-Based Veteran Services Data Sources

Research compiled: January 28, 2026

This document identifies faith-based organizations providing Veteran services with available data sources, API access, and integration priorities for Vibe4Vets.

## Executive Summary

Faith-based organizations operate some of the largest networks of Veteran services in the United States, particularly in housing, emergency assistance, and transitional support. However, data access varies significantly:

- **Tier 1 Organizations** (national scope, structured data): Salvation Army, Catholic Charities USA, Volunteers of America, Lutheran Services America
- **Tier 2 Organizations** (regional networks, partial data): Individual Salvation Army locations, Methodist Services, Presbyterian Church networks
- **Tier 3 Organizations** (faith-based advocacy): Jewish War Veterans, National Coalition for Homeless Veterans, Operation We Are Here
- **Data Access Challenge**: Most faith-based organizations lack public APIs; data collection requires scraping local websites or partnering with HMIS systems

---

## Primary Faith-Based Veteran Service Organizations

### 1. The Salvation Army

**National Headquarters**
- URL: https://www.salvationarmyusa.org/usn/serve-veterans/
- Contact: Serve Veterans programs information available through regional offices

**Veterans Programs**
- Veterans and Family Center (VFC) - transitional housing, substance use disorder treatment, family reunification
- SAVE Program (Veterans Enrichment) - permanent housing with comprehensive case management for chronically homeless, disabled Veterans
- Emergency assistance programs (rent, utilities, food)
- Job training and employment services

**Data Format**
- No public API for Veteran services locations
- Individual locations maintain their own web pages
- HMIS integration available through housing programs
- Regional data accessible through local Salvation Army offices

**Regional Centers**
- North Texas Veteran Programs: https://salvationarmyntx.org/north-texas/veteran-programs/
- Phoenix Veteran Services: https://www.salvationarmyphoenix.org/veteran-services
- Southern Nevada: https://www.salvationarmysouthernnevada.org/veteran-services
- Florida (Palm Beach): https://westpalmbeach.salvationarmyflorida.org/Palm-Beach-County/veterans-programs/
- Freedom Center/Harbor Light: https://centralusa.salvationarmy.org/freedom/serve-veterans-1/

**Integration Priority: HIGH**
- Large national footprint with Veterans programs in all states
- Direct SSVF and HUD-VASH partnership capability
- Challenge: No centralized data feed; requires aggregate scraping or partnership

**Recommended Approach**
- Partner with national headquarters for regional listing data
- Scrape individual location pages for services offered
- Cross-reference with HMIS system for housing program data
- Contact: Headquarters at 2050 Ballenger Ave, Alexandria, VA 22314

---

### 2. Catholic Charities USA

**National Headquarters**
- URL: https://www.catholiccharitiesusa.org/
- Address: 2050 Ballenger Ave, Suite 400, Alexandria, VA 22314

**Veteran Services Network**
- 1,700+ local Catholic Charities agencies nationwide
- Military Families and Veteran Services: https://www.catholiccharitiesusa.org/category/military-families-and-veteran-services/
- Supportive Services for Veteran Families (SSVF) programs

**Services Provided**
- One-on-one case management
- Housing assistance and placement
- Emergency assistance (rent, utilities)
- Employment and budgeting education
- Healthcare navigation
- Legal services referrals

**Regional Examples**
- Catholic Charities Atlanta: https://catholiccharitiesatlanta.org/services/veteran-services/
- Paterson, NJ (SSVF): https://ccpaterson.org/veterans
- Kansas City-St. Joseph: https://catholiccharities-kcsj.org/veteran-services/
- Southern Missouri: https://ccsomo.org/veteran-services/

**Data Format**
- No centralized public API
- Local agencies maintain independent websites
- SSVF programs integrate with HMIS
- Referrals available through national office

**Integration Priority: HIGH**
- Second-largest faith-based Veteran services network
- Strong SSVF program participation
- Local autonomy requires distributed scraping approach

**Recommended Approach**
- Contact national headquarters for list of SSVF-participating agencies
- Scrape agency websites for location and services data
- Focus on SSVF programs for structured data
- Archive: https://stories.catholiccharitiesusa.org/serving-those-who-serve/index.html

---

### 3. Volunteers of America (VOA)

**National Organization**
- URL: https://www.voa.org/
- Homepage: https://www.voa.org/services/supportive-services-for-veterans-and-their-families/
- History: Serving Veterans since World War I

**Veteran Services Programs**
- Flexible continuum of housing (studios, 1-4 bedroom units)
- SSVF programs funded by VA
- Transitional housing programs
- Supportive services for Veteran families
- 24/7 case management in some programs

**Regional Affiliates with Veteran Programs**
- VOA Ohio & Indiana: https://www.voaohin.org/services/veteran-housing/
- VOA Mid-States: https://www.voamid.org/services/veterans-services/
- VOA Michigan: https://www.voami.org/services/veteran-services/
- VOA Chesapeake: https://www.voachesapeake.org/services/veteran-services/
- VOA Los Angeles: https://voala.org/services/veterans/
- VOA Greater New York: https://www.voa-gny.org/services/veterans/ (700+ Veterans/year)
- VOA Florida: https://www.voaflorida.org/services/veteran-services/ (largest Veteran housing provider in Florida, 19 communities)
- VOA Southeast Louisiana: https://www.voasela.org/services/veterans-transitional-housing/ (24-month program)
- VOA Northern States: https://www.voans.org/services/affordable-housing/
- VOA New Jersey/Chesapeake: https://www.voachesapeake.org/services/veteran-services/

**Data Format**
- Distributed regional websites
- SSVF program data available through VA HMIS integration
- No national API; requires local contact or scraping

**Integration Priority: HIGH**
- One of largest private Veteran housing providers
- Extensive national footprint
- SSVF partnership provides structured data opportunity

**Recommended Approach**
- Scrape main landing page for affiliate list
- Collect individual affiliate program data
- Leverage SSVF reporting requirements for consistent data
- Contact: National office at main website

---

### 4. Lutheran Services in America

**National Organization**
- URL: https://lutheranservices.org/
- Member Organizations: 300+ Lutheran health and human services organizations
- Headquarters: Washington, DC

**Veteran Services**
- Reintegration support programs
- Personal and financial counseling
- Caregiver support services
- Housing assistance and placement
- Minnesota Service CORE program (Casework, Outreach, Referral, Education)

**Notable Regional Programs**
- Lutheran Social Service of Minnesota: https://www.lssmn.org/services/military-and-veterans
- Lutheran Military Veterans and Families Ministries, Inc.: https://lmvfm.org/ (national focus)
- Lutheran Services financial assistance: https://www.needhelppayingbills.com/html/lutheran_social_ministry_finan.html

**Data Format**
- Member organizations operate independently
- Lutheran Military Veterans and Families Ministries provides some centralized data
- HMIS integration available for housing programs
- Directory of services available through national network

**Integration Priority: MEDIUM-HIGH**
- 300+ member organizations with distributed services
- Strong focus on reintegration and counseling
- Partnership potential through national organization

**Recommended Approach**
- Contact Lutheran Services in America central office
- Research Lutheran Military Veterans and Families Ministries for national coordination
- Identify state-level affiliates with structured programs
- Scrape LMVFM funding and program pages

---

### 5. Jewish War Veterans (JWV)

**Organization**
- URL: https://www.jwv.org/
- Foundation: https://jwvfoundation.org/

**Services & Programs**
- Membership benefits and fellowship (annual meetings, seminars, events)
- VA benefits advocacy and counseling (National Service Officers)
- Volunteer service at VA hospitals
- Educational grants and scholarships ($9,000+ annually)
- National Achievement Award Program (essay contest for Veterans/active duty)
- Group insurance and discount plans (partnerships with USAA)
- Boy Scout/Girl Scout programs
- JROTC program support

**Additional Resources**
- National Museum of American Jewish Military History (Washington, DC)
- State departments (New Jersey: https://www.jwv-nj.org/)
- TexVet resource: https://texvet.org/resources/jewish-war-veterans-jwv

**Data Format**
- Membership-based organization with local posts
- Benefits advocacy data (not public API)
- Educational programs with application data

**Integration Priority: MEDIUM**
- Specialized community (Jewish Veterans)
- Strong benefits advocacy function
- Limited direct housing/emergency assistance
- Valuable for community-specific referrals

**Recommended Approach**
- Monitor for educational grant and advocacy programs
- Reference for cultural community resources
- Partnership opportunity for benefits counseling referrals

---

## Secondary Faith-Based Organizations

### 6. Salvation Army Regional Programs (Distributed Network)

Multiple regional programs provide specialized Veterans services:
- **Community Integration Services (CIS)**: https://cis.salvationarmy.org/cis/veterans-services/
- **Adult Program Services**: https://www.salvationarmyusa.org/adult-program-services/

**Integration Priority: MEDIUM**
- Good geographic distribution
- Challenge: Decentralized structure

---

### 7. Convoy of Hope

**Organization**
- URL: https://convoyofhope.org/
- Type: Faith-based nonprofit humanitarian organization

**Veteran Services**
- Community event programming for Veterans and families
- Grocery distribution, shoes, haircuts, career services, medical services
- Honor and recognition of Veteran sacrifice at community events

**Data Format**
- Community engagement programs database
- Volunteer portal: https://volunteer.convoyofhope.org/

**Integration Priority: MEDIUM**
- Focus on event-based services rather than direct assistance
- Good community engagement but limited specialized Veteran programming

---

### 8. United Methodist Church Veteran Services

**Organization**
- Veterans Ministries: https://www.umc.org/en/content/veterans-ministries-at-church-by-and-for-those-who-served

**Services**
- Local congregation-based support
- Housing assistance through church partnerships
- Transportation to VA appointments
- Emergency meal programs
- Community fundraising for Veteran support

**Regional Examples**
- Skyland UMC (homeless services): https://www.skylandumc.com/homeless-outreach/
- Methodist Services Organization: https://methodistservices.org/?page_id=73
- Hope Bridge program: Permanent housing for chronically homeless individuals

**Data Format**
- Congregation-based (decentralized)
- Limited central coordination
- Local website listings available

**Integration Priority: LOW-MEDIUM**
- Strong local community presence
- Challenge: Highly distributed, no central coordination
- Better approached through state/regional Methodist organizations

---

### 9. Presbyterian Church Veteran Services

**Organization**
- Presbyterian Church (U.S.A.): https://pcusa.org/
- Board of Pensions Assistance Program: https://pensions.org/

**Services**
- Local congregation-based support
- Transportation to VA appointments
- Transitional housing programs

**Notable Programs**
- Liberation Veteran Services (Southminster Presbyterian Church)
- Arthur Cassell Transitional Housing programs (24 Veterans)

**Data Format**
- Highly localized through congregations
- Limited denominational coordination
- Board of Pensions assistance (primarily for church workers, not broad Veterans)

**Integration Priority: LOW**
- Strong local presence but minimal central coordination
- Limited Veterans-specific programming at denomination level

---

### 10. Baptist Church Veteran Services

**Organizations & Programs**
- Operation We Are Here: https://www.operationwearehere.com/ (Faith-based Baptist ministry)
  - Church Military Ministry Resources: https://www.operationwearehere.com/forchurches.html
- Westside Baptist Church Veterans Ministry: https://wbcchurch.org/ministry/veterans/
- Metropolitan Baptist Church Veterans Ministry: https://metropolitanbaptist.org/ministry/veterans-ministry/
- White Rock Baptist Church Emergency Assistance: https://whiterockbaptistchurch.org/emergency-assistance-ministry/
- Bethel Baptist Church (Cincinnati): Rent/utility assistance

**Services**
- Fellowship and community building
- Financial assistance (rent, utilities)
- Information on VA benefits and services
- Evangelism and discipleship
- Connections to other community resources

**Data Format**
- Congregation-based
- Operation We Are Here has directory of partner churches
- Limited centralized data

**Integration Priority: LOW-MEDIUM**
- Strong local community engagement
- Better for referral networks than structured data

---

### 11. Open Door Ministries

**Organizations**

**Open Door Ministries - High Point, NC**
- URL: https://www.opendoorministrieshp.org/
- Program: Arthur Cassell Transitional Housing (ACTH) - 24 Veterans experiencing homelessness
- Partners: WG "Bill" Hefner Medical Center, Veterans Administration
- Services: Homeless shelter, meals, emergency assistance, permanent housing services, job training

**Open Doors to Future Possibilities**
- URL: https://opendoorstofuturepossibilities.org/programs/
- Services: Transitional housing and supplies for unhoused Veterans and families
- Approach: Faith-based healing conversations and transition support
- Cost: Free services for Veterans and families

**Open Door Ministries - Denver**
- URL: https://www.odmdenver.org/need-housing
- Services: Housing assistance programs

**Data Format**
- Organization-specific websites
- Local HMIS integration available
- Limited centralized coordination

**Integration Priority: MEDIUM**
- Good model for transitional housing programs
- Geographic limitations (regional programs)
- Strong community partnerships

---

## Supporting Organizations & Resources

### 12. National Coalition for Homeless Veterans (NCHV)

**Organization**
- URL: https://nchv.org/
- Hotline: 1-877-424-3838 (24/7 assistance)
- Type: Only national organization solely focused on ending Veteran homelessness

**Services**
- Emergency and supportive housing referrals
- Food, health services, job training
- Searchable state database of Veteran service providers
- 24/7 emergency assistance coordination

**Data Format**
- Searchable provider database by state
- Hotline referral system
- Agency partnerships and coordination

**Integration Priority: MEDIUM**
- Excellent for cross-reference and validation
- Provider database valuable for completeness checks
- Hotline data not directly API-accessible

---

### 13. VA Center for Faith-Based and Neighborhood Partnerships (CFBNP)

**Organization**
- URL: https://www.va.gov/CFBNP/
- Email: VACFBNP@va.gov
- Mission: Engage, educate, and inform faith-based organizations about VA tools and resources

**Services**
- Clergy and community group training facilitation
- Coordination of faith-based partnerships
- Spiritual and emotional needs support for Veterans
- Outreach events nationwide
- Education on Veteran homelessness, opioid crisis, suicide prevention

**Data Format**
- Partnership coordination database
- Event listings and training programs
- Collaborations directory: https://www.va.gov/CFBNP/collaborations.asp

**Integration Priority: HIGH**
- Direct VA partnership opportunity
- Network of faith-based organizations
- Potential data sharing partnership

**Recommended Approach**
- Contact VACFBNP@va.gov for formal partnership
- Leverage collaborations directory for organization verification
- Coordinate on training materials and resources

---

### 14. Homeless Management Information System (HMIS)

**System Overview**
- URL: https://www.hudexchange.info/programs/hmis/
- VA Integration: https://www.va.gov/homeless/hmis/
- Purpose: Local electronic data collection for homeless services

**Veteran Data Integration**
- HMIS data standards include Veteran status (HMIS-3.07)
- SSVF programs required to submit monthly Veteran data to VA Repository
- CSV export format available for analysis
- CoC-specific implementations across regions

**Data Format**
- CSV file exports (standardized format)
- Local HMIS software vendors vary by region
- VA Repository receives aggregated Veteran housing data

**Integration Priority: HIGH**
- Structured Veteran-specific data available
- SSVF programs provide consistent reporting
- Multiple vendor implementations (WellSky, Foothold, etc.)

**HMIS Software Vendors**
- WellSky: https://wellsky.com/hmis-software/
- Foothold Technology: https://footholdtechnology.com/hmis-software/
- Regional systems (NYC, San Diego, Houston, etc.)

**Recommended Approach**
- Contact CoC leads in priority regions
- Request HMIS export permissions for SSVF-participating organizations
- Map HMIS data to Veteran-focused taxonomy
- Partner with faith-based organizations participating in SSVF

---

## Data Integration Strategy

### High Priority Integration Pathway

```
HMIS (Structured Data) → CoC Coordination
    ↓
Faith-Based SSVF Programs (Salvation Army, Catholic Charities, VOA, LSA)
    ↓
VA Repository Export
    ↓
Vibe4Vets Taxonomy Mapping
```

### Medium Priority - Web Scraping Approach

```
Organization Websites (Regional Affiliates)
    ↓
Service Extraction & Normalization
    ↓
Location Geocoding (Census API)
    ↓
Trust Scoring (Tier 2-3 based on source)
```

### Low Priority - Referral Network

```
VA Center for Faith (CFBNP)
    ↓
National Coalition for Homeless Veterans
    ↓
Local VSO Partnerships
    ↓
Verification & Cross-Reference
```

---

## Key Challenges & Recommendations

### Challenge 1: No Centralized API for Faith-Based Services

**Current State**
- Organizations operate independently
- Each regional entity maintains separate websites
- No standardized data format

**Recommendation**
- Prioritize HMIS integration (already structured)
- Build web scraper for top-tier organizations (Salvation Army, Catholic Charities, VOA, Lutheran)
- Create partnership agreements with national organizations for periodic data exports
- Target SSVF programs for consistent, validated data

### Challenge 2: Organizational Autonomy

**Current State**
- Local agencies make independent decisions on data sharing
- Regional variation in service offerings
- Different technology adoption levels

**Recommendation**
- Approach through national headquarters for data sharing policy
- Focus on SSVF and HUD-VASH programs (federally required reporting)
- Establish pilot partnerships with 2-3 large regional providers
- Use VA CFBNP as trusted intermediary

### Challenge 3: Incomplete Veteran Program Coverage

**Current State**
- Many faith-based organizations don't specialize in Veteran services
- Mixed programming (general emergency assistance + Veteran support)
- Limited Veteran-specific data collection

**Recommendation**
- Use HMIS "Veteran status" field as primary filter
- Cross-reference with VA benefits programs (SSVF, HUD-VASH, GPD)
- Validate through National Coalition for Homeless Veterans database
- Tag faith-based designation separately for user discovery

### Challenge 4: Geographic Variability

**Current State**
- Services concentrated in urban areas
- Rural communities often underserved
- Denominational presence varies by region

**Recommendation**
- Map current faith-based coverage by state/county
- Identify geographic gaps
- Coordinate with state VA offices for regional supplement
- Consider CVSO (County Veterans Service Officers) network for rural referrals

---

## Data Collection Priorities (Phase 3+)

### Immediate (Q1 2026)

1. **HMIS Partnership Development**
   - Identify 5-10 CoCs with active SSVF programs
   - Establish data-sharing MOA with HMIS leads
   - Extract Veteran-specific housing data
   - Timeline: 4-6 weeks

2. **VA CFBNP Partnership**
   - Initial outreach to VACFBNP@va.gov
   - Explore data-sharing opportunity
   - Access collaborations directory
   - Timeline: 2-4 weeks

3. **Top-Tier Organization Data**
   - Salvation Army headquarters partnership for regional listings
   - Catholic Charities national office SSVF program data
   - VOA affiliate directory aggregation
   - Timeline: 4-8 weeks

### Phase 2 (Q2-Q3 2026)

4. **Web Scraping Infrastructure**
   - Build regional website parser for Salvation Army locations
   - Catholic Charities local agency sites
   - Methodist Services and Presbyterian networks
   - Timeline: 6-8 weeks

5. **HMIS Data Model Integration**
   - Map HMIS fields to Vibe4Vets taxonomy
   - Build ETL pipeline from HMIS CSV exports
   - Quality assurance and deduplication
   - Timeline: 3-4 weeks

### Phase 3 (Q3-Q4 2026)

6. **Secondary Organization Integration**
   - Convoy of Hope event data
   - Church Military Ministry Resources directory
   - Mighty Oaks and other faith-based recovery programs
   - Timeline: 4-6 weeks

---

## Files & Resources

### Reference Documents
- VA Center for Faith: https://www.va.gov/CFBNP/
- HMIS Data Standards: https://www.hudexchange.info/programs/hmis/hmis-data-standards/
- National Coalition for Homeless Veterans: https://nchv.org/

### Contact Information
- **VA CFBNP**: VACFBNP@va.gov (partnership inquiries)
- **Catholic Charities USA**: 2050 Ballenger Ave, Suite 400, Alexandria, VA 22314
- **Salvation Army National**: Headquarters in Alexandria, VA
- **VOA**: https://www.voa.org/ (national office)
- **Lutheran Services**: Lutheran Services in America, Washington, DC

---

## Next Steps for Implementation

1. **Validate data sources** - Confirm current status and availability with organizations
2. **Negotiate MOAs** - Formal data-sharing agreements with top-tier organizations
3. **Build connectors** - Python connectors for HMIS export, web scraping, API access
4. **Map taxonomy** - Ensure faith-based programs fit Vibe4Vets category structure
5. **Set up ETL** - Integrate with existing pipeline for normalization and deduplication
6. **Test validation** - Verify data quality against national databases (NCHV)

---

**Document Version**: 1.0
**Last Updated**: January 28, 2026
**Research Method**: Web search and organization website review
**Coverage**: United States (national scope)
