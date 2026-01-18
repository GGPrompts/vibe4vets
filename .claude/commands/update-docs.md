---
description: Update documentation based on recently completed beads issues
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# /update-docs - Documentation Update Assistant

Update project documentation based on recently completed beads issues.

## Workflow

### Step 1: Get Recently Closed Issues

```bash
bd list --status closed --json | head -20
```

Look for issues closed in the last session or since the last doc update.

### Step 2: Read Documentation Standards

Read `docs/documentation-standards.md` to understand the update rules.

### Step 3: Analyze What Needs Updating

For each recently completed issue, determine:

1. **CHANGELOG.md** - Does this need a changelog entry?
   - New features → Yes, under `### Added`
   - Bug fixes → Yes, under `### Fixed`
   - Breaking changes → Yes, under `### Changed`
   - Refactors with no user-visible change → No

2. **CLAUDE.md / AGENTS.md** - Does this change project structure?
   - New API endpoints → Update API Structure table
   - New key files → Update Key Files table
   - New workflows → Add section or update existing
   - Schema changes → Update Core Data Model

3. **docs/*.md** - Is detailed documentation needed?
   - Complex features → Maybe create a spec doc
   - API changes → Consider docs/API.md

### Step 4: Update CHANGELOG.md

Add entries to the `[Unreleased]` section following this format:

```markdown
### Added
- **Feature name** - Brief description (ISSUE-ID)

### Fixed
- **Bug description** - What was fixed (ISSUE-ID)

### Changed
- **Breaking change** - What changed (ISSUE-ID)
```

Rules:
- Keep entries concise (one line each)
- Include the beads issue ID
- Group by type (Added/Fixed/Changed)
- Check line count - if over 200, suggest archiving old entries

### Step 5: Update CLAUDE.md if Needed

If architecture changed:
- Add new endpoints to API Structure table
- Add new files to Key Files table
- Update directory layout if structure changed

### Step 6: Sync AGENTS.md

After updating CLAUDE.md, sync to AGENTS.md:
- Copy the changed sections
- Keep the title as "# AGENTS.md - Vibe4Vets"

### Step 7: Report Changes

Summarize what was updated:

```
## Documentation Updated

### CHANGELOG.md
- Added: Feature X (V4V-abc)
- Fixed: Bug Y (V4V-def)

### CLAUDE.md / AGENTS.md
- Updated Key Files table with new script
- No other changes needed

### Recommendations
- Consider creating docs/API.md for new endpoints
- CHANGELOG.md is at 180 lines (under 200 limit)
```

## Usage Examples

**After closing an issue:**
```
User: /update-docs
Assistant: [Checks recent issues, updates CHANGELOG, syncs docs]
```

**With specific issue:**
```
User: /update-docs V4V-625
Assistant: [Updates docs based on that specific issue]
```

## Notes

- Don't create unnecessary documentation
- Keep entries brief - one line per change
- Always include issue IDs for traceability
- CHANGELOG is for users; CLAUDE.md is for agents
