<p align="center">
  <img src="https://img.shields.io/badge/Tier-Gold%20%F0%9F%A5%87-FFD700?style=flat-square&logoColor=white" alt="Gold Tier"/>
  <img src="https://img.shields.io/badge/Cloud-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="Cloud"/>
  <img src="https://img.shields.io/badge/HITL-Enabled-FF6B35?style=flat-square&logo=shield&logoColor=white" alt="HITL"/>
  <img src="https://img.shields.io/badge/MCP-4%20Servers-10B981?style=flat-square&logo=server&logoColor=white" alt="MCP"/>
  <img src="https://img.shields.io/badge/Audit-JSON%20%2B%20Neon%20DB-6366F1?style=flat-square&logo=postgresql&logoColor=white" alt="Audit"/>
  <img src="https://img.shields.io/badge/FastAPI-15%20Endpoints-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/HuggingFace-Spaces%20Ready-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="HuggingFace"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License"/>
</p>

<h1 align="center">🚀 AI Employee Vault — Gold Tier</h1>
<h3 align="center">Autonomous AI Agent with HITL, MCP, Audit Logging & Cloud Deployment</h3>

<p align="center"><em>Hackathon 0 · Personal AI Employee with full cross-domain autonomy</em></p>

## What Is This?

A fully autonomous AI Employee that processes tasks from email or manual input, classifies them across **Personal** and **Business** domains, summarizes them with OpenAI, and loops until everything is done — then generates a **Weekly CEO Briefing**.

Built on 4 MCP servers, a production FastAPI REST API with 15 endpoints, comprehensive JSON audit logging, error recovery with graceful degradation, and a **Ralph Wiggum autonomous loop** that keeps running until all tasks reach `Done/`.

---

## 🎥 Live Demo

![Demo GIF](docs/demo.gif)

> _Swap `docs/demo.gif` with a real screen recording of the Swagger UI + HITL approval flow._

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
| **HITL Approval Workflow** | Sensitive tasks paused in `Pending_Approval/` with YAML-frontmatter approval requests |
| **CEO Weekly Briefing** | Auto-generated markdown briefing with task counts, domain splits, error rates |
| **JSON Audit Logging** | Every action logged as individual JSON file in `/Logs` with timestamp, server, details |
| **Neon DB Audit Trail** | All events + agent run stats persisted to Postgres `agent_runs` + `events` tables |
| **Error Recovery** | Failed tasks retry up to MAX_RETRIES, then move to Done with error status |
| **Gmail Inbox Watcher** | Polls Gmail, converts unread emails to `Inbox/` task files; safe DRY_RUN=true default |
| **Docker / HF Spaces** | Single `Dockerfile` deploys on Hugging Face Spaces (Docker SDK) — port 7860 |

---

## A) Live Local Run

### Step 1 — Install dependencies

```bash
git clone https://github.com/Mehreen676/AI_Employee_Vault_Gold_Hackathon0.git
cd AI_Employee_Vault_Gold_Hackathon0
pip install -r requirements.txt
```

