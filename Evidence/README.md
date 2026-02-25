# Evidence Pack — AI Employee Vault Gold Tier

Generated: 2026-02-25T09:05:09Z

This folder contains judge-ready proof for every Gold Tier claim.

---

## Quick Verification

```bash
# Verify MCP registry (live)
python -c "from mcp.registry import list_registered; r=list_registered(); print(len(r), 'tools')"
# Expected: 24 tools

# Run social demo (dry-run, safe)
python tools/load_demo_task.py facebook_post_demo
python gold_agent.py
python approve.py --all
python gold_agent.py
ls Logs/  # JSON audit log written
```

---

## Files in This Folder

| File | What It Proves |
|------|----------------|
| `README.md` | This index |
| `PROOF_CHECKLIST.md` | All claims mapped to source files + Social MCP section |
| `REGISTERED_MCP_TOOLS.json` | Live dump — 24 tools from `mcp.registry.list_registered()` |
| `LAST_RUN_SUMMARY.json` | Latest run: run_id=181, db_events=24 |
| `ODOO_DEMO.md` | Dry-run proof for 3 Odoo MCP tools |
| `SOCIAL_DEMO.md` | Dry-run proof for 4 Social MCP tools (safety gate demo) |

---

## Dead-Letter Queue

| `Failed_Tasks/` | Dead-letter queue empty — all tasks processed successfully |

Failed tasks are preserved in `Failed_Tasks/` for review and reprocessing.
The agent uses `@with_retry` (exponential backoff, 3 attempts) before a task
is declared failed and moved to the dead-letter queue.

---

## Social MCP Safety Model

The `social_mcp_stub` has a **permanent safety gate** that blocks live posting
even when `MCP_DRY_RUN=false`.  No real Facebook / Instagram / Twitter post
is ever made.  All actions are logged as JSON to `Logs/`.

---

*AI Employee Vault — Gold Tier | Hackathon 0*
