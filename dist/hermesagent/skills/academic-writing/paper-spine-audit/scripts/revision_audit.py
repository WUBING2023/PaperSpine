#!/usr/bin/env python3
"""Audit whether a manuscript revision is substantive or mostly shallow edits.

The script compares original and revised .txt/.md/.tex files. It reports
near-identical revised paragraphs, mostly new paragraphs, and original
paragraphs that disappeared. Use it as a guardrail, not as a literary judge.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path

from _paper_spine_utils import (
    CanonParagraph,
    canonical,
    make_canon,
    normalize_markdown,
    normalize_tex,
    preview,
    read_text,
    similarity_canon,
    split_paragraphs,
    strip_tex_comments,
)


@dataclass
class ParagraphMatch:
    revised_index: int
    original_index: int | None
    similarity: float
    revised_preview: str
    original_preview: str


@dataclass
class AuditSummary:
    original_paragraphs: int
    revised_paragraphs: int
    near_identical_revised: int
    mostly_new_revised: int
    likely_deleted_original: int
    near_identical_ratio: float
    mostly_new_ratio: float
    likely_deleted_ratio: float
    addition_heavy: bool
    shallow_warning: bool


def normalize_text(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".tex":
        text = normalize_tex(text)
    elif suffix == ".md":
        text = normalize_markdown(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def best_matches(original: list[str], revised: list[str]) -> list[ParagraphMatch]:
    matches: list[ParagraphMatch] = []
    original_canon = [make_canon(item) for item in original]
    revised_canon = [make_canon(item) for item in revised]
    for revised_index, revised_para in enumerate(revised_canon, start=1):
        best_index: int | None = None
        best_score = 0.0
        best_original: CanonParagraph | None = None
        for original_index, original_para in enumerate(original_canon, start=1):
            score = similarity_canon(original_para, revised_para)
            if score > best_score:
                best_score = score
                best_index = original_index
                best_original = original_para
        matches.append(
            ParagraphMatch(
                revised_index=revised_index,
                original_index=best_index,
                similarity=best_score,
                revised_preview=preview(revised_para.text),
                original_preview=preview(best_original.text if best_original else ""),
            )
        )
    return matches


def deletion_count(original: list[str], revised: list[str], threshold: float) -> int:
    count = 0
    original_canon = [make_canon(item) for item in original]
    revised_canon = [make_canon(item) for item in revised]
    for original_para in original_canon:
        best = max((similarity_canon(original_para, revised_para) for revised_para in revised_canon), default=0.0)
        if best < threshold:
            count += 1
    return count


def ratio(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def audit(original_path: Path, revised_path: Path, unchanged_threshold: float, new_threshold: float) -> tuple[AuditSummary, list[ParagraphMatch]]:
    original = split_paragraphs(normalize_text(original_path, read_text(original_path)))
    revised = split_paragraphs(normalize_text(revised_path, read_text(revised_path)))
    matches = best_matches(original, revised)
    near_identical = sum(1 for item in matches if item.similarity >= unchanged_threshold)
    mostly_new = sum(1 for item in matches if item.similarity < new_threshold)
    likely_deleted = deletion_count(original, revised, new_threshold)
    mostly_new_ratio = ratio(mostly_new, len(revised))
    near_identical_ratio = ratio(near_identical, len(revised))
    deleted_ratio = ratio(likely_deleted, len(original))
    summary = AuditSummary(
        original_paragraphs=len(original),
        revised_paragraphs=len(revised),
        near_identical_revised=near_identical,
        mostly_new_revised=mostly_new,
        likely_deleted_original=likely_deleted,
        near_identical_ratio=near_identical_ratio,
        mostly_new_ratio=mostly_new_ratio,
        likely_deleted_ratio=deleted_ratio,
        addition_heavy=mostly_new_ratio > 0.35 and deleted_ratio < 0.15,
        shallow_warning=near_identical_ratio > 0.35,
    )
    return summary, matches


def md_escape(text: object) -> str:
    return str(text).replace("\n", " ").replace("|", "\\|")


def render_markdown(summary: AuditSummary, matches: list[ParagraphMatch]) -> str:
    lines = ["# Revision Audit", ""]
    lines.extend(
        [
            f"- Original paragraphs: {summary.original_paragraphs}",
            f"- Revised paragraphs: {summary.revised_paragraphs}",
            f"- Near-identical revised paragraphs: {summary.near_identical_revised} ({summary.near_identical_ratio:.1%})",
            f"- Mostly new revised paragraphs: {summary.mostly_new_revised} ({summary.mostly_new_ratio:.1%})",
            f"- Likely deleted original paragraphs: {summary.likely_deleted_original} ({summary.likely_deleted_ratio:.1%})",
            f"- Addition-heavy: {'yes' if summary.addition_heavy else 'no'}",
            f"- Shallow-warning: {'yes' if summary.shallow_warning else 'no'}",
            "",
        ]
    )
    lines.append("## Highest Similarity Revised Paragraphs")
    lines.append("")
    lines.append("| Revised Para | Original Para | Similarity | Revised Preview | Original Preview |")
    lines.append("|---:|---:|---:|---|---|")
    for item in sorted(matches, key=lambda m: m.similarity, reverse=True)[:20]:
        lines.append(
            f"| {item.revised_index} | {item.original_index or ''} | {item.similarity:.3f} | {md_escape(item.revised_preview)} | {md_escape(item.original_preview)} |"
        )
    lines.append("")
    lines.append("## Lowest Similarity Revised Paragraphs")
    lines.append("")
    lines.append("| Revised Para | Best Original Para | Similarity | Revised Preview |")
    lines.append("|---:|---:|---:|---|")
    for item in sorted(matches, key=lambda m: m.similarity)[:20]:
        lines.append(
            f"| {item.revised_index} | {item.original_index or ''} | {item.similarity:.3f} | {md_escape(item.revised_preview)} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Audit whether a manuscript revision is shallow.")
    parser.add_argument("original", type=Path, help="Original .txt/.md/.tex file.")
    parser.add_argument("revised", type=Path, help="Revised .txt/.md/.tex file.")
    parser.add_argument("--unchanged-threshold", type=float, default=0.82, help="Similarity at or above this is near-identical.")
    parser.add_argument("--new-threshold", type=float, default=0.25, help="Similarity below this is mostly new.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown (default).")
    args = parser.parse_args(argv)

    if not args.original.exists():
        print(f"Original file not found: {args.original}", file=sys.stderr)
        return 2
    if not args.revised.exists():
        print(f"Revised file not found: {args.revised}", file=sys.stderr)
        return 2

    summary, matches = audit(args.original, args.revised, args.unchanged_threshold, args.new_threshold)
    if args.json:
        print(
            json.dumps(
                {
                    "summary": asdict(summary),
                    "matches": [asdict(item) for item in matches],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_markdown(summary, matches), end="")
    return 1 if summary.shallow_warning else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
