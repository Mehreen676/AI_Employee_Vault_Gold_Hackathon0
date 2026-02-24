#!/usr/bin/env python3
"""
generate_gmail_token.py — One-time Gmail OAuth2 token generator.

Run this script ONCE locally to authorise the app and create token.json.
After that, the Gmail MCP server uses token.json for all API calls (auto-
refreshing as needed).  You should never need to run this script again
unless you revoke access or change the OAuth2 scopes.

Prerequisites
-------------
  1. Enable the Gmail API in your Google Cloud Console project.
  2. Create OAuth2 credentials (type: Desktop App).
  3. Download the JSON file and save it as  credentials.json  (project root).
  4. Install dependencies:
       pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  5. Run this script:
       python generate_gmail_token.py

See docs/GMAIL_SETUP.md for the full step-by-step guide.

SECURITY
--------
Both credentials.json and token.json are in .gitignore.
NEVER commit either file to version control.
Revoke access at: https://myaccount.google.com/permissions

Environment variable overrides
-------------------------------
  GMAIL_CREDENTIALS_PATH   Path to credentials JSON  (default: credentials.json)
  GMAIL_TOKEN_PATH          Path for saved token      (default: token.json)
  GMAIL_SCOPES              Comma-separated scopes    (default: compose,readonly)
"""

from __future__ import annotations

import os
import pickle
import sys
from pathlib import Path

# Default least-privilege scopes matching the Gmail MCP server tools
_SCOPES_DEFAULT: list[str] = [
    "https://www.googleapis.com/auth/gmail.compose",   # draft_email + send_email
    "https://www.googleapis.com/auth/gmail.readonly",  # search_email + read
]


def _resolve_scopes() -> list[str]:
    raw = os.getenv("GMAIL_SCOPES", "").strip()
    if raw:
        return [s.strip() for s in raw.split(",") if s.strip()]
    return _SCOPES_DEFAULT


def main() -> None:
    creds_path = Path(os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"))
    token_path = Path(os.getenv("GMAIL_TOKEN_PATH",        "token.json"))
    scopes     = _resolve_scopes()

    print()
    print("=" * 62)
    print("  Gmail OAuth2 Token Generator — AI Employee Vault Gold Tier")
    print("=" * 62)
    print(f"  credentials : {creds_path.resolve()}")
    print(f"  token path  : {token_path.resolve()}")
    print(f"  scopes      :")
    for s in scopes:
        print(f"    • {s}")
    print()

    # ── Dependency check ──────────────────────────────────────────────────────
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow   # type: ignore
        from google.auth.transport.requests import Request        # type: ignore
    except ImportError:
        print("ERROR: Google auth libraries not found.")
        print()
        print("Install them with:")
        print("  pip install google-auth google-auth-oauthlib \\")
        print("              google-auth-httplib2 google-api-python-client")
        sys.exit(1)

    # ── credentials.json check ────────────────────────────────────────────────
    if not creds_path.exists():
        print(f"ERROR: {creds_path} not found.")
        print()
        print("Steps to fix:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Select your project (or create one).")
        print("  3. APIs & Services -> Credentials -> + Create Credentials -> OAuth client ID")
        print("  4. Application type: Desktop App  ->  Create")
        print("  5. Download JSON  ->  rename the file to  credentials.json")
        print("  6. Place credentials.json in the project root, then rerun this script.")
        print()
        print("See docs/GMAIL_SETUP.md for the full guide with screenshots.")
        sys.exit(1)

    # ── Load or refresh existing token ────────────────────────────────────────
    creds = None

    if token_path.exists():
        print(f"Found existing token at {token_path} — checking validity …")
        try:
            with token_path.open("rb") as fh:
                creds = pickle.load(fh)
        except Exception as exc:
            print(f"WARNING: Could not load existing token ({exc}). Will generate a new one.")
            creds = None

    if creds and creds.expired and creds.refresh_token:
        print("Token is expired — refreshing …")
        try:
            creds.refresh(Request())
            print("Token refreshed successfully.")
        except Exception as exc:
            print(f"WARNING: Refresh failed ({exc}). Will generate a new token.")
            creds = None

    # ── Full OAuth2 consent flow (browser) ───────────────────────────────────
    if not creds or not creds.valid:
        print("Opening browser for OAuth2 consent …")
        print("(A browser window will open — sign in and grant the requested permissions.)")
        print()
        flow  = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
        creds = flow.run_local_server(port=0)

    # ── Persist the token ─────────────────────────────────────────────────────
    with token_path.open("wb") as fh:
        pickle.dump(creds, fh)

    print()
    print(f"OK  Token saved to  {token_path.resolve()}")
    print()
    print("SECURITY REMINDER")
    print("  token.json is in .gitignore — do NOT commit it.")
    print("  Revoke access: https://myaccount.google.com/permissions")
    print()
    print("Next steps")
    print("  1. Set MCP_DRY_RUN=false in .env to enable live Gmail calls.")
    print("  2. Run the agent:  python gold_agent.py")
    print("=" * 62)
    print()


if __name__ == "__main__":
    main()
