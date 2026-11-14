# Paper production methods by current action

This is a navigation overview of the existing scientific methods. For a whole
paper, use the applicable sections as the work develops. For a focused change,
use the section that changes the next useful action; retain the shared boundaries
and quality rules in SKILL.md. Read the applicable original method files fully
on first use, not every unrelated section or resource. This overview does not
replace those methods, authorize analyses or reset a task.

## Scientific work and expected results

For a research topic without existing results, or a request for new experiments,
start with [research.md](research.md) and [research-full-cycle.md](research-full-cycle.md).
That route supplies question/prior-work checking, design, fair baselines, actual
execution and analysis before rejoining the writing/figure methods below. It does
not require new research for materials-only writing, rewrite, review or local edits.
Use [agent-orchestration.md](agent-orchestration.md) only for available, authorized
delegation or runtime handoff; a single host can follow the same scientific path.

Use [current-method-routing.md](current-method-routing.md) to select applicable original methods. Read their full text on first use; routing is not application or quality proof. If the helper is unavailable, read the local originals and continue the same task.

### 1. Anchor, intake and inventory

Read [intake.md](intake.md), [intent-configuration.md](intent-configuration.md) and [resume.md](resume.md) as applicable. Preserve originals. Inventory results, draft, figures, references, scripts, provenance, permissions and limits; identify only necessary missing decisions. Do not create placeholders.

Select actual research files deliberately: pass exact root-relative files in
`grants[].include_paths` to `paperspine_authorize_materials`. A project folder may
contain locked logs, caches and generated drafts; do not treat all of them as
scientific inputs. Keep generated outputs in the task workspace. Read the returned
inventory and `scan_issues`, then actually open the files needed for each claim.
A listed filename or successful registration does not prove reading. Individual
`materials.read_failed` warnings do not cancel saved configuration or the entire
paper: use readable inputs and continue unaffected research/writing. State which
file failed and why, retry only that concrete problem, and pause only claims that
need indispensable unavailable evidence. Never invent its contents. When the user
replaces the material folder, use `replace: true`; otherwise retain the same roots
and explicit selection. See the material call example in the workflow reference.

### 2. Research, target learning and citations

Read [research.md](research.md), [local-reference-ingestion.md](local-reference-ingestion.md), [citation.md](citation.md), [journal-learning.md](journal-learning.md), [target-journal-research.md](target-journal-research.md) and the applicable venue playbook. Read public literature unless explicitly limited. Use the saved learning-set sizes; inspect actual target-venue PDFs, current official instructions and any applicable official template. Abstracts can support bounded claims but cannot prove full-text, figure or page-design learning. Verify citation identity and use; build useful references without padding.

Resolve target identity before claiming target-format learning. An Agent-selected comparator is not the saved target. If unknown, save a delegated choice, ask once, or keep the draft venue-neutral. Format learning counts only when the source uses a verified template/style or stated fallback and representative pages match actual exemplars.

Apply the saved analysis scope to actual tool work:

- `required`: carry out justified research or analysis on authorized materials.
  Preserve reusable code, derived data, Methods, Results and uncertainty. A
  literature dossier or analysis plan alone does not complete research.
  For topic-first work, follow research-full-cycle.md to obtain real inputs and
  perform a bounded design; absence of supplied results is the study's starting
  point, not permission to invent an outcome or switch to inventory-only work.
- `agent_decide`: assess what evidence the scientific question needs and what
  the inputs support, state the rationale briefly, and perform the justified
  work. This mode does not silently mean `materials_only`.
- `materials_only`: use the supplied analyses, tables, images and reported
  results without new EDA, tests, modelling, experiments or reruns. Literature
  study, faithful extraction, plotting supplied results and consistency checks
  remain available. Missing raw arrays alone do not invalidate user results.

Learning depth (3+3/6+6) does not authorize analysis. Pursue the strongest
supported question within scope; missing endpoint facts do not require an
inventory-only paper. Never invent facts, change accepted direction silently,
or analyze outside the selected mode.

### 3. Contribution, motivation and evidence contract

Read [contribution.md](contribution.md), [semantic-confirmation.md](semantic-confirmation.md), [scientific-evidence-ledger.md](scientific-evidence-ledger.md), and [results-validation.md](results-validation.md) for evidence-bearing work. Form a small set of evidence-backed options; have the user choose when choice matters. Use the accepted contribution, motivation, claim boundaries, terminology and uncertainty to guide drafting. Refine the argument as actual findings develop; request another choice only for a substantive change to the user-selected direction.

### 4. Outline, writing and figures

For `build_from_materials`, read [build.md](build.md); for rewriting, read [rewrite.md](rewrite.md). Apply [editorial-completeness.md](editorial-completeness.md) and [assertive-scientific-writing.md](assertive-scientific-writing.md). Write a complete evidence-bound argument, not a summary or template shell.

