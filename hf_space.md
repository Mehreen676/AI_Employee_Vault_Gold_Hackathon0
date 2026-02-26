# Hugging Face Spaces — Deployment Guide

> **Status: not yet deployed.**
> All required files are already in this repo. Follow the steps below to go live.

---

## Pre-flight checklist

Verify these files exist before you start:

| File | Status | What it does |
|------|--------|-------------|
| `Dockerfile` | ✅ in repo | Builds the Docker image, exposes **port 7860**, starts `uvicorn` |
| `requirements.txt` | ✅ in repo | All Python deps: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg2-binary`, `openai`, `python-dotenv` |
| `.dockerignore` | ✅ in repo | Keeps `.env`, `venv/`, `.git/` out of the image |
| `main.py` | ✅ in repo | FastAPI app — `app` object that uvicorn loads |
| `backend/routers/` | ✅ in repo | 5 router files, 15 endpoints |

---

## Step 1 — Create a Docker Space on Hugging Face

1. Go to **[huggingface.co/new-space](https://huggingface.co/new-space)**
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Owner** | your HF username |
   | **Space name** | e.g. `ai-employee-vault-gold` |
   | **License** | MIT |
   | **SDK** | **Docker** ← must be Docker, not Gradio/Streamlit |
   | **Visibility** | Public (or Private) |

3. Click **Create Space**

HF creates an empty git repo at:
```
https://huggingface.co/spaces/<your-username>/ai-employee-vault-gold
```

---

## Step 2 — Connect the repo and push the code

HF Spaces is a standard git remote. You push your code the same way as GitHub.

### Option A — Push directly from this repo

```bash
# Add HF as a second remote
cd AI_Employee_Vault_Gold_Hackathon0

git remote add hf https://huggingface.co/spaces/<your-username>/ai-employee-vault-gold

# Push main branch to HF
git push hf main
```

### Option B — Clone the Space repo and copy files in

```bash
# Clone the empty Space HF just created
git clone https://huggingface.co/spaces/<your-username>/ai-employee-vault-gold
cd ai-employee-vault-gold

# Copy all project files into the Space repo
cp -r /path/to/AI_Employee_Vault_Gold_Hackathon0/. .

# Add, commit, push
git add .
git commit -m "Initial deployment — Gold Cloud FastAPI"
git push
```

### Add the required HF YAML header to README.md in the Space

HF Spaces reads the YAML frontmatter at the top of `README.md` to configure
the Space (title, SDK, port). Add this block to the **very top** of the
`README.md` you push to HF (you do not need to add it to this GitHub repo's README):

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

> **Why `app_port: 7860`?**
> The `Dockerfile` already contains `EXPOSE 7860` and
> `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]`.
> HF Spaces routes external traffic to this port. Your local dev still uses
> `--port 8000` — nothing in `main.py` changes.

---

## Step 3 — Set environment variables in Space Settings

> ⚠️ **Never commit secrets.** Do not put real values in `.env`, `Dockerfile`, or any file in the repo.
> All secrets go in HF Space Settings only.

1. Open your Space on HF
2. Click the **Settings** tab
3. Scroll to **Repository secrets**
4. Add each variable:

| Variable | Required | Value |
|----------|----------|-------|
| `DATABASE_URL` | **Yes** | Your Neon Postgres URL, e.g. `postgresql://user:pass@host/db?sslmode=require` |
| `OPENAI_API_KEY` | **Yes** | `sk-...` from [platform.openai.com](https://platform.openai.com) |
| `INSTAGRAM_ACCESS_TOKEN` | **Yes** | Your Meta/Instagram token. Use any non-empty string as a placeholder if not using Instagram |
| `ALLOWED_ORIGINS` | No | `*` for public Spaces, or your frontend URL |

5. Click **Save** — HF rebuilds the Space automatically

---

## Step 4 — Wait for the build

Go to the **App** tab of your Space. You will see a build log. Expected output:

```
--> Building Docker image
Step 1/7 : FROM python:3.11-slim
Step 2/7 : WORKDIR /app
Step 3/7 : COPY requirements.txt .
Step 4/7 : RUN pip install --no-cache-dir -r requirements.txt
...
Step 6/7 : EXPOSE 7860
Step 7/7 : CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

--> Running
INFO:     vault | Running create_all against Neon Postgres …
INFO:     vault | Schema ready.
INFO:     vault | AI Employee Vault is online.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

The Space status dot turns **green** when the app is ready.

---

## Step 5 — Open /docs from the Space

Your Space URL follows this pattern:

```
https://<your-username>-<your-space-name>.hf.space
```

Open these URLs to verify everything works:

```bash
# Interactive Swagger UI — all 15 endpoints
https://<your-username>-<your-space-name>.hf.space/docs

# Health check — should return {"status": "healthy"}
https://<your-username>-<your-space-name>.hf.space/health

# MCP tool list
https://<your-username>-<your-space-name>.hf.space/mcp/tools

# Root
https://<your-username>-<your-space-name>.hf.space/
```

Or with curl (replace the hostname):

```bash
HF=https://<your-username>-<your-space-name>.hf.space

curl $HF/health
curl $HF/mcp/tools
curl $HF/agent/status
curl $HF/inbox/tasks
```

**Expected `/health` response when DB is connected:**

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

---

## Local Docker test (run before pushing to HF)

Verify the image builds and starts correctly on your machine first:

```bash
# Build
docker build -t vault-gold .

# Run — secrets come from your local .env file (never committed)
docker run -p 7860:7860 --env-file .env vault-gold

# Verify
curl http://localhost:7860/health
curl http://localhost:7860/docs       # open in browser
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Space shows **Build error** | Missing or broken dependency | Check HF build log for `pip install` errors |
| `/health` returns `"database": "unavailable"` | `DATABASE_URL` secret not set | Add it in Space Settings → Repository secrets |
| `/health` returns `503` | `DATABASE_URL` invalid or DB unreachable | Verify the Neon connection string is correct |
| Space shows **Runtime error** | `OPENAI_API_KEY` missing | Add it in Space Settings |
| Port error in build log | `app_port` mismatch in Space README.md | Make sure `app_port: 7860` is in the YAML header |
| `EXPOSE` missing | Old Dockerfile | Confirm `EXPOSE 7860` is in `Dockerfile` — it already is |

---

## What does NOT change for local development

| Setting | Local | HF Spaces |
|---------|-------|-----------|
| Start command | `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` | `CMD` in Dockerfile: `--port 7860` |
| Docs URL | `http://localhost:8000/docs` | `https://<space>.hf.space/docs` |
| Secrets | `.env` file (never committed) | HF Space Settings → Repository secrets |
| `main.py` | **unchanged** | **unchanged** — same file, different port at launch |

The port difference is handled entirely by the `Dockerfile` `CMD`. No code changes are needed.
