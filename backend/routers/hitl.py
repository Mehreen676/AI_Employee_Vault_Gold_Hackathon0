"""
HITL Router — /hitl

Human-in-the-Loop approval queue management.

GET  /hitl/pending  — List hitl_*.md files waiting in Pending_Approval/
POST /hitl/approve  — Move one file to Approved/ (agent resumes task)
POST /hitl/reject   — Move one file to Rejected/ with an optional reason
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/hitl", tags=["HITL"])

# Vault root is three levels up: backend/routers/ -> backend/ -> vault root
_VAULT = Path(__file__).resolve().parent.parent.parent
_PENDING  = _VAULT / "Pending_Approval"
_APPROVED = _VAULT / "Approved"
_REJECTED = _VAULT / "Rejected"


# ── Pydantic models ───────────────────────────────────────────────────────────

class HITLItem(BaseModel):
    filename: str
    action: str
    task_file: str
    status: str


class ApproveRequest(BaseModel):
    filename: str                      # must start with hitl_


class RejectRequest(BaseModel):
    filename: str                      # must start with hitl_
    reason: Optional[str] = "No reason provided"


class HITLActionResponse(BaseModel):
    success: bool
    filename: str
    message: str


# ── Internal helpers ──────────────────────────────────────────────────────────

def _parse_frontmatter(content: str) -> dict:
    """Extract scalar key: value pairs from a YAML frontmatter block."""
    result: dict = {}
    if not content.startswith("---"):
        return result
    for line in content.split("\n")[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def _update_frontmatter_status(content: str, new_status: str, reason: str = "") -> str:
    """Replace the `status:` field in YAML frontmatter and optionally add rejection_reason."""
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


def _require_hitl_filename(filename: str) -> None:
    if not filename.startswith("hitl_"):
        raise HTTPException(
            status_code=400,
            detail="filename must start with 'hitl_' (e.g. hitl_20260226_120000_task.md)",
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/pending",
    response_model=list[HITLItem],
    summary="List pending HITL approval requests",
)
async def list_pending():
    """
    Returns every hitl_*.md file in Pending_Approval/ with parsed frontmatter.
    An empty list means no tasks are awaiting human review.
    """
    _PENDING.mkdir(parents=True, exist_ok=True)
    items: list[HITLItem] = []

    for f in sorted(_PENDING.glob("hitl_*.md")):
        try:
            meta = _parse_frontmatter(f.read_text(encoding="utf-8"))
            items.append(
                HITLItem(
                    filename=f.name,
                    action=meta.get("action", "unknown"),
                    task_file=meta.get("task_file", "unknown"),
                    status=meta.get("status", "pending_approval"),
                )
            )
        except Exception:
            items.append(
                HITLItem(
                    filename=f.name,
                    action="unknown",
                    task_file="unknown",
                    status="unreadable",
                )
            )

    return items


@router.post(
    "/approve",
    response_model=HITLActionResponse,
    summary="Approve a pending HITL request",
)
async def approve_hitl(payload: ApproveRequest):
    """
    Moves the specified hitl_*.md from Pending_Approval/ to Approved/.
    The Gold Agent will resume the original task on its next run.
    """
    _require_hitl_filename(payload.filename)

    src = _PENDING / payload.filename
    if not src.exists():
        raise HTTPException(
            status_code=404,
            detail=f"'{payload.filename}' not found in Pending_Approval/",
        )

    _APPROVED.mkdir(parents=True, exist_ok=True)
    dst = _APPROVED / payload.filename

    try:
        content = src.read_text(encoding="utf-8")
        updated = _update_frontmatter_status(content, "approved")
        dst.write_text(updated, encoding="utf-8")
        src.unlink()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Approve failed: {exc}")

    return HITLActionResponse(
        success=True,
        filename=payload.filename,
        message="Approved and moved to Approved/. Run the agent to resume the task.",
    )


@router.post(
    "/reject",
    response_model=HITLActionResponse,
    summary="Reject a pending HITL request",
)
async def reject_hitl(payload: RejectRequest):
    """
    Moves the specified hitl_*.md from Pending_Approval/ to Rejected/ and
    embeds the rejection reason in the frontmatter.
    The Gold Agent will archive the original task on its next run.
    """
    _require_hitl_filename(payload.filename)

    src = _PENDING / payload.filename
    if not src.exists():
        raise HTTPException(
            status_code=404,
            detail=f"'{payload.filename}' not found in Pending_Approval/",
        )

    _REJECTED.mkdir(parents=True, exist_ok=True)
    dst = _REJECTED / payload.filename
    reason = payload.reason or "No reason provided"

    try:
        content = src.read_text(encoding="utf-8")
        updated = _update_frontmatter_status(content, "rejected", reason=reason)
        dst.write_text(updated, encoding="utf-8")
        src.unlink()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reject failed: {exc}")

    return HITLActionResponse(
        success=True,
        filename=payload.filename,
        message=f"Rejected (reason: {reason}). Moved to Rejected/.",
    )