For full-paper drafting or reference-guided reconstruction, apply
[reference-guided-writing.md](reference-guided-writing.md). Build the study's
own contribution hierarchy and outline, then use complementary real references
from the saved learning pool. Keep actual sentence/move anchors in existing
notes; use fresh writing and distinct fresh review with complete evidence when
available. Local edits do not require whole-paper reconstruction.

Before figures, read [scientific-figure-workflow.md](scientific-figure-workflow.md), [figure-story.md](figure-story.md) and [figure-reference-mapping.md](figure-reference-mapping.md). Map actual results to questions and assign each useful job—cohort, primary finding, comparison, uncertainty/validation, robustness/subgroup and explanation—to a figure, table, prose, supplement or justified omission. No quota: merge duplicates, but do not let the current folder or one omnibus plot define the story. View matched references before design. Before locking panel geometry, apply the panel-substitution decision in figure-reference-mapping.md: documenting a changed statistic is not evidence that the reference's scientific job survived. Start a provisional caption with the first candidate using scientific-figure-workflow.md; keep explanatory headings in that caption rather than defaulting to a title/subtitle above every panel.

For existing-figure feedback, use [figure-revision-decisions.md](figure-revision-decisions.md) to recover the accepted baseline, distinguish text/geometry/evidence problems, and check the actual placed size before choosing the repair. A local correction does not restart reference retrieval or whole-paper production.

For a new or substantially redesigned figure needing a stronger contribution or linked evidence, use [figure-argument-retrieval.md](figure-argument-retrieval.md) to find and verify the relevant published comparison at panel level before choosing its visual structure. Reuse valid mappings for local corrections.

For `mechanism_figure: auto` or `prefer`, make an explicit decision. If explanation is central and sourced, create a complete mechanism/conceptual/architecture candidate in addition to necessary data figures, distinguishing observations, established knowledge and hypotheses. Under `auto`, omit only for a concrete reason. A flowchart, ROC panel or statistical summary is not a mechanism figure.

Expose current, reference and candidate files for each selectable figure and read every saved choice/comment before assembly. Preserve data truth, editable sources, panel identity, caption/body alignment, units, claim boundaries and prior figure bytes; keep references/comparisons separate from final candidates.

### 5. Render, assemble and inspect

Read [latex.md](latex.md), [manuscript-format.md](manuscript-format.md), [visual-readiness-gate.md](visual-readiness-gate.md), and [publication-surface.md](publication-surface.md). Produce the requested editable source, a submission-oriented file when the venue defines one, a clean reading PDF, and DOCX unless the user explicitly opts out. Submission and reading surfaces must share one semantic source, numbers, citations, captions and selected figures; layout may differ only for a documented venue purpose. Inspect every PDF page and the actual DOCX/faithful Word rendering. Check title, headings, citations/links, figures, captions, references, units, clipping, page breaks, fonts, declarations, page occupancy and reader flow. Any blank or nearly blank page/column, avoidable large void, stranded heading, excessive float gap, orphaned caption, or late source/Word/PDF mismatch is a failure requiring source-level repair. Visible TeX, inert literal citations, missing images and unreadable pages are failures.

### 6. Independent review and repair

Read [review-policy.md](review-policy.md), [audit.md](audit.md), [reviewer-audit.md](reviewer-audit.md), [evidence-grounded-review.md](evidence-grounded-review.md) and [publication-surface.md](publication-surface.md) as applicable. An independent-context reviewer must inspect the actual current manuscript, figures and renders. `balanced` means compact editorial review; `strict` adds requested depth/specialists. Never substitute the writer's self-check or fabricate a reviewer, objection, score or PASS. If unavailable, disclose pending independent review and continue safe local repair.

Trace headline claims to sources, controls and uncertainty; compare final figures and evidence coverage with venue exemplars. Independently check three demonstrated failure points: whether the saved target was actually applied to source and rendered pages, whether distinct result families received an appropriate visual/table/text role, and whether an `auto`/`prefer` explanatory figure was completed or honestly omitted for a stated reason. Separate scientific, editorial, technical and submission findings: a format check or figure choice cannot approve the whole paper. Repair the producing source/method, regenerate affected outputs and re-review, rather than editing receipts.

For reference-guided writing, also check real anchor-to-prose correspondence,
contribution hierarchy, non-defensive but complete reporting, complementary
reference use and structural independence through reference-guided-writing.md.
Anonymous comparisons keep document identity and desired outcomes from the
reviewer; preserve raw findings and disclose unavoidable identification cues.

### 7. Delivery and same-task revision

Read [submission.md](submission.md), [publication-cycle.md](publication-cycle.md), [publication-cycle-interface.md](publication-cycle-interface.md), and [submission-metadata.md](submission-metadata.md) only when the requested delivery/venue operation needs them. Use [open-release.md](open-release.md) only for explicit release work. Publish the real files, keep shareable and local-workspace packages separate, exclude private raw materials by default, and verify the actual browser download when claiming it. On feedback, reread the saved feedback and affected artifacts, preserve the previous revision, change only affected work, regenerate and re-review in this same task.
