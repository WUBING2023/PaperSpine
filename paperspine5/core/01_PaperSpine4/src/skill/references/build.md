# Build Stage

This file is the canonical stage playbook for the paper-spine orchestrator.

## Purpose

Build a manuscript from materials when no real draft exists yet. Shares the
same research, motivation, and rationale logic as the rewrite stage.

For the full manuscript, apply
[reference-guided-writing.md](reference-guided-writing.md): derive its argument
from this study's evidence, assign complementary exemplar roles within the saved
learning pool, and keep actual changes traceable without copying an exemplar's
special structure. Fresh writing/review receives complete scientific evidence,
not conversational emphasis or an expected verdict.

## Start from the same task

Read its saved configuration, confirmed materials, supported contribution and
motivation choices, actual results and literature notes. Reuse valid decisions
and existing files. Apply [research.md](research.md) to the selected research
mode; resolve specific evidence gaps before making dependent claims. No legacy
filename or checker is needed merely to start writing.

## First Pass

```bash
python scripts/material_inventory.py <materials_dir> --output-dir paper_rewriting_output
```

Use the existing material inventory; run the inventory helper only for a real
gap. Identify the evidence supporting each claim before drafting it.

When the inventory contains multiple versions of data, figures/tables, code,
or editable sources, read `asset-selection.md`. Preserve the user's explicit
choice; otherwise select the newest candidate only within the same confirmed
scientific identity and declared project/materials roots. Preserve the current task
selection and resolve uncertain identity before using an asset. Legacy selector
receipts are needed only when that selector is actually invoked.

## Authorial Voice Restoration

When configuration enables author_voice_restoration, use assertive-scientific-writing.md and the relevant authorial-voice scientific safeguards. Read authorized author material when available, preserve the original, make only needed changes, and allow a clean-text no-op. Verify that facts, terminology, negation, causality, uncertainty and citation meaning are unchanged. Use the existing independent review for actual concerns; do not require a new hash-bound author confirmation for ordinary revision already within the user's scope.

## Historical helper inventory

These names are inputs to legacy helpers, not additional deliverables for the
current host. Keep the actual manuscript, scientific links and relevant decisions
in the existing task; follow manuscript-format.md for requested outputs.

- `source_inventory.md`, plus `asset_selection_request.json` and
  `asset_selection_receipt.json/.md` when versioned candidates exist;
  `evidence_bank.md`, `figure_asset_map.md`, `claim_register.md`
- `section_blueprints.md`; `writing_rationale_matrix.md` in strict mode or when requested
- `results_validation.md` for journal, conference, and competition scenes
- `scientific_evidence_ledger.json` for journal, conference, and competition scenes
- Manuscript draft
- `author_voice_profile.json`, `author_voice_revision.json`,
  `author_voice_receipt.json`, and `author_voice_report.md` when enabled
- `final_paper/main.tex`, `latex_report.md`, `final_artifact_manifest.md`

## Planning Depth

Balanced mode lets the Agent design the manuscript from `section_blueprints.md`,
primary evidence links, and the results map. Use the matrix only for strict mode
or a user-requested paragraph-level rationale trace.

Read `editorial-completeness.md`. The blueprint is scaffolding, not the paper:
develop each evidence or figure unit into a complete reader-facing argument and
preserve a full ending appropriate to the venue. Research `tier` never changes
this manuscript-scale commitment.

## Writing Rationale Matrix (Strict / Optional)

| Row ID | Manuscript Unit | Planned Function | Contribution Promise / Claim ID | Motivation Alignment | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Text Move | Final Text Check |
|---|---|---|---|---|---|---|---|---|---|

When strict mode applies, read `references/writing-rationale-matrix.md` and apply its
full depth rules. Every non-trivial row must identify a contribution promise
and include concrete anchors from the aligned motivation, SOTA/example pattern,
target scene, evidence/citation, and the planned text move. For evidence-bearing
scenes, apply results-validation.md to the real results and claims before
drafting them; reuse existing notes instead of creating another planning gate.
The first row must justify the whole-work framework.
After drafting, every `Final Text Check` value must start with `PASS` or
`FAIL`; do not write vague notes such as "done" or only a section location.

## Build Rules

- Treat images as potential figure assets.
- Do not fabricate missing experiments or results.
- Quote paths with spaces or non-ASCII chars.
- Use `output_language` from config.
- Select citations sentence by sentence.
- Tie scientific values and results to their actual sources. After authorized
  analysis changes, update those links and affected claims together.
- Let the Agent choose section names, paragraph structure, and revision order.
  Use the contribution and reader questions as guidance; do not turn planning
  rows, section counts, or word ranges into prose templates.
- Draft the scientific argument from the evidence-aware plan. Apply
  publication-surface.md by meaning: production narration belongs in work notes;
  study procedures, reproducibility details and required disclosures remain.
  Do not remove legitimate scientific review/workflow descriptions by keyword.
- Preserve semantic citation keys and object IDs through manuscript-format.md;
  use the venue citation processor rather than manually typed reference numbers.
- Read `references/assertive-scientific-writing.md`; evidence precision should
  support a clear voice, not produce repetitive defensive hedging.
- Draft and render early enough to review the actual paper. Use review-policy.md
  for independent editorial, evidence and format review; correct located defects
  and recheck affected outputs. An unused brief or historical pre-LaTeX receipt
  is not a prerequisite for rendering, and rendering is not review approval.
- Apply the last language pass, then run the publication-surface scrub; internal
  evidence IDs stay in the ledger and must not leak into the manuscript.
- Before rendering, run the serialized-command guard (`scripts/latex_guard.py`)
  against the exact source that will be compiled. This guard must reject
  doubled leading backslashes introduced by JSON/YAML/string serialization;
  never repair the PDF after rendering.
- Compile `final_paper/main.tex` with a real LaTeX engine available in the
  environment. A source dump, screenshot, or ReportLab stand-in is not a
  manuscript build and cannot be placed in the delivery package.
- Parse the resulting PDF (`pdfinfo`/a PDF parser), extract text with
  `pdftotext`, and render every page with `pdftoppm` (or an equivalent
  renderer) for visual inspection. The PDF must begin with `%PDF`, contain no
  literal TeX source markers, and have page images that are readable and
  complete.
- Validate the editable DOCX as a ZIP/XML document, extract its visible text,
  and render its pages independently from the PDF. Reusing PDF page images as
  Word evidence is a provisional fallback and must be labelled as such; it is
  not proof of Word-native layout fidelity.
- Record the source/PDF/DOCX hashes, parser results, page-count results, and
  any provisional evidence in the artifact audit before setting a local
  delivery package to ready.
- Build final LaTeX under `final_paper/`.
