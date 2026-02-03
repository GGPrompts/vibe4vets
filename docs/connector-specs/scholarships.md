# Veteran Scholarships Connector Specification

## Overview

This document outlines options for integrating Veteran scholarship opportunities into Vibe4Vets. Veterans have access to numerous scholarship programs ranging from federal benefits to private foundation awards. This spec evaluates data sources, integration approaches, and operational requirements.

---

## Integration Options Analysis

### 1. Military.com Scholarship Finder

**Status:** No Public API Available

**Current Situation:**
- Military.com operates a comprehensive scholarship finder with thousands of programs
- No official API documentation available for developers
- Requires direct partnership inquiry with Military.com

**Integration Approach:**
- **Contact Path:** Reach out to Military.com partnerships team for API access or data licensing
- **Alternative:** Web scraping with proper attribution and robots.txt compliance
- **Viability:** Moderate - would require ongoing relationship management

**Data Quality:** High (vetted by Military.com editorial team)

---

### 2. Fastweb.com Scholarship Database

**Status:** No Direct Developer API (B2C Platform)

**Current Situation:**
- Fastweb operates the largest scholarship database with 1.5M+ opportunities
- Pioneered online scholarship search in 1995
- Partners with Military.com for military/Veteran scholarships
- No public API for B2B data access

**Educator Program:**
- Fastweb for Educators allows schools to create custom scholarship lists
- Listbuilder tool enables filtering by demographics
- Free resource for educational institutions

**Integration Approach:**
- **Direct API:** Not available - would require business partnership discussion
- **Data Licensing:** Contact Fastweb business development for wholesale data
- **Viability:** Low-to-Moderate - heavily B2C focused, unlikely to license raw data

---

### 3. Recommended Approach: Individual Connector Architecture

Rather than depending on external APIs, build **individual connectors** for top-tier scholarship programs. This approach provides:

- **Data Control:** Direct source management with version control
- **Freshness:** Annual update cycles aligned with application deadlines
- **Transparency:** Clear attribution and program details for Veterans
- **Reliability:** No third-party dependency or API changes

---

## Top 10 Individual Veteran Scholarship Programs

### 1. Pat Tillman Foundation Scholarship

**Program:** Pat Tillman Scholar Program (Tillman Scholars)

| Property | Value |
|----------|-------|
| **Organization** | Pat Tillman Foundation |
| **URL** | https://pattillmanfoundation.org/ |
| **Award Amount** | ~$10,000/year (varies by need) |
| **Application Deadline** | December 1 (annual) |
| **Award Deadline** | ~May 31 |
| **Target Audience** | Service members, Veterans, military spouses |
| **Education Level** | Full-time undergraduate or graduate |
| **Application Cycle** | Annual (December 1 - typically Jan) |

**Eligibility Requirements:**
- U.S. service members, Veterans, or military spouses
- Pursuing full-time degree at accredited U.S. institution
- Strong academic performance
- Demonstrated leadership and community involvement
- Financial need considered

**Award Details:**
- Average $10,000 per academic year
- Variable based on financial need and educational expenses
- Covers tuition, books, living expenses

**Application Format:**
- Online application portal
- Essays required
- Financial documentation (FAFSA)
- Military service documentation
- Character reference letter

**Data Freshness:** Annual - Application opens December 1 each year

**Scrapeable:** ⭐ No (form-based application, requires portal access)
**Manual Entry:** ✅ Yes - Program details stable year-to-year

**Integration Notes:**
- One of the most competitive (3% acceptance, ~2,000 applicants for 60 slots)
- Excellent for high-achieving Veterans
- Leadership component differentiates from other scholarships

---

### 2. Folds of Honor Military Higher Education Scholarship

**Program:** Folds of Honor Scholarship

| Property | Value |
|----------|-------|
| **Organization** | Folds of Honor Foundation |
| **URL** | https://foldsofhonor.org/scholarships/ |
| **Award Amount** | Up to $5,000/year ($2,500 max per term, $100 minimum) |
| **Application Deadline** | February 1 - March 31 (annual) |
| **Award Notification** | Mid-July |
| **Target Audience** | Children/spouses of fallen/disabled service members |
| **Education Level** | K-12, associate, bachelor's, or graduate |

