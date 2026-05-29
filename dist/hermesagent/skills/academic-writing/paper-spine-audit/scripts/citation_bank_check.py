#!/usr/bin/env python3
"""Validate PaperSpine citation_support_bank.md."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from _paper_spine_utils import is_separator_row, split_table_line, table_rows, year_from_row

CURRENT_YEAR = 2026
DEFAULT_TARGET_COUNT = 20
DEFAULT_MULTIPLIER = 3
DEFAULT_RECENT_RATIO = 0.80


@dataclass
class CitationBankResult:
    path: str
    ok: bool
    target_count: int
    required_candidates: int
    row_count: int
    recent_count: int
    required_recent_count: int
    findings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PaperSpine citation support bank.")
    parser.add_argument("path", nargs="?", default="paper_rewriting_output/citation_support_bank.md")
    parser.add_argument("--target-count", type=int, default=DEFAULT_TARGET_COUNT)
    parser.add_argument("--multiplier", type=int, default=DEFAULT_MULTIPLIER)
    parser.add_argument("--recent-years", type=int, default=3)
    parser.add_argument("--recent-ratio", type=float, default=DEFAULT_RECENT_RATIO)
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def has_claim_sentence(row: list[str]) -> bool:
    joined = " ".join(row).strip()
    if len(joined) < 80:
        return False
    return bool(re.search(r"[.!?。！？]", joined))


def has_reference_format(row: list[str]) -> bool:
    joined = " ".join(row)
    return any(token in joined for token in ("@", "doi", "DOI", "http", "arXiv", "Proceedings", "Journal"))


def validate(path: Path, target_count: int, multiplier: int, recent_years: int, recent_ratio: float) -> CitationBankResult:
    required_candidates = target_count * multiplier
    required_recent_count = int(required_candidates * recent_ratio + 0.999)
    findings: list[str] = []
    if not path.exists():
        return CitationBankResult(str(path), False, target_count, required_candidates, 0, 0, required_recent_count, ["file does not exist"])

    text = path.read_text(encoding="utf-8", errors="ignore")
    header, rows = table_rows(text)
    if not header:
        findings.append("citation_support_bank.md must contain a Markdown table.")
    header_text = " ".join(cell.lower() for cell in header)
    if not any(term in header_text for term in ("citation", "reference", "bibtex")):
        findings.append("citation_support_bank.md table should include a `reference` or `citation` column.")
    for required in ("claim", "sentence"):
        if required not in header_text:
            findings.append(f"citation_support_bank.md table should include a `{required}` column.")

    nonempty_rows = [row for row in rows if any(cell.strip() for cell in row)]
    if len(nonempty_rows) < required_candidates:
        findings.append(
            f"citation_support_bank.md has {len(nonempty_rows)} candidates; expected at least {required_candidates} for target_count={target_count} and multiplier={multiplier}."
        )

    threshold = CURRENT_YEAR - recent_years
    recent_rows = [row for row in nonempty_rows if (year_from_row(row) or 0) >= threshold]
    if len(recent_rows) < required_recent_count:
        findings.append(
            f"citation_support_bank.md has {len(recent_rows)} recent candidates since {threshold}; expected at least {required_recent_count}."
        )

    weak_rows = []
    for index, row in enumerate(nonempty_rows[:required_candidates], start=1):
        if not has_claim_sentence(row) or not has_reference_format(row):
            weak_rows.append(index)
    if weak_rows:
        sample = ", ".join(str(value) for value in weak_rows[:8])
        findings.append(
            f"citation_support_bank.md rows need a reference format plus one or two usable claim-support sentences; weak rows include: {sample}."
        )

    return CitationBankResult(
        str(path),
        not findings,
        target_count,
        required_candidates,
        len(nonempty_rows),
        len(recent_rows),
        required_recent_count,
        findings,
    )


def to_markdown(result: CitationBankResult) -> str:
    lines = [
        "# Citation Bank Check",
        "",
        f"- Path: `{result.path}`",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        f"- Target citation count: {result.target_count}",
        f"- Required candidate rows: {result.required_candidates}",
        f"- Candidate rows: {result.row_count}",
        f"- Required recent rows: {result.required_recent_count}",
        f"- Recent rows: {result.recent_count}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- {finding}" for finding in result.findings) if result.findings else lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = validate(Path(args.path), args.target_count, args.multiplier, args.recent_years, args.recent_ratio)
    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
