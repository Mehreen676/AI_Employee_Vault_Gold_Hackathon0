#!/usr/bin/env python3
"""
browser_demo.py — Safe Playwright browser demo (example.com only).

This demo always passes dry_run=False directly to the Playwright browser
server handlers, bypassing the MCP_DRY_RUN env var, so you can see a real
browser session run even in a dry-run agent environment.

What it does
------------
  Step 1 — open_url   -> https://example.com
  Step 2 — screenshot -> Screenshots/demo_example_com.png

Only ever contacts https://example.com — the IANA-reserved safe demo domain.
No logins, no form submissions, no real data.

Requirements
------------
    pip install playwright
    python -m playwright install chromium

Usage
-----
    python browser_demo.py                    # headless (default)
    PLAYWRIGHT_HEADLESS=false python browser_demo.py   # headed (watch it!)
    PLAYWRIGHT_BROWSER=firefox python browser_demo.py  # use firefox
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

DEMO_URL = "https://example.com"
DEMO_SCREENSHOT_FILENAME = "demo_example_com.png"
SCREENSHOT_DIR = Path(os.getenv("PLAYWRIGHT_SCREENSHOT_DIR", "Screenshots"))


def _check_playwright() -> bool:
    """Return True if playwright is importable; print a helpful error if not."""
    try:
        import playwright  # type: ignore  # noqa: F401
        return True
    except ImportError:
        print()
        print("ERROR: Playwright is not installed.")
        print()
        print("Install it with:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")
        print()
        print("See docs/BROWSER_SETUP.md for the full guide.")
        return False


def _browser_config() -> dict:
    return {
        "browser":    os.getenv("PLAYWRIGHT_BROWSER",  "chromium").lower(),
        "headless":   os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() != "false",
        "timeout_ms": int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000")),
        "slow_mo":    int(os.getenv("PLAYWRIGHT_SLOW_MO_MS",  "0")),
    }


def _sep(char: str = "─", width: int = 62) -> str:
    return char * width


def run_demo() -> bool:
    """
    Run the two-step demo. Returns True on full success, False on any error.
    """
    print()
    print(_sep("═"))
    print("  AI Employee Vault — Browser MCP Demo")
    print("  Target: https://example.com  (IANA safe demo domain)")
    print(_sep("═"))

    if not _check_playwright():
        return False

    from playwright.sync_api import sync_playwright  # type: ignore

    cfg = _browser_config()
    print(f"  browser   : {cfg['browser']}")
    print(f"  headless  : {cfg['headless']}")
    print(f"  timeout   : {cfg['timeout_ms']} ms")
    print()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = SCREENSHOT_DIR / DEMO_SCREENSHOT_FILENAME
    success = False

    pw = sync_playwright().start()
    browser = None
    try:
        # ── Step 1: open_url ──────────────────────────────────────────────────
        print(_sep())
        print("  STEP 1 — open_url")
        print(_sep())

        launcher = getattr(pw, cfg["browser"], pw.chromium)
        browser  = launcher.launch(headless=cfg["headless"], slow_mo=cfg["slow_mo"])
        ctx      = browser.new_context()
        ctx.set_default_timeout(cfg["timeout_ms"])
        page     = ctx.new_page()

        print(f"  Navigating to: {DEMO_URL}")
        page.goto(DEMO_URL, wait_until="load")

        final_url = page.url
        title     = page.title()
        print(f"  [OK] Loaded — title: {title!r}")
        print(f"     Final URL: {final_url}")

        # ── Step 2: screenshot ────────────────────────────────────────────────
        print()
        print(_sep())
        print("  STEP 2 — screenshot")
        print(_sep())
        print(f"  Capturing full-page PNG -> {screenshot_path}")

        page.screenshot(path=str(screenshot_path), full_page=True)

        file_size = screenshot_path.stat().st_size if screenshot_path.exists() else 0
        print(f"  [OK] Screenshot saved: {screenshot_path.resolve()}")
        print(f"     File size: {file_size:,} bytes")

        success = True

    except Exception as exc:
        print(f"  [FAIL] Demo failed: {exc}")
        success = False
    finally:
        if browser:
            browser.close()
        pw.stop()

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(_sep("═"))
    if success:
        print("  DEMO COMPLETE [OK]")
        print(f"  Screenshot: {screenshot_path.resolve()}")
        print()
        print("  Next steps:")
        print("  1. Set MCP_DRY_RUN=false in .env to enable live browser tools.")
        print("  2. Dispatch 'open_url' or 'screenshot' via the MCP router:")
        print("       from mcp.router import dispatch_action")
        print("       dispatch_action('screenshot', {'url': 'https://example.com'})")
        print("  3. See docs/BROWSER_SETUP.md for full integration guide.")
    else:
        print("  DEMO FAILED [FAIL]")
        print("  See error above. Check docs/BROWSER_SETUP.md for troubleshooting.")
    print(_sep("═"))
    print()
    return success


if __name__ == "__main__":
    ok = run_demo()
    sys.exit(0 if ok else 1)
