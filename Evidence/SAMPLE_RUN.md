# Sample Run — Annotated Console Output

Generated: 2026-02-25T09:05:09Z

---

## Social Media Demo Run (facebook_post_demo.md)

```
$ python tools/load_demo_task.py facebook_post_demo
Loaded demo scenario into Inbox/
  Source:      Demo_Scenarios/facebook_post_demo.md
  Destination: Inbox/demo_20260225T090000_facebook_post_demo.md

$ python gold_agent.py
[Gold Agent] Run ID: 179
[Gold Agent] Stage 0: processing approvals...
[Gold Agent] Stage 1: flushing inbox...
[Gold Agent] Moved: demo_20260225T090000_facebook_post_demo.md → Needs_Action/
[Gold Agent] Stage 2: processing tasks...
[Gold Agent] Task: facebook_post_demo.md
[Gold Agent]   Domain: business
[Gold Agent]   HITL: sensitive keyword 'publish' detected
[Gold Agent]   → Task held in Pending_Approval/
[hitl] Approval request written: hitl_20260225T090001_facebook_post_demo.md

$ python approve.py --all
Approved: hitl_20260225T090001_facebook_post_demo.md
Moved to Approved/

$ python gold_agent.py
[Gold Agent] Run ID: 180
[Gold Agent] Stage 0: processing approvals...
[Gold Agent] Resuming approved task: facebook_post_demo.md
[Gold Agent]   action_type: publish
[mcp_router] dispatch_action: publish
  [browser_mcp_stub] DRY RUN: Content publication (post / broadcast / announce)
  [browser_mcp_stub]   action_type: publish
  [browser_mcp_stub]   task_file:   facebook_post_demo.md
  [browser_mcp_stub]   domain:      business
  [browser_mcp_stub]   -> Set env MCP_DRY_RUN=false to enable real execution.
[Gold Agent]   MCP result: dry_run_logged
[Gold Agent]   Task moved to Done/

$ ls Logs/ | grep publish
20260225_090002_abc123def456.json

$ cat Logs/20260225_090002_abc123def456.json
{
  "server": "browser_mcp_stub",
  "action": "publish_dry_run",
  "timestamp": "2026-02-25T09:00:02Z",
  "data": {
    "action_type": "publish",
    "task_file": "facebook_post_demo.md",
    "domain": "business",
    "dry_run": true
  },
  "success": true
}
```

---

## Social MCP Direct Demo

```
$ python -c "
from mcp.router import dispatch_action
result = dispatch_action('social_post_twitter', {
    'text': 'Exciting news from our Q1 launch! #GoldTier #AI',
    'task_file': 'twitter_demo.md',
})
print(result['result'])
"
  [social_mcp_stub] DRY RUN: Would post to Twitter/X
  [social_mcp_stub]   Account: @AIEmployeeVault
  [social_mcp_stub]   Text:    Exciting news from our Q1 launch! #GoldTier #AI...
  [social_mcp_stub]   Sim ID:  tw_52847291034_simulated
  [social_mcp_stub]   -> social_safety_gate: live posting permanently blocked.
dry_run_logged
```

---

*AI Employee Vault — Gold Tier*
