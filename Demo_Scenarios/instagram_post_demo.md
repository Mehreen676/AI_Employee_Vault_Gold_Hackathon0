---
type: demo_task
domain: business
action: publish
mcp_tool: publish
mcp_server: browser_mcp_stub
platform: instagram
priority: medium
status: pending
created: 2026-02-25T09:05:00Z
tags:
  - social_media
  - demo
  - publish
---

# Demo Task — Publish Instagram Post

**Action requiring MCP tool:** `publish` (via `browser_mcp_stub`)
**Domain:** Business
**Platform:** Instagram

## Task

Publish a visual product highlight post to the company Instagram account.

**Caption:**
> "Meet your new AI team member 🤖 AI Employee Vault Gold autonomously
> processes your inbox, drafts replies, books meetings, and briefs the CEO —
> all without being asked. Link in bio. #AIEmployee #GoldTier #Automation
> #ProductivityHack"

**Image asset:** `assets/gold_tier_promo.png` (must be provided before real run)
**Target account:** @ai_employee_vault
**Schedule:** Immediately on approval

## Why This Needs Approval

This task triggers the `publish` MCP tool in `browser_mcp_stub`. Posting to
Instagram is a public, irreversible action classified as a sensitive publish
event requiring human sign-off.

**Sensitive keywords detected:** `publish`, `post to`, `broadcast`

## How the Agent Will Handle It

1. Gold Agent detects `publish` keyword → classifies as HITL-sensitive.
2. Task held in `Pending_Approval/`; approval request written alongside it.
3. Human approves: `python approve.py hitl_<timestamp>_instagram_post_demo.md`
4. Gold Agent calls `browser_mcp_stub.handle_publish(payload)`.
5. **DRY_RUN=true** (default): full intent logged to `Logs/` — no real post.
6. **DRY_RUN=false**: real Instagram Graph API call executed (requires `IG_ACCESS_TOKEN`).

## Expected MCP Tool Call

```python
from mcp.registry import get_handler

handler = get_handler("publish")
result = handler(
    payload={
        "task_file": "instagram_post_demo.md",
        "domain": "business",
        "platform": "instagram",
        "caption": "Meet your new AI team member...",
        "image_asset": "assets/gold_tier_promo.png",
        "account": "@ai_employee_vault",
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