### Step 2 — Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```ini
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
OPENAI_API_KEY=sk-...
INSTAGRAM_ACCESS_TOKEN=any-non-empty-value
```

> ⚠️ **Never commit `.env` to git.** It is listed in `.gitignore`. All secrets stay local or in Secrets managers.

### Step 3 — Start the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected startup output:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     vault | Running create_all against Neon Postgres …
INFO:     vault | Schema ready.
INFO:     vault | AI Employee Vault is online.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4 — Open Swagger UI

Navigate to **http://localhost:8000/docs**

The Swagger UI loads automatically and shows all **15 endpoints** grouped under 6 tags:
`General` · `Agent` · `HITL` · `Approval` · `MCP` · `Inbox`

Every endpoint is expandable — click **Try it out** to send live requests directly from the browser.

### Step 5 — Verify health

```bash
curl http://localhost:8000/health
```

**Expected output when DB is connected:**

```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "openai_key_set": true,
    "instagram_token_set": true
  }
}
```

HTTP `200 OK` — all systems green.

**Expected output when DATABASE_URL is missing:**

```json
{
  "status": "degraded",
  "checks": {
    "database": "unavailable",
    "openai_key_set": false,
    "instagram_token_set": false
  }
}
```

HTTP `503 Service Unavailable` — DB is considered critical.

---

## 📊 System Observability

| Signal | What it captures |
|--------|-----------------|
| **Neon Postgres** | Every agent run recorded in `agent_runs` table — run ID, timestamp, loop count, tasks processed, failures |
| **JSON audit logs** | Each action written as an individual `.json` file under `/Logs` — server name, tool, arguments, result, timestamp |
| **`GET /health`** | Validates live DB connectivity and presence of `OPENAI_API_KEY` + `INSTAGRAM_ACCESS_TOKEN`; returns `200` healthy or `503` degraded |
| **`GET /agent/status`** | Returns latest `AgentRun` record — last run ID, timestamp, total run count, current state |
| **`GET /mcp/tools`** | Lists every registered MCP tool with name, description, and JSON input schema |
| **GitHub Actions** | `.github/workflows/gold-agent.yml` runs on push and cron — inbox watcher → agent → commits results back to repo automatically |

### Quick observability checks

```bash
GET /health        # DB + key validation
GET /agent/status  # last agent run record
GET /mcp/tools     # registered tool registry
```

---

## B) API Endpoints (as seen in Swagger)

All 15 endpoints grouped by Swagger tag. Every route is registered in `main.py` via `app.include_router()` from `backend/routers/`.

### General

| Method | Path | Description | Example response |
|--------|------|-------------|-----------------|
| `GET` | `/` | Service info — name, version, status, docs link | `{"service": "AI Employee Vault — Gold Cloud", "version": "1.0.0", "status": "running", "docs": "/docs"}` |
| `GET` | `/health` | DB + env var health check. `200` = healthy, `503` = degraded | `{"status": "healthy", "checks": {"database": "connected", ...}}` |

### Agent

| Method | Path | Description | Body / Response |
|--------|------|-------------|----------------|
| `POST` | `/agent/run` | Trigger an agent run. Returns **202 Accepted** immediately. Wire to a task queue for async execution. | Body: `{"mode": "once", "max_loops": 1}` → `{"status": "accepted", "triggered_at": "..."}` |
| `GET` | `/agent/status` | Latest `AgentRun` record from Neon DB — run ID, timestamp, total run count | `{"status": "idle", "last_run_id": 7, "last_run_at": "2026-02-26T...", "total_runs": 7}` |

### HITL

| Method | Path | Description | Body / Response |
|--------|------|-------------|----------------|
| `GET` | `/hitl/pending` | List all `hitl_*.md` files in `Pending_Approval/` with parsed frontmatter | `[{"filename": "hitl_...", "action": "email_send", "task_file": "task.md", "status": "pending_approval"}]` |
| `POST` | `/hitl/approve` | Move a `hitl_*.md` from `Pending_Approval/` → `Approved/`. Agent resumes task on next run. | Body: `{"filename": "hitl_20260226_120000_task.md"}` → `{"success": true, "message": "Approved..."}` |
| `POST` | `/hitl/reject` | Move a `hitl_*.md` from `Pending_Approval/` → `Rejected/` with reason. | Body: `{"filename": "hitl_...", "reason": "Too risky"}` → `{"success": true, "message": "Rejected..."}` |

### Approval

| Method | Path | Description | Body / Response |
|--------|------|-------------|----------------|
| `POST` | `/approve/apply` | Unified endpoint — set `"action": "approve"` or `"action": "reject"` with optional reason | Body: `{"filename": "hitl_...", "action": "approve"}` → `{"success": true, "action": "approve", "message": "..."}` |
| `GET` | `/approve/help` | Returns structured workflow guide: all endpoints + CLI commands | `{"description": "...", "endpoints": [...], "cli_usage": [...]}` |

### MCP

| Method | Path | Description | Body / Response |
|--------|------|-------------|----------------|
| `GET` | `/mcp/tools` | List all registered MCP tools with name, description, and JSON input schema | `{"count": 3, "tools": [{"name": "list_tasks", ...}, ...]}` |
| `POST` | `/mcp/execute` | Execute a whitelisted tool. Only vault folders are permitted. Path traversal is blocked. | Body: `{"tool": "list_tasks", "arguments": {"folder": "Inbox"}}` → `{"success": true, "result": ["task.md"]}` |

**Available MCP tools via API:**

| Tool | Arguments | What it does |
|------|-----------|-------------|
| `list_tasks` | `{"folder": "Inbox"}` | Lists `*.md` files in a vault folder |
| `read_task` | `{"folder": "Inbox", "filename": "task.md"}` | Reads full file content |
| `move_task` | `{"filename": "task.md", "from_folder": "Inbox", "to_folder": "Needs_Action"}` | Moves a file between vault folders |

### Inbox

| Method | Path | Description | Body / Response |
|--------|------|-------------|----------------|
| `GET` | `/inbox/tasks` | List all `*.md` files currently sitting in `Inbox/` (not yet processed by watcher) | `{"count": 2, "tasks": [{"filename": "task.md", "size_bytes": 128, "preview": "..."}]}` |
| `POST` | `/inbox/add` | Write a new `*.md` task file to `Inbox/`. YAML frontmatter auto-injected if missing. Returns **201 Created**. | Body: `{"filename": "task.md", "content": "Review Q4..."}` → `{"success": true, "path": "Inbox/task.md"}` |

### Complete curl test suite

```bash
BASE=http://localhost:8000

