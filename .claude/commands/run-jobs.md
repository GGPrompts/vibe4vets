# Local Job Runner

Run maintenance jobs that are overdue based on `.claude/job-state.json`.

## How It Works

1. Read job state from `.claude/job-state.json`
2. Check which jobs are overdue (current time > last_run + frequency_hours)
3. Run overdue jobs using subagents
4. Update timestamps after successful completion

## Job State Format

```json
{
  "job_name": {
    "last_run": "2026-01-31T04:00:00Z",  // ISO timestamp or null
    "frequency_hours": 168,               // How often to run (168 = weekly)
    "description": "What this job does",
    "batch_size": 500,                    // Optional: for parallelized jobs
    "parallel": 10                        // Optional: subagent count
  }
}
```

## Available Jobs

### link_checker (Weekly)
Check all resource URLs for broken links and soft 404s.
- Fetches each URL and analyzes content
- Detects: real 404s, soft 404s, parked domains, stale content
- Updates `link_health_score` and flags for review
- Uses parallel haiku subagents with WebFetch

### freshness (Daily)
Update trust and freshness scores for all resources.
- Recalculates freshness decay based on last verification
- Updates trust scores: reliability × freshness
- Fast, runs directly without subagents

### etl_refresh (Weekly)
Run the full ETL pipeline for all connectors.
- Fetches latest data from all sources
- Normalizes, dedupes, enriches, loads
- Updates existing resources, creates new ones

### embeddings (Weekly)
Generate vector embeddings for resources missing them.
- Finds resources without embeddings
- Generates using Claude
- Enables semantic search

## Execution

```bash
# Check what's due and run it
/run-jobs

# Force run a specific job even if not due
/run-jobs link_checker --force

# Dry run - show what would run without executing
/run-jobs --dry-run
```

## Instructions

1. **Read the job state file**: `.claude/job-state.json`

2. **Parse arguments** (if any):
   - No args: run all overdue jobs
   - Job name: run only that job if overdue
   - `--force`: run even if not overdue
   - `--dry-run`: just report, don't execute

3. **Check each job**:
   ```python
   from datetime import datetime, timedelta

   now = datetime.utcnow()
   for job_name, config in jobs.items():
       last_run = config.get("last_run")
       freq = config.get("frequency_hours", 24)

       if last_run is None:
           is_due = True
       else:
           last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
           is_due = now > last_dt + timedelta(hours=freq)
   ```

4. **For overdue jobs, run them**:

   **link_checker**: Use parallel haiku subagents
   ```
   - Query: SELECT id, title, website FROM resources WHERE website IS NOT NULL
   - Split into batches of 500
   - Launch N parallel haiku agents, each batch:
     - For each URL: WebFetch → analyze for 404/soft-404
     - Return list of {resource_id, status, score, reason}
   - Aggregate results
   - Update database: link_health_score, link_checked_at, link_flagged_reason
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

   **embeddings**: Run directly
   ```bash
   cd backend && source .venv/bin/activate
   PYTHONPATH=. python -c "
   from app.database import engine
   from sqlmodel import Session
   from jobs import EmbeddingsJob

   with Session(engine) as session:
       result = EmbeddingsJob().execute(session)
       print(f'Generated {result}')
   "
   ```

5. **Update job state** after successful run:
   ```python
   import json
   from datetime import datetime

   state = json.load(open(".claude/job-state.json"))
   state[job_name]["last_run"] = datetime.utcnow().isoformat() + "Z"
   json.dump(state, open(".claude/job-state.json", "w"), indent=2)
   ```

6. **Report results** to user

## Link Checker Subagent Prompt

When spawning link checker subagents, use this prompt:

```
Check these resource URLs for broken links and soft 404s.

Resources to check:
{batch_json}

For each resource:
1. Use WebFetch to load the URL
2. Check if it's a real 404 (status code), soft 404 (page says "not found"),
   parked domain, or stale/abandoned content
3. Return a score 0.0-1.0:
   - 1.0: Healthy, active resource page
   - 0.7-0.9: Page exists but may be outdated
   - 0.3-0.6: Questionable - may need review
   - 0.0-0.2: Broken, 404, parked, or completely wrong content

Return JSON array:
[
  {"id": "uuid", "score": 0.95, "status": "healthy"},
  {"id": "uuid", "score": 0.1, "status": "broken", "reason": "404 Not Found"},
  {"id": "uuid", "score": 0.3, "status": "flagged", "reason": "Page says 'no longer available'"}
]
```

## Notes

- Jobs update the LOCAL database - sync to production separately if needed
- Link checker is the most expensive (network + AI) - runs weekly by default
- Freshness is cheap - runs daily
- Use `--force` after deploying new connectors to refresh immediately
