# Local Reference Ingestion

PaperSpine must prefer user-provided local references before web-only search.
This supports paywalled databases, library exports, downloaded PDFs, CNKI/CAJ
files, course materials, competition handbooks, and private reference folders
that the agent cannot legally or technically fetch from the open web.

## Modes

- `local_first` is the default. Read the current working folder, `materials_dir`,
  `reference_materials/`, `references/`, `literature/`, `papers/`, and user
  uploads first; then use web research only to fill gaps.
- `specified_paths` means the user supplied `reference_paths`; index those
  paths before using any other source.
- `web` means web research is the main route, but any local seed references
  still need to be indexed if present.

## Required Behavior

1. Create `paper_rewriting_output/reference_materials/`.
2. Run or emulate `scripts/reference_inventory.py` on the local/default paths.
3. Write `reference_materials/source_index.md`.
4. Every local source must record its local path in `Origin/URL/Path` and
   `Local File/Note`.
5. Do not treat local references as user evidence for the manuscript's results.
   Local references can support literature context, citation expansion, target
   style learning, and background claims.
6. Never bypass paywalls or login restrictions. If a paper is not accessible,
   ask the user to provide a legal local copy or citation metadata.

## Source Index Columns

| Source ID | Type | Title/Name | Origin/URL/Path | Why Included | Local File/Note | Used For |
|---|---|---|---|---|---|---|

Use stable source IDs such as `REF001`, `REF002`, and keep them reusable in
`research_dossier.md`, `citation_support_bank.md`, and
`writing_rationale_matrix.md`.
