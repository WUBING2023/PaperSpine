# Translation Package Coverage

Use this reference when `output_language` is `en` and `translation_package` is
`zh`.

The translation package is a complete Chinese reading aid for the whole
workflow. It must not replace the authoritative English manuscript.

## Required Folder

```text
paper_rewriting_output/translation_zh/
  manifest.md
  translation_coverage.md
  paper_spine_config.zh.md
  source_map.zh.md
  reference_materials/source_index.zh.md
  research_dossier.zh.md
  exemplar_learning_dossier.zh.md
  style_profile.zh.md
  sota_gap_map.zh.md
  motivation_options_after_research.zh.md
  confirmed_motivation.zh.md
  section_blueprints.zh.md
  writing_rationale_matrix.zh.md
  final_structure.zh.md
  final_paper.zh.md
  full_paper_translation.zh.md
  latex_report.zh.md
  final_artifact_manifest.zh.md
  artifact_check.zh.md
```

Rewrite workflow also requires:

- `original_logic_map.zh.md`
- `rewrite_matrix.zh.md`
- `logic_transfer_audit.zh.md`

Build workflow also requires:

- `source_inventory.zh.md`
- `evidence_bank.zh.md`
- `figure_asset_map.zh.md`
- `claim_register.zh.md`

## Full Paper Translation

`full_paper_translation.zh.md` is mandatory. It must translate the final paper's
reader-facing text completely:

- title and subtitle,
- abstract,
- every section and subsection body paragraph,
- figure captions,
- table captions and table notes,
- limitations, conclusion, acknowledgements when present,
- appendix narrative text when present.

Preserve citation keys, LaTeX labels, equations, file paths, raw numeric values,
URLs, dataset identifiers, and code identifiers. Translate the surrounding prose
and explain technical terms consistently.

## Translation Rules

Translate explanations, section logic, evidence summaries, rationale, and final
reader-facing structure. Do not stop after translating only the config or a few
intermediate files.

Large intermediate artifacts must be translated completely, not summarized.
This especially applies to:

- `writing_rationale_matrix.md`
- `section_blueprints.md`
- `research_dossier.md`
- `exemplar_learning_dossier.md`
- `sota_gap_map.md`
- `original_logic_map.md`
- `rewrite_matrix.md`
- `source_inventory.md`
- `evidence_bank.md`
- `claim_register.md`

For Markdown tables, preserve the table row structure. Translate every row and
every explanatory cell. For `writing_rationale_matrix.zh.md`, the translated
table must contain at least the same number of rationale rows as
`writing_rationale_matrix.md`; a shortened summary table is a failed output.

`translation_coverage.md` must list every required English artifact and every
final-paper textual unit with its Chinese counterpart and status `translated`,
`not applicable`, or `missing`. Partial translation is a failed audit.