**Eligibility Requirements:**
- Spouses of fallen service members
- Children of fallen service members
- Children of 10% or greater VA-rated disabled Veterans
- Active duty spouses (if service member has Purple Heart)
- Veterans with 10% or greater VA disability rating

**Award Details:**
- Up to $5,000 annually
- $2,500 maximum per term
- $100 minimum payment
- Disburses directly to educational institution
- Based on unmet financial need

**Application Format:**
- Online portal at foldsofhonor.org
- Documentation of military service/disability
- FAFSA strongly encouraged
- School enrollment verification

**Data Freshness:** Annual - Applications open February 1, close March 31

**Scrapeable:** ⭐ No (online portal-based)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- 73,000 scholarships awarded since 2007
- Highest impact on military families (91% of expenses support scholarships)
- Specifically targets families of fallen/disabled Veterans
- Contact: (918) 274-4700, Mon-Fri 8am-5pm Central

---

### 3. Disabled American Veterans (DAV) Auxiliary National Education Scholarship

**Program:** DAV Education Scholarship Fund

| Property | Value |
|----------|-------|
| **Organization** | Disabled American Veterans Auxiliary |
| **URL** | https://www.dav.org/get-involved/volunteer/dav-scholarships/ |
| **Award Amount** | Full-time: up to $2,500; Part-time: up to $750 |
| **Application Deadline** | Varies by program (check annually) |
| **Target Audience** | Veterans, disabled Veterans, family members |
| **Education Level** | Accredited college, university, vocational |

**Eligibility Requirements:**
- DAV/DAV Auxiliary membership or volunteer hours
- Pursuing degree at accredited institution
- U.S. citizens or permanent residents
- Enrolled students (full or part-time)

**Volunteer Scholarship (Premium):**
- Age 21 or younger
- Minimum 100 volunteer hours (DAV/DAV Auxiliary)
- Awards: $30K, $20K, $15K, $10K (2), $7.5K (4), $5K (4), $2.5K (2)

**Award Details:**
- Educational Scholarship: $2,500 full-time, $750 part-time annually
- Volunteer Scholarship: Up to $30,000 for exceptional volunteers
- Multiple renewal opportunities

**Application Format:**
- Online application
- Volunteer hours documentation (if applicable)
- Academic transcripts
- Financial need documentation

**Data Freshness:** Annual

**Scrapeable:** ⭐ Partial (static pages exist, but deadlines change)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- DAV is Tier 2 non-profit (highly credible)
- Active volunteer component increases engagement
- Multiple pathways (scholarship vs. volunteer award)

---

### 4. American Legion Legacy Scholarship

**Program:** Legacy Scholarship (Post-9/11)

| Property | Value |
|----------|-------|
| **Organization** | The American Legion |
| **URL** | https://www.legion.org/get-involved/scholarships |
| **Award Amount** | Up to $20,000 total (varies by state) |
| **Application Deadline** | March 15 (annual) |
| **Target Audience** | Children of post-9/11 fallen/disabled Veterans |
| **Education Level** | Accredited U.S. college/university |

**Eligibility Requirements:**
- Child of service member killed in post-9/11 combat
- Child of Veteran with 50%+ VA disability rating from post-9/11 service
- Must be under 25 years old
- Enrolled full-time at accredited institution

**Award Details:**
- Up to $20,000 per academic year
- Renewable for 4 years (undergraduate)
- Based on financial need and merit

**Application Format:**
- Online application via legion.org
- Military documentation (DD-214, disability rating)
- FAFSA required
- Academic transcripts
- Essay

**Data Freshness:** Annual

**Scrapeable:** ⭐ Partial
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Tier 2 non-profit (high credibility)
- Specifically targets post-9/11 families
- Substantial award amounts
- Also offers Samsung Scholarship for Boys/Girls State

