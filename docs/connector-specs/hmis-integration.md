# HMIS Integration for Vibe4Vets

## Overview

**HMIS (Homeless Management Information System)** is a federally-mandated database system used by Continuums of Care (CoCs) to track and aggregate data on homeless populations, including Veterans experiencing homelessness. HMIS contains structured data on faith-based and community-based homeless Veteran services at the local level.

### Key Facts

- **Purpose**: Locally-administered, confidential client-level data collection for homeless services
- **Coverage**: 400+ Continuums of Care nationwide (CoCs are regional homeless service networks)
- **Veteran Data**: HMIS tracks Veteran status (universal data element), SSVF (Supportive Services for Veteran Families) services, and housing outcomes
- **Standards**: FY 2026 HUD HMIS Data Standards (effective October 1, 2025) with 12+ mandatory data elements for each client
- **Access Model**: Restricted access via CoC governance; public aggregated data available; individual-level data requires partnership agreements

---

## HMIS Data Structure

### Core Components

HMIS captures three types of data:

| Component | Description | Veteran Relevance |
|-----------|-------------|------------------|
| **Universal Data Elements** | Collected for all clients in all projects | Veteran Status (3.07) |
| **Project Descriptor Data** | Project metadata, CoC information | Describes homeless service providers |
| **Program-Specific Elements** | SSVF, HUD-VASH, ESG, RRH data | Veteran program enrollment, eligibility |

### Veteran-Specific Data Fields

```
Universal Elements:
├── 3.07 Veteran Status (Required) - Primary indicator
├── 3.08 Date Received Honorable Discharge - Discharge verification
├── 3.09 Military Branch - Service history
└── 3.10 Last Grade of Rank - Officer/enlisted classification

SSVF Program-Specific Elements:
├── V1 Eligibility
├── V2 Services Provided - Case management, counseling, emergency rental
├── V3 Financial Assistance - Rent, utilities, other assistance amounts
└── R6 Employment Status - At intake and exit for RRH/HP

Data Granularity:
├── Individual client-level records
├── Service transactions (multiple services per client)
├── Financial assistance records
├── Housing outcomes (permanent housing, exits, employment gains)
└── Follow-up data (post-exit outcomes tracked 6+ months)
```

### FY 2026 Data Standards Changes

As of October 1, 2025:
- **New Element**: `Sex` (replacing retired Gender and Sexual Orientation)
- **Updated**: Hispanic/Latina/o terminology standardization
- **Retired**: Translation Assistance Needed
- **Enhanced**: Reporting through CoC Annual Performance Reports (APR), ESG CAPER, PATH reports

---

## CoC Governance Model

### Structure

Each Continuum of Care operates as a regional homeless services network with legal authority to:

```
HUD
 └─ Continuum of Care (Regional governance)
     ├─ CoC Board of Directors (Policy oversight)
     ├─ HMIS Lead Agency (Operator responsibility)
     │   └─ HMIS System Administrator
     ├─ Participating Providers (Homeless service agencies)
     │   └─ HMIS End Users (Case managers, data staff)
     └─ Collaborative Applicant (Grant administration)
```

### Key Governance Documents

Every CoC must establish and update annually:

1. **HMIS Governance Charter**
   - Procedures for designating HMIS software and HMIS Lead
   - Access policies and user roles
   - Data quality assurance protocols
   - Sanctions for non-compliance

2. **Privacy Plan**
   - Data protection standards
   - Permitted uses and disclosures
   - Client privacy rights

3. **Security Plan**
   - System access controls
   - Encryption and backup procedures
   - Incident response protocols

4. **Data Quality Plan**
   - Validation rules
   - Missing data standards
   - Audit procedures

5. **HMIS Participation Agreement**
   - Written contract with participating providers
   - Compliance requirements
   - Data entry standards
   - Performance metrics

### Multi-CoC Arrangements

Some regions use shared HMIS across multiple CoCs. In these cases:
- All CoCs must designate the same HMIS Lead
- Joint governance charter required
- Unified privacy, security, and data quality standards
- Common participation agreements

---

## Data Access Pathways for Vibe4Vets

### Pathway 1: Restricted Individual-Level Data (Partnership Route)

**Who Qualifies:**
- Organizations receiving CoC, ESG, CDBG, VA, or other HUD homeless funding
- Nonprofits serving homeless populations (case-by-case basis)
- Research institutions with IRB approval

