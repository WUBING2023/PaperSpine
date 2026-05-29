# Motivation-Thread Writing

Use this when the user wants a strong paper rather than a polished draft. The motivation thread is the backbone and highest-priority organizing constraint of the manuscript.

## Core Idea

A good paper is not a set of improved sections. It is one problem-solution arc:

```text
Field problem -> specific gap -> design response -> evidence -> interpretation -> limitation/future
```

Every section should advance that arc. The arc should be visible at strategic reader touchpoints: title if editable, abstract order, Introduction promise, direct-evidence section, key transitions, figure/table callouts, and Discussion closure. Do not force the same motivation keyword into every subsection heading.

## Motivation Confirmation Comes First

Before building the motivation thread model, create or verify `paper_rewriting_output/confirmed_motivation.md`. The user's confirmed motivation is the spine. Exemplar papers may teach rhetorical moves, but they must not choose the paper's motivation for the user.

There are two allowed intake paths:

1. If the user provides a clear motivation and confirms it, save it directly as `confirmed_motivation.md`.
2. If the user does not provide one, infer 3-5 options from the draft and evidence, save `motivation_options.md`, and stop for user selection or editing.

Do not proceed to section blueprints or manuscript rewriting while only `motivation_options.md` exists.

## Motivation Options Template

Save as `paper_rewriting_output/motivation_options.md` when motivation is absent or unclear.

```markdown
# Motivation Options

| Option | One-Sentence Motivation | Field Problem | Specific Gap | Design Response | Evidence Available | Fit To Target Venue | Risk | What Would Be Emphasized | What Would Be De-Emphasized |
|---|---|---|---|---|---|---|---|---|---|
| A | | | | | | | | | |
| B | | | | | | | | | |
| C | | | | | | | | | |

## User Decision Needed

Choose one option, edit one option, combine parts, or write a new motivation.
```

Each option must be a real strategic choice. Do not create cosmetic variants. A useful option changes at least one of: Introduction gap, Methods rationale, Results emphasis, Discussion interpretation, or target-venue fit.

## Confirmed Motivation Template

Save as `paper_rewriting_output/confirmed_motivation.md`.

```markdown
# Confirmed Motivation

| Field | Content |
|---|---|
| Source | user-provided / selected option / edited option |
| Confirmed motivation statement | |
| One-sentence red thread | |
| Field problem | |
| Specific gap | |
| Design response | |
| Main evidence available | |
| Target-venue fit | |
| Prioritized claims | |
| Claims to avoid | |
| Secondary motivations or boundaries | |
| Surface language priorities | title/heading/topic-sentence language that should foreground the motivation |

## Section Consequences

| Section | What This Motivation Requires | What It Should Avoid |
|---|---|---|
| Abstract | | |
| Introduction | | |
| Methods | | |
| Results | | |
| Discussion | | |
```

`confirmed_motivation.md` must say not only what the paper argues, but also what it should not argue. This prevents later sections from drifting into generic claims.

## Required Output

After `confirmed_motivation.md` exists, save:

- `paper_rewriting_output/motivation_thread_model.md`
- `paper_rewriting_output/motivation_surface_map.md`

```markdown
# Motivation Thread Model

## Confirmed Motivation Source

Derived from `paper_rewriting_output/confirmed_motivation.md`.

## One-Sentence Red Thread

This paper addresses [specific problem] because [why it matters], by [design response], showing [supported finding], which matters because [field-level implication].

## Problem-Solution Arc

| Arc Element | Content | Evidence Source | Required Section |
|---|---|---|---|
| Field problem | | | Introduction P1 |
| Measurement/computational bottleneck | | | Introduction P2 |
| Prior method limitation | | | Introduction P3 |
| Specific gap | | | Introduction P4 |
| Design response | | | Introduction P5 / Methods |
| Primary evidence | | | Results 1 |
| Component evidence | | | Results 2 |
| Generalization evidence | | | Results 3 |
| Biological interpretability | | | Results 4-5 |
| Final interpretation | | | Discussion |

## Introduction-to-Discussion Closure Map

| Introduction Claim/Question | Where Results Answer It | Where Discussion Resolves It |
|---|---|---|

## Introduction-to-Results Promise Map

| Final Introduction Promise | Results Subsection That Tests It | Required Evidence | Result Narrative Template |
|---|---|---|---|

## Section Anchors

| Section | Opening Job | Closing Job | Must Mention | Must Avoid |
|---|---|---|---|---|
```

Then save the reader-visible layer as `paper_rewriting_output/motivation_surface_map.md`.

```markdown
# Motivation Surface Map

| Surface Element | Current Wording | Motivation Role | Proposed Wording/Strategy | Venue Constraint | Status |
|---|---|---|---|---|---|
| Title/subtitle | | | | | |
| Abstract opening | | | | | |
| Abstract contribution sentence | | | | | |
| Abstract closing | | | | | |
| Introduction paragraph topic sentences | | | | | |
| Methods subsection headings/openings | | | | | |
| Results subsection headings/openings | | | | | |
| Figure/table callouts | | | | | |
| Discussion opening | | | | | |
| Discussion closing | | | | | |
```

Use motivation-led wording where it reads naturally and helps navigation. If a neutral heading is clearer, use the heading for the section's logical job and put the motivation in the opening sentence or transition.

## How To Use It

1. Derive the red thread from `confirmed_motivation.md` before writing any section.
2. Convert the red thread into paragraph jobs.
3. Convert the red thread into the visible manuscript surface: a few strategic headings, topic sentences, transitions, and callouts.
4. Make the final Introduction paragraph a promise of what the Results will prove.
5. Make the first Discussion paragraph answer that promise.
6. Map every Results subsection to one Introduction promise and one `result_narrative_templates.md` row.
7. Delete or move content that does not support the red thread.

## Motivation-Led Section Rules

### Introduction

The Introduction should not be a literature list. It should create necessity.

Typical move order:

1. Establish the biological or computational importance.
2. Explain why the task is hard.
3. Show what prior methods solved.
4. Identify what remains unresolved.
5. Present the method as a direct response.
6. Preview the evidence that will support the response.

The paragraph openings should make the motivation progressively narrower: field problem, bottleneck, prior-work limit, unresolved gap, response, and testable promise.

### Methods

Methods should not read like code documentation. Each design choice should answer a motivation:

- Why this input?
- Why this architecture?
- Why this loss?
- Why this evaluation split?
- Why these metrics?

When subsection headings are editable, prefer headings that identify the design rationale or evaluation purpose in natural journal language. Avoid repeating the same motivation term in every heading; use the first sentence to carry the motivation when a neutral heading is clearer.

### Results

Results should not be a metric dump. Each subsection should test one promise from the Introduction:

1. setup/question,
2. figure or metric evidence,
3. comparison,
4. interpretation,
5. implication for the motivation thread.

Before rewriting a Results subsection, write one sentence:

```text
This subsection tests the Introduction promise that [promise] by showing [evidence], which supports [interpretation] but does not claim more than [limit].
```

Results headings should help the reader see the section logic. They may name a benchmark, transfer test, motif analysis, or direct biological test; avoid turning every heading into a repeated slogan.

### Discussion

Discussion should close the loop:

1. restate the answer, not just the method,
2. explain what each design choice contributed,
3. place the result relative to prior work,
4. state limitations without undermining the central claim,
5. end with the field-level implication.

The final paragraph should return to the confirmed motivation, not to a generic claim that the method is useful.
