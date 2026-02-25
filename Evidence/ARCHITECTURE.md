# Architecture — AI Employee Vault Gold Tier

Generated: 2026-02-25T09:05:09Z

```
Gmail / Manual Input
        |
     [Inbox/]
        |
   stage_inbox()          ← Gold Agent auto-flushes
        |
  [Needs_Action/]
        |
  ┌─────────────────────────────────────────────────────────┐
  │              gold_agent.py                              │
  │              Ralph Wiggum Loop                          │
  │                                                         │
  │  Stage 0: hitl.process_approvals()  ← Approved/        │
  │           hitl.process_rejections() ← Rejected/         │
  │                                                         │
  │  Stage 1: stage_inbox() flush                           │
  │                                                         │
  │  Stage 2: per-task pipeline                             │
  │    ┌─── mcp.router.dispatch_action()                    │
  │    │      email_mcp_stub    (email_send, notify)        │
  │    │      browser_mcp_stub  (publish, payment, deploy)  │
  │    │      calendar_mcp_stub (create_calendar_event)     │
  │    │      gmail_mcp_server  (draft/send/search email)   │
  │    │      playwright_server (open_url, screenshot)      │
  │    │      odoo_mcp_stub     (invoices, partners)        │
  │    │      social_mcp_stub   (FB/IG/TW — safety gated)  │
  │    ├─── domain_router.py   (Personal/Business)          │
  │    ├─── audit_logger.py    (JSON → /Logs + Neon)        │
  │    └─── hitl.py            (HITL detection)             │
  │                                                         │
  │    classify → HITL-check → summarize → route            │
  └─────────────────────────────────────────────────────────┘
        |            |              |
   sensitive?    safe tasks     approved?
        |            |              |
  [Pending_Approval/] |        [Approved/] ──→ resume
  (held + request)   |        [Rejected/] ──→ archive
                     |
              [Personal/] [Business/]
                     |
                 [Done/]
                     |
             ceo_briefing.py
                     |
               [Briefings/]
```

---

## MCP Server Stack

| Server | File | Action Types |
|--------|------|-------------|
| email_mcp_stub | `mcp/email_mcp_stub.py` | `email_send`, `notify_external` |
| browser_mcp_stub | `mcp/browser_mcp_stub.py` | `publish`, `payment`, `deploy`, `delete`, `authorize`, `browser_action` |
| calendar_mcp_stub | `mcp/calendar_mcp_stub.py` | `create_calendar_event` |
| gmail_mcp_server | `mcp/gmail_mcp_server.py` | `draft_email`, `send_email`, `search_email` |
| playwright_browser_server | `mcp/playwright_browser_server.py` | `open_url`, `click_selector`, `type_text`, `screenshot` |
| odoo_mcp_stub | `mcp/odoo_mcp_stub.py` | `odoo_create_partner`, `odoo_create_invoice`, `odoo_list_invoices` |
| **social_mcp_stub** | `mcp/social_mcp_stub.py` | `social_post_facebook`, `social_post_instagram`, `social_post_twitter`, `social_get_analytics` |

All servers default to `DRY_RUN=true`.  The social stub has an additional
permanent safety gate that blocks live posting regardless of `MCP_DRY_RUN`.

---

*AI Employee Vault — Gold Tier*