# ── General ──────────────────────────────────────────────────────────────────
curl $BASE/
curl $BASE/health

# ── Agent ────────────────────────────────────────────────────────────────────
curl $BASE/agent/status
curl -X POST $BASE/agent/run \
  -H "Content-Type: application/json" \
  -d '{"mode": "once", "max_loops": 1}'

# ── HITL ─────────────────────────────────────────────────────────────────────
curl $BASE/hitl/pending
curl -X POST $BASE/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_task.md"}'
curl -X POST $BASE/hitl/reject \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_task.md", "reason": "Too risky"}'

# ── Approval ─────────────────────────────────────────────────────────────────
curl $BASE/approve/help
curl -X POST $BASE/approve/apply \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_task.md", "action": "approve"}'

# ── MCP ──────────────────────────────────────────────────────────────────────
curl $BASE/mcp/tools
curl -X POST $BASE/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "list_tasks", "arguments": {"folder": "Inbox"}}'
curl -X POST $BASE/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "read_task", "arguments": {"folder": "Inbox", "filename": "task.md"}}'

# ── Inbox ─────────────────────────────────────────────────────────────────────
curl $BASE/inbox/tasks
curl -X POST $BASE/inbox/add \
  -H "Content-Type: application/json" \
  -d '{"filename": "test-task.md", "content": "Review Q4 numbers and prepare summary."}'
```

### Router source files

| File | Prefix | Endpoints |
|------|--------|-----------|
| `backend/routers/agent.py` | `/agent` | `POST /run` · `GET /status` |
| `backend/routers/hitl.py` | `/hitl` | `GET /pending` · `POST /approve` · `POST /reject` |
| `backend/routers/approve.py` | `/approve` | `POST /apply` · `GET /help` |
| `backend/routers/mcp.py` | `/mcp` | `GET /tools` · `POST /execute` |
| `backend/routers/inbox.py` | `/inbox` | `GET /tasks` · `POST /add` |

---

## C) Cloud Deployment — Hugging Face Spaces

> **Status: not yet deployed.** Follow these steps to go live on HF Spaces.

The repo already contains all required files. No new code is needed.

### Required files (already in repo)

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds the Docker image — `python:3.11-slim`, installs deps, exposes **port 7860** |
| `requirements.txt` | All Python dependencies (`fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg2-binary`, `openai`, …) |
| `main.py` | FastAPI app entry point — `uvicorn main:app --host 0.0.0.0 --port 7860` |
| `.env.example` | Template for all required environment variables |

### Environment variables to set in HF Space

> ⚠️ **Never put real secrets in code or README.** Set them only in HF Space Settings → Repository secrets.

| Variable | Required | What it does |
|----------|----------|-------------|
| `DATABASE_URL` | **Yes** | Neon Postgres connection string — enables `/health` to return `"database": "connected"` |
| `OPENAI_API_KEY` | **Yes** | OpenAI key — required for agent AI summaries |
| `INSTAGRAM_ACCESS_TOKEN` | **Yes** | Meta/Instagram token — can be any non-empty string for demo |
| `ALLOWED_ORIGINS` | No | CORS allowed origins. Set to `*` for public Spaces or your frontend URL |

### Step-by-step deployment

**Step 1 — Create a new Space on Hugging Face**

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name:** e.g. `ai-employee-vault-gold`
   - **License:** MIT
   - **SDK:** `Docker` ← important
   - **Visibility:** Public or Private
3. Click **Create Space**

**Step 2 — Configure the Space (HF YAML frontmatter)**

HF Spaces reads the first block of `README.md` to configure the Space.
When you push to HF, your `README.md` must start with:

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

> Note: this header is for the HF Space repo only — do not add it to this GitHub repo's README.

**Step 3 — Push the code to your Space**

```bash
# Clone your new HF Space repo
git clone https://huggingface.co/spaces/<your-hf-username>/<your-space-name>
cd <your-space-name>

