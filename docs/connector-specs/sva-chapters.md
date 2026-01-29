# SVA Chapters Connector Specification

**Organization:** Student Veterans of America (SVA)
**Data Type:** Educational chapters directory
**Estimated Records:** 1,600+ chapters
**Categories:** education, supportServices
**Source Tier:** 2 (nonprofit partner - established, trusted organization)
**Last Updated:** 2026-01-28

---

## Overview

Student Veterans of America is a national nonprofit with **over 1,600 chapters** representing nearly **600,000 student veterans** in **50 states and 4 countries**. SVA chapters operate on college and university campuses, providing peer support, mentoring, and resources for student veterans and military-connected students.

The chapter directory is one of the primary ways Veterans discover local educational support communities.

---

## Directory Access

### Primary URL
**https://studentveterans.org/chapters/find-a-chapter/**

### Supporting Pages
- **Chapters Hub:** https://studentveterans.org/chapters/
- **Establish a Chapter:** https://studentveterans.org/chapters/establish-a-chapter/
- **Chapter Resources:** https://studentveterans.org/chapters/chapter-guide/resources/
- **Chapter Onboarding:** https://studentveterans.org/chapters/chapter-guide/chapter-onboarding/

---

## Directory Structure

### Frontend Implementation

The directory is built with:
- **Page Builder:** Elementor (WordPress)
- **Table Library:** FooTable v2/v3 (jQuery plugin for searchable tables)
- **Backend:** Salesforce Community (Salesforce-based platform at studentveterans.my.site.com)
- **Search Form:** WPForms with CAPTCHA
- **Analytics:** Google Analytics (ID: G-2CHBCX3R1L) + Monster Insights

### Data Loading

Chapter data **does not load inline** in the HTML. Instead:
1. FooTable is configured with table ID `#footable_1852`
2. Data loads **dynamically via AJAX** from a backend endpoint
3. The search functionality suggests data is queried server-side from the Salesforce platform

### Search Capabilities

Users can search by:
- School name
- Chapter name
- City
- State
- Zip code

---

## Data Fields Per Chapter

Based on directory structure analysis and MySVA documentation, each chapter record contains:

| Field | Type | Notes |
|-------|------|-------|
| Chapter Name | String | Unique identifier |
| School/Institution | String | College/university name |
| State | String | 2-letter state code |
| City | String | Campus city |
| Zip Code | String | Campus postal code |
| Chapter Email | Email | Primary contact email |
| Chapter Leader | String | Student veteran contact (optional) |
| Chapter Advisor | String | Faculty/staff advisor contact (optional) |
| Chapter Leader Email | Email | Contact for chapter leader |
| Chapter Advisor Email | Email | Contact for chapter advisor |
| Institution Website | URL | Link to college website |
| Chapter Website/Social | URL | Link to chapter page or social media |
| Last Updated | Date | Last verified/updated in MySVA |

### Data Governance

- **Update Frequency:** Database updated "at the beginning of each month"
- **Chapter Self-Service:** Chapters update info via MySVA portal login
- **Support Email:** [email protected] (for technical issues)
- **New Chapters:** Email [email protected] to add chapter to directory

---

## Scraping/API Approach

### Option 1: Web Scraping (Recommended for MVP)

**Method:** Selenium + FooTable interaction

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Load the page
driver = webdriver.Chrome()
driver.get("https://studentveterans.org/chapters/find-a-chapter/")

# 2. Wait for FooTable to load
wait = WebDriverWait(driver, 10)
table = wait.until(EC.presence_of_element_located((By.ID, "footable_1852")))

# 3. Extract all rows (may require pagination/scrolling)
rows = driver.find_elements(By.CSS_SELECTOR, "#footable_1852 tbody tr")

# 4. Extract data from each row
chapters = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    chapters.append({
        "name": cells[0].text,
        "school": cells[1].text,
        "city": cells[2].text,
        "state": cells[3].text,
        "zip": cells[4].text,
        # ... additional fields based on column order
    })
```

**Challenges:**
- FooTable may implement server-side pagination (need to identify page size)
- JavaScript rendering required (can't use requests/BeautifulSoup)
- CAPTCHA on search form may require manual handling or token bypass

### Option 2: Salesforce API (Advanced)

If Salesforce Community API is available:
```
Base URL: https://studentveterans.my.site.com/services/apexrest/
Endpoint: /chapters or /directory (requires discovery)
Auth: May require OAuth or API key
```

**Status:** Not publicly documented; would require direct contact with SVA.

### Option 3: Contact SVA Directly (Most Reliable)

**Advantages:**
- No scraping risk
- Guaranteed data completeness and accuracy
- Potential for automated monthly feeds
- Relationship-building with SVA

**Contact:**
- Email: [email protected]
- Request: "Bulk chapter data export for non-profit resource directory integration"
- Scope: All 1,600+ chapters with contact information

---

## Connector Implementation

### SVAChaptersConnector Class

```python
from typing import Optional
from datetime import datetime
from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata, Location

