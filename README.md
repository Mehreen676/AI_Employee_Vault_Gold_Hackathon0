# AI Employee Vault — Gold Tier

> Hackathon 0 | Personal AI Employee with full cross-domain autonomy

<p align="center">
  <img src="https://img.shields.io/badge/Tier-Gold%20%F0%9F%A5%87-FFD700?style=flat-square&logoColor=white" alt="Gold Tier"/>
  <img src="https://img.shields.io/badge/Cloud-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="Cloud"/>
  <img src="https://img.shields.io/badge/HITL-Enabled-FF6B35?style=flat-square&logo=shield&logoColor=white" alt="HITL"/>
  <img src="https://img.shields.io/badge/MCP-4%20Servers-10B981?style=flat-square&logo=server&logoColor=white" alt="MCP"/>
  <img src="https://img.shields.io/badge/Audit-JSON%20%2B%20Neon%20DB-6366F1?style=flat-square&logo=postgresql&logoColor=white" alt="Audit"/>
  <img src="https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/HuggingFace-Spaces-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="HuggingFace"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License"/>
</p>

## What Is This?

A fully autonomous AI Employee that processes tasks from email or manual input, classifies them across **Personal** and **Business** domains, summarizes them with OpenAI, and loops until everything is done — then generates a **Weekly CEO Briefing**.

Built on 4 MCP servers, a production FastAPI REST API, comprehensive JSON audit logging, error recovery with graceful degradation, and a **Ralph Wiggum autonomous loop** ("I'm in danger!") that keeps running until all tasks reach `Done/`.

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

## Architecture (Visual)

<p align="center">
  <img src="docs/architecture.svg" alt="Gold Tier Architecture" width="900"/>
</p>

> Full Mermaid diagram: [`Evidence/ARCH_DIAGRAM.md`](Evidence/ARCH_DIAGRAM.md) &nbsp;|&nbsp; ASCII: [`Evidence/ARCH_DIAGRAM.txt`](Evidence/ARCH_DIAGRAM.txt)

---

## Gold Tier Features

| Feature | Description |
|---------|-------------|
| **REST API (FastAPI)** | 15 production endpoints across 5 routers — fully documented at `/docs` |
| **Cross-Domain Integration** | Tasks auto-classified as Personal or Business via keyword scoring + header detection |
| **4 MCP Servers** | `file_ops`, `email_ops`, `calendar_ops`, `audit_ops` — each with dedicated tools |
| **Ralph Wiggum Loop** | Autonomous loop keeps processing until `Needs_Action/` is empty or MAX_LOOPS hit |
| **HITL Approval Workflow** | Sensitive tasks (email send, payment, deploy, publish) paused in `Pending_Approval/` with YAML-frontmatter approval requests |
| **CEO Weekly Briefing** | Auto-generated markdown briefing with task counts, domain splits, error rates |
| **JSON Audit Logging** | Every action logged as individual JSON file in `/Logs` with timestamp, server, details |
| **Neon DB Audit Trail** | All events + agent run stats persisted to Postgres `agent_runs` + `events` tables |
| **Error Recovery** | Failed tasks retry up to MAX_RETRIES, then move to Done with error status |
| **Gmail Inbox Watcher** | `watchers/gmail_inbox_watcher.py` polls Gmail, converts unread emails to `Inbox/` task files; safe DRY_RUN=true default |
| **Docker / HF Spaces** | Single `Dockerfile` deploys on Hugging Face Spaces (Docker SDK) — port 7860 |

---

## REST API — Cloud Proof

The FastAPI backend is live with **15 endpoints** across 5 routers, all visible in the interactive Swagger UI at `/docs`.

### Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000/docs** to explore and test every endpoint interactively.

### Endpoint Reference

