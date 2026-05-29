---
name: paper-spine-citation
description: Builds a citation support bank for Introduction, Discussion, and background claims.
---

# PaperSpine Citation

Use this branch after research and before final writing. Its job is not to learn
paper structure. Its job is to build a verified citation support bank that can
support literature statements in the user's manuscript.

## Inputs

Read `paper_rewriting_output/paper_spine_config.json`, especially:

- `target_name`
- `scene`
- `output_language`
- `reference_mode`
- `reference_paths`
- `citation_target_count` defaulting to `20`
- `materials_dir`
- `draft_path`
- `research_dossier.md`
- `sota_gap_map.md`
- `reference_materials/source_index.md`

## Required Output

Create:

```text
paper_rewriting_output/citation_support_bank.md
```

Use this table:

| Candidate ID | Reference/BibTeX | Year | Recency | Supports Section | Support Claim Sentence | Why This Paper Fits | Source | Verified | Verification Note |
|---|---|---|---|---|---|---|---|---|---|

Rules:

- Generate at least `citation_target_count * 3` candidates. Default: 60.
- About 80% of candidates should be recent. In 2026, use 2023 or later as the
  simple recent threshold.
- Each candidate must pair one paper with one or two support sentences that can
  be used in Introduction, Related Work, Discussion, limitations, or
  application paragraphs.
- Prefer same-field, similar-field, foundational, benchmark, review, and
  application papers. Do not only cite near-identical SOTA papers.
- Do not invent bibliography. Use local PDFs/metadata, DOI/arXiv/Crossref-like
  metadata, official publisher pages, or user-provided reference files.
- Mark uncertain items as `[VERIFY]` and do not use them in final writing until
  the user verifies them.
- This bank is a candidate pool. Final writing should select a coherent subset,
  not dump all candidates into the paper.

Read `references/citation-support-bank.md` when detailed rules are needed.

## Flow

1. **Collection pass:** Build the initial candidate pool with at least
   `citation_target_count * 3` rows. Leave `Verified` and `Verification Note`
   columns empty during this pass.
2. **Verification pass:** Run `citation_quality_audit.py` to verify each DOI
   against Crossref, score citation quality, analyze diversity gaps, and
   produce `citation_quality_audit.md`. Fill in the `Verified` column as `yes`,
   `mismatch`, `dead`, or `error` based on the audit results.
3. **Curation:** Select the final subset of verified, recent, and
   field-appropriate citations for the manuscript. Do not use unverified or
   mismatched citations in final writing until the user confirms them.

## Check

```bash
python scripts/citation_bank_check.py paper_rewriting_output/citation_support_bank.md --target-count 20 --markdown
python scripts/citation_quality_audit.py paper_rewriting_output --write
```

If the config has a different `citation_target_count`, use that value.
