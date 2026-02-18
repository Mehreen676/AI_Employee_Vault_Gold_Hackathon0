"""
Gold Tier Audit Logger – JSON-per-action logging to /Logs.

Every MCP tool call, agent decision, and error is logged as a separate
JSON file in /Logs with timestamp, server, action, details, and success status.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "Logs"


def log_action(
    server: str,
    action: str,
    details: dict | None = None,
    success: bool = True,
) -> str:
    """Write one JSON audit log entry to /Logs. Returns the log filename."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    log_id = uuid.uuid4().hex[:12]
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{log_id}.json"

    entry = {
        "id": log_id,
        "timestamp": now.isoformat(),
        "server": server,
        "action": action,
        "details": details or {},
        "success": success,
    }

    log_path = LOGS_DIR / filename
    try:
        log_path.write_text(json.dumps(entry, indent=2, default=str), encoding="utf-8")
    except Exception:
        # Last resort: print to stdout so we never crash on logging
        print(f"[AUDIT FALLBACK] {json.dumps(entry, default=str)}")

    return filename
