---
name: paper-spine-translate
description: Produces the complete translation_zh/ package with row-by-row translation of all required artifacts and full-paper translation.
---

# PaperSpine Translate

Use this branch when `output_language` is `en` and `translation_package` is
`zh`.  Its job is to produce every required Chinese translation file under
`paper_rewriting_output/translation_zh/` — not a summary, not a partial set.

## Operating Principle

A translation package that covers only a few files is a failed output.
The orchestrator requires a complete `translation_zh/` before declaring the
workflow complete.  This branch owns the translation responsibility end-to-end.

## Three-Phase Flow

### Phase 1 — Inventory

Read `paper_spine_config.json` to determine `workflow`.  List every file that
must be translated.  Write the inventory to `translation_zh/manifest.md` with
status `pending` for each entry.

**Common files (both workflows):**

| English Source | Chinese Target |
|---|---|
| `paper_spine_config.json` | `paper_spine_config.zh.md` |
| `source_map.md` | `source_map.zh.md` |
| `reference_materials/source_index.md` | `reference_materials/source_index.zh.md` |
| `research_dossier.md` | `research_dossier.zh.md` |
| `exemplar_learning_dossier.md` | `exemplar_learning_dossier.zh.md` |
| `style_profile.md` | `style_profile.zh.md` |
| `sota_gap_map.md` | `sota_gap_map.zh.md` |
| `motivation_options_after_research.md` | `motivation_options_after_research.zh.md` |
| `confirmed_motivation.md` | `confirmed_motivation.zh.md` |
| `section_blueprints.md` | `section_blueprints.zh.md` |
| `writing_rationale_matrix.md` | `writing_rationale_matrix.zh.md` |
| `citation_support_bank.md` | `citation_support_bank.zh.md` |
| `latex_report.md` | `latex_report.zh.md` |
| `final_artifact_manifest.md` | `final_artifact_manifest.zh.md` |
| `artifact_check.md` | `artifact_check.zh.md` |
| the final paper (`.tex` or `.md`) | `full_paper_translation.zh.md` |
| — | `translation_coverage.md` |

**Rewrite-only additions:**

| `original_logic_map.md` | `original_logic_map.zh.md` |
| `rewrite_matrix.md` | `rewrite_matrix.zh.md` |
| `logic_transfer_audit.md` | `logic_transfer_audit.zh.md` |

**Build-only additions:**

| `source_inventory.md` | `source_inventory.zh.md` |
| `evidence_bank.md` | `evidence_bank.zh.md` |
| `figure_asset_map.md` | `figure_asset_map.zh.md` |
| `claim_register.md` | `claim_register.zh.md` |

### Phase 2 — Translate

Translate every file listed in the inventory.  Follow these rules:

- **Plain prose files:** Translate the full text.  Preserve LaTeX citation keys
  (`\cite{...}`), labels (`\label{...}`), equations, file paths, raw numeric
  values, URLs, and code identifiers as-is.  Translate the surrounding prose.
- **Large tabular files** (`writing_rationale_matrix.md`,
  `citation_support_bank.md`, `section_blueprints.md`,
  `research_dossier.md`, `exemplar_learning_dossier.md`,
  `sota_gap_map.md`, and any workflow-specific tabular files):
  Translate **every row and every cell**.  The translated table must have
  at least as many rows as the original.  A shortened summary table is a
  failed output.
- **`full_paper_translation.zh.md`** must include: title, abstract, every
  section and subsection body paragraph, figure captions, table captions
  and table notes, limitations, conclusion, acknowledgements, and appendix
  narrative text.
- Update `manifest.md` status from `pending` → `translated` after each file.

Do not skip files because they are "large."  Do not summarize instead of
translating.  The audit will reject partial translations.

### Phase 3 — Verify

Run the guard script and require PASS:

```bash
python scripts/translate_guard.py paper_rewriting_output --markdown --write
```

This produces `translation_zh/translate_guard_report.md`.  If any check fails,
return to Phase 2 and fix the specific files flagged by the report.

Write `translation_coverage.md` listing every source file, its Chinese
counterpart, and its final status (`translated`).  Every entry must be
`translated` before the audit passes.

## Integration

This branch is called by the orchestrator after `paper-spine-latex` and before
`paper-spine-audit`.  The orchestrator's Non-Negotiable Route step 14 requires
the translate guard to PASS before audit begins.
