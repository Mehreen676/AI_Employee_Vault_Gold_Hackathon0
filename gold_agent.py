"""
Gold Cloud Agent – Full autonomous loop with cross-domain integration.

Ralph Wiggum Loop: Agent keeps running until ALL tasks are moved to Done.
Each iteration: scan -> classify -> process -> route -> verify -> loop.
Graceful degradation: falls back if OpenAI unavailable.
Error recovery: retries failed tasks up to MAX_RETRIES before skipping.
Neon DB: writes agent_runs + events for judge-proof audit trail.
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone

# -------- OpenAI --------
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

# -------- MCP Servers --------
from mcp_file_ops import list_tasks, read_task, write_task, move_task
from mcp_calendar_ops import get_current_week, is_briefing_due
from mcp_email_ops import classify_sender
from domain_router import classify_task, route_task
from audit_logger import log_action, set_run_id, get_db_event_count
from ceo_briefing import save_briefing

# -------- Neon DB (optional) --------
_db_enabled = False
_SessionLocal = None
_AgentRun = None

try:
    from backend.db import db_available, SessionLocal
    from backend.models import AgentRun
    if db_available and SessionLocal is not None:
        _db_enabled = True
        _SessionLocal = SessionLocal
        _AgentRun = AgentRun
except Exception:
    pass

# -------- Config --------
BASE_DIR = Path(__file__).resolve().parent
INBOX = BASE_DIR / "Inbox"
NEEDS_ACTION = BASE_DIR / "Needs_Action"
DONE = BASE_DIR / "Done"
PERSONAL = BASE_DIR / "Personal"
BUSINESS = BASE_DIR / "Business"
LOGS_DIR = BASE_DIR / "Logs"
RUN_LOG = BASE_DIR / "run_log.md"
PROMPT_HISTORY = BASE_DIR / "prompt_history.md"

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_CHARS = int(os.getenv("MAX_TASK_CHARS", "6000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_LOOPS = int(os.getenv("MAX_LOOPS", "50"))  # Safety cap
LOOP_DELAY = float(os.getenv("LOOP_DELAY", "1.0"))  # Seconds between loops

AGENT_NAME = "gold_agent"


# -------- Helpers --------
def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def append_log(text: str) -> None:
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(text)


def build_prompt(task_text: str, domain: str) -> str:
    return (
        f"You are an AI employee handling a {domain} task.\n"
        "Summarize the task clearly in 3-6 bullet points.\n"
        "Then write a short 'Next actions' section (1-3 bullets).\n"
        "Keep it concise. Do NOT invent details.\n\n"
        f"TASK:\n{task_text[:MAX_CHARS]}"
    )


def openai_summarize(prompt: str) -> tuple[str, str]:
    """Call OpenAI with graceful degradation."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or OpenAI is None:
        log_action(AGENT_NAME, "openai_fallback", {"reason": "no_key_or_lib"})
        return (
            "Gold Agent processed this task. (fallback: OpenAI not configured)\n"
            "- Task has been classified and routed\n"
            "- Content preserved in original section\n"
            "- Ready for human review",
            "fallback",
        )

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=30,
        )
        text = resp.choices[0].message.content.strip()
        if not text:
            log_action(AGENT_NAME, "openai_empty", {})
            return ("Summary generated but empty response.", "openai_empty")
        log_action(AGENT_NAME, "openai_success", {"model": MODEL, "chars": len(text)})
        return (text, "openai_ok")
    except Exception as e:
        log_action(AGENT_NAME, "openai_error", {"error": str(e)}, success=False)
        return (
            f"(OpenAI error — graceful fallback)\n"
            f"- Error: {e}\n"
            "- Task preserved and classified\n"
            "- Retry or manual review recommended",
            "openai_error",
        )


# -------- Stage 1: Inbox -> Needs_Action --------
def stage_inbox() -> int:
    """Move files from Inbox/ to Needs_Action/. Returns count moved."""
    INBOX.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)

    files = list_tasks(INBOX)
    moved = 0
    for name in files:
        src = INBOX / name
        dst = NEEDS_ACTION / name
        if move_task(src, dst):
            append_log(f"{utc_ts()} - Gold Inbox: moved {name} -> Needs_Action/\n")
            moved += 1
    return moved


