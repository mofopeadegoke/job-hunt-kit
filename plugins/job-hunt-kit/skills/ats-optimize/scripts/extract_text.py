#!/usr/bin/env python3
"""Show the text an ATS sees in a resume PDF, compiling a .tex file first if needed.

Usage: python extract_text.py resume.pdf|resume.tex [--json]
Exit code: 0 = ok, 2 = bad input, 3 = a needed tool is missing, 4 = LaTeX failed to compile.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ENGINES = {
    "latexmk": lambda tex: ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex],
    "pdflatex": lambda tex: ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex],
    "tectonic": lambda tex: ["tectonic", tex],
}


class ToolMissing(Exception):
    pass


class CompileFailed(Exception):
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show the text an ATS sees in a resume.")
    parser.add_argument("file", type=Path, help="the resume .pdf, or a .tex to compile first")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    args = parser.parse_args(argv)

    path = args.file
    if not path.is_file() or path.suffix.lower() not in (".pdf", ".tex"):
        print(f"error: expected an existing .pdf or .tex file: {path}", file=sys.stderr)
        return 2

    try:
        pdf = compile_tex(path) if path.suffix.lower() == ".tex" else path
        text = extract_text(pdf)
    except ToolMissing as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except CompileFailed as e:
        print(f"error: {e}", file=sys.stderr)
        return 4

    pages = page_count(pdf)
    if args.json:
        print(json.dumps({"pdf": str(pdf), "pages": pages, "text": text}, indent=2))
    else:
        # Windows consoles can't print every character a resume might contain.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
        print(f"pdf: {pdf}\npages: {pages if pages is not None else 'unknown'}\n")
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
