# Faith-Based Veteran Services - Implementation Roadmap

**Issue**: V4V-gofm
**Research Date**: January 28, 2026
**Status**: Ready for Phase 3 Integration

---

## Top 4 Organizations to Integrate (By Impact & Data Availability)

### 1. The Salvation Army + HMIS System

**Why First**:
- Largest faith-based Veteran network in US
- Already participates in HMIS (Homeless Management Information System)
- SSVF programs provide federally-required data exports
- All regional locations can be aggregated through HMIS

**Data Source Strategy**:
```
Salvation Army HQ → Regional SSVF Programs → HMIS CoC Systems → CSV Exports
```

**Integration Steps**:
1. Contact Salvation Army National HQ (2050 Ballenger Ave, Alexandria, VA)
2. Identify all SSVF-participating Salvation Army programs (by state)
3. Get list of CoC HMIS administrators in partner regions
4. Request monthly HMIS CSV export permissions
5. Map Veteran records to Vibe4Vets taxonomy
6. Build connector: `backend/connectors/salvation_army_hmis.py`

**Expected Output**:
- 100-500+ resources across all states
- Housing, emergency assistance, job training categories
- Trust Tier 1-2 (federal HMIS standard)
- Updated monthly

**Contact**: National HQ coordination or regional SSVF directors

**Timeline**: 4-6 weeks (MOA negotiation + technical setup)

---

### 2. Catholic Charities USA Network

**Why Second**:
- 1,700+ local agencies nationwide (largest faith-based network)
- Established SSVF programs with consistent data standards
- National headquarters can coordinate data sharing
- Each agency maintains web presence (scrapeable)

**Data Source Strategy**:
```
Catholic Charities USA HQ → Local SSVF Programs → HMIS + Agency Websites
```

**Integration Steps**:
1. Contact Catholic Charities USA national office (2050 Ballenger Ave, Suite 400, Alexandria, VA 22314)
2. Request list of all Veteran services agencies + SSVF programs
3. For large agencies: HMIS export data
4. For regional agencies: Scrape agency websites for services
5. Aggregate using national office coordination
6. Build connector: `backend/connectors/catholic_charities.py`

**Expected Output**:
- 300-800+ resources (SSVF + local programs)
- Housing, emergency assistance, case management
- Trust Tier 1-2 (federal SSVF participation)
- Updated quarterly

**Contact**: National office at main headquarters; regional coordinators

**Timeline**: 4-8 weeks (diverse agency coordination)

---

### 3. Volunteers of America (VOA)

**Why Third**:
- Second-largest private Veteran housing provider
- 9+ regional affiliates with dedicated websites
- SSVF programs with structured reporting
- Geographic diversity (all major regions covered)

**Data Source Strategy**:
```
VOA National Office → Regional Affiliates → HMIS + VOA Websites
```

**Integration Steps**:
1. Contact VOA national office (www.voa.org)
2. Request regional affiliate directory with Veteran program info
3. For each affiliate: Get HMIS export for housing programs
4. Scrape regional websites for non-housing services
5. Standardize across 9+ affiliate brands
6. Build connector: `backend/connectors/voa_veteran_programs.py`

**Expected Output**:
- 200-500+ resources (housing + supportive services)
- Geographic coverage: 40+ states
- Trust Tier 1-2 (SSVF + HMIS)
- Updated monthly (HMIS) + quarterly (website)

**Contact**: National office coordination; regional affiliate directors

**Timeline**: 4-6 weeks (existing affiliate coordination)

---

### 4. VA Center for Faith-Based & Neighborhood Partnerships (CFBNP)

**Why Fourth (Foundation)**:
- Official VA coordination point for faith-based organizations
- Can facilitate partnerships with national organizations
- Maintains directory of faith-based Veteran service providers
- Can provide data-sharing guidance and template MOAs

**Integration Steps**:
1. Initial outreach email to VACFBNP@va.gov
   - Introduce Vibe4Vets
   - Request partnership for faith-based data aggregation
   - Ask for existing organization directory