class SVAChaptersConnector(BaseConnector):
    """
    Extracts SVA chapter data from the Salesforce-backed directory.

    Data is used to populate the Education category with chapter locations
    where Veterans can connect with peer support and resources.
    """

    @property
    def metadata(self) -> SourceMetadata:
        return SourceMetadata(
            name="Student Veterans of America Chapters",
            url="https://studentveterans.org/chapters/find-a-chapter/",
            tier=2,  # Established nonprofit partner
            frequency="monthly",  # SVA updates database monthly
            description="1,600+ college/university chapters providing peer support, mentoring, and resources for student veterans"
        )

    def run(self) -> list[ResourceCandidate]:
        """Scrape SVA chapter directory and return normalized resources."""
        chapters = self._scrape_chapters()
        candidates = []

        for chapter in chapters:
            candidate = ResourceCandidate(
                # Required fields
                title=f"SVA Chapter at {chapter['school']}",
                description=(
                    f"Student Veterans of America chapter at {chapter['school']} in {chapter['city']}, {chapter['state']}. "
                    f"Connect with student veterans and military-connected students for peer support, mentoring, and resources."
                ),
                categories=["education", "supportServices"],

                # Location
                location=Location(
                    street="",  # Campus location - may not be specific street address
                    city=chapter['city'],
                    state=chapter['state'],
                    zip_code=chapter['zip'],
                    country="USA",
                    latitude=None,  # Will be geocoded by ETL pipeline
                    longitude=None
                ),

                # Contact
                phone=chapter.get('phone', ''),
                email=chapter.get('email', ''),
                website=chapter.get('website', ''),

                # Metadata
                external_id=f"sva_chapter_{chapter['school'].lower().replace(' ', '_')}",
                eligibility="Open to current student veterans and military-connected students at the institution",
                coverage_area="Campus/Local",

                # Source tracking
                source_tier=2,
                source_url=self.metadata.url,
                source_name=self.metadata.name,
                last_verified=datetime.utcnow()
            )
            candidates.append(candidate)

        return candidates

    def _scrape_chapters(self) -> list[dict]:
        """
        Scrape chapters from SVA directory using Selenium.

        Returns list of dicts with keys:
            - school, city, state, zip, name, email, phone, website, advisor_name, advisor_email
        """
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        driver = webdriver.Chrome()
        chapters = []

        try:
            driver.get("https://studentveterans.org/chapters/find-a-chapter/")

            # Wait for FooTable to render
            wait = WebDriverWait(driver, 10)
            table = wait.until(
                EC.presence_of_element_located((By.ID, "footable_1852"))
            )

            # Extract all visible rows
            rows = driver.find_elements(By.CSS_SELECTOR, "#footable_1852 tbody tr")

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:  # Minimum expected columns
                    chapter = {
                        "name": cells[0].text.strip(),
                        "school": cells[1].text.strip(),
                        "city": cells[2].text.strip(),
                        "state": cells[3].text.strip(),
                        "zip": cells[4].text.strip(),
                        "email": cells[5].text.strip() if len(cells) > 5 else "",
                        # Additional fields if columns exist
                    }
                    chapters.append(chapter)

            return chapters

        finally:
            driver.quit()
```

### Requirements

Add to `backend/requirements.txt`:
```
selenium>=4.0.0,<5.0.0
# WebDriver management (optional)
webdriver-manager>=3.9.0
```

### Registration

1. **Export in `backend/connectors/__init__.py`:**
   ```python
   from connectors.sva_chapters import SVAChaptersConnector
   __all__ = [..., "SVAChaptersConnector"]
   ```

2. **Register in `backend/jobs/refresh.py`:**
   ```python
   CONNECTOR_REGISTRY = {
       ...,
       "sva_chapters": SVAChaptersConnector,
   }
   ```

---

## Mapping to Vibe4Vets Resource Model

### Category Mapping

| SVA Context | Vibe4Vets Category | Rationale |
|---|---|---|
| Student Veterans support | **education** | Primary: resources for pursuing educational goals |
| Peer mentoring | **supportServices** | Secondary: case management, peer mentoring aspect |
| Career prep workshops | **employment** | May offer employment-focused programming |

**Recommended:** Tag as `education` primary, cross-index with `supportServices`.

### Fields

| SVA Field | Resource Model | Processing |
|---|---|---|
| Chapter name | `organization.name` | "SVA Chapter at [School]" |
| School | `location.institution` | For disambiguation |
| Address (city, state, zip) | `location.*` | Geocode during ETL enrichment |
| Chapter email | `contact_email` | Primary contact |
| Advisor email/name | `metadata.advisor_*` | For reference/backup contact |
| Chapter website | `website_url` | Link to chapter social media or webpage |
| Last updated | `source_record.verified_at` | Used for freshness calculation |

### Coverage Area

- **Scope:** CAMPUS/LOCAL (institution-specific)
- **Eligibility:** "Open to student veterans and military-connected students at [Institution]"
- **Note:** Not portable across universities (each chapter is distinct entity)

### Trust Score Calculation

```
Base reliability: 0.8 (Tier 2: established nonprofit)
Freshness factor: 1.0 - (days_since_update / 365)  # Decays over 1 year
Final score: 0.8 × freshness_factor

