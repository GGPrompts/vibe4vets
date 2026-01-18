# Documentation Standards

Documentation is **LLM-optimized** - meant for AI agents to consume, not humans to read. Keep it minimal, current, and machine-parseable.

## Document Map

| File | Audience | Purpose |
|------|----------|---------|
| `README.md` | **Humans** | Only human-facing doc. Project overview, setup, contribution guide. |
| `CLAUDE.md` | **LLMs** | Project context, architecture, commands, workflows. Agents read this first. |
| `AGENTS.md` | **LLMs** | Same as CLAUDE.md (for non-Claude agents like Codex, Cursor). Keep in sync. |
| `CHANGELOG.md` | **Both** | What changed and when. LLMs use for context, humans for releases. |
| `docs/*.md` | **LLMs** | Specs, API docs, architecture details. Reference material for agents. |

## Update Triggers

### CLAUDE.md / AGENTS.md

Update when:
- Adding new API endpoints
- Changing database schema
- Adding new commands or workflows
- Changing project structure
- Modifying key files list

These files must stay in sync. After editing CLAUDE.md:
```bash
cp CLAUDE.md AGENTS.md
# Update title line: "# AGENTS.md - Vibe4Vets"
```

### CHANGELOG.md

Update when:
- Completing a feature (add to `[Unreleased]`)
- Fixing a bug
- Making breaking changes

**Line limit: 200 lines**. When exceeded, move old released versions to `docs/changelog-archive.md`.

Format:
```markdown
## [Unreleased]

### Added
- **Feature name** - Brief description (ISSUE-ID)

### Fixed
- **Bug name** - What was fixed (ISSUE-ID)

### Changed
- **Breaking change** - What changed and migration path
```

### docs/*.md

Create for:
- **Specs before implementation** - Like `eligibility-wizard-spec.md`
- **Complex API documentation** - `docs/API.md` for detailed endpoint docs
- **Architecture decisions** - When "why" matters for future work

## What NOT to Document

- **No inline code comments** explaining obvious code
- **No README files** in subdirectories (use CLAUDE.md key files table instead)
- **No auto-generated docs** committed to repo (OpenAPI/Swagger served live is fine)
- **No meeting notes or design discussions** (use beads issues for context)
- **No duplicate information** - reference other docs, don't copy

## Automation

Use `/update-docs` after completing beads issues to:
1. Check if completed work requires doc updates
2. Update CHANGELOG.md with new entries
3. Update CLAUDE.md/AGENTS.md if architecture changed
4. Sync AGENTS.md with CLAUDE.md

## Examples

### Good CHANGELOG Entry
```markdown
- **AI resource discovery pipeline** - Prompts and import script for discovering veteran resources via web search (V4V-625)
```

### Bad CHANGELOG Entry
```markdown
- Added new feature for finding resources using AI that searches the web and imports them into the database with a review queue
```

### Good CLAUDE.md Key Files Entry
```markdown
| `backend/scripts/import_discoveries.py` | Import AI-discovered resources to review queue |
```

### Bad: Creating a Separate README
```
backend/scripts/README.md  ← Don't do this
```
Instead, add to CLAUDE.md key files table.
