# Food Assistance Parallel Collection Template

## Quick Start

Run 3 terminals in parallel. Each terminal spawns 6-8 Haiku subagents.

### Terminal 1 Command
```
cd /home/marci/projects/vibe4vets && claude

# Then paste:
Using Haiku subagents IN PARALLEL, collect food assistance resources for veterans. Each agent searches 1-2 metro areas.

Agent assignments (spawn ALL in parallel):
1. New York City metro area
2. Philadelphia, PA + Pittsburgh, PA
3. Boston, MA + Providence, RI
4. Newark/Jersey City, NJ + Hartford, CT
5. Cleveland, OH + Columbus, OH
6. Detroit, MI + Buffalo, NY
7. Chicago, IL

For each area, search:
- "[City] veteran food pantry"
- "[City] VFW food bank"
- "[City] VA medical center food"
- "[City] American Legion food assistance"

Output format: JSON array per agent (see template below).
Save results to: /home/marci/projects/vibe4vets/backend/data/food/northeast-raw.json
```

### Terminal 2 Command
```
cd /home/marci/projects/vibe4vets && claude

# Then paste:
Using Haiku subagents IN PARALLEL, collect food assistance resources for veterans. Each agent searches 1-2 metro areas.

Agent assignments (spawn ALL in parallel):
1. Miami, FL + Fort Lauderdale, FL
2. Tampa, FL + Orlando, FL
3. Atlanta, GA + Charlotte, NC
4. Houston, TX + Dallas, TX
5. San Antonio, TX + Austin, TX
6. Nashville, TN + Memphis, TN
7. New Orleans, LA + Jacksonville, FL

For each area, search:
- "[City] veteran food pantry"
- "[City] VFW food bank"
- "[City] VA medical center food"
- "[City] American Legion food assistance"

Output format: JSON array per agent (see template below).
Save results to: /home/marci/projects/vibe4vets/backend/data/food/southeast-raw.json
```

### Terminal 3 Command
```
cd /home/marci/projects/vibe4vets && claude

# Then paste:
Using Haiku subagents IN PARALLEL, collect food assistance resources for veterans. Each agent searches 1-2 metro areas.

Agent assignments (spawn ALL in parallel):
1. Los Angeles, CA + San Diego, CA
2. San Francisco Bay Area, CA
3. Phoenix, AZ + Tucson, AZ
4. Seattle, WA + Portland, OR
5. Denver, CO + Las Vegas, NV
6. Minneapolis, MN + Milwaukee, WI
7. St. Louis, MO + Kansas City, MO

For each area, search:
- "[City] veteran food pantry"
- "[City] VFW food bank"
- "[City] VA medical center food"
- "[City] American Legion food assistance"

Output format: JSON array per agent (see template below).
Save results to: /home/marci/projects/vibe4vets/backend/data/food/west-raw.json
```

---

## JSON Resource Template

Each Haiku agent should output resources in this format:

```json
{
  "metro_area": "Phoenix, AZ",
  "searched_at": "2026-01-20",
  "agent_queries": [
    "Phoenix veteran food pantry",
    "Phoenix VFW food bank"
  ],
  "resources": [
    {
      "name": "VFW Post 720 Food Pantry",
      "organization": "VFW Post 720",
      "category": "food",
      "subcategory": "food-pantry",
      "description": "Weekly food distribution for veterans in Phoenix area",
      "phone": "602-555-1234",
      "website": "https://example.org",
      "address": "123 Main St, Phoenix, AZ 85001",
      "city": "Phoenix",
      "state": "AZ",
      "eligibility": {
        "veteran_status_required": true,
        "docs_required": ["DD-214 or VA ID"],
        "income_requirements": null
      },
      "food_details": {
        "distribution_schedule": "Every Tuesday 10am-2pm",
        "serves_dietary": ["vegetarian"],
        "quantity_limit": "One bag per household per week",
        "id_required": true,
        "appointment_required": false
      },
      "intake": {
        "phone": "602-555-1234",
        "hours": "Distribution hours only",
        "notes": "Walk-ins welcome"
      },
      "source_url": "https://where-you-found-this.org",
      "confidence": 0.85,
      "notes": "Verified on organization website"
    }
  ]
}
```

---

## Required Fields Priority

### Critical (must have):
- name
- city + state
- phone OR website
- distribution_schedule (when do they serve?)
- subcategory (food-pantry, meal-program, mobile-distribution, senior-food)

### Important (strongly preferred):
- address
- eligibility.veteran_status_required
- eligibility.docs_required
- food_details.quantity_limit
- intake.notes

### Nice to have:
- serves_dietary
- organization (parent org)
- hours for intake calls

---

## Subcategory Mapping

| Type | Subcategory ID | Examples |
|------|----------------|----------|
| Food banks, pantries | `food-pantry` | VFW food bank, food boxes |
| Hot meals, dining | `meal-program` | Community meals, soup kitchen |
| Mobile/pop-up | `mobile-distribution` | Food trucks, parking lot events |
| Senior-focused | `senior-food` | SNAP help, senior meals |

---

## After Collection

1. **Merge the 3 JSON files** into one consolidated file
2. **Deduplicate** by (name + city + state) tuple
3. **Run the seed script** to import into database

```bash
# Merge step (manual or scripted)
cd backend/data/food
# Combine northeast-raw.json + southeast-raw.json + west-raw.json

# Then create a seed_food_national.py based on seed_dmv_food.py pattern
```

---

## Quality Checklist

Before finalizing each metro area:

- [ ] At least 3-5 resources found per city
- [ ] Hours/schedule included for food distribution
- [ ] Phone or website for each resource
- [ ] Veteran-specific flag set correctly
- [ ] Subcategory assigned correctly
- [ ] No duplicate entries within area

---

## Estimated Coverage

| Terminal | Cities | Expected Resources |
|----------|--------|-------------------|
| T1 Northeast | 14 metros | 50-80 resources |
| T2 Southeast | 14 metros | 50-80 resources |
| T3 West | 14 metros | 50-80 resources |
| **Total** | 42 metros | **150-240 resources** |
