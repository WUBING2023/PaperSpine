# Exemplar Learning Dossier

Use this when the user asks the skill to learn from excellent papers. The dossier is the main learning artifact. It should be produced before `paragraph_function_templates.md`, `result_narrative_templates.md`, `style_profile.md`, `section_blueprints.md`, or manuscript writing.

## Goal

Explain why selected papers are well written and how their writing logic should transfer to the user's manuscript.

Do not merely summarize each paper. The dossier must answer:

- How does the paper make the reader care?
- How does it narrow from field problem to specific gap?
- How does each Introduction paragraph function?
- How do Methods justify choices rather than list procedures?
- How do Results turn measurements into claims?
- How does Discussion close the loop opened in the Introduction?
- What should our paper imitate, avoid, or adapt?

## Required Output

Save as `paper_rewriting_output/exemplar_learning_dossier.md`.

```markdown
# Exemplar Learning Dossier

## Corpus

| ID | Paper | Venue/Year | Role | Why This Paper Is Worth Learning From |
|---|---|---|---|---|

## What Makes These Papers Good

| Dimension | Observed Pattern | Why It Works | Transfer Rule for Our Paper |
|---|---|---|---|
| Motivation | | | |
| Gap construction | | | |
| Contribution framing | | | |
| Method explanation | | | |
| Result interpretation | | | |
| Discussion closure | | | |

## Section-Level Learning

### Introduction

| Paper | Paragraph | Move | How It Works | Transfer Rule |
|---|---:|---|---|---|

### Methods / System and Methods

| Paper | Subsection | Move | How It Works | Transfer Rule |
|---|---|---|---|---|

### Results

| Paper | Subsection | Move | Evidence Pattern | Interpretation Pattern | Transfer Rule |
|---|---|---|---|---|---|

### Discussion

| Paper | Paragraph | Move | How It Resolves Motivation | Transfer Rule |
|---|---:|---|---|---|

## Sentence Skeletons

Use skeletons, not copied wording.

| Function | Skeleton | Source Logic | Where To Use |
|---|---|---|---|

## Anti-Patterns To Avoid

| Anti-Pattern | Why It Fails | Replacement |
|---|---|---|

## Transfer Plan

| Our Section | Learned Pattern | Required Rebuild |
|---|---|---|
```

Also save:

- `paper_rewriting_output/paragraph_function_templates.md`
- `paper_rewriting_output/result_narrative_templates.md`

The dossier explains the papers; the templates convert that explanation into reusable writing logic for the user's manuscript.

## Reading Procedure

For each exemplar:

1. Read the abstract and identify the five moves.
2. Map each Introduction paragraph to a rhetorical job.
3. Identify the first sentence and last sentence of each major section.
4. In Methods, mark where the paper explains why a design choice is needed.
5. In Results, mark the sequence: setup -> metric/figure -> comparison -> interpretation -> transition.
6. In Discussion, map each paragraph to: summary, mechanism/significance, limitations, future/closure.
7. Extract reusable sentence skeletons with slots.

## Paragraph Function Template

Save as `paper_rewriting_output/paragraph_function_templates.md`.

```markdown
# Paragraph Function Templates

## Template Rules

- Corpus basis:
- Target venue:
- Transfer principle:

## Section Templates

| Section | Paragraph Slot | Reader Question | Rhetorical Move | Typical Opening Function | Typical Closing Function | Evidence Needed From Our Paper | Forbidden Shortcut |
|---|---:|---|---|---|---|---|---|
| Abstract | 1 | | | | | | |
| Introduction | 1 | | | | | | |
| Methods | 1 | | | | | | |
| Results | 1 | | | | | | |
| Discussion | 1 | | | | | | |

## Transfer Notes

| Our Section | Original Defect | Template That Fixes It | Rewrite Consequence |
|---|---|---|---|
```

Each row must be tied to at least one exemplar pattern or target-venue requirement. Do not write generic advice such as "make it clear" or "add motivation."

## Results Narrative Template

Save as `paper_rewriting_output/result_narrative_templates.md`.

```markdown
# Result Narrative Templates

## Corpus Pattern Summary

| Pattern | Exemplar Evidence | Why It Works | Transfer Rule |
|---|---|---|---|

## Subsection-Level Templates

| Result Type | Setup Question | Evidence Move | Comparison Move | Interpretation Move | Transition Move | Claim-Strength Limit |
|---|---|---|---|---|---|---|
| benchmark | | | | | | |
| ablation | | | | | | |
| generalization | | | | | | |
| interpretability | | | | | | |
| biological analysis | | | | | | |

## Anti-Metric-Dump Rules

| Weak Pattern | Why It Fails | Replacement Pattern |
|---|---|---|
```

For each Results subsection in the user's manuscript, the later rewrite matrix must cite one template row.

## Completion Test

The dossier is incomplete if it cannot tell the writer:

- how many paragraphs the Introduction should have,
- what each paragraph should do,
- which Results subsection should come first and why,
- what the first Discussion paragraph must resolve,
- what tone and claim strength fit the venue,
- what content from the original draft should be deleted or moved,
- which paragraph-function template each major rewritten paragraph will follow,
- which result-narrative template each Results subsection will follow.
