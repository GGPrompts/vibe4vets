# Discover Veteran Discounts

You are researching veteran discounts at businesses. Focus on reliable, ongoing discounts (not just Veterans Day specials).

## Execution Strategy

**Use Haiku subagents in parallel to minimize token cost:**

1. Spawn 3-4 Haiku Explore agents simultaneously, each searching different business categories
2. Each agent handles 2-3 search queries and extracts results
3. Collect and merge results from all agents
4. Only use the main session for final deduplication and verification

Example for national scope:
```
Agent 1: "veteran discount restaurants", "veteran discount fast food"
Agent 2: "veteran discount home improvement stores", "veteran discount retail"
Agent 3: "veteran discount hotels", "veteran discount car rental"
Agent 4: "veteran discount phone plans", "veteran discount insurance"
```

## Scope
{{SCOPE}} - either "national" for nationwide chains, or a specific area for local businesses

## What to Find

### National Chains (if scope is national)
1. **Restaurants** - Ongoing veteran discounts (not just Nov 11)
2. **Retail stores** - Home improvement, clothing, outdoor gear
3. **Auto services** - Oil changes, repairs, car washes
4. **Hotels** - Veteran rates
5. **Entertainment** - Theme parks, movies, museums
6. **Services** - Phone plans, internet, insurance

### Local Businesses (if scope is specific area)
1. **Local restaurants** with veteran discounts
2. **Local services** - barbers, mechanics, etc.
3. **Regional chains** in the area

## Search Strategy

For national:
- "veteran discount [company name]"
- "military discount retail stores 2024"
- "restaurants with veteran discounts"
- "[company] veteran discount policy"

For local:
- "[AREA] veteran discount restaurants"
- "[AREA] businesses veteran discount"
- "[AREA] military friendly businesses"

## Required Information

For each discount, extract:
- **Business name**: Company/restaurant name
- **Discount**: Percentage or dollar amount
- **Requirements**: What ID is needed (VA card, DD-214, etc.)
- **Restrictions**: Dine-in only, certain days, etc.
- **Verification source**: Official company page confirming discount

## Output Format

Return a JSON array of discounts:

```json
[
  {
    "business_name": "Example Store",
    "business_type": "retail|restaurant|service|entertainment|hotel",
    "discount_type": "percentage|dollar_amount|free_item|special_rate",
    "discount_value": "10%",
    "discount_description": "10% off all purchases",
    "requirements": ["veteran_id", "active_duty_id"],
    "restrictions": "Not valid on sale items",
    "days_available": "everyday" or "Tuesdays only",
    "locations": "nationwide" or "specific locations",
    "verification_url": "https://company.com/military-discount",
    "verified_date": "2024-01",
    "confidence": 0.9,
    "notes": "Must mention discount before checkout"
  }
]
```

## Quality Standards

- **Only verified discounts** - Must have official source
- **Current discounts** - Not expired promotions
- **Clear requirements** - What ID/proof is needed
- **Practical info** - How to actually get the discount

## Do NOT Include

- Veterans Day one-day specials (unless specifically requested)
- Discounts that require military email (.mil)
- Discounts only for active duty (unless noted)
- Rumored or unverified discounts
- Discounts that have been discontinued