| Method | Path | Router | Description |
|--------|------|--------|-------------|
| `GET` | `/` | General | Service info + version |
| `GET` | `/health` | General | Health check — DB + env var status |
| `GET` | `/docs` | — | Swagger UI (interactive docs) |
| `GET` | `/redoc` | — | ReDoc API reference |
| `POST` | `/agent/run` | Agent | Trigger agent run — returns **202 Accepted** |
| `GET` | `/agent/status` | Agent | Latest `AgentRun` stats from Neon DB |
| `GET` | `/hitl/pending` | HITL | List `hitl_*.md` files in `Pending_Approval/` |
| `POST` | `/hitl/approve` | HITL | Move file to `Approved/` (agent resumes task) |
| `POST` | `/hitl/reject` | HITL | Move file to `Rejected/` with reason |
| `POST` | `/approve/apply` | Approval | Unified approve or reject by `action` field |
| `GET` | `/approve/help` | Approval | Workflow guide + CLI commands |
| `GET` | `/mcp/tools` | MCP | List registered MCP tools + schemas |
| `POST` | `/mcp/execute` | MCP | Execute `list_tasks`, `read_task`, `move_task` |
| `GET` | `/inbox/tasks` | Inbox | List files currently in `Inbox/` |
| `POST` | `/inbox/add` | Inbox | Write a new task file to `Inbox/` |

### Quick curl proof

```bash
# 1. Root
curl http://localhost:8000/

# 2. Health check
curl http://localhost:8000/health

# 3. Agent status (reads from Neon DB)
curl http://localhost:8000/agent/status

# 4. List pending HITL approvals
curl http://localhost:8000/hitl/pending

# 5. Approve a HITL request
curl -X POST http://localhost:8000/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_task.md"}'

# 6. List MCP tools
curl http://localhost:8000/mcp/tools

# 7. List tasks in Inbox/
curl http://localhost:8000/inbox/tasks

# 8. Add a task to Inbox/
curl -X POST http://localhost:8000/inbox/add \
  -H "Content-Type: application/json" \
  -d '{"filename": "test-api-task.md", "content": "Review Q4 numbers and prepare summary."}'

# 9. Trigger agent run (202 Accepted)
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"mode": "once", "max_loops": 1}'

# 10. Approval help guide
curl http://localhost:8000/approve/help
```

### Router files

| File | Prefix | Router defines |
|------|--------|----------------|
| `backend/routers/agent.py` | `/agent` | `POST /run`, `GET /status` |
| `backend/routers/hitl.py` | `/hitl` | `GET /pending`, `POST /approve`, `POST /reject` |
| `backend/routers/approve.py` | `/approve` | `POST /apply`, `GET /help` |
| `backend/routers/mcp.py` | `/mcp` | `GET /tools`, `POST /execute` |
| `backend/routers/inbox.py` | `/inbox` | `GET /tasks`, `POST /add` |

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
git clone https://github.com/Mehreen676/AI_Employee_Vault_Gold_Hackathon0.git
cd AI_Employee_Vault_Gold_Hackathon0
pip install -r requirements.txt
```

### 2. Configure Secrets

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, OPENAI_API_KEY, INSTAGRAM_ACCESS_TOKEN
```

### 3. Start the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### 4. Drop a Task

```bash
# Via API
curl -X POST http://localhost:8000/inbox/add \
  -H "Content-Type: application/json" \
  -d '{"filename": "q4-report.md", "content": "Review Q4 revenue numbers and prepare executive summary.\nClient: Acme Corp\nDeadline: Friday\nDomain: business"}'

# Or drop a file directly
echo "# Q4 Report\nReview Q4 numbers." > Inbox/q4-report.md
```

### 5. Run the Gold Agent

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
  DONE: q4-report.md

  All tasks processed!

CEO Briefing saved: CEO_Briefing_2026-02-26.md

============================================================
  GOLD AGENT COMPLETE
  Loops: 1
  Processed: 1
  Failed: 0
============================================================
```

### 6. (Optional) Gmail Inbox Watcher — Stream Live Emails as Tasks

```bash
# First-time only: generate OAuth2 token (opens browser)
py generate_gmail_token.py

# Terminal 1 — watcher polls Gmail every 10 s (DRY_RUN=true by default)
py watchers/gmail_inbox_watcher.py

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

### Diagnostic Tools

```bash
# MCP Health Report — registered tools, DRY_RUN status, last log timestamp
python tools/mcp_health_report.py
# Writes: Evidence/MCP_HEALTH_REPORT.json

# Architecture Diagrams — ASCII + Mermaid
python tools/generate_architecture_diagram.py
# Writes: Evidence/ARCH_DIAGRAM.txt
#         Evidence/ARCH_DIAGRAM.md
```

### Check Results

