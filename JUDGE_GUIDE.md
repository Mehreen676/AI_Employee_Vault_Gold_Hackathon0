# 🏆 AI Employee Vault — Gold Tier Judge Guide

This document helps judges quickly validate all Gold requirements.

## ✅ 1. System Overview

- Autonomous Agent Loop (Ralph Wiggum loop)
- MCP multi-tool architecture
- JSON audit logging
- Social integrations (FB, IG, Twitter)
- Accounting integration (Xero stub)
- Prometheus metrics endpoint
- Dashboard preview
- HuggingFace deployment

## 🔁 2. How to Test Autonomous Agent

1. Run watcher / agent
2. Add task in Inbox/
3. Observe Needs_Action/
4. Final output in Done/
5. Check run_log.md and Logs/

## 🌐 3. How to Test Social Integration

Example:

```bash
curl -X POST http://localhost:8000/social/facebook \
  -H "Content-Type: application/json" \
  -d '{"message":"Test post from judge"}'
```

Check:
- JSON response
- Logs/social_facebook.json
- Evidence/SOCIAL_FACEBOOK_SUMMARY.json

## 💰 4. How to Test Accounting (Xero Stub)

```bash
curl -X POST http://localhost:8000/accounting/invoice \
  -H "Content-Type: application/json" \
  -d '{"customer":"Judge Corp","amount":500}'
```

Check:
- JSON response
- Logs/accounting.json

## 📈 5. Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

Sample:

```
vault_agent_runs_total 0
vault_tasks_processed_total 0
vault_hitl_pending_total 0
vault_mcp_tools_registered_total 4
vault_errors_total 0
vault_uptime_seconds 123
```

## 📂 6. Where to See Logs

- Logs/
- Evidence/
- run_log.md

## 🖥 7. Dashboard Preview

Open:

```
dashboard/index.html
```

## ☁ 8. Cloud Deployment

- HuggingFace Spaces
- Docker
- GitHub Actions