Example: If updated 30 days ago:
  freshness = 1.0 - (30/365) = 0.918
  score = 0.8 × 0.918 = 0.734
```

---

## Data Quality Considerations

### Known Limitations

1. **No street addresses:** SVA chapters are campus-based; specific building/office info may not be available
2. **Advisor contact volatility:** Advisor emails may change annually (when officers rotate)
3. **Social media URLs:** Some chapters may only have Facebook/Instagram, not dedicated websites
4. **Phone numbers:** Not always publicly listed; primarily email-based contact
5. **Geocoding:** Will need Census geocoding for zip codes to determine lat/lon

### Deduplication

- **Primary key:** `(school_name, state)` - Each institution should have one SVA chapter
- **Exception handling:** Some large universities may have multiple chapters (different campuses) - flag for manual review
- **Name variations:** Normalize school names against IPEDS database for consistency

### Review Triggers

Escalate for manual review if:
- Email domain is non-institutional (Gmail, Outlook) - suggest chapter use institution email
- No advisor contact listed (may indicate inactive chapter)
- Zip code + city mismatch (data quality issue)

---

## Update Frequency & Scheduling

### Recommended Schedule

| Frequency | Justification |
|---|---|
| **Primary:** Monthly | SVA explicitly updates database monthly |
| **Secondary:** Quarterly dry-run | Detect new chapters, chapter closures |
| **Urgent:** Ad-hoc on escalation | If chapter reports data issues |

### Job Configuration

```python
# In backend/jobs/scheduler.py

JOBS = [
    {
        "name": "refresh_sva_chapters",
        "job_func": "jobs.refresh.run_connectors",
        "trigger": "cron",
        "day_of_week": "mon",  # First Monday of month
        "hour": 2,
        "minute": 0,
        "args": [["sva_chapters"]],
        "kwargs": {"dry_run": False},
    }
]
```

### Monitoring

- **Alert:** If < 1,400 chapters returned (below expected baseline)
- **Alert:** If > 5% of chapters missing email contact (data quality regression)
- **Metric:** Track chapter addition/removal rate month-over-month

---

## Future Enhancements

### Phase 1: Direct Integration
- [ ] Contact SVA for programmatic data export
- [ ] Negotiate monthly data feed (CSV/API)
- [ ] Establish SLA for data freshness

### Phase 2: Enrichment
- [ ] Scrape chapter websites for programming details (career workshops, etc.)
- [ ] Extract social media links (LinkedIn, Instagram, etc.)
- [ ] Identify chapter specializations (e.g., "leadership development," "job placement focused")

### Phase 3: Bidirectional
- [ ] Allow SVA chapters to claim and update their listing on Vibe4Vets
- [ ] Sync updates back to SVA via API
- [ ] Track chapter feedback/ratings

---

## Technical Notes

### Web Scraping Considerations

**Selenium Setup:**
```bash
# On Linux (WSL or native)
apt-get install -y chromium-browser
pip install selenium webdriver-manager

# Usage
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

**FooTable Pagination:**
- Inspect network tab to identify AJAX endpoint or page size limit
- May need to implement scrolling or "load more" button clicking
- Consider headless mode for performance: `options.headless = True`

**Timeout Handling:**
```python
from selenium.common.exceptions import TimeoutException

try:
    element = wait.until(EC.presence_of_element_located((By.ID, "footable_1852")))
except TimeoutException:
    raise Exception("FooTable failed to load - directory may be temporarily unavailable")
```

### Rate Limiting

- Single scrape of 1,600+ chapters: ~2-3 minutes in headless mode
- **Recommended:** Run during off-hours (2 AM) to avoid impacting SVA website
- **Best practice:** Add random delays between requests if implementing pagination loops

### Error Recovery

If scrape fails mid-way:
1. Log failed chapters for retry
2. Partial load is acceptable (incremental update vs. full replace)
3. Implement idempotent upsert logic in ETL loader

---

## Contact Information

**SVA National Headquarters:**
- Email: [email protected]
- Website: https://studentveterans.org/
- Support: For MySVA technical support or chapter onboarding

**For Connector Development:**
- Initial scraping can proceed without SVA contact
- Recommend outreach after MVP implementation to discuss bulk export options

---

## References

- SVA Homepage: https://studentveterans.org/
- Find a Chapter: https://studentveterans.org/chapters/find-a-chapter/
- Chapter Guide: https://studentveterans.org/chapters/chapter-guide/
- MySVA Portal: https://studentveterans.my.site.com/
- Wikipedia: Student Veterans of America

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-01-28 | 1.0 | Initial specification document |
