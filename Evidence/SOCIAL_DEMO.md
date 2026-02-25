# Social MCP Stub — Dry-Run Proof

Generated: 2026-02-25T09:05:09Z
Source:    mcp/social_mcp_stub.py
Server:    social_mcp_stub
DRY_RUN:   true (default)

## Safety Model

The Social MCP stub has a permanent **social_safety_gate** that blocks live
posting regardless of the `MCP_DRY_RUN` setting.  This ensures that no real
posts are ever sent to Facebook, Instagram, or Twitter/X from a
demo / hackathon environment.

| DRY_RUN | Result |
|---------|--------|
| `true` (default) | `dry_run_logged` — full intent logged, no real call |
| `false` | `blocked_live_mode` — safety gate fires, no real call |

To enable live posting, remove the `social_safety_gate` block in
`mcp/social_mcp_stub.py` and configure real credentials.
See `docs/SOCIAL_SETUP.md`.

---

## social_post_facebook

Console output:
  [social_mcp_stub] DRY RUN: Would post to Facebook Page
  [social_mcp_stub]   Page:    @AIEmployeeVault
  [social_mcp_stub]   Content: Exciting news! AI Employee Vault Gold is now live. #AIEmployee #Automation...
  [social_mcp_stub]   Sim ID:  fb_29670191165_simulated
  [social_mcp_stub]   -> social_safety_gate: live posting permanently blocked.

Return value:
{
  "server": "social_mcp_stub",
  "action_type": "social_post_facebook",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would post to Facebook Page '@AIEmployeeVault' \u2014 task: 'facebook_post_demo.md'",
  "simulated_post_id": "fb_29670191165_simulated",
  "timestamp": "2026-02-25T09:05:09.233780+00:00",
  "intent": {
    "platform": "facebook",
    "page": "@AIEmployeeVault",
    "content_preview": "Exciting news! AI Employee Vault Gold is now live. #AIEmployee #Automation",
    "task_file": "facebook_post_demo.md"
  }
}

---

## social_post_instagram

Console output:
  [social_mcp_stub] DRY RUN: Would post to Instagram
  [social_mcp_stub]   Account: @AIEmployeeVault
  [social_mcp_stub]   Caption: Behind the scenes at AI Employee Vault. #AI #Productivity...
  [social_mcp_stub]   Sim ID:  ig_71732280908_simulated
  [social_mcp_stub]   -> social_safety_gate: live posting permanently blocked.

Return value:
{
  "server": "social_mcp_stub",
  "action_type": "social_post_instagram",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would post to Instagram account '@AIEmployeeVault' \u2014 task: 'instagram_post_demo.md'",
  "simulated_post_id": "ig_71732280908_simulated",
  "timestamp": "2026-02-25T09:05:09.236632+00:00",
  "intent": {
    "platform": "instagram",
    "account": "@AIEmployeeVault",
    "caption_preview": "Behind the scenes at AI Employee Vault. #AI #Productivity",
    "task_file": "instagram_post_demo.md"
  }
}

---

## social_post_twitter

Console output:
  [social_mcp_stub] DRY RUN: Would post to Twitter/X
  [social_mcp_stub]   Account: @AIEmployeeVault
  [social_mcp_stub]   Text:    Exciting news from our Q1 launch! #GoldTier #AI...
  [social_mcp_stub]   Sim ID:  tw_79504853697_simulated
  [social_mcp_stub]   -> social_safety_gate: live posting permanently blocked.

Return value:
{
  "server": "social_mcp_stub",
  "action_type": "social_post_twitter",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would tweet from '@AIEmployeeVault' \u2014 task: 'twitter_post_demo.md'",
  "simulated_post_id": "tw_79504853697_simulated",
  "timestamp": "2026-02-25T09:05:09.238644+00:00",
  "intent": {
    "platform": "twitter",
    "account": "@AIEmployeeVault",
    "text_preview": "Exciting news from our Q1 launch! #GoldTier #AI",
    "char_count": 47,
    "task_file": "twitter_post_demo.md"
  }
}

---

## social_get_analytics (simulated cloud data)

Console output:
  [social_mcp_stub] SIMULATED analytics: platform='all', period='30d'
  [social_mcp_stub]   facebook: followers=4820, reach_30d=12400
  [social_mcp_stub]   instagram: followers=7310, reach_30d=18750
  [social_mcp_stub]   twitter: followers=2140, reach_30d=8300

Return value:
{
  "server": "social_mcp_stub",
  "action_type": "social_get_analytics",
  "dry_run": true,
  "result": "simulated_analytics",
  "message": "[SIMULATED] Analytics for platform='all', period='30d'",
  "analytics": {
    "facebook": {
      "followers": 4820,
      "reach_30d": 12400,
      "impressions_30d": 38900,
      "engagements_30d": 1230,
      "top_post_reach": 5600
    },
    "instagram": {
      "followers": 7310,
      "reach_30d": 18750,
      "impressions_30d": 52100,
      "engagements_30d": 2890,
      "top_post_reach": 9200
    },
    "twitter": {
      "followers": 2140,
      "reach_30d": 8300,
      "impressions_30d": 24600,
      "engagements_30d": 670,
      "top_post_reach": 3400
    }
  },
  "period": "30d",
  "timestamp": "2026-02-25T09:05:09.241172+00:00",
  "note": "All metrics are simulated cloud data \u2014 no real API call made."
}

---

## End-to-End Demo Flow

```bash
# Step 1 — load a social demo task into Inbox
python tools/load_demo_task.py facebook_post_demo

# Step 2 — run Gold Agent (detects publish keyword → HITL)
python gold_agent.py

# Step 3 — approve the HITL action
python approve.py --all

# Step 4 — run agent again (resumes + fires MCP tool)
python gold_agent.py

# Step 5 — check audit log
ls Logs/   # look for social_mcp_stub_social_post_facebook_dry_run_*.json
```

No real post is ever sent.  All actions are logged to `Logs/` as JSON.

---

## Registered Social Action Types

| Action Type | Server | Result (DRY_RUN=true) | Result (DRY_RUN=false) |
|---|---|---|---|
| `social_post_facebook` | `social_mcp_stub` | `dry_run_logged` | `blocked_live_mode` |
| `social_post_instagram` | `social_mcp_stub` | `dry_run_logged` | `blocked_live_mode` |
| `social_post_twitter` | `social_mcp_stub` | `dry_run_logged` | `blocked_live_mode` |
| `social_get_analytics` | `social_mcp_stub` | `simulated_analytics` | `simulated_analytics` |

---

*AI Employee Vault — Gold Tier | Social MCP Demo*
