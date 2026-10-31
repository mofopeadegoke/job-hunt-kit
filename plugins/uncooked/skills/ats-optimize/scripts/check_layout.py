#!/usr/bin/env python3
"""Check a LaTeX resume against the layout rules R1-R7 and R10.

Usage: python check_layout.py resume.tex [--pdf resume.pdf] [--json]
Exit code: 0 = no rule failed, 1 = at least one rule failed, 2 = bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

PASS, FAIL, WARN, SKIP = "pass", "fail", "warn", "skip"


@dataclass
class Result:
    rule: str
    name: str
    status: str
    details: list[str] = field(default_factory=list)


@dataclass
class Section:
    title: str
    line: int
    start: int
    end: int


SECTION_RE = re.compile(r"\\section\*?\s*\{((?:[^{}]|\{[^{}]*\})*)\}")
BEGIN_DOC, END_DOC = "\\begin{document}", "\\end{document}"


def strip_comments(source: str) -> str:
    # Newlines are kept so line numbers still match the user's file.
    return re.sub(r"(?<!\\)%.*", "", source)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def plain_title(raw: str) -> str:
    title = raw.replace("\\&", "&")
    title = re.sub(r"\\[a-zA-Z]+\*?", "", title)
    title = title.replace("{", "").replace("}", "")
    return " ".join(title.split())


class Resume:
    def __init__(self, source: str):
        self.text = strip_comments(source)
        begin = self.text.find(BEGIN_DOC)
        end = self.text.find(END_DOC)
        self.body_start = begin + len(BEGIN_DOC) if begin != -1 else 0
        self.body_end = end if end != -1 else len(self.text)

        matches = list(SECTION_RE.finditer(self.text, self.body_start, self.body_end))
        self.sections = []
        for i, m in enumerate(matches):
            stop = matches[i + 1].start() if i + 1 < len(matches) else self.body_end
            self.sections.append(
                Section(plain_title(m.group(1)), line_of(self.text, m.start()), m.end(), stop)
            )
        self.header_end = matches[0].start() if matches else self.body_end

    def font_size_pt(self) -> int:
        m = re.search(r"\\documentclass\s*\[[^\]]*\b(10|11|12)pt\b", self.text)
        return int(m.group(1)) if m else 10

    def find_section(self, words: tuple[str, ...]) -> Section | None:
        for s in self.sections:
            if any(w in s.title.lower() for w in words):
                return s
        return None

    def hits(self, pattern: re.Pattern, start: int = 0, end: int | None = None) -> list[str]:
        end = len(self.text) if end is None else end
        return [
            f"line {line_of(self.text, m.start())}: {m.group(0).strip()}"
            for m in pattern.finditer(self.text, start, end)
        ]


# R1 ---------------------------------------------------------------------------

STANDARD_HEADING_WORDS = (
    "summary", "profile", "objective", "experience", "employment", "work history",
    "education", "skills", "projects", "certification", "licenses", "awards",
    "achievements", "honors", "honours", "competitions", "publications", "volunteer",
    "languages", "leadership", "activities", "coursework", "courses", "interests",
    "references", "research", "training",
)
EXPERIENCE_WORDS = ("experience", "employment", "work history")


def check_headings(r: Resume) -> Result:
    result = Result("R1", "Standard section headings", PASS)
    if not r.sections:
        result.status = WARN
        result.details.append(
            "No \\section headings found, so headings can't be checked "
            "(custom heading commands aren't supported)."
        )
        return result

    for s in r.sections:
        if not any(w in s.title.lower() for w in STANDARD_HEADING_WORDS):
            result.status = FAIL
            result.details.append(f'line {s.line}: "{s.title}" is not a standard heading')

    for label, words in (("Experience", EXPERIENCE_WORDS), ("Education", ("education",))):
        if not r.find_section(words):
            result.details.append(f"No {label} section found.")
            if result.status == PASS:
                result.status = WARN
    return result


# R2 ---------------------------------------------------------------------------

COLUMN_RE = re.compile(
    r"\\documentclass\s*\[[^\]]*\btwocolumn\b[^\]]*\]"
    r"|\\twocolumn\b"
    r"|\\begin\{(?:multicols\*?|paracol|minipage)\}"
    r"|\\begin\{(?:tabular[x*]?|tabularx|tabulary|longtable|table\*?)\}"
)


def check_single_column(r: Resume) -> Result:
    hits = r.hits(COLUMN_RE)
    if not hits:
        return Result("R2", "Single column, no tables", PASS)
    return Result("R2", "Single column, no tables", FAIL, hits)


# R3 ---------------------------------------------------------------------------

SEPARATOR_RE = re.compile(
    r"\$\s*\\(?:cdot|bullet|vert|mid|diamond|ast|circ)\s*\$"
    r"|\$\s*\|\s*\$"
    r"|\\text(?:bullet|bar|periodcentered|bardbl)(?:\{\})?"
    r"|[·•|]"
)
WIDE_SPACE = r"(?:\\quad|\\qquad|\\hspace\*?\s*\{[^{}]*\})"
WIDE_BEFORE_RE = re.compile(WIDE_SPACE + r"\s*$")
WIDE_AFTER_RE = re.compile(r"^\s*" + WIDE_SPACE)
CONTACT_RE = re.compile(
    r"@|\\href|\\url|https?://|www\.|\.(?:com|io|dev|me|org|net|app)\b|\+?\d[\d\s().-]{6,}\d"
)
LINE_BREAK = "\\\\"


def header_line_around(r: Resume, pos: int) -> str:
    start = r.text.rfind(LINE_BREAK, r.body_start, pos)
    end = r.text.find(LINE_BREAK, pos, r.header_end)
    return r.text[r.body_start if start == -1 else start:r.header_end if end == -1 else end]


def check_contact_spacing(r: Resume) -> Result:
    result = Result("R3", "Clear space around contact separators", PASS)
    for m in SEPARATOR_RE.finditer(r.text, r.body_start, r.header_end):
        # Tight separators only glued fields together on lines with contact details
        # (email to phone in version A), so lines like work authorization are left alone.
        if not CONTACT_RE.search(header_line_around(r, m.start())):
            continue
        before = r.text[max(r.body_start, m.start() - 60):m.start()]
        after = r.text[m.end():min(r.header_end, m.end() + 60)]
        if not (WIDE_BEFORE_RE.search(before) and WIDE_AFTER_RE.search(after)):
            result.status = FAIL
            result.details.append(
                f"line {line_of(r.text, m.start())}: {m.group(0)} needs \\quad on both sides"
            )
    return result


# R4 ---------------------------------------------------------------------------

BASELINE_SKIP_PT = {10: 12.0, 11: 13.6, 12: 14.5}
UNIT_PT = {
    "pt": 1.0, "bp": 72.27 / 72, "mm": 72.27 / 25.4, "cm": 72.27 / 2.54,
    "in": 72.27, "pc": 12.0, "dd": 1238 / 1157, "sp": 1 / 65536,
}
NAMED_SKIP_PT = {"smallskip": 3.0, "medskip": 6.0, "bigskip": 12.0}
LENGTH_RE = re.compile(
    r"\s*([-+]?(?:\d+\.?\d*|\.\d+))?\s*(pt|bp|mm|cm|in|pc|dd|sp|em|ex|\\baselineskip)"
    r"(?:\s*(?:plus|minus)\b.*)?\s*"
)
END_LIST_RE = re.compile(r"\\end\{(?:itemize|enumerate)\}")
GAP_RE = re.compile(
    r"\s*(?:\\vspace\*?\s*\{([^{}]*)\}|\\(smallskip|medskip|bigskip)\b|\\vskip\s*([^\\\n]*))"
)


def length_pt(spec: str, font_pt: int = 10) -> float | None:
    m = LENGTH_RE.fullmatch(spec)
    if not m:
        return None
    number = float(m.group(1)) if m.group(1) else 1.0
    unit = m.group(2)
    if unit == "em":
        return number * font_pt
    if unit == "ex":
        return number * font_pt * 0.43
    if unit == "\\baselineskip":
        return number * BASELINE_SKIP_PT.get(font_pt, font_pt * 1.2)
    return number * UNIT_PT[unit]


def min_entry_gap_pt(font_pt: int) -> float:
    # A simple parser starts a new entry when the gap between lines is more than 1.4x the
    # normal line gap, so the extra space must be over 0.4 of a baseline.
    return 0.4 * BASELINE_SKIP_PT.get(font_pt, font_pt * 1.2)


def check_entry_spacing(r: Resume) -> Result:
    result = Result("R4", "Visible space between entries", PASS)
    font_pt = r.font_size_pt()
    minimum = min_entry_gap_pt(font_pt)
    for s in r.sections:
        for m in END_LIST_RE.finditer(r.text, s.start, s.end):
            rest = r.text[m.end():s.end].lstrip()
            if not rest or rest.startswith(("\\end{", "\\item")):
                continue
            where = f"line {line_of(r.text, m.start())}"
            gap = GAP_RE.match(r.text, m.end(), s.end)
            if not gap:
                result.status = FAIL
                result.details.append(f"{where}: no space before the next entry; add \\vspace{{6pt}}")
                continue
            if gap.group(2):
                size = NAMED_SKIP_PT[gap.group(2)]
            else:
                size = length_pt(gap.group(1) if gap.group(1) is not None else gap.group(3), font_pt)
            if size is None:
                if result.status == PASS:
                    result.status = WARN
                result.details.append(f"{where}: can't measure {gap.group(0).strip()}")
            elif size < minimum:
                result.status = FAIL
                result.details.append(
                    f"{where}: {gap.group(0).strip()} is {size:.1f}pt; needs more than {minimum:.1f}pt"
                )
    return result


# R5 ---------------------------------------------------------------------------


def parse_pdfinfo_pages(output: str) -> int | None:
    m = re.search(r"^Pages:\s*(\d+)", output, re.MULTILINE)
    return int(m.group(1)) if m else None


def normalize_heading(text: str) -> str:
    return " ".join(text.replace("&amp;", "&").split()).upper()


def check_pages(r: Resume, pdf: Path | None) -> Result:
    result = Result("R5", "One page, or no heading at the top of page 2", SKIP)
    if pdf is None:
        result.details.append("No PDF given (use --pdf).")
        return result
    if not shutil.which("pdfinfo"):
        result.details.append("pdfinfo is not installed (it comes with Poppler).")
        return result

    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, errors="replace")
    pages = parse_pdfinfo_pages(info.stdout)
    if pages is None:
        result.details.append(f"pdfinfo could not read {pdf}.")
        return result
    if pages == 1:
        result.status = PASS
        return result

    if not shutil.which("pdftotext"):
        result.status = WARN
        result.details.append(f"{pages} pages; pdftotext is not installed, so page 2 wasn't checked.")
        return result
    page2 = subprocess.run(
        ["pdftotext", "-f", "2", "-l", "2", "-layout", str(pdf), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    first_line = next((ln.strip() for ln in page2.splitlines() if ln.strip()), "")
    headings = {normalize_heading(s.title) for s in r.sections}
    if normalize_heading(first_line) in headings:
        result.status = FAIL
        result.details.append(f'{pages} pages; page 2 starts with the heading "{first_line}"')
    else:
        result.status = WARN
        result.details.append(f"{pages} pages; page 2 doesn't start with a heading, but one page is safer.")
    return result


# R6 ---------------------------------------------------------------------------

HYPHENAT_NONE_RE = re.compile(r"\\usepackage\s*\[[^\]]*\bnone\b[^\]]*\]\s*\{hyphenat\}")
HYPHEN_PENALTY_RE = re.compile(r"\\hyphenpenalty\s*=?\s*(\d+)")


def check_hyphenation(r: Resume) -> Result:
    name = "Hyphenation off"
    if HYPHENAT_NONE_RE.search(r.text):
        return Result("R6", name, PASS)
    if any(int(v) >= 10000 for v in HYPHEN_PENALTY_RE.findall(r.text)):
        return Result("R6", name, PASS)
    return Result(
        "R6", name, FAIL,
        ["Add \\usepackage[none]{hyphenat} (or \\hyphenpenalty=10000) to the preamble."],
    )


# R7 ---------------------------------------------------------------------------

ICON_RE = re.compile(
    r"\\fa[A-Z][A-Za-z]*|\\faIcon\b|\\ding\s*\{|\\ai[A-Z][A-Za-z]*"
    r"|\\(?:Letter|Mobilefone|Telefon|Email|EmailCT|Mundus|Faxmachine|Pickup)\b"
    r"|\\includegraphics"
    "|[\u2600-\u27bf\U0001f300-\U0001faff]"
)


def check_icons(r: Resume) -> Result:
    hits = r.hits(ICON_RE)
    if not hits:
        return Result("R7", "No icons or images", PASS)
    return Result("R7", "No icons or images", FAIL, hits)


# R10 --------------------------------------------------------------------------

EDUCATION_ALIGN_RE = re.compile(
    r"\\hfill\b|\\hspace\*?\s*\{\s*\\(?:fill|stretch)|\\dotfill\b|\\begin\{tabular"
)


def check_education_stacked(r: Resume) -> Result:
    name = "Stacked Education block"
    education = r.find_section(("education",))
    if education is None:
        return Result("R10", name, SKIP, ["No Education section found."])
    hits = r.hits(EDUCATION_ALIGN_RE, education.start, education.end)
    if not hits:
        return Result("R10", name, PASS)
    return Result(
        "R10", name, FAIL,
        hits + ["Put school, degree, location/date and GPA each on their own line."],
    )


# ------------------------------------------------------------------------------


def run_checks(source: str, pdf: Path | None = None) -> list[Result]:
    r = Resume(source)
    return [
        check_headings(r),
        check_single_column(r),
        check_contact_spacing(r),
        check_entry_spacing(r),
        check_pages(r, pdf),
        check_hyphenation(r),
        check_icons(r),
        check_education_stacked(r),
    ]


def format_text(path: Path, results: list[Result]) -> str:
    lines = [f"check_layout: {path}"]
    for res in results:
        lines.append(f"  {res.status.upper():<4}  {res.rule:<3}  {res.name}")
        lines.extend(f"              {d}" for d in res.details)
    failed = sum(res.status == FAIL for res in results)
    warned = sum(res.status == WARN for res in results)
    lines.append(f"Result: {failed} failed, {warned} warnings")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a LaTeX resume against layout rules.")
    parser.add_argument("tex", type=Path, help="the resume .tex file")
    parser.add_argument("--pdf", type=Path, help="the compiled PDF, for the page check (R5)")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    args = parser.parse_args(argv)

    for path in (args.tex, args.pdf):
        if path is not None and not path.is_file():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    results = run_checks(args.tex.read_text(encoding="utf-8", errors="replace"), args.pdf)
    passed = not any(res.status == FAIL for res in results)
    if args.json:
        print(json.dumps(
            {"file": str(args.tex), "passed": passed, "checks": [asdict(res) for res in results]},
            indent=2,
        ))
    else:
        # Windows consoles can't print every character a resume might contain.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
        print(format_text(args.tex, results))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