**Requirements:**
- Demonstrated service delivery to homeless individuals
- Organizational reference from existing CoC member
- Signed Data Sharing Agreement / Memorandum of Understanding (MOA)
- HIPAA/FERPA compliance documentation
- User training on confidentiality obligations
- Annual access renewal

**Process:**
1. Identify target CoC (see Table 2 for largest CoCs)
2. Contact HMIS Lead Agency or CoC Collaborative Applicant
3. Complete HMIS User Access Request form
4. Provide organizational documentation and reference
5. Negotiate Data Sharing Agreement (typical timeline: 2-6 months)
6. Execute MOA with confidentiality provisions
7. Receive system access and user credentials
8. Complete HIPAA/data protection training

**Data Available:**
- Client-level records (de-identified or identified, per agreement)
- Service transaction data (housing, employment, financial assistance)
- Outcome tracking (housing placement, exits, employment gains)
- Veteran-specific cohort analysis
- Geographic/demographic aggregations

### Pathway 2: Public Aggregated Data (No Partnership Required)

**Sources:**
- HUD USER database (huduser.gov)
- HUD Exchange (hudexchange.info)
- Annual Homeless Assessment Report (AHAR)
- CoC Homeless Populations and Subpopulations Reports
- Point-in-Time (PiT) Count annual releases (January)

**Data Available:**
- National veteran homelessness estimates (2024: 32,882 veterans)
- State-level veteran counts
- CoC-level sheltered/unsheltered veteran breakdowns
- Chronically homeless veteran counts
- 10-year trends (2009-2024: 55% decrease)

**Frequency:**
- Annual PIT Count (January, results published December)
- AHAR Part 1 (PIT data, published ~10-12 months after collection)
- Longitudinal Systems Analysis (LSA) data submitted by CoCs (as of FY 2018)

**Sample Statistics (2024 Data):**
```
Total Veterans Experiencing Homelessness:       32,882
├─ Sheltered:                                   19,031 (57.8%)
└─ Unsheltered:                                 13,851 (42.2%)

Year-over-Year Change:                          -7.5%
Change Since 2009:                              -55.0%

Trend:                                          Positive (declining)
```

### Pathway 3: VA Repository Access (SSVF Focus)

**Scope:**
- Veteran-specific SSVF service data
- Requires SSVF grant participation or research authorization

**Data Elements:**
- SSVF service types and frequencies
- Financial assistance tracking
- Housing outcomes (permanent housing placements)
- Employment outcomes

**Requirements:**
- SSVF grantee status OR VA research partnership
- VA data use agreement
- Monthly data export compliance (CSV 5.1 format)
- HUD HMIS data standards compliance

**Access Contact:**
- VA Homeless Programs (www.va.gov/homeless/ssvf/hmis/)
- VA repository administrators

---

## Largest CoCs by Veteran Population

### Top 10 CoCs Serving Most Veterans

Based on HUD PIT Count data and veteran homelessness estimates:

| Rank | CoC | Region | Est. Homeless Veterans | Key Features |
|------|-----|--------|----------------------|--------------|
| 1 | Los Angeles | California | ~3,500-4,500 | Largest homeless population; extensive SSVF programs |
| 2 | San Francisco | California | ~1,500-2,000 | Urban services; strong nonprofits (Swords to Plowshares) |
| 3 | San Diego | California | ~1,200-1,500 | Regional Task Force; established HMIS |
| 4 | New York City | New York | ~2,000-2,500 | Complex multi-CoC system; CCOC governance |
| 5 | Seattle/King County | Washington | ~1,000-1,200 | Regional coordination; veteran-specific programs |
| 6 | Phoenix | Arizona | ~800-1,000 | Fast-growing; HMIS vendor: Clarity |
| 7 | Portland | Oregon | ~600-800 | Strong CoC infrastructure; veteran coalitions |
| 8 | Las Vegas | Nevada | ~500-700 | SSVF-heavy; tourism-driven economy |
| 9 | Chicago | Illinois | ~600-800 | AllChicago HMIS; strong faith-based partners |
| 10 | Denver | Colorado | ~400-600 | Growing homeless population; expanding services |

**Note**: Estimates based on 2024 PIT Count data (most recent). Exact numbers updated annually in January following PiT Count.

### How to Find Your Target CoCs

