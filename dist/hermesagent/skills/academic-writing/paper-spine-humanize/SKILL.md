---
name: paper-spine-humanize
description: Reduces AI detection rates via tiered stylistic constraints mapped to real AIGC detection dimensions. Produces a teaching humanize_matrix.md.
---

# PaperSpine Humanize

**Self-contained skill** — can be used standalone on any academic text, or as
part of the PaperSpine suite.  Applies tier-specific writing constraints based
on real AIGC detection dimensions and produces a teaching matrix that documents
every change.

## When To Use

- In PaperSpine: auto-invoked by rewrite/build when `humanize_tier` is not `none`
- Standalone: invoke directly on any academic text that needs AI detection reduction

## Configuration

Read `paper_spine_config.json` for `humanize_tier` (none/light/medium/heavy)
and `output_language` (zh/en).  When used standalone, default to `medium` / `zh`
if no config found.

## Required Output: humanize_matrix.md

This is the **primary deliverable** — produce `paper_rewriting_output/humanize_matrix.md`.
Every humanization change must be recorded, not applied silently:

| Row ID | Manuscript Unit | AI Pattern Found | Detection Dim | Severity | Applied Change | Expected Effect | Teaching Note |
|--------|----------------|------------------|---------------|----------|---------------|-----------------|---------------|

- **Manuscript Unit**: paragraph number or section name
- **AI Pattern Found**: specific AI feature detected
- **Detection Dim**: D1-D5 (see reference document)
- **Severity**: High (>50% contribution to detection) / Medium (20-50%) / Low (<20%)
- **Applied Change**: what specific change was made
- **Expected Effect**: which dimension this reduces
- **Teaching Note**: why detectors flag this pattern

### Matrix Rules

- Write rows **during writing**, one per unit processed — not after the fact
- At least one row per writing unit for D1 (sentence length)
- At least one row per paragraph for D2 (paragraph structure)
- At least one row per connector replaced (D4)
- At least one row per density adjustment (D3, medium+)
- At least one row per term substitution (D5, heavy only)
- Fill all 8 columns for every row — no empty cells

## Instructions

Read `references/humanize-tiers-{output_language}.md` for the complete
tier-specific directives mapped to the 5 detection dimensions:
D1-Sentence Length / D2-Paragraph Structure / D3-Information Density /
D4-Connector Frequency / D5-Term-Context Matching.

## Verification

```bash
python scripts/humanize_check.py paper_rewriting_output --markdown --write
```

Produces `paper_rewriting_output/humanize_report.md`.  Checks matrix coverage
against total paragraphs, scans sentence-length distribution and connector
density, and flags remaining AI patterns.

## Integration

In PaperSpine: called internally by rewrite and build.  Standalone: place this
skill directory under `~/.claude/skills/` and invoke directly.