2. Schedule call with CFBNP leadership
3. Request access to collaborations directory (https://www.va.gov/CFBNP/collaborations.asp)
4. Establish referral relationship for unmatched organizations
5. Use as validation point for organization tier assignment

**Expected Output**:
- Formal VA partnership recognition
- Access to validated organization directory
- Support for organizational outreach and MOA negotiation
- Ongoing relationship for program updates

**Contact**: VACFBNP@va.gov

**Timeline**: 2-4 weeks (government coordination)

---

## Secondary Integration (Phases 2-3)

### 5. Lutheran Services America
- **Data**: Member organization websites + LMVFM coordination
- **Volume**: 50-150+ programs across 300+ member organizations
- **Timeline**: Weeks 8-12

### 6. Open Door Ministries Network
- **Data**: Regional HMIS + local partnerships
- **Volume**: 10-20 programs (specialized transitional housing)
- **Timeline**: Weeks 10-14

### 7. National Coalition for Homeless Veterans
- **Data**: State-level provider database (for validation)
- **Volume**: Cross-reference and backup validation
- **Timeline**: Ongoing (quarterly cross-checks)

---

## HMIS Integration Blueprint

**Critical Discovery**: Most faith-based Veteran services are already tracked in HMIS for SSVF programs.

### HMIS Data Model

```
HMIS Client (Veteran Flag = Yes)
  ├── Demographics (name, DOB, veteran status)
  ├── Housing Status (homeless → transitional → permanent)
  ├── Services Received
  │   ├── Emergency assistance (rent, utilities)
  │   ├── Case management
  │   ├── Job training
  │   ├── Counseling/Mental health
  │   └── Healthcare referrals
  ├── Organization (Salvation Army, Catholic Charities, VOA, etc.)
  ├── Program (SSVF, HUD-VASH, GPD)
  └── CoC (Continuum of Care) Region
```

### Data Export Process

```bash
# Each CoC provides monthly HMIS CSV export with:
# - universal_data_elements.csv (demographics + veteran status)
# - services_provided.csv (service type + date)
# - organizations.csv (provider info + location)
# - projects.csv (program type + funder)

# Vibe4Vets ETL:
# 1. Import CSV from HMIS system
# 2. Filter records where Veteran Status = "Yes"
# 3. Extract organization + location + services
# 4. Normalize to Vibe4Vets Resource model
# 5. Calculate trust score (HMIS participation = Tier 1-2)
# 6. Deduplicate against existing resources
```

### CoCs to Prioritize

**Largest/Most Active (Start Here):**
1. Los Angeles CoC (largest Veteran homeless population)
2. New York City CoC (700+ Veterans served by VOA alone)
3. Chicago CoC (Midwest hub)
4. Bay Area CoC (tech-friendly; better data systems)
5. Houston CoC (TxHOME program; established SSVF)

**Medium Priority:**
- Miami, Phoenix, Seattle, Boston, Denver, San Diego, Atlanta

---

## Web Scraping Strategy (For Non-HMIS Data)

### Salvation Army Regional Pages
```python
# backend/connectors/salvation_army_scraper.py
# Target: salvationarmyusa.org + regional affiliates
# Extract: Organization name, location, services, phone
# Frequency: Monthly
```

### Catholic Charities Local Agencies
```python
# backend/connectors/catholic_charities_scraper.py
# Target: catholiccharitiesusa.org + local agency sites
# Extract: Agency name, SSVF status, services, contact
# Frequency: Quarterly
```

### VOA Regional Affiliates
```python
# backend/connectors/voa_scraper.py
# Target: voa.org + affiliate websites (9+ brands)
# Extract: Program name, location, housing type, capacity
# Frequency: Monthly
```

### Methodist/Presbyterian Local Programs
```python
# backend/connectors/faith_communities_scraper.py
# Target: methodistservices.org, pcusa.org + local sites
# Extract: Program name, emergency assistance, housing
# Frequency: Quarterly
```

---

## Implementation Phase Timeline

### Phase 3A: Foundation (Weeks 1-4)
- [ ] Contact VA CFBNP for partnership
- [ ] Reach out to Salvation Army national HQ
- [ ] Identify 3-5 CoCs with active SSVF programs
- [ ] Draft HMIS data-sharing MOA template

### Phase 3B: HMIS Integration (Weeks 5-10)
- [ ] Finalize HMIS data-sharing agreements
- [ ] Build HMIS CSV importer
- [ ] Create Veteran status filter
- [ ] Map HMIS service types to Vibe4Vets categories
- [ ] Build `backend/connectors/hmis_ssvf.py`
- [ ] Test with 3-5 pilot CoCs
- [ ] Deploy monthly refresh job

### Phase 3C: National Organization Outreach (Weeks 8-14)
- [ ] Catholic Charities partnership negotiation
- [ ] VOA national office coordination
- [ ] Collect SSVF program lists
- [ ] Build web scrapers for regional websites
- [ ] Build `backend/connectors/catholic_charities.py`
- [ ] Build `backend/connectors/voa_veteran_programs.py`
- [ ] Deploy quarterly refresh jobs

### Phase 3D: Secondary Organizations (Weeks 12-16)
- [ ] Lutheran Services America coordination
- [ ] Open Door Ministries partnership
- [ ] Identify Methodist/Presbyterian local programs
- [ ] Build faith-based filtering on frontend
- [ ] Establish faith-based category tag

### Phase 3E: Validation & Launch (Weeks 16-20)
- [ ] Cross-validate against NCHV database
- [ ] Test faith-based discovery features
- [ ] Quality assurance on all data
- [ ] Launch faith-based Veteran services integration
- [ ] Promote through VA CFBNP network

---

## Expected Data Volume & Impact

### Conservative Estimate (HMIS + Top 3 Organizations)
- **Resources**: 500-1,500 faith-based Veteran services
- **Coverage**: All 50 states
- **Categories**: Housing, emergency assistance, job training, case management
- **Trust Level**: Primarily Tier 1-2 (federal partnerships)
- **Update Frequency**: Monthly (HMIS) + Quarterly (websites)

### Optimistic Estimate (Full Implementation)
- **Resources**: 2,000-3,500 faith-based services
- **Coverage**: All 50 states + some territories
- **Categories**: All Vibe4Vets categories represented
- **Trust Level**: Mix of Tier 1-3
- **Update Frequency**: Monthly across all sources

### User Impact
- Users find faith-based alternatives for housing
- Cultural/religious community matching for Veterans
- Emergency assistance options in every state
- Diverse service pathways beyond VA.gov alone

---

## Success Metrics

### Launch Criteria
- [ ] 500+ resources integrated (HMIS primary)
- [ ] All 50 states with ≥1 faith-based option
- [ ] Housing + Emergency Assistance categories populated
- [ ] Faith-based tag visible on all resources
- [ ] Trust scores assigned correctly

### Ongoing Success
- [ ] Monthly data refresh 95%+ success rate
- [ ] <1% stale/invalid resources (verified quarterly)
- [ ] User analytics show faith-based filtering usage
- [ ] NCHV database validation shows >90% match rate
- [ ] VA CFBNP recognizes as trusted Veteran resource

---

## Risk Mitigation

### Risk 1: HMIS Data Access Delays
**Mitigation**: Start parallel web scraping while negotiating HMIS MOAs
**Timeline Buffer**: +2 weeks

### Risk 2: Organization Coordination Complexity
**Mitigation**: Use VA CFBNP as trusted intermediary; leverage existing partnerships
**Timeline Buffer**: +3 weeks

### Risk 3: Data Quality Variability
**Mitigation**: NCHV database cross-validation; manual audit of first 100 resources
**Timeline Buffer**: +1 week

### Risk 4: Geographic Gaps
**Mitigation**: Identify rural/underserved regions early; seek CVSO (County Veterans Service Officers) data for supplement
**Timeline Buffer**: +2 weeks

---

## Budget & Resource Estimates

### Personnel
- 1 Backend Engineer: 8-12 weeks (HMIS, connectors, ETL)
- 1 Data Analyst: 4-6 weeks (MOA coordination, validation)
- 1 Frontend Engineer: 2-3 weeks (faith-based filtering UI)

### External Resources
- HMIS software licenses/access: Negotiated through partner organizations
- Web scraping infrastructure: Existing Vibe4Vets resources
- Census API geocoding: Existing budget

### Estimated Cost
- Personnel: $60-80K (contractor rates)
- Infrastructure: Minimal additional (use existing)
- Total: $60-80K over 5 months

---

## Next Steps (Immediate Actions)

### Week 1 Actions
1. Email VACFBNP@va.gov with partnership proposal
2. Draft Salvation Army outreach email (national HQ contact)
3. Research top 5 CoCs in pilot regions (LA, NYC, Chicago, Bay Area, Houston)
4. Review HMIS data standards documentation

### Week 2-3 Actions
1. Schedule call with VA CFBNP
2. Connect with Salvation Army national office
3. Identify HMIS CoC administrators for pilot regions
4. Draft HMIS data-sharing MOA template

### Week 4 Actions
1. Begin HMIS MOA negotiations with pilot CoCs
2. Collect initial Salvation Army SSVF program list
3. Start HMIS CSV importer development
4. Research Catholic Charities national coordination

---

## Reference Materials

### Key Documents Created
- `docs/faith-based-veteran-services.md` - Full research (639 lines)
- `docs/faith-based-veteran-sources-summary.md` - Quick reference table
- `docs/faith-based-implementation-roadmap.md` - This document

### External Resources
- VA CFBNP: https://www.va.gov/CFBNP/
- HMIS Data Standards: https://www.hudexchange.info/programs/hmis/hmis-data-standards/
- NCHV Provider Database: https://nchv.org/
- Salvation Army National: https://www.salvationarmyusa.org/
- Catholic Charities USA: https://www.catholiccharitiesusa.org/
- VOA National: https://www.voa.org/

### Contact Directory
- VA CFBNP: VACFBNP@va.gov
- Salvation Army HQ: 2050 Ballenger Ave, Alexandria, VA
- Catholic Charities USA: 2050 Ballenger Ave, Suite 400, Alexandria, VA 22314
- Volunteers of America: https://www.voa.org/contact
- National Coalition for Homeless Veterans: 1-877-424-3838

---

**Document Type**: Implementation Roadmap
**Version**: 1.0
**Created**: January 28, 2026
**Status**: Ready for Phase 3 Planning
**Issue Closed**: V4V-gofm
