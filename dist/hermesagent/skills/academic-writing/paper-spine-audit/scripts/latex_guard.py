#!/usr/bin/env python3
"""Guard checks for LaTeX manuscripts.

This is not a replacement for compilation. It catches common structural issues
early so prose revision does not silently damage labels, citations, figures, or
environments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


GRAPHIC_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".tif", ".tiff"]


@dataclass
class Finding:
    severity: str
    check: str
    message: str
    line: int | None = None


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        cut = None
        for match in re.finditer(r"(?<!\\)%", line):
            cut = match.start()
            break
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_bib_keys(path: Path | None) -> set[str]:
    if not path:
        return set()
    text = read_text(path)
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))


def check_document_markers(text: str) -> list[Finding]:
    findings: list[Finding] = []
    if "\\begin{document}" not in text:
        findings.append(Finding("error", "document", "Missing \\begin{document}."))
    if "\\end{document}" not in text:
        findings.append(Finding("error", "document", "Missing \\end{document}."))
    return findings


def check_merge_markers(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for marker in ("<<<<<<<", "=======", ">>>>>>>"):
        index = text.find(marker)
        if index >= 0:
            findings.append(
                Finding("error", "merge-marker", f"Found merge/conflict marker {marker}.", line_number(text, index))
            )
    return findings


def check_braces(text: str) -> list[Finding]:
    findings: list[Finding] = []
    stack: list[tuple[str, int]] = []
    for match in re.finditer(r"(?<!\\)[{}]", text):
        token = match.group(0)
        if token == "{":
            stack.append((token, line_number(text, match.start())))
        elif stack:
            stack.pop()
        else:
            findings.append(Finding("error", "braces", "Closing brace without matching opening brace.", line_number(text, match.start())))
    for _, line in stack[-10:]:
        findings.append(Finding("error", "braces", "Opening brace without matching closing brace.", line))
    return findings


def check_environments(text: str) -> list[Finding]:
    findings: list[Finding] = []
    stack: list[tuple[str, int]] = []
    for match in re.finditer(r"\\(begin|end)\{([^{}]+)\}", text):
        action, env = match.group(1), match.group(2)
        line = line_number(text, match.start())
        if action == "begin":
            stack.append((env, line))
            continue
        if not stack:
            findings.append(Finding("error", "environment", f"\\end{{{env}}} has no matching begin.", line))
            continue
        last_env, last_line = stack.pop()
        if last_env != env:
            findings.append(
                Finding(
                    "error",
                    "environment",
                    f"\\end{{{env}}} closes \\begin{{{last_env}}} from line {last_line}.",
                    line,
                )
            )
    for env, line in stack[-10:]:
        findings.append(Finding("error", "environment", f"\\begin{{{env}}} is not closed.", line))
    return findings


def check_labels_and_refs(text: str) -> list[Finding]:
    findings: list[Finding] = []
    labels: dict[str, int] = {}
    for match in re.finditer(r"\\label\{([^{}]+)\}", text):
        key = match.group(1)
        line = line_number(text, match.start())
        if key in labels:
            findings.append(Finding("error", "label", f"Duplicate label `{key}` also defined at line {labels[key]}.", line))
        else:
            labels[key] = line

    ref_pattern = re.compile(r"\\(?:ref|autoref|cref|Cref|eqref)\{([^{}]+)\}")
    for match in ref_pattern.finditer(text):
        keys = [item.strip() for item in match.group(1).split(",") if item.strip()]
        for key in keys:
            if key not in labels:
                findings.append(Finding("warning", "reference", f"Reference `{key}` has no matching label.", line_number(text, match.start())))
    return findings


def check_citations(text: str, bib_keys: set[str], bib_was_provided: bool) -> list[Finding]:
    findings: list[Finding] = []
    cite_pattern = re.compile(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^{}]+)\}")
    used: set[str] = set()
    for match in cite_pattern.finditer(text):
        keys = [item.strip() for item in match.group(1).split(",") if item.strip()]
        used.update(keys)
        if bib_was_provided:
            for key in keys:
                if "#" in key:
                    continue
                if key not in bib_keys:
                    findings.append(Finding("error", "citation", f"Citation key `{key}` not found in BibTeX file.", line_number(text, match.start())))
    if used and not bib_was_provided:
        findings.append(Finding("warning", "citation", "Citations found, but no --bib file was provided."))
    return findings


def graphic_paths(text: str, tex_dir: Path) -> list[Path]:
    paths = [tex_dir]
    match = re.search(r"\\graphicspath\{((?:\{[^{}]+\})+)\}", text, flags=re.DOTALL)
    if not match:
        return paths
    for item in re.findall(r"\{([^{}]+)\}", match.group(1)):
        paths.append((tex_dir / item).resolve())
    return paths


def graphic_exists(name: str, roots: list[Path]) -> bool:
    candidate = Path(name)
    names = [candidate] if candidate.suffix else [Path(str(candidate) + ext) for ext in GRAPHIC_EXTENSIONS]
    for root in roots:
        for item in names:
            if (root / item).exists():
                return True
    return False


def check_graphics(text: str, tex_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    roots = graphic_paths(text, tex_path.parent)
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}")
    for match in pattern.finditer(text):
        name = match.group(1)
        if not graphic_exists(name, roots):
            findings.append(Finding("warning", "graphics", f"Graphic `{name}` was not found relative to known graphic paths.", line_number(text, match.start())))
    return findings


def check_placeholders(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for pattern in (r"\[NEED DATA:[^\]]*\]", r"\[NEED CITATION:[^\]]*\]", r"TODO", r"FIXME"):
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append(Finding("warning", "placeholder", f"Placeholder remains: {match.group(0)}", line_number(text, match.start())))
    return findings


def check_alignment_tabs(text: str) -> list[Finding]:
    findings: list[Finding] = []
    math_or_table_envs = {
        "align",
        "align*",
        "array",
        "tabular",
        "tabularx",
        "matrix",
        "pmatrix",
        "bmatrix",
        "cases",
        "split",
    }
    stack: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\\(begin|end)\{([^{}]+)\}", line):
            if match.group(1) == "begin":
                stack.append(match.group(2))
            elif stack:
                stack.pop()
        if "&" in line and r"\&" not in line:
            active = set(stack)
            if not active.intersection(math_or_table_envs):
                findings.append(Finding("warning", "special-char", "Unescaped `&` may break LaTeX outside tables/math.", number))
    return findings


def run_checks(tex_path: Path, bib_path: Path | None) -> list[Finding]:
    raw = read_text(tex_path)
    text = strip_comments(raw)
    bib_keys = parse_bib_keys(bib_path)
    findings: list[Finding] = []
    findings.extend(check_document_markers(text))
    findings.extend(check_merge_markers(text))
    findings.extend(check_braces(text))
    findings.extend(check_environments(text))
    findings.extend(check_labels_and_refs(text))
    findings.extend(check_citations(text, bib_keys, bib_path is not None))
    findings.extend(check_graphics(text, tex_path))
    findings.extend(check_placeholders(text))
    findings.extend(check_alignment_tabs(text))
    return findings


def render_markdown(tex_path: Path, bib_path: Path | None, findings: list[Finding]) -> str:
    errors = [item for item in findings if item.severity == "error"]
    warnings = [item for item in findings if item.severity == "warning"]
    lines = ["# LaTeX Guard Report", ""]
    lines.append(f"- TeX file: `{tex_path}`")
    lines.append(f"- BibTeX file: `{bib_path}`" if bib_path else "- BibTeX file: not provided")
    lines.append(f"- Errors: {len(errors)}")
    lines.append(f"- Warnings: {len(warnings)}")
    lines.append("")
    if findings:
        lines.append("| Severity | Check | Line | Message |")
        lines.append("|---|---|---:|---|")
        for item in findings:
            line = "" if item.line is None else str(item.line)
            message = item.message.replace("|", "\\|")
            lines.append(f"| {item.severity} | {item.check} | {line} | {message} |")
    else:
        lines.append("No guard issues found.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run structural guard checks for a LaTeX manuscript.")
    parser.add_argument("tex", type=Path, help="Main .tex file.")
    parser.add_argument("--bib", type=Path, help="Optional .bib file for citation-key checks.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown (default).")
    args = parser.parse_args(argv)

    if not args.tex.exists():
        print(f"TeX file not found: {args.tex}", file=sys.stderr)
        return 2
    if args.bib and not args.bib.exists():
        print(f"BibTeX file not found: {args.bib}", file=sys.stderr)
        return 2

    findings = run_checks(args.tex.resolve(), args.bib.resolve() if args.bib else None)
    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2, ensure_ascii=False))
    else:
        print(render_markdown(args.tex.resolve(), args.bib.resolve() if args.bib else None, findings), end="")

    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
