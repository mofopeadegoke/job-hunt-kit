"""Tests for compare_text.py. Run from the repo root: python -m unittest discover tests"""
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/job-hunt-kit/skills/ats-optimize/scripts"
JANE_TEX_PATH = ROOT / "fixtures/jane-doe/resume.tex"
JANE_TEX = JANE_TEX_PATH.read_text(encoding="utf-8")
WORD = ROOT / "fixtures/jane-doe/word"
HAS_POPPLER = bool(shutil.which("pdftotext") and shutil.which("pdfinfo"))

spec = importlib.util.spec_from_file_location("compare_text", SCRIPTS / "compare_text.py")
compare_text = importlib.util.module_from_spec(spec)
sys.modules["compare_text"] = compare_text
spec.loader.exec_module(compare_text)
read_resume = compare_text.extract_text.read_resume


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = compare_text.main([str(a) for a in args])
    return code, out.getvalue(), err.getvalue()


def against_word(tex):
    return compare_text.compare(read_resume(WORD / "resume.docx"), tex)


def words_of(result, key):
    return [item["word"] for item in result[key]]


class TexText(unittest.TestCase):
    def text(self, body):
        return compare_text.tex_text("\\begin{document}\n" + body + "\n\\end{document}")

    def test_escapes_and_dashes(self):
        text, _ = self.text(r"Testing \& Tools \quad$\cdot$\quad 20--30\% faster, C\# and a\_b")
        self.assertEqual(text, "Testing & Tools 20–30% faster, C# and a_b")

    def test_links_and_formatting(self):
        text, links = self.text(r"\textbf{Acme} \hfill \href{https://github.com/x}{github.com/x} \\ \textit{Dev}")
        self.assertEqual(text.splitlines(), ["Acme github.com/x", "Dev"])
        self.assertEqual(links, ["https://github.com/x"])

    def test_layout_commands_leave_no_words(self):
        text, _ = self.text("\\vspace{6pt}\n\\begin{itemize}[leftmargin=*]\n\\item One\n\\item Two\n\\end{itemize}")
        self.assertEqual(text.splitlines(), ["One", "Two"])

    def test_comments_are_ignored(self):
        text, _ = self.text("Real % secret note\nwords")
        self.assertEqual(text.split(), ["Real", "words"])


class SameResume(unittest.TestCase):
    def test_word_docx_matches_jane_tex(self):
        result = against_word(JANE_TEX)
        self.assertTrue(result["same"], result)
        self.assertEqual(result["link_labels_replaced"], ["github", "linkedin"])

    @unittest.skipUnless(HAS_POPPLER, "needs pdftotext and pdfinfo")
    def test_word_pdf_matches_jane_tex(self):
        result = compare_text.compare(read_resume(WORD / "resume.pdf"), JANE_TEX)
        self.assertTrue(result["same"], result)

    @unittest.skipUnless(HAS_POPPLER, "needs pdftotext and pdfinfo")
    def test_latex_pdf_matches_jane_tex(self):
        result = compare_text.compare(read_resume(ROOT / "fixtures/jane-doe/resume.pdf"), JANE_TEX)
        self.assertTrue(result["same"], result)


class CaughtChanges(unittest.TestCase):
    def test_dropped_bullet(self):
        tex = JANE_TEX.replace("    \\item Built about 15 reusable React components, documented in Storybook.\n", "")
        result = against_word(tex)
        self.assertFalse(result["same"])
        self.assertIn("documented", words_of(result, "missing"))
        # "in" is part of linkedin.com/in/..., but only site names count as link labels.
        self.assertIn("in", words_of(result, "missing"))

    def test_added_skill(self):
        result = against_word(JANE_TEX.replace("Storybook \\\\", "Storybook, GraphQL \\\\"))
        self.assertEqual(words_of(result, "added"), ["graphql"])
        self.assertEqual(result["missing"], [])

    def test_changed_number(self):
        result = against_word(JANE_TEX.replace("Built about 15 reusable", "Built 15+ reusable"))
        self.assertEqual(words_of(result, "missing"), ["15", "about"])
        self.assertEqual(words_of(result, "added"), ["15+"])

    def test_inflated_verb(self):
        result = against_word(JANE_TEX.replace("Helped migrate", "Led the migration of"))
        self.assertIn("helped", words_of(result, "missing"))
        self.assertIn("led", words_of(result, "added"))
        self.assertIn("Led the migration", result["added"][0]["line"])

    def test_dropped_repeat_of_a_word(self):
        # Word counts matter: the phrase still exists elsewhere, but one copy is gone.
        result = against_word(JANE_TEX.replace("Built React pages for the clinic admin portal.", "Built pages for the clinic admin portal."))
        self.assertEqual(words_of(result, "missing"), ["react"])

    def test_changed_link(self):
        result = against_word(JANE_TEX.replace("github.com/janedoe-dev", "github.com/janedoe"))
        self.assertEqual(result["links_missing"], ["github.com/janedoe-dev"])
        self.assertEqual(result["links_added"], ["github.com/janedoe"])

    def test_dropped_link_keeps_its_label_missing(self):
        tex = JANE_TEX.replace(
            "\\href{https://github.com/janedoe-dev}{github.com/janedoe-dev} \\quad$\\cdot$\\quad ", "")
        result = against_word(tex)
        self.assertIn("github", words_of(result, "missing"))
        self.assertEqual(result["links_missing"], ["github.com/janedoe-dev"])


class Cli(unittest.TestCase):
    def test_same_exits_0(self):
        code, out, _ = run(WORD / "resume.docx", JANE_TEX_PATH)
        self.assertEqual(code, 0)
        self.assertIn("same words and links", out)

    def test_differences_exit_1_with_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = Path(tmp, "resume.tex")
            tex.write_text(JANE_TEX.replace("Storybook \\\\", "Storybook, GraphQL \\\\"), encoding="utf-8")
            code, out, _ = run(WORD / "resume.docx", tex, "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["added"][0]["word"], "graphql")

    def test_tex_as_original_exits_2(self):
        self.assertEqual(run(JANE_TEX_PATH, JANE_TEX_PATH)[0], 2)

    def test_doc_without_libreoffice_exits_3(self):
        from unittest import mock
        with mock.patch.object(compare_text.extract_text, "find_soffice", return_value=None):
            code, _, err = run(WORD / "resume.doc", JANE_TEX_PATH)
        self.assertEqual(code, 3)
        self.assertIn("Save As .docx or PDF", err)


if __name__ == "__main__":
    unittest.main()
