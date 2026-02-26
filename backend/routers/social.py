"""
Social Router — /social

Thin API wrapper around the three social MCP stubs.

POST /social/facebook  — Post a message via SocialFacebookTool
POST /social/instagram — Post a message via SocialInstagramTool
POST /social/twitter   — Post a message via SocialTwitterTool

Never crashes: if the MCP tool import fails or raises, the endpoint
returns a structured error response rather than a 5xx.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/social", tags=["Social"])

# Vault root is three levels above this file:
# backend/routers/social.py → backend/routers/ → backend/ → vault/
_VAULT_ROOT = Path(__file__).resolve().parent.parent.parent

# Ensure vault root is on sys.path so the mcp_social_*.py modules
# can be imported without modification from within this sub-package.
if str(_VAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(_VAULT_ROOT))


# ── Pydantic models ───────────────────────────────────────────────────────────

class SocialPostRequest(BaseModel):
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/facebook",
    summary="Post a message to Facebook (stub)",
)
async def post_facebook(payload: SocialPostRequest):
    """
    Calls ``SocialFacebookTool.post_message()`` and returns the result.

    Simulates a Facebook Graph API post — no real token required.
    Returns a structured error dict (not a 5xx) if the tool fails.
    """
    try:
        from mcp_social_facebook import SocialFacebookTool
        result = SocialFacebookTool().post_message(payload.message)
    except Exception as exc:
        result = {
            "platform":  "facebook",
            "status":    "error",
            "message":   payload.message,
            "summary":   "",
            "timestamp": _now_iso(),
            "error":     str(exc),
        }
    status_code = 200 if result.get("status") == "posted" else 422
    return JSONResponse(content=result, status_code=status_code)


@router.post(
    "/instagram",
    summary="Post a message to Instagram (stub)",
)
async def post_instagram(payload: SocialPostRequest):
    """
    Calls ``SocialInstagramTool.post_message()`` and returns the result.

    Simulates a Meta Graph API post — no real token required.
    Returns a structured error dict (not a 5xx) if the tool fails.
    """
    try:
        from mcp_social_instagram import SocialInstagramTool
        result = SocialInstagramTool().post_message(payload.message)
    except Exception as exc:
        result = {
            "platform":  "instagram",
            "status":    "error",
            "message":   payload.message,
            "summary":   "",
            "timestamp": _now_iso(),
            "error":     str(exc),
        }
    status_code = 200 if result.get("status") == "posted" else 422
    return JSONResponse(content=result, status_code=status_code)


@router.post(
    "/twitter",
    summary="Post a tweet (stub)",
)
async def post_twitter(payload: SocialPostRequest):
    """
    Calls ``SocialTwitterTool.post_message()`` and returns the result.

    Simulates a Twitter API v2 tweet — enforces 280-char limit.
    Returns a structured error dict (not a 5xx) if the tool fails.
    """
    try:
        from mcp_social_twitter import SocialTwitterTool
        result = SocialTwitterTool().post_message(payload.message)
    except Exception as exc:
        result = {
            "platform":  "twitter",
            "status":    "error",
            "message":   payload.message,
            "summary":   "",
            "timestamp": _now_iso(),
            "error":     str(exc),
        }
    status_code = 200 if result.get("status") == "posted" else 422
    return JSONResponse(content=result, status_code=status_code)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
