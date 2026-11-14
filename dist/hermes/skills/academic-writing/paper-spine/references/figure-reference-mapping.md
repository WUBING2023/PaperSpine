# Reference-Figure Mapping and Neutral Background

Use [scientific-figure-workflow.md](scientific-figure-workflow.md) for reference
selection and construction. Keep the mapping below in existing notes/sources;
Master attestations, frozen JSON and readiness flags apply only to the legacy
compatibility section.

## Map the Scientific Job Before Generation

After question/evidence planning, open the reference and caption, resolve its
actual figure label and compare its structure before fixing plot types. Record:

- source identity, venue/year, exact page/figure locator, retained viewable asset
  and access/use basis; distinguish a knowledge source from a design exemplar;
- the reference's panel roles, marks/encodings, hierarchy, reading order and useful
  annotations; use panel bounds when needed to identify a crop or mapped region;
- the current question, supported claim, boundary, manuscript/Results units,
  intended conclusion and hero panel;
- each current panel's evidence anchor, data fields, units, transforms, role,
  intended reading, semantic conversion and retained domain differences;
- the concrete structural features that will transfer, where they belong in the
  current drawing and which source content must not transfer.

Cover each current panel and identify each exemplar's structural contribution;
a bibliography entry or similar chart mark alone is not a mapping. Transfer
linked comparisons, uncertainty, scales or process layers where they serve the
question, retaining a simple design when it suffices.

Never present reference data, values, results, wording or patient information as
this study's own. Actually read, attributed literature may support conceptual
entities/relationships, distinct from observations and hypotheses. Preserve user
results and `materials_only`; learning does not authorize analysis or reruns.

If no suitable lawful reference can be viewed, record original design and the
specific limitation; continue without claiming reference-guided completion or
backfilling guidance. Reuse valid learning for minor edits and revise the affected
mapping openly when the question or evidence changes.

## Decide whether a panel substitution preserves its scientific job

Before locking the template, compare the reference and proposed panel's question,
measured quantity, biological/statistical unit, comparison and unique contribution
to adjacent panels. Use the existing mapping note; do not add a separate approval
form. A change of marks can be faithful, while keeping the same heatmap can lose
the argument. Recording the difference or adding a caption caveat does not by
itself make that substitution adequate.

Inspect the relevant evidence inventory before declaring a data limitation. A
small convenience table, previous selected-gene set or ready-made plot is not the
full inventory when broader results are supplied. Distinguish results already
available, calculations possible within the authorized scope but not yet done,
and evidence unavailable or outside scope. Inspect the relevant schemas/coverage;
use more data only for a scientific purpose, not to fill a longer reference panel.
Do not silently change a frozen comparison protocol or expand `materials_only`.
The restriction applies when that mode is in force; apply the user's current
authorization to the task at hand, separately from a planning-only review's limits.

When the source's job is central and further descriptive work is authorized,
assess the feasible calculation before defaulting to the convenient smaller
display. Not yet computed is not unavailable. Verify missing definitions or
inputs rather than assuming they exist. Bind proposed dimensions to actual IDs
and coverage: specimens assigned to conditions do not imply every specimen was
measured in every condition. Preserve relevant strata and pairing, or justify
their aggregation.

Make the drawing decision from that comparison:

- Preserve the scientific job with compatible evidence and a suitable encoding.
- If authorized computation is needed, perform and verify it before presenting
  the panel as a result. A proposed analysis is not an available result.
- Otherwise narrow the question, change the reference/affected region, or identify
  the exact missing evidence. Label the loss of explanatory scope; do not accept
  an inferior substitute merely because it occupies the reference's rectangle.

For example, a selected single gene does not represent a functional gene-set
score without evidence for that role; a mean matrix does not replace donor
heterogeneity; a second mean matrix does not replace upstream-regulator analysis.
By contrast, paired points instead of boxes can preserve a valid comparison.
Apply this reasoning across domains, not as a requirement to use these analyses.
Known gene names alone do not validate a module, pathway or mechanistic claim.

