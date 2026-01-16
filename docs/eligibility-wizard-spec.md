# No-PII Eligibility Wizard Specification

> **Design Status:** Complete - Ready for implementation
> **Issue:** V4V-jqh
> **Focus:** DC/MD/VA housing ecosystem (SSVF + senior housing)

## Problem

Most resources discovered so far are national VA.gov pages. Local resources (SSVF providers, senior housing, food distributions, benefits consults) have location-specific eligibility and intake constraints. Users—especially seniors and less tech-savvy vets—need step-by-step narrowing and clear next actions, but we must not store PII.

## Goals

- Guided eligibility narrowing with **zero PII storage**
- Per-location modeling for programs with differing rules by provider/location
- Explainable results ("why this matches") and actionable intake steps
- Verification metadata + low-friction correction reporting
- Initial focus: DC/MD/VA housing ecosystem (SSVF + senior housing), extensible later

## Non-goals

- **No accounts** - Anonymous access only
- **No PII storage** - No names, addresses, phone numbers, SSNs, DOBs
- **No scheduling/booking system** - We provide intake info, not bookings
- **No eligibility guarantees** - Guidance only, not determination

---

## Proposed UX

### 1) Entry Points

- Existing State selector map → leads to a local search context
- Add an "Eligibility Wizard" panel (optional) at top of search/discover/hub pages

### 2) Eligibility Wizard (Anonymous)

All inputs are coarse/bucketed to avoid collecting PII:

| Input | Options | Storage |
|-------|---------|---------|
| State | Multi-select from existing list | URL param |
| ZIP (optional) | 5-digit | Client-side only (distance calc) |
| Household size | 1, 2, 3, 4, 5+ | URL param |
| Monthly income | Bucketed ranges or client-side calc | URL param (bracket only) |
| Age bracket | <55, 55–61, 62+, 65+ | URL param |
| Disability | Yes / No / Prefer not to say | URL param |
| Housing status | Homeless / At-risk / Stably housed | URL param |
| Active duty | Yes / No | URL param |
| Discharge status | Unknown / Other-than-dishonorable / Dishonorable | URL param |

**Key Privacy Points:**
- ZIP is used **only client-side** for distance calculation; never sent to server
- Income is converted to bracket client-side before any API call
- All filters stored in URL query params (shareable) or localStorage (persistence)

### 3) Result Presentation

Each resource shows:
- **Match reasons chips** (e.g., "62+", "Serves Fairfax County", "Income under 50% AMI")
- **Clear intake CTA** (Call, Website, Directions)
- **"What to bring" checklist** from docs_required field
- **Last verified date** + verification source badge
- **Report update button** (anonymous feedback form)

### 4) Privacy Approach

- Store wizard inputs in URL query params and/or client localStorage only
- Backend receives filters only for the current request; no persistence/logging of raw inputs
- Future: Avoid analytics logging query strings with PII-like data

---

## Data Model

### Current State

- `Organization` - Parent entity
- `Resource` - Programs/services (has eligibility as free-text)
- `Location` - Physical locations with service_area array

### Proposed Changes

Extend `Location` model with structured eligibility and verification fields:

```python
# backend/app/models/location.py - New fields

# Eligibility constraints
age_min: int | None = None
age_max: int | None = None
household_size_min: int | None = None
household_size_max: int | None = None
income_limit_type: str | None = None  # "ami_percent", "monthly_abs", "annual_abs"
income_limit_value: int | None = None
income_limit_ami_percent: int | None = None  # e.g., 50 for 50% AMI
housing_status_required: list[str] = []  # ["homeless", "at_risk"]
active_duty_required: bool | None = None
discharge_required: str | None = None  # "honorable", "other_than_dishonorable"
veteran_status_required: bool = True
docs_required: list[str] = []  # ["DD-214", "Income verification"]
waitlist_status: str | None = None  # "open", "closed", "unknown"

# Intake info
intake_phone: str | None = None
intake_url: str | None = None
intake_hours: str | None = None
intake_notes: str | None = None  # "Walk-ins welcome Tues/Thurs"

# Verification
last_verified_at: datetime | None = None
verified_by: str | None = None  # "official_directory", "provider_contact", "user_report"
verification_notes: str | None = None
```