---

### 5. Posse Veterans Program Full-Tuition Scholarship

**Program:** Posse Scholars - Veterans Track

| Property | Value |
|----------|-------|
| **Organization** | The Posse Foundation |
| **URL** | https://www.possefoundation.org/recruiting-students/veteran-nominations |
| **Award Amount** | Full tuition (100%) + additional financial aid for room/board |
| **Application Deadline** | Varies by cohort (rolling) |
| **Target Audience** | Veterans without bachelor's degrees |
| **Education Level** | Bachelor's degree at Posse partner colleges |
| **Partner Colleges** | 70+ selective institutions |

**Eligibility Requirements:**
- Veteran of U.S. Armed Forces (any branch)
- No bachelor's degree
- High school diploma or GED
- Willingness to attend summer pre-college training (NYC, 1 month)
- SAT/ACT scores (not determining factor)
- Must be nominated (nomination required)

**Award Details:**
- Full tuition for all 4 years (partner institution guarantee)
- Additional financial aid covers room, board, fees
- Covers gap after GI Bill/Yellow Ribbon exhaustion
- Mentoring and support services included

**Selection Process:**
- Nomination by sponsor (employer, community org, etc.)
- Group interviews (Dynamic Assessment Process)
- 3-stage selection process

**Data Freshness:** Rolling admissions

**Scrapeable:** ⭐ No (nomination-required)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Unique "peer posse" model (cohorts of 10)
- One-month summer program required (intensive but valuable)
- Covers tuition gaps after federal benefits
- Partner college network of elite institutions
- Highly selective but high support

---

### 6. Post-9/11 GI Bill (Chapter 33) - Federal Benefit

**Program:** Post-9/11 GI Bill Educational Benefit

| Property | Value |
|----------|-------|
| **Organization** | U.S. Department of Veterans Affairs |
| **URL** | https://www.va.gov/education/about-gi-bill-benefits/post-9-11/ |
| **Award Amount** | Up to $29,920.95/year tuition + $1,000 books + BAH stipend |
| **Application Deadline** | Rolling (apply anytime) |
| **Target Audience** | Service members with 36+ months active duty (post-9/11) |
| **Education Level** | Undergraduate, graduate, vocational, apprenticeship |

**Eligibility Requirements:**
- Active duty service on or after September 11, 2001
- 36 months continuous or aggregate service (honorably discharged)
- Must use within 15 years of discharge
- Full-time or part-time enrollment

**Benefit Amounts (2025-2026):**
- **Tuition & Fees:** Up to $29,920.95/year (public in-state maximum)
- **Books & Supplies:** Up to $1,000/year (prorated for part-time)
- **Monthly Housing Allowance (MHA):** Based on BAH for E-5 with dependents (location-specific)

**Yellow Ribbon Program:**
- Partner schools waive tuition over national max
- VA matches school waiver amount
- Covers private/out-of-state/graduate school costs

**Application Format:**
- Apply online at VA.gov or through school
- Requires Certificate of Eligibility (COE)
- Enrollment verification from school

**Data Freshness:** Ongoing (rates update annually on August 1)

**Scrapeable:** ⭐ Yes (VA website has static rates)
**Manual Entry:** ✅ Yes (but recommend periodic VA.gov audit)

**Integration Notes:**
- **Core benefit** for all post-9/11 Veterans
- Most Veterans should apply for this first
- Integrates with Yellow Ribbon at partner schools
- Can be combined with other scholarships
- Should appear prominently on Vibe4Vets

---

### 7. Montgomery GI Bill (MGIB-AD) - Chapter 30

**Program:** Montgomery GI Bill - Active Duty

| Property | Value |
|----------|-------|
| **Organization** | U.S. Department of Veterans Affairs |
| **URL** | https://www.va.gov/education/about-gi-bill-benefits/montgomery-selected-reserve/ |
| **Award Amount** | $2,518/month (full-time, 2025-2026) |
| **Application Deadline** | Rolling |
| **Target Audience** | Active duty service members (pre-9/11) or Selected Reserve |
| **Education Level** | Undergraduate, graduate, vocational |

