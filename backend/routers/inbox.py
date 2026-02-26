"""
Inbox Router — /inbox

Manages the Inbox/ task ingestion queue.

GET  /inbox/tasks — List all *.md files currently in Inbox/
POST /inbox/add   — Write a new task file to Inbox/ with auto-injected frontmatter
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/inbox", tags=["Inbox"])

_VAULT = Path(__file__).resolve().parent.parent.parent
_INBOX = _VAULT / "Inbox"

_SKIP_FILES = {".gitkeep", ".keep"}
_VALID_FILENAME = re.compile(r"^[\w\-. ]+\.md$")


# ── Pydantic models ───────────────────────────────────────────────────────────

class TaskItem(BaseModel):
    filename: str
    size_bytes: int
    preview: str        # first 200 characters of content


class TasksResponse(BaseModel):
    count: int
    tasks: list[TaskItem]


class AddTaskRequest(BaseModel):
    filename: str
    content: str

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.endswith(".md"):
            raise ValueError("filename must end with .md")
        if not _VALID_FILENAME.match(v):
            raise ValueError("filename contains invalid characters (use letters, digits, -, _, ., space)")
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("filename must not contain path separators")
        return v


class AddTaskResponse(BaseModel):
    success: bool
    filename: str
    path: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/tasks",
    response_model=TasksResponse,
    summary="List tasks in Inbox/",
)
async def list_inbox_tasks():
    """
    Returns all *.md files currently sitting in the ``Inbox/`` folder.

    These files have not yet been processed by the InboxWatcher.
    Once the watcher runs, they are moved to ``Needs_Action/`` with
    YAML frontmatter injected.
    """
    _INBOX.mkdir(parents=True, exist_ok=True)
    tasks: list[TaskItem] = []

    for f in sorted(_INBOX.glob("*.md")):
        if f.name in _SKIP_FILES:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            tasks.append(
                TaskItem(
                    filename=f.name,
                    size_bytes=f.stat().st_size,
                    preview=content[:200],
                )
            )
        except Exception:
            tasks.append(TaskItem(filename=f.name, size_bytes=0, preview="(unreadable)"))

    return TasksResponse(count=len(tasks), tasks=tasks)


@router.post(
    "/add",
    response_model=AddTaskResponse,
    status_code=201,
    summary="Add a new task to Inbox/",
)
async def add_inbox_task(payload: AddTaskRequest):
    """
    Writes a new *.md task file to ``Inbox/``.

    The ``InboxWatcher`` (or the ``/inbox/tasks`` route) will pick it up on
    its next scan and move it to ``Needs_Action/``.

    YAML frontmatter is automatically prepended when the content does not
    already start with ``---``.
    """
    _INBOX.mkdir(parents=True, exist_ok=True)

    dest = _INBOX / payload.filename
    if dest.exists():
        raise HTTPException(
            status_code=409,
            detail=(
                f"'{payload.filename}' already exists in Inbox/. "
                "Choose a unique filename or delete the existing file first."
            ),
        )

    content = payload.content

    # Auto-inject frontmatter when the caller has not provided it
    if not content.strip().startswith("---"):
        now = datetime.now(timezone.utc).isoformat()
        frontmatter = (
            "---\n"
            "source: api\n"
            f"ingested_at: {now}\n"
            "watcher: inbox_router\n"
            "status: pending\n"
            "---\n\n"
        )
        content = frontmatter + content

    try:
        dest.write_text(content, encoding="utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Write failed: {exc}")

    return AddTaskResponse(
        success=True,
        filename=payload.filename,
        path=f"Inbox/{payload.filename}",
        message=(
            "Task written to Inbox/. "
            "The InboxWatcher will move it to Needs_Action/ on its next scan."
        ),
    )
