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
  ┌─────────────────────────────────────────────────────┐
  │              gold_agent.py                          │
  │              Ralph Wiggum Loop                      │
  │                                                     │
  │  Stage 0: hitl.process_approvals()  ← Approved/    │
  │           hitl.process_rejections() ← Rejected/     │
  │                                                     │
  │  Stage 1: stage_inbox() flush                       │
  │                                                     │
  │  Stage 2: per-task pipeline                         │
  │    ┌─── mcp_file_ops.py    (CRUD files)             │
  │    ├─── mcp_email_ops.py   (classify email)         │
  │    ├─── mcp_calendar_ops.py(schedule/priority)      │
  │    ├─── mcp_audit_ops.py   (audit queries)          │
  │    ├─── domain_router.py   (Personal/Business)      │
  │    ├─── audit_logger.py    (JSON -> /Logs + Neon)   │
  │    └─── hitl.py            (HITL detection)         │
  │                                                     │
  │    classify → HITL-check → summarize → route        │
  └─────────────────────────────────────────────────────┘
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

## Gold Tier Features

| Feature | Description |
|---------|-------------|
| **Cross-Domain Integration** | Tasks auto-classified as Personal or Business via keyword scoring + header detection |
| **4 MCP Servers** | `file_ops`, `email_ops`, `calendar_ops`, `audit_ops` — each with dedicated tools |
| **Ralph Wiggum Loop** | Autonomous loop keeps processing until `Needs_Action/` is empty or MAX_LOOPS hit |
| **HITL Approval Workflow** | Sensitive tasks (email send, payment, deploy, publish) paused in `Pending_Approval/` with YAML-frontmatter approval requests |
| **CEO Weekly Briefing** | Auto-generated markdown briefing with task counts, domain splits, error rates |
| **JSON Audit Logging** | Every action logged as individual JSON file in `/Logs` with timestamp, server, details |
| **Neon DB Audit Trail** | All events + agent run stats persisted to Postgres `agent_runs` + `events` tables |
| **Error Recovery** | Failed tasks retry up to MAX_RETRIES, then move to Done with error status |
| **Gmail Inbox Watcher** | `watchers/gmail_inbox_watcher.py` polls Gmail, converts unread emails to `Inbox/` task files; safe DRY_RUN=true default |

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

### 5. (Optional) Gmail Inbox Watcher — Stream Live Emails as Tasks

```bash
# First-time only: generate OAuth2 token (opens browser)
py generate_gmail_token.py

# Terminal 1 — watcher polls Gmail every 10 s (DRY_RUN=true by default)
py watchers/gmail_inbox_watcher.py
# Windows batch shortcut:
# scripts\run_gmail_watcher.bat

# Terminal 2 — agent processes emails that land in Inbox/
py gold_agent.py
```

> **DRY_RUN default (`MCP_DRY_RUN=true`):** the watcher creates `Inbox/` task files
> but does **not** mark emails as read or touch Gmail in any way.
> To enable mark-read, set in `.env`:
> ```ini
> MCP_DRY_RUN=false
> GMAIL_MARK_READ_ON_PROCESS=true
> ```
> See [`docs/GMAIL_WATCHER_SETUP.md`](docs/GMAIL_WATCHER_SETUP.md) for the full setup guide.

---

### 6. Check Results

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

## HITL Demo Steps

Human-in-the-Loop approval gates sensitive tasks before they execute.

### Sensitive action triggers

The following keywords in a task's content automatically trigger HITL:

| Keyword | Action type |
|---------|------------|
| `send email`, `email blast` | `email_send` |
| `payment`, `wire transfer`, `purchase` | `payment` |
| `publish`, `post to`, `broadcast` | `publish` |
| `deploy to prod`, `push to production`, `go-live` | `deploy` |
| `delete all`, `purge`, `drop table` | `delete` |
| `submit form`, `click confirm`, `auto-click` | `browser_action` |
| `slack message`, `webhook` | `notify_external` |

### Step-by-step demo

**1. Drop a sensitive task**
```bash
cat > Inbox/send-campaign.md << 'EOF'
# Q1 Email Campaign
Send email blast to all subscribers with the new product announcement.
Subject: "Introducing Gold Tier — April Launch"
EOF
```

**2. Run the agent — it detects sensitivity and pauses**
```bash
python gold_agent.py
```
Output:
```
--- Loop 1 ---
  Tasks pending: 1
  HITL: send-campaign.md (awaiting approval in Pending_Approval/)

  HITL queue: 1
```

