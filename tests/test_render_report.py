"""Tests for render_report.py. Run from the repo root: python -m unittest discover tests"""
import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/uncooked/skills/ats-optimize/scripts/render_report.py"

spec = importlib.util.spec_from_file_location("render_report", SCRIPT)
render_report = importlib.util.module_from_spec(spec)
sys.modules["render_report"] = render_report
spec.loader.exec_module(render_report)

REPORT = """# Frontend Engineer at Pollen Analytics

## Verdict
A **strong** match. The biggest risk is `TypeScript` years.

## Knockouts
| Requirement | Profile says | Status |
| --- | --- | --- |
| Remote EMEA | Kenyan citizen | **Unclear**: ask the recruiter |
| 3+ years TypeScript | Since Mar 2024 | **Not met as full-time (short by about 5 months).** |
| English | Fluent | Met |

## Requirements
| Requirement | Required / nice | Status | Fact IDs | Change made |
| --- | --- | --- | --- | --- |
| Storybook | required | present / partial | BL-3 | Gap closed by rewording |
| GraphQL | nice | gap | | none |

## Changes
- Moved freelance into Experience (FR-1)
- Reordered bullets
  so Storybook comes first (BL-3)
"""


def body(markdown):
    return render_report.render(markdown)[0]


class Render(unittest.TestCase):
    def setUp(self):
        self.html, self.title = render_report.render(REPORT)

    def test_title_and_headings(self):
        self.assertEqual(self.title, "Frontend Engineer at Pollen Analytics")
        self.assertIn("<h2>Knockouts</h2>", self.html)

    def test_inline_formatting(self):
        self.assertIn("A <strong>strong</strong> match", self.html)
        self.assertIn("<code>TypeScript</code>", self.html)

    def test_status_labels(self):
        self.assertIn('<span class="badge warn">Unclear</span> ask the recruiter', self.html)
        self.assertIn('<span class="badge good">Met</span>', self.html)
        self.assertIn('<span class="badge bad">gap</span>', self.html)

    def test_not_met_is_not_read_as_met_and_keeps_its_bold(self):
        self.assertIn('<span class="badge bad">Not met</span> <strong>as full-time', self.html)

    def test_two_statuses_in_one_cell(self):
        self.assertIn('<span class="badge good">present</span> <span class="badge warn">partial</span>', self.html)

    def test_verdict_is_highlighted(self):
        self.assertIn('<h2>Verdict</h2>\n<section class="verdict">\n<p>A <strong>strong</strong>', self.html)
        self.assertIn("</section>\n<h2>Knockouts</h2>", self.html)

    def test_plain_language_statuses(self):
        table = "| Requirement | Status |\n| --- | --- |\n"
        rows = ["On resume", "Reworded", "Moved higher", "Added from facts", "Partial match", "Missing"]
        html = body(table + "\n".join(f"| x | {r} |" for r in rows))
        for row, kind in zip(rows, ["good", "info", "info", "info", "warn", "bad"]):
            self.assertIn(f'<span class="badge {kind}">{row}</span>', html)

    def test_status_words_outside_status_columns_stay_text(self):
        self.assertIn("<td>Gap closed by rewording</td>", self.html)

    def test_list_with_wrapped_item(self):
        self.assertIn("<li>Reordered bullets so Storybook comes first (BL-3)</li>", self.html)

    def test_html_in_the_report_is_escaped(self):
        self.assertIn("&lt;script&gt;", body("Posting said <script>alert(1)</script>"))

    def test_only_safe_links_are_clickable(self):
        self.assertIn('<a href="https://example.com/job">job</a>', body("[job](https://example.com/job)"))
        self.assertNotIn("<a", body("[click](javascript:alert(1))"))

    def test_page_is_a_complete_document(self):
        page = render_report.page(REPORT)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("<title>Frontend Engineer at Pollen Analytics</title>", page)
        self.assertIn("prefers-color-scheme: dark", page)


class Cli(unittest.TestCase):
    def test_writes_html_next_to_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp, "report.md")
            report.write_text(REPORT, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                code = render_report.main([str(report)])
            self.assertEqual(code, 0)
            self.assertIn("Pollen Analytics", Path(tmp, "report.html").read_text(encoding="utf-8"))

    def test_not_markdown_exits_2(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(render_report.main(["missing.txt"]), 2)


if __name__ == "__main__":
    unittest.main()
