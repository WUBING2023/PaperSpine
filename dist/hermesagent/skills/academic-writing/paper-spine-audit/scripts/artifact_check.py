#!/usr/bin/env python3
"""Check whether required PaperSpine workflow artifacts exist and are usable."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from _paper_spine_utils import (
    is_separator_row,
    markdown_tables,
    split_table_line,
    table_rows,
    year_from_row,
)


WORKFLOWS = ("rewrite_existing", "build_from_materials")
TIERS = ("flash", "pro")
PDF_POLICIES = ("auto", "always", "never")
WORD_POLICIES = ("auto", "always", "never")

COMMON = (
    "paper_spine_config.json",
    "paper_spine_config.md",
    "source_map.md",
    "reference_materials/source_index.md",
    "research_dossier.md",
    "exemplar_learning_dossier.md",
    "style_profile.md",
    "sota_gap_map.md",
    "motivation_options_after_research.md",
    "citation_support_bank.md",
    "confirmed_motivation.md",
    "section_blueprints.md",
    "writing_rationale_matrix.md",
)
REWRITE = (
    "original_logic_map.md",
    "evidence_bank.md",
    "rewrite_matrix.md",
    "logic_transfer_audit.md",
)
BUILD = (
    "source_inventory.md",
    "evidence_bank.md",
    "figure_asset_map.md",
    "claim_register.md",
)
FINAL_LATEX = (
    "latex_report.md",
    "final_artifact_manifest.md",
    "final_paper/main.tex",
)
FINAL_PDF = (
    "final_paper/paper.pdf",
)
FINAL_WORD = (
    "final_paper/paper.docx",
    "word_report.md",
)
TRANSLATION_COMMON = (
    "translation_zh/manifest.md",
    "translation_zh/translation_coverage.md",
    "translation_zh/paper_spine_config.zh.md",
    "translation_zh/source_map.zh.md",
    "translation_zh/reference_materials/source_index.zh.md",
    "translation_zh/research_dossier.zh.md",
    "translation_zh/exemplar_learning_dossier.zh.md",
    "translation_zh/style_profile.zh.md",
    "translation_zh/sota_gap_map.zh.md",
    "translation_zh/motivation_options_after_research.zh.md",
    "translation_zh/citation_support_bank.zh.md",
    "translation_zh/confirmed_motivation.zh.md",
    "translation_zh/section_blueprints.zh.md",
    "translation_zh/writing_rationale_matrix.zh.md",
    "translation_zh/final_structure.zh.md",
    "translation_zh/final_paper.zh.md",
    "translation_zh/full_paper_translation.zh.md",
    "translation_zh/latex_report.zh.md",
    "translation_zh/final_artifact_manifest.zh.md",
    "translation_zh/artifact_check.zh.md",
)
TRANSLATION_REWRITE = (
    "translation_zh/original_logic_map.zh.md",
    "translation_zh/rewrite_matrix.zh.md",
    "translation_zh/logic_transfer_audit.zh.md",
)
TRANSLATION_BUILD = (
    "translation_zh/source_inventory.zh.md",
    "translation_zh/evidence_bank.zh.md",
    "translation_zh/figure_asset_map.zh.md",
    "translation_zh/claim_register.zh.md",
)

GENERIC_CELL_VALUES = {
    "",
    "-",
    "--",
    "n/a",
    "na",
    "none",
    "todo",
    "tbd",
    "x",
    "improve clarity",
    "make academic",
    "polish wording",
    "add detail",
    "提升清晰度",
    "学术化",
    "润色",
    "补充细节",
    "待定",
    "无",
}
BAD_GENERIC_PHRASES = (
    "improve clarity",
    "make academic",
    "polish wording",
    "add detail",
    "提升清晰度",
    "学术化",
    "润色",
    "补充细节",
)
FRAMEWORK_TERMS = (
    "framework",
    "whole-paper",
    "overall",
    "structure",
    "spine",
    "throughline",
    "architecture",
    "框架",
    "整体",
    "全文",
    "全局",
    "结构",
    "主线",
)

RATIONALE_MIN_ROWS = 8
RATIONALE_MIN_CHARS = 320
FRAMEWORK_MIN_CHARS = 500
TRANSLATION_MIN_RATIO = 0.30
CITATION_BANK_MULTIPLIER = 3
CITATION_BANK_RECENT_RATIO = 0.80
CURRENT_YEAR = 2026

TRANSLATION_SOURCE_BY_TARGET = {
    "translation_zh/paper_spine_config.zh.md": "paper_spine_config.md",
    "translation_zh/source_map.zh.md": "source_map.md",
    "translation_zh/reference_materials/source_index.zh.md": "reference_materials/source_index.md",
    "translation_zh/research_dossier.zh.md": "research_dossier.md",
    "translation_zh/exemplar_learning_dossier.zh.md": "exemplar_learning_dossier.md",
    "translation_zh/style_profile.zh.md": "style_profile.md",
    "translation_zh/sota_gap_map.zh.md": "sota_gap_map.md",
    "translation_zh/motivation_options_after_research.zh.md": "motivation_options_after_research.md",
    "translation_zh/citation_support_bank.zh.md": "citation_support_bank.md",
    "translation_zh/confirmed_motivation.zh.md": "confirmed_motivation.md",
    "translation_zh/section_blueprints.zh.md": "section_blueprints.md",
    "translation_zh/writing_rationale_matrix.zh.md": "writing_rationale_matrix.md",
    "translation_zh/final_structure.zh.md": "final_structure.md",
    "translation_zh/final_paper.zh.md": "final_paper.md",
    "translation_zh/full_paper_translation.zh.md": "final_paper/main.tex",
    "translation_zh/latex_report.zh.md": "latex_report.md",
    "translation_zh/final_artifact_manifest.zh.md": "final_artifact_manifest.md",
    "translation_zh/artifact_check.zh.md": "artifact_check.md",
    "translation_zh/original_logic_map.zh.md": "original_logic_map.md",
    "translation_zh/rewrite_matrix.zh.md": "rewrite_matrix.md",
    "translation_zh/logic_transfer_audit.zh.md": "logic_transfer_audit.md",
    "translation_zh/source_inventory.zh.md": "source_inventory.md",
    "translation_zh/evidence_bank.zh.md": "evidence_bank.md",
    "translation_zh/figure_asset_map.zh.md": "figure_asset_map.md",
    "translation_zh/claim_register.zh.md": "claim_register.md",
}

RATIONALE_ANCHOR_CATEGORIES = {
    "motivation": ("motivation", "spine", "throughline", "动机", "主线", "贡献"),
    "reference": ("reference", "sota", "example", "pattern", "paper", "literature", "参考", "样例", "论文", "文献"),
    "target": ("target", "scene", "venue", "journal", "conference", "competition", "rubric", "norm", "目标", "场景", "期刊", "会议", "比赛", "评分", "规范"),
    "evidence": ("evidence", "figure", "table", "result", "citation", "data", "source", "claim", "证据", "图", "表", "结果", "引用", "数据", "素材", "主张"),
    "text_move": ("reframe", "rewrite", "move", "place", "sequence", "contrast", "echo", "narrow", "写作", "重构", "改写", "前后呼应", "收束", "对照"),
}


@dataclass
class CheckResult:
    output_dir: str
    workflow: str
    tier: str
    pdf_policy: str
    tex_engine: str
    word_policy: str
    translation_required: bool
    required: list[str]
    missing: list[str]
    content_issues: list[str]

    @property
    def ok(self) -> bool:
        return not self.missing and not self.content_issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check PaperSpine artifacts.")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--workflow", choices=WORKFLOWS)
    parser.add_argument("--tier", choices=TIERS)
    parser.add_argument(
        "--pdf-policy",
        choices=PDF_POLICIES,
        default="auto",
        help="Require final_paper/paper.pdf: auto when a TeX engine exists, always, or never.",
    )
    parser.add_argument(
        "--word-policy",
        choices=WORD_POLICIES,
        default="auto",
        help="Require Word artifacts: auto when requested/present, always, or never.",
    )
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write artifact_check.md into the output directory.",
    )
    return parser.parse_args()


def read_config(output_dir: Path) -> dict[str, object]:
    config_path = output_dir / "paper_spine_config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def detect_tex_engine() -> str:
    for name in ("latexmk", "xelatex", "pdflatex"):
        path = shutil.which(name)
        if path:
            return name
    return ""


def config_requests_word(config: dict[str, object]) -> bool:
    value = config.get("word_output")
    return value is True or str(value).lower() in {"docx", "word", "true", "yes"}


def config_requests_translation(config: dict[str, object]) -> bool:
    language = str(config.get("output_language") or "").lower()
    package = str(config.get("translation_package") or "").lower()
    return language == "en" and package == "zh"


def required_artifacts(
    workflow: str,
    output_dir: Path,
    config: dict[str, object],
    pdf_policy: str,
    word_policy: str,
    tex_engine: str,
) -> tuple[list[str], bool]:
    items = list(COMMON)
    if workflow == "build_from_materials":
        items.extend(BUILD)
    else:
        items.extend(REWRITE)
    items.extend(FINAL_LATEX)

    if pdf_policy == "always" or (pdf_policy == "auto" and tex_engine):
        items.extend(FINAL_PDF)

    word_exists = (output_dir / "final_paper" / "paper.docx").exists()
    if word_policy == "always" or (
        word_policy == "auto" and (word_exists or config_requests_word(config))
    ):
        items.extend(FINAL_WORD)

    translation_required = config_requests_translation(config)
    if translation_required:
        items.extend(TRANSLATION_COMMON)
        if workflow == "build_from_materials":
            items.extend(TRANSLATION_BUILD)
        else:
            items.extend(TRANSLATION_REWRITE)
    return items, translation_required


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def is_generic_cell(text: str) -> bool:
    return normalize(text).strip(" .。:：") in GENERIC_CELL_VALUES


def header_has(header: list[str], alternatives: tuple[str, ...]) -> bool:
    joined = " ".join(normalize(cell) for cell in header)
    return any(term in joined for term in alternatives)


def column_index(header: list[str], alternatives: tuple[str, ...]) -> int | None:
    for index, cell in enumerate(header):
        normalized = normalize(cell)
        if any(term in normalized for term in alternatives):
            return index
    return None


def find_rationale_table(text: str) -> tuple[list[str], list[list[str]]] | None:
    for table in markdown_tables(text):
        if not table:
            continue
        header = table[0]
        if header_has(header, ("manuscript", "unit", "writing", "section", "单元", "段落", "章节")) and header_has(
            header, ("motivation", "动机")
        ):
            return header, table[1:]
    return None


def validate_writing_rationale_matrix(output_dir: Path) -> list[str]:
    path = output_dir / "writing_rationale_matrix.md"
    if not path.exists():
        return []

    issues: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    table = find_rationale_table(text)
    if table is None:
        return [
            "writing_rationale_matrix.md must contain a Markdown table with manuscript/writing units and motivation links."
        ]

    header, rows = table
    required_columns = {
        "manuscript unit": ("manuscript", "unit", "writing", "section", "单元", "段落", "章节"),
        "motivation link": ("motivation", "动机"),
        "reference or SOTA pattern": ("reference", "sota", "example", "样例", "参考", "文献", "优秀"),
        "target scene or venue norm": ("target", "scene", "venue", "norm", "目标", "场景", "期刊", "会议", "比赛", "规范"),
        "evidence or citation anchor": ("evidence", "citation", "anchor", "证据", "引用", "材料", "数据"),
        "planned change or text move": ("planned", "change", "move", "function", "plan", "修改", "计划", "写法", "功能"),
        "final text check": ("final", "check", "最终", "检查", "落点"),
    }
    column_map: dict[str, int] = {}
    for label, alternatives in required_columns.items():
        index = column_index(header, alternatives)
        if index is None:
            issues.append(f"writing_rationale_matrix.md is missing a `{label}` column.")
        else:
            column_map[label] = index

    if len(rows) < RATIONALE_MIN_ROWS:
        issues.append(
            f"writing_rationale_matrix.md has fewer than {RATIONALE_MIN_ROWS} rationale rows; split the manuscript/report into finer task-specific writing units."
        )

    if rows:
        first_row = " ".join(rows[0]).lower()
        if not any(term in first_row for term in FRAMEWORK_TERMS):
            issues.append(
                "writing_rationale_matrix.md first data row must justify the overall framework, structure, or throughline."
            )

    checked_rows = 0
    for row_number, row in enumerate(rows, start=1):
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        combined = " ".join(row)
        lowered = normalize(combined)
        if not lowered:
            continue
        checked_rows += 1
        rationale_cells: list[str] = []
        for label in (
            "motivation link",
            "reference or SOTA pattern",
            "target scene or venue norm",
            "evidence or citation anchor",
            "planned change or text move",
            "final text check",
        ):
            index = column_map.get(label)
            if index is None or index >= len(row):
                continue
            value = row[index]
            rationale_cells.append(value)
            if is_generic_cell(value):
                issues.append(f"writing_rationale_matrix.md row {row_number} has a generic or empty `{label}` cell.")
        rationale_text = " ".join(rationale_cells).strip()
        if len(rationale_text) < RATIONALE_MIN_CHARS:
            issues.append(
                f"writing_rationale_matrix.md row {row_number} rationale is too thin; explain the writing decision with motivation, reference/SOTA, target-scene, evidence, and text-move anchors."
            )
        if row_number == 1 and len(rationale_text) < FRAMEWORK_MIN_CHARS:
            issues.append(
                "writing_rationale_matrix.md first data row is too shallow; the whole-work framework row must deeply justify the controlling structure before section-level writing."
            )
        category_hits = sum(
            1 for terms in RATIONALE_ANCHOR_CATEGORIES.values() if any(term in lowered for term in terms)
        )
        required_hits = 5 if row_number == 1 else 4
        if category_hits < required_hits:
            issues.append(
                f"writing_rationale_matrix.md row {row_number} lacks enough concrete anchors; include motivation, learned reference/SOTA pattern, target-scene norm, evidence/citation, and the planned text move."
            )
        if any(phrase in lowered for phrase in BAD_GENERIC_PHRASES) and not any(
            token in lowered for token in ("because", "动机", "evidence", "sota", "reference", "目标", "证据", "引用")
        ):
            issues.append(
                f"writing_rationale_matrix.md row {row_number} uses generic polishing language without a concrete anchor."
            )
        if len(issues) >= 25:
            issues.append("writing_rationale_matrix.md has additional issues not shown; fix the matrix and rerun the check.")
            break

    if checked_rows == 0:
        issues.append("writing_rationale_matrix.md has no usable rationale rows.")
    return issues


def table_row_count(text: str) -> int:
    table = find_rationale_table(text)
    if table is None:
        return 0
    _, rows = table
    return len([row for row in rows if any(cell.strip() for cell in row)])


def find_citation_table(text: str) -> tuple[list[str], list[list[str]]] | None:
    for table in markdown_tables(text):
        if not table:
            continue
        header = table[0]
        joined = " ".join(normalize(cell) for cell in header)
        has_reference = any(term in joined for term in ("citation", "reference", "bibtex"))
        if has_reference and "claim" in joined and "sentence" in joined:
            return header, table[1:]
    return None


def validate_citation_support_bank(output_dir: Path, config: dict[str, object]) -> list[str]:
    path = output_dir / "citation_support_bank.md"
    if not path.exists():
        return []
    issues: list[str] = []
    try:
        target_count = max(1, int(config.get("citation_target_count") or 20))
    except (TypeError, ValueError):
        target_count = 20
    required_candidates = target_count * CITATION_BANK_MULTIPLIER
    required_recent = int(required_candidates * CITATION_BANK_RECENT_RATIO + 0.999)
    recent_threshold = CURRENT_YEAR - 3

    text = path.read_text(encoding="utf-8", errors="ignore")
    table = find_citation_table(text)
    if table is None:
        return [
            "citation_support_bank.md must contain a Markdown table with reference/citation, claim, and sentence columns."
        ]
    _, rows = table
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if len(rows) < required_candidates:
        issues.append(
            f"citation_support_bank.md has fewer than {required_candidates} candidates; create 3x the target citation count before selecting final citations."
        )
    recent_rows = [row for row in rows if (year_from_row(row) or 0) >= recent_threshold]
    if len(recent_rows) < required_recent:
        issues.append(
            f"citation_support_bank.md should keep about 80% recent candidates since {recent_threshold}; found {len(recent_rows)} of required {required_recent}."
        )
    weak_rows = []
    for index, row in enumerate(rows[:required_candidates], start=1):
        joined = " ".join(row)
        has_reference = any(token in joined for token in ("@", "doi", "DOI", "http", "arXiv", "Journal", "Proceedings"))
        has_sentence = len(joined) >= 80 and bool(re.search(r"[.!?。！？]", joined))
        if not has_reference or not has_sentence:
            weak_rows.append(index)
    if weak_rows:
        issues.append(
            "citation_support_bank.md rows must pair each paper with one or two usable support sentences; weak rows include "
            + ", ".join(str(row) for row in weak_rows[:8])
            + "."
        )
    return issues


def validate_translation_package(output_dir: Path, required: list[str]) -> list[str]:
    issues: list[str] = []
    coverage_path = output_dir / "translation_zh" / "translation_coverage.md"
    coverage_text = ""
    if coverage_path.exists():
        coverage_text = coverage_path.read_text(encoding="utf-8", errors="ignore")
        coverage_lower = coverage_text.lower()
        if any(status in coverage_lower for status in ("missing", "partial", "not translated", "未翻译", "缺失", "部分")):
            issues.append("translation_zh/translation_coverage.md reports missing or partial translation.")

    required_translation_targets = [name for name in required if name.startswith("translation_zh/")]
    for target_name in required_translation_targets:
        source_name = TRANSLATION_SOURCE_BY_TARGET.get(target_name)
        if coverage_text and target_name not in coverage_text and Path(target_name).name not in coverage_text:
            issues.append(f"translation_zh/translation_coverage.md does not mention `{target_name}`.")
        if not source_name:
            continue
        source_path = output_dir / source_name
        target_path = output_dir / target_name
        if not source_path.exists() or not target_path.exists():
            continue
        source_text = source_path.read_text(encoding="utf-8", errors="ignore")
        target_text = target_path.read_text(encoding="utf-8", errors="ignore")
        if len(source_text.strip()) >= 300:
            minimum = max(120, int(len(source_text.strip()) * TRANSLATION_MIN_RATIO))
            if len(target_text.strip()) < minimum:
                issues.append(
                    f"{target_name} appears too short for a complete translation of {source_name}; translate the full artifact, not only a summary."
                )

    source_matrix = output_dir / "writing_rationale_matrix.md"
    target_matrix = output_dir / "translation_zh" / "writing_rationale_matrix.zh.md"
    if source_matrix.exists() and target_matrix.exists():
        source_rows = table_row_count(source_matrix.read_text(encoding="utf-8", errors="ignore"))
        target_rows = table_row_count(target_matrix.read_text(encoding="utf-8", errors="ignore"))
        if source_rows and target_rows < source_rows:
            issues.append(
                "translation_zh/writing_rationale_matrix.zh.md must preserve and translate every row from writing_rationale_matrix.md."
            )
    return issues


def validate_content(output_dir: Path, required: list[str], translation_required: bool, config: dict[str, object]) -> list[str]:
    issues: list[str] = []
    issues.extend(validate_writing_rationale_matrix(output_dir))
    issues.extend(validate_citation_support_bank(output_dir, config))
    if translation_required:
        issues.extend(validate_translation_package(output_dir, required))
    return issues


def check(
    output_dir: Path,
    workflow: str,
    tier: str,
    config: dict[str, object],
    pdf_policy: str,
    word_policy: str,
) -> CheckResult:
    tex_engine = detect_tex_engine()
    required, translation_required = required_artifacts(
        workflow, output_dir, config, pdf_policy, word_policy, tex_engine
    )
    missing = [name for name in required if not (output_dir / name).exists()]
    content_issues = validate_content(output_dir, required, translation_required, config)
    return CheckResult(
        output_dir=str(output_dir),
        workflow=workflow,
        tier=tier,
        pdf_policy=pdf_policy,
        tex_engine=tex_engine or "not found",
        word_policy=word_policy,
        translation_required=translation_required,
        required=required,
        missing=missing,
        content_issues=content_issues,
    )


def to_markdown(result: CheckResult) -> str:
    lines = [
        "# PaperSpine Artifact Check",
        "",
        f"- Output directory: `{result.output_dir}`",
        f"- Workflow: `{result.workflow}`",
        f"- Tier: `{result.tier}`",
        f"- PDF policy: `{result.pdf_policy}`",
        f"- TeX engine: `{result.tex_engine}`",
        f"- Word policy: `{result.word_policy}`",
        f"- Translation package required: {'yes' if result.translation_required else 'no'}",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Missing",
        "",
    ]
    if result.missing:
        lines.extend(f"- `{name}`" for name in result.missing)
    else:
        lines.append("- None")
    lines.extend(["", "## Content Issues", ""])
    if result.content_issues:
        lines.extend(f"- {issue}" for issue in result.content_issues)
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    config = read_config(output_dir)
    workflow = args.workflow or str(config.get("workflow") or "rewrite_existing")
    tier = args.tier or str(config.get("tier") or "flash")
    result = check(
        output_dir,
        workflow,
        tier,
        config,
        args.pdf_policy,
        args.word_policy,
    )
    markdown = to_markdown(result)

    if args.write:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "artifact_check.md").write_text(markdown, encoding="utf-8")

    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(markdown)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

