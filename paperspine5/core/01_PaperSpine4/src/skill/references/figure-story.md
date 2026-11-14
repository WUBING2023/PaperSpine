# Figure Story: Scientific Images as First-Class Evidence

Use this playbook for the paper's visual argument and existing/new figures.
Apply [scientific-figure-workflow.md](scientific-figure-workflow.md) for result
coverage, reference selection, construction and public choices. Keep the story
in existing notes and editable sources. The legacy appendix is not a prerequisite.

A figure is a compressed argument: the paper's contribution determines the figure
question, the figure informs the Results unit, and the actual rendered image can
falsify the intended prose. Preserve user results and the saved research mode,
including `materials_only`.

## 1. Understand the Existing Images Before Planning Prose

Render or open every existing figure at page scale and close scale with a
multimodal tool. For each complete figure and each panel, identify:

- the scientific question and the single dominant claim;
- the hero panel where the claim becomes visible;
- every panel's job (setup, mechanism, primary result, comparison, ablation,
  diagnostic, boundary, or interpretation);
- what is actually measured, inferred, or merely illustrated;
- visible methods, datasets, metrics, baselines, units, uncertainty, sample
  size, and statistical marks;
- the intended reading order and the conclusion a careful reader can earn;
- conflicts among the pixels, source data, caption, Results text, and planned
  contribution.

Do not infer the meaning of an image from its filename or caption alone. If an
existing figure contradicts prose or evidence, resolve the visible scientific
conflict in the source or claim. Ask the user only when a missing fact or decision
is needed; ordinary correctable drawing errors do not create a new approval.

## 2. Decide Which Visual Arguments the Paper Needs

Follow the workflow's whole-paper coverage plan before fixing chart types or
count. Compare strong references for the supported questions, then choose
`keep`, `redesign`, or `create` for each needed figure:

- **keep:** the image already carries the required claim and is publication-ready;
- **redesign:** the evidence is valid but hierarchy, panel logic, legibility, or
  visual grammar prevents the claim from reading clearly;
- **create:** a supported question needs a visual argument that does not yet exist.

A no-figure decision needs a reason tied to that visual job: redundancy, better
text/table communication or missing evidence. Use the workflow's distinction
between unavailable measured outcomes and literature-supported explanations.

Reference figures teach structure and visual grammar, never this study's facts.
Preserve real project evidence, terminology and valid existing visual encodings.

## 3. Plan the Figure Story and Reference Transfer

Before producing candidates, keep these decisions in the existing figure notes
or storyboard; no fixed JSON object or immutable approval step is required.

| Scope | Information needed to draw and interpret the figure |
| --- | --- |
| Whole figure | Keep/redesign/create; role; scientific question; dominant claim; intended conclusion; claim boundary; Results units; hero panel and reading order |
| Each panel | Panel identity; question and role; source/result anchor; actual data fields, units, transforms, sample size and uncertainty where applicable; intended reading |
| Reference transfer | Viewed source and figure locator; transferable panel structure, marks, hierarchy and annotations; mapping to current evidence; domain differences and prohibited transfers |
| Working assets | Current figure when present; editable source and dependencies; candidate/revision identity so the chosen image can be traced into the manuscript |

For example, a comparison panel uses the retained baseline, outcome and uncertainty
to support improvement or no clear difference; it does not establish mechanism or
external generalization. Link actual result sources, not invented ledger IDs.

Use [figure-reference-mapping.md](figure-reference-mapping.md) for panel/domain
mapping. Revise the brief when evidence, feedback or actual candidates reveal a
problem; preserve earlier revisions and do not backfill reference guidance.

One dominant claim may require several panels; separate unrelated claims when
their combination obscures the argument. Preserve the prototype's useful
explanatory layers while correcting its errors.
Write the strongest conclusion the visible evidence earns.

## 4. Let the Figure Structure the Results

Write each major Results unit as question -> visible evidence -> bounded answer.
Use the hero panel as the anchor, then bring in supporting panels for their
scientific jobs. Do not narrate panels chronologically (`A shows`, `B shows`,
`C shows`) when the scientific claim provides a stronger structure.

The storyboard is a starting point, not finished prose. Establish why the question
comes next, surface the decisive comparison or quantitative anchor, explain what
changes in the paper's argument, and bridge to the next question. Use this sequence
flexibly; do not force every result into the same paragraph template.

The introduction and discussion may not promise more than the figure and its
evidence support. The caption is the second explanation layer: identify panels,
entities, measurements, uncertainty/statistics and boundaries without trying to
repair an incoherent image. A literature framework supports interpretation; it
does not become a measured Results finding merely because it appears in the paper.

## 5. Produce and Select the Figure in the Current Workflow