```bash
# Processed task
cat Done/q4-report.md

# Domain-routed copy
cat Business/q4-report.md

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

**3a. Review + Approve via API**
```bash
# List pending
curl http://localhost:8000/hitl/pending

# Approve
curl -X POST http://localhost:8000/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_send-campaign.md"}'
```

**3b. Review + Reject via API**
```bash
curl -X POST http://localhost:8000/hitl/reject \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_send-campaign.md", "reason": "Not ready for launch"}'
```

**3c. Or use the CLI**
```bash
python approve.py                                          # list all pending
python approve.py hitl_20260226_120000_send-campaign.md    # approve
python approve.py --reject hitl_20260226_120000_send-campaign.md --reason "Not ready"
```

**4. Run agent again to complete approved tasks**
```bash
python gold_agent.py
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

---

## Cloud Deployment (GitHub Actions)

The Gold Agent runs automatically via `.github/workflows/gold-agent.yml`:

1. Add `OPENAI_API_KEY` to repo **Settings > Secrets > Actions**
2. Add `DATABASE_URL` (Neon Postgres connection string) to repo secrets
3. Drop `.md` files into `Inbox/` and push to `main`
4. Or wait for the scheduled cron (every 10 minutes)
5. Workflow: `init_db` → `inbox_watcher --once` → `gold_agent` → commit results

---

## Hugging Face Spaces Deployment

The `Dockerfile` in this repo is ready for **Hugging Face Spaces — Docker SDK**.

### Prerequisites

- Hugging Face account
- The following secrets set in your Space settings:

| Secret | Required | Description |
|--------|----------|-------------|
| `DATABASE_URL` | Yes | Neon Postgres connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `INSTAGRAM_ACCESS_TOKEN` | Yes | Meta/Instagram token (any value for demo) |
| `ALLOWED_ORIGINS` | No | CORS origins (default `*`) |

### Step-by-step

**1. Create a new Space**

