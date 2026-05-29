# Rewrite Matrix Workflow

Use this reference when transforming a diagnosis or style profile into revised manuscript text.

## Principle

Do not rewrite by asking for "better prose." Rewrite by assigning each paragraph a motivation job, evidence source, model pattern, target length, and operation. The matrix must make shallow patching and motivation drift visible.

## Required Inputs

- User draft.
- `confirmed_motivation.md` showing the user-confirmed controlling motivation.
- `motivation_surface_map.md` showing how the motivation should appear in headings, topic sentences, transitions, and closure.
- `paper_diagnosis.md` or equivalent argument diagnosis.
- `original_logic_map.md` showing current section and paragraph logic.
- `style_profile.md` if style imitation is requested.
- `paragraph_function_templates.md` for section drafting.
- `result_narrative_templates.md` for Results drafting.
- `section_blueprints.md` for substantive rewrites.
- `evidence_bank.md` for Results and Discussion.
- Source map showing where data, claims, figures, and citations come from.

## Step 1: Build the Red Thread

Read `confirmed_motivation.md` and derive one sentence from it:

```text
This paper addresses [specific problem] for [specific audience/context] by [approach], showing that [main supported finding], which matters because [significance].
```

Every section, subsection opening, transition, and Discussion closure should either set up, test, support, interpret, or qualify this sentence. Headings should be natural navigation labels that support the same logic without mechanically repeating the motivation. If the draft suggests a different motivation, return to motivation intake instead of silently changing the spine.

## Step 2: Make the Section Role Map

```markdown
| Section | Current Role | Motivation Job Needed | Heading/Surface Decision | Main Defect | Action |
|---|---|---|---|---|---|
| Abstract | | | | | |
| Introduction | | | | | |
| Methods | | | | | |
| Results | | | | | |
| Discussion | | | | | |
```

Common defects:

- background without a gap,
- method recipe without rationale,
- results without interpretation,
- discussion that repeats instead of resolving,
- claims that are stronger than evidence,
- paragraphs that contain several moves at once.

## Step 3: Create Paragraph Rows

Save as `paper_rewriting_output/rewrite_matrix.md`.

```markdown
| Section | Unit ID | Current Function | Motivation Link | Operation | Intended Move | Evidence Source | Model Pattern | Target Length | Logic Change | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
```

Use these move labels unless the field has a better taxonomy:

| Section | Common Moves |
|---|---|
| Abstract | background, problem, method, key result, significance |
| Introduction | territory, prior work, gap, problem statement, contribution, paper roadmap |
| Methods | materials/data, procedure, rationale, implementation, evaluation |
| Results | setup, headline finding, evidence, comparison, interpretation |
| Discussion | answer, significance, mechanism, comparison with prior work, limitation, implication |

## Step 4: Rewrite Row by Row

For each row:

1. Read the original paragraph.
2. Read the relevant `style_profile.md` section.
3. Confirm the row's motivation job from `confirmed_motivation.md` and `motivation_surface_map.md`.
4. Confirm the intended move.
5. Verify the evidence source.
6. Cite the exact paragraph-function or result-narrative template row.
7. State the logic change from `original_logic_map.md`.
8. Choose the operation: `REWRITE`, `SPLIT`, `MERGE`, `DELETE`, `MOVE`, `ADD`, or `KEEP`.
9. Write the paragraph with the target length and claim strength.
10. Check that no number or citation was invented.

For style imitation, prefer `REWRITE`, `SPLIT`, `MERGE`, and `MOVE`. Treat repeated `KEEP` or `ADD` rows as a warning that the revision is shallow.

Do not change LaTeX commands during this step. If the source is `.tex`, draft the new prose from the blueprint first, then transplant it around preserved labels, citations, equations, and figure/table blocks.

## Step 4.5: Closed-Book Rewrite

For major sections, do not edit the original paragraph in place.

1. Extract facts, numbers, citations, and figure references into notes.
2. Hide the original prose.
3. Write the new section from `section_blueprints.md` and notes.
4. Reopen the original only for integrity checks.

This is mandatory when the user complains that prior revisions only added sentences or were too shallow.

## Step 5: Section Audit

After each section:

```markdown
## Section Audit: [Section]

| Check | Result | Notes |
|---|---|---|
| All obligatory moves present | pass/fail | |
| Move order matches style profile | pass/fail | |
| Red thread advanced | pass/fail | |
| Heading/opening follows motivation surface map | pass/fail | |
| Every paragraph has a motivation job | pass/fail | |
| Numbers traced | pass/fail | |
| Claims calibrated | pass/fail | |
| LaTeX commands preserved | pass/fail/not applicable | |
```

## Step 6: Whole-Paper Audit

Use the seven-sentence lineage test:

1. Abstract final sentence.
2. Introduction opening sentence.
3. Introduction gap sentence.
4. Introduction final contribution sentence.
5. Methods opening/rationale sentence.
6. Results first headline finding.
7. Discussion closing sentence.

These sentences should tell one coherent story. If they do not, revise the relevant section anchors before polishing local language.

Also run the surface test: title/subtitle if editable, Results subsection headings, figure/table callouts, and Discussion closing sentence should all support the same confirmed motivation without repeating a slogan.

## Step 7: Logic-Transfer Audit

Create `paper_rewriting_output/logic_transfer_audit.md` using `references/logic-transfer-audit.md`. A rewrite is not done until the audit can state how each major section's reasoning changed.

Minimum table:

```markdown
| Section | Original Logic | Learned Target Logic | Revised Logic | Evidence of Transfer | Verdict |
|---|---|---|---|---|---|
```

If the audit says the original logic is mostly preserved in a section that was diagnosed as weak, rebuild that section from the blueprint.

## Step 8: Shallow-Edit Audit

Run:

```bash
python scripts/revision_audit.py <original> <revised> --markdown > paper_rewriting_output/revision_audit.md
```

Interpretation:

- High unchanged ratio means the rewrite preserved too much old prose.
- High addition ratio means the rewrite mainly appended content.
- High similarity in weak sections means the section should be rebuilt from the blueprint.

If the user asked for deep imitation, do not finalize until the audit is acceptable or the report explicitly explains why unchanged text was necessary.

## Editing Rules

- Prefer deleting weak generic text over adding unsupported claims.
- Keep user-provided technical terms unless the style profile gives a better field-standard term.
- Preserve all user data exactly unless the user confirms a correction.
- Mark missing evidence as `[NEED DATA: ...]`.
- Mark missing citations as `[NEED CITATION: ...]`.
- Use the style corpus for structure and language patterns, not for scientific facts about the user's experiment.

## Output Summary

End a rewrite pass with:

```markdown
## Rewrite Summary

| Section | Main Change | Evidence Preserved? | Style Rule Applied | Remaining Author Task |
|---|---|---|---|---|

## Motivation Surface

| Surface Element | Changed? | Motivation Link | Remaining Weakness |
|---|---|---|---|

## Logic Transfer

| Section | Logic Changed? | Learned Pattern Used | Remaining Weakness |
|---|---|---|---|

## Integrity Notes

- Numbers changed:
- Claims softened:
- Unsupported claims removed:
- Author decisions needed:

## Shallow-Edit Audit

- Near-identical paragraph ratio:
- Addition-heavy:
- Sections requiring another pass:
```
