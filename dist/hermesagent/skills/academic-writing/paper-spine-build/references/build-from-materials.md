# Build From Materials

Use this workflow when the user provides a folder of materials rather than a
complete manuscript draft.

## Source Inventory First

Before writing, classify all files and create:

- `source_inventory.md`
- `source_inventory.json`

Use `scripts/material_inventory.py` when available. This script only classifies
files. It does not extract PDF/DOCX content.

## Evidence Bank

Create `evidence_bank.md` from user-provided materials only:

| Evidence ID | Source File | Claim Supported | Figure/Table Link | Verification Needed |
|---|---|---|---|---|

If a result cannot be verified from user materials, mark it as requiring user
confirmation instead of writing it as fact.

## Figure Asset Map

Create `figure_asset_map.md`:

| Figure ID | Source Image | Intended Caption | Target Location | LaTeX Label |
|---|---|---|---|---|

Images may be copied into the final LaTeX project's `figures/` folder only when
they are user-provided or user-approved.

## Claim Register

Create `claim_register.md`:

| Claim | Evidence ID | Strength | Allowed Wording | Avoid |
|---|---|---|---|---|

The claim register controls what the final paper is allowed to say.

## Manuscript Construction

Build the paper from:

1. confirmed motivation,
2. target-scene research,
3. evidence bank,
4. figure asset map,
5. section blueprints,
6. output language.

Do not write a result, comparison, dataset, or citation that is not supported by
the materials or verified external sources.

## Final LaTeX Deliverable

The from-materials workflow must not stop at Markdown. After the manuscript
draft is stable, create a final LaTeX project:

```text
paper_rewriting_output/
├── final_paper/
│   ├── main.tex
│   ├── paper.pdf        # when a TeX engine is available
│   ├── paper.docx       # optional Word output
│   └── figures/
├── latex_report.md
├── word_report.md       # required when paper.docx is generated
└── final_artifact_manifest.md
```

Rules:

- Copy every approved figure asset into `final_paper/figures/`.
- Use stable labels such as `fig:workflow`, `fig:result-curve`, and
  `tab:main-results`.
- The `.tex` file must be the source of the final paper/report. Markdown is
  only an intermediate writing artifact.
- Always create `main.tex`. Compile the PDF when `latexmk`, `xelatex`, or
  `pdflatex` is available. For Chinese output, use XeLaTeX and a CJK-capable
  template. For English output, use the target venue or task template when
  available.
- If no TeX engine is available, record that in `latex_report.md` and still
  deliver `main.tex`. If a TeX engine exists but compilation cannot succeed,
  record the exact command and first fatal error in `latex_report.md`; the
  workflow is not complete until the compile issue is reported.
- If a Word version is requested, generate `paper.docx`, run `word_guard.py`,
  and save the report as `word_report.md`.

## Optional Translation Package

When `output_language` is `en` and `translation_package` is `zh`, create:

```text
paper_rewriting_output/translation_zh/
├── manifest.md
├── paper_spine_config.zh.md
├── research_dossier.zh.md
├── section_blueprints.zh.md
├── final_structure.zh.md
└── artifact_summary.zh.md
```

Translate the purpose, section logic, evidence summaries, and final structure.
Do not treat the translated package as the authoritative paper and do not
translate citation keys, labels, file paths, formulas, or raw data values.
