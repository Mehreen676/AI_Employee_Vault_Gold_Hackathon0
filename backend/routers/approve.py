"""
Approve Router — /approve

Unified approval application endpoint and usage guide.

POST /approve/apply — Approve or reject a hitl_*.md (action field selects which)
GET  /approve/help  — Structured guide to the approval workflow and CLI commands
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/approve", tags=["Approval"])

_VAULT    = Path(__file__).resolve().parent.parent.parent
_PENDING  = _VAULT / "Pending_Approval"
_APPROVED = _VAULT / "Approved"
_REJECTED = _VAULT / "Rejected"


# ── Pydantic models ───────────────────────────────────────────────────────────

class ApplyRequest(BaseModel):
    filename: str
    action: str = "approve"            # "approve" | "reject"
    reason: Optional[str] = None


class ApplyResponse(BaseModel):
    success: bool
    filename: str
    action: str
    message: str


class EndpointInfo(BaseModel):
    method: str
    path: str
    description: str


class HelpResponse(BaseModel):
    description: str
    endpoints: list[EndpointInfo]
    cli_usage: list[str]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _update_status(content: str, new_status: str, reason: str = "") -> str:
    """Replace the `status:` field in YAML frontmatter; optionally inject rejection_reason."""
    lines = content.split("\n")
    result: list[str] = []
    in_front = False
    status_replaced = False

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_front = True
            result.append(line)
            continue
        if in_front and line.strip() == "---":
            if reason and new_status == "rejected":
                result.append(f'rejection_reason: "{reason}"')
            in_front = False
            result.append(line)
            continue
        if in_front and line.startswith("status:") and not status_replaced:
            result.append(f"status: {new_status}")
            status_replaced = True
            continue
        result.append(line)

    return "\n".join(result)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/apply",
    response_model=ApplyResponse,
    summary="Apply an approve or reject action to a HITL request",
)
async def apply_approval(payload: ApplyRequest):
    """
    Unified approval endpoint.

    - ``action=approve`` → moves the file to ``Approved/``
    - ``action=reject``  → moves the file to ``Rejected/`` with an optional ``reason``

    The Gold Agent will act on the file during its next scheduled run.
    """
    if not payload.filename.startswith("hitl_"):
        raise HTTPException(
            status_code=400,
            detail="filename must start with 'hitl_'",
        )
    if payload.action not in ("approve", "reject"):
        raise HTTPException(
            status_code=400,
            detail="action must be 'approve' or 'reject'",
        )

    src = _PENDING / payload.filename
    if not src.exists():
        raise HTTPException(
            status_code=404,
            detail=f"'{payload.filename}' not found in Pending_Approval/",
        )

    target_dir = _APPROVED if payload.action == "approve" else _REJECTED
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / payload.filename
    reason = payload.reason or "No reason provided"

    try:
        content = src.read_text(encoding="utf-8")
        updated = _update_status(
            content,
            new_status=payload.action,
            reason=reason if payload.action == "reject" else "",
        )
        dst.write_text(updated, encoding="utf-8")
        src.unlink()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Apply failed: {exc}")

    if payload.action == "approve":
        msg = "Approved → Approved/. Run the agent to resume the task."
    else:
        msg = f"Rejected → Rejected/ (reason: {reason}). Run the agent to archive."

    return ApplyResponse(
        success=True,
        filename=payload.filename,
        action=payload.action,
        message=msg,
    )


@router.get(
    "/help",
    response_model=HelpResponse,
    summary="Approval system usage guide",
)
async def approval_help():
    """
    Returns a structured guide describing every approval endpoint and the
    equivalent CLI commands available via ``approve.py``.
    """
    return HelpResponse(
        description=(
            "Gold Tier HITL Approval System. "
            "Sensitive tasks flagged by the agent are held in Pending_Approval/ "
            "until a human approves or rejects them via the API or CLI."
        ),
        endpoints=[
            EndpointInfo(
                method="GET",
                path="/hitl/pending",
                description="List all hitl_*.md files currently awaiting approval",
            ),
            EndpointInfo(
                method="POST",
                path="/hitl/approve",
                description="Approve a specific file — moves it to Approved/",
            ),
            EndpointInfo(
                method="POST",
                path="/hitl/reject",
                description="Reject a specific file with an optional reason — moves it to Rejected/",
            ),
            EndpointInfo(
                method="POST",
                path="/approve/apply",
                description="Unified endpoint: set action='approve' or 'reject'",
            ),
        ],
        cli_usage=[
            "python approve.py                                   # list all pending",
            "python approve.py <hitl_filename.md>               # approve one file",
            "python approve.py --all                            # approve all pending",
            "python approve.py --reject <hitl_filename.md>     # reject one file",
            "python approve.py --reject --all                  # reject all pending",
            "python approve.py --reject <file> --reason 'Too risky'",
        ],
    )