**Eligibility Requirements:**
- Active duty service (or Selected Reserve)
- Completed 2-4 years of service
- High school diploma or equivalency
- Enrolled in approved education program

**Benefit Amounts:**
- Monthly stipend varies by service length and enrollment
- Full-time: $2,518/month (2025-2026)
- Part-time: Prorated
- No housing allowance (stipend-based)

**Application Format:**
- Apply online at VA.gov
- Requires Certificate of Eligibility
- School enrollment verification

**Data Freshness:** Annual (rates update)

**Scrapeable:** ⭐ Yes
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Predecessor to Post-9/11 GI Bill
- Still important for pre-9/11 Veterans
- Simpler benefit (stipend rather than tuition + BAH)
- Can be compared side-by-side with Post-9/11 GI Bill

---

### 8. Iraq and Afghanistan Service Grant (IASG) - Federal Grant

**Program:** Federal Iraq & Afghanistan Service Grant

| Property | Value |
|----------|-------|
| **Organization** | U.S. Department of Education / VA |
| **URL** | https://studentaid.gov/help-center/answers/article/iasg |
| **Award Amount** | Up to $1,000-$6,895/year (equals max Pell Grant) |
| **Application Deadline** | FAFSA deadline (June 30 for current year) |
| **Target Audience** | Children of service members killed in Iraq/Afghanistan |
| **Education Level** | Undergraduate (degree-seeking) |

**Eligibility Requirements:**
- Parent or guardian died in military service (Iraq/Afghanistan post-9/11)
- Dependent under 24 OR enrolled part-time at time of death
- High school diploma/GED
- Unable to qualify for Pell Grant on Student Aid Index alone

**Note:** Effective 2024-25, IASG replaced by Special Rule for Pell Grants (broader eligibility)

**Award Details:**
- Maximum award: Equal to max Pell Grant for academic year
- Cannot exceed cost of attendance
- Prorated for part-time enrollment
- Coordinated with other aid

**Application Format:**
- FAFSA filing (federal form)
- School financial aid office confirms eligibility

**Data Freshness:** Annual

**Scrapeable:** ⭐ Partial (eligibility changing, requires annual audit)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Federal program (high credibility)
- Smaller award amounts vs. scholarships
- Highly specific eligibility (children of fallen)
- Consider pairing with Special Rule for Pell Grants (2024-25+)

---

### 9. Student Veterans of America (SVA) John Edelman Scholars Scholarship

**Program:** John Edelman Mental Health Counseling Scholarship

| Property | Value |
|----------|-------|
| **Organization** | Student Veterans of America & John Edelman Foundation |
| **URL** | https://studentveterans.org/programs-events/scholarships/john-edelman-scholars/ |
| **Award Amount** | $10,000 per scholarship (5 awarded annually) |
| **Application Deadline** | Typically September/October (check annually) |
| **Target Audience** | Student Veterans pursuing mental health counseling |
| **Education Level** | Undergraduate or graduate (STEM eligible via Northrop Grumman) |

**Eligibility Requirements:**
- Current or enrolled student Veteran
- Full-time enrollment at U.S. university
- Pursuing degree toward mental health counseling career
- Strong academic performance
- Demonstrated commitment to addressing Veteran mental health

**Award Details:**
- $10,000 per award
- 5 scholarships annually (John Edelman program)
- Additional Northrop Grumman STEM scholarships: $2,000 (5 annually)

**Application Format:**
- Online application via Student Veterans of America
- Essays (leadership, career goals, Veteran mental health focus)
- Academic transcripts
- Personal statement

**Data Freshness:** Annual

**Scrapeable:** ⭐ No (application portal)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Focuses on mental health (key Veteran need)
- Tier 2 non-profit (highly credible)
- Good for post-service educational goals
- SVA also manages Northrop Grumman STEM scholarships

---

### 10. Gratitude Initiative (formerly Operation Gratitude) Scholarships

