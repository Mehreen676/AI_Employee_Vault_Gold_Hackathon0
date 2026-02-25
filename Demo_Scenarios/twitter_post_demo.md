---
type: demo_task
domain: business
action: publish
mcp_tool: publish
mcp_server: browser_mcp_stub
platform: twitter
priority: high
status: pending
created: 2026-02-25T09:10:00Z
tags:
  - social_media
  - demo
  - publish
---

# Demo Task — Publish Twitter / X Post

**Action requiring MCP tool:** `publish` (via `browser_mcp_stub`)
**Domain:** Business
**Platform:** Twitter / X

## Task

Post a launch announcement tweet from the official company account.

**Tweet content (≤280 chars):**
> "AI Employee Vault Gold is live. Your inbox → autonomous AI agent → CEO
> briefing. No prompts needed. Ship it. #AI #Automation #GoldTier
> aiemployeevault.io"

**Target account:** @AIEmployeeVault
**Schedule:** Immediately on approval
**Thread follow-up:** Optional (see payload `thread` key below)

## Why This Needs Approval

This task triggers the `publish` MCP tool in `browser_mcp_stub`. Tweeting from
a verified business account is a public broadcast — classified as sensitive and
subject to HITL approval before execution.

**Sensitive keywords detected:** `publish`, `broadcast`, `announcement`

## How the Agent Will Handle It

1. Gold Agent detects `publish` / `announcement` keyword → HITL-sensitive.
2. Task moved to `Pending_Approval/`; approval file written.
3. Human approves: `python approve.py hitl_<timestamp>_twitter_post_demo.md`
4. Gold Agent calls `browser_mcp_stub.handle_publish(payload)`.
5. **DRY_RUN=true** (default): intent logged to `Logs/` — no tweet sent.
6. **DRY_RUN=false**: real Twitter API v2 call made (requires `TWITTER_BEARER_TOKEN`).

## Expected MCP Tool Call

```python
from mcp.registry import get_handler

handler = get_handler("publish")
result = handler(
    payload={
        "task_file": "twitter_post_demo.md",
        "domain": "business",
        "platform": "twitter",
        "text": "AI Employee Vault Gold is live...",
        "account": "@AIEmployeeVault",
        "thread": [],   # add follow-up tweet texts here for a thread
    },
    dry_run=True,   # set False to go live
)
print(result)
# -> {"server": "browser_mcp_stub", "action_type": "publish", "result": "dry_run_logged", ...}
```

## Audit Log Location

Every execution (dry run or real) writes a JSON entry to:
```
Logs/browser_mcp_stub_publish_dry_run_<timestamp>.json
```

---
*Demo scenario for AI Employee Vault — Gold Tier | MCP tool: `publish`*
