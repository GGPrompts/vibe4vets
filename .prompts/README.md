# Vibe4Vets Resource Discovery Prompts

Prompts for AI-powered resource discovery and validation.

## Directory Structure

```
.prompts/
├── discovery/      # High-volume discovery (Haiku)
├── validation/     # Quality checking (Opus)
└── specialized/    # Specific use cases
```

## Full Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. DISCOVER                                                     │
│    Run discovery prompts (use Haiku subagents)                  │
│    Output: JSON array of resources                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. SAVE                                                         │
│    Save JSON to: backend/data/discoveries/                      │
│    Naming: scan-{category}-{location}-{date}.json               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. IMPORT                                                       │
│    python -m backend.scripts.import_discoveries <file.json>     │
│    → Creates Organizations (if new)                             │
│    → Creates Resources (status: NEEDS_REVIEW)                   │
│    → Creates ReviewState entries                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. REVIEW                                                       │
│    Go to /admin or use API: GET /api/v1/admin/review-queue      │
│    Approve → Resource goes live                                 │
│    Reject → Resource stays inactive                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Run discovery (in Claude Code)
#    Use the prompts, save output to JSON

# 2. Import to review queue
python -m backend.scripts.import_discoveries backend/data/discoveries/my-discoveries.json

# 3. Dry run first to preview
python -m backend.scripts.import_discoveries --dry-run backend/data/discoveries/my-discoveries.json
```

## Output Format

All discovery prompts output JSON matching `ResourceCandidate`:

```json
{
  "name": "Program Name",
  "organization": "Organization Name",
  "category": "housing",
  "subcategory": "emergency_shelter",
  "description": "What this resource provides",
  "phone": "555-123-4567",
  "website": "https://...",
  "address": "123 Main St, City, ST 12345",
  "eligibility": ["veteran", "homeless", "low_income"],
  "coverage_area": "Virginia",
  "source_url": "https://... (where this info was found)",
  "confidence": 0.85
}
```

## Testing Workflow

1. Run prompt manually
2. Review output quality
3. Check links are valid
4. Compare against existing DB for duplicates
5. Iterate on prompt wording
6. Document what works

## Model Recommendations

| Task | Model | Why |
|------|-------|-----|
| Discovery (volume) | Haiku | Fast, cheap, good enough for initial finds |
| Validation | Opus | Thorough, catches errors, better judgment |
| Link checking | Code/script | Don't waste tokens on HTTP requests |
| Deduplication | Sonnet | Good balance of speed and accuracy |

## Cost Optimization: Parallel Haiku Agents

**If you're running these prompts from an Opus session, don't burn expensive tokens on web searches!**

Each discovery prompt includes an "Execution Strategy" section that recommends:

1. **Spawn Haiku subagents in parallel** - Each handles 2-3 search queries
2. **Agents do the bulk work** - Web searches, content extraction, initial filtering
3. **Main session only does final work** - Merging results, deduplication, formatting

This pattern:
- Cuts costs by 60-80% vs running everything in Opus
- Runs faster (parallel searches)
- Uses Opus judgment only where it matters (final quality pass)

### Example Usage in Claude Code

```
User: Run the housing discovery prompt for Richmond, Virginia

Claude: I'll spawn Haiku agents in parallel to search efficiently.

[Task: Haiku agent 1 - search shelters and emergency housing]
[Task: Haiku agent 2 - search SSVF and HUD-VASH providers]
[Task: Haiku agent 3 - search transitional housing and VA programs]

*Agents return results*

Now I'll dedupe and format the combined results...
```
