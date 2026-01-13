# Agent Instructions

This project uses **bd** (beads) for issue tracking.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status=in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Session Completion

**See `.beads/PRIME.md` for the full completion protocol.**

Quick reference:
```bash
# Standard completion (with code review)
/conductor:bdw-verify-build
/conductor:bdw-code-review
/conductor:bdw-commit-changes
/conductor:bdw-close-issue <id>
bd sync && git push

# Quick completion (trivial changes)
/conductor:bdw-verify-build
/conductor:bdw-commit-changes
/conductor:bdw-close-issue <id>
bd sync && git push
```

**CRITICAL:** Work is NOT complete until `git push` succeeds.
