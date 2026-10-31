#!/usr/bin/env python3
"""Turn report.md into report.html, a styled page that opens in any browser.

Usage: python render_report.py report.md [--out report.html]
Handles the Markdown the report uses: headings, paragraphs, lists, tables, bold, italics,
inline code, links, code blocks and rules. Status words in tables get coloured labels.
Exit code: 0 = written, 2 = bad input.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# Older reports used the short names on the right of each line.
STATUSES = {
    "met": "good", "on resume": "good", "present": "good",
    "reworded": "info", "moved higher": "info", "added from facts": "info", "reword": "info", "move up": "info",
    "partial match": "warn", "unclear": "warn", "partial": "warn",
    "not met": "bad", "missing": "bad", "gap": "bad",
}
# Longest first, so "not met" isn't read as "met".
STATUS_RE = re.compile(
    r"^\s*([*_]{0,2})(" + "|".join(sorted(STATUSES, key=len, reverse=True)) + r")(?=$|[*_\s:;,.(/—–-])",
    re.IGNORECASE,
)
TABLE_SEPARATOR_RE =re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]|(\d+)[.)])\s+(.*)$")

STYLE = """
:root {
  --bg: #ffffff; --text: #1f2328; --muted: #59636e; --border: #d1d9e0; --stripe: #f6f8fa;
  --accent: #0969da;
  --good-bg: #dafbe1; --good: #116329; --info-bg: #ddf4ff; --info: #0550ae;
  --warn-bg: #fff8c5; --warn: #7d4e00; --bad-bg: #ffebe9; --bad: #a40e26;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117; --text: #e6edf3; --muted: #9198a1; --border: #3d444d; --stripe: #151b23;
    --accent: #4493f8;
    --good-bg: #12361f; --good: #57d364; --info-bg: #0c2d6b; --info: #79c0ff;
    --warn-bg: #3b2e00; --warn: #e3b341; --bad-bg: #4c1219; --bad: #ff7b72;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.6 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
main { max-width: 960px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 1.9rem; line-height: 1.25; margin: 0 0 8px; }
h2 { font-size: 1.3rem; margin: 36px 0 12px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
h3 { font-size: 1.1rem; margin: 24px 0 8px; }
p, ul, ol { margin: 0 0 12px; }
li { margin: 4px 0; }
a { color: var(--accent); }
code { font: 0.9em ui-monospace, Consolas, monospace; background: var(--stripe); padding: 1px 5px; border-radius: 4px; }
pre { background: var(--stripe); padding: 12px; border-radius: 6px; overflow-x: auto; }
pre code { padding: 0; background: none; }
hr { border: 0; border-top: 1px solid var(--border); margin: 24px 0; }
blockquote { margin: 0 0 12px; padding: 0 14px; color: var(--muted); border-left: 4px solid var(--border); }
.table { overflow-x: auto; margin: 0 0 16px; }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
th, td { text-align: left; vertical-align: top; padding: 8px 10px; border: 1px solid var(--border); }
th { background: var(--stripe); }
tr:nth-child(even) td { background: var(--stripe); }
.verdict {
  margin: 0 0 16px; padding: 16px 20px; border-left: 6px solid var(--accent); border-radius: 8px;
  background: var(--stripe); font-size: 1.2rem; font-weight: 600; line-height: 1.5;
}
.verdict p:last-child { margin-bottom: 0; }
.badge { display: inline-block; padding: 1px 9px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; white-space: nowrap; }
.good { background: var(--good-bg); color: var(--good); }
.info { background: var(--info-bg); color: var(--info); }
.warn { background: var(--warn-bg); color: var(--warn); }
.bad { background: var(--bad-bg); color: var(--bad); }
@media print { body { background: #fff; color: #000; } main { padding: 0; } }
"""


def safe_url(url: str) -> str | None:
    # Links come from job postings too; only plain web, mail and relative links become clickable.
    if re.match(r"^(?:https?://|mailto:|#|\.{0,2}/|[\w.-]+(?:/|$))", url) and not url.lower().startswith("javascript:"):
        return url
    return None


def inline(text: str) -> str:
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)

    def link(m: re.Match) -> str:
        url = safe_url(html.unescape(m.group(2)))
        if url is None:
            return m.group(1)
        return f'<a href="{html.escape(url)}">{m.group(1)}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w])_(?![\s_])(.+?)(?<![\s_])_(?![\w])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line)]


def status_cell(text: str) -> str:
    """Leading status words ("partial", "present / partial") become labels; the rest stays text."""
    badges = []
    while m := STATUS_RE.match(text):
        marks, word = m.group(1), m.group(2)
        badges.append(f'<span class="badge {STATUSES[word.lower()]}">{html.escape(word)}</span>')
        text = text[m.end():]
        if marks and text.startswith(marks):
            text = text[len(marks):]
            marks = ""
        text = text.lstrip(" :;,—–-")
        if text.startswith("/") and STATUS_RE.match(text[1:]):
            text = text[1:]
            continue
        # Bold that ran past the status word ("**Not met as full-time**") still wraps the rest.
        text = marks + text
        break
    if not badges:
        return inline(text)
    return " ".join(badges) + (f" {inline(text)}" if text.strip() else "")


def table(lines: list[str]) -> str:
    head = split_row(lines[0])
    is_status = ["status" in h.lower() for h in head]
    rows = [split_row(line) for line in lines[2:]]
    out = ['<div class="table"><table>', "<thead><tr>"]
    out += [f"<th>{inline(h)}</th>" for h in head]
    out.append("</tr></thead><tbody>")
    for row in rows:
        row = (row + [""] * len(head))[:len(head)]
        cells = (status_cell(c) if s else inline(c) for c, s in zip(row, is_status))
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render(markdown: str) -> tuple[str, str]:
    """The HTML body and the page title (the first # heading)."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    title = ""
    paragraph: list[str] = []
    verdict_open = False
    i = 0

    def flush() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_verdict() -> None:
        nonlocal verdict_open
        if verdict_open:
            out.append("</section>")
            verdict_open = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush()
            i += 1
        elif stripped.startswith("```"):
            flush()
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block), quote=False)}</code></pre>")
            i += 1
        elif m := re.match(r"^(#{1,6})\s+(.*?)\s*#*$", stripped):
            flush()
            level = len(m.group(1))
            plain = re.sub(r"[*_`]", "", m.group(2)).strip()
            if level <= 2:
                close_verdict()
            if level == 1 and not title:
                title = plain
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            if level == 2 and plain.lower() == "verdict":
                out.append('<section class="verdict">')
                verdict_open = True
            i += 1
        elif stripped.startswith("|") and i + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[i + 1]):
            flush()
            block = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(table(block))
        elif re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", stripped):
            flush()
            out.append("<hr>")
            i += 1
        elif stripped.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
        elif m := LIST_RE.match(line):
            flush()
            tag = "ol" if m.group(1) else "ul"
            items = []
            while i < len(lines) and lines[i].strip():
                item = LIST_RE.match(lines[i])
                if item:
                    items.append(item.group(2))
                elif items:
                    # A wrapped line continues the item above it.
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
        else:
            paragraph.append(stripped)
            i += 1
    flush()
    close_verdict()
    return "\n".join(out), title or "Report"


def page(markdown: str) -> str:
    body, title = render(markdown)
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(title)}</title>\n<style>{STYLE}</style>\n</head>\n"
        f"<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turn report.md into a styled report.html.")
    parser.add_argument("report", type=Path, help="the report .md file")
    parser.add_argument("--out", type=Path, help="where to write the HTML (default: next to the report)")
    args = parser.parse_args(argv)

    if not args.report.is_file() or args.report.suffix.lower() != ".md":
        print(f"error: expected an existing .md file: {args.report}", file=sys.stderr)
        return 2
    out = args.out or args.report.with_suffix(".html")
    out.write_text(page(args.report.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
