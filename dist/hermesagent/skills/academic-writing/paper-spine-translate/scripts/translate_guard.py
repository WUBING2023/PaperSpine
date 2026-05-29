#!/usr/bin/env python3
"""PaperSpine Translation Guard — verify translation_zh/ completeness and quality.

Checks file existence, structural preservation (table row counts for large
artifacts), content density (stricter 50% threshold), full-paper coverage,
and manifest cross-validation.  Produces a teaching-oriented report that
says *what* is missing and *how* to fix it.

Pattern: follows the writing_rationale_matrix philosophy — every finding teaches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _paper_spine_utils import markdown_tables, read_text, table_rows

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

TRANSLATION_DIR = "translation_zh"

TRANSLATION_COMMON = [
    "manifest.md",
    "translation_coverage.md",
    "paper_spine_config.zh.md",
    "source_map.zh.md",
    "reference_materials/source_index.zh.md",
    "research_dossier.zh.md",
    "exemplar_learning_dossier.zh.md",
    "style_profile.zh.md",
    "sota_gap_map.zh.md",
    "motivation_options_after_research.zh.md",
    "confirmed_motivation.zh.md",
    "section_blueprints.zh.md",
    "writing_rationale_matrix.zh.md",
    "citation_support_bank.zh.md",
    "final_structure.zh.md",
    "final_paper.zh.md",
    "full_paper_translation.zh.md",
    "latex_report.zh.md",
    "final_artifact_manifest.zh.md",
    "artifact_check.zh.md",
]

TRANSLATION_REWRITE = [
    "original_logic_map.zh.md",
    "rewrite_matrix.zh.md",
    "logic_transfer_audit.zh.md",
]

TRANSLATION_BUILD = [
    "source_inventory.zh.md",
    "evidence_bank.zh.md",
    "figure_asset_map.zh.md",
    "claim_register.zh.md",
]

# source -> target mapping for density checks
TRANSLATION_SOURCE: dict[str, str] = {}
for _t in TRANSLATION_COMMON + TRANSLATION_REWRITE + TRANSLATION_BUILD:
    _en = _t.replace(".zh.md", ".md")
    TRANSLATION_SOURCE[_t] = _en

# files that must preserve table structure (row-by-row, no summaries)
LARGE_TABULAR = {
    "writing_rationale_matrix.zh.md",
    "citation_support_bank.zh.md",
    "section_blueprints.zh.md",
    "research_dossier.zh.md",
    "exemplar_learning_dossier.zh.md",
    "sota_gap_map.zh.md",
    "original_logic_map.zh.md",
    "rewrite_matrix.zh.md",
    "source_inventory.zh.md",
    "evidence_bank.zh.md",
    "claim_register.zh.md",
}

# full paper required sections
FULL_PAPER_SECTIONS = [
    "title", "abstract", "introduction", "method", "experiment",
    "result", "discussion", "conclusion", "figure", "table",
    "caption", "limitation", "acknowledgement", "appendix",
]

MIN_DENSITY_RATIO = 0.50  # Chinese translation must be at least 50% of English source chars

# ---------------------------------------------------------------------------
# data types
# ---------------------------------------------------------------------------

@dataclass
class TranslationFinding:
    id: str
    severity: str          # BLOCKER | WARNING | INFO
    what: str
    fix: str
    teaching: str = ""


@dataclass
class TranslationGuardReport:
    output_dir: str
    workflow: str
    findings: list[TranslationFinding] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.severity == "BLOCKER" for f in self.findings)

    @property
    def total_findings(self) -> int:
        return len(self.findings)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify PaperSpine translation_zh/ completeness and quality.")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write translate_guard_report.md")
    return parser.parse_args()


def load_config(out_dir: Path) -> dict:
    config_path = out_dir / "paper_spine_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


# ---------------------------------------------------------------------------
# Check 1 — File Completeness
# ---------------------------------------------------------------------------

def check_file_completeness(trans_dir: Path, out_dir: Path, config: dict) -> list[TranslationFinding]:
    workflow = config.get("workflow", "rewrite_existing")
    required = list(TRANSLATION_COMMON)
    if workflow == "rewrite_existing":
        required.extend(TRANSLATION_REWRITE)
    else:
        required.extend(TRANSLATION_BUILD)

    findings: list[TranslationFinding] = []
    missing = [f for f in required if not (trans_dir / f).exists()]
    present = [f for f in required if (trans_dir / f).exists()]

    for f in missing:
        en_name = TRANSLATION_SOURCE.get(f, f)
        findings.append(TranslationFinding(
            id=f"FILE-{len(findings)+1:03d}",
            severity="BLOCKER",
            what=f"Missing translation: `translation_zh/{f}`",
            fix=f"Translate `{en_name}` into `translation_zh/{f}`. "
                f"Use `paper-spine-translate` to produce this file.",
            teaching=f"Every intermediate artifact needs a Chinese counterpart. "
                      f"`{en_name}` is a required PaperSpine artifact — its translation "
                      f"is not optional.",
        ))

    if not findings and present:
        findings.append(TranslationFinding(
            id="FILE-000", severity="INFO",
            what=f"All {len(required)} required translation files present",
            fix="", teaching="",
        ))
    return findings


# ---------------------------------------------------------------------------
# Check 2 — Structural Preservation (table rows for large tabular artifacts)
# ---------------------------------------------------------------------------

def check_structural_preservation(trans_dir: Path, out_dir: Path) -> list[TranslationFinding]:
    findings: list[TranslationFinding] = []
    for zh_name in sorted(LARGE_TABULAR):
        zh_path = trans_dir / zh_name
        if not zh_path.exists():
            continue
        en_name = TRANSLATION_SOURCE.get(zh_name, "")
        en_path = out_dir / en_name
        if not en_path.exists():
            continue

        zh_text = zh_path.read_text(encoding="utf-8", errors="ignore")
        en_text = en_path.read_text(encoding="utf-8", errors="ignore")

        if "|" in en_text:
            _, en_rows = table_rows(en_text)
            _, zh_rows = table_rows(zh_text)
            en_count = len(en_rows)
            zh_count = len(zh_rows)

            if zh_count < en_count:
                findings.append(TranslationFinding(
                    id=f"STRUCT-{len(findings)+1:03d}",
                    severity="BLOCKER",
                    what=f"`{zh_name}` has {zh_count} table rows vs {en_count} in source — "
                          f"missing {en_count - zh_count} rows",
                    fix=f"Translate every row of `{en_name}` into `{zh_name}`. "
                        f"Row-by-row translation is mandatory for this file — "
                        f"a shortened summary table is a failed output.",
                    teaching="Large tabular artifacts must preserve their row structure in translation. "
                            "Each row represents a unit of reasoning or a citation candidate — "
                            "losing rows means losing information the reader needs.",
                ))

    if not findings:
        tabular_present = [f for f in LARGE_TABULAR if (trans_dir / f).exists()]
        if tabular_present:
            findings.append(TranslationFinding(
                id="STRUCT-000", severity="INFO",
                what=f"Table structure preserved in all {len(tabular_present)} checked tabular files",
                fix="", teaching="",
            ))
    return findings


# ---------------------------------------------------------------------------
# Check 3 — Content Density
# ---------------------------------------------------------------------------

def check_content_density(trans_dir: Path, out_dir: Path) -> list[TranslationFinding]:
    findings: list[TranslationFinding] = []
    for zh_name, en_name in sorted(TRANSLATION_SOURCE.items()):
        zh_path = trans_dir / zh_name
        en_path = out_dir / en_name
        if not zh_path.exists() or not en_path.exists():
            continue

        en_len = len(en_path.read_text(encoding="utf-8", errors="ignore"))
        zh_len = len(zh_path.read_text(encoding="utf-8", errors="ignore"))

        if en_len < 300:
            continue  # too short to meaningfully check

        ratio = zh_len / en_len if en_len > 0 else 0
        if ratio < MIN_DENSITY_RATIO:
            findings.append(TranslationFinding(
                id=f"DENS-{len(findings)+1:03d}",
                severity="BLOCKER" if ratio < 0.25 else "WARNING",
                what=f"`{zh_name}` is {zh_len} chars vs {en_len} in source — "
                      f"density ratio {ratio:.0%} (minimum: {MIN_DENSITY_RATIO:.0%})",
                fix=f"Expand the translation of `{zh_name}` to cover all content from `{en_name}`. "
                    f"Chinese translations typically reach 40-70% of English character count. "
                    f"At {ratio:.0%}, this file appears to be a summary, not a translation.",
                teaching="A translation should convey the same information as the source. "
                        "When a translated file is dramatically shorter than the original, "
                        "content has been lost — usually because the translator summarized instead of translating.",
            ))

    if not findings:
        checked = sum(1 for zh, en in TRANSLATION_SOURCE.items()
                      if (trans_dir / zh).exists() and (out_dir / en).exists()
                      and len((out_dir / en).read_text(encoding="utf-8", errors="ignore")) >= 300)
        findings.append(TranslationFinding(
            id="DENS-000", severity="INFO",
            what=f"Content density adequate in all {checked} checked files",
            fix="", teaching="",
        ))
    return findings


# ---------------------------------------------------------------------------
# Check 4 — Full Paper Translation Coverage
# ---------------------------------------------------------------------------

SECTION_HEADING_RE = re.compile(r"^#{1,4}\s+(.+)", re.MULTILINE)

def check_full_paper_coverage(trans_dir: Path, out_dir: Path) -> list[TranslationFinding]:
    findings: list[TranslationFinding] = []
    fp_path = trans_dir / "full_paper_translation.zh.md"
    if not fp_path.exists():
        findings.append(TranslationFinding(
            id="FULL-001", severity="BLOCKER",
            what="full_paper_translation.zh.md is missing — the most important translation file",
            fix="Translate the complete final paper (title, abstract, all sections, figure/table captions, "
                "conclusion, acknowledgements) into full_paper_translation.zh.md. "
                "This is mandatory — do not skip or summarize.",
            teaching="full_paper_translation.zh.md is the Chinese reader's primary entry point. "
                    "Without it, the translation package fails its purpose: making the paper "
                    "accessible to Chinese readers.",
        ))
        return findings

    text = fp_path.read_text(encoding="utf-8", errors="ignore")
    headings = set(m.strip().lower() for m in SECTION_HEADING_RE.findall(text))
    heading_text = " ".join(headings)
    text_lower = text.lower()

    covered = []
    missing_sections = []
    for section in FULL_PAPER_SECTIONS:
        if section in heading_text or section in text_lower:
            covered.append(section)
        else:
            missing_sections.append(section)

    if missing_sections:
        findings.append(TranslationFinding(
            id="FULL-002",
            severity="WARNING" if len(missing_sections) <= 3 else "BLOCKER",
            what=f"full_paper_translation.zh.md may be missing sections: {', '.join(missing_sections)}",
            fix=f"Check that the full paper translation covers: {', '.join(missing_sections)}. "
                f"The translation must include every section of the final paper.",
            teaching="A complete paper translation must cover all reader-facing sections. "
                    "Missing sections mean the Chinese reader cannot fully understand the paper.",
        ))

    if len(text) < 1000:
        findings.append(TranslationFinding(
            id="FULL-003", severity="BLOCKER",
            what=f"full_paper_translation.zh.md is only {len(text)} chars — far too short for a full paper",
            fix="Expand the full paper translation to cover all sections. "
                "A conference paper translation should be at least 3000+ characters.",
            teaching="A full paper translation that is shorter than the abstract "
                    "is not a translation — it's a note saying 'I was supposed to translate this.'",
        ))

    if not findings:
        findings.append(TranslationFinding(
            id="FULL-000", severity="INFO",
            what=f"Full paper translation covers {len(covered)}/{len(FULL_PAPER_SECTIONS)} expected section types",
            fix="", teaching="",
        ))
    return findings


# ---------------------------------------------------------------------------
# Check 5 — Manifest Cross-Validation
# ---------------------------------------------------------------------------

def check_manifest(trans_dir: Path, config: dict) -> list[TranslationFinding]:
    findings: list[TranslationFinding] = []
    manifest_path = trans_dir / "manifest.md"
    if not manifest_path.exists():
        findings.append(TranslationFinding(
            id="MANIFEST-001", severity="BLOCKER",
            what="translation_zh/manifest.md is missing",
            fix="Create manifest.md listing every translation file with its status (translated/missing/partial).",
            teaching="The manifest is the translation package's table of contents. "
                    "Without it, there's no way to quickly assess translation coverage.",
        ))
        return findings

    manifest_text = manifest_path.read_text(encoding="utf-8", errors="ignore")

    # Check manifest references actual files
    workflow = config.get("workflow", "rewrite_existing")
    required = list(TRANSLATION_COMMON)
    if workflow == "rewrite_existing":
        required.extend(TRANSLATION_REWRITE)
    else:
        required.extend(TRANSLATION_BUILD)

    manifest_mentions = []
    for f in required:
        filename = Path(f).name
        if filename in manifest_text or f in manifest_text:
            manifest_mentions.append(f)

    missing_from_manifest = [f for f in required if f not in manifest_mentions]
    if missing_from_manifest:
        findings.append(TranslationFinding(
            id="MANIFEST-002", severity="WARNING",
            what=f"Manifest does not reference {len(missing_from_manifest)} required files: "
                  f"{', '.join(missing_from_manifest[:5])}",
            fix="Add entries for every required translation file to manifest.md with status.",
            teaching="The manifest should be a complete inventory. "
                    "Missing entries mean the manifest is out of sync with the file system.",
        ))

    # Check manifest flags partial/missing
    if re.search(r"(missing|partial|not translated|缺失|未翻译|部分翻译)", manifest_text, re.IGNORECASE):
        findings.append(TranslationFinding(
            id="MANIFEST-003", severity="BLOCKER",
            what="Manifest reports files as missing or partially translated",
            fix="Complete the translation for all files marked as missing or partial, "
                "then update the manifest to reflect 'translated' status.",
            teaching="A translation package with self-reported gaps is incomplete. "
                    "The manifest should show all files as translated before the package passes audit.",
        ))

    if not findings:
        findings.append(TranslationFinding(
            id="MANIFEST-000", severity="INFO",
            what="Manifest is present and references all required files",
            fix="", teaching="",
        ))
    return findings


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def to_markdown(report: TranslationGuardReport) -> str:
    lines = [
        "# Translation Guard Report",
        "",
        f"- Output directory: `{report.output_dir}`",
        f"- Workflow: {report.workflow}",
        f"- Total findings: {report.total_findings}",
        f"- Status: {'BLOCKED' if report.blocked else 'PASS'}",
        "",
        "> Each finding explains *what* is missing and *how* to fix it. "
        "Translation is not optional — it's a required deliverable.",
        "",
    ]

    for f in report.findings:
        if f.severity == "INFO":
            lines.append(f"**{f.id}** PASSED: {f.what}")
            lines.append("")
            continue
        icon = "BLOCKED" if f.severity == "BLOCKER" else "WARNING"
        lines.append(f"### {f.id} — {icon}")
        lines.append("")
        lines.append(f"**What:** {f.what}")
        lines.append("")
        lines.append(f"**Fix:** {f.fix}")
        lines.append("")
        if f.teaching:
            lines.append(f"> {f.teaching}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    trans_dir = out_dir / TRANSLATION_DIR

    if not out_dir.is_dir():
        print(f"Output directory not found: {out_dir}", file=sys.stderr)
        return 2

    config = load_config(out_dir)
    trans_dir.mkdir(parents=True, exist_ok=True)

    all_findings: list[TranslationFinding] = []
    all_findings.extend(check_file_completeness(trans_dir, out_dir, config))
    all_findings.extend(check_structural_preservation(trans_dir, out_dir))
    all_findings.extend(check_content_density(trans_dir, out_dir))
    all_findings.extend(check_full_paper_coverage(trans_dir, out_dir))
    all_findings.extend(check_manifest(trans_dir, config))

    report = TranslationGuardReport(str(out_dir), config.get("workflow", "rewrite_existing"), all_findings)

    if args.json:
        print(json.dumps({
            "output_dir": str(out_dir), "blocked": report.blocked,
            "total_findings": report.total_findings,
            "findings": [{"id": f.id, "severity": f.severity, "what": f.what, "fix": f.fix} for f in all_findings],
        }, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(report))

    if args.write:
        report_path = trans_dir / "translate_guard_report.md"
        report_path.write_text(to_markdown(report), encoding="utf-8")
        print(f"Wrote {report_path}", file=sys.stderr)

    return 1 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
