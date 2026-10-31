"""Tests for the resume template that converted resumes are poured into.
Run from the repo root: python -m unittest discover tests"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/uncooked/skills/ats-optimize"
TEMPLATE = (SKILL / "references/resume-template.tex").read_text(encoding="utf-8")
JANE = (ROOT / "fixtures/jane-doe/resume.tex").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("check_layout", SKILL / "scripts/check_layout.py")
check_layout = importlib.util.module_from_spec(spec)
sys.modules["check_layout"] = check_layout
spec.loader.exec_module(check_layout)


def without_comments(tex):
    return "\n".join(line for line in check_layout.strip_comments(tex).splitlines() if line.strip())


def preamble(tex):
    return without_comments(tex).split("\\begin{document}")[0].strip()


def body(tex):
    return without_comments(tex).split("\\begin{document}", 1)[1]


class Template(unittest.TestCase):
    def test_is_jane_does_layout(self):
        # Jane's resume is the layout the research rules were tested on.
        self.assertEqual(preamble(TEMPLATE), preamble(JANE))

    def test_passes_every_layout_rule(self):
        statuses = {r.rule: r.status for r in check_layout.run_checks(TEMPLATE)}
        self.assertEqual({rule for rule, status in statuses.items() if status != "pass"}, {"R5"})

    def test_braces_balance(self):
        text = body(TEMPLATE).replace("\\{", "").replace("\\}", "")
        depth = 0
        for ch in text:
            depth += {"{": 1, "}": -1}.get(ch, 0)
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)

    def test_no_square_brackets_in_body(self):
        # After \\ or \item, LaTeX reads [..] as an option, not text.
        self.assertNotRegex(body(TEMPLATE), r"\[")

    def test_has_no_jane_doe_details(self):
        for detail in ("Jane", "Brightleaf", "Kilima", "Nairobi", "+254"):
            self.assertNotIn(detail, TEMPLATE)

    def test_placeholders_cover_every_block(self):
        found = set(re.findall(r"\{\{([^{}]+)\}\}", TEMPLATE))
        for needed in ("FULL NAME", "Company", "Job Title", "Bullet, word for word.", "School", "Degree"):
            self.assertIn(needed, found)


if __name__ == "__main__":
    unittest.main()
