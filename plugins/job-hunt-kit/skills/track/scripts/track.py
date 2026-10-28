#!/usr/bin/env python3
"""Keep a job application log (applications.csv) and answer questions about it.

Usage:
  python track.py add applications.csv --set company=Pollen --set role="Frontend Engineer" [--set key=value ...]
  python track.py update applications.csv ID [--set key=value ...] [--followed-up]
  python track.py due applications.csv [--today YYYY-MM-DD] [--json]
  python track.py stats applications.csv [--json]
  python track.py hook        (session-start hook: reads the hook's JSON on stdin)
Exit code: 0 = ok, 2 = bad input.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

COLUMNS = [
    "id", "date_applied", "company", "role", "link", "location_terms", "ats", "resume_version",
    "inscribe_title", "tailored", "status", "response_date", "response_type", "next_step",
    "follow_up_date", "autofill_title", "autofill_jobs", "autofill_phone", "autofill_gpa", "notes",
]
REQUIRED = ["id", "date_applied", "company", "role", "status", "follow_up_date", "notes"]
STATUSES = ["applied", "screening", "interview", "offer", "rejected", "withdrawn", "ghosted"]
FOLLOW_UP_DAYS = 3
LOG_NAME = "applications.csv"
STAMP_SECONDS = 30


class BadInput(Exception):
    pass


def parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise BadInput(f"{field} must be a date like 2026-10-28, got {value!r}") from None


def read_log(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        return list(COLUMNS), []
    # utf-8-sig: logs saved from Excel start with a byte-order mark.
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        rows = [{k: (v or "") for k, v in row.items() if k is not None} for row in reader]
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        raise BadInput(f"{path} is missing columns: {', '.join(missing)}")
    return header, rows


def write_log(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_sets(pairs: list[str], header: list[str]) -> dict[str, str]:
    values = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        key = key.strip()
        if not sep or key not in header:
            raise BadInput(f"--set needs column=value with a column from the log, got {pair!r}")
        values[key] = value.strip()
    if "status" in values and values["status"] not in STATUSES:
        raise BadInput(f"status must be one of {', '.join(STATUSES)}, got {values['status']!r}")
    for field in ("date_applied", "response_date", "follow_up_date"):
        if values.get(field):
            parse_date(values[field], field)
    return values


def add(path: Path, pairs: list[str], today: date) -> dict[str, str]:
    header, rows = read_log(path)
    values = parse_sets(pairs, header)
    if not values.get("company") or not values.get("role"):
        raise BadInput("add needs at least --set company=... and --set role=...")
    if "id" in values:
        raise BadInput("id is assigned automatically")
    ids = [int(r["id"]) for r in rows if r.get("id", "").isdigit()]
    row = {c: "" for c in header}
    row.update(values)
    row["id"] = str(max(ids, default=0) + 1)
    row["date_applied"] = row["date_applied"] or today.isoformat()
    row["status"] = row["status"] or "applied"
    if not row["follow_up_date"]:
        applied = parse_date(row["date_applied"], "date_applied")
        row["follow_up_date"] = (applied + timedelta(days=FOLLOW_UP_DAYS)).isoformat()
    write_log(path, header, rows + [row])
    return row


def update(path: Path, row_id: str, pairs: list[str], followed_up: bool, today: date) -> dict[str, str]:
    header, rows = read_log(path)
    values = parse_sets(pairs, header)
    if "id" in values:
        raise BadInput("id can't be changed")
    row = next((r for r in rows if r.get("id") == row_id), None)
    if row is None:
        raise BadInput(f"no application with id {row_id} in {path}")
    row.update(values)
    if followed_up:
        row["follow_up_date"] = (today + timedelta(days=FOLLOW_UP_DAYS)).isoformat()
        note = f"followed up {today.isoformat()}"
        row["notes"] = f"{row['notes']}; {note}" if row["notes"] else note
    write_log(path, header, rows)
    return row


def follow_ups_sent(row: dict[str, str]) -> int:
    return row.get("notes", "").count("followed up ")


def due(rows: list[dict[str, str]], today: date) -> list[dict[str, str]]:
    result = []
    for row in rows:
        # Anything past "applied" has had a reply, so there is nothing to chase.
        if row.get("status") != "applied" or not row.get("follow_up_date"):
            continue
        try:
            when = date.fromisoformat(row["follow_up_date"])
        except ValueError:
            continue
        if when <= today:
            result.append(row)
    return sorted(result, key=lambda r: r["follow_up_date"])


def reached_interview(row: dict[str, str]) -> bool:
    # A rejection after an interview keeps response_type "interview", so it still counts.
    return row.get("status") in ("interview", "offer") or row.get("response_type") == "interview"


def stats(rows: list[dict[str, str]]) -> dict:
    total = len(rows)
    by_status = {s: 0 for s in STATUSES}
    for row in rows:
        by_status[row.get("status", "")] = by_status.get(row.get("status", ""), 0) + 1
    replied = sum(1 for r in rows if r.get("status") not in ("applied", "ghosted"))
    interviews = sum(1 for r in rows if reached_interview(r))
    return {
        "applications": total,
        "by_status": by_status,
        "replied": replied,
        "reply_rate": round(replied / total, 3) if total else None,
        "interviews": interviews,
        "interview_rate": round(interviews / total, 3) if total else None,
    }


def describe(row: dict[str, str], today: date) -> str:
    days = (today - date.fromisoformat(row["date_applied"])).days if row.get("date_applied") else None
    since = f"applied {row['date_applied']} ({days} days ago)" if days is not None else "date unknown"
    sent = follow_ups_sent(row)
    chased = f", followed up {sent}x" if sent else ""
    return f"#{row['id']} {row['company']}, {row['role']}: {since}{chased}"


def first_to_speak(session_id: str, stamp_dir: Path) -> bool:
    # hooks.json starts the hook under both `python3` and `python`, since either name may be the
    # real Python. Where both work, the first claims the session and the second stays silent.
    stamp = stamp_dir / f"job-hunt-kit-{''.join(c for c in session_id if c.isalnum() or c == '-')}"
    try:
        os.close(os.open(stamp, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        return True
    except FileExistsError:
        # A stamp older than a few seconds is from an earlier start (e.g. a resume); speak again.
        if time.time() - stamp.stat().st_mtime > STAMP_SECONDS:
            stamp.touch()
            return True
        return False
    except OSError:
        return True


def hook(stdin: str, today: date, stamp_dir: Path | None = None) -> str:
    """Session-start reminder. Silent unless the session's folder has a log with something due."""
    try:
        # Windows PowerShell puts a byte-order mark in front of text it pipes in.
        payload = json.loads(stdin.lstrip("﻿") or "{}")
        log = Path(payload.get("cwd") or ".") / LOG_NAME
        if not log.is_file():
            return ""
        _, rows = read_log(log)
    except (BadInput, OSError, ValueError, AttributeError):
        # A reminder isn't worth a broken session start; stay silent and let `due` report the error.
        return ""
    pending = due(rows, today)
    if not pending:
        return ""
    session_id = str(payload.get("session_id") or "")
    if session_id and not first_to_speak(session_id, stamp_dir or Path(tempfile.gettempdir())):
        return ""
    lines = [describe(r, today) for r in pending]
    summary = f"{len(pending)} job application(s) in {LOG_NAME} are due a follow-up"
    return json.dumps({
        "systemMessage": f"Job Hunt Kit: {summary}. Ask Claude to show them.",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{summary} (no reply yet, follow-up date passed):\n" + "\n".join(lines),
        },
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Keep a job application log.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="log a new application")
    p_add.add_argument("log", type=Path)
    p_add.add_argument("--set", action="append", default=[], metavar="COLUMN=VALUE")

    p_update = sub.add_parser("update", help="change an application")
    p_update.add_argument("log", type=Path)
    p_update.add_argument("id")
    p_update.add_argument("--set", action="append", default=[], metavar="COLUMN=VALUE")
    p_update.add_argument("--followed-up", action="store_true",
                          help=f"record a follow-up today and set the next one {FOLLOW_UP_DAYS} days out")

    for name in ("due", "stats"):
        p = sub.add_parser(name)
        p.add_argument("log", type=Path)
        p.add_argument("--json", action="store_true")

    sub.add_parser("hook", help="session-start hook; reads the hook JSON on stdin")

    for p in sub.choices.values():
        p.add_argument("--today", help="pretend today is this date (for testing)")

    args = parser.parse_args(argv)
    # Windows consoles can't print every character a company name might contain.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    try:
        today = parse_date(args.today, "--today") if args.today else date.today()
        if args.command == "hook":
            out = hook(sys.stdin.read(), today)
            if out:
                print(out)
            return 0
        if args.command in ("due", "stats") and not args.log.is_file():
            raise BadInput(f"no log at {args.log}")
        if args.command == "add":
            row = add(args.log, args.set, today)
            print(f"added #{row['id']} {row['company']}, {row['role']}; follow up on {row['follow_up_date']}")
        elif args.command == "update":
            row = update(args.log, args.id, args.set, args.followed_up, today)
            print(f"updated #{row['id']} {row['company']}, {row['role']}: status {row['status']}, "
                  f"follow up on {row['follow_up_date'] or 'n/a'}")
        elif args.command == "due":
            pending = due(read_log(args.log)[1], today)
            if args.json:
                print(json.dumps(pending, indent=2))
            else:
                print("\n".join(describe(r, today) for r in pending) or "nothing due")
        elif args.command == "stats":
            result = stats(read_log(args.log)[1])
            print(json.dumps(result, indent=2) if args.json else "\n".join(f"{k}: {v}" for k, v in result.items()))
    except BadInput as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
