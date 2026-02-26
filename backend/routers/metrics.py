"""
Metrics Router — /metrics

Returns a Prometheus-style plain-text metrics snapshot.
Safe to call at any time: DB failures degrade gracefully to 0 values.

GET /metrics
"""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["General"])

# Captured once at import time — uptime is relative to process start.
_PROCESS_START: float = time.monotonic()

# Vault root (three levels up from this file: routers/ → backend/ → vault/)
_VAULT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers — each returns a plain int, never raises
# ---------------------------------------------------------------------------

def _db_metrics() -> dict[str, int]:
    """Query Neon Postgres for live counters. Returns zeros on any failure."""
    try:
        from backend.db import SessionLocal, db_available
        from backend.models import AgentRun

        if not db_available or SessionLocal is None:
            return {"runs": 0, "processed": 0, "errors": 0}

        with SessionLocal() as session:
            from sqlalchemy import func as sa_func

            row = session.query(
                sa_func.count(AgentRun.id).label("runs"),
                sa_func.coalesce(sa_func.sum(AgentRun.processed), 0).label("processed"),
                sa_func.coalesce(sa_func.sum(AgentRun.failed), 0).label("errors"),
            ).one()

            return {
                "runs":      int(row.runs),
                "processed": int(row.processed),
                "errors":    int(row.errors),
            }
    except Exception:
        return {"runs": 0, "processed": 0, "errors": 0}


def _hitl_pending() -> int:
    """Count *.md files in Pending_Approval/ — filesystem only, no DB needed."""
    try:
        folder = _VAULT / "Pending_Approval"
        if not folder.is_dir():
            return 0
        return sum(1 for f in folder.glob("*.md") if f.name not in {".gitkeep", ".keep"})
    except Exception:
        return 0


def _mcp_servers() -> int:
    """Count mcp_*.py server modules in the vault root."""
    try:
        return sum(1 for _ in _VAULT.glob("mcp_*.py"))
    except Exception:
        return 4  # known value, safe fallback


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus-style metrics",
    description=(
        "Returns a plain-text snapshot of key vault counters in Prometheus "
        "exposition format. DB failures degrade gracefully — counters fall "
        "back to 0 rather than returning a 5xx."
    ),
)
async def metrics() -> PlainTextResponse:
    db  = _db_metrics()
    now = time.monotonic()

    lines = [
        "# HELP vault_agent_runs_total Total number of Gold Agent executions recorded in DB",
        "# TYPE vault_agent_runs_total counter",
        f"vault_agent_runs_total {db['runs']}",
        "",
        "# HELP vault_tasks_processed_total Cumulative tasks processed across all agent runs",
        "# TYPE vault_tasks_processed_total counter",
        f"vault_tasks_processed_total {db['processed']}",
        "",
        "# HELP vault_hitl_pending_total Tasks currently waiting in Pending_Approval/",
        "# TYPE vault_hitl_pending_total gauge",
        f"vault_hitl_pending_total {_hitl_pending()}",
        "",
        "# HELP vault_mcp_servers_total Number of MCP server modules in vault root",
        "# TYPE vault_mcp_servers_total gauge",
        f"vault_mcp_servers_total {_mcp_servers()}",
        "",
        "# HELP vault_errors_total Cumulative failed tasks across all agent runs",
        "# TYPE vault_errors_total counter",
        f"vault_errors_total {db['errors']}",
        "",
        "# HELP vault_uptime_seconds Seconds since the FastAPI process started",
        "# TYPE vault_uptime_seconds gauge",
        f"vault_uptime_seconds {now - _PROCESS_START:.2f}",
        "",
    ]

    return PlainTextResponse(
        content="\n".join(lines),
        media_type="text/plain; charset=utf-8",
    )
