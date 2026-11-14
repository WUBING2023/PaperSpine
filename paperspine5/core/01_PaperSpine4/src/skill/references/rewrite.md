# Rewrite Stage

This file is the canonical stage playbook for the paper-spine orchestrator.

## Purpose

Substantively rewrite an existing manuscript from confirmed motivation,
research outputs, and a compact evidence-aware writing plan.

## Inputs

Read the current draft, saved configuration and contribution/motivation choices,
actual source results, relevant literature and prior feedback. Identify which
reader problem needs repair and which scientific content remains valid.

Reuse the same task's valid configuration, choices, source evidence and learning notes. If a substantive input is missing, resolve that specific gap; the absence of a historical filename alone does not send the current host back to an old stage.

For full-paper reconstruction or a reference-guided rewrite, apply
[reference-guided-writing.md](reference-guided-writing.md). Establish the study's
question and contribution hierarchy before exemplar selection; learn complementary
moves from the existing learning pool, preserve an independent structure, and
use fresh-context writing followed by a distinct fresh reviewer when available.
Existing valid prose may remain. A local edit uses only affected claims/passages.

## Authorial Voice Restoration

Apply the saved author-expression preference through
assertive-scientific-writing.md. Preserve the prior draft, retain already-clear
text, and compare revised meaning, terminology, evidence and claim strength.
Use independent review for actual concerns; ordinary authorized editing does
not require another author confirmation or a detector/rhythm target.

## Historical helper inventory

Use these files only when an invoked helper or an explicit trace request needs
them. Existing notes may carry the reasoning in the current host; the requested
revised manuscript and its usable outputs are the delivery.

- `original_logic_map.md` - map the existing manuscript in order
- `evidence_bank.md`
- `section_blueprints.md`
- `writing_rationale_matrix.md` - strict-mode or user-requested rationale trace
- `results_validation.md` for journal, conference, and competition scenes
- `scientific_evidence_ledger.json` for journal, conference, and competition scenes
- `rewrite_matrix.md`
- `logic_transfer_audit.md`
- Revised manuscript
- `author_voice_profile.json`, `author_voice_revision.json`,
  `author_voice_receipt.json`, and `author_voice_report.md` when enabled

## Planning Depth

Balanced mode uses `section_blueprints.md`, the evidence ledger/results map, and
the Agent's own manuscript judgment. Do not create paragraph rows merely to fill
a matrix. Strict mode or an explicit trace request uses the matrix below.

Read `editorial-completeness.md`. Preserve or rebuild the full reader-facing
research arc rather than compressing the manuscript into a safer summary. The
Agent may depart from the old section structure when the contribution, venue,
and evidence support a better one; `tier` does not reduce manuscript scale.

## Writing Rationale Matrix (Strict / Optional)

| Row ID | Manuscript Unit | Original Problem or Planned Function | Contribution Promise / Claim ID | Motivation Alignment | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Change | Final Text Check |
|---|---|---|---|---|---|---|---|---|---|

First row: deeply justify the whole-work framework. Each subsequent row must
teach why this writing move is better.

When strict mode applies, read `references/writing-rationale-matrix.md` and apply its
full depth rules. Every non-trivial row must identify a contribution promise
and include concrete anchors from the aligned motivation, SOTA/example pattern,
target scene, evidence/citation, and the planned text move. For evidence-bearing
scenes, apply results-validation.md to the current results and claim boundaries
before dependent prose; a separate table/checker is not a drafting gate.
After drafting, every `Final Text Check` value must
start with `PASS` or `FAIL`; do not write vague notes such as "done" or only a
section location.

## Rewrite Rules

- Rewrite from the applicable evidence-aware plan. Use matrix rows when requested or useful; preserve valid passages and make the changes needed by the actual problem rather than merely appending generic prose.
- Preserve LaTeX commands, labels, citations, equations, figures, tables.
- Use `output_language` from config.
- Select citations sentence by sentence from `citation_support_bank.md`.
- `rewrite_matrix.md` maps original to final units, classifying each change.
- Read `references/assertive-scientific-writing.md`. State supported findings
  directly; put qualifications only where causal scope, generalization, or
  provenance genuinely changes.
- Use figure contracts and evidence maps as private scaffolding. Expand them
  into Results and Discussion that explain progression and meaning, rather than
  emitting a sequence of audited captions.

For a deeper, literature-informed pass — motivation-thread extraction,
move-guided section rewrite, structural-coherence pass, and a numerical /
cross-section motivation audit — apply the staged method in
`references/round1-literature-revision.md`.

## Review the revised paper

Use review-policy.md for an independent, located assessment of actual prose,
evidence and rendered outputs. Render when needed for that assessment; a
pre-LaTeX approval chain cannot inspect pagination or Word fidelity. Revise
affected passages and outputs in the same task, reusing valid unaffected work.
Compare the final distinct cited references with citation.md and rebuild portable
packages with submission.md. Report scientific, editorial, format and submission
limitations separately.
