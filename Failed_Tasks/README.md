# Failed_Tasks/ — Dead-Letter Queue

Tasks land here when the Gold Agent exhausts all retry attempts without
successfully processing them.  This folder acts as a **dead-letter queue**:
nothing is silently discarded — every failure is preserved for review.

---

## Why a task ends up here

| Cause | Details |
|-------|---------|
| OpenAI API unavailable | `OPENAI_API_KEY` missing or network error after 3 retries |
| MCP tool exception | File-ops or dispatch error that persists across retries |
| Max retry loop reached | Task failed `MAX_RETRIES` times inside the Ralph Wiggum loop |

Each failed file contains a frontmatter block with:
- The error reason
- Timestamp of final failure
- Number of attempts made

---

## Retry mechanism

`gold_agent.py` wraps `openai_summarize` (the primary MCP tool call) with
`@with_retry` from `utils/retry.py`:

```python
@with_retry(max_attempts=3, base_delay=2.0, backoff=2.0, max_delay=30.0)
def openai_summarize(prompt: str) -> tuple[str, str]:
    ...
```

Retry schedule per task attempt:
```
Attempt 1 → failure → wait 2s
Attempt 2 → failure → wait 4s
Attempt 3 → failure → task marked failed
```

At the loop level, `MAX_RETRIES` (default 3) controls how many loop
iterations a task gets before being moved here.

---

## Remediation workflow

```bash
# 1. Inspect failed tasks
ls Failed_Tasks/
cat Failed_Tasks/<task-name>.md

# 2a. Fix and requeue
cp Failed_Tasks/<task-name>.md Inbox/<task-name>.md
rm Failed_Tasks/<task-name>.md
python gold_agent.py

# 2b. Discard permanently
rm Failed_Tasks/<task-name>.md
```

---

## Monitoring

The daily audit runner includes the dead-letter count:

```bash
python scripts/run_daily_audit.py
# Evidence/DAILY_AUDIT_<date>.json → stats.failed_tasks_queued
```

The evidence pack also reports the count:

```bash
python tools/generate_evidence_pack.py
# Evidence/LAST_RUN_SUMMARY.json → failed_tasks_queued
```

---

*AI Employee Vault — Gold Tier | Dead-Letter Queue*