**Program:** Gratitude Initiative Scholarship Program

| Property | Value |
|----------|-------|
| **Organization** | Gratitude Initiative |
| **URL** | https://gratitudeinitiative.org/ |
| **Award Amount** | Varies (full range available) |
| **Application Deadline** | Rolling (year-round) |
| **Target Audience** | Military families, Veterans, dependents |
| **Education Level** | All levels (K-12 through graduate) |

**Eligibility Requirements:**
- Children/spouses of:
  - Service members killed in line of duty
  - Veterans/service members wounded/injured/disabled in duty
  - Active-duty service members (all branches, post-9/11)
  - Reserve/National Guard (activated post-9/11)
  - Honorably discharged Veterans (post-9/11)
- U.S. citizens
- In-state or online education

**Program Services (Beyond Scholarships):**
- College preparatory program
- Career counseling
- Free educational workshops
- Test prep resources
- Holistic support services

**Award Details:**
- Scholarship amounts vary
- Multiple opportunities throughout year
- Emphasis on comprehensive support vs. single award
- Free services to military families

**Application Format:**
- Online portal at gratitudeinitiative.org
- Rolling admissions
- Eligibility verification
- Essay or application materials vary

**Data Freshness:** Rolling/Ongoing

**Scrapeable:** ⭐ Partial (rolling deadline makes automation difficult)
**Manual Entry:** ✅ Yes

**Integration Notes:**
- Unique "ecosystem" approach (scholarships + counseling + resources)
- Broader eligibility than some foundations
- Good for families seeking comprehensive support
- Rolling applications reduce pressure vs. single deadline

---

## Summary Table: Top 10 Programs

| Program | Award | Deadline | Audience | API/Scrape | Manual |
|---------|-------|----------|----------|-----------|--------|
| Pat Tillman | ~$10,000 | Dec 1 | Service members/spouses | ⭐ No | ✅ Yes |
| Folds of Honor | $5,000 | Feb 1-Mar 31 | Children of fallen | ⭐ No | ✅ Yes |
| DAV Auxiliary | $750-$2,500 | Varies | DAV members | ⭐ Partial | ✅ Yes |
| American Legion | $20,000 | Mar 15 | Children of post-9/11 | ⭐ Partial | ✅ Yes |
| Posse Veterans | Full tuition | Rolling | Veterans (nomination) | ⭐ No | ✅ Yes |
| Post-9/11 GI Bill | ~$30K/year | Rolling | Post-9/11 Veterans | ⭐ Yes | ✅ Yes |
| Montgomery GI | $2,518/mo | Rolling | Pre-9/11 service | ⭐ Yes | ✅ Yes |
| IASG | $1K-$6.9K | FAFSA | Children of fallen | ⭐ Partial | ✅ Yes |
| SVA John Edelman | $10,000 | Sept/Oct | Student Veterans | ⭐ No | ✅ Yes |
| Gratitude Initiative | Varies | Rolling | Military families | ⭐ Partial | ✅ Yes |

---

## Data Freshness & Update Strategy

### Annual Cycles

Most scholarship programs follow an **academic calendar cycle**:

| Timing | Action |
|--------|--------|
| **August-September** | New academic year benefits announced; GI Bill rates published |
| **September-October** | Fall application deadlines open (SVA, some private scholarships) |
| **December-January** | Winter/spring deadlines (Pat Tillman, others) |
| **February-March** | Early spring deadlines (Folds of Honor, Legion) |
| **April-May** | Late spring deadlines; award notifications begin |
| **June-July** | Summer preparation; enrollment verification |

### Recommended Update Schedule

| Frequency | Task | Owner |
|-----------|------|-------|
| **Quarterly** | Audit VA.gov GI Bill rates (August 1, annually) | Automated task |
| **Semi-annually** | Review Fastweb Military.com partnership updates | Manual |
| **Annually** (Nov-Dec) | Update all scholarship deadlines for next cycle | Manual review |
| **As-needed** | Capture eligibility changes (e.g., IASG → Pell Rule) | Monitor press releases |

