#!/usr/bin/env python3
"""PaperSpine Integrity Audit — teaching-quality checkpoint before LaTeX.

Unlike a binary gate, this audit produces a structured report where every finding
includes a root-cause analysis, a concrete fix action, the downstream impact if
left unfixed, and a teaching note.  The report is designed to be read by both
the user and downstream PaperSpine agents so they can reason about what to fix
and why.

Pattern: follows the *writing_rationale_matrix* philosophy — every row teaches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _paper_spine_utils import (
    is_separator_row,
    markdown_tables,
    read_text,
    split_table_line,
    table_rows,
)


# ---------------------------------------------------------------------------
# data types
# ---------------------------------------------------------------------------

@dataclass
class AuditFinding:
    id: str                         # e.g. "ART-001"
    severity: str                   # BLOCKER | WARNING | INFO
    dimension: str                  # parent audit dimension
    what_was_found: str             # plain-language description
    root_cause: str                 # which upstream artifact / step is weak
    fix_action: str                 # concrete action the user or agent should take
    downstream_impact: str          # what breaks later if this is ignored
    teaching_note: str              # why this pattern matters (educates the user)


@dataclass
class AuditDimension:
    name: str
    findings: list[AuditFinding] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(f.severity == "BLOCKER" for f in self.findings):
            return "BLOCKED"
        if any(f.severity == "WARNING" for f in self.findings):
            return "WARNINGS"
        return "CLEAN"


@dataclass
class IntegrityAuditReport:
    output_dir: str
    dimensions: list[AuditDimension] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(d.status == "BLOCKED" for d in self.dimensions)

    @property
    def total_findings(self) -> int:
        return sum(len(d.findings) for d in self.dimensions)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the PaperSpine integrity audit (teaching mode).")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write integrity_audit.md to output dir")
    return parser.parse_args()


def load_config(out_dir: Path) -> dict:
    config_path = out_dir / "paper_spine_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


# ---------------------------------------------------------------------------
# Dimension 1 — Artifact Chain Audit
# ---------------------------------------------------------------------------

ARTIFACT_OWNERS: dict[str, str] = {
    "paper_spine_config.json": "paper-spine-intake",
    "research_dossier.md": "paper-spine-research",
    "exemplar_learning_dossier.md": "paper-spine-research",
    "citation_support_bank.md": "paper-spine-citation",
    "confirmed_motivation.md": "user confirmation (after paper-spine-research)",
    "section_blueprints.md": "paper-spine-rewrite / paper-spine-build",
    "writing_rationale_matrix.md": "paper-spine-rewrite / paper-spine-build",
    "original_logic_map.md": "paper-spine-rewrite",
    "evidence_bank.md": "paper-spine-rewrite / paper-spine-build",
    "rewrite_matrix.md": "paper-spine-rewrite",
    "logic_transfer_audit.md": "paper-spine-rewrite",
    "material_inventory.md": "paper-spine-build",
}

ARTIFACT_DESCRIPTIONS: dict[str, str] = {
    "writing_rationale_matrix.md": "the execution plan that explains *why* every unit is written that way",
    "research_dossier.md": "target-scene norms, requirements, and format expectations",
    "citation_support_bank.md": "the verified pool of literature to draw from during writing",
    "confirmed_motivation.md": "the user-approved controlling idea the whole paper serves",
    "evidence_bank.md": "all user-provided evidence organized for claim support",
}


def audit_artifacts(out_dir: Path, config: dict) -> AuditDimension:
    dim = AuditDimension("Artifact Chain")
    workflow = config.get("workflow", "rewrite_existing")
    required = [
        "paper_spine_config.json", "research_dossier.md",
        "exemplar_learning_dossier.md", "citation_support_bank.md",
        "confirmed_motivation.md", "section_blueprints.md",
        "writing_rationale_matrix.md",
    ]
    if workflow == "rewrite_existing":
        required.extend(["original_logic_map.md", "evidence_bank.md", "rewrite_matrix.md", "logic_transfer_audit.md"])
    else:
        required.extend(["material_inventory.md"])

    for i, artifact in enumerate(required, start=1):
        path = out_dir / artifact
        if not path.exists():
            owner = ARTIFACT_OWNERS.get(artifact, "unknown")
            desc = ARTIFACT_DESCRIPTIONS.get(artifact, artifact)
            dim.findings.append(AuditFinding(
                id=f"ART-{i:03d}",
                severity="BLOCKER",
                dimension=dim.name,
                what_was_found=f"Required artifact `{artifact}` is missing",
                root_cause=f"`{owner}` did not produce `{artifact}` — either the skill was skipped or it failed silently",
                fix_action=f"Route back to `{owner}` and regenerate `{artifact}`. "
                           f"Do not hand-write this file — the owning skill produces it from research data.",
                downstream_impact=f"Without {artifact} ({desc}), downstream writing stages lack the input they need "
                                  "to make informed decisions. LaTeX assembly should not proceed.",
                teaching_note=f"Each PaperSpine artifact is a checkpoint. When one is missing, it usually means "
                              "an upstream step was skipped. Fix the step, not the gap.",
            ))
    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="ART-000", severity="INFO", dimension=dim.name,
            what_was_found=f"All {len(required)} required artifacts present",
            root_cause="", fix_action="", downstream_impact="",
            teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 2 — Reasoning Depth Audit
# ---------------------------------------------------------------------------

def audit_reasoning_depth(out_dir: Path, _config: dict) -> AuditDimension:
    dim = AuditDimension("Reasoning Depth")
    matrix_path = out_dir / "writing_rationale_matrix.md"
    if not matrix_path.exists():
        dim.findings.append(AuditFinding(
            id="RSN-001", severity="BLOCKER", dimension=dim.name,
            what_was_found="writing_rationale_matrix.md not found — cannot audit reasoning depth",
            root_cause="paper-spine-rewrite or paper-spine-build did not produce the rationale matrix",
            fix_action="Return to the rewrite/build step and generate a complete rationale matrix before retrying.",
            downstream_impact="Without the matrix, the manuscript has no documented reasoning. "
                              "The LaTeX stage cannot verify that structural choices are intentional.",
            teaching_note="The rationale matrix is the 'why' document. A paper without one is just formatted text.",
        ))
        return dim

    text = matrix_path.read_text(encoding="utf-8", errors="ignore")
    tables = markdown_tables(text)
    if not tables:
        dim.findings.append(AuditFinding(
            id="RSN-002", severity="BLOCKER", dimension=dim.name,
            what_was_found="No parseable Markdown table in writing_rationale_matrix.md",
            root_cause="The matrix was generated without a proper table structure — likely a format error in the writing step.",
            fix_action="Regenerate the rationale matrix ensuring it contains a valid Markdown table with header + data rows.",
            downstream_impact="The rewrite matrix and structured review depend on parseable rationale rows. "
                              "Without them, downstream audits cannot map findings to rationale.",
            teaching_note="Structured thinking needs structured output. A paragraph of prose is not a rationale matrix.",
        ))
        return dim

    rows = tables[0]
    header_text = " ".join(cell.lower() for cell in rows[0])
    has_motivation = "motivation" in header_text
    has_evidence = "evidence" in header_text

    # Check first data row depth (whole-work framework)
    if len(rows) > 1:
        first_row_text = " ".join(rows[1])
        if len(first_row_text) < 300:
            dim.findings.append(AuditFinding(
                id="RSN-003", severity="WARNING", dimension=dim.name,
                what_was_found=f"First rationale row is shallow ({len(first_row_text)} chars). "
                               "The whole-work framework justification should be at least 300 chars.",
                root_cause="The writing step spent insufficient effort on the controlling structure justification. "
                           "This row should explain *why* the chosen framework fits the confirmed motivation.",
                fix_action="Expand the first data row to include: (a) why this structure was chosen over alternatives, "
                           "(b) how SOTA examples informed it, (c) how it serves the confirmed motivation, "
                           "(d) which user evidence anchors it, and (e) how the final text will be checked against it.",
                downstream_impact="A weak first row means the entire paper structure is unjustified. "
                                  "The structured review will flag this as a fundamental weakness.",
                teaching_note="The whole-work framework row is the most important row in the matrix. "
                              "It's not a summary — it's a design justification.",
            ))

    # Count shallow rows
    shallow = [(i, len(" ".join(r))) for i, r in enumerate(rows[1:], start=1) if len(" ".join(r)) < 80]
    if len(shallow) > max(2, (len(rows) - 1) * 0.3):
        dim.findings.append(AuditFinding(
            id="RSN-004", severity="BLOCKER", dimension=dim.name,
            what_was_found=f"{len(shallow)} of {len(rows) - 1} rows are shallow (< 80 chars): "
                           f"{[s[0] for s in shallow[:8]]}",
            root_cause="The writing agent is producing placeholder rows instead of reasoned units. "
                       "This typically happens when the matrix is treated as a checklist rather than a design tool.",
            fix_action="For each shallow row, add: (a) the original problem this unit solves, "
                       "(b) the motivation link, (c) a SOTA pattern reference, and (d) a concrete planned change. "
                       "A row that just says 'improve clarity' is not a rationale — it's an admission of not thinking.",
            downstream_impact="Shallow rows produce shallow writing. The structured review will have nothing "
                              "to verify against, and the final manuscript will read as generic.",
            teaching_note="Every row should teach the reader *why* this writing move is better. "
                          "If you can't explain why, you haven't designed it yet.",
        ))
    elif shallow:
        dim.findings.append(AuditFinding(
            id="RSN-005", severity="WARNING", dimension=dim.name,
            what_was_found=f"{len(shallow)} shallow rows: {[s[0] for s in shallow[:8]]}",
            root_cause="Minor gaps in reasoning depth — likely rows that were left as placeholders.",
            fix_action="Review each shallow row and add at least motivation link + planned change.",
            downstream_impact="These rows will produce weaker-than-necessary writing units.",
            teaching_note="A rationale row doesn't need to be long, but it needs to be specific.",
        ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="RSN-000", severity="INFO", dimension=dim.name,
            what_was_found=f"All {len(rows) - 1} rationale rows have adequate depth",
            root_cause="", fix_action="", downstream_impact="",
            teaching_note="",
        ))

    return dim


# ---------------------------------------------------------------------------
# Dimension 3 — Evidence Chain Audit
# ---------------------------------------------------------------------------

def audit_evidence_chain(out_dir: Path, config: dict) -> AuditDimension:
    dim = AuditDimension("Evidence Chain")
    workflow = config.get("workflow", "rewrite_existing")

    if workflow == "rewrite_existing":
        rewrite_matrix = out_dir / "rewrite_matrix.md"
        if rewrite_matrix.exists():
            text = rewrite_matrix.read_text(encoding="utf-8", errors="ignore")
            tables = markdown_tables(text)
            if tables:
                rows = tables[0]
                unsupported = 0
                for i, row in enumerate(rows[1:], start=1):
                    joined = " ".join(row).lower()
                    if any(m in joined for m in ("unsupported", "no evidence", "[verify]", "tbd", "todo")):
                        unsupported += 1
                if unsupported:
                    dim.findings.append(AuditFinding(
                        id="EVD-001", severity="WARNING", dimension=dim.name,
                        what_was_found=f"{unsupported} rewrite matrix rows flagged as unsupported or unverified",
                        root_cause="Claims were mapped in the rewrite matrix without confirmed evidence backing. "
                                   "This happens when the evidence_bank was not populated before writing.",
                        fix_action="For each flagged row: either find evidence in evidence_bank.md, "
                                   "or narrow the claim to what can be supported, or remove the claim.",
                        downstream_impact="Unsupported claims in the manuscript undermine credibility. "
                                          "The structured review will flag these as critical weaknesses.",
                        teaching_note="Every claim needs an evidence anchor. If you can't point to which evidence "
                                      "supports a claim, the claim is an assumption, not a finding.",
                    ))

        evidence_bank = out_dir / "evidence_bank.md"
        if evidence_bank.exists():
            eb = evidence_bank.read_text(encoding="utf-8", errors="ignore")
            if len(eb) < 300:
                dim.findings.append(AuditFinding(
                    id="EVD-002", severity="WARNING", dimension=dim.name,
                    what_was_found="evidence_bank.md is very short — may lack sufficient evidence entries",
                    root_cause="Evidence was not systematically extracted from user materials before writing.",
                    fix_action="Re-read user-provided materials (draft, data, figures, notes) and extract "
                               "every claim-supporting piece of evidence into evidence_bank.md.",
                    downstream_impact="A sparse evidence bank limits what claims can be made. "
                                      "The paper will have fewer supported arguments than it could.",
                    teaching_note="The evidence bank is your ammunition. Write it before you write the paper.",
                ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="EVD-000", severity="INFO", dimension=dim.name,
            what_was_found="Claims are adequately linked to evidence",
            root_cause="", fix_action="", downstream_impact="",
            teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 4 — Integrity Pattern Scan
# ---------------------------------------------------------------------------

CITATION_RE = re.compile(r"\\cite\w*\{([^}]+)\}")
P_VALUE_RE = re.compile(r"p\s*[<>=]\s*0\.0[15](?!\d)")
UNREALISTIC_RE = re.compile(r"\b\d+\.\d{5,}\b")
WEAK_WORDS = {"clearly", "obviously", "undoubtedly", "without a doubt", "it is clear that"}
LEAP_WORDS = {"therefore", "thus", "hence", "consequently", "it follows that"}

FAILURE_PATTERN_TEACHING: dict[str, str] = {
    "orphan_citation": (
        "A citation key in the manuscript has no matching entry in the .bib file. "
        "This is one of the most common AI hallucinations — the model invents a plausible-sounding "
        "citation key that doesn't correspond to any real reference. Always verify every \\cite{} key "
        "against the .bib file before compilation."
    ),
    "suspicious_pvalue": (
        "P-values like p<0.01 or p=0.05 that appear without explicit test statistics (F-value, t-value, "
        "degrees of freedom) are a hallmark of AI-generated results sections. Real statistical reporting "
        "includes the test name, test statistic, degrees of freedom, and effect size alongside the p-value."
    ),
    "weak_assertion": (
        "Words like 'clearly', 'obviously', and 'undoubtedly' are rhetorical shortcuts. "
        "In academic writing, if something is clear, you don't need to say it is — the evidence "
        "should make it clear. These words often mask gaps in reasoning."
    ),
    "logical_leap": (
        "A high density of deductive connectors (therefore, thus, hence) without intermediate "
        "reasoning steps suggests the text is jumping from premise to conclusion without building "
        "the bridge. Each leap should be unpacked into: observation → interpretation → implication."
    ),
}


def audit_integrity_patterns(out_dir: Path, _config: dict) -> AuditDimension:
    dim = AuditDimension("Integrity Patterns")
    manuscript_text = ""
    final_paper = out_dir / "final_paper"
    if final_paper.is_dir():
        for tex_file in final_paper.glob("*.tex"):
            manuscript_text += tex_file.read_text(encoding="utf-8", errors="ignore") + "\n"
    if not manuscript_text:
        dim.findings.append(AuditFinding(
            id="INT-001", severity="WARNING", dimension=dim.name,
            what_was_found="No manuscript text to scan for integrity patterns",
            root_cause="The manuscript hasn't been written yet or final_paper/ is empty.",
            fix_action="Proceed with writing, then re-run this audit.",
            downstream_impact="Cannot verify integrity of unwritten text.",
            teaching_note="",
        ))
        return dim

    counter = 0

    # orphan citations
    bib_paths = list(final_paper.glob("*.bib")) if final_paper.is_dir() else []
    if bib_paths:
        bib_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in bib_paths)
        bib_keys = set(re.findall(r"@\w+\{([^,]+)", bib_text))
        orphans = [k for k in CITATION_RE.findall(manuscript_text) if k not in bib_keys]
        if orphans:
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"INT-{counter:03d}", severity="BLOCKER", dimension=dim.name,
                what_was_found=f"Orphan citations (in .tex but not in .bib): {', '.join(orphans[:6])}",
                root_cause="These citation keys were written into the manuscript but never added to the .bib file. "
                           "Either the citation is hallucinated, or the .bib entry was forgotten.",
                fix_action="For each orphan: (a) verify the paper actually exists via citation_quality_audit.py, "
                           "(b) add a correct BibTeX entry to references.bib, or (c) remove the citation if it cannot be verified.",
                downstream_impact="LaTeX compilation will fail with undefined citation warnings. "
                                  "Worse, if the citation is hallucinated and compiled, the paper contains a fabricated reference.",
                teaching_note=FAILURE_PATTERN_TEACHING["orphan_citation"],
            ))

    # suspicious p-values
    p_matches = P_VALUE_RE.findall(manuscript_text)
    if p_matches:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"INT-{counter:03d}", severity="WARNING", dimension=dim.name,
            what_was_found=f"Suspicious p-values found (without visible test statistics): {p_matches[:4]}",
            root_cause="AI-generated text tends to produce neat p-values (p<0.01, p<0.05) without reporting "
                       "the actual statistical test used, the test statistic, or effect sizes.",
            fix_action="For each flagged p-value: add the test name (e.g., t-test, ANOVA), "
                       "the test statistic (t=, F=, χ²=), degrees of freedom, and effect size. "
                       "If these values aren't known, the p-value should not be in the paper.",
            downstream_impact="Statistical reviewers will immediately flag incomplete statistics. "
                              "Journals increasingly reject papers with insufficient statistical reporting.",
            teaching_note=FAILURE_PATTERN_TEACHING["suspicious_pvalue"],
        ))

    # weak assertions
    found_weak = [w for w in WEAK_WORDS if w in manuscript_text.lower()]
    if found_weak:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"INT-{counter:03d}", severity="WARNING", dimension=dim.name,
            what_was_found=f"Weak assertion words used: {', '.join(found_weak)}",
            root_cause="Rhetorical shortcuts often appear when the underlying reasoning is thin. "
                       "The writer is asserting confidence rather than demonstrating it through evidence.",
            fix_action="Search for each weak word. Replace with concrete evidence or remove the assertion. "
                       "Instead of 'Clearly, X improves Y', write 'X improved Y by 23% (Table 2, p<0.01)'.",
            downstream_impact="Weak assertions reduce credibility with expert readers. "
                              "They signal that the writer is persuading rather than proving.",
            teaching_note=FAILURE_PATTERN_TEACHING["weak_assertion"],
        ))

    # logical leap density
    leap_count = sum(manuscript_text.lower().count(w) for w in LEAP_WORDS)
    para_count = max(1, manuscript_text.count("\n\n") + 1)
    if para_count > 0 and leap_count / para_count > 1.5:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"INT-{counter:03d}", severity="WARNING", dimension=dim.name,
            what_was_found=f"High logical-leap density: {leap_count} deductive connectors in ~{para_count} "
                           f"paragraphs ({leap_count / para_count:.1f}/paragraph)",
            root_cause="Deductive connectors are being used as substitutes for actual reasoning steps. "
                       "Each 'therefore' or 'thus' should be preceded by the evidence or logic that justifies it.",
            fix_action="For paragraphs with multiple leap words: unpack the reasoning chain. "
                       "Add the intermediate step between observation and conclusion. "
                       "A good rule: one 'therefore' per paragraph maximum.",
            downstream_impact="Readers perceive high leap density as shallow reasoning. "
                              "The paper reads as a list of conclusions without the work of getting there.",
            teaching_note=FAILURE_PATTERN_TEACHING["logical_leap"],
        ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="INT-000", severity="INFO", dimension=dim.name,
            what_was_found="No significant integrity patterns detected",
            root_cause="", fix_action="", downstream_impact="",
            teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def to_markdown(report: IntegrityAuditReport) -> str:
    lines = [
        "# Integrity Audit",
        "",
        f"- Output directory: `{report.output_dir}`",
        f"- Total findings: {report.total_findings}",
        f"- LaTeX gate: {'BLOCKED' if report.blocked else 'READY'}",
        "",
        "> This report teaches, not just checks. Each finding includes a root cause, "
        "a concrete fix, what happens downstream if unfixed, and why this pattern matters.",
        "",
        "## Summary",
        "",
        "| Dimension | Status | Findings |",
        "|---|---|---|",
    ]
    for dim in report.dimensions:
        lines.append(f"| {dim.name} | {dim.status} | {len(dim.findings)} |")
    lines.append("")

    for dim in report.dimensions:
        if not dim.findings:
            continue
        lines.append(f"## {dim.name}")
        lines.append("")
        for f in dim.findings:
            if f.severity == "INFO":
                lines.append(f"**{f.id}** ✅ {f.what_was_found}")
                lines.append("")
                continue
            icon = "🚫" if f.severity == "BLOCKER" else "⚠️"
            lines.append(f"### {icon} {f.id} — {f.severity}")
            lines.append("")
            lines.append(f"**What was found:** {f.what_was_found}")
            lines.append("")
            lines.append(f"**Root cause:** {f.root_cause}")
            lines.append("")
            lines.append(f"**Fix:** {f.fix_action}")
            lines.append("")
            lines.append(f"**Downstream impact:** {f.downstream_impact}")
            lines.append("")
            if f.teaching_note:
                lines.append(f"**Why this matters:** {f.teaching_note}")
                lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    if not out_dir.is_dir():
        print(f"Output directory not found: {out_dir}", file=sys.stderr)
        return 2

    config = load_config(out_dir)
    dimensions = [
        audit_artifacts(out_dir, config),
        audit_reasoning_depth(out_dir, config),
        audit_evidence_chain(out_dir, config),
        audit_integrity_patterns(out_dir, config),
    ]
    report = IntegrityAuditReport(str(out_dir), dimensions)

    if args.json:
        output = {
            "output_dir": str(out_dir),
            "blocked": report.blocked,
            "total_findings": report.total_findings,
            "dimensions": [
                {
                    "name": d.name,
                    "status": d.status,
                    "findings": [
                        {"id": f.id, "severity": f.severity, "what": f.what_was_found,
                         "root_cause": f.root_cause, "fix": f.fix_action,
                         "downstream": f.downstream_impact, "teaching": f.teaching_note}
                        for f in d.findings
                    ],
                }
                for d in dimensions
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(report))

    if args.write:
        report_path = out_dir / "integrity_audit.md"
        report_path.write_text(to_markdown(report), encoding="utf-8")
        print(f"Wrote {report_path}", file=sys.stderr)

    return 1 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
