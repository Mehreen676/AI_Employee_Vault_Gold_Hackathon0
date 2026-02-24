# Gmail Inbox Watcher — Setup Guide

`watchers/gmail_inbox_watcher.py` polls Gmail for unread emails and converts
each one into a Markdown task file inside `Inbox/`. Gold Agent picks them up
automatically on the next loop.

---

## Prerequisites

| Item | Notes |
|------|-------|
| Python 3.10+ | Tested on Windows 10 (PowerShell) and Ubuntu |
| Google account | The inbox you want to watch |
| Google Cloud project | Free tier is fine |
| `pip install -r requirements.txt` | `google-api-python-client`, `google-auth`, `google-auth-oauthlib` already listed |

---

## Step 1 — Enable the Gmail API

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Select an existing project **or** create a new one (top-left dropdown → **New Project**).
3. In the left sidebar go to **APIs & Services → Library**.
4. Search for **Gmail API** and click **Enable**.

---

## Step 2 — Create OAuth 2.0 Desktop Credentials

1. Go to **APIs & Services → Credentials**.
2. Click **+ Create Credentials → OAuth client ID**.
3. If prompted, configure the **OAuth consent screen** first:
   - User type: **External** (or Internal if you own the domain)
   - App name: `AI Employee Vault` (or anything you like)
   - Add your Gmail address as a **test user**
   - Save and continue through the remaining screens.
4. Back on **Create OAuth client ID**:
   - Application type: **Desktop app**
   - Name: `gmail-inbox-watcher`
   - Click **Create**
5. Click **Download JSON** on the confirmation dialog.
6. Rename the downloaded file to **`credentials.json`** and place it in the **repo root**:

```
AI_Employee_Vault_Gold_Cloud/
├── credentials.json   ← here
├── gold_agent.py
└── ...
```

> `credentials.json` is already in `.gitignore` — it will never be committed.

---

## Step 3 — Generate the OAuth Token

Run the one-time token generator (opens a browser for Google sign-in):

```powershell
# PowerShell / CMD from repo root
py generate_gmail_token.py
```

This:
1. Opens a browser tab for Google OAuth2 consent.
2. Grants `gmail.readonly` + `gmail.compose` scopes (least-privilege).
3. Saves the token as **`token.json`** in the repo root.

> `token.json` is also in `.gitignore`. Tokens auto-refresh — you only need to
> run this once (or after revoking access).

Verify it worked:
```powershell
py -c "from mcp.gmail_oauth import build_service; print(build_service())"
# Expected: <googleapiclient.discovery.Resource object at 0x...>
```

---

## Step 4 — Configure `.env`

Open `.env` (copy from `.env.example` if needed) and review these variables:

```ini
# ── Gmail Inbox Watcher ───────────────────────────────────────
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
GMAIL_USER_ID=me

# How often to poll (seconds)
GMAIL_POLL_SECONDS=10

# Which emails to ingest (Gmail search syntax)
GMAIL_QUERY=is:unread -category:promotions -category:social newer_than:7d

# Max emails processed per poll cycle
GMAIL_MAX_PER_POLL=5

# ── DRY RUN (safe default) ────────────────────────────────────
# true  = create task files, but DO NOT modify Gmail
# false = live mode (required for mark-read)
MCP_DRY_RUN=true

# Mark emails as read after creating a task (only if DRY_RUN=false)
GMAIL_MARK_READ_ON_PROCESS=false
```

For a live demo that also marks emails as read, set:
```ini
MCP_DRY_RUN=false
GMAIL_MARK_READ_ON_PROCESS=true
```

---

## Step 5 — Run the Watcher

**Option A — Windows batch script (recommended for demos):**

```cmd
scripts\run_gmail_watcher.bat
```

**Option B — Python directly:**

```powershell
# Infinite loop (local dev) — press Ctrl+C to stop
py watchers/gmail_inbox_watcher.py

# One-shot (GitHub Actions / cron)
py watchers/gmail_inbox_watcher.py --once

# Custom poll interval
py watchers/gmail_inbox_watcher.py --interval 30
```

---

## Step 6 — Run Gold Agent

In a second terminal (or after `--once` completes):

```powershell
py gold_agent.py
```

The agent will find the email task files in `Inbox/`, classify them, process
them through the full pipeline, and move them to `Done/`.

---

## State Files

| File | Purpose |
|------|---------|
| `Logs/Watchers/gmail_seen.json` | De-dupe store — message IDs already converted to tasks |
| `Logs/Watchers/gmail_watcher_YYYY-MM-DD.log` | Daily rotating log (DEBUG level to file, INFO to stdout) |

To reset the de-dupe state and re-process all matching emails:
```powershell
del Logs\Watchers\gmail_seen.json
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `GmailAuthError: No valid Gmail token` | Run `py generate_gmail_token.py` |
| `GmailAuthError: Could not load Gmail token` | Delete `token.json` and re-run token generator |
| `Google API client libraries not installed` | Run `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'base_watcher'` | Run from repo root: `py watchers/gmail_inbox_watcher.py` |
| `credentials.json not found` | Download from Google Cloud Console → Credentials (see Step 2) |
| No task files created | Check `Logs/Watchers/gmail_watcher_<date>.log`; verify query matches real emails |
| Emails re-processed after restart | `gmail_seen.json` was deleted; this is expected |

---

## Security Notes

- `credentials.json` and `token.json` are in `.gitignore` — never commit them.
- The token grants only `gmail.readonly` + `gmail.compose` scopes.
- `MCP_DRY_RUN=true` (default) means the watcher **never** modifies Gmail.
- Revoke access at any time: <https://myaccount.google.com/permissions>

---

## Judge Demo (5 Steps)

> Demonstrates a live Gmail email appearing as a Gold Agent task end-to-end.

**Step 1 — Start the watcher (DRY_RUN=true, safe mode)**

```powershell
py watchers/gmail_inbox_watcher.py
```

Expected console output:
```
==============================================================
  Gmail Inbox Watcher — AI Employee Vault Gold Tier
==============================================================
  DRY_RUN            : True
  MARK_READ          : False
  Gmail query        : is:unread -category:promotions ...
  ...
[gmail_inbox_watcher] 10:00:00 INFO: Initialised | DRY_RUN=True ...
[gmail_inbox_watcher] 10:00:01 INFO: Task created: gmail_20260224_100001_abc123.md
```

**Step 2 — Verify the task file in `Inbox/`**

```powershell
dir Inbox\
type Inbox\gmail_20260224_100001_abc123.md
```

Expected: Markdown file with YAML frontmatter (`type: email`, `source: gmail`,
`status: pending`) and the full email body.

**Step 3 — Press Ctrl+C to stop the watcher, then run Gold Agent**

```powershell
py gold_agent.py
```

**Step 4 — Confirm the task was processed**

```powershell
dir Done\
dir Business\   # or Personal\ depending on domain classification
type Done\gmail_20260224_100001_abc123.md
```

**Step 5 — Inspect the audit trail**

```powershell
dir Logs\Watchers\
type Logs\Watchers\gmail_seen.json
dir Logs\
```

- `Logs/Watchers/gmail_seen.json` — contains the processed message ID.
- `Logs/Watchers/gmail_watcher_<date>.log` — full debug log.
- `Logs/*.json` — per-action audit entries from Gold Agent.
- `Briefings/CEO_Briefing_*.md` — weekly briefing updated with email task.
