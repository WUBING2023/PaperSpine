# Writing Rationale Matrix

Use this reference in both `rewrite_existing` and `build_from_materials`.

The matrix is the core writing method. It must be written before final prose and
then used as the checklist for drafting/revision. It is not a post-hoc change
log and it is not a fixed IMRaD template.

## Principle

Create one row for each smallest useful writing unit that needs a deliberate
choice. The unit size depends on the task:

- journal or conference paper: framework, title/abstract units, Introduction
  moves, method-design explanations, result evidence units, figure/table claims,
  discussion moves, captions, and claim-bearing headings;
- report or review: executive summary units, problem/background units, taxonomy
  or comparison units, evidence synthesis units, recommendation units,
  limitation/future-work units, and important headings/figures/tables;
- competition paper/report: problem restatement, assumptions, notation, model
  design, solution procedure, validation, sensitivity/robustness, strengths and
  weaknesses, recommendations, and visual/table claims.

Do not force every task into Abstract/Introduction/Methods/Results/Discussion.
Do not use only one row per top-level section. Split the manuscript into
paragraph-sized or claim-sized units whenever the writing decision changes.

## Required Table

| Row ID | Manuscript Unit | Current Problem or Planned Function | Motivation Link | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Change/Text Move | Final Text Check |
|---|---|---|---|---|---|---|---|---|

## Required Coverage

- The first data row must justify the whole-work framework, structure, or main
  throughline.
- Every subsequent row should correspond to a real writing unit in manuscript
  order.
- Use task-specific units rather than a fixed template. For example, a
  competition solution may need rows for assumptions, symbols, model derivation,
  algorithm steps, sensitivity analysis, and recommendations; a review may need
  rows for search scope, inclusion logic, taxonomy, comparison dimensions, and
  synthesis claims.
- Include titles, subsection headings, figure captions, and table captions when
  they carry argument logic.
- If one paragraph has two separate functions, split it into two rows. If three
  short paragraphs share one function, one row may cover that paragraph group.

## Reason Quality Bar

Every row must contain concrete reasoning, not generic polishing language. It
should explain how the unit uses all major anchors whenever possible:

- advances or narrows the confirmed motivation,
- transfers a structural move learned from SOTA/example work without copying
  wording or results,
- matches a target journal/conference/report/competition norm,
- uses a specific user evidence item, figure, table, result, or citation anchor,
- moves evidence next to the claim it supports,
- creates a front/back echo with an earlier or later unit,
- fixes an original logic failure,
- prevents overclaiming beyond available evidence.

Generic reasons such as "improve clarity", "make academic", "polish wording",
or "add detail" do not pass.

Minimum depth requirement:

- Use at least 8 rows for ordinary manuscripts/reports. Longer manuscripts
  should have many more rows. A complex paper often needs 20-60 rows.
- The first row is the whole-work framework row. It must deeply explain the
  controlling structure: why this structure is chosen, how it comes from the
  confirmed motivation, what SOTA/example pattern it transfers, how it matches
  the target scene, which user evidence anchors it, and how later sections will
  be checked against it.
- Each non-trivial row must contain enough detail to teach the writing decision,
  not only name the section. Include motivation, learned reference/SOTA pattern,
  target-scene norm, evidence/citation anchor, planned text move, and final
  check. If any of these is not applicable, state why.
- Do not compress a large decision into one phrase such as "conservation-first
  abstract" or "add ablation section". Explain why that move changes the paper's
  logic and how the final text will prove it.

## Rewrite And Build Discipline

The final manuscript should be drafted row by row. For rewrite tasks, each row
should be traceable to the original logic map and/or a deliberate structural
change. For build-from-materials tasks, each row should be traceable to the
source inventory, evidence bank, claim register, or figure asset map.

After drafting, update the `Final Text Check` column with the final location or
a short pass/fail note.
## Detail Standard

A row should be detailed enough that the user can learn the writing logic from
it. Do not write rows like "graphic path fix" or "rewrite abstract" as the main
explanation. For every non-trivial row, include:

- what the original or planned unit is trying to achieve,
- why the current version is logically weak or why this unit is needed,
- how the confirmed motivation controls this unit,
- which SOTA/example/target-scene pattern is being transferred,
- which user evidence, figure, table, result, or citation anchor supports it,
- what exact rhetorical move will be made,
- how the final text should be checked.

For important units, prefer 2-4 sentences inside cells rather than keywords.
The matrix should be useful as a learning document, not only an audit checklist.

## Deep Framework Row Example

The whole-work row should look more like a design memo than a TODO item:

| Row ID | Manuscript Unit | Current Problem or Planned Function | Motivation Link | Reference/SOTA Pattern Learned | Target Scene or Venue Norm | User Evidence or Citation Anchor | Planned Change/Text Move | Final Text Check |
|---|---|---|---|---|---|---|---|---|
| F1 | Whole-work framework | Decide the paper's controlling argument before editing any paragraph. The current draft may contain multiple valid technical points, but the paper needs one dominant contribution and a sequence of evidence that makes that contribution inevitable. | The confirmed motivation becomes the spine: the paper first exposes the missing signal or unresolved evaluation problem, then shows why the proposed design is needed, then lets results test that promise. Secondary engineering choices are positioned as enabling mechanisms, not competing innovations. | Learn from SOTA and target examples at the level of structure: how they stage gap, design rationale, evidence order, failure modes, and bounded discussion. Do not copy wording; transfer the move that makes the reader accept why this paper had to be written. | The target scene expects a recognizable argument architecture. A journal paper may need IMRaD and independent evaluation; a competition report may need assumptions, model logic, validation, sensitivity, and recommendations; a course report may need rubric-visible evidence. | Anchor the framework to the user's actual draft/materials: source_map.md, evidence_bank.md, figures/tables, citations, experiment settings, claim register, and any special requirements. External papers only teach writing logic. | Reframe the manuscript so every major section answers one part of the same question. Move background, method rationale, results interpretation, captions, and discussion claims until the evidence sequence is visible. | Pass only if a reader can summarize the paper's problem, gap, design, evidence, limitation, and implication from the ordered section openings and captions without seeing unsupported claims. |