# Copy this project's files into the Space repo
cp -r /path/to/AI_Employee_Vault_Gold_Hackathon0/. .

# Prepend the HF YAML header to README.md (see Step 2 above)
# Edit README.md and add the --- block at the very top

# Commit and push
git add .
git commit -m "Initial deployment — Gold Cloud FastAPI on HF Spaces"
git push
```

**Step 4 — Set secrets in Space Settings**

In your HF Space:
1. Go to **Settings** tab → **Repository secrets**
2. Add each secret:
   - `DATABASE_URL` → your Neon Postgres connection string
   - `OPENAI_API_KEY` → your OpenAI API key
   - `INSTAGRAM_ACCESS_TOKEN` → your token (or any placeholder)
3. Click **Save** — the Space rebuilds automatically

**Step 5 — Wait for build and verify**

HF Spaces builds the Docker image automatically (takes ~2-3 minutes).
Watch the **Build logs** tab for:

```
Step 1/5 : FROM python:3.11-slim
...
Step 4/5 : EXPOSE 7860
Step 5/5 : CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
...
INFO:     vault | AI Employee Vault is online.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

**Step 6 — Confirm live endpoints**

Once the Space shows **Running** status, your API is live at:

```
https://<your-hf-username>-<your-space-name>.hf.space/docs
https://<your-hf-username>-<your-space-name>.hf.space/health
https://<your-hf-username>-<your-space-name>.hf.space/mcp/tools
```

### Local Docker test (before pushing to HF)

```bash
# Build the image
docker build -t vault-gold .

# Run with local .env (secrets stay in the file, not committed)
docker run -p 7860:7860 --env-file .env vault-gold

# Open:  http://localhost:7860/docs
# Health: http://localhost:7860/health
```

### How the Dockerfile works

```dockerfile
FROM python:3.11-slim          # slim Python base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # install deps
COPY . .                       # copy application code
RUN mkdir -p Inbox Needs_Action Done ...            # create vault dirs
EXPOSE 7860                    # HF Spaces requires this port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

> **Secrets safety:** `.dockerignore` excludes `.env`, `credentials.json`, `token.json`,
> `venv/`, `.git/` from the Docker image. Secrets are injected at runtime via HF Space secrets, never baked in.

---

## D) Evidence Pack — Cloud Proof

Four items that prove the Gold Tier backend is complete and running.

### Proof 1 — Swagger endpoint list

**What to check:** Open `/docs` — all 15 endpoints visible under 6 tags.

```bash
# Local
curl http://localhost:8000/docs          # opens Swagger UI

# On HF Spaces (after deployment)
curl https://<username>-<space>.hf.space/docs
```

Expected: Swagger UI loads with tags `General`, `Agent`, `HITL`, `Approval`, `MCP`, `Inbox` and all 15 routes listed and testable.

Screenshot checklist:
- [ ] `POST /agent/run` visible under **Agent** tag
- [ ] `GET /hitl/pending` visible under **HITL** tag
- [ ] `POST /mcp/execute` visible under **MCP** tag
- [ ] `POST /inbox/add` visible under **Inbox** tag

---

### Proof 2 — Health check: DB connected

**What to check:** `/health` returns `200 OK` with `"database": "connected"`.

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

Expected output:

```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "openai_key_set": true,
    "instagram_token_set": true
  }
}
```

HTTP status: `200 OK`

If you see `"database": "unavailable"`, check that `DATABASE_URL` is set correctly in `.env` (local) or in Space secrets (HF).

---

### Proof 3 — GitHub commit history

**What to check:** The commit log shows all router, Dockerfile, and README changes committed and pushed.

```bash
git log --oneline -10
```

Expected (most recent first):

```
24c3c6f Add FastAPI routers, Dockerfile, and HF Spaces deployment config
71a2ff2 Gold Agent: autonomous task processing + CEO briefing
...
485eebd Real X API v2 MCP integration
94e3999 Real Meta Graph API MCP integration
85debd2 Real Odoo JSON-RPC MCP integration
```

Public commit history:
`https://github.com/Mehreen676/AI_Employee_Vault_Gold_Hackathon0/commits/main`

