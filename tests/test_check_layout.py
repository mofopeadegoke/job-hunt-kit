"""Tests for check_layout.py.

Like the research, each variant takes Jane Doe's good resume and breaks exactly one rule.
Run from the repo root: python -m unittest discover tests
"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/job-hunt-kit/skills/ats-optimize/scripts/check_layout.py"
JANE_TEX = ROOT / "fixtures/jane-doe/resume.tex"
JANE_PDF = ROOT / "fixtures/jane-doe/resume.pdf"

spec = importlib.util.spec_from_file_location("check_layout", SCRIPT)
check_layout = importlib.util.module_from_spec(spec)
sys.modules["check_layout"] = check_layout
spec.loader.exec_module(check_layout)

GOOD = JANE_TEX.read_text(encoding="utf-8")


def statuses(source, pdf=None):
    return {r.rule: r.status for r in check_layout.run_checks(source, pdf)}


def variant(old, new):
    assert old in GOOD, f"fixture changed, can't find: {old!r}"
    return GOOD.replace(old, new)


class GoodResume(unittest.TestCase):
    def test_jane_doe_passes_every_tex_rule(self):
        results = statuses(GOOD)
        self.assertEqual(results.pop("R5"), "skip")
        self.assertEqual(set(results.values()), {"pass"}, results)

    @unittest.skipUnless(shutil.which("pdfinfo") and JANE_PDF.exists(), "needs pdfinfo and resume.pdf")
    def test_jane_doe_pdf_is_one_page(self):
        self.assertEqual(statuses(GOOD, JANE_PDF)["R5"], "pass")


class OneBrokenRule(unittest.TestCase):
    def assertOnlyFails(self, source, rule):
        results = statuses(source)
        failed = {k for k, v in results.items() if v == "fail"}
        self.assertEqual(failed, {rule}, results)

    def test_creative_heading_fails_r1(self):
        self.assertOnlyFails(variant("\\section*{Experience}", "\\section*{Where I've Worked}"), "R1")

    def test_two_columns_fail_r2(self):
        source = variant("\\pagestyle{empty}", "\\pagestyle{empty}\n\\begin{multicols}{2}")
        source = source.replace("\\end{document}", "\\end{multicols}\n\\end{document}")
        self.assertOnlyFails(source, "R2")

    def test_skills_table_fails_r2(self):
        source = variant(
            "\\textbf{Languages:} TypeScript, JavaScript (ES6+), HTML5, CSS3, SQL \\\\",
            "\\begin{tabular}{lllll}\nTypeScript & JavaScript & HTML5 & CSS3 & SQL\n\\end{tabular} \\\\",
        )
        self.assertOnlyFails(source, "R2")

    def test_tight_contact_separators_fail_r3(self):
        self.assertOnlyFails(variant("Kenya \\quad$\\cdot$\\quad +254", "Kenya $\\cdot$ +254"), "R3")

    def test_tight_separators_on_a_line_without_contact_details_pass_r3(self):
        source = variant(
            "Kenyan Citizen \\quad$\\cdot$\\quad Remote Ready (GMT+3) \\quad$\\cdot$\\quad Visa",
            "Kenyan Citizen $\\cdot$ Remote Ready (GMT+3) $\\cdot$ Visa",
        )
        self.assertEqual(statuses(source)["R3"], "pass")

    def test_tight_separator_between_links_fails_r3(self):
        source = variant("example.com} \\\\\n    \\href{https://github.com/janedoe-dev}{github.com/janedoe-dev} \\quad$\\cdot$\\quad",
                         "example.com} \\\\\n    \\href{https://github.com/janedoe-dev}{github.com/janedoe-dev} $\\cdot$")
        self.assertOnlyFails(source, "R3")

    def test_pipe_separators_with_wide_space_pass_r3(self):
        source = GOOD.replace("\\quad$\\cdot$\\quad", "\\quad$|$\\quad")
        self.assertEqual(statuses(source)["R3"], "pass")

    def test_no_space_between_entries_fails_r4(self):
        self.assertOnlyFails(GOOD.replace("\\vspace{6pt}\n", ""), "R4")

    def test_smallskip_is_too_small_for_r4(self):
        self.assertOnlyFails(GOOD.replace("\\vspace{6pt}", "\\smallskip"), "R4")

    def test_medskip_and_baselineskip_pass_r4(self):
        for gap in ("\\medskip", "\\vspace{0.5\\baselineskip}", "\\vspace{6pt plus 2pt}"):
            with self.subTest(gap=gap):
                self.assertEqual(statuses(GOOD.replace("\\vspace{6pt}", gap))["R4"], "pass")

    def test_hyphenation_on_fails_r6(self):
        self.assertOnlyFails(variant("\\usepackage[none]{hyphenat}\n", ""), "R6")

    def test_hyphen_penalty_passes_r6(self):
        source = variant("\\usepackage[none]{hyphenat}", "\\hyphenpenalty=10000")
        self.assertEqual(statuses(source)["R6"], "pass")

    def test_fontawesome_icon_fails_r7(self):
        self.assertOnlyFails(variant("Nairobi, Kenya \\quad", "\\faMapMarker\\ Nairobi, Kenya \\quad"), "R7")

    def test_emoji_icon_fails_r7(self):
        self.assertOnlyFails(variant("\\href{mailto:", "\u2709 \\href{mailto:"), "R7")

    def test_hfill_in_education_fails_r10(self):
        source = variant("\\textbf{Kilima University} \\\\", "\\textbf{Kilima University} \\hfill Nairobi, Kenya \\\\")
        self.assertOnlyFails(source, "R10")

    def test_commented_out_problems_are_ignored(self):
        source = variant("\\pagestyle{empty}", "\\pagestyle{empty}\n% \\begin{multicols}{2} \\faPhone")
        self.assertEqual(statuses(source)["R2"], "pass")
        self.assertEqual(statuses(source)["R7"], "pass")

    def test_failure_reports_line_number(self):
        source = variant("\\section*{Experience}", "\\section*{Where I've Worked}")
        r1 = next(r for r in check_layout.run_checks(source) if r.rule == "R1")
        expected_line = source.splitlines().index("\\section*{Where I've Worked}") + 1
        self.assertIn(f"line {expected_line}:", r1.details[0])


class Helpers(unittest.TestCase):
    def test_length_pt(self):
        self.assertEqual(check_layout.length_pt("6pt"), 6.0)
        self.assertEqual(check_layout.length_pt("0.5em", 10), 5.0)
        self.assertAlmostEqual(check_layout.length_pt("2mm"), 5.69, places=2)
        self.assertEqual(check_layout.length_pt("0.5\\baselineskip", 10), 6.0)
        self.assertIsNone(check_layout.length_pt("\\itemsep"))

    def test_min_entry_gap_follows_font_size(self):
        self.assertAlmostEqual(check_layout.min_entry_gap_pt(10), 4.8)
        self.assertAlmostEqual(check_layout.min_entry_gap_pt(12), 5.8)

    def test_parse_pdfinfo_pages(self):
        self.assertEqual(check_layout.parse_pdfinfo_pages("Title: x\nPages:          2\n"), 2)
        self.assertIsNone(check_layout.parse_pdfinfo_pages("garbage"))


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_exit_codes(self):
        self.assertEqual(self.run_script(str(JANE_TEX)).returncode, 0)
        self.assertEqual(self.run_script("does-not-exist.tex").returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp, "bad.tex")
            bad.write_text(GOOD.replace("\\vspace{6pt}\n", ""), encoding="utf-8")
            self.assertEqual(self.run_script(str(bad)).returncode, 1)

    def test_json_output(self):
        out = self.run_script(str(JANE_TEX), "--json")
        self.assertIn('"passed": true', out.stdout)


if __name__ == "__main__":
    unittest.main()
