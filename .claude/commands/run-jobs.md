# Local Job Runner

Run maintenance jobs that are overdue based on `.claude/job-state.json`.

## How It Works

1. Read job state from `.claude/job-state.json`
2. Check which jobs are overdue (current time > last_run + frequency_hours)
3. Run overdue jobs locally
4. Update timestamps after successful completion
5. **Sync changes to Railway** (efficient incremental sync, not full restore)

## Job State Format

```json
{
  "job_name": {
    "last_run": "2026-01-31T04:00:00Z",  // ISO timestamp or null
    "frequency_hours": 168,               // How often to run (168 = weekly)
    "description": "What this job does",
    "disabled": false                     // Optional: skip this job
  }
}
```

## Available Jobs

### crawl4ai_verify (Weekly)
Recheck flagged resources using Crawl4AI browser automation.
- Visits URLs that failed HTTP checks (403s, connection errors)
- Uses Firefox browser to bypass bot detection
- ~45% recovery rate on false positives
- Confirms truly broken URLs for cleanup
- No API costs (pure browser automation)

### crawl4ai_discovery (Bi-weekly)
Discover new veteran resources from configured URLs.
- **Phase 1:** Crawl4AI fetches pages → markdown (handles JS, bot detection)
- **Phase 2:** Parallel haiku subagents extract resources (10 at a time)
- 10-20x faster and cheaper than CLI extraction
- URLs configured in `data/reference/discovery_urls.json`
- State VA pages, 211 directories, nonprofit veteran orgs

### link_checker (Weekly)
Check all resource URLs for broken links and soft 404s.
- Uses `scripts/parallel_link_check.py` for fast async checking (~50 concurrent)
- Detects: real 404s, timeouts, DNS failures, bot-blocked sites
- Updates `link_health_score`, `link_http_status`, `link_flagged_reason`
- Rechecks 403s with browser User-Agent to recover false positives
- Marks resources with broken links as `NEEDS_REVIEW`

### freshness (Daily)
Update trust and freshness scores for all resources.
- Recalculates freshness decay based on last verification
- Updates trust scores: reliability × freshness
- Fast, runs directly without subagents

### etl_refresh (Weekly)
Run the full ETL pipeline for all connectors.
- Fetches latest data from all sources (APIs, files)
- Normalizes, dedupes, enriches, loads
- Updates existing resources, creates new ones
- Note: Some connectors need API keys (VA_API_KEY, etc.)

### embeddings (Weekly) - DISABLED
Generate vector embeddings for resources.
- Currently disabled on Railway (no pgvector)
- Skip this job

## Execution

```bash
# Check what's due and run it
/run-jobs

# Force run a specific job even if not due
/run-jobs link_checker --force

# Dry run - show what would run without executing
/run-jobs --dry-run

# Sync to Railway after running jobs
/run-jobs --sync
```

## Instructions

1. **Start Docker database** (if not running):
   ```bash
   cd /home/marci/projects/vibe4vets && docker-compose up -d db
   ```

2. **Read the job state file**: `.claude/job-state.json`

3. **Parse arguments** (if any):
   - No args: run all overdue jobs
   - Job name: run only that job if overdue
   - `--force`: run even if not overdue
   - `--dry-run`: just report, don't execute
   - `--sync`: sync to Railway after jobs complete

4. **Check each job**:
   ```python
   from datetime import datetime, timedelta, UTC

   now = datetime.now(UTC)
   for job_name, config in jobs.items():
       if config.get("disabled"):
           continue
       last_run = config.get("last_run")
       freq = config.get("frequency_hours", 24)

       if last_run is None:
           is_due = True
       else:
           last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
           is_due = now > last_dt + timedelta(hours=freq)
   ```