Go to [huggingface.co/new-space](https://huggingface.co/new-space) and choose:
- SDK: **Docker**
- Visibility: Public or Private

**2. Add this YAML to the top of your Space's `README.md`**

```yaml
---
title: AI Employee Vault Gold Cloud
emoji: 🤖
colorFrom: yellow
colorTo: gold
sdk: docker
app_port: 7860
pinned: false
---
```

**3. Push the code**

```bash
# Clone your new HF Space
git clone https://huggingface.co/spaces/<your-username>/<your-space-name>
cd <your-space-name>

# Copy this repo's files in
cp -r /path/to/AI_Employee_Vault_Gold_Cloud/. .

# Add the HF YAML header to the top of README.md (see step 2 above)

# Push
git add .
git commit -m "Initial deployment — Gold Cloud FastAPI"
git push
```

**4. Set secrets in Space settings**

Go to **Space Settings → Repository secrets** and add:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `INSTAGRAM_ACCESS_TOKEN`

**5. Space is live**

HF Spaces builds the Docker image and starts the server. Your API is available at:
```
https://<your-username>-<your-space-name>.hf.space/docs
https://<your-username>-<your-space-name>.hf.space/health
```

### Local Docker test

```bash
docker build -t vault-gold .
docker run -p 7860:7860 --env-file .env vault-gold
# API docs: http://localhost:7860/docs
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

# Load the Gmail draft demo (triggers HITL)
python tools/load_demo_task.py gmail
python gold_agent.py             # agent pauses — task held in Pending_Approval/
curl http://localhost:8000/hitl/pending    # list via API
python approve.py                          # or list via CLI
python approve.py hitl_<ts>_gmail_draft_demo.md
python gold_agent.py             # agent resumes
```

---

## Social MCP Demo (Safe Stub)

The `social_mcp_stub` provides a **permanently safe** social media integration.
No real post is ever sent — a hardcoded `social_safety_gate` blocks live posting
even when `MCP_DRY_RUN=false`.  All actions are logged to `Logs/` as JSON.

### Run the demo in 3 commands

```bash
python tools/load_demo_task.py facebook_post_demo
python gold_agent.py
python tools/generate_evidence_pack.py
```

---

## Scheduled Audit (Daily)

```bash
python scripts/run_daily_audit.py
```

Outputs:
- `Business/Reports/DAILY_AUDIT_<date>.md` — executive summary
- `Evidence/DAILY_AUDIT_<date>.json` — full stats snapshot

---

## X (Twitter) API v2 Integration

> `MCP_DRY_RUN=true` (default) simulates tweets — no X API calls made.

```ini
X_BEARER_TOKEN=AAAAAAAAxxxxx...   # OAuth 2.0 user access token (tweet.write)
```

---

## Meta (Facebook/Instagram) Integration

> `MCP_DRY_RUN=true` (default) simulates all posts — no Meta API calls made.

```ini
META_ACCESS_TOKEN=EAAxxxxx...
META_PAGE_ID=123456789
META_IG_USER_ID=987654321
```

---

## Real Odoo (JSON-RPC) Integration

> When `MCP_DRY_RUN=true` (default) all calls are simulated — no Odoo needed.

```ini
ODOO_URL=http://localhost:8069
ODOO_DB=mycompany
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

---

## File Structure

```
AI_Employee_Vault_Gold_Cloud/
├── main.py                # FastAPI entry point (uvicorn main:app)
├── Dockerfile             # HF Spaces / Docker deployment
├── .dockerignore          # Excludes secrets + venv from Docker image
├── requirements.txt       # Python dependencies (fastapi, uvicorn, sqlalchemy…)
├── .env.example           # Config template (copy to .env)
│
├── backend/               # DB layer + REST API routers
│   ├── __init__.py
│   ├── db.py              # SQLAlchemy engine + SessionLocal (Neon Postgres)
│   ├── models.py          # ORM: Task, AgentRun, Event
│   ├── init_db.py         # Schema creation script
│   └── routers/           # FastAPI APIRouter modules
│       ├── __init__.py
│       ├── agent.py       # POST /agent/run, GET /agent/status
│       ├── hitl.py        # GET /hitl/pending, POST /hitl/approve|reject
│       ├── approve.py     # POST /approve/apply, GET /approve/help
│       ├── mcp.py         # GET /mcp/tools, POST /mcp/execute
│       └── inbox.py       # GET /inbox/tasks, POST /inbox/add
│
├── gold_agent.py          # Main agent (Ralph Wiggum loop)
├── base_watcher.py        # Abstract BaseWatcher (loop + backoff + CLI)
├── inbox_watcher.py       # Gold Tier InboxWatcher (Inbox/ → Needs_Action/)
├── audit_logger.py        # JSON per-action logging → Logs/ + Neon DB
├── ceo_briefing.py        # Weekly CEO briefing generator
├── domain_router.py       # Personal/Business classifier
├── hitl.py                # HITL detection, approval requests, resume/reject
├── approve.py             # HITL approval CLI (approve / reject)
├── mcp_file_ops.py        # MCP Server 1: File operations
├── mcp_email_ops.py       # MCP Server 2: Email operations
├── mcp_calendar_ops.py    # MCP Server 3: Calendar/scheduling
├── mcp_audit_ops.py       # MCP Server 4: Audit queries
│
├── watchers/
│   └── gmail_inbox_watcher.py
├── scripts/
│   └── run_gmail_watcher.bat
│
├── Inbox/                 # Drop tasks here (watcher picks up)
├── Needs_Action/          # Agent working queue
├── Done/                  # Completed & AI-summarized tasks
├── Personal/              # Personal-domain routed copies
├── Business/              # Business-domain routed copies
├── Pending_Approval/      # HITL: held tasks + approval request files
├── Approved/              # HITL: human-approved
├── Rejected/              # HITL: human-rejected
├── Briefings/             # Weekly CEO briefings
├── Logs/                  # Per-action JSON files
├── Evidence/              # Judge-ready evidence pack
└── .github/workflows/
    └── gold-agent.yml     # CI/CD: watcher + agent + commit
```

---

## Tier Progression

| Tier | Features |
|------|----------|
| **Bronze** | Vault + 1 watcher + Claude Code processing |
| **Silver** | OpenAI integration + MCP server + GitHub Actions cloud |
| **Gold** | Cross-domain + 4 MCP servers + CEO briefing + audit logs + autonomous loop + FastAPI REST API + HF Spaces Docker deployment |

---

*Built for Hackathon 0 by Mehreen*
