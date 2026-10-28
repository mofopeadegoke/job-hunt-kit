"""Tests for extract_text.py. Run from the repo root: python -m unittest discover tests"""
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
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


NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"')


def para(*runs):
    return "<w:p>" + "".join(runs) + "</w:p>"


def t(text):
    return f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r>'


def make_docx(folder, body, header=None, rels=None):
    """The smallest .docx the reader needs: document.xml, plus an optional header and link rels."""
    path = Path(folder, "resume.docx")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", f"<w:document {NS}><w:body>{body}</w:body></w:document>")
        if header:
            z.writestr("word/header1.xml", f"<w:hdr {NS}>{header}</w:hdr>")
        if rels:
            z.writestr(
                "word/_rels/document.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(f'<Relationship Id="{i}" Target="{url}" TargetMode="External"/>' for i, url in rels.items())
                + "</Relationships>",
            )
    return path


class Docx(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def text(self, path):
        return extract_text.extract_docx(path)

    def test_paragraphs_tabs_and_breaks(self):
        path = make_docx(self.tmp, para(t("Brightleaf Labs"), "<w:r><w:tab/></w:r>", t("Mar 2024 – Present"))
                         + para(t("Frontend Developer"), "<w:r><w:br/></w:r>", t("Nairobi")))
        self.assertEqual(self.text(path), "Brightleaf Labs\tMar 2024 – Present\nFrontend Developer\nNairobi\n")

    def test_header_comes_first(self):
        path = make_docx(self.tmp, para(t("Experience")), header=para(t("JANE DOE · +254 700 000 000")))
        self.assertEqual(self.text(path).splitlines(), ["JANE DOE · +254 700 000 000", "Experience"])

    def test_link_address_is_kept_when_hidden(self):
        body = para('<w:hyperlink r:id="rId1">' + t("LinkedIn") + "</w:hyperlink>",
                    t(" · "),
                    '<w:hyperlink r:id="rId2">' + t("jane.doe@example.com") + "</w:hyperlink>")
        path = make_docx(self.tmp, body, rels={"rId1": "https://www.linkedin.com/in/jane-doe-example",
                                                "rId2": "mailto:jane.doe@example.com"})
        self.assertEqual(self.text(path).strip(),
                         "LinkedIn · jane.doe@example.com <https://www.linkedin.com/in/jane-doe-example>")

    def test_text_box_is_read_once(self):
        box = para("<w:r><mc:AlternateContent><mc:Choice><w:txbxContent>" + para(t("Skills: React"))
                   + "</w:txbxContent></mc:Choice><mc:Fallback><w:txbxContent>" + para(t("Skills: React"))
                   + "</w:txbxContent></mc:Fallback></mc:AlternateContent></w:r>")
        path = make_docx(self.tmp, box)
        self.assertEqual(self.text(path).count("Skills: React"), 1)

    def test_cli_reads_docx(self):
        path = make_docx(self.tmp, para(t("Kilima University")))
        code, out, _ = run(path, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["text"], "Kilima University\n")

    def test_not_a_docx_exits_2(self):
        path = Path(self.tmp, "resume.docx")
        path.write_text("not a zip", encoding="utf-8")
        code, _, err = run(path)
        self.assertEqual(code, 2)
        self.assertIn("re-save", err)

    def test_doc_without_libreoffice_asks_to_resave(self):
        path = Path(self.tmp, "resume.doc")
        path.write_bytes(b"\xd0\xcf\x11\xe0")
        with mock.patch.object(extract_text, "find_soffice", return_value=None):
            code, _, err = run(path)
        self.assertEqual(code, 3)
        self.assertIn("Save As .docx or PDF", err)


if __name__ == "__main__":
    unittest.main()
