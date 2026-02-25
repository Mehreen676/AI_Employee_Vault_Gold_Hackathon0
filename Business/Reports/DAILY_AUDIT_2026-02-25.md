# Daily Audit Report — 2026-02-25

> Generated: 2026-02-25T08:04:52Z  
> Source: `Logs/*.json`

---

## Summary

| Metric | Value |
|--------|-------|
| Total events | **65** |
| Successes | 64 |
| Failures | 1 |
| Success rate | ✅ **98.5%** |

---

## Activity by Server

| Server | Events |
|--------|--------|
| `mcp_file_ops` | 28 |
| `gold_agent` | 9 |
| `mcp_router` | 7 |
| `mcp_audit_ops` | 6 |
| `mcp_calendar_ops` | 4 |
| `social_mcp_stub` | 4 |
| `odoo_mcp_stub` | 3 |
| `domain_router` | 2 |
| `ceo_briefing` | 2 |

---

## Top Actions

| Action | Count |
|--------|-------|
| `read_task` | 20 |
| `list_tasks` | 6 |
| `get_current_week` | 4 |
| `get_recent_actions` | 4 |
| `loop_complete` | 2 |
| `get_all_domain_tasks` | 2 |
| `agent_start` | 2 |
| `loop_start` | 2 |
| `get_action_summary` | 2 |
| `agent_complete` | 2 |
| `write_task` | 2 |
| `save_briefing` | 2 |
| `openai_config_missing` | 1 |
| `social_post_facebook_dry_run` | 1 |
| `dispatch_ok.odoo_list_invoices` | 1 |

---

## Hourly Distribution

| Hour (UTC) | Events |
|------------|--------|
| 02:00 | 25 █████████████████████████ |
| 04:00 | 26 ██████████████████████████ |
| 05:00 | 14 ██████████████ |

---

## Errors

**1 error(s) detected:**

- `2026-02-25T04:16:17.798324+00:00` | `gold_agent` | `openai_config_missing` | {'reason': 'openai library missing'}

---

*AI Employee Vault — Gold Tier | Daily Audit Runner*