Key commit to verify: **`24c3c6f`** — adds:
- `backend/routers/` (5 router files)
- `main.py` (updated router loading)
- `Dockerfile` + `.dockerignore`
- `requirements.txt` (fastapi + uvicorn added)

---

### Proof 4 — HF Spaces /docs link (after deployment)

**What to check:** The live Space serves the FastAPI app on port 7860.

After completing section C deployment:

```
https://<your-hf-username>-<your-space-name>.hf.space/docs
```

Verify:
- [ ] Page loads Swagger UI (not a 404 or build error)
- [ ] `GET /health` returns `{"status": "healthy", ...}` with `200`
- [ ] `GET /mcp/tools` returns the 3 registered tools
- [ ] Space logs show `INFO: vault | AI Employee Vault is online.`

> The Space URL pattern is: `https://<username>-<space-name>.hf.space`
> Replace hyphens in your Space name with hyphens in the URL.

---

### Generate the full evidence pack

```bash
python tools/generate_evidence_pack.py
```

Produces judge-ready files in `Evidence/`:

| File | What it proves |
|------|----------------|
| `Evidence/README.md` | Index — what to check and where |
| `Evidence/ARCHITECTURE.md` | ASCII system diagram + full data flow |
| `Evidence/PROOF_CHECKLIST.md` | 66-item checklist mapped to exact source files |
| `Evidence/SAMPLE_RUN.md` | Annotated console output + screenshot placeholders |
| `Evidence/REGISTERED_MCP_TOOLS.json` | Live dump from `mcp.registry.list_registered()` |
| `Evidence/LAST_RUN_SUMMARY.json` | Latest run_id, loops, processed, failed, db_events |
| `Evidence/ODOO_DEMO.md` | Live dry-run proof for all 3 Odoo MCP tools |

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
# Docs:   http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### 4. Drop a Task

```bash
curl -X POST http://localhost:8000/inbox/add \
  -H "Content-Type: application/json" \
  -d '{"filename": "q4-report.md", "content": "Review Q4 revenue numbers and prepare executive summary."}'
```

### 5. Run the Gold Agent

```bash
python gold_agent.py
```

---

## HITL Demo Steps

**1. Drop a sensitive task**
```bash
cat > Inbox/send-campaign.md << 'EOF'
# Q1 Email Campaign
Send email blast to all subscribers with the new product announcement.
EOF
```

**2. Run agent — it pauses on sensitive content**
```bash
python gold_agent.py
```

**3. Review + approve via API**
```bash
curl http://localhost:8000/hitl/pending
curl -X POST http://localhost:8000/hitl/approve \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_send-campaign.md"}'
```

**4. Or reject with a reason**
```bash
curl -X POST http://localhost:8000/hitl/reject \
  -H "Content-Type: application/json" \
  -d '{"filename": "hitl_20260226_120000_send-campaign.md", "reason": "Not ready for launch"}'
```

**5. Run agent again to complete**
```bash
python gold_agent.py
```

### Sensitive keyword triggers

| Keyword | Action type |
|---------|------------|
| `send email`, `email blast` | `email_send` |
| `payment`, `wire transfer`, `purchase` | `payment` |
| `publish`, `post to`, `broadcast` | `publish` |
| `deploy to prod`, `push to production`, `go-live` | `deploy` |
| `delete all`, `purge`, `drop table` | `delete` |
| `submit form`, `click confirm`, `auto-click` | `browser_action` |
| `slack message`, `webhook` | `notify_external` |

---

## Cloud Deployment (GitHub Actions)

The Gold Agent runs automatically via `.github/workflows/gold-agent.yml`:

1. Add `OPENAI_API_KEY` to repo **Settings > Secrets > Actions**
2. Add `DATABASE_URL` (Neon Postgres connection string) to repo secrets
3. Drop `.md` files into `Inbox/` and push to `main`
4. Or wait for the scheduled cron (every 10 minutes)
5. Workflow: `init_db` → `inbox_watcher --once` → `gold_agent` → commit results

---

## Demo Scenarios

| Scenario | File | Triggers | HITL? |
|---|---|---|---|
| Odoo invoice check | `Demo_Scenarios/odoo_invoice_check.md` | `odoo_list_invoices` | No — auto |
| Gmail draft demo | `Demo_Scenarios/gmail_draft_demo.md` | `draft_email` + `email_send` | Yes |
| Browser screenshot | `Demo_Scenarios/browser_screenshot_demo.md` | `browser_action` | Yes |

