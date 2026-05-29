#!/usr/bin/env python3
"""Validate PaperSpine humanize_matrix.md and scan for remaining AI patterns.

Self-contained — standard library only, no dependencies on other PaperSpine
modules.  Can be distributed standalone with paper-spine-humanize skill.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path


# --- self-contained table helpers (no _paper_spine_utils import) ---

def _split_table_line(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_sep(cells: list[str]) -> bool:
    return bool(cells) and all(c and set(c) <= {"-", ":", " "} for c in cells)


def _table_rows(text: str) -> tuple[list[str], list[list[str]]]:
    rows: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = _split_table_line(line)
        if _is_sep(cells):
            continue
        rows.append(cells)
    return (rows[0], rows[1:]) if rows else ([], [])


def _split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if len(p.strip()) > 50]


# --- AI pattern detection ---

AI_CONNECTORS_ZH = [
    "首先", "其次", "再次", "最后", "综上所述", "总而言之", "总的来说",
    "此外", "另外", "不仅如此", "值得注意的是", "需要指出的是", "不容忽视的是",
    "具有重要意义", "具有重要的理论意义", "具有重要的现实意义",
    "为……奠定基础", "在……的过程中",
]
AI_CONNECTORS_EN = [
    "firstly", "secondly", "thirdly", "finally", "in conclusion", "to sum up",
    "furthermore", "moreover", "additionally", "it is worth noting",
    "it should be pointed out", "it cannot be ignored", "plays a crucial role",
    "has significant implications",
]

CNKI_DIMENSIONS = (
    "sentence structure", "paragraph similarity", "information density",
    "connector frequency", "term-context matching",
)


@dataclass
class HumanizeCheckResult:
    path: str
    ok: bool
    matrix_rows: int = 0
    manuscript_paragraphs: int = 0
    coverage_ratio: float = 0.0
    sentence_length_stddev: float = 0.0
    connector_density: float = 0.0
    findings: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PaperSpine humanize_matrix.md")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write humanize_report.md")
    return parser.parse_args()


def sentence_lengths(text: str) -> list[int]:
    sents = re.split(r"[.。!！?？;；\n]+", text)
    return [len(s.strip()) for s in sents if 5 < len(s.strip()) < 300]


def count_connectors(text: str, lang: str) -> int:
    pool = AI_CONNECTORS_ZH if lang == "zh" else AI_CONNECTORS_EN
    return sum(text.count(c) for c in pool)


def check_matrix(matrix_path: Path, manuscript_text: str, lang: str) -> HumanizeCheckResult:
    result = HumanizeCheckResult(str(matrix_path), False)
    if not matrix_path.exists():
        result.findings.append("humanize_matrix.md not found")
        return result

    text = matrix_path.read_text(encoding="utf-8", errors="ignore")
    header, rows = _table_rows(text)
    if not header:
        result.findings.append("humanize_matrix.md has no parseable table")
        return result

    result.matrix_rows = len(rows)
    result.manuscript_paragraphs = len(_split_paragraphs(manuscript_text))
    if result.manuscript_paragraphs > 0:
        result.coverage_ratio = result.matrix_rows / result.manuscript_paragraphs

    if result.coverage_ratio < 0.5 and result.manuscript_paragraphs > 2:
        result.findings.append(
            f"Coverage {result.coverage_ratio:.0%}: {result.matrix_rows} rows for "
            f"{result.manuscript_paragraphs} paragraphs. Minimum 50%."

        )

    header_text = " ".join(c.lower() for c in header)
    for col in ("ai pattern", "detection dim", "severity", "applied change", "teaching"):
        if col not in header_text:
            result.findings.append(f"Missing column: {col}")

    empty_rows = [i for i, row in enumerate(rows, start=1) if any(not c.strip() for c in row)]
    if empty_rows:
        result.findings.append(f"Rows with empty cells: {empty_rows[:8]}")

    severity_counts = {"high": 0, "medium": 0, "low": 0}
    dim_hits: set[str] = set()
    for row in rows:
        joined = " ".join(row).lower()
        for sev in severity_counts:
            if sev in joined:
                severity_counts[sev] += 1
        for dim in CNKI_DIMENSIONS:
            if dim in joined:
                dim_hits.add(dim)
    if result.matrix_rows > 2 and severity_counts["high"] == 0:
        result.findings.append("No high-severity patterns found — matrix may be under-reporting")

    missing_dims = set(CNKI_DIMENSIONS) - dim_hits
    if missing_dims:
        result.findings.append(f"Dimensions not covered: {', '.join(sorted(missing_dims))}")

    lengths = sentence_lengths(manuscript_text)
    if len(lengths) > 2:
        result.sentence_length_stddev = round(statistics.stdev(lengths), 2)
        if result.sentence_length_stddev < 6:
            result.findings.append(
                f"Sentence length stddev = {result.sentence_length_stddev} — too uniform. "
                "AI text typically < 6; human text > 10."
            )

    char_count = len(manuscript_text)
    conn_count = count_connectors(manuscript_text, lang)
    if char_count > 0:
        result.connector_density = round(conn_count / (char_count / 1000), 2)
        threshold = 8
        if result.connector_density > threshold:
            result.findings.append(
                f"Connector density = {result.connector_density}/1k chars (threshold: {threshold}). "
                "High connector density is a strong AI signal."
            )

    # Check for long dash separators (common AI pattern)
    dash_pattern = re.search(r"[—\-—―]{3,}", manuscript_text)
    if dash_pattern:
        result.findings.append(
            "Long dash separators detected (e.g. '————'). "
            "These are a strong AI-generation signal — replace with section headings or blank lines."
        )

    result.ok = not result.findings
    return result


def to_markdown(result: HumanizeCheckResult) -> str:
    lines = [
        "# Humanize Check Report",
        "",
        f"- Matrix path: `{result.path}`",
        f"- Matrix rows: {result.matrix_rows}",
        f"- Manuscript paragraphs: {result.manuscript_paragraphs}",
        f"- Coverage: {result.coverage_ratio:.0%}",
        f"- Sentence length stddev: {result.sentence_length_stddev}",
        f"- Connector density: {result.connector_density}/1k chars",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- {f}" for f in result.findings) if result.findings else lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    matrix_path = out_dir / "humanize_matrix.md"

    if not matrix_path.exists():
        print(f"Matrix not found: {matrix_path}", file=sys.stderr)
        return 2

    lang = "zh"
    config_path = out_dir / "paper_spine_config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            lang = config.get("output_language", "zh")
        except json.JSONDecodeError:
            pass

    manuscript_text = ""
    final_paper = out_dir / "final_paper"
    if final_paper.is_dir():
        for f in final_paper.glob("*.tex"):
            manuscript_text += f.read_text(encoding="utf-8", errors="ignore") + "\n"

    result = check_matrix(matrix_path, manuscript_text, lang)

    if args.json:
        print(json.dumps({
            "ok": result.ok, "matrix_rows": result.matrix_rows,
            "paragraphs": result.manuscript_paragraphs,
            "coverage": result.coverage_ratio,
            "sentence_stddev": result.sentence_length_stddev,
            "connector_density": result.connector_density,
            "findings": result.findings,
        }, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(result))

    if args.write:
        report_path = out_dir / "humanize_report.md"
        report_path.write_text(to_markdown(result), encoding="utf-8")
        print(f"Wrote {report_path}", file=sys.stderr)

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
