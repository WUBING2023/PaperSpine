# Review Policy and Agent Autonomy

PaperSpine has two review policies. The policy changes process depth, not the
truth standard.

It also does not grant interaction authority. `balanced` and `strict` cannot
authorize the Agent to answer contribution, motivation, figure, target,
submission, or external-action questions for the user. Follow the current task's
saved choices and explicit delegated-choice authorization. Without delegation,
retain guided user choices. Historical typed interaction records are not an
additional permission prerequisite for the current host.

The default policy is editorially ambitious and procedurally light.
Independent review is read-only with respect to the manuscript: the reviewer
reports located, evidence-backed findings. For a task that already authorizes
writing or revision, the producing host implements supported scientific, citation
and layout corrections within that scope. External review methods' interactive
REPLACE/REMOVE approval steps do not create a new per-edit permission requirement
for this host. A review-only request still returns findings without editing.
Changing research scope, answering an undelegated user choice, or taking an
external action still requires the applicable user authorization; review findings
do not supply it. Preserve scientific truth and verify affected outputs after
repair. A longer audit trail is not evidence of a better paper.

For full-paper reference-guided writing, apply the distinct fresh-context review
in [reference-guided-writing.md](reference-guided-writing.md). Compare actual
reference moves, contribution hierarchy, complete non-defensive reporting and
structural independence. A writer's own check cannot close that review. An
anonymous comparison withholds the version key and desired outcome; preserve
original judgments and independently recheck affected revisions.

## Balanced (default)

Use for ordinary research writing, evidence-bounded rewrites, reports, early and
middle drafts, and most user-directed production work.

- Let the Agent choose the manuscript architecture, paragraph moves, emphasis,
  and revision order from the confirmed contribution and evidence.
- Require a compact section blueprint, primary-claim evidence links, one
  independent review of the current final manuscript and figures, a real PDF visual inspection, and usable final artifacts.
- Ground every actionable editorial comment in a precise manuscript location
  and short excerpt. This evidence rule does not require extra personas.
- Do not require a paragraph-by-paragraph rationale matrix, three reviewer
  personas, separate objection registers, or repeated receipts unless they help
  resolve an actual risk.
- CRITICAL scientific defects block. MAJOR findings block only when they affect
  a primary claim, figure/text identity, citation truth, or deliverable usability.
  MINOR/style findings are advisory.
- A gate may report `PASS_WITH_ADVISORIES`; this does not mean the advice must be
  converted into more forms before writing can continue.
- Judge manuscript completeness through one free-form editor synthesis, not a
  fixed scorecard. The synthesis must read the actual paper and may recommend
  any structure that fits the venue.
- Carry the user's unresolved quality requirements and their existing evidence
  into that review. Report whether each was assessed and met within the review's
  scope; a numerical or format pass cannot close an unassessed literature,
  contribution or exemplar-comparison request. Repair with the available material
  where possible, and keep a justified remaining limitation explicit.
- In that synthesis, compare the headline contribution with the actual controls,
  uncertainty and closest prior work; identify important results that the paper
  leaves invisible or repeats. Open the chosen external exemplars, final figures
  and their manuscript placement. Distinguish evidence-limited simplicity from
  lost or poorly expressed structure that can be repaired with existing material.
- Readability includes labels at their final physical size in each requested
  format. Keeping a caption with its image or passing pixel/DPI checks cannot
  compensate for unreadable figure text. Follow manuscript-format.md and the
  scientific figure workflow when repairing the affected layout.
- `tier` changes research/process breadth only. It must not shorten the promised
  manuscript, remove an earned ending, or turn Results/Discussion into notes.

## Strict

Use when the user explicitly requests strict audit, submission certification,
regulatory/compliance review, or a high-stakes final package. Strict mode adds
deeper evidence scrutiny and specialist review where the requested certification
needs it. Reuse the manuscript's existing rationale, sources and review notes
instead of duplicating them in compulsory forms.

Strict mode still must not reward bureaucracy. An artifact passes because it
captures a useful decision or verifiable fact, not because it is long.

Examine Methods, Contribution and Clarity distinctly; add literature, baseline,
fact-checking or other specialist perspectives for a concrete unresolved question,
not to fill a fixed role chain. Keep actionable findings tied to an exact current
manuscript location, source excerpt or justified absence check, real reviewer,
evidence, uncertainty, severity, disposition and concrete repair. Open-literature
novelty/positioning blockers also need retrieved external evidence; provider
failure and no-hit states cannot serve as proof. Current notes and public review
records can carry this information. Only an explicitly invoked historical Runner
requires its `evidence_review.json`, `evidence_review_check.md`, `review_plan.json`
or reviewer-receipt schemas; these are not current-host startup or writing gates.

## Always Hard

Both policies require truthful primary facts and references, valid citation and figure links, authorized data handling, and readable, portable requested outputs. Missing author or ethics facts limit the relevant claims or submission package; they do not prevent safe local drafting or delivery with those limitations made explicit.

Name the scope of each conclusion: a local format correction, a figure revision,
or a whole-paper editorial review. A prior format PASS remains a historical
finding for the files and properties it inspected; it does not close newly
observed scientific, visual or cross-format defects. User selection determines
the selected option, not an independent scientific-quality verdict.

Missing a preferred heading, exceeding a default section count, or departing
from an example outline is not automatically a hard failure. Ask whether the
reader-facing intellectual job is complete and whether the venue permits the
chosen form.

## Policy Resolution

Use `review_policy` from the current saved configuration; historical tasks may
carry it in `paper_spine_config.json`.
Missing/unknown values resolve to `balanced`. Do not ask an extra intake question
unless the user's requested outcome genuinely depends on strict certification.
