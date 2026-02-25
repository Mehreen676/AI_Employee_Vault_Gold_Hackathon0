"""
mcp/social_mcp_stub.py — Social Media MCP Stub (Gold Tier).

Cloud-simulated social media posting for Facebook, Instagram, and Twitter/X.
Provides a safe demo path with full audit logging and zero real platform calls.

Safety Design
-------------
    This stub has a permanent social_safety_gate that blocks live posting
    regardless of the MCP_DRY_RUN setting. The gate exists because:

    - Social media posts are publicly visible and irreversible.
    - Credential misuse (leaked tokens) could cause reputational damage.
    - Hackathon/demo environments should never reach live platforms.

    DRY_RUN=true  (default)   → result: dry_run_logged
    DRY_RUN=false             → result: blocked_live_mode  (safety gate fires)

    To lift the gate for production use, remove the social_safety_gate block
    and wire up the real API calls in the TODO sections below.

Registered action_types
-----------------------
    social_post_facebook    — Post text/image to a Facebook Page.
    social_post_instagram   — Post image + caption to Instagram Business.
    social_post_twitter     — Post a tweet to Twitter/X.
    social_get_analytics    — Retrieve simulated engagement analytics.

Environment variables (documented only — not read by this stub)
----------------------------------------------------------------
    FACEBOOK_PAGE_TOKEN     Meta Graph API page-level access token.
    FACEBOOK_PAGE_ID        Numeric Facebook Page ID.
    INSTAGRAM_ACCESS_TOKEN  Instagram Business account token.
    INSTAGRAM_ACCOUNT_ID    Instagram Business account ID.
    TWITTER_API_KEY         Twitter/X OAuth1.0a consumer key.
    TWITTER_API_SECRET      Twitter/X OAuth1.0a consumer secret.
    TWITTER_ACCESS_TOKEN    Twitter/X OAuth1.0a access token.
    TWITTER_ACCESS_SECRET   Twitter/X OAuth1.0a access token secret.

See docs/SOCIAL_SETUP.md for credential and live-mode upgrade instructions.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from audit_logger import log_action
from mcp.registry import register

SERVER_NAME = "social_mcp_stub"

# ── Simulated engagement data (used by social_get_analytics) ─────────────────
_SIMULATED_ANALYTICS: dict[str, dict] = {
    "facebook": {
        "followers": 4_820,
        "reach_30d": 12_400,
        "impressions_30d": 38_900,
        "engagements_30d": 1_230,
        "top_post_reach": 5_600,
    },
    "instagram": {
        "followers": 7_310,
        "reach_30d": 18_750,
        "impressions_30d": 52_100,
        "engagements_30d": 2_890,
        "top_post_reach": 9_200,
    },
    "twitter": {
        "followers": 2_140,
        "reach_30d": 8_300,
        "impressions_30d": 24_600,
        "engagements_30d": 670,
        "top_post_reach": 3_400,
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _simulated_post_id(platform: str) -> str:
    """Generate a realistic-looking simulated post ID for audit logs."""
    suffix = random.randint(10_000_000_000, 99_999_999_999)
    prefixes = {"facebook": "fb", "instagram": "ig", "twitter": "tw"}
    return f"{prefixes.get(platform, 'sm')}_{suffix}_simulated"


# ── Social safety gate ────────────────────────────────────────────────────────

def _safety_gate_blocked(action_type: str, payload: dict) -> dict:
    """
    Return a blocked_live_mode result.

    Called when DRY_RUN=false is set — the social stub never posts live.
    """
    task_file = payload.get("task_file", "unknown")
    msg = (
        f"[SAFETY GATE] Live social posting is permanently blocked in this stub. "
        f"action_type={action_type!r}, task_file={task_file!r}. "
        "To enable real posting, remove the social_safety_gate block and add "
        "real API calls. See docs/SOCIAL_SETUP.md."
    )
    log_action(SERVER_NAME, f"{action_type}_blocked_live_mode", {
        "action_type": action_type,
        "task_file": task_file,
        "reason": "social_safety_gate",
    }, success=False)
    print(f"  [{SERVER_NAME}] SAFETY GATE: live social posting blocked.")
    print(f"  [{SERVER_NAME}]   action_type: {action_type}")
    print(f"  [{SERVER_NAME}]   See docs/SOCIAL_SETUP.md for live-mode upgrade.")
    return {
        "server": SERVER_NAME,
        "action_type": action_type,
        "dry_run": False,
        "result": "blocked_live_mode",
        "message": msg,
        "timestamp": _now(),
    }


# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_social_post_facebook(payload: dict, dry_run: bool = True) -> dict:
    """
    Simulate or (safely block) a Facebook Page post.

    Expected payload keys (all optional):
        task_file   — originating task filename
        domain      — "business" or "personal"
        content     — post text / caption
        page        — target Facebook Page name or ID
        image_url   — optional image attachment URL
    """
    # ── social_safety_gate ────────────────────────────────────────────────────
    if not dry_run:
        return _safety_gate_blocked("social_post_facebook", payload)
    # ─────────────────────────────────────────────────────────────────────────

    task_file = payload.get("task_file", "unknown")
    content = payload.get("content", "<no content provided>")
    page = payload.get("page", "@AIEmployeeVault")
    sim_id = _simulated_post_id("facebook")

    result: dict = {
        "server": SERVER_NAME,
        "action_type": "social_post_facebook",
        "dry_run": True,
        "result": "dry_run_logged",
        "message": f"[DRY RUN] Would post to Facebook Page {page!r} — task: {task_file!r}",
        "simulated_post_id": sim_id,
        "timestamp": _now(),
        "intent": {
            "platform": "facebook",
            "page": page,
            "content_preview": content[:120],
            "task_file": task_file,
        },
    }
    log_action(SERVER_NAME, "social_post_facebook_dry_run", {
        "action_type": "social_post_facebook",
        "platform": "facebook",
        "page": page,
        "task_file": task_file,
        "dry_run": True,
        "simulated_post_id": sim_id,
        "note": "social_safety_gate active — live posting permanently blocked in stub.",
    })
    print(f"  [{SERVER_NAME}] DRY RUN: Would post to Facebook Page")
    print(f"  [{SERVER_NAME}]   Page:    {page}")
    print(f"  [{SERVER_NAME}]   Content: {content[:80]}...")
    print(f"  [{SERVER_NAME}]   Sim ID:  {sim_id}")
    print(f"  [{SERVER_NAME}]   -> social_safety_gate: live posting permanently blocked.")
    return result


def handle_social_post_instagram(payload: dict, dry_run: bool = True) -> dict:
    """
    Simulate or (safely block) an Instagram Business post.

    Expected payload keys (all optional):
        task_file    — originating task filename
        domain       — "business" or "personal"
        caption      — post caption text
        image_url    — image URL (required for real IG posts)
        account      — target Instagram account name
    """
    # ── social_safety_gate ────────────────────────────────────────────────────
    if not dry_run:
        return _safety_gate_blocked("social_post_instagram", payload)
    # ─────────────────────────────────────────────────────────────────────────

    task_file = payload.get("task_file", "unknown")
    caption = payload.get("caption", payload.get("content", "<no caption provided>"))
    account = payload.get("account", "@AIEmployeeVault")
    sim_id = _simulated_post_id("instagram")

    result: dict = {
        "server": SERVER_NAME,
        "action_type": "social_post_instagram",
        "dry_run": True,
        "result": "dry_run_logged",
        "message": f"[DRY RUN] Would post to Instagram account {account!r} — task: {task_file!r}",
        "simulated_post_id": sim_id,
        "timestamp": _now(),
        "intent": {
            "platform": "instagram",
            "account": account,
            "caption_preview": caption[:120],
            "task_file": task_file,
        },
    }
    log_action(SERVER_NAME, "social_post_instagram_dry_run", {
        "action_type": "social_post_instagram",
        "platform": "instagram",
        "account": account,
        "task_file": task_file,
        "dry_run": True,
        "simulated_post_id": sim_id,
        "note": "social_safety_gate active — live posting permanently blocked in stub.",
    })
    print(f"  [{SERVER_NAME}] DRY RUN: Would post to Instagram")
    print(f"  [{SERVER_NAME}]   Account: {account}")
    print(f"  [{SERVER_NAME}]   Caption: {caption[:80]}...")
    print(f"  [{SERVER_NAME}]   Sim ID:  {sim_id}")
    print(f"  [{SERVER_NAME}]   -> social_safety_gate: live posting permanently blocked.")
    return result


def handle_social_post_twitter(payload: dict, dry_run: bool = True) -> dict:
    """
    Simulate or (safely block) a Twitter/X post.

    Expected payload keys (all optional):
        task_file   — originating task filename
        domain      — "business" or "personal"
        text        — tweet text (max 280 chars for real posts)
        account     — target Twitter/X handle
    """
    # ── social_safety_gate ────────────────────────────────────────────────────
    if not dry_run:
        return _safety_gate_blocked("social_post_twitter", payload)
    # ─────────────────────────────────────────────────────────────────────────

    task_file = payload.get("task_file", "unknown")
    text = payload.get("text", payload.get("content", "<no text provided>"))
    account = payload.get("account", "@AIEmployeeVault")
    sim_id = _simulated_post_id("twitter")

    result: dict = {
        "server": SERVER_NAME,
        "action_type": "social_post_twitter",
        "dry_run": True,
        "result": "dry_run_logged",
        "message": f"[DRY RUN] Would tweet from {account!r} — task: {task_file!r}",
        "simulated_post_id": sim_id,
        "timestamp": _now(),
        "intent": {
            "platform": "twitter",
            "account": account,
            "text_preview": text[:120],
            "char_count": len(text),
            "task_file": task_file,
        },
    }
    log_action(SERVER_NAME, "social_post_twitter_dry_run", {
        "action_type": "social_post_twitter",
        "platform": "twitter",
        "account": account,
        "task_file": task_file,
        "dry_run": True,
        "simulated_post_id": sim_id,
        "note": "social_safety_gate active — live posting permanently blocked in stub.",
    })
    print(f"  [{SERVER_NAME}] DRY RUN: Would post to Twitter/X")
    print(f"  [{SERVER_NAME}]   Account: {account}")
    print(f"  [{SERVER_NAME}]   Text:    {text[:80]}...")
    print(f"  [{SERVER_NAME}]   Sim ID:  {sim_id}")
    print(f"  [{SERVER_NAME}]   -> social_safety_gate: live posting permanently blocked.")
    return result


def handle_social_get_analytics(payload: dict, dry_run: bool = True) -> dict:
    """
    Return simulated social media engagement analytics.

    Analytics are always simulated regardless of DRY_RUN — no real API calls.

    Expected payload keys (all optional):
        task_file   — originating task filename
        platform    — "facebook" | "instagram" | "twitter" | "all"
        period      — e.g. "30d", "7d", "90d"
    """
    task_file = payload.get("task_file", "unknown")
    platform = payload.get("platform", "all").lower()
    period = payload.get("period", "30d")

    if platform == "all":
        analytics = _SIMULATED_ANALYTICS.copy()
    else:
        analytics = {platform: _SIMULATED_ANALYTICS.get(platform, {})}

    result: dict = {
        "server": SERVER_NAME,
        "action_type": "social_get_analytics",
        "dry_run": dry_run,
        "result": "simulated_analytics",
        "message": f"[SIMULATED] Analytics for platform={platform!r}, period={period!r}",
        "analytics": analytics,
        "period": period,
        "timestamp": _now(),
        "note": "All metrics are simulated cloud data — no real API call made.",
    }
    log_action(SERVER_NAME, "social_get_analytics_simulated", {
        "action_type": "social_get_analytics",
        "platform": platform,
        "period": period,
        "task_file": task_file,
        "simulated": True,
    })
    print(f"  [{SERVER_NAME}] SIMULATED analytics: platform={platform!r}, period={period!r}")
    for p, data in analytics.items():
        print(f"  [{SERVER_NAME}]   {p}: followers={data.get('followers', 'n/a')}, "
              f"reach_30d={data.get('reach_30d', 'n/a')}")
    return result


# ── Self-registration (runs at import time) ───────────────────────────────────

register("social_post_facebook",  SERVER_NAME, handle_social_post_facebook)
register("social_post_instagram", SERVER_NAME, handle_social_post_instagram)
register("social_post_twitter",   SERVER_NAME, handle_social_post_twitter)
register("social_get_analytics",  SERVER_NAME, handle_social_get_analytics)