### Enums

```python
class IncomeLimitType(str, Enum):
    AMI_PERCENT = "ami_percent"
    MONTHLY_ABSOLUTE = "monthly_abs"
    ANNUAL_ABSOLUTE = "annual_abs"
    UNKNOWN = "unknown"

class HousingStatus(str, Enum):
    HOMELESS = "homeless"
    AT_RISK = "at_risk"
    STABLY_HOUSED = "stably_housed"

class VerificationSource(str, Enum):
    OFFICIAL_DIRECTORY = "official_directory"
    PROVIDER_CONTACT = "provider_contact"
    USER_REPORT = "user_report"
    AUTOMATED = "automated"

class WaitlistStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    UNKNOWN = "unknown"
```

---

## API Specification

### Eligibility Filter Endpoint

`GET /api/v1/resources/search`

**New Query Parameters (all optional):**

| Param | Type | Example | Description |
|-------|------|---------|-------------|
| `state` | string | `VA,MD,DC` | Multi-state filter (comma-sep) |
| `counties` | string | `fairfax,arlington` | County filter (lowercase, comma-sep) |
| `age_bracket` | string | `62_plus` | `under_55`, `55_61`, `62_plus`, `65_plus` |
| `household_size` | int | `3` | 1-5 (5 = 5+) |
| `income_bracket` | string | `low` | `low` (<50% AMI), `moderate` (50-80%), `any` |
| `housing_status` | string | `homeless` | `homeless`, `at_risk`, `stably_housed` |
| `veteran_status` | bool | `true` | Veteran requirement filter |
| `discharge` | string | `other_than_dis` | `honorable`, `other_than_dis`, `unknown` |
| `has_disability` | bool | `true` | Disability filter |

**Response Format:**

```json
{
  "results": [
    {
      "id": "uuid",
      "title": "SSVF Program - Northern Virginia",
      "organization_name": "Volunteers of America",
      "description": "...",
      "categories": ["housing"],
      "location": {
        "city": "Fairfax",
        "state": "VA",
        "address": "123 Main St",
        "counties_served": ["Fairfax", "Arlington", "Alexandria"]
      },
      "eligibility": {
        "age_min": null,
        "age_max": null,
        "income_limit_ami_percent": 50,
        "housing_status_required": ["homeless", "at_risk"],
        "docs_required": ["DD-214", "Income verification"],
        "waitlist_status": "open"
      },
      "intake": {
        "phone": "703-555-1234",
        "url": "https://example.org/apply",
        "hours": "Mon-Fri 9am-5pm",
        "notes": "Call for appointment"
      },
      "verification": {
        "last_verified_at": "2026-01-10T14:30:00Z",
        "verified_by": "provider_contact"
      },
      "match_reasons": [
        {"type": "location", "label": "Serves Fairfax County"},
        {"type": "income", "label": "Income under 50% AMI"},
        {"type": "housing_status", "label": "Serves homeless veterans"}
      ],
      "trust_score": 0.85
    }
  ],
  "total": 12,
  "filters_applied": ["state", "housing_status", "income_bracket"]
}
```

### Match Reason Types

| Type | Example Labels |
|------|---------------|
| `location` | "Serves Fairfax County", "Available in Virginia" |
| `age` | "62+", "All ages", "55 and older" |
| `income` | "Income under 50% AMI", "No income requirements" |
| `housing_status` | "Serves homeless veterans", "For at-risk housing" |
| `veteran_status` | "Veterans only", "Veterans and families" |
| `discharge` | "Any discharge accepted", "Honorable discharge required" |
| `category` | "Housing assistance", "Employment services" |

