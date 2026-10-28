"""Tests for track.py, the application log behind the track skill and its session-start hook.

Run from the repo root: python -m unittest discover tests
"""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/job-hunt-kit/skills/track/scripts/track.py"

spec = importlib.util.spec_from_file_location("track", SCRIPT)
track = importlib.util.module_from_spec(spec)
sys.modules["track"] = track
spec.loader.exec_module(track)

MON = date(2026, 10, 26)


class LogTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.log = self.dir / "applications.csv"

    def add(self, today=MON, **values):
        return track.add(self.log, [f"{k}={v}" for k, v in values.items()], today)

    def rows(self):
        return track.read_log(self.log)[1]


class Add(LogTest):
    def test_first_add_creates_the_full_header(self):
        self.add(company="Pollen Analytics", role="Frontend Engineer")
        header = self.log.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(header.split(","), track.COLUMNS)

    def test_defaults_id_date_status_and_follow_up_in_3_days(self):
        row = self.add(company="Pollen Analytics", role="Frontend Engineer")
        self.assertEqual(
            (row["id"], row["date_applied"], row["status"], row["follow_up_date"]),
            ("1", "2026-10-26", "applied", "2026-10-29"),
        )

    def test_follow_up_counts_from_the_given_apply_date(self):
        row = self.add(company="Relay", role="Engineer", date_applied="2026-10-20")
        self.assertEqual(row["follow_up_date"], "2026-10-23")

    def test_ids_increase(self):
        self.add(company="A", role="R")
        self.assertEqual(self.add(company="B", role="R")["id"], "2")

    def test_commas_and_quotes_survive_a_round_trip(self):
        self.add(company='Kranich "Mobility", GmbH', role="Senior Frontend Engineer, Web")
        self.assertEqual(self.rows()[0]["company"], 'Kranich "Mobility", GmbH')

    def test_rejects_bad_input(self):
        for values in (
            {"company": "A"},
            {"company": "A", "role": "R", "status": "maybe"},
            {"company": "A", "role": "R", "salary": "100k"},
            {"company": "A", "role": "R", "date_applied": "26/10/2026"},
            {"company": "A", "role": "R", "id": "7"},
        ):
            with self.subTest(values=values), self.assertRaises(track.BadInput):
                self.add(**values)

    def test_keeps_a_users_extra_columns(self):
        self.log.write_text(",".join(track.COLUMNS + ["salary"]) + "\n", encoding="utf-8")
        self.add(company="A", role="R", salary="100k")
        self.assertEqual(self.rows()[0]["salary"], "100k")

    def test_reads_a_log_saved_by_excel(self):
        self.log.write_text("﻿" + ",".join(track.COLUMNS) + "\n", encoding="utf-8")
        self.assertEqual(self.add(company="A", role="R")["id"], "1")

    def test_refuses_a_log_without_required_columns(self):
        self.log.write_text("company,role\nA,R\n", encoding="utf-8")
        with self.assertRaises(track.BadInput):
            self.rows()


class Update(LogTest):
    def setUp(self):
        super().setUp()
        self.add(company="Pollen Analytics", role="Frontend Engineer")

    def test_sets_status_and_response(self):
        track.update(self.log, "1", ["status=interview", "response_type=interview",
                                     "response_date=2026-10-28"], False, MON)
        self.assertEqual(self.rows()[0]["status"], "interview")

    def test_followed_up_moves_the_date_and_notes_it(self):
        row = track.update(self.log, "1", [], True, date(2026, 10, 30))
        self.assertEqual(row["follow_up_date"], "2026-11-02")
        self.assertEqual(row["notes"], "followed up 2026-10-30")
        row = track.update(self.log, "1", [], True, date(2026, 11, 2))
        self.assertEqual(track.follow_ups_sent(row), 2)

    def test_unknown_id(self):
        with self.assertRaises(track.BadInput):
            track.update(self.log, "9", ["status=offer"], False, MON)


class Due(LogTest):
    def test_only_unanswered_applications_past_their_date(self):
        self.add(company="Due today", role="R", date_applied="2026-10-23")
        self.add(company="Overdue", role="R", date_applied="2026-10-01")
        self.add(company="Not yet", role="R", date_applied="2026-10-25")
        self.add(company="Replied", role="R", date_applied="2026-10-01", status="screening")
        self.add(company="Ghosted", role="R", date_applied="2026-10-01", status="ghosted")
        names = [r["company"] for r in track.due(self.rows(), MON)]
        self.assertEqual(names, ["Overdue", "Due today"])

    def test_skips_a_hand_edited_bad_date(self):
        self.add(company="A", role="R")
        rows = self.rows()
        rows[0]["follow_up_date"] = "soon"
        self.assertEqual(track.due(rows, MON), [])


class Stats(LogTest):
    def test_rates(self):
        self.add(company="A", role="R")
        self.add(company="B", role="R", status="interview")
        self.add(company="C", role="R", status="rejected", response_type="interview")
        self.add(company="D", role="R", status="rejected", response_type="rejection")
        result = track.stats(self.rows())
        self.assertEqual((result["applications"], result["replied"], result["interviews"]), (4, 3, 2))
        self.assertEqual(result["interview_rate"], 0.5)

    def test_empty_log(self):
        self.assertIsNone(track.stats([])["interview_rate"])


class Hook(LogTest):
    def run_hook(self, payload=None, today=MON):
        return track.hook(json.dumps(payload or {"cwd": str(self.dir)}), today)

    def test_silent_without_a_log(self):
        self.assertEqual(self.run_hook(), "")

    def test_silent_when_nothing_is_due(self):
        self.add(company="A", role="R")
        self.assertEqual(self.run_hook(), "")

    def test_reminds_when_something_is_due(self):
        self.add(company="Pollen Analytics", role="Frontend Engineer", date_applied="2026-10-20")
        out = json.loads(self.run_hook())
        self.assertIn("1 job application", out["systemMessage"])
        context = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Pollen Analytics", context)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_accepts_input_piped_by_windows_powershell(self):
        self.add(company="A", role="R", date_applied="2026-10-20")
        self.assertIn("systemMessage", track.hook("﻿" + json.dumps({"cwd": str(self.dir)}), MON))

    def test_silent_on_bad_input(self):
        self.log.write_text("company,role\nA,R\n", encoding="utf-8")
        self.assertEqual(self.run_hook(), "")
        self.assertEqual(track.hook("not json", MON), "")


class Cli(LogTest):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = track.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_add_then_due(self):
        log = str(self.log)
        code, out, _ = self.run_main("add", log, "--set", "company=Relay", "--set", "role=Engineer",
                                     "--today", "2026-10-20")
        self.assertEqual(code, 0, out)
        self.assertIn("follow up on 2026-10-23", out)
        code, out, _ = self.run_main("due", log, "--today", "2026-10-26")
        self.assertIn("#1 Relay, Engineer: applied 2026-10-20 (6 days ago)", out)

    def test_bad_input_exits_2(self):
        code, _, err = self.run_main("add", str(self.log), "--set", "company=A")
        self.assertEqual(code, 2)
        self.assertIn("error:", err)

    def test_due_without_a_log_exits_2(self):
        self.assertEqual(self.run_main("due", str(self.log))[0], 2)


if __name__ == "__main__":
    unittest.main()
