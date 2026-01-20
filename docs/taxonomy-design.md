# Vibe4Vets Taxonomy Design: Categories vs Filters

**Status**: Draft
**Issue**: V4V-qy5
**Date**: 2026-01-20

## Executive Summary

This document establishes a clear framework for classifying resource attributes as **Categories** (primary service type), **Subcategories** (service specializations), **Audience Filters** (who the resource serves), or **Tags** (searchable attributes). The framework resolves ambiguity about where to place new attributes like seniors, discounts, mental health, and healthcare.

---

## Decision Framework

### The Core Question

When adding a new attribute, ask: **"What question does this answer?"**

| Layer | Question Answered | Selection | Example |
|-------|-------------------|-----------|---------|
| **Category** | "What type of service does this provide?" | Single primary | housing, employment |
| **Subcategory** | "What specific program is this?" | Multiple allowed | HUD-VASH, SSVF, job-placement |
| **Audience Filter** | "Who is this specifically for?" | Multiple allowed | seniors, families, women |
| **Tag** | "What attributes or features does it have?" | Multiple allowed | free, walk-in, mental-health-support |

### Category Rules (Strict)

A **Category** must meet ALL of these criteria:

1. **Answers "What does this organization DO?"** - It describes the primary service delivered
2. **Mutually exclusive at the primary level** - A resource has ONE primary category (though may touch others)
3. **Warrants dedicated navigation** - Users should be able to browse all [category] resources
4. **Has distinct subcategories** - Each category has specialized programs within it
5. **Stable over time** - Won't change frequently

**Current Categories** (6):
- `employment` - Job placement and career services
- `training` - Education and vocational programs
- `housing` - Shelter and housing assistance
- `legal` - Legal aid and advocacy
- `food` - Food assistance programs
- `benefits` - VA benefits consultation

### Subcategory Rules

A **Subcategory** must:

1. **Belong to exactly one Category** - e.g., "HUD-VASH" belongs to housing
2. **Be a named program or service type** - Specific enough to search for
3. **Help users narrow within a category** - "I want housing, specifically SSVF"

### Audience Filter Rules

An **Audience Filter** describes WHO the resource serves:

1. **Answers "Is this FOR me?"** - Based on demographics or situation
2. **Cross-cuts categories** - Seniors can need housing, employment, food, etc.
3. **Part of eligibility** - Used in the Eligibility Wizard
4. **Binary or bracketed** - seniors (yes/no), age (under_55, 55_61, 62_plus)

### Tag Rules

A **Tag** describes attributes that don't fit above:

1. **Searchable keyword** - Helps find resources
2. **Multiple per resource** - "free", "walk-in", "mental-health-support"
3. **Not eligibility-based** - Describes the resource, not who qualifies
4. **Flexible** - New tags can be added without schema changes

---

## Classification of Proposed Additions

### 1. **Seniors** → AUDIENCE FILTER (not Category)

**Rationale**: "Seniors" answers "who is it for?" not "what does it provide?"

- A senior needs housing → they search Housing + filter by 62+
- A senior needs food → they search Food + filter by 62+
- The service TYPE is housing/food; the audience is seniors

**Implementation**: Already exists as `age_bracket` in EligibilityWizard (62_plus, 65_plus). Add a derived "seniors" convenience filter or surface existing age filters more prominently.

**UI Impact**:
- Eligibility Wizard: ✅ Already has age_bracket
- Filters Sidebar: Add "Age" section with senior options
- Resource Card: No change (show as eligibility badge if relevant)

### 2. **Discounts** → TAG

**Rationale**: "Discounts" is an attribute of how a resource operates, not what it provides.

- "Free" and "sliding-scale" are already in the `cost` field
- "Discounts" is similar - it's a feature/perk
- A discount on training is still training; a discount on housing is still housing

**Implementation**: Add to `tags` array. Resources can have tags like `veteran-discount`, `military-discount`, `free`, `sliding-scale`.

**UI Impact**:
- Tags section on resource cards (already renders tags)
- Possible "Cost" filter in sidebar: Free, Sliding Scale, Discount Available
- Search: "discount" matches tags

### 3. **Mental Health** → TAG (not Category)

**Rationale**: This is the trickiest one. Mental health could be:
- A service type (Category): "Mental health counseling"
- An attribute (Tag): "Housing program with mental health support"

**Decision**: TAG, because:
1. Most mental health support in veteran resources is **integrated** into housing (SSVF), benefits, employment services
2. VA healthcare (mental health services) would be under a future "healthcare" category
3. As a tag, it surfaces resources that have mental health COMPONENTS
4. If we create a dedicated mental health category, we'd duplicate resources or split them confusingly

**Implementation**: Add `mental-health-support` and `counseling` tags. Resources with mental health components get tagged.

**UI Impact**:
- Tags render on resource cards
- Add "Includes Support" filter section: mental-health, case-management, peer-support
- Search: "mental health" matches tags and descriptions

### 4. **Healthcare** → CATEGORY (future addition)