### Data Validation

- Verify award amounts on official source websites before updating
- Cross-reference deadlines across military.com and official sources
- Check for eligibility requirement changes
- Confirm contact information annually

---

## Recommended Connector Implementation

### Architecture: `ScholarshipsConnector`

Create a modular connector that manages multiple scholarship sources:

```python
# backend/connectors/scholarships.py

class ScholarshipsConnector(BaseConnector):
    """Aggregates top Veteran scholarships from authoritative sources."""

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Veteran Scholarships",
            url="https://vibe4vets.org",
            tier=2,  # Mix of federal (tier 1) and nonprofit (tier 2)
            frequency="annual",  # Data refreshed once per year
        )

    def run(self) -> list[ResourceCandidate]:
        """Fetch scholarships from curated sources."""
        scholarships = [
            self._pat_tillman(),
            self._folds_of_honor(),
            self._dav_auxiliary(),
            self._american_legion(),
            self._posse_veterans(),
            self._post_9_11_gi_bill(),
            self._montgomery_gi_bill(),
            self._iasg(),
            self._sva_john_edelman(),
            self._gratitude_initiative(),
        ]
        return scholarships

    def _pat_tillman(self) -> ResourceCandidate:
        """Pat Tillman Scholar Program."""
        return ResourceCandidate(
            title="Pat Tillman Scholar Program",
            description="Leadership-focused scholarship for service members, Veterans, and military spouses pursuing full-time degrees. Average $10,000/year. Highly competitive (3% acceptance).",
            organization_name="Pat Tillman Foundation",
            website="https://pattillmanfoundation.org/apply/",
            phone="Unavailable (online portal)",
            categories=["education", "financial"],
            eligibility_summary="Service members, Veterans, military spouses; full-time student; strong academics; leadership commitment",
            tags=["scholarship", "highly-competitive", "leadership-focused"],
        )
        # ... etc
```

### Data Storage

Store scholarships as `Resource` entities with:

- **Category:** `education` (primary)
- **Tags:** `scholarship`, `federal-benefit` or `private-foundation`, deadline window
- **Eligibility fields:** Encoded in resource description and eligibility summary
- **Trust score:** Tier 1 (federal) or Tier 2 (nonprofit) depending on source

### Search & Discovery

Enable Veterans to find scholarships by:

- **Category filter:** "Education" or "Scholarships"
- **Eligibility filters:**
  - Service period (post-9/11, pre-9/11, any)
  - Relationship (Veteran, dependent, survivor)
  - Disability rating (10%+ for some)
  - Degree level (undergraduate, graduate, vocational)
- **Award amount range** (low, moderate, high)
- **Deadline urgency** (open now, upcoming, closed)

---

## Alternative Integration: Third-Party Partnerships

### If Direct API Becomes Available

Should Military.com, Fastweb, or another major platform offer API access:

1. **Evaluate data licensing terms**
   - Cost per record
   - Update frequency guarantees
   - Attribution requirements
   - Exclusive vs. non-exclusive rights

2. **Build adapter layer** (`backend/connectors/military_com_api.py`)
   - Map external schema to ResourceCandidate
   - Implement trust score calculations
   - Handle pagination and rate limits

3. **Maintain fallback connectors**
   - Keep manual/scraped data for redundancy
   - Compare data freshness between sources
   - Alert on divergence

---

## Implementation Roadmap

### Phase 1: MVP (Scholarships v0.1)

**Deliverable:** Manual curation of top 10 programs

- [ ] Create `ScholarshipsConnector` with hardcoded data
- [ ] Test data validation and trust scoring
- [ ] UI: Add "Education" category with scholarship filter
- [ ] Document update process

**Timeline:** 1-2 weeks
**Effort:** Low (no API integration, data stability high)

### Phase 2: Enhanced (Scholarships v1.0)

**Deliverable:** Expanded program list + annual refresh automation

