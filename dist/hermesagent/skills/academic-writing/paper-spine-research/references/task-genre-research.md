# Task-Genre Research

Use this when the user wants the same learning-and-writing method applied to a paper-like task that is not simply a journal/conference manuscript.

Examples include mathematical-modeling contest papers, technical reports, thesis/proposal-style reports, review reports, policy/white-paper style analyses, grant-like narratives, or other structured documents with a target audience and evaluation criteria.

## Core Principle

Do not assume the journal-paper structure. First learn the task genre:

```text
audience -> evaluation criteria -> required deliverable -> exemplar structure -> evidence standard -> writing strategy
```

The output should still be motivation-driven, but the "motivation" may be a problem objective, client need, decision question, scoring criterion, or design constraint rather than a scientific contribution.

## Required Output

Save as `paper_rewriting_output/genre_research.md`.

```markdown
# Genre Research

## Task Identity

| Field | Content |
|---|---|
| Task type | |
| Target audience/evaluator | |
| Official rules/rubric/source | |
| Required deliverable format | |
| Length/page constraints | |
| Language/style expectations | |

## Evaluation Logic

| Criterion | What Evaluators Reward | What They Penalize | Writing Consequence |
|---|---|---|---|

## Exemplar Learning

| Exemplar | Why Selected | Section Order | Strong Moves | Transferable Pattern | Do Not Copy |
|---|---|---|---|---|---|

## Genre-Specific Section Blueprint

| Section | Reader/Evaluator Question | Required Evidence | Typical Move Sequence | Common Failure |
|---|---|---|---|---|

## Writing Strategy

- central objective:
- required assumptions or constraints:
- model/method/evidence chain:
- validation/sensitivity/robustness requirement:
- figure/table role:
- final recommendation or conclusion role:
```

## Modeling-Contest Report Pattern

For mathematical-modeling style reports, learn these elements from rules and strong exemplars:

- problem restatement that translates the prompt into decision variables and objectives,
- assumptions that are necessary, testable, and not merely convenient,
- notation table and variable definitions,
- model construction with a clear reason for each modeling choice,
- algorithm or solution procedure that is reproducible,
- validation, sensitivity analysis, error analysis, or robustness checks,
- strengths and weaknesses tied to assumptions,
- concise summary/memo if required by the contest,
- figures/tables that explain model behavior, not only decorate results.

Do not over-academicize contest papers. Judges often reward clear problem decomposition, transparent assumptions, executable models, and persuasive validation more than literature-style novelty.

## Technical/White-Paper Report Pattern

For technical, policy, or decision reports:

- identify the decision-maker and decision question,
- separate facts, assumptions, analysis, and recommendation,
- put the most actionable result early,
- use figures/tables to support decisions,
- state uncertainty and implementation constraints plainly.

## Proposal/Grant-Like Pattern

For proposal-style documents:

- create urgency and fit,
- define a feasible aim structure,
- connect methods to risks and milestones,
- show expected outcomes and contingency plans,
- avoid writing as if results already exist.

## Red Flags

- The document follows a journal IMRaD structure when the target genre rewards another structure.
- The problem is restated without variables, constraints, or evaluator-relevant objectives.
- Assumptions are generic and not used later.
- A model is described but not validated.
- Results are listed without a decision, recommendation, or scoring-relevant interpretation.
- Exemplar learning copies surface formatting but misses the evaluation logic.