For redesign/create, carry the viewed reference and story/domain mapping into
editable candidate sources. Alternatives communicate the same evidence. Apply
the panel-substitution decision in figure-reference-mapping.md and create the
provisional caption alongside the first render as specified in
scientific-figure-workflow.md. Keep that caption synchronized through revision;
the later manuscript pass reconciles it rather than creating it from scratch. Preserve
the useful whole-concept structure in a mechanism's final reconstruction; an
organ atlas remains an intermediate asset.

For `keep`, retain the current image/source without ceremonial A/B candidates.
For `redesign`, preserve exports, caption, result inputs and editable dependencies
as the baseline; keep the original selectable when a redesign does not improve it.
Follow saved choices/authorization. For independently selectable panels, retain
identities and apply each saved choice/comment before the whole-figure selection.
This sequence serves actual panel/assembly decisions; reuse valid selections
for ordinary corrections already authorized, without a new choice per typo,
spacing change or export. Do not label the host's correction a user confirmation.

Keep the candidate that makes the main conclusion clearest while retaining the
supported evidence density, panel jobs and boundary. A beautiful candidate that
changes topology, labels, data, panel meaning or statistical semantics fails.
User preference and independent scientific review serve different purposes.

## 6. Integrate the Selected Image and Re-read the Final Pages

For scatter figures, compare the full source scope with the values actually plotted and inspect each finite, unmasked offset after its collection offset transform against the axis bounds. Input-array counts alone do not show that every point is visible: fixed limits can omit negative or extreme observations. The existing layout probe can flag offset-center candidates; it does not approve scientific completeness, assess bars/lines, or replace native-size pixel inspection. Intentional zoom, excluded observations and custom clipping need explicit accounting in the caption or supporting figure. Running the probe executes a trusted producer with its normal exports and other side effects; use an isolated copied producer when preserving an immutable figure.

Connect the actual selected export and editable source to the caption, manuscript
label, Results units and story fields in section 3. Read current sources and
choices, not filenames or memory; preserve unaffected choices.

Every included figure needs a body reference (`\ref`, `\autoref` or `\cref` in
LaTeX, appropriate cross-references elsewhere) and interpretation. A copied asset,
caption or label alone is not integration. Use the named Results unit for measured
findings and the relevant Methods/Discussion passage for explanatory figures.

After final assembly, render and inspect the selected image against:

- dominant claim and intended conclusion;
- hero panel and every panel role;
- evidence anchors, data bindings, units and uncertainty;
- relation meanings, temporal order or state transitions where applicable;
- claim boundary, caption and corresponding manuscript passage;
- useful structure retained from the whole prototype and viewed exemplars.

Use the mapping reference's distinct external/current, prototype/final and old/new
comparisons. If pixels contradict the story, repair the image or manuscript and
recheck the affected work.

Read the assembled PDF in page order and each requested format's actual placement,
including Word or its faithful rendering. Check physical size, smallest labels,
resolution, caption and nearby interpretation. Reposition a detached float or
rework layout/caption placement when reduction makes a figure unreadable. File,
hash and schema checks do not replace inspection.

## Legacy compatibility: explicit historical Runner/PaperFigure maintenance only

Current sections 1-6 carry the scientific meaning of these old wrappers:

- `figure_policy` used `existing_only`, `generate_or_redesign` or text-only `none`.
  `figure_requests.json` held the section 3 story and panel fields; its
  `reference_plan` path/SHA-256 bound the Master-owned plan described in
  figure-reference-mapping.md.
- PaperFigure/FigMirror consumed that handoff. `current_figure` retained the keep/
  redesign baseline; `selected_candidate=existing` meant keep. Current public
  choices and actual source files carry these selections.
- `figure_body_contract.json` was the engine's only figure-to-body interface,
  binding selected publication/editable hashes, caption, label, Results units,
  claims and panel evidence. The final reference mapping bound plan, independent
  winner, background probe and comparison.
- `visual_audit_manifest.json` stored `story_claim_alignment`,
  `panel_role_alignment`, `claim_boundary_respected` and panel receipts.
  These remain scientific checks on actual files, not forms to unlock local work.

Only for a compatible, explicitly maintained legacy output tree:

```bash
python scripts/figure_story_check.py paper_rewriting_output --phase planning --markdown --write
python scripts/figure_story_check.py paper_rewriting_output --phase final --markdown --write
```

The final command followed visual inspection and checked bindings, real body
references, exact-white/transparent backgrounds and simultaneous previews.
Current backgrounds follow the mapping rule's justified exceptions. Legacy
`awaiting_paper_integration` ended at `is_complete=true` with five readiness
dimensions green, exposed by `workflow` or `GET /api/workflow`. These historical
statuses do not govern current completion or prove paper quality.