**3. Review the approval request**
```bash
python approve.py
```
Output:
```
Pending HITL approval requests (1):

  hitl_20260219_103000_send-campaign.md
    action=email_send  task=send-campaign.md

Approve:  python approve.py <filename>
Reject:   python approve.py --reject <filename> [--reason "text"]
```

**4a. Approve** (agent will resume task on next run)
```bash
python approve.py hitl_20260219_103000_send-campaign.md
```

**4b. Reject with reason**
```bash
python approve.py --reject hitl_20260219_103000_send-campaign.md --reason "Not ready for launch"
```

**5. Run agent again to complete approved tasks**
```bash
python gold_agent.py
```
Output:
```
--- Loop 1 ---
  HITL: 1 task(s) approved and processed
  DONE: send-campaign.md
```

**6. Check results**
```bash
ls Pending_Approval/    # empty — request processed
ls Done/                # approved task summary here
ls Done/rejected_*      # rejected tasks archived here
cat Logs/*.json | python -m json.tool | head -40   # audit trail
```

### Approval request format (YAML frontmatter)

```yaml
---
type: hitl_approval_request
action: email_send
task_file: send-campaign.md
domain: business
status: pending_approval
created: 2026-02-19T10:30:00+00:00
expires: 2026-02-20T10:30:00+00:00
run_id: 3
sensitive_keywords:
  - send email
  - email blast
payload_summary: "Send email blast to all subscribers..."
---
```

---

## Watcher Architecture

Watchers are modular, cloud-safe components that feed tasks into the pipeline.
All share a common **`BaseWatcher`** skeleton with two operating modes:

| Mode | Flag | Use case |
|------|------|----------|
| **Infinite loop** | *(no flag)* | Local dev — polls `Inbox/` continuously |
| **One-shot** | `--once` | GitHub Actions / cron — one scan then exit |

### BaseWatcher (`base_watcher.py`)

Abstract base. Subclasses implement one method:

```python
class MyWatcher(BaseWatcher):
    name = "my_watcher"

    def run_once(self) -> int:
        # scan, process, return items-processed count
        return processed_count

if __name__ == "__main__":
    MyWatcher.cli(base_dir=BASE_DIR, default_interval=10.0).run()
```

Built-in features:
- **Exponential backoff** on consecutive errors (doubles per error, capped at 60s)
- **Structured audit logging** on every start / stop / error / processed cycle
- **`--once` / `--interval` / `--dir`** CLI flags via `argparse`

### InboxWatcher (`inbox_watcher.py`)

Concrete Gold Tier watcher. `Inbox/` → `Needs_Action/`.

On each scan cycle:
1. Globs `Inbox/*.md` (skips `.gitkeep`)
2. If a file has **no YAML frontmatter** → injects standardised block:
   ```yaml
   ---
   source: inbox
   ingested_at: "2026-02-19T12:00:00+00:00"
   watcher: inbox_watcher
   status: pending
   ---
   ```
3. Writes enriched file to `Needs_Action/<filename>`
4. Removes original from `Inbox/`
5. Logs the event to `audit_logger`

### Run locally (infinite loop)

```bash
# Terminal 1 — watcher polls every 5s, adds frontmatter as tasks arrive
python inbox_watcher.py

# Terminal 2 — agent processes as tasks appear in Needs_Action/
python gold_agent.py
```

Output:
```
[inbox_watcher] Starting (polling every 5.0s)
  [inbox_watcher] q1-review.md → Needs_Action/  (frontmatter added)
[inbox_watcher] 12:34:56Z — 1 item(s) processed
```

Custom options:
```bash
python inbox_watcher.py --interval 30      # poll every 30s
python inbox_watcher.py --dir /vault/path  # custom vault root
```

### Run in GitHub Actions (one-shot)

The workflow runs the watcher as a one-shot step **before** the agent:

```yaml
- name: Run Inbox Watcher (one-shot, standardize tasks)
  run: python inbox_watcher.py --once

- name: Run Gold Agent
  run: python gold_agent.py
```

The watcher moves and standardizes `Inbox/` → `Needs_Action/`. The agent's internal `stage_inbox()` then finds `Inbox/` empty and processes `Needs_Action/` directly.

### Adding a new watcher