- [ ] Expand to 30+ scholarship programs
- [ ] Add eligibility-driven filtering (service period, disability, etc.)
- [ ] Create admin task for annual deadline updates
- [ ] Build notifications for upcoming deadlines

**Timeline:** 3-4 weeks
**Effort:** Moderate (requires UI enhancements, job scheduling)

### Phase 3: Integration (Scholarships v2.0)

**Deliverable:** API partnerships or smart scraping

- [ ] Attempt Military.com partnership
- [ ] Implement web scraper for static scholarship pages (if approved)
- [ ] Build data validation pipeline
- [ ] Add scholarship matching to chat endpoint

**Timeline:** 6-8 weeks
**Effort:** High (requires legal review, ongoing maintenance)

---

## Legal & Attribution Considerations

### Web Scraping Guidelines

If scraping scholarship pages:

- ✅ **Respect robots.txt** on source domains
- ✅ **Include attribution** in resource description ("Data from [Source Name]")
- ✅ **Link directly** to official application portals
- ✅ **Cache responsibly** (daily updates max, not per-request)
- ✅ **Monitor terms of service** for changes

### Data Licensing

- Pat Tillman Foundation: Public information, no explicit license
- VA.gov content: Public domain (can reuse with attribution)
- Folds of Honor: Check with organization before data use
- Military.com: Licensed content (would require partnership)

### Privacy

- **Do NOT store** scholarship application data or PII
- **Do NOT track** which Veteran applied to which scholarship
- **Do provide** direct links to official applications (no redirect capture)

---

## Success Metrics

### Phase 1 (MVP)

- [ ] 10 major scholarships indexed
- [ ] Searchable by category and award type
- [ ] Clear deadline visibility (upcoming, open, closed)
- [ ] >90% data accuracy (vs. official sources)

### Phase 2

- [ ] 30+ scholarships indexed
- [ ] Eligibility-driven filtering working
- [ ] Annual refresh process documented
- [ ] Veterans can narrow results to relevant programs

### Phase 3

- [ ] Real-time deadline tracking (automated alerts)
- [ ] Chat integration (AI recommends scholarships based on profile)
- [ ] 50+ scholarships indexed
- [ ] Data freshness >95% (automatically validated)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Deadlines become outdated | Veterans miss opportunities | Automated annual refresh; prominent deadline display |
| Eligibility requirements change | Incorrect guidance to Veterans | Source audit process; link to official pages |
| Third-party platform changes TOS | Loss of data access | Maintain independent scrapers/connectors as backup |
| No partner API available | Manual-only data entry | Design connector architecture for sustainable curation |
| Scholarship program closes | Orphaned resource in database | Annual validation audit; mark inactive resources |

---

## References & Resources

### Federal Benefits
- [VA GI Bill Overview](https://www.va.gov/education/about-gi-bill-benefits/)
- [Post-9/11 GI Bill Rates](https://www.va.gov/education/benefit-rates/post-9-11-gi-bill-rates/)
- [Yellow Ribbon Program](https://www.va.gov/education/about-gi-bill-benefits/post-9-11/yellow-ribbon-program/)
- [Student Aid (IASG)](https://studentaid.gov/help-center/answers/article/iasg)

### Nonprofit Scholarships
- [Pat Tillman Foundation](https://pattillmanfoundation.org/)
- [Folds of Honor](https://foldsofhonor.org/)
- [Disabled American Veterans](https://www.dav.org/)
- [American Legion](https://www.legion.org/)
- [Student Veterans of America](https://studentveterans.org/)

### Search Platforms
- [Military.com Scholarships](https://www.military.com/education/money-for-school/scholarships)
- [Fastweb.com](https://www.fastweb.com/)
- [Bold.org Veteran Scholarships](https://bold.org/scholarships/by-demographics/veteran-scholarships/)
- [Scholarships360 Veteran Listing](https://scholarships360.org/scholarships/scholarships-for-veterans/)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-28 | Claude Code | Initial spec with 10 programs, integration options analysis |
| TBD | TBD | Team | Updates after API partnership inquiries |
