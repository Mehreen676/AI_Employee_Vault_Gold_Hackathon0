"""
mcp/registry.py — MCP Tool Registry for Gold Tier.

Central in-process registry that maps action_type strings to handler functions.
Stubs self-register on import by calling register().

DRY_RUN (default True)
    True  → stubs log intent only; no real external actions taken.
    False → stubs attempt real implementations (most are still placeholders).

    Override at runtime:
        export MCP_DRY_RUN=false          # bash / GitHub Actions secret
        $env:MCP_DRY_RUN = "false"        # PowerShell
"""

from __future__ import annotations

import os
from typing import Callable

# ── DRY_RUN flag (read once at import time) ───────────────────────────────────
DRY_RUN: bool = os.getenv("MCP_DRY_RUN", "true").lower() != "false"

# ── Registry store ─────────────────────────────────────────────────────────────
# Maps action_type → (server_name, handler_callable)
_REGISTRY: dict[str, tuple[str, Callable]] = {}


def register(action_type: str, server_name: str, handler: Callable) -> None:
    """
    Register a handler for the given action_type.

    Called at module import time by each MCP stub.
    Later registrations silently overwrite earlier ones (last-writer wins),
    which lets gmail_mcp_server override the email_mcp_stub alias for
    send_email / draft_email.

    Args:
        action_type:  String key, e.g. "email_send", "publish", "payment".
        server_name:  Human-readable server label, e.g. "email_mcp_stub".
        handler:      Callable with signature handler(payload: dict, dry_run: bool) -> dict.
    """
    _REGISTRY[action_type] = (server_name, handler)


def get_handler(action_type: str) -> Callable | None:
    """
    Return the registered handler for action_type, or None if not found.

    Args:
        action_type:  String key to look up.

    Returns:
        handler callable, or None.
    """
    entry = _REGISTRY.get(action_type)
    return entry[1] if entry else None


def list_registered() -> dict[str, str]:
    """
    Return a snapshot of all registered action_types → server_name mappings.

    Returns:
        dict mapping action_type → server_name.
    """
    return {action_type: server_name for action_type, (server_name, _) in _REGISTRY.items()}
