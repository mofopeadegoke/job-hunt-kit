#!/usr/bin/env python3
"""Show the text in a resume: what an ATS sees in a PDF, or the words in a Word file.

Usage: python extract_text.py resume.pdf|resume.tex|resume.docx|resume.doc [--json]
A .tex is compiled first; a .doc is converted to .docx with LibreOffice first.
Exit code: 0 = ok, 2 = bad input, 3 = a needed tool is missing, 4 = LaTeX failed to compile.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ENGINES = {
    "latexmk": lambda tex: ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex],
    "pdflatex": lambda tex: ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex],
    "tectonic": lambda tex: ["tectonic", tex],
}
SUFFIXES = (".pdf", ".tex", ".docx", ".doc")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
RELS = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
# LibreOffice isn't on PATH after a default Windows or macOS install.
SOFFICE_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


class ToolMissing(Exception):
    pass


class CompileFailed(Exception):
    pass


class BadFile(Exception):
    pass


def compile_tex(tex: Path) -> Path:
    engine = next((name for name in ENGINES if shutil.which(name)), None)
    if engine is None:
        raise ToolMissing(
            "No LaTeX engine found (latexmk, pdflatex or tectonic). "
            "Compile the .tex in Overleaf or your editor and pass the PDF instead."
        )
    # Run next to the .tex so relative \input paths and the output PDF land where the user expects.
    run = subprocess.run(
        ENGINES[engine](tex.name), cwd=tex.parent, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    pdf = tex.with_suffix(".pdf")
    if run.returncode != 0 or not pdf.is_file():
        tail = "\n".join((run.stdout + run.stderr).splitlines()[-20:])
        raise CompileFailed(f"{engine} failed on {tex}:\n{tail}")
    return pdf


def page_count(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, errors="replace").stdout
    m = re.search(r"^Pages:\s*(\d+)", out, re.MULTILINE)
    return int(m.group(1)) if m else None


def extract_text(pdf: Path) -> str:
    if not shutil.which("pdftotext"):
        raise ToolMissing("pdftotext is not installed (it comes with Poppler).")
    return subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout


def link_targets(docx: zipfile.ZipFile, part: str) -> dict[str, str]:
    rels = f"{part.rsplit('/', 1)[0]}/_rels/{part.rsplit('/', 1)[1]}.rels"
    if rels not in docx.namelist():
        return {}
    root = ElementTree.fromstring(docx.read(rels))
    return {r.get("Id"): r.get("Target") for r in root.iter(RELS) if r.get("TargetMode") == "External"}


def paragraph_text(p: ElementTree.Element, links: dict[str, str]) -> str:
    parts = []
    # A tab-stop setting (<w:tabs><w:tab/></w:tabs>) has the same tag as a typed tab.
    stops = {id(stop) for tabs in p.iter(f"{W}tabs") for stop in tabs}
    for node in p.iter():
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag == f"{W}tab" and id(node) not in stops:
            parts.append("\t")
        elif node.tag in (f"{W}br", f"{W}cr"):
            parts.append("\n")
        elif node.tag == f"{W}hyperlink":
            # The visible text is often just "LinkedIn"; the address only lives in the rels file.
            target = links.get(node.get(R_ID) or "")
            shown = "".join(t.text or "" for t in node.iter(f"{W}t"))
            if target and target.removeprefix("mailto:") not in shown:
                parts.append(f"__LINK__{target}__")
    text = "".join(parts)
    # Link markers go after the paragraph's own text so they don't split words.
    found = re.findall(r"__LINK__(.*?)__", text)
    text = re.sub(r"__LINK__.*?__", "", text)
    return text + "".join(f" <{url}>" for url in found)


def docx_part_text(docx: zipfile.ZipFile, part: str) -> list[str]:
    root = ElementTree.fromstring(docx.read(part))
    # Word stores each text box twice: a modern copy and a Fallback for old readers.
    for parent in root.iter():
        for child in [c for c in parent if c.tag == f"{MC}Fallback"]:
            parent.remove(child)
    links = link_targets(docx, part)
    lines = []
    for p in root.iter(f"{W}p"):
        # A text box is a paragraph inside a paragraph; take only the innermost ones.
        if any(child.tag == f"{W}p" for child in p.iter() if child is not p):
            continue
        lines.append(paragraph_text(p, links))
    return lines


def extract_docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as docx:
            names = docx.namelist()
            if "word/document.xml" not in names:
                raise BadFile(f"{path} is not a Word .docx file")
            headers = sorted(n for n in names if re.fullmatch(r"word/header\d*\.xml", n))
            footers = sorted(n for n in names if re.fullmatch(r"word/footer\d*\.xml", n))
            lines = []
            for part in headers + ["word/document.xml"] + footers:
                lines.extend(docx_part_text(docx, part))
    except (zipfile.BadZipFile, ElementTree.ParseError):
        raise BadFile(f"{path} is not a readable .docx (re-save it from Word or Google Docs)") from None
    # Word repeats a header on every section; keep the first copy of each line in a row.
    out = [line for i, line in enumerate(lines) if i == 0 or line != lines[i - 1] or not line.strip()]
    return "\n".join(out).strip() + "\n"


def find_soffice() -> str | None:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    return found or next((p for p in SOFFICE_PATHS if Path(p).is_file()), None)


def convert_doc(doc: Path, out_dir: Path) -> Path:
    soffice = find_soffice()
    if soffice is None:
        raise ToolMissing(
            "Old .doc files need LibreOffice to read, and it isn't installed. "
            "Open the file in Word or Google Docs and Save As .docx or PDF, then use that file."
        )
    subprocess.run(
        [soffice, "--headless", "--convert-to", "docx", "--outdir", str(out_dir), str(doc)],
        capture_output=True, text=True, errors="replace", timeout=120,
    )
    docx = out_dir / f"{doc.stem}.docx"
    if not docx.is_file():
        raise BadFile(f"LibreOffice couldn't convert {doc}. Save it as .docx or PDF and use that file.")
    return docx


def read_resume(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return {"source": str(path), "pdf": None, "pages": None, "text": extract_docx(path)}
    if suffix == ".doc":
        with tempfile.TemporaryDirectory() as tmp:
            return {"source": str(path), "pdf": None, "pages": None,
                    "text": extract_docx(convert_doc(path, Path(tmp)))}
    pdf = compile_tex(path) if suffix == ".tex" else path
    return {"source": str(path), "pdf": str(pdf), "pages": page_count(pdf), "text": extract_text(pdf)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show the text in a resume.")
    parser.add_argument("file", type=Path, help="the resume: .pdf, .docx, .doc, or a .tex to compile first")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    args = parser.parse_args(argv)

    path = args.file
    if not path.is_file() or path.suffix.lower() not in SUFFIXES:
        print(f"error: expected an existing {', '.join(SUFFIXES)} file: {path}", file=sys.stderr)
        return 2

    try:
        result = read_resume(path)
    except BadFile as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except ToolMissing as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except CompileFailed as e:
        print(f"error: {e}", file=sys.stderr)
        return 4

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Windows consoles can't print every character a resume might contain.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
        pages = result["pages"]
        print(f"source: {result['source']}\npdf: {result['pdf'] or 'n/a'}\n"
              f"pages: {pages if pages is not None else 'unknown'}\n")
        print(result["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
