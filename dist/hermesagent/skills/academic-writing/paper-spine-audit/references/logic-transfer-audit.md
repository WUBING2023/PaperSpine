# Logic Transfer Audit

Use this reference when a rewrite must prove that it learned from strong papers and changed the manuscript's argument logic, not only wording, length, or LaTeX formatting.

## Purpose

A successful revision should be able to answer four questions:

1. What was the original manuscript trying to do?
2. What logic did the target venue and exemplar papers teach us?
3. What logic does the revised manuscript now use?
4. Which concrete paragraphs, section openings, result framings, and discussion closures changed because of that learning?

If these questions cannot be answered, the rewrite is not complete.

## Required Inputs

- `source_map.md`
- `target_journal_research.md` when a venue is named
- `paper_diagnosis.md`
- `original_logic_map.md`
- `exemplar_learning_dossier.md`
- `paragraph_function_templates.md`
- `result_narrative_templates.md` for Results rewriting
- `style_profile.md`
- `motivation_thread_model.md`
- `section_blueprints.md`
- `rewrite_matrix.md`
- original manuscript
- revised manuscript

## Required Output

Save as `paper_rewriting_output/logic_transfer_audit.md`.

```markdown
# Logic Transfer Audit

## Executive Verdict

- Logic transfer verdict:
- Strongest transferred pattern:
- Weakest section:
- Sections requiring another rewrite:

## Whole-Paper Argument Lineage

| Anchor | Original Manuscript | Revised Manuscript | Improvement Type | Pass/Fail |
|---|---|---|---|---|
| Abstract motivation | | | | |
| Introduction opening problem | | | | |
| Introduction gap sentence | | | | |
| Final Introduction promise | | | | |
| Methods rationale sentence | | | | |
| First Results headline | | | | |
| Discussion first answer sentence | | | | |
| Discussion closing implication | | | | |

## Section Logic Comparison

| Section | Original Logic | Learned Target Logic | Revised Logic | Evidence of Transfer | Verdict |
|---|---|---|---|---|---|
| Abstract | | | | | |
| Introduction | | | | | |
| Methods | | | | | |
| Results | | | | | |
| Discussion | | | | | |

## Paragraph Function Transfer

| Section | Paragraph Slot | Original Function | Target Function Template | Revised Function | Transfer Quality |
|---|---:|---|---|---|---|

## Results Narrative Transfer

| Result Subsection | Introduction Promise Tested | Evidence Used | Interpretation Added | Transition/Implication | Verdict |
|---|---|---|---|---|---|

## Shallow Patch Check

| Warning Sign | Observed? | Evidence | Required Fix |
|---|---|---|---|
| Same paragraph order with sentence-level polish | | | |
| Mostly append-only revision | | | |
| New claims without evidence bank support | | | |
| Results still metric-dump style | | | |
| Discussion repeats Results without resolving motivation | | | |
| LaTeX formatting work displaced writing logic | | | |
```

## Procedure

### 1. Extract the Original Logic

Use `original_logic_map.md`, not memory. For each major section, identify:

- the reader question the section currently answers,
- the paragraph move sequence,
- where the section starts and ends logically,
- what evidence it uses,
- what it fails to explain.

Label common defects precisely:

| Defect | Meaning |
|---|---|
| `background-stack` | literature/background is listed without narrowing to necessity |
| `gap-vague` | gap is present but not operational or testable |
| `method-recipe` | Methods list components without explaining design need |
| `metric-dump` | Results report numbers without interpreting what promise they test |
| `claim-leap` | interpretation exceeds evidence |
| `discussion-repeat` | Discussion repeats Results instead of resolving motivation |
| `latex-driven` | revision focused on formatting rather than argument |

### 2. State the Learned Target Logic

Use the dossier and templates. For each section, name the learned pattern:

- Abstract: motivation -> gap -> method -> key evidence -> significance.
- Introduction: field problem -> bottleneck -> prior progress -> unresolved gap -> design response -> evidence preview.
- Methods: design need -> implementation choice -> rationale -> evaluation.
- Results: question/promise -> evidence -> comparison -> interpretation -> transition.
- Discussion: answer -> mechanism/significance -> relation to prior work -> limitations -> field implication.

If the target venue uses a different pattern, use the venue-specific pattern and cite the artifact that supports it.

### 3. Compare Revised Logic Against Both Baselines

For every major section, compare three things:

1. Original logic.
2. Learned target logic.
3. Revised logic.

The revised section passes only if it follows the learned target logic while preserving the user's actual evidence.

Do not give credit for:

- changing synonyms,
- adding one explanatory sentence after an unchanged paragraph,
- adding generic motivation without connecting it to Results,
- preserving all original paragraph roles in the same order when those roles were diagnosed as weak.

### 4. Run the Seven-Anchor Test

Extract these exact anchors from original and revised manuscripts:

1. Abstract motivation sentence.
2. First Introduction problem sentence.
3. Main gap sentence.
4. Final Introduction contribution or roadmap sentence.
5. First Methods rationale sentence.
6. First Results headline finding.
7. First Discussion answer sentence.

The revised anchors should form one coherent problem-solution-evidence-resolution arc. If the arc breaks, revise the corresponding section blueprint before polishing language.

### 5. Audit Results Subsections

For each Results subsection, require:

| Move | Question |
|---|---|
| Setup | What Introduction promise or design claim is being tested? |
| Evidence | Which figure/table/number supports the claim? |
| Comparison | What baseline, condition, or ablation makes the evidence interpretable? |
| Interpretation | What should the reader conclude beyond the number? |
| Transition | Why does the next subsection logically follow? |

If a subsection only reports performance, label it `metric-dump` and rewrite from `result_narrative_templates.md`.

### 6. Decide Whether Another Rewrite Is Required

Require another rewrite when any of these are true:

- Abstract or Introduction lacks a clear motivation-gap-response chain.
- Results cannot be mapped to Introduction promises.
- Discussion lacks a direct answer to the paper's central question.
- Most changed sections have the same paragraph functions as the original.
- `revision_audit.md` reports high near-identical paragraphs in sections that were supposed to be rebuilt.
- The logic-transfer audit says "partially transferred" for Introduction, Results, or Discussion.

## Reporting Standard

Be specific and concrete. Prefer:

```text
Introduction P4 changed from a general limitation list to a three-part modelling gap that later maps to BiGRU, CDF loss, and PhyloP.
```

Avoid:

```text
The Introduction is improved and more logical.
```

The audit should make it possible for the user to challenge whether the rewrite really learned from the exemplar papers.