For each adjacent panel, ask what additional observation or inference it supplies.
Repeated rows across groups can be useful when they expose a defined interaction;
repeating a small selected set to fill space is not equivalent to a richer joint
structure. Do not add unsupported clustering, arbitrary gene sets, balanced red/
blue selections or decorative branches to imitate complexity. Close visual
reconstruction and sufficient scientific adaptation are separate judgments.

## Trace the Chosen Figure and Compare the Right Sources

Connect the selected export/source to actual transfers, panel evidence, caption
and manuscript use. Repair lost explanatory layers before cosmetic polishing.

Keep these comparison purposes distinct:

| Comparison | What it can establish |
| --- | --- |
| External published reference / current figure | Whether the viewed exemplar's relevant scientific structure and visual grammar were learned; label the external source and exact figure locator |
| Whole concept prototype / reconstructed final | Whether supported structure survived and prototype errors were corrected |
| Previous study figure / revised study figure | Whether the requested edit improved the figure without regressions |

Do not label this study's earlier figure "Reference / existing figure" or claim
it demonstrates published-reference learning. Reference sheets and prototypes
are learning aids, not selectable results.

Show complete sides simultaneously and legibly, adding attributed detail crops
when needed. A toggle or context-hiding crop does not suffice. Inspect the sheet
for clipped titles/labels and retain direct views for zoom. Check the selected
figure at actual manuscript size in each requested format.

## Background Rule

Prefer transparent editable canvases and pure-white publication backgrounds.
Another background can be justified by the user, venue or scientific encoding;
inspect actual contrast and publication-size readability. Avoid decorative tints,
gradients and textures. Semantic marks, heatmap cells, mechanism regions and
informative highlights may use color. A pixel/SVG probe can assist this inspection
but cannot establish scientific quality; do not claim a probe that was not run.

## Reuse of Point/Line Grammar

Point, line, interval, ROC, forest, heatmap, flow and network marks are neither
advanced nor primitive by themselves. Reuse a family when the questions and data
structure warrant it, retaining stable meanings and noting the reason when useful.
Do not manufacture variety by changing statistical semantics or repeat the same
result merely to create more figures.

## Recheck Affected Work

Recheck affected mapping/comparisons when source, reference, evidence, story,
panel map, candidate, selected asset, editable source, caption, Results link or
placement changes. Preserve unaffected checks/choices. Dependency changes matter
even with unchanged filenames; unrelated task/installation versions do not
invalidate the figure set.

## Legacy compatibility: explicit historical engine maintenance only

The old engine contracts below retain their own schemas and dependency checks.
Use them only for an explicitly maintained historical task; they do not create
current-host approval or file-work prerequisites.

- `paperspine5.figure-reference-plan/1.0`: before candidate generation, the Master
  owned the plan, authority attestation and self-hash, bound from
  `figure_requests.json` by relative path/SHA-256. It identified task, material
  snapshot/revision, `reference_guided` or explicit `original_no_reference`,
  source/image bytes and lawful-use locators, content/preview hashes, reference
  panel bboxes/grammar and the current scientific mapping described above.
  Workers consumed that frozen plan rather than authoring or backfilling it.
- `paperspine5.figure-reference-mapping/1.0`: after independent selection it
  bound the unchanged plan, exact current/candidate/winner/publication/editable
  assets, independent review, background probe and simultaneous comparison.
  The publication hash matched `figure_body_contract.json`. Its historical left
  side allowed a reference, original figure or explicit original-design sentinel;
  that compatibility allowance does not equate old/new comparison with external
  reference learning.
- Historical original design used an empty reference array and concrete rationale;
  missing fields did not imply it, and it could not pass reference-guided review.
  Probe records included version/render hash and every panel; data plots declared
  complete axes, while mechanisms could mark axes `not_applicable`.
- `FIGURE_MAPPING_READY` combined plan, mapping, probe, independent review, body
  binding, pixels and user comparison. Explicit engine hash invalidation remains
  local to those dependencies. This flag never authorizes submission or another
  external action and is not the current host's scientific acceptance rule.