**Rationale**: Healthcare is fundamentally different from existing categories:
1. **Answers "what does it provide?"** - Medical care
2. **Has distinct subcategories** - VA healthcare enrollment, community health centers, mental health clinics
3. **Warrants dedicated navigation** - Users browse healthcare specifically
4. **Not an attribute of other services** - A clinic isn't "housing with healthcare"

**Decision**: Category, but **defer implementation** until:
- VA healthcare facility connector is built
- Mental health clinics are in scope
- Community health centers are sourced

For now, use `benefits` category with `healthcare-enrollment` subcategory for resources that HELP veterans ACCESS healthcare (benefits counseling), not provide it directly.

---

## Mutually Exclusive Categories?

### Recommendation: Single PRIMARY Category, Multiple Allowed for Overlap

**Current state**: `categories: list[str]` allows multiple
**Proposed state**: Keep array, but establish conventions

**Rules**:
1. Every resource has ONE primary category (first in array)
2. Secondary categories allowed for genuine overlap
3. Avoid double-counting in navigation/counts

**Examples of legitimate overlap**:
- Apprenticeship program: Primary `training`, Secondary `employment` (leads to job)
- SSVF: Primary `housing`, Secondary `benefits` (helps with VA benefits too)
- Veterans Court: Primary `legal`, Secondary `training` (if includes job training)

**Examples of BAD overlap**:
- Housing program: Primary `housing`, Secondary `food` just because they have snacks ❌
- Job fair: Primary `employment`, Secondary `training` just because they have info booths ❌

**UI Impact**:
- Resource card shows primary category color/icon
- Secondary categories shown as additional badges
- Filters match on ANY category (union)
- Landing page cards count primary category only (avoid double-counting)

---

## Updated Taxonomy

### Categories (6 current, 1 future)

| ID | Name | Description |
|----|------|-------------|
| `employment` | Employment | Job placement, career services, hiring programs |
| `training` | Training & Education | Vocational rehab, certifications, GI Bill |
| `housing` | Housing | HUD-VASH, SSVF, shelters, housing assistance |
| `legal` | Legal | Legal aid, VA appeals, discharge upgrades |
| `food` | Food Assistance | Food pantries, meal programs |
| `benefits` | Benefits Consultation | VA claims assistance, VSO services |
| `healthcare` | Healthcare *(future)* | VA health, mental health clinics, community health |

### Audience Filters (in Eligibility Wizard)

| Filter | Values | Description |
|--------|--------|-------------|
| `age_bracket` | under_55, 55_61, 62_plus, 65_plus | Age range |
| `household_size` | 1-5+ | Family size |
| `income_bracket` | low, moderate, any | Relative to AMI |
| `housing_status` | homeless, at_risk, stably_housed | Current situation |
| `veteran_status` | true/false | Requires veteran status |
| `discharge` | honorable, other_than_dis, unknown | Discharge type |
| `has_disability` | true/false | Disability-related |

### Tags (Searchable Attributes)

**Benefit Tags**:
- `free`, `sliding-scale`, `veteran-discount`, `military-discount`

**Support Tags**:
- `mental-health-support`, `counseling`, `case-management`, `peer-support`, `crisis-services`

**Access Tags**:
- `walk-in`, `appointment-required`, `virtual-available`, `24-7`

**Audience Tags** (for resources not in eligibility wizard):
- `families`, `women-veterans`, `lgbtq-friendly`, `spanish-speaking`

---

## UI Implications

### Landing Page Category Cards

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Employment  │ │  Training   │ │   Housing   │
│   (icon)    │ │   (icon)    │ │   (icon)    │
│  X resources│ │  X resources│ │  X resources│
└─────────────┘ └─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│    Legal    │ │    Food     │ │  Benefits   │
│   (icon)    │ │   (icon)    │ │   (icon)    │
│  X resources│ │  X resources│ │  X resources│
└─────────────┘ └─────────────┘ └─────────────┘
```

Count = resources with this as PRIMARY category.

### Filters Sidebar (Updated)

```
FILTERS

Categories (checkboxes)        ← Multi-select
├── Employment
├── Training
├── Housing
├── Legal
├── Food
└── Benefits

Age (NEW section)              ← Single-select radio
├── All ages
├── 55-61
├── 62+ (Seniors)
└── 65+

Support Services (NEW)         ← Multi-select checkboxes
├── Mental health support
├── Case management
└── Peer support

Cost (NEW)                     ← Multi-select checkboxes
├── Free
├── Sliding scale
└── Discounts available

Coverage (radio)               ← Single-select
├── All Resources
├── Nationwide Only
└── State-Specific

States (checkboxes)            ← Multi-select
```

### Resource Card Display

```
┌──────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔│← Category accent bar
│ [Icon] Resource Title                    │
│         Organization Name                │
│                                          │
│ Resource description text here...        │
│                                          │
│ [Housing] [Employment] [VA] [Nationwide] │← Categories + location badges
│ [free] [mental-health] [walk-in]         │← Tags (muted, smaller)
│                                          │
│ ┌─ Why this matched ─────────────────┐   │
│ │ • Matches your location (Virginia) │   │
│ │ • Covers housing resources         │   │
│ └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### Eligibility Wizard

Keep current structure. Add prominent "seniors" callout:

```
Age
├── Under 55
├── 55-61
├── 62+ (Senior programs)    ← Highlight this option
└── 65+ (Senior-only)
```

---

## Backend Changes Required

### Schema Changes: NONE

Current schema supports this design:
- `categories: list[str]` - Already supports multiple
- `subcategories: list[str]` - Already exists
- `tags: list[str]` - Already exists

### Data Migration

1. **Populate `tags`** on existing resources:
   - Resources with mental health in description → add `mental-health-support` tag
   - Resources with "free" in cost → add `free` tag
   - Resources with walk-in → add `walk-in` tag

2. **Normalize categories**:
   - Ensure first category is the "primary"
   - Review any resources with >2 categories

### API Changes

1. **Add `tag` query parameter** to search endpoints:
   ```
   GET /api/v1/resources?tags=mental-health-support,free
   ```

2. **Update `/api/v1/search` to accept `age_bracket`** for non-wizard filtering

### Frontend Changes

1. **Update `filters-sidebar.tsx`**:
   - Add missing categories (food, benefits)
   - Add Age section
   - Add Support Services section
   - Add Cost section

2. **Update category colors** in design system for food, benefits (if not already)

---

## Validation: Team Examples

### Example 1: Job Training Bootcamp (Tech Training Institute)

| Field | Value |
|-------|-------|
| **Primary Category** | `training` |
| **Secondary Category** | `employment` (leads to job placement) |
| **Subcategories** | `certifications`, `apprenticeships` |
| **Tags** | `free`, `virtual-available`, `veteran-discount` |
| **Scope** | National |

**Why this works**:
- Browsing "Training" finds it ✓
- Browsing "Employment" finds it (secondary) ✓
- Tag filter "free" finds it ✓
- Search "coding bootcamp discount" finds it ✓

### Example 2: SSVF Housing + Mental Health (Community Housing Inc)

| Field | Value |
|-------|-------|
| **Primary Category** | `housing` |
| **Secondary Category** | `benefits` (helps with VA benefits) |
| **Subcategories** | `ssvf` |
| **Tags** | `mental-health-support`, `case-management`, `free` |
| **Scope** | State (VA, MD, DC) |
| **Eligibility** | age: any, housing_status: homeless/at_risk, income: low |

**Why this works**:
- Browsing "Housing" finds it ✓
- Filter "mental health support" finds it ✓
- Eligibility wizard: homeless + VA → finds it ✓
- Search "SSVF mental health Virginia" finds it ✓
- NOT miscategorized as a "mental health clinic" (that would be healthcare category)

### Example 3: Senior Food Pantry (VFW Post 123)

| Field | Value |
|-------|-------|
| **Primary Category** | `food` |
| **Subcategories** | `food-pantry`, `senior-food` |
| **Tags** | `free`, `walk-in` |
| **Scope** | Local |
| **Eligibility** | age: 62_plus, veteran_status: true |

**Why this works**:
- Browsing "Food" finds it ✓
- Age filter "62+" finds it ✓
- Eligibility wizard: 65+ → finds it ✓
- NOT a new "seniors" category - seniors is WHO, food is WHAT

---

## Acceptance Criteria

### Design (This Document)

- [x] Decision framework clearly distinguishes Category from Filter from Tag
- [x] All proposed items classified with rationale
- [x] Mutually-exclusive vs multiple categories decided
- [x] UI mockups/descriptions for each surface area
- [x] Two team examples validated against the framework
- [ ] Team review and signoff

### Backend (Follow-up Issue)

- [ ] Add `tags` query parameter to resource list/search endpoints
- [ ] Add `age_bracket` to filters sidebar search (non-wizard)
- [ ] Migration script to populate tags from descriptions
- [ ] API documentation updated

### Frontend (Follow-up Issue)

- [ ] Add Food and Benefits categories to filters-sidebar.tsx
- [ ] Add Age filter section
- [ ] Add Support Services filter section
- [ ] Add Cost filter section
- [ ] Add colors/icons for food, benefits categories
- [ ] Test category filtering works with new options

---

## Open Questions for Team Discussion

1. **Healthcare category timing** - Add now as empty, or wait for connector?
2. **Tag discovery UX** - Should we show "popular tags" or let users type?
3. **Primary category enforcement** - Validate at API level or convention only?
4. **Category counts** - Count primary only, or include secondary?

---

## Appendix: Full Category → Subcategory Mapping

```
employment
├── job-placement
├── career-counseling
├── veteran-preference
└── self-employment

training
├── voc-rehab
├── certifications
├── apprenticeships
└── gi-bill

housing
├── hud-vash
├── ssvf
├── emergency-shelter
└── home-repair

legal
├── va-appeals
├── discharge-upgrade
├── legal-aid
└── veterans-court

food
├── food-pantry
├── meal-program
├── mobile-distribution
└── senior-food

benefits
├── disability-claims
├── pension-claims
├── education-benefits
├── healthcare-enrollment
├── survivor-benefits
├── vso-services
└── cvso

healthcare (FUTURE)
├── va-medical-center
├── mental-health-clinic
├── community-health-center
└── telehealth
```