1. Create `my_watcher.py`, subclass `BaseWatcher`
2. Set `name = "my_watcher"`, implement `run_once() -> int`
3. Add entry point: `if __name__ == "__main__": MyWatcher.cli(base_dir=BASE_DIR).run()`
4. Add an optional `--once` step to `gold-agent.yml`

---

## Cloud Deployment (GitHub Actions)

The Gold Agent runs automatically via `.github/workflows/gold-agent.yml`:

1. Add `OPENAI_API_KEY` to repo **Settings > Secrets > Actions**
2. Add `DATABASE_URL` (Neon Postgres connection string) to repo secrets
3. Drop `.md` files into `Inbox/` and push to `main`
4. Or wait for the scheduled cron (every 10 minutes)
5. Workflow: `init_db` → `inbox_watcher --once` → `gold_agent` → commit results

---

## File Structure

```
AI_Employee_Vault_Gold_Cloud/
├── gold_agent.py          # Main agent (Ralph Wiggum loop)
├── base_watcher.py        # Abstract BaseWatcher (loop + backoff + CLI)
├── inbox_watcher.py       # Gold Tier InboxWatcher (Inbox/ → Needs_Action/)
├── audit_logger.py        # JSON per-action logging → Logs/ + Neon DB
├── vault_logger.py        # Daily JSON array + Obsidian run timelines
├── ceo_briefing.py        # Weekly CEO briefing generator
├── domain_router.py       # Personal/Business classifier
├── hitl.py                # HITL detection, approval requests, resume/reject
├── approve.py             # HITL approval CLI (approve / reject)
├── mcp_file_ops.py        # MCP Server 1: File operations
├── mcp_email_ops.py       # MCP Server 2: Email operations
├── mcp_calendar_ops.py    # MCP Server 3: Calendar/scheduling
├── mcp_audit_ops.py       # MCP Server 4: Audit queries
├── watchers/
│   └── gmail_inbox_watcher.py  # Gmail Inbox Watcher (polls Gmail → Inbox/ tasks)
├── scripts/
│   └── run_gmail_watcher.bat   # Windows launcher for Gmail watcher
├── watcher_inbox.py       # Legacy Silver watcher (preserved)
├── agent.py               # Legacy Silver agent (preserved)
├── mcp_server.py          # Legacy Silver MCP server (preserved)
├── .env.example           # Config template (copy to .env)
├── .gitignore             # Secrets + runtime files excluded
├── requirements.txt       # Python dependencies
│
├── Dashboard.md           # Obsidian home note (start here)
├── Index.md               # Complete vault table of contents
├── Company_Handbook.md    # Procedures, HITL guide, env vars
├── Business_Goals.md      # OKRs, sprint backlog, key metrics
├── Templates/             # Obsidian note templates
│   ├── Daily_Note.md
│   ├── Task_Note.md
│   └── HITL_Review.md
│
├── Inbox/                 # Drop tasks here (watcher picks up)
├── Needs_Action/          # Agent working queue
├── Done/                  # Completed & AI-summarized tasks
├── Personal/              # Personal-domain routed copies
├── Business/              # Business-domain routed copies
├── Pending_Approval/      # HITL: held tasks + approval request files
├── Approved/              # HITL: human-approved (agent resumes on next run)
├── Rejected/              # HITL: human-rejected (agent archives)
├── Briefings/             # Weekly CEO briefings (Obsidian-linked)
├── Plans/                 # AI-generated task plans
├── Logs/                  # Per-action JSON files + daily JSON arrays
│   └── Runs/              # Per-run Obsidian timelines (run_<id>.md)
├── backend/               # SQLAlchemy + Neon DB layer
│   ├── db.py
│   ├── models.py
│   └── init_db.py
├── specs/                 # Tier requirement docs
├── skills/                # Claude Code skill definitions
└── .github/workflows/
    └── gold-agent.yml     # CI/CD: watcher + agent + commit
```

---

## Evidence Pack

Generate a judge-ready `Evidence/` folder in one command:

```bash
python tools/generate_evidence_pack.py
# or
make evidence
```

This produces:

| File | What it proves |
|---|---|
| `Evidence/README.md` | Index — what to check and where |
| `Evidence/ARCHITECTURE.md` | ASCII system diagram + full data flow |
| `Evidence/PROOF_CHECKLIST.md` | 66-item checklist mapped to exact source files |
| `Evidence/SAMPLE_RUN.md` | Annotated console output + screenshot placeholders |
| `Evidence/REGISTERED_MCP_TOOLS.json` | **Live** dump from `mcp.registry.list_registered()` |
| `Evidence/LAST_RUN_SUMMARY.json` | Latest run_id, loops, processed, failed, db_events |
| `Evidence/ODOO_DEMO.md` | **Live** dry-run proof for all 3 Odoo MCP tools |

---

## Demo Scenarios

Three ready-made task files live in `Demo_Scenarios/`. Each demonstrates a different MCP integration path. Use `tools/load_demo_task.py` to copy a scenario into `Inbox/` with a timestamped filename so you can run multiple demos without collisions.

### Available scenarios

| Scenario | File | Triggers | HITL? |
|---|---|---|---|
| Odoo invoice check | `Demo_Scenarios/odoo_invoice_check.md` | `odoo_list_invoices` | No — auto |
| Gmail draft demo | `Demo_Scenarios/gmail_draft_demo.md` | `draft_email` + `email_send` | Yes |
| Browser screenshot | `Demo_Scenarios/browser_screenshot_demo.md` | `browser_action` | Yes |

### Load and run a demo

```bash
# List all scenarios with trigger descriptions
python tools/load_demo_task.py --list

# Load the Odoo scenario (auto-triggers, no HITL needed)
python tools/load_demo_task.py odoo
python gold_agent.py
# Check: Done/<timestamp>_odoo_invoice_check.md
# Check: Logs/Runs/run_*_mcp_report.json  (odoo_list_invoices call logged)

# Load the Gmail draft demo (triggers HITL)
python tools/load_demo_task.py gmail
python gold_agent.py             # agent pauses — task held in Pending_Approval/
python approve.py                # list pending approvals
python approve.py hitl_<ts>_gmail_draft_demo.md   # approve
python gold_agent.py             # agent resumes — email_send dispatched (dry-run)

# Load the browser screenshot demo (triggers HITL)
python tools/load_demo_task.py browser
python gold_agent.py             # agent pauses — browser_action HITL request
python approve.py                # list pending approvals
python approve.py hitl_<ts>_browser_screenshot_demo.md
python gold_agent.py             # agent resumes — browser_action stub runs
```

Or use the Makefile shortcuts:

```bash
make demo-odoo      # loads + instructs you to run gold_agent
make demo-gmail
make demo-browser
make demo-list      # prints the scenario table
```

### What each scenario demonstrates

**`odoo_invoice_check.md`** — the automatic Odoo path:
- Keywords `invoice`, `accounting`, `receivable` trigger `should_trigger_odoo()` in the agent
- `odoo_list_invoices` is called via MCP router before OpenAI summarization
- No human approval required; task goes straight to `Done/`
- In DRY_RUN mode returns simulated data (INV/2026/00001, ACME Corp, $1500)
- Set `MCP_DRY_RUN=false` with real Odoo credentials for live results — see `docs/ODOO_SETUP.md`

**`gmail_draft_demo.md`** — the HITL email path:
- Keyword `send email` triggers HITL (action type: `email_send`)
- Agent writes `Pending_Approval/hitl_<ts>_gmail_draft_demo.md` and pauses
- Human reviews and approves with `python approve.py`
- On next agent run: task resumes, `email_mcp_stub.handle_email_send` dispatched
- With Gmail OAuth configured (`token.json`), `gmail_mcp_server.draft_email` creates a real draft — see `docs/GMAIL_SETUP.md`

**`browser_screenshot_demo.md`** — the HITL browser path:
- Keywords `submit form` + `auto-click` trigger HITL (action type: `browser_action`)
- Agent writes `Pending_Approval/hitl_<ts>_browser_screenshot_demo.md` and pauses
- Human reviews and approves with `python approve.py`
- On next agent run: `browser_mcp_stub.handle_browser_action` dispatched (dry-run)
- Set `MCP_DRY_RUN=false` + install Playwright for real browser execution

---

## Tier Progression

| Tier | Features |
|------|----------|
| **Bronze** | Vault + 1 watcher + Claude Code processing |
| **Silver** | OpenAI integration + MCP server + GitHub Actions cloud |
| **Gold** | Cross-domain + 4 MCP servers + CEO briefing + audit logs + autonomous loop + error recovery |

---

*Built for Hackathon 0 by Mehreen*
