"""
MCP Router — /mcp

Exposes the vault's MCP-style tool registry and a safe execution interface.

GET  /mcp/tools   — List all registered tools with their input schemas
POST /mcp/execute — Execute a whitelisted tool against the vault filesystem
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/mcp", tags=["MCP"])

_VAULT = Path(__file__).resolve().parent.parent.parent

# Only these folders may be read from or written to via the API
_ALLOWED_FOLDERS: frozenset[str] = frozenset({
    "Inbox",
    "Needs_Action",
    "Done",
    "Pending_Approval",
    "Approved",
    "Rejected",
    "Failed_Tasks",
})


# ── Pydantic models ───────────────────────────────────────────────────────────

class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: dict


class ToolsResponse(BaseModel):
    count: int
    tools: list[MCPTool]


class ExecuteRequest(BaseModel):
    tool: str
    arguments: dict = {}


class ExecuteResponse(BaseModel):
    tool: str
    success: bool
    result: Any
    message: str


# ── Tool registry ─────────────────────────────────────────────────────────────

_TOOLS: list[MCPTool] = [
    MCPTool(
        name="list_tasks",
        description="List all *.md task files inside a vault folder.",
        input_schema={
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Folder name relative to vault root.",
                    "enum": sorted(_ALLOWED_FOLDERS),
                },
            },
            "required": ["folder"],
        },
    ),
    MCPTool(
        name="read_task",
        description="Read the full content of a *.md task file.",
        input_schema={
            "type": "object",
            "properties": {
                "folder":   {"type": "string", "description": "Source folder name."},
                "filename": {"type": "string", "description": "Filename ending in .md."},
            },
            "required": ["folder", "filename"],
        },
    ),
    MCPTool(
        name="move_task",
        description="Move a *.md task file from one vault folder to another.",
        input_schema={
            "type": "object",
            "properties": {
                "filename":    {"type": "string", "description": "Filename ending in .md."},
                "from_folder": {"type": "string", "description": "Source folder name."},
                "to_folder":   {"type": "string", "description": "Destination folder name."},
            },
            "required": ["filename", "from_folder", "to_folder"],
        },
    ),
]


# ── Internal guards ───────────────────────────────────────────────────────────

def _safe_filename(filename: str) -> None:
    """Reject filenames that could escape the vault root."""
    if not filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="filename must end with .md")
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="filename contains invalid path characters")


def _safe_folder(folder: str) -> None:
    if folder not in _ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Folder '{folder}' is not allowed. Allowed: {sorted(_ALLOWED_FOLDERS)}",
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/tools",
    response_model=ToolsResponse,
    summary="List available MCP tools",
)
async def list_tools():
    """Returns all registered MCP tools with their names, descriptions, and input schemas."""
    return ToolsResponse(count=len(_TOOLS), tools=_TOOLS)


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    summary="Execute an MCP tool",
)
async def execute_tool(payload: ExecuteRequest):
    """
    Execute one of the registered MCP tools.

    Only whitelisted tools and vault folders are permitted.
    Filenames are validated to prevent path traversal.

    **list_tasks** — ``{"folder": "Inbox"}``

    **read_task**  — ``{"folder": "Inbox", "filename": "task_001.md"}``

    **move_task**  — ``{"filename": "task_001.md", "from_folder": "Inbox", "to_folder": "Needs_Action"}``
    """
    tool = payload.tool
    args = payload.arguments

    # ── list_tasks ────────────────────────────────────────────────────────────
    if tool == "list_tasks":
        folder = args.get("folder", "")
        _safe_folder(folder)

        folder_path = _VAULT / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        files = sorted(
            f.name
            for f in folder_path.glob("*.md")
            if f.name not in {".gitkeep", ".keep"}
        )
        return ExecuteResponse(
            tool=tool,
            success=True,
            result=files,
            message=f"{len(files)} file(s) in {folder}/",
        )

    # ── read_task ─────────────────────────────────────────────────────────────
    elif tool == "read_task":
        folder   = args.get("folder", "")
        filename = args.get("filename", "")
        _safe_folder(folder)
        _safe_filename(filename)

        file_path = _VAULT / folder / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"'{filename}' not found in {folder}/",
            )

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return ExecuteResponse(
            tool=tool,
            success=True,
            result=content,
            message=f"Read '{filename}' from {folder}/",
        )

    # ── move_task ─────────────────────────────────────────────────────────────
    elif tool == "move_task":
        filename    = args.get("filename", "")
        from_folder = args.get("from_folder", "")
        to_folder   = args.get("to_folder", "")
        _safe_filename(filename)
        _safe_folder(from_folder)
        _safe_folder(to_folder)

        src = _VAULT / from_folder / filename
        if not src.exists():
            raise HTTPException(
                status_code=404,
                detail=f"'{filename}' not found in {from_folder}/",
            )

        dst_dir = _VAULT / to_folder
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / filename

        try:
            shutil.move(str(src), str(dst))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Move failed: {exc}")

        return ExecuteResponse(
            tool=tool,
            success=True,
            result={"moved_to": f"{to_folder}/{filename}"},
            message=f"Moved '{filename}' from {from_folder}/ to {to_folder}/",
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool: '{tool}'. Call GET /mcp/tools for the full list.",
        )
