#!/usr/bin/env python3
"""Check that a converted resume.tex has the same words and links as the original resume.

Usage: python compare_text.py original.pdf|original.docx|original.doc converted.tex [--json]
Words are compared ignoring case, punctuation, bullets and LaTeX code; order is not checked.
Exit code: 0 = same, 1 = differences, 2 = bad input, 3 = a needed tool is missing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_text  # noqa: E402

ORIGINAL_SUFFIXES = (".pdf", ".docx", ".doc")

ESCAPES = {
    "\\textbackslash{}": "\\", "\\textasciitilde{}": "~", "\\textasciicircum{}": "^",
    "\\&": "&", "\\%": "%", "\\$": "$", "\\#": "#", "\\_": "_", "\\{": "{", "\\}": "}",
}
# Commands whose arguments are settings, not resume text.
LAYOUT_RE = re.compile(
    r"\\(?:vspace|hspace|setlength|addtolength|pagestyle|thispagestyle|begin|end|label"
    r"|includegraphics|color|titleformat|titlespacing|setlist)\*?"
    r"(?:\s*\[[^\]]*\])?(?:\s*\{[^{}]*\})*(?:\s*\[[^\]]*\])?"
)
URL_RE = re.compile(
    r"<?(?:mailto:|https?://)[^\s<>]+>?"
    r"|[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
    r"|\b(?:www\.)?[\w-]+(?:\.[\w-]+)*\.(?:com|org|net|io|dev|me|app|co|ai|so|xyz|tech|page)\b(?:/[^\s,;)<>]*)?"
)
WORD_RE = re.compile(r"[^\W_]+(?:['.+#][^\W_]+)*[+#]*")


def tex_text(source: str) -> tuple[str, list[str]]:
    """The words a reader sees in a .tex body, and its link addresses, without compiling."""
    text = re.sub(r"(?<!\\)%.*", "", source)
    begin, end = text.find("\\begin{document}"), text.find("\\end{document}")
    text = text[begin + len("\\begin{document}") if begin != -1 else 0:end if end != -1 else len(text)]
    # Private-use characters hold escaped symbols so later steps don't treat them as LaTeX.
    for i, escape in enumerate(ESCAPES):
        text = text.replace(escape, chr(0xE000 + i))
    links = re.findall(r"\\(?:href|url)\s*\{([^{}]*)\}", text)
    text = re.sub(r"\\href\s*\{[^{}]*\}", "", text)
    text = re.sub(r"\\url\s*\{([^{}]*)\}", r"\1", text)
    text = LAYOUT_RE.sub(" ", text)
    text = re.sub(r"\\\\\*?(?:\s*\[[^\]]*\])?", "\n", text)
    text = re.sub(r"\\item\b\s*(?:\[([^\]]*)\])?", lambda m: "\n" + (m.group(1) or ""), text)
    text = re.sub(r"\\[a-zA-Z]+\*?|\\[^a-zA-Z]", " ", text)
    text = text.replace("---", "\u2014").replace("--", "\u2013").replace("~", " ")
    text = re.sub(r"[{}$]", "", text)
    for i, escape in enumerate(ESCAPES):
        text = text.replace(chr(0xE000 + i), ESCAPES[escape])
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip()), links


def normalize_link(url: str) -> str:
    url = url.strip("<>").lower().rstrip("/.,;")
    return re.sub(r"^(?:mailto:|https?://)?(?:www\.)?", "", url)


def split_links(text: str, extra: list[str]) -> tuple[str, set[str]]:
    links = {normalize_link(u) for u in URL_RE.findall(text) + extra}
    return URL_RE.sub(" ", text), links


def words(text: str) -> Counter:
    text = unicodedata.normalize("NFKC", text).replace("\u2019", "'").replace("\u2018", "'")
    return Counter(WORD_RE.findall(text.lower()))


def site_names(links: set[str]) -> set[str]:
    return {part for link in links for part in link.split("/")[0].split("@")[-1].split(".")[:-1]}


def line_with(word: str, text: str, other: str) -> str:
    """A line holding the word, preferring one the other file doesn't have word for word."""
    other_lines = {" ".join(words(line).elements()) for line in other.splitlines()}
    candidates = [line for line in text.splitlines() if word in words(line)]
    changed = [line for line in candidates if " ".join(words(line).elements()) not in other_lines]
    line = " ".join((changed or candidates or [""])[0].split())
    return line if len(line) <= 110 else line[:107] + "..."


def compare(original: dict, tex_source: str) -> dict:
    tex_plain, tex_links = tex_text(tex_source)
    orig_text, orig_links = split_links(original["text"], original.get("links", []))
    conv_text, conv_links = split_links(tex_plain, tex_links)
    orig_words, conv_words = words(orig_text), words(conv_text)

    missing, labels = [], []
    sites = site_names(conv_links)
    for word, count in sorted((orig_words - conv_words).items()):
        # "LinkedIn" shown over a hidden address may become the address itself.
        if word in sites:
            labels.append(word)
        else:
            missing.append({"word": word, "count": count, "line": line_with(word, orig_text, conv_text)})
    added = [{"word": w, "count": c, "line": line_with(w, conv_text, orig_text)}
             for w, c in sorted((conv_words - orig_words).items())]
    result = {
        "missing": missing,
        "added": added,
        "links_missing": sorted(orig_links - conv_links),
        "links_added": sorted(conv_links - orig_links),
        "link_labels_replaced": labels,
    }
    result["same"] = not any(result[k] for k in ("missing", "added", "links_missing", "links_added"))
    return result


def format_text(original: Path, converted: Path, result: dict) -> str:
    lines = [f"compare_text: {original} -> {converted}"]
    for key, title in (("missing", "In the original, not in the .tex"), ("added", "In the .tex, not in the original")):
        for item in result[key]:
            times = f" x{item['count']}" if item["count"] > 1 else ""
            lines.append(f"  {title}: {item['word']}{times}    | {item['line']}")
    for key, title in (("links_missing", "Link lost"), ("links_added", "Link not in the original")):
        lines.extend(f"  {title}: {link}" for link in result[key])
    if result["link_labels_replaced"]:
        lines.append(f"  OK: link labels shown as their address: {', '.join(result['link_labels_replaced'])}")
    lines.append("Result: same words and links" if result["same"] else "Result: differences found")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare a converted resume.tex with the original resume.")
    parser.add_argument("original", type=Path, help="the original resume: .pdf, .docx or .doc")
    parser.add_argument("converted", type=Path, help="the converted resume .tex")
    parser.add_argument("--json", action="store_true", help="print results as JSON")
    args = parser.parse_args(argv)

    if not args.original.is_file() or args.original.suffix.lower() not in ORIGINAL_SUFFIXES:
        print(f"error: expected an existing {', '.join(ORIGINAL_SUFFIXES)} file: {args.original}", file=sys.stderr)
        return 2
    if not args.converted.is_file() or args.converted.suffix.lower() != ".tex":
        print(f"error: expected an existing .tex file: {args.converted}", file=sys.stderr)
        return 2

    try:
        original = extract_text.read_resume(args.original)
    except extract_text.BadFile as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except extract_text.ToolMissing as e:
        print(f"error: {e}", file=sys.stderr)
        return 3

    result = compare(original, args.converted.read_text(encoding="utf-8", errors="replace"))
    if args.json:
        print(json.dumps({"original": str(args.original), "converted": str(args.converted), **result}, indent=2))
    else:
        # Windows consoles can't print every character a resume might contain.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
        print(format_text(args.original, args.converted, result))
    return 0 if result["same"] else 1


if __name__ == "__main__":
    sys.exit(main())
