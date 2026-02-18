# AI Employee Vault — Gold Tier

> Hackathon 0 | Personal AI Employee with full cross-domain autonomy

## What Is This?

A fully autonomous AI Employee that processes tasks from email or manual input, classifies them across **Personal** and **Business** domains, summarizes them with OpenAI, and loops until everything is done — then generates a **Weekly CEO Briefing**.

Built on 4 MCP servers, comprehensive JSON audit logging, error recovery with graceful degradation, and a **Ralph Wiggum autonomous loop** ("I'm in danger!") that keeps running until all tasks reach `Done/`.

---

## Architecture

```
Gmail / Manual Input
        |
     [Inbox/]
        |
   stage_inbox()          ← Gold Agent auto-flushes
        |
  [Needs_Action/]
        |
  ┌─────────────────────────────────────────────┐
  │         gold_agent.py                       │
  │         Ralph Wiggum Loop                   │
  │                                             │
  │  ┌─── mcp_file_ops.py    (CRUD files)       │
  │  ├─── mcp_email_ops.py   (classify email)   │
  │  ├─── mcp_calendar_ops.py(schedule/priority) │
  │  ├─── mcp_audit_ops.py   (audit queries)    │
  │  ├─── domain_router.py   (Personal/Business)│
  │  └─── audit_logger.py    (JSON -> /Logs)    │
  │                                             │
  │  classify → summarize → route → verify      │
  └─────────────────────────────────────────────┘
        |               |
   [Personal/]     [Business/]
        |               |
        +-------+-------+
                |
            [Done/]
                |
        ceo_briefing.py
                |
          [Briefings/]
```

---

## Gold Tier Features

| Feature | Description |
|---------|-------------|
| **Cross-Domain Integration** | Tasks auto-classified as Personal or Business via keyword scoring + header detection |
| **4 MCP Servers** | `file_ops`, `email_ops`, `calendar_ops`, `audit_ops` — each with dedicated tools |
| **Ralph Wiggum Loop** | Autonomous loop keeps processing until `Needs_Action/` is empty or MAX_LOOPS hit |
| **CEO Weekly Briefing** | Auto-generated markdown briefing with task counts, domain splits, error rates |
| **JSON Audit Logging** | Every action logged as individual JSON file in `/Logs` with timestamp, server, details |
| **Error Recovery** | Failed tasks retry up to MAX_RETRIES, then move to Done with error status |
| **Graceful Degradation** | If OpenAI is down/unconfigured, agent still classifies, routes, and logs (fallback mode) |
| **Gmail Integration** | `gmail_watcher.py` ingests unread emails as task files (optional, local-only) |

---

## MCP Servers

| Server | File | Tools |
|--------|------|-------|
| File Ops | `mcp_file_ops.py` | `list_tasks`, `read_task`, `write_task`, `move_task`, `delete_task` |
| Email Ops | `mcp_email_ops.py` | `classify_sender`, `parse_email_headers`, `create_task_from_email`, `draft_reply` |
| Calendar Ops | `mcp_calendar_ops.py` | `get_current_week`, `is_briefing_due`, `prioritize_tasks`, `create_schedule_entry` |
| Audit Ops | `mcp_audit_ops.py` | `get_recent_actions`, `get_error_log`, `get_action_summary`, `compliance_check` |

---

## Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd AI_Employee_Vault_Gold_Cloud
pip install -r requirements.txt
```

### 2. Configure Secrets

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Drop a Task

```bash
# Create a test task in Inbox/
cat > Inbox/test-task.md << 'EOF'
# Quarterly Sales Report

Review Q4 revenue numbers and prepare executive summary.
Client: Acme Corp
Deadline: Friday
Domain: business
EOF
```

### 4. Run the Gold Agent

```bash
python gold_agent.py
```

You'll see:
```
============================================================
  AI Employee Vault — GOLD TIER Agent
============================================================

--- Loop 1 ---
  Inbox: 1 file(s) moved to Needs_Action
  Tasks pending: 1
  DONE: test-task.md

  All tasks processed!

CEO Briefing saved: CEO_Briefing_2026-02-18.md

============================================================
  GOLD AGENT COMPLETE
  Loops: 1
  Processed: 1
  Failed: 0
============================================================
```

### 5. Check Results

```bash
# Processed task
cat Done/test-task.md

# Domain-routed copy
cat Business/test-task.md

# CEO Briefing
cat Briefings/CEO_Briefing_*.md

# Audit logs (JSON per action)
ls Logs/
cat Logs/*.json | head -20
```

---

## Demo: Full Pipeline

```bash
# Step 1: Create multiple tasks (mix of personal + business)
cat > Inbox/meeting-prep.md << 'EOF'
# Meeting Prep
Prepare slides for stakeholder review.
Budget discussion with vendor.
EOF

cat > Inbox/grocery-list.md << 'EOF'
# Grocery Shopping
Pick up milk, eggs, bread.
Also need birthday cake for Saturday.
EOF

# Step 2: Run agent — it processes BOTH, classifies, and loops
python gold_agent.py

# Step 3: Verify cross-domain routing
ls Business/    # meeting-prep.md
ls Personal/    # grocery-list.md
ls Done/        # both files
ls Logs/        # JSON audit trail for every action
cat Briefings/CEO_Briefing_*.md
```

---

## Cloud Deployment (GitHub Actions)

The Gold Agent runs automatically via `.github/workflows/gold-agent.yml`:

1. Add `OPENAI_API_KEY` to repo **Settings > Secrets > Actions**
2. Drop `.md` files into `Inbox/` or `Needs_Action/`
3. Push to trigger, or wait for the 10-minute cron schedule
4. Agent processes all tasks, commits results back to repo

---

## File Structure

```
AI_Employee_Vault_Gold_Cloud/
├── gold_agent.py          # Main agent (Ralph Wiggum loop)
├── agent.py               # Legacy Silver agent (preserved)
├── audit_logger.py        # JSON audit logging engine
├── ceo_briefing.py        # Weekly CEO briefing generator
├── domain_router.py       # Personal/Business classifier
├── mcp_file_ops.py        # MCP Server 1: File operations
├── mcp_email_ops.py       # MCP Server 2: Email operations
├── mcp_calendar_ops.py    # MCP Server 3: Calendar/scheduling
├── mcp_audit_ops.py       # MCP Server 4: Audit queries
├── mcp_server.py          # Legacy Silver MCP server
├── gmail_watcher.py       # Gmail ingestion (local, optional)
├── watcher_inbox.py       # Inbox -> Needs_Action watcher
├── approve.py             # Human-in-the-loop approval
├── .env.example           # Config template (copy to .env)
├── .gitignore             # Secrets + runtime files excluded
├── requirements.txt       # Python dependencies
├── Inbox/                 # Drop tasks here
├── Needs_Action/          # Agent picks up from here
├── Done/                  # Completed tasks land here
├── Personal/              # Personal domain tasks
├── Business/              # Business domain tasks
├── Briefings/             # Weekly CEO briefings
├── Logs/                  # JSON audit logs (one per action)
├── specs/                 # Tier requirement docs
├── skills/                # Claude Code skill definitions
└── .github/workflows/     # CI/CD automation
```

---

## Tier Progression

| Tier | Features |
|------|----------|
| **Bronze** | Vault + 1 watcher + Claude Code processing |
| **Silver** | OpenAI integration + MCP server + GitHub Actions cloud |
| **Gold** | Cross-domain + 4 MCP servers + CEO briefing + audit logs + autonomous loop + error recovery |

---

*Built for Hackathon 0 by Mehreen*