5. **For overdue jobs, run them**:

   **link_checker**: Use the fast parallel script
   ```bash
   cd backend && source .venv/bin/activate
   python scripts/parallel_link_check.py
   ```

   Then fix false positives:
   ```python
   # Fix HTTP 429 (rate limited = alive)
   UPDATE resources SET status = 'ACTIVE', link_health_score = 0.8,
          link_flagged_reason = NULL
   WHERE link_flagged_reason = 'HTTP 429';

   # Recheck 403s with browser User-Agent
   python scripts/recheck_403s.py
   ```

   **freshness**: Run directly
   ```bash
   cd backend && source .venv/bin/activate
   PYTHONPATH=. python -c "
   from app.database import engine
   from sqlmodel import Session
   from jobs import FreshnessJob

   with Session(engine) as session:
       result = FreshnessJob().execute(session)
       print(f'Updated {result}')
   "
   ```

   **etl_refresh**: Run directly
   ```bash
   cd backend && source .venv/bin/activate
   PYTHONPATH=. python -c "
   from app.database import engine
   from sqlmodel import Session
   from etl import ETLPipeline
   from jobs.refresh import CONNECTOR_REGISTRY

   connectors = [cls() for cls in CONNECTOR_REGISTRY.values()]
   with Session(engine) as session:
       result = ETLPipeline(session).run(connectors)
       print(f'Created: {result.stats.created}, Updated: {result.stats.updated}')
   "
   ```

   **crawl4ai_verify**: Use browser automation to recheck flagged resources
   ```bash
   cd backend && source .venv/bin/activate
   python scripts/crawl4ai_verify.py --flagged --limit 100
   ```
   - Rechecks resources flagged as 403/broken using Crawl4AI browser automation
   - Recovers ~45% of false positives (bot-blocked sites that actually work)
   - Confirms truly broken URLs for cleanup
   - No API costs (just browser automation)

   **crawl4ai_discovery**: Discover new resources using parallel haiku subagents

   This job uses a two-phase approach for 10-20x faster, cheaper extraction:

   **Phase 1: Crawl URLs (Python script)**
   ```bash
   cd backend && source .venv/bin/activate
   PYTHONPATH=. python -c "
   import json
   from pathlib import Path
   from connectors.crawl4ai_discovery import crawl_urls

   # Load discovery URLs
   config = json.loads(Path('data/reference/discovery_urls.json').read_text())
   all_urls = [url for source in config['sources'] for url in source['urls']]

   # Crawl all URLs, save markdown
   results = crawl_urls(all_urls)
   Path('/tmp/crawl4ai_discovery.json').write_text(json.dumps(results))
   print(f'Crawled {len(results)} pages, saved to /tmp/crawl4ai_discovery.json')
   "
   ```

   **Phase 2: Parallel haiku extraction (in Claude Code session)**

   Launch waves of 10 haiku subagents to extract resources:

   ```
   # Read crawled content
   crawled = json.loads(Path('/tmp/crawl4ai_discovery.json').read_text())

   # For each batch of 10 URLs, launch parallel haiku subagents:
   for url, markdown in batch(crawled.items(), 10):
       Task(
           description=f"Extract resources from {domain}",
           prompt=f"Extract veteran resources from this page. Return JSON array...\n\n{markdown}",
           model="haiku",
           subagent_type="general-purpose"
       )

   # Collect results, parse to ResourceCandidates, load via ETL
   ```

   **Benefits:**
   - 10x faster (parallel vs sequential)
   - 10-20x cheaper (haiku vs Opus/Sonnet)
   - Better quality (stays in session context)

   **Configured in:** `data/reference/discovery_urls.json` (17 URLs across State VA, 211, nonprofits)

6. **Update job state** after successful run:
   ```python
   import json
   from datetime import datetime, UTC

   state = json.load(open(".claude/job-state.json"))
   state[job_name]["last_run"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
   json.dump(state, open(".claude/job-state.json", "w"), indent=2)
   ```

7. **Sync to Railway** (if --sync or prompted):

   **IMPORTANT**: Use incremental sync, NOT pg_dump/pg_restore!

   pg_restore generates massive WAL files and can fill up Railway storage.
   Instead, use the efficient sync script:

   ```bash
   cd backend && source .venv/bin/activate
   python scripts/sync_to_railway.py
   ```

   This syncs only changed fields (link_health, freshness, status) using
   UPDATE statements, which generates minimal WAL.

8. **Report results** to user

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/parallel_link_check.py` | Fast async link checker (50 concurrent) |
| `scripts/recheck_403s.py` | Recheck 403s with browser User-Agent |
| `scripts/sync_to_railway.py` | Efficient incremental sync to Railway |
| `scripts/crawl4ai_verify.py` | Recheck flagged resources using Crawl4AI browser automation |
| `scripts/test_crawl4ai.py` | Test Crawl4AI on individual URLs |
| `scripts/test_tier34_crawl.py` | Test Crawl4AI quality on Tier 3-4 sources |

## Notes

- Jobs update the LOCAL database first
- Always use `sync_to_railway.py` for production sync (not pg_restore!)
- Link checker is network-intensive but free (no API calls)
- Freshness job is fast (~30 seconds for 20k resources)
- ETL refresh may fail for connectors missing API keys locally
- Check Railway volume usage after sync: `railway volume list`

## Troubleshooting

**Railway storage full after sync?**
- Don't use pg_dump/pg_restore - generates huge WAL
- Use `scripts/sync_to_railway.py` instead
- If already full: truncate change_logs, run VACUUM FULL, restart service

**Link checker too slow?**
- Use `scripts/parallel_link_check.py` (async, 50 concurrent)
- NOT the sequential LinkCheckerJob

**403 errors seem wrong?**
- Many sites block bots - run `scripts/recheck_403s.py` with browser User-Agent
- Usually recovers 80%+ of 403s as healthy
