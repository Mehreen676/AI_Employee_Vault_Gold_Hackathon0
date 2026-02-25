# AI Employee Vault — Architecture Diagram

> Generated: 2026-02-25T08:26:59Z

## System Flow

```mermaid
flowchart TD
    %% Input sources
    Gmail([📧 Gmail OAuth])
    Manual([📄 Manual Drop])
    Inbox[/"📥 Inbox/"/]

    %% Watcher
    IW["inbox_watcher.py\n(YAML frontmatter)"]

    %% Agent core
    NA[/"⚙️ Needs_Action/"/]
    Agent["🤖 gold_agent.py\nRalph Wiggum Loop"]

    %% MCP Layer
    subgraph MCP["MCP Layer"]
        FileOps["mcp_file_ops\n(CRUD vault files)"]
        EmailOps["mcp_email_ops\n(classify / parse)"]
        CalOps["mcp_calendar_ops\n(schedule / priority)"]
        AuditOps["mcp_audit_ops\n(compliance queries)"]
        Stubs["stubs: gmail · odoo\nbrowser · social"]
    end

    %% HITL
    HITL{"🛑 HITL Gate\nhitl.py"}
    Pending[/"⏳ Pending_Approval/"/]
    Human(["👤 Human Review\napprove.py"])
    Approved[/"✅ Approved/"/]

    %% Processing
    OpenAI["OpenAI\nSummarize"]
    DomainRouter["domain_router.py"]

    %% Output folders
    Personal[/"🏠 Personal/"/]
    Business[/"💼 Business/"/]
    Done[/"✅ Done/"/]

    %% Output layer
    CEO["ceo_briefing.py"]
    Briefings[/"📊 Briefings/"/]
    Logs[/"🗂️ Logs/\nJSON audit trail"/]
    NeonDB[("🐘 Neon Postgres\nagent_runs · events")]
    Evidence[/"📋 Evidence/"/]

    %% ── Edges ──────────────────────────────────────
    Gmail --> Inbox
    Manual --> Inbox
    Inbox --> IW --> NA --> Agent

    Agent --> MCP
    MCP --> HITL

    HITL -- sensitive --> Pending --> Human
    Human -- approve --> Approved --> Agent
    Human -- reject --> Done

    HITL -- safe --> OpenAI --> DomainRouter
    DomainRouter --> Personal & Business --> Done

    Done --> CEO --> Briefings
    Agent --> Logs --> NeonDB
    Agent --> Evidence

    %% ── Styles ──────────────────────────────────────
    classDef folder    fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    classDef agent     fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef mcp       fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef hitl      fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef output    fill:#f3e8ff,stroke:#9333ea,color:#3b0764
    classDef external  fill:#f1f5f9,stroke:#64748b,color:#1e293b

    class Inbox,NA,Pending,Approved,Personal,Business,Done,Briefings,Logs,Evidence folder
    class Agent,IW,DomainRouter,OpenAI,CEO agent
    class FileOps,EmailOps,CalOps,AuditOps,Stubs mcp
    class HITL hitl
    class NeonDB output
    class Gmail,Manual,Human external
```

## Component Summary

| Component | File | Role |
|-----------|------|------|
| Gold Agent | `gold_agent.py` | Autonomous Ralph Wiggum loop |
| Inbox Watcher | `inbox_watcher.py` | Normalises Inbox/ → Needs_Action/ |
| MCP File Ops | `mcp_file_ops.py` | Vault CRUD (list/read/write/move/delete) |
| MCP Email Ops | `mcp_email_ops.py` | Classify sender, parse headers, draft reply |
| MCP Calendar Ops | `mcp_calendar_ops.py` | Schedule, prioritise, briefing-due check |
| MCP Audit Ops | `mcp_audit_ops.py` | Compliance queries, error log, summary |
| HITL Gate | `hitl.py` | Sensitive-keyword detection + approval flow |
| Domain Router | `domain_router.py` | Personal / Business classifier |
| CEO Briefing | `ceo_briefing.py` | Weekly executive markdown report |
| Audit Logger | `audit_logger.py` | Per-action JSON → Logs/ + Neon DB |
