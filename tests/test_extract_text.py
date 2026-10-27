"""Tests for extract_text.py. Run from the repo root: python -m unittest discover tests"""
import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/job-hunt-kit/skills/ats-optimize/scripts/extract_text.py"
JANE_TEX = ROOT / "fixtures/jane-doe/resume.tex"
JANE_PDF = ROOT / "fixtures/jane-doe/resume.pdf"

spec = importlib.util.spec_from_file_location("extract_text", SCRIPT)
extract_text = importlib.util.module_from_spec(spec)
sys.modules["extract_text"] = extract_text
spec.loader.exec_module(extract_text)


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = extract_text.main([str(a) for a in args])
    return code, out.getvalue(), err.getvalue()


class ExtractText(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pdftotext") and JANE_PDF.exists(), "needs pdftotext and resume.pdf")
    def test_extracts_jane_doe_pdf(self):
        code, out, _ = run(JANE_PDF)
        self.assertEqual(code, 0)
        self.assertIn("jane.doe@example.com", out)
        self.assertIn("Kilima University", out)

    @unittest.skipUnless(shutil.which("pdfinfo") and JANE_PDF.exists(), "needs pdfinfo and resume.pdf")
    def test_counts_pages(self):
        self.assertEqual(extract_text.page_count(JANE_PDF), 1)

    def test_tex_without_latex_engine_exits_3(self):
        with mock.patch.object(extract_text.shutil, "which", return_value=None):
            code, _, err = run(JANE_TEX)
        self.assertEqual(code, 3)
        self.assertIn("Overleaf", err)

    def test_wrong_file_type_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Path(tmp, "job.txt")
            job.write_text("Frontend Engineer", encoding="utf-8")
            self.assertEqual(run(job)[0], 2)

    def test_missing_file_exits_2(self):
        self.assertEqual(run("does-not-exist.pdf")[0], 2)


if __name__ == "__main__":
    unittest.main()