# -------- Stage 2: Process tasks --------
def process_task(name: str) -> bool:
    """Process a single task: read, classify, summarize, route, write to Done."""
    file_path = NEEDS_ACTION / name

    try:
        # Read
        original = read_task(file_path)
        if not original:
            log_action(AGENT_NAME, "skip_empty_task", {"name": name})
            move_task(file_path, DONE / name)
            return True

        # Classify domain
        domain = classify_task(original)

        # Build prompt and summarize
        prompt = build_prompt(original, domain)
        summary, status = openai_summarize(prompt)

        # Build output
        output = (
            "# Processed Task (Gold Tier)\n\n"
            f"**Domain:** {domain.title()}\n"
            f"**Processed:** {utc_ts()}\n"
            f"**Model:** {MODEL}\n"
            f"**Status:** {status}\n\n"
            "## Original Content\n"
            f"{original}\n\n"
            "## AI Summary\n"
            f"{summary}\n\n"
            "Status: Completed\n"
        )

        # Write to Done
        DONE.mkdir(parents=True, exist_ok=True)
        dest = DONE / name
        write_task(dest, output)

        # Also copy to domain folder for cross-domain tracking
        domain_dir = route_task(name, original, BASE_DIR)
        write_task(domain_dir / name, output)

        # Remove from Needs_Action (move_task already moved, but source file cleanup)
        if file_path.exists():
            file_path.unlink()

        # Log
        append_log(f"{utc_ts()} - Gold Processed: {name} | domain={domain} | {status}\n")

        # Prompt history
        with open(PROMPT_HISTORY, "a", encoding="utf-8") as f:
            prompt_log = "fallback" if status == "fallback" else prompt
            f.write(
                f"---\n[{utc_ts()}] FILE: {name}\n"
                f"DOMAIN: {domain}\nMODEL: {MODEL}\nSTATUS: {status}\n"
                f"PROMPT:\n{prompt_log}\n---\n\n"
            )

        log_action(AGENT_NAME, "task_completed", {
            "name": name, "domain": domain, "status": status,
        })
        return True

    except Exception as e:
        log_action(AGENT_NAME, "task_error", {
            "name": name, "error": str(e), "traceback": traceback.format_exc(),
        }, success=False)
        append_log(f"{utc_ts()} - Gold ERROR: {name} | {e}\n")
        return False


# -------- Ralph Wiggum Loop --------
def ralph_wiggum_loop() -> dict:
    """
    Autonomous completion loop.
    'I'm in danger!' — keeps processing until no tasks remain.

    Loop behavior:
    1. Move Inbox -> Needs_Action
    2. Process all tasks in Needs_Action
    3. If tasks remain (retries), loop again
    4. Stop when Needs_Action is empty or MAX_LOOPS reached
    """
    stats = {
        "loops": 0,
        "tasks_processed": 0,
        "tasks_failed": 0,
        "retries": {},
    }

    print("=== Gold Agent: Ralph Wiggum Loop Starting ===")
    print(f"    MAX_LOOPS={MAX_LOOPS}, MAX_RETRIES={MAX_RETRIES}")
    log_action(AGENT_NAME, "loop_start", {"max_loops": MAX_LOOPS, "max_retries": MAX_RETRIES})

    for loop_num in range(1, MAX_LOOPS + 1):
        stats["loops"] = loop_num
        print(f"\n--- Loop {loop_num} ---")

        # Stage 1: Inbox flush
        moved = stage_inbox()
        if moved:
            print(f"  Inbox: {moved} file(s) moved to Needs_Action")

        # Check for work
        pending = list_tasks(NEEDS_ACTION)
        if not pending:
            print("  No tasks remaining. Loop complete!")
            log_action(AGENT_NAME, "loop_complete", stats)
            break

        print(f"  Tasks pending: {len(pending)}")

        # Stage 2: Process each task
        for name in pending:
            retry_count = stats["retries"].get(name, 0)

            if retry_count >= MAX_RETRIES:
                print(f"  SKIP (max retries): {name}")
                log_action(AGENT_NAME, "max_retries_reached", {"name": name, "retries": retry_count}, success=False)
                # Move to Done with error note
                error_content = (
                    "# Failed Task (Gold Tier)\n\n"
                    f"**Error:** Max retries ({MAX_RETRIES}) exceeded\n"
                    f"**Time:** {utc_ts()}\n\n"
                    "Status: Failed\n"
                )
                write_task(DONE / name, error_content)
                src = NEEDS_ACTION / name
                if src.exists():
                    src.unlink()
                stats["tasks_failed"] += 1
                continue

            success = process_task(name)
            if success:
                stats["tasks_processed"] += 1
                print(f"  DONE: {name}")
            else:
                stats["retries"][name] = retry_count + 1
                print(f"  RETRY ({retry_count + 1}/{MAX_RETRIES}): {name}")

        # Check if everything is done
        remaining = list_tasks(NEEDS_ACTION)
        if not remaining:
            print("\n  All tasks processed!")
            log_action(AGENT_NAME, "loop_complete", stats)
            break

        # Brief pause before next loop iteration
        time.sleep(LOOP_DELAY)

    else:
        print(f"\n  MAX_LOOPS ({MAX_LOOPS}) reached. Stopping.")
        log_action(AGENT_NAME, "loop_max_reached", stats)

    return stats


