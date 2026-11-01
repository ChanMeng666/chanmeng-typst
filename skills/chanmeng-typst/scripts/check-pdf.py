#!/usr/bin/env python3
"""Check a compiled Typst PDF for problems the compiler does not report.

    python check-pdf.py doc.pdf [--source doc.typ ...] [--pages N | --max-pages N]
                                [--ats] [--require TEXT ...]

Requires poppler (pdfinfo, pdffonts, pdfimages, pdftotext) on PATH.
Exit codes: 0 all checks passed, 1 a check failed, 2 could not run.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = ("pdfinfo", "pdffonts", "pdfimages", "pdftotext")
INSTALL_HINT = (
    "poppler is required: winget install oschwartz10612.Poppler (Windows), "
    "brew install poppler (macOS), or apt install poppler-utils (Debian/Ubuntu)"
)
COMPOUND = re.compile(r"[A-Za-z0-9][A-Za-z0-9.]*(?:-[A-Za-z0-9.]+)+")
LOST_TILDE = re.compile(r"(?:^|[\s(\[])~\d", re.M)
ATS_LAYOUT = re.compile(r"(?<![\w-])(grid|table|columns|image)\(")

failures = []


def check(label, ok, detail=""):
    print(f"{'  ok  ' if ok else ' FAIL '} {label}{f': {detail}' if detail else ''}")
    if not ok:
        failures.append(label)


def warn(label, detail=""):
    print(f" warn  {label}{f': {detail}' if detail else ''}")


def run(*cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        sys.exit(f"{cmd[0]} failed: {result.stderr.strip()}")
    return result.stdout


def strip_comments(source):
    """Remove Typst comments, leaving string literals intact (URLs contain //)."""
    pattern = r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*'
    return re.sub(pattern, lambda m: m.group(0) if m.group(0)[0] == '"' else " ", source, flags=re.S)


def parse_info(text):
    info = {}
    for line in text.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            info[key.strip()] = value.strip()
    return info


def parse_fonts(text):
    """Return (name, embedded, unicode) rows. Columns end: emb sub uni objID gen."""
    rows = []
    for line in text.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 6:
            rows.append((parts[0], parts[-5] == "yes", parts[-3] == "yes"))
    return rows


def check_pages(info, args):
    pages = int(info.get("Pages", "0"))
    if args.pages is not None:
        check("page count", pages == args.pages, f"{pages} (want {args.pages})")
    elif args.max_pages is not None:
        check("page count", pages <= args.max_pages, f"{pages} (max {args.max_pages})")
    else:
        print(f" info  page count: {pages}")


def check_fonts(pdf):
    rows = parse_fonts(run("pdffonts", str(pdf)))
    bad_embed = [name for name, embedded, _ in rows if not embedded]
    bad_unicode = [name for name, _, unicode_map in rows if not unicode_map]
    check("fonts embedded", not bad_embed, ", ".join(bad_embed) or f"{len(rows)} fonts")
    check("fonts map to Unicode", not bad_unicode, ", ".join(bad_unicode))


def check_sources(sources, text):
    """Find source compounds whose hyphen was lost, and tildes that became spaces."""
    flat = re.sub(r"\s+", " ", text)
    lost = set()
    for path in sources:
        source = strip_comments(path.read_text(encoding="utf-8"))
        for compound in set(COMPOUND.findall(source)):
            if compound not in flat and compound.replace("-", "") in flat:
                lost.add(f"{compound} -> {compound.replace('-', '')}")
        for match in LOST_TILDE.finditer(source):
            warn("bare ~ before a digit renders as a space", f"{path.name}: {match.group(0).strip()}")
    check("hyphens survive extraction", not lost, "; ".join(sorted(lost)))


def check_ats(info, pdf, sources):
    images = len(run("pdfimages", "-list", str(pdf)).splitlines()[2:])
    check("ATS: no images", images == 0, f"{images} found" if images else "")
    check("ATS: tagged PDF", info.get("Tagged") == "yes")
    check("ATS: creation and modification dates", bool(info.get("CreationDate") and info.get("ModDate")))
    check("ATS: title set", bool(info.get("Title")))
    check("ATS: no Keywords metadata", not info.get("Keywords"), info.get("Keywords", ""))
    hits = []
    for path in sources:
        source = strip_comments(path.read_text(encoding="utf-8"))
        hits += [f"{path.name}: {m}" for m in sorted(set(ATS_LAYOUT.findall(source)))]
    check("ATS: no grid, table, columns or image in source", not hits, "; ".join(hits))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--source", type=Path, nargs="+", default=[],
                        help=".typ files to compare against (default: same name as the PDF)")
    parser.add_argument("--pages", type=int, help="exact page count required")
    parser.add_argument("--max-pages", type=int, help="maximum page count")
    parser.add_argument("--ats", action="store_true", help="apply the rules in references/ats-resume.md")
    parser.add_argument("--require", nargs="+", default=[], help="text that must survive extraction")
    args = parser.parse_args()

    missing = [tool for tool in TOOLS if not shutil.which(tool)]
    if missing:
        print(f"missing {', '.join(missing)}. {INSTALL_HINT}", file=sys.stderr)
        return 2
    if not args.pdf.is_file():
        print(f"{args.pdf} not found. Did typst compile succeed?", file=sys.stderr)
        return 2

    sources = args.source
    if not sources and args.pdf.with_suffix(".typ").is_file():
        sources = [args.pdf.with_suffix(".typ")]
    absent = [str(path) for path in sources if not path.is_file()]
    if absent:
        print(f"source not found: {', '.join(absent)}", file=sys.stderr)
        return 2

    info = parse_info(run("pdfinfo", str(args.pdf)))
    text = run("pdftotext", "-enc", "UTF-8", str(args.pdf), "-")

    check_pages(info, args)
    check_fonts(args.pdf)
    check("text extracts", bool(text.strip()), "no text: the PDF may be image-only" if not text.strip() else "")
    if sources:
        check_sources(sources, text)
    else:
        warn("no .typ source given, so hyphen and tilde checks were skipped")
    if args.ats:
        check_ats(info, args.pdf, sources)

    flat = re.sub(r"\s+", " ", text)
    for needle in args.require:
        check(f'contains "{needle}"', needle in flat)

    print(f"\n{'FAILED: ' + str(len(failures)) + ' check(s)' if failures else 'All checks passed.'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
