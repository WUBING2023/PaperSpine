---
name: paper-spine-build
description: Builds a paper or report from materials using the shared PaperSpine research, motivation, and rationale workflow.
---

# PaperSpine Build From Materials

Use this skill when the user does not have a real manuscript draft yet and
instead provides a materials folder with experiment settings, results, figures,
notes, PDFs, Word files, TXT/Markdown reports, or partial drafts.

This workflow shares the same research, motivation confirmation, evidence bank,
section blueprint, and writing rationale matrix logic as `paper-spine-rewrite`.
It is not a separate shortcut.

## Required Inputs

- `paper_rewriting_output/paper_spine_config.json`
- `materials_dir`
- target scene and output language
- `paper_rewriting_output/reference_materials/source_index.md`
- `paper_rewriting_output/research_dossier.md`
- `paper_rewriting_output/exemplar_learning_dossier.md`
- `paper_rewriting_output/style_profile.md`
- `paper_rewriting_output/sota_gap_map.md`
- `paper_rewriting_output/citation_support_bank.md`
- `paper_rewriting_output/confirmed_motivation.md` with user confirmation

If research or confirmed motivation is missing, do not draft. Return to
`paper-spine-research` and ask the user to confirm the motivation after seeing
research-grounded options.

If `citation_support_bank.md` is missing or shallow, return to
`paper-spine-citation`. From-zero writing still needs literature support for
background, Introduction/overview, Discussion, limitations, and applications.

## First Pass

Run or emulate:

```bash
python scripts/material_inventory.py <materials_dir> --output-dir paper_rewriting_output
```

Create `source_inventory.md` before making claims.

## Required Outputs

- `paper_rewriting_output/source_inventory.md`
- `paper_rewriting_output/evidence_bank.md`
- `paper_rewriting_output/figure_asset_map.md`
- `paper_rewriting_output/claim_register.md`
- `paper_rewriting_output/section_blueprints.md`
- `paper_rewriting_output/writing_rationale_matrix.md`
- manuscript draft as an intermediate artifact
- `paper_rewriting_output/final_paper/main.tex`
- `paper_rewriting_output/final_paper/paper.pdf` when a TeX engine is available
- `paper_rewriting_output/latex_report.md`
- `paper_rewriting_output/final_artifact_manifest.md`
- `paper_rewriting_output/translation_zh/` when `translation_package` is `zh` (via `paper-spine-translate`)

## Writing Rationale Matrix

Before final prose, create `writing_rationale_matrix.md` and read
`references/writing-rationale-matrix.md`. The matrix is the build plan. It must
be ordered by the target document's actual writing units, not by a fixed paper
template.

Use this table:

| Row ID | Manuscript Unit | Planned Function | Motivation Link | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Text Move | Final Text Check |
|---|---|---|---|---|---|---|---|---|

The first data row must deeply justify the whole-work framework or throughline:
why this controlling structure is chosen, how SOTA/target examples informed it,
how it follows the confirmed motivation, which user evidence anchors it, and how
the final manuscript/report will be checked against it. After that, split the
work into the smallest useful units for the selected scene:
abstract/summary moves, problem restatement, assumptions, model design, methods
choices, result/claim units, review synthesis blocks, validation blocks,
recommendations, headings, captions, or other argument-bearing fragments.

No row may be generic. Each row must state why that unit exists and how it is
connected to the confirmed motivation, learned examples, target-scene norms, or
user evidence. If a paragraph or figure claim needs a separate writing decision,
it needs its own row.

## Humanize Tier

If `paper_spine_config.json` has `humanize_tier` set to `light`, `medium`, or
`heavy`, route to `paper-spine-humanize` before writing.  The humanize skill
provides tier-specific writing constraints enforced during all prose generation.

## Build Rules

- Treat images as potential figure assets, not as verified evidence unless the
  user explains what they show.
- Use existing document/PDF skills for complex PDF, DOCX, or scanned material
  extraction when available.
- Do not fabricate missing experiments or results.
- Copy user-approved figure assets into the final LaTeX project's `figures/`
  folder and reference them with labels and captions.
- Follow `output_language`: `en` or `zh`.
- Use `citation_support_bank.md` to select citations sentence by sentence; do
  not treat citation candidates as user evidence or insert all candidates.
- Before routing through `paper-spine-latex`, run `python scripts/integrity_audit.py paper_rewriting_output --markdown --write` and `python scripts/structured_review.py paper_rewriting_output --dispatch`. After dispatch, launch three parallel review sub-agents per `review_prompts/dispatch.md`, then validate independence. Only proceed when all dimensions PASS.
- Always finish by routing through `paper-spine-latex`. A Markdown draft is not
  a final deliverable for this workflow.
- Build the final LaTeX project under `paper_rewriting_output/final_paper/`.
- If `word_output` is `docx`, generate `final_paper/paper.docx` and run
  `scripts/word_guard.py`, saving `paper_rewriting_output/word_report.md`.
- If `output_language` is `en` and `translation_package` is `zh`, create a full
  `paper_rewriting_output/translation_zh/` package. This includes complete
  row-by-row translation of large intermediate files such as
  `writing_rationale_matrix.md`; partial translation or summary translation is
  a failure.

Read `references/build-from-materials.md` and
`references/writing-rationale-matrix.md` before building the manuscript.

