---
name: paper-spine-latex
description: Handles LaTeX project assembly, figure placement, citations, labels, and compile-safe cleanup.
---

# PaperSpine LaTeX

Use this skill for LaTeX assembly, template integration, figure placement,
citations, labels, and compile-safety checks. Do not change manuscript logic
unless rewrite/build outputs require it.

## Required Inputs

- revised manuscript or built manuscript
- target template if any
- figures, tables, bibliography, and source files
- `paper_rewriting_output/figure_asset_map.md` when building from materials

## Required Outputs

- updated LaTeX project; for from-materials builds, use
  `paper_rewriting_output/final_paper/main.tex`
- compiled PDF when a TeX engine is available; for from-materials builds, use
  `paper_rewriting_output/final_paper/paper.pdf`
- `paper_rewriting_output/latex_report.md`
- `paper_rewriting_output/final_artifact_manifest.md` when producing final
  deliverables
- optional `paper_rewriting_output/final_paper/paper.docx` plus
  `paper_rewriting_output/word_report.md`

## Rules

- Keep content work separate from LaTeX scaffolding.
- Preserve citation keys and labels unless there is a verified reason to rename.
- Copy approved images into `figures/` and use stable labels.
- Run `scripts/latex_guard.py` when available.
- Record unresolved compile or asset issues in `latex_report.md`.
- Do not treat Markdown as the final manuscript when the workflow is
  `build_from_materials`.
- For Chinese output, prefer XeLaTeX and a CJK-capable template. For English
  output, follow the target template or use a conservative article template.
- If no TeX engine is available, keep the `.tex` and record that compilation was
  skipped in `latex_report.md`.
- If compilation fails despite an available engine, keep the `.tex`, write the
  first fatal error to `latex_report.md`, and do not claim the artifact check
  passes.
- If generating Word output, use pandoc from the `final_paper/` directory:
  ```bash
  cd final_paper
  pandoc main.tex -o paper.docx --from latex --to docx \
    --resource-path=. --extract-media=./media
  ```
  - `--resource-path=.` resolves `\includegraphics{figures/...}` paths
  - `--extract-media=./media` embeds images into the docx
  - Without these flags, pandoc silently drops images and produces a blank docx
  - Run from `final_paper/` so relative paths in `.tex` resolve correctly
  - Do NOT use intermediate plain-text steps that strip encoding
- Run `scripts/word_guard.py final_paper/paper.docx --markdown --output
  paper_rewriting_output/word_report.md` and fix failures before presenting
  the Word file as usable. If word_guard reports 0 paragraphs, check that
  images are in supported formats (PNG/JPG) and the `figures/` directory exists.

Read `references/latex-source-control.md` before structural LaTeX edits.
