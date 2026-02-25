---
type: demo_task
domain: business
action: publish
mcp_tool: publish
mcp_server: browser_mcp_stub
platform: facebook
priority: medium
status: pending
created: 2026-02-25T09:00:00Z
tags:
  - social_media
  - demo
  - publish
---

# Demo Task — Publish Facebook Post

**Action requiring MCP tool:** `publish` (via `browser_mcp_stub`)
**Domain:** Business
**Platform:** Facebook

## Task

Post a product announcement to the company Facebook page.

**Content:**
> "Exciting news! AI Employee Vault Gold is now live — your autonomous AI
> employee that reads emails, schedules meetings, and executes tasks without
> lifting a finger. Try it today. #AIEmployee #Automation #ProductLaunch"

**Target page:** @AIEmployeeVault
**Schedule:** Immediately on approval

## Why This Needs Approval

This task triggers the `publish` MCP tool in `browser_mcp_stub`. Publishing
content to a public social platform is a high-visibility action that requires
human sign-off before execution.

**Sensitive keywords detected:** `post to`, `publish`, `broadcast`

## How the Agent Will Handle It

1. Gold Agent detects `publish` keyword → classifies as HITL-sensitive.
2. Task is moved to `Pending_Approval/` and an approval request is written.
3. Human reviews and runs: `python approve.py hitl_<timestamp>_facebook_post_demo.md`
4. On approval, Gold Agent calls `browser_mcp_stub.handle_publish(payload)`.
5. In **DRY_RUN=true** (default): action is logged to `Logs/` — no real post sent.
6. In **DRY_RUN=false**: real Facebook Graph API call is executed (requires credentials).

## Expected MCP Tool Call

```python
from mcp.registry import get_handler

handler = get_handler("publish")
result = handler(
    payload={
        "task_file": "facebook_post_demo.md",
        "domain": "business",
        "platform": "facebook",
        "content": "Exciting news! AI Employee Vault Gold is now live...",
        "page": "@AIEmployeeVault",
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