```bash
python tools/load_demo_task.py --list    # list all
python tools/load_demo_task.py odoo      # load + run
python gold_agent.py
```

---

## Scheduled Audit (Daily)

```bash
python scripts/run_daily_audit.py
# Output: Business/Reports/DAILY_AUDIT_<date>.md
#         Evidence/DAILY_AUDIT_<date>.json
```

---

## File Structure

```
AI_Employee_Vault_Gold_Cloud/
├── main.py                # FastAPI entry point (uvicorn main:app)
├── Dockerfile             # HF Spaces / Docker deployment (port 7860)
├── .dockerignore          # Excludes .env, venv, .git from image
├── requirements.txt       # fastapi, uvicorn[standard], sqlalchemy, openai…
├── .env.example           # Config template — copy to .env, never commit .env
│
├── backend/               # DB layer + REST API routers
│   ├── db.py              # SQLAlchemy engine + SessionLocal (Neon Postgres)
│   ├── models.py          # ORM: Task, AgentRun, Event
│   ├── init_db.py
│   └── routers/
│       ├── agent.py       # POST /agent/run  GET /agent/status
│       ├── hitl.py        # GET /hitl/pending  POST /hitl/approve|reject
│       ├── approve.py     # POST /approve/apply  GET /approve/help
│       ├── mcp.py         # GET /mcp/tools  POST /mcp/execute
│       └── inbox.py       # GET /inbox/tasks  POST /inbox/add
│
├── gold_agent.py          # Main agent (Ralph Wiggum loop)
├── hitl.py                # HITL detection + approval requests
├── approve.py             # HITL approval CLI
├── mcp_file_ops.py        # MCP Server 1: File operations
├── mcp_email_ops.py       # MCP Server 2: Email operations
├── mcp_calendar_ops.py    # MCP Server 3: Calendar/scheduling
├── mcp_audit_ops.py       # MCP Server 4: Audit queries
├── audit_logger.py        # JSON per-action logging → Logs/ + Neon DB
├── domain_router.py       # Personal/Business classifier
├── ceo_briefing.py        # Weekly CEO briefing generator
│
├── Inbox/                 # Drop tasks here
├── Needs_Action/          # Agent working queue
├── Done/                  # Completed tasks
├── Pending_Approval/      # HITL held tasks
├── Approved/              # HITL approved
├── Rejected/              # HITL rejected
├── Briefings/             # CEO briefings
├── Logs/                  # Per-action JSON audit files
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
| **Gold** | Cross-domain + 4 MCP servers + CEO briefing + audit logs + autonomous loop + **FastAPI REST API (15 endpoints)** + **HF Spaces Docker deployment** |
| **Platinum** | Gold + UI Dashboard + Metrics + RBAC + Real-time Monitoring |

---

## 🔐 Production Security

| Layer | Control |
|-------|---------|
| **Secrets management** | All API keys and DB credentials stored in HF Spaces repository secrets — never in code |
| **`.env` exclusion** | `.env` is listed in `.gitignore`; a safe `.env.example` template is committed instead |
| **Docker image hygiene** | `.dockerignore` excludes `.env`, `credentials.json`, `token.json`, `venv/`, `.git/` — secrets are injected at runtime only |
| **MCP tool whitelist** | `POST /mcp/execute` only runs tools explicitly registered in the MCP registry — unknown tool names are rejected with `400` |
| **Path traversal blocking** | MCP file operations validate all folder arguments against a hardcoded whitelist of vault folders; `../` and absolute paths are rejected |
| **HITL gate** | Tasks containing sensitive keywords (`send email`, `payment`, `deploy to prod`, `delete all`, etc.) are paused in `Pending_Approval/` and require explicit human approval before execution resumes |
| **Graceful degradation** | If `OPENAI_API_KEY` is missing or the API call fails, the agent logs the error and continues processing remaining tasks — no hard crash |

### Key files enforcing these controls

| File | What it protects |
|------|-----------------|
| `.gitignore` | Prevents `.env`, `token.json`, `credentials.json` from ever being committed |
| `.dockerignore` | Strips secrets and dev artifacts from the Docker image |
| `backend/routers/mcp.py` | Whitelist check + path traversal guard on every `/mcp/execute` call |
| `hitl.py` | Keyword scanner that intercepts sensitive actions before execution |
| `audit_logger.py` | Every action written to `/Logs` and Neon DB — full tamper-evident trail |

---

*Built for Hackathon 0 by Mehreen*
