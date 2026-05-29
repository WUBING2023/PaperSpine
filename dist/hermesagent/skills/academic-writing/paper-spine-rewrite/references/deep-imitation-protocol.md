# Deep Imitation Protocol

Use this reference when the user says the revision must learn from or imitate excellent papers. This protocol is designed to prevent shallow edits that merely add a few sentences to the old draft.

## What "Learning From Papers" Means

Learning is not copying phrases and not loosely "sounding academic." It is extracting reusable writing decisions:

| Layer | What to Learn | Output |
|---|---|---|
| Argument architecture | how the paper moves from field problem to contribution | move sequence |
| Section rhythm | paragraph count, paragraph jobs, length distribution | section blueprint |
| Claim calibration | how strongly claims are stated given evidence | claim rules |
| Evidence placement | where numbers, figures, citations, and caveats appear | evidence placement map |
| Sentence architecture | sentence roles and slots, not copied sentences | skeleton bank |
| Reader contract | what the paper assumes, explains, and omits | audience rule |

The output of learning is `style_profile.md` plus `section_blueprints.md`. If these artifacts do not exist, no deep imitation has happened.

## Three-Table Method

For each target section, create three tables.

### Table 1: Exemplar Move Table

```markdown
| Exemplar | Paragraph | Move | Evidence Type | Opening Function | Closing Function | Notes |
|---|---|---|---|---|---|---|
```

Fill this from 3-6 exemplar papers. Use exact quotations only inside analysis notes. Convert them into abstract patterns before rewriting.

### Table 2: User Draft Move Table

```markdown
| Draft Paragraph | Current Move | Evidence Present | Problem | Keepable Content |
|---|---|---|---|---|
```

Mark problems honestly:

- wrong move,
- move missing,
- multiple moves in one paragraph,
- unsupported claim,
- weak transition,
- wrong level of detail,
- not aligned with target style.

### Table 3: Target Section Blueprint

```markdown
| Target Paragraph | Move | Source Evidence | Exemplar Pattern | Target Length | Required Operation |
|---|---|---|---|---|---|
```

Allowed operations:

- `REWRITE`: old content is retained as evidence, but prose and structure are regenerated.
- `SPLIT`: one overpacked draft paragraph becomes multiple target paragraphs.
- `MERGE`: several weak paragraphs become one stronger paragraph.
- `DELETE`: unsupported or off-thread content is removed.
- `MOVE`: content moves to a better section.
- `ADD`: new connective or explanatory text is added from existing evidence.
- `KEEP`: paragraph is retained nearly as-is, with explicit justification.

`KEEP` should be rare in style imitation. `ADD` should be secondary.

## Closed-Book Section Rewrite

Use this procedure for each important section:

1. Read the original section and extract facts, claims, citations, figure references, and numbers into notes.
2. Read the exemplar move table and section blueprint.
3. Stop looking at the original prose.
4. Draft the new section from notes and blueprint.
5. Reopen the original only to verify that claims, numbers, citations, and figure references are preserved.
6. Run `revision_audit.py` to detect near-identical paragraphs.

This prevents the common failure mode where the model simply edits one sentence, adds one sentence, and leaves the rest untouched.

## Minimum Rewrite Standards

For substantive revision, the output should usually satisfy:

| Metric | Target |
|---|---|
| Near-identical paragraph ratio | below 35% for revised sections |
| Dominant operation | not `ADD` |
| `KEEP` rows | below 25% unless the user requested minor polish |
| Missing obligatory moves | 0 |
| Unsupported new claims | 0 |
| Numbers without source | 0 |

These are not universal quality metrics, but they catch shallow revision.

## Section Blueprint Requirements

Each blueprint must answer:

1. What is this section's communicative job?
2. Which exemplar paper provides the closest section structure?
3. What moves are obligatory?
4. What order should the moves appear in?
5. What old content should be deleted, merged, split, or moved?
6. What evidence from the user's materials supports each target paragraph?
7. What style constraints apply: sentence length, citation density, claim strength, opening/closing style?

## Results and Discussion Discipline

For Results:

- Do not borrow results from exemplar papers.
- Do not infer numerical values from figures unless the user permits visual estimation.
- Prefer exact values from tables/logs/source draft.
- If a figure exists but the data are not available, describe only visually supported qualitative patterns and mark `[AUTHOR VERIFY]`.

For Discussion:

- Resolve the Introduction's gap using the user's results.
- Compare to prior work only with citations already present or supplied.
- Limit future work and limitations to claims supported by the study design.

## Failure Pattern: Patch Writing

Patch writing looks like:

- "This paragraph is adequate; minor polish only" repeated across the matrix.
- Most actions are `ADD` or `KEEP`.
- A new subsection is added, but existing weak sections are untouched.
- Exemplar papers appear in the report but not in the actual paragraph plan.
- No section blueprint exists.
- No audit compares original and revised text.

When this happens, discard the patch pass and redo the section with the closed-book method.