- **HUD CoC Directory**: https://www.hud.gov/hud-partners/community-coc
- **State-Specific Lists**: https://www.hudexchange.info/programs/coc/coc-homeless-populations-and-subpopulations-reports/
- **CoC HMIS Lead Contacts**: Available via HUD Exchange by state and metropolitan area

---

## Veteran-Specific Data Available

### Service Categories Tracked in HMIS

```
Housing Services:
├─ HUD-VASH (Veterans Affairs Supportive Housing)
├─ SSVF (Supportive Services for Veteran Families)
├─ Permanent Supportive Housing (PSH)
├─ Rapid Re-housing (RRH)
├─ Emergency Shelter
└─ Prevention/Homelessness Prevention

Support Services:
├─ Case Management
├─ Mental Health Counseling (including PTSD)
├─ Substance Abuse Treatment
├─ Employment Services
├─ Benefits Counseling
├─ Legal Services
├─ Medical Services
└─ Childcare/Family Services

Financial Assistance (SSVF):
├─ Emergency Rent
├─ Utilities
├─ Security Deposit
├─ Moving Costs
├─ Household Items
└─ Other Emergency Assistance
```

### Outcome Metrics

HMIS tracks outcomes for follow-up (6-24 months post-exit):

```
Housing Outcomes:
├─ Permanent housing placement rate
├─ Housing stability (retention at 6/12 months)
├─ Exits to permanent housing
└─ Returns to homelessness

Employment Outcomes:
├─ Employment at project start
├─ Employment at exit
├─ Wage earnings
└─ Benefits obtained (SSI, SSDI, VA benefits)

Income/Assistance:
├─ Non-cash benefits received
├─ Income sources
└─ Financial assistance amounts
```

### Veteran Classification Data

HMIS enables analysis by Veteran subgroups:

```
├─ Family status (individuals vs. families with children)
├─ Chronic homelessness status
├─ Service-connection disability status
├─ Discharge status (honorable, other than honorable, etc.)
├─ Military branch of service
├─ Age and era of service
└─ Disability type/severity (when collected)
```

---

## How to Access HMIS Data

### Step 1: Identify Your Strategy

| Your Goal | Best Pathway | Timeline | Cost |
|-----------|--------------|----------|------|
| Publish aggregated Veteran statistics | Public AHAR data | 1-2 weeks | $0 |
| Display local CoC services | Partner MOA | 2-6 months | $0-5K legal |
| Integrate client data | SSVF or CoC partnership | 3-12 months | $0-20K |
| Research/academic | VA or IRB route | 6-12 months | Varies |

### Step 2: Contact the Right Organization

**For Public Data:**
- HUD USER: https://www.huduser.gov/portal/datasets/ahar.html
- HUD Exchange: https://www.hudexchange.info/programs/coc/coc-homeless-populations-and-subpopulations-reports/
- Download AHAR Part 1 (PIT data with CoC breakdowns)

**For Partnership Data:**
- Identify CoC(s) by state/city
- Contact HMIS Lead Agency (listed on CoC website)
- Alternative: CoC Collaborative Applicant office

**Sample CoC Websites:**
- **Los Angeles CoC**: www.lahomelessservices.org
- **San Francisco CoC**: www.sfgov.org/homelessness
- **NYC CoC**: www.nyc.gov/site/nycccoc/hmis/hmis.page
- **All Chicago HMIS**: www.allchicago.org/hmis/
- **San Diego CoC**: www.rtfhsd.org/about-coc/homeless-management-information-system-hmis/

### Step 3: Prepare Documentation

**For HMIS Data Partnership:**