# -------- DB helpers --------
def db_start_run() -> int | None:
    """Insert a new agent_runs row. Returns run_id or None."""
    if not _db_enabled or _SessionLocal is None or _AgentRun is None:
        return None
    try:
        session = _SessionLocal()
        try:
            row = _AgentRun(model=MODEL, loops=0, processed=0, failed=0)
            session.add(row)
            session.commit()
            session.refresh(row)
            run_id = row.id
            return run_id
        finally:
            session.close()
    except Exception as e:
        print(f"  [DB] start_run error: {e}")
        return None


def db_finish_run(run_id: int, stats: dict) -> None:
    """Update the agent_runs row with final stats."""
    if not _db_enabled or _SessionLocal is None or _AgentRun is None:
        return
    try:
        session = _SessionLocal()
        try:
            row = session.query(_AgentRun).filter(_AgentRun.id == run_id).first()
            if row:
                row.loops = stats.get("loops", 0)
                row.processed = stats.get("tasks_processed", 0)
                row.failed = stats.get("tasks_failed", 0)
                session.commit()
        finally:
            session.close()
    except Exception as e:
        print(f"  [DB] finish_run error: {e}")


# -------- Main --------
def main() -> None:
    print("=" * 60)
    print("  AI Employee Vault — GOLD TIER Agent")
    print("=" * 60)

    # Ensure directories exist
    for d in [INBOX, NEEDS_ACTION, DONE, PERSONAL, BUSINESS, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    if not RUN_LOG.exists():
        RUN_LOG.write_text("# Run Log (Gold Tier)\n\n", encoding="utf-8")
    if not PROMPT_HISTORY.exists():
        PROMPT_HISTORY.write_text("# Prompt History (Gold Tier)\n\n", encoding="utf-8")

    # ---- DB: start run ----
    print(f"  DB enabled: {_db_enabled}")
    run_id = db_start_run()
    if run_id is not None:
        set_run_id(run_id)
        print(f"  Inserted run_id={run_id}")
    else:
        print("  DB run_id: None (DB not available or not configured)")

    # ---- OpenAI check ----
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    print(f"  OpenAI configured: {bool(api_key and OpenAI is not None)}")
    if api_key and OpenAI is not None:
        print(f"  OpenAI model: {MODEL}")

    log_action(AGENT_NAME, "agent_start", {
        "model": MODEL,
        "max_loops": MAX_LOOPS,
        "max_retries": MAX_RETRIES,
        "db_enabled": _db_enabled,
        "run_id": run_id,
    })

    # Run the Ralph Wiggum loop
    stats = ralph_wiggum_loop()

    # CEO Briefing check
    try:
        briefing_file = save_briefing()
        print(f"\nCEO Briefing generated: {briefing_file}")
    except Exception as e:
        log_action(AGENT_NAME, "briefing_error", {"error": str(e)}, success=False)
        print(f"\nCEO Briefing skipped (error: {e})")

    # ---- DB: finish run ----
    if run_id is not None:
        db_finish_run(run_id, stats)

    db_events = get_db_event_count()

    # Final summary
    print(f"\n{'=' * 60}")
    print(f"  GOLD AGENT COMPLETE")
    print(f"  Loops: {stats['loops']}")
    print(f"  Processed: {stats['tasks_processed']}")
    print(f"  Failed: {stats['tasks_failed']}")
    print(f"  DB enabled: {_db_enabled}")
    print(f"  Inserted run_id={run_id}")
    print(f"  DB events count={db_events}")
    print(f"{'=' * 60}")

    log_action(AGENT_NAME, "agent_complete", {
        **stats,
        "db_enabled": _db_enabled,
        "run_id": run_id,
        "db_events": db_events,
    })
    append_log(
        f"{utc_ts()} - Gold Agent Complete | "
        f"loops={stats['loops']} processed={stats['tasks_processed']} "
        f"failed={stats['tasks_failed']} db={_db_enabled} run_id={run_id} "
        f"db_events={db_events}\n"
    )


if __name__ == "__main__":
    main()
