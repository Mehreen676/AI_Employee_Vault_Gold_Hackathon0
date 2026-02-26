"""
Agent Router — /agent

Exposes control and status endpoints for the Gold Cloud Agent.

POST /agent/run    — Enqueue an agent run (stub; wire to task queue when ready)
GET  /agent/status — Return latest run stats from the DB
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["Agent"])


# ── Pydantic models ───────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    mode: str = "once"        # "once" | "loop"
    max_loops: int = 1


class RunResponse(BaseModel):
    status: str
    message: str
    triggered_at: str


class StatusResponse(BaseModel):
    status: str
    last_run_id: Optional[int]
    last_run_at: Optional[str]
    total_runs: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/run",
    response_model=RunResponse,
    summary="Trigger the Gold Agent",
    status_code=202,
)
async def run_agent(payload: RunRequest):
    """
    Accepts an agent run request.

    Production note: wire this to a task queue (Celery / ARQ / RQ) to
    execute ``gold_agent.main()`` asynchronously.  Returns HTTP 202 Accepted
    immediately so the caller is never left waiting on a long-running loop.
    """
    if payload.mode not in ("once", "loop"):
        raise HTTPException(status_code=400, detail="mode must be 'once' or 'loop'")
    if not (1 <= payload.max_loops <= 100):
        raise HTTPException(status_code=400, detail="max_loops must be between 1 and 100")

    return RunResponse(
        status="accepted",
        message=(
            f"Agent run queued (mode={payload.mode}, max_loops={payload.max_loops}). "
            "Connect a task queue (Celery/ARQ) to execute asynchronously."
        ),
        triggered_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Get latest agent run status",
)
async def agent_status():
    """
    Returns the most recent AgentRun record from the DB.
    Falls back gracefully when the DB is unavailable.
    """
    try:
        from backend.db import SessionLocal, db_available
        from backend.models import AgentRun

        if not db_available or SessionLocal is None:
            return StatusResponse(
                status="db_unavailable",
                last_run_id=None,
                last_run_at=None,
                total_runs=0,
            )

        db = SessionLocal()
        try:
            total: int = db.query(AgentRun).count()
            latest: Optional[AgentRun] = (
                db.query(AgentRun).order_by(AgentRun.id.desc()).first()
            )
            return StatusResponse(
                status="idle" if latest else "never_run",
                last_run_id=latest.id if latest else None,
                last_run_at=latest.run_ts.isoformat() if latest else None,
                total_runs=total,
            )
        finally:
            db.close()

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Status check failed: {exc}")