---

## UI Components

### EligibilityWizard Component

**Location:** `frontend/src/components/EligibilityWizard.tsx`

- Step-by-step form or collapsible panel (follows FiltersSidebar pattern)
- Stores state in URL params (shareable links)
- Falls back to localStorage for persistence across sessions
- "Skip" option for each question
- "Clear all" to reset

**State Management:**
```typescript
interface EligibilityState {
  states: string[];
  ageBracket: 'under_55' | '55_61' | '62_plus' | '65_plus' | null;
  householdSize: number | null;
  incomeBracket: 'low' | 'moderate' | 'any' | null;
  housingStatus: 'homeless' | 'at_risk' | 'stably_housed' | null;
  veteranStatus: boolean | null;
  discharge: 'honorable' | 'other_than_dis' | 'unknown' | null;
  hasDisability: boolean | null;
}
```

### MatchReasonChips Component

**Location:** `frontend/src/components/MatchReasonChips.tsx`

- Badge-style chips showing why resource matched
- Color-coded by match type (follows existing categoryColors pattern)
- Tooltip on hover explains the match

### ResourceDetail Intake Section

**Location:** Update `frontend/src/app/resources/[id]/page.tsx`

- "How to Apply" card with phone, website, directions
- "What to Bring" checklist from docs_required
- Verification badge with last_verified_at
- "Report Update" button (anonymous feedback form)

---

## Data Sourcing (DC/MD/VA First)

### Initial Dataset Target

10-20 housing resources with full eligibility data:

1. **SSVF Providers** - Official VA SSVF provider directory
2. **HUD-VASH** - Public housing with veteran preference
3. **Senior Housing** - 62+ age-restricted properties

### Data Collection

- Identify official SSVF provider directory source(s)
- Map providers to locations + counties served
- Verify intake details via provider contact
- Seed with verified phone, hours, docs_required

---

## Rollout Plan

### Phase 1: Schema Migration
- Add eligibility + verification fields to Location model
- Create Alembic migration
- Update Location model in `backend/app/models/location.py`

### Phase 2: API Extension
- Add eligibility filters to search endpoint
- Implement match_reasons generation logic
- Update search service in `backend/app/services/search.py`

### Phase 3: Wizard UI
- Create EligibilityWizard component
- Add MatchReasonChips component
- Integrate with search page
- URL state management

### Phase 4: Seed Data
- Seed 10-20 DC/MD/VA housing providers
- Create seed script `backend/scripts/seed_dmv_housing.py`
- Verify data accuracy

### Phase 5: Iterate
- Expand to food distributions
- Expand to benefits consults
- User feedback collection

---

## Implementation Tasks

| # | File | Task |
|---|------|------|
| 1 | `backend/alembic/versions/*_add_eligibility_fields.py` | Migration for Location eligibility fields |
| 2 | `backend/app/models/location.py` | Add eligibility/intake/verification fields |
| 3 | `backend/app/services/search.py` | Add eligibility filter logic + match_reasons |
| 4 | `backend/app/api/v1/search.py` | Add query params for eligibility filters |
| 5 | `frontend/src/components/EligibilityWizard.tsx` | Wizard component with URL state |
| 6 | `frontend/src/components/MatchReasonChips.tsx` | Match reason display component |
| 7 | `frontend/src/app/resources/[id]/page.tsx` | Add intake section to detail page |
| 8 | `backend/scripts/seed_dmv_housing.py` | Seed script for DC/MD/VA housing data |

---

## Acceptance Criteria Checklist

- [x] Wizard inputs (no PII) and where they're stored (URL/localStorage)
- [x] Proposed data model changes for per-location eligibility + verification
- [x] Search API filter params and expected response including match reasons
- [x] UX for results and reporting updates
- [x] Initial DC/MD/VA housing-focused rollout plan
- [x] Explicitly states no PII storage and avoids account creation
- [x] Clear implementation tasks can be derived from the spec
