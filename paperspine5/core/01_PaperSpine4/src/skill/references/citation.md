# Citation Stage

For the current host, use [journal-learning.md](journal-learning.md) for public
literature scope and [manuscript-format.md](manuscript-format.md) for emitted
markers, bibliography links and format verification. A rewrite, local material
path or `materials_only` setting does not by itself restrict public literature
to a closed corpus. Only an explicit user restriction does. The historical
Runner bank schemas and quotas below do not add a gate to normal host writing.

This file is the canonical stage playbook for the paper-spine orchestrator.

## Purpose

Build a verified citation support bank that can support literature statements
in the user's manuscript. This is separate from exemplar learning.

## Literature Retrieval Priority Protocol

1. **Literature MCP tools (preferred).** If the host has MCP servers, use them
   first. Record the source channel per citation: `MCP-CNKI`, `MCP-IEEE`,
   `MCP-PubMed`, `MCP-Crossref`, `web`, `local`, or `unknown`.
2. **Host WebSearch / browsing tools (fallback).** Mark Source Channel as `web`.
3. **Local files.** Mark Source Channel as `local`.
4. **MCP is an enhancement, not a dependency.** Build the bank from web/local
   sources when no MCP is available.

## Working citation notes

Use the existing task bibliography and claim-support notes. When using the
legacy table checker, this table is its accepted input format:

| Candidate ID | Source ID | Claim Use ID | Reference/BibTeX | Year | Recency | Supports Section | Support Claim Sentence | Why This Paper Fits | Source | Source Channel | Verified | Verification Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Literature Contracts

Resolve `literature_scope` before collection:

- `open_literature`: use when the task permits literature discovery or needs a
  new SOTA/field map. Expand the pool to answer actual coverage gaps in
   background, methods, close comparisons and interpretation. The saved final
   bibliography target is not a candidate-pool multiplier or an age quota.
- `closed_corpus`: use for evidence-bounded rewrites that may cite only supplied
  materials. Deduplicate and exhaust the available bibliography. Require at
  least the planned final citation target when available; if the corpus is
  smaller, add `CLOSED_CORPUS_EXHAUSTIVE` and report the actual total. Do not
  block writing merely because the fixed corpus is old or smaller than 3x.

Resolve to `closed_corpus` only when the user explicitly restricts usable literature to supplied sources. A local path, `specified_paths`, `rewrite_existing`, or `materials_only` alone does not close public literature; an explicit offline instruction limits retrieval, not the identity checks of already available sources.

## Shared Rules

- Verify contributor roles as well as names. Use the article's author byline and
  author-specific publisher metadata; a DOI match or a list of all PDF/JATS names
  does not establish authorship. Academic editors, reviewers, correspondents and
  affiliations are not additional authors. In JATS, select the author contribution
  group and its applicable author roles rather than every `name`/`contrib` node;
  check the emitted order against the original byline before adopting the BibTeX.
- `Source ID` identifies the paper; `Claim Use ID` identifies one manuscript
  use. A source may support multiple claims, but it contributes only once to
  source-coverage, recency, and diversity quotas.
- Each row pairs one paper with one or two support sentences.
- Fill `Source Channel` for every row: `MCP-CNKI`, `MCP-IEEE`, `web`, `local`, `unknown`.
- For external channels (`web`, `MCP-*`, `Crossref`, `PubMed`, `Scholar`,
  `Semantic Scholar`, `IEEE`, `CNKI`, `WOS`), do not leave verification blank:
  `Verified` must be `yes`, `verified`, `pass`, or `true`, and
  `Verification Note` must state how the item was checked (DOI match, title
  match, Crossref/PubMed page, publisher page, database record, or local PDF
  metadata).
- If external verification cannot be completed, keep the row out of the usable
  adopted set, preserve its actual source channel and mark verification pending.
  Continue the source check while drafting from already supported evidence.
- Local sources still require bibliographic identity and cited-context checks. Record what the actual file supports and any unresolved provenance; a `local` channel or a blank verification field is not evidence of verification.
- Keep unresolved candidates visibly pending and separate from adopted sources.
  A legacy checker may reject pending rows; that diagnoses its input bank, not a
  reason to stop supported writing or change a source channel to conceal doubt.
- The bank is a candidate pool; final writing selects a coherent subset.

## Flow

1. **Collection pass:** Build the initial pool with `Source Channel` filled for
   every row.
2. **Verification pass:** Verify every external-source row and fill `Verified`
   plus `Verification Note`. Run `citation_quality_audit.py` and
   `citation_verification_en.py` where applicable.
3. **Coverage check:** distinguish `unique_source_count` from
   `claim_use_count`. Resolve a final target shortfall by finding and integrating
   relevant, verified support; do not silently reduce the requested coverage.
   If an explicit corpus restriction or venue rule prevents it, report the
   conflict and actual coverage. `CLOSED_CORPUS_EXHAUSTIVE` is a legacy checker
   marker for an exhausted supplied corpus, not another host writing gate.
   Never duplicate use rows to pad either mode.
4. **Curation:** Use only verified, context-matched sources in the manuscript. Keep unresolved candidates separate and continue drafting from the valid evidence already available; do not let an unused candidate's blank field block all writing.

## Candidate-bank diagnostics

Resolve the target from the saved custom count or the counted venue sample in
[journal-learning.md](journal-learning.md). Compare it with distinct entries
actually cited in the current manuscript, not the bank size, number of use rows
or uncited BibTeX entries. A bank check does not perform this final comparison.
If short, locate useful missing literature and integrate the supported points;
report a genuine scope/venue conflict rather than silently treating a diagnostic
PASS as meeting the preference. Reuse the existing notes and review.

```bash
python scripts/citation_bank_check.py <existing-bank.md> --target-count <resolved-target> --scope open_literature --markdown
python scripts/citation_bank_check.py <existing-bank.md> --target-count <resolved-target> --scope closed_corpus --markdown
python scripts/citation_quality_audit.py paper_rewriting_output --write
python scripts/citation_verification_en.py paper_rewriting_output/citation_support_bank.md --markdown --write
```