Prepare:
1. Organizational 501(c)(3) certificate or non-profit status proof
2. Mission statement and service description
3. Reference from existing CoC-funded organization
4. Data security/privacy policy
5. Staff list with training records (or commitment)
6. Data use statement (what you'll do with the data)

**Template Content for MOA/DSA:**

```
Data Sharing Agreement Key Sections:

1. Purpose
   - Stated use: "Resource directory aggregation for Veteran services"
   - Scope: Aggregated data only (no individual PII) OR
           De-identified data for analysis

2. Data Access Levels
   - Read-only access to HMIS (no write/modify)
   - Geographic filters (state-level, zip-code-level)
   - Service type filters (veteran-specific only)
   - Time restrictions (real-time or daily delayed)

3. Data Security
   - Encryption in transit and at rest
   - User access controls and audit logs
   - Annual security assessments
   - Breach notification (within 24-48 hours)

4. Permitted Uses
   - Aggregated reporting: YES
   - Public-facing resource directory: YES
   - Client-level PII matching: NO (unless de-identified)
   - Sharing with third parties: NO

5. Confidentiality
   - Non-disclosure of individual records
   - HIPAA/FERPA compliance
   - Criminal penalties for unauthorized disclosure
   - Acknowledgment of sensitive data nature

6. Term & Termination
   - Initial term: 1-3 years
   - Annual renewal requirements
   - Immediate termination for breach
   - Data return/destruction upon termination

7. Liability
   - Limitation of liability clauses
   - Indemnification provisions
   - Insurance requirements (if applicable)
```

### Step 4: Execute Agreement

1. **Negotiation Phase** (4-12 weeks)
   - CoC/HMIS Lead reviews proposal
   - Legal department review (if required)
   - Scope refinement (what data, how often)
   - Cost negotiation (some CoCs charge data fees)

2. **Execution Phase** (1-2 weeks)
   - Signatures from authorized parties
   - Effective date documentation
   - System provisioning (user account creation)

3. **Implementation Phase** (1-4 weeks)
   - HMIS system access setup
   - Training on data extraction/reporting
   - Test data pulls
   - Production access activation

---

## HMIS Software Vendors & APIs

### Major HMIS Platforms

| Vendor | Product | Market Share | API Support | Veteran Features |
|--------|---------|--------------|-------------|-----------------|
| **Bitfocus** | Clarity Human Services | ~35% (especially CA) | RESTful API | Full SSVF support |
| **WellSky** | ServicePoint | ~20% | Supported | SSVF integration |
| **Foothold Technology** | AWARDS | ~15% | Limited | VA program focus |
| **PlanStreet** | HMIS | ~10% | Planned | Developing |
| **Housing Works** | EiCare | ~5% | Limited | Basic support |
| **Others** | Various platforms | ~15% | Varies | Case-by-case |

### API Integration Considerations

**Bitfocus Clarity API** (Most Common):
- Endpoint: RESTful architecture
- Authentication: OAuth 2.0
- Rate Limiting: Typically 100-1000 requests/hour
- Data Format: JSON
- Veteran-specific endpoints: `/clients`, `/services`, `/outcomes` with Veteran filters
- Documentation: Available via Bitfocus partner portal

**Data Export Formats:**
- CSV (5.1 HUD standard format for bulk exports)
- JSON (for API integration)
- XML (legacy systems)
- Direct database connectivity (if authorized)

**Integration Challenges:**
- Each CoC uses different vendor (no unified API)
- Data refreshes on different schedules (daily, weekly, monthly)
- API rate limits for large-scale data pulls
- Regional governance variations affect access

---

## Sample Data Sharing Agreement

### Vibe4Vets MOA Template

```markdown
MEMORANDUM OF UNDERSTANDING
DATA SHARING AGREEMENT

Between:
  - [CoC NAME] Continuum of Care
  - [HMIS LEAD AGENCY NAME]

And:
  - Vibe4Vets (Resource Directory)

Effective Date: [DATE]
Term: One (1) year, automatically renewing unless terminated

PURPOSE AND SCOPE
This Agreement establishes the terms for sharing HMIS data to support
Vibe4Vets' mission of aggregating Veteran homeless services resources
in [STATE/REGION].

DATA TO BE SHARED
The HMIS Lead Agency agrees to provide:
  - Aggregated Veteran service provider locations and contact information
  - Service types and availability
  - Capacity and program eligibility information
  - De-identified outcome statistics (by service type, not by individual)
  - Updated data on [FREQUENCY: daily/weekly/monthly]

DATA NOT TO BE SHARED
The following data shall NOT be provided:
  - Individual client-level records or PII
  - SSN, date of birth, or identification numbers
  - Home addresses, phone numbers (unless provider info)
  - Any information not de-identified or aggregated
  - Funding/budget details

PERMITTED USES
Vibe4Vets may use shared data to:
  - Create and maintain public-facing resource directory
  - Publish aggregated statistics on Veteran homelessness in [REGION]
  - Generate reports for funders/partners (aggregated only)
  - Train staff on local resources
  - Support Veterans in accessing services

PROHIBITED USES
Vibe4Vets shall NOT:
  - Share data with third parties without written consent
  - Attempt to re-identify individuals
  - Sell, license, or commercialize the data
  - Match HMIS data with other databases to identify individuals
  - Use data for marketing or fund-raising beyond stated purpose

DATA SECURITY
Vibe4Vets commits to:
  - Store data in encrypted format (AES-256 or equivalent)
  - Restrict access to authorized staff only
  - Maintain audit logs of all data access
  - Conduct annual security assessments
  - Report breaches within 48 hours
  - Destroy data upon agreement termination

CONFIDENTIALITY & COMPLIANCE
Vibe4Vets acknowledges:
  - Sensitive and confidential nature of HMIS data
  - HIPAA, FERPA, and state privacy law compliance
  - Criminal penalties for unauthorized disclosure
  - Personal liability of staff with access

DATA RETENTION
  - Active data: Maintained during agreement term
  - Archived data: Deleted within 90 days of termination
  - Backup copies: Destroyed within 30 days of deletion

TERMINATION
Either party may terminate with 30 days' written notice.
Immediate termination allowed for:
  - Breach of confidentiality
  - Unauthorized data access
  - Violation of permitted uses
  - Non-compliance with security standards

Upon termination:
  - All data access revoked immediately
  - Data destruction completed within 30 days
  - Certification of destruction provided

GOVERNING LAW
This Agreement is governed by the laws of [STATE].

SIGNATURE AUTHORITY
[CoC/HMIS Lead Signatory]
Name, Title, Organization
Date

[Vibe4Vets Signatory]
Name, Title, Organization
Date
```

---

## Alternative: HUD HMIS Repository Access

### What is the VA HMIS Repository?

The **VA HMIS Repository** is a HUD-approved centralized database where SSVF grantees (and some other VA program grantees) must submit client-level data monthly.

### Who Has Access?

- **Direct Access**: SSVF grantees (required)
- **Secondary Access**: VA Medical Centers, VA regional offices
- **Restricted Access**: Research institutions with VA research authority

### Data Available

- Veteran client profiles (with discharge date, military branch)
- SSVF service transaction records
- Financial assistance amounts and types
- Housing placement and stability outcomes
- Employment outcomes at exit and follow-up

### How to Request Access

1. **If SSVF Grantee**: Automatic VA Repository access as condition of funding
2. **If Researcher**: Contact VA Office of Research & Development for IRB approval
3. **If Nonprofit Partner**: Request via VA Regional Office with sponsorship from local SSVF grantee

### Data Extract Process

- **Format**: CSV (FY 2026 HMIS Data Standards compliant)
- **Frequency**: Monthly submission required; extracts available upon request
- **Turnaround**: 2-4 weeks for custom extracts
- **Contact**: VA.gov/homeless/ssvf/hmis/

---

## Implementation Roadmap for Vibe4Vets

### Phase 1: Quick Start (Weeks 1-4)

**Goal**: Publish aggregated public Veteran homelessness statistics

1. Download 2024 AHAR Part 1 data from HUD USER
2. Extract CoC-level veteran counts for target states
3. Create "Veteran Homelessness by Region" dashboard
4. Link to HUD data sources for transparency

**Deliverables**:
- Static resource directory with public AHAR data
- By-state veteran homeless population estimates
- Links to national HMIS reports

**Time**: 2-4 weeks | **Cost**: $0

### Phase 2: Regional Partnership (Months 2-6)

**Goal**: Integrate direct HMIS access for top 5 CoCs

1. Identify target CoCs (LA, SF, NYC, Seattle, Phoenix)
2. Send outreach to each CoC's HMIS Lead
3. Prepare MOA templates and data security documentation
4. Negotiate access with 2-3 pilot CoCs

**Deliverables**:
- Executed Data Sharing Agreements (2-3 CoCs)
- Real-time service provider data integration
- CoC-specific resource pages

**Time**: 3-6 months | **Cost**: $0-10K legal (for MOA negotiation)

### Phase 3: Expansion (Months 6-12)

**Goal**: Scale to 10+ CoCs nationwide

1. Develop HMIS API connector library (vendor-agnostic)
2. Standardize data extraction across different HMIS platforms
3. Implement automated data validation and deduplication
4. Expand MOAs to additional CoCs

**Deliverables**:
- Multi-vendor HMIS connector
- Nationwide veteran services directory
- Monthly data refresh automation

**Time**: 4-8 months | **Cost**: $15-40K development

### Phase 4: Advanced Analytics (Months 9+)

**Goal**: Dashboard, trends, and resource discovery

1. Aggregate veteran outcomes across CoCs
2. Create trend analysis (housing placement rates, employment gains)
3. Build "Find Services Near Me" matching engine
4. Publish monthly Veteran homelessness trends report

**Deliverables**:
- Public analytics dashboard
- Veteran services recommendation engine
- Monthly trends report

**Time**: 3-6 months | **Cost**: $20-50K development + AWS hosting

---

## Key Contacts & Resources

### HUD Resources

- **HUD Exchange**: https://www.hudexchange.info/programs/hmis/
  - HMIS Data Standards documentation
  - Guides and tools
  - CoC directory

- **HUD USER**: https://www.huduser.gov/
  - AHAR reports and data downloads
  - PIT Count historical data
  - Research datasets

- **HUD CoC Program**: https://www.hud.gov/hud-partners/community-coc
  - CoC directory by state
  - Grant information
  - CoC governance requirements

### VA Resources

- **VA Homeless Programs**: https://www.va.gov/homeless/
  - SSVF program information
  - HMIS reporting requirements
  - VA Repository access

- **VA HMIS**: https://www.va.gov/homeless/ssvf/hmis/
  - SSVF data collection guide
  - Technical specifications
  - Repository contacts

### HMIS Vendor Contacts

- **Bitfocus (Clarity)**: https://www.bitfocus.com/
  - API documentation
  - Partner integrations
  - Veteran program features

- **WellSky (ServicePoint)**: https://www.wellsky.com/
  - HMIS solutions
  - Legacy system support

- **Foothold Technology (AWARDS)**: https://footholdtechnology.com/
  - Veteran-specific HMIS

### Sample CoC Contacts (for outreach)

**Email Outreach Template**:
```
Subject: Vibe4Vets Collaboration - Veteran Services Resource Directory

Dear [CoC Director Name],

We are reaching out to explore a data partnership between Vibe4Vets and
[CoC NAME].

Vibe4Vets is building a nationwide Veteran-focused resource directory to
help Veterans find housing, employment, and other critical services. We
are seeking to partner with Continuums of Care to include SSVF, HUD-VASH,
and other Veteran service providers in our public directory.

We are interested in:
- Provider locations and contact information
- Service types and availability
- Aggregated outcome statistics (de-identified)
- Monthly data updates

We can execute a Data Sharing Agreement that protects client privacy and
complies with all HMIS governance requirements.

Would you be available for a brief call to discuss this opportunity?

Best regards,
[Your Name]
Vibe4Vets
```

---

## Regulatory & Compliance Notes

### HIPAA/FERPA Applicability

- **HMIS Data**: Typically NOT covered by HIPAA (not "protected health information" if used for homeless services coordination)
- **Exception**: If data links to VA health records, HIPAA applies
- **FERPA**: Does not apply to HMIS
- **State Privacy Laws**: May apply (vary by state)

### Data Breaches

- Must be reported within 24-48 hours to HMIS Lead
- Client notification required if PII exposed
- HHS Breach Notification Rule applies if any health data involved
- Criminal liability for intentional unauthorized disclosure

### Limitations on Use

- **For-profit use prohibited** without explicit CoC consent
- **Re-identification prohibited** (cannot match with other datasets to identify individuals)
- **Sharing with third parties prohibited** except as permitted in MOA
- **Research use** requires IRB approval and formal research agreement

---

## Frequently Asked Questions

### Q: Can we scrape CoC websites instead of getting HMIS access?

**A**: Scraping is NOT recommended because:
- Data quality: Websites often out-of-date
- Legal: May violate Terms of Service
- Coverage: Only captures subset of providers
- Outdated: No access to outcomes/program updates

HMIS access is the authoritative source.

### Q: How long does it take to get HMIS access?

**A**: Typically 2-6 months depending on:
- CoC responsiveness (some process requests quarterly)
- Legal review (if MOA required)
- System setup (HMIS vendor provisioning)
- Your documentation completeness

Parallel outreach to 3-5 CoCs speeds up timeline.

### Q: What if the CoC wants money for data access?

**A**:
- Some CoCs charge flat fees ($0-5K annually)
- Some charge per-extract ($50-500 per query)
- Public data is always free
- Negotiate in MOA discussion

Budget $5-10K for CoC partnerships initially.

### Q: Can we use individual-level HMIS data for matching Veterans?

**A**: NO - Individual PII is strictly prohibited.

**What IS allowed:**
- Aggregated service provider information
- De-identified outcome statistics
- Veteran count trends

**What IS NOT allowed:**
- Matching individuals across systems
- Publishing client names/details
- Using for eligibility determination

### Q: Do all CoCs use the same HMIS platform?

**A**: NO - Each CoC chooses its own vendor:
- Bitfocus (Clarity): ~35% nationally, more in CA
- WellSky (ServicePoint): ~20% nationally
- Others: 45% spread across 5+ vendors

Plan for multi-vendor integration.

### Q: Can we access data from all CoCs nationwide?

**A**: Technically yes, but practically:
- 400+ CoCs = 400+ separate negotiations
- Different data availability/terms per CoC
- Start with top 10-15 CoCs by Veteran population
- Expand gradually

### Q: What is the difference between public AHAR data and HMIS partnership data?

**AHAR (Public):**
- Aggregated national/state/CoC level
- Published 10-12 months after PIT Count
- Veteran counts only (high-level)
- Free, openly available

**HMIS Partnership:**
- Provider-level detail (locations, services)
- Real-time or monthly updates
- De-identified outcomes
- Restricted access, confidentiality agreement required

---

## Recommended Next Steps for Vibe4Vets

1. **Immediate (Week 1)**
   - Download 2024 AHAR data from HUD USER
   - Compile Top 10 CoCs list with HMIS Lead contacts

2. **Short-term (Weeks 2-4)**
   - Draft MOA/Data Sharing Agreement template
   - Send initial outreach to 3-5 largest CoCs
   - Review HMIS Data Standards documentation

3. **Medium-term (Months 2-3)**
   - Negotiate first 2 MOAs in parallel
   - Prepare system architecture for HMIS data ingestion
   - Develop vendor-agnostic HMIS connector library

4. **Long-term (Months 4-6)**
   - Launch pilot with 2-3 CoCs
   - Iterate based on feedback
   - Plan expansion to 10+ CoCs
   - Build analytics dashboard

---

## Sources & References

- [HUD Exchange - HMIS Program](https://www.hudexchange.info/programs/hmis/)
- [FY 2026 HMIS Data Standards](https://www.hudexchange.info/programs/hmis/hmis-data-standards/)
- [HUD USER - 2024 AHAR Data](https://www.huduser.gov/portal/datasets/ahar/2024-ahar-part-1-pit-estimates-of-homelessness-in-the-us.html)
- [VA Homeless Programs - SSVF HMIS](https://www.va.gov/homeless/ssvf/hmis/)
- [HUD - Continuum of Care Program](https://www.hud.gov/hud-partners/community-coc)
- [Bitfocus Clarity HMIS](https://www.bitfocus.com/hmis-software)
- [CoC Program HMIS Manual](https://www.hudexchange.info/resource/4445/coc-program-hmis-manual/)
- [VA Programs HMIS Manual](https://www.hudexchange.info/resource/4450/va-programs-hmis-manual/)
- [Supportive Services for Veteran Families Data Collection Guide](https://www.hudexchange.info/resource/4781/supportive-services-for-veteran-families-program-ssvf-data-collection-guide/)
- [HMIS Data and Privacy Security Toolkit](https://www.hudexchange.info/resource/7250/hmis-data-and-privacy-security-toolkit/)
- [San Diego CoC HMIS Policies and Procedures](https://home-start.org/wp-content/uploads/2022/02/HMIS-Policies-and-Procedures-Manual-Final-12312019.pdf)
- [Coalition for the Homeless - HMIS Access Policies](https://louhomeless.org/hmis-policies-access/)
- [Prince George's CoC HMIS Policies and Procedures](https://www.princegeorgescountymd.gov/sites/default/files/media-document/dcv38016_hud-2021-coc-hmis-policies-and-procedures.pdf)
- [California CoCs and HMIS Vendors](https://homelessstrategy.com/california-continuums-of-care-and-homeless-management-information-system-hmis-vendors-who-they-are-and-next-steps/)
- [National Coalition for Homeless Veterans](https://nchv.org/2024-point-in-time-count/)
- [Bob Woodruff Foundation - Veteran Homelessness](https://bobwoodrufffoundation.org/success-stories/veteran-homelessness-in-the-u-s-understanding-the-numbers/)

