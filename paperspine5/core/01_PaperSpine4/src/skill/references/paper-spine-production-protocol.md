# PaperSpine 17-step production protocol

This protocol is the operational spine for producing one paper. It turns the
scientific instructions in the other playbooks into a continuous handoff: each
step consumes the current task state and leaves a checkable result for the next
step. It is a quality protocol, not a second business authority and not a
fixed J-number or persona chain.

## How the host uses it

Read this protocol at the start of whole-paper production or whole-task
recovery. For a focused edit, review or explanation, use only the applicable
steps and original methods; reuse saved configuration and unaffected work.
Resuming a local correction does not require repeating all seventeen steps.
For each applicable step, record the factual result in the task's existing working notes
or artifact inventory. Do not create a form merely to satisfy this list. A
single note may cover several adjacent steps when it contains the same evidence.
The host may run independent retrieval, analysis, rendering and review work in
parallel, but it must not claim a later step is done when its required input is
missing. The current task, material root and semantic manuscript remain the
only writable authorities.

Before moving to the next substantive segment or stage, **verify that the previous
result is in the same task's workbench**. Publish its real user-visible outputs,
record a factual milestone using an existing stage, and read back the same task,
version, summary, files and pending choices. Reuse a matching checkpoint; repair
an actual mismatch before claiming progression. Local files and artifact stage
labels alone do not move Web progress. Several steps below can share one stage.
This is a host continuation instruction, not seventeen new backend approvals.
See [product-v1-workflow.md](product-v1-workflow.md) for actual calls.

## Inspect, use and repair; do not fill a checklist

Apply only the steps needed for the saved workflow. A focused review/audit
returns findings; it does not trigger a new research run, rewrite or all 17
handoffs. On resume reuse saved configuration, choices and unaffected work.
These are host work instructions, not new backend states or per-step gates.

Separate what was proposed, what was produced, and what was actually checked.
An existing file is a candidate, not proof of reading or scientific quality.
A hash identifies bytes; it cannot prove that someone viewed a page, that a
citation supports a claim, or that the current manuscript used a learned method.
Check the result **and its downstream use** at the locations described below.
Report the scope of the check, not a blanket completed/verified/accepted label.

Use deterministic tools for observable defects (missing links, inconsistent
numbers, actual page geometry), the host's source-aware reading for meaning,
and an independent reader for the requested scientific/editorial review.
Keep these three scopes separate. A tool's pass, a changed note or a writer's
self-check cannot stand in for independent review. If an independent reader is
unavailable, deliver the safely improved draft with that review still pending.

When a defect is found, make the **next action a concrete source repair**, not
"continue step N". In existing notes or the review response state: current
file/revision and page/panel/paragraph; observed defect versus the evidence or
target requirement; smallest source/tool action; and the affected output to
reinspect. Use current hashes when available or needed to distinguish versions,
but do not introduce a receipt chain. Example: a page has a large unintended
void below a float; inspect that page and its neighbor, repair the float or
page break in the source, rebuild the PDF and requested Word proof, then read
those affected pages for continuity. Do not edit the check record to erase it.

After repair compare the same defect location and its downstream use. Progress
means the defect is reduced or resolved without losing supported science,
readability or cross-output consistency. Rewritten notes, timestamps, hashes,
more citations/panels or repeated identical renders are not quality gains.
If two targeted attempts leave the same defect unchanged, stop that tactic:
re-read the specific evidence/reference, use a different layout/drawing method,
or narrow the correction. A new hash alone does not reset this rule. Continue
unaffected work; report a blocker only for a real unavailable capability,
indispensable fact or authorization. Do not invent missing science, add filler,
or shrink fonts just to improve a metric. Stop repairing when the requested
issue is resolved, not after an arbitrary minimum number of loops.

## The seventeen steps

### 1. Identify the paper task

Resolve the user's topic, requested output, language, target and named input.
Use one task ID and give it a useful title and one-sentence description. Verify
that the task title, task ID and material summary shown in Web are the same
ones used by the host. A stale tab, latest-task shortcut or shell directory is
not an identity decision.

Check and use: compare the actual task snapshot and Web title/ID with the
user-named paper; use that binding for the next action. If they differ, restore
the correct existing task, not a replacement task or a renamed wrong paper.

### 2. Bind materials and workspace

Resolve the user-named material root before substantive analysis. Inventory
original files, existing drafts, figures, references, scripts, permissions and
known limitations. Generated work belongs below the task's returned workspace;
authorized source roots may be elsewhere. Preserve originals and separate raw,
derived and shareable material. Select the actual files with `grants[].include_paths`
instead of recursively treating caches/logs/generated outputs as research inputs.
Read successful inventory entries and each scan warning. One unreadable file must
not cancel saved scope or unrelated work; only conclusions needing that file wait.
Retry the concrete file problem, never pretend it was read, and use `replace: true`
when the user intentionally changes roots so the old failing root is not retained.

Check and use: open representative supplied results and locate the inputs
used by each main claim/figure; reuse one material/result inventory. Repair an
incorrect root or omitted result before depending on it; preserve originals.

### 3. Save configuration and establish the research scope

Open the exact task Web path and prefill only what the user's first message
supports: article/genre, target, language, workflow, research mode, reading
depth and delivery formats. Treat these as proposals until the Web save has
`source=web_user`, `user_confirmed=true` and `readiness.ready=true`. Public
literature reading is a normal capability; there is no separate public-paper
permission toggle. Private material remains local unless the user explicitly
authorizes sharing.

Use the saved mode literally. `materials_only` does not add analyses; it may
read literature, extract supplied results, plot supplied results and check
consistency. `required` performs justified research/analysis. `agent_decide`
chooses the justified work from the evidence and performs it. Separate
research depth from analysis permission. Default learning is 3 same-direction
plus 3 target-venue papers; a deeper request uses 6+6; an explicit count wins.

Check and use: read back the same task's saved configuration and material
choice, then check the next analysis/writing action against that scope. A
prefill is not a save. Reuse valid saved values on resume; never invent a click.

### 4. Read and apply the Skill methods

Use the current method-routing catalog to select the applicable intake,
research, contribution, evidence, figure, writing, format, review and delivery
methods. Read the full selected resources on first use, including scientific
detail in tables and examples. Keep a short record of the resources actually
read and the action they changed. A route name, method list or summary does not
prove application.

Check and use: name the specific method decision that changes the next
source edit, analysis or review. A method list is not evidence of application.
If the action ignores the method, read the relevant passage and fix the action,
not the reading log. After context loss a prior read marker does not replace those
passages. Use the local source if the helper is unavailable.

### 5. Learn the target scene, literature and format

Research the current official target instructions and the requested article
type. Save the applicable target-venue papers as local PDFs whenever possible,
open them, and inspect writing, figures and page design. Use distinct same-
direction and target-venue sets; a list of titles, abstract-only notes or
screenshots is not figure/layout learning. The bibliography count must satisfy
the user's configured count and, by default, be above the observed mean of
the target exemplars unless the user specifies otherwise. Apply the official
article-type cap first and explain any conflict; never pad unrelated citations.

Find the official template or official sample and record the source, date,
version/year, article type, package files and build instructions. Read its
README, sample, class/style options and bibliography workflow. Compile an
untouched demo, then apply it to a representative page and to the manuscript.
An official package downloaded but not applied is not template use. If no
applicable package can be found, record the focused search and use a justified
fallback without claiming official compliance.

Check and use: actually view the local exemplar pages/figures, then compare
the current outline, citations and representative rendered pages against them.
Check the applied template/class, not just a downloaded package or note. Repair
the specific unsupported claim or layout difference; disclose inaccessible
sources without claiming full-text/figure reading or blocking unrelated work.

### 6. Inventory evidence and usable results

Read all supplied results, tables, figures, methods and relevant analyses,
including material outside an earlier draft. Separate measured results,
literature-supported explanations, proposed analyses and unavailable evidence.
Preserve numbers, units, denominators, controls, uncertainty and limitations.
Run only analyses permitted by the saved research mode and retain reusable
code, derived data and result tables when new analysis is authorized.

Check and use: trace primary numbers, units, denominators and uncertainty
from the actual result assets into the proposed claims and figure inputs. A
ledger alone is insufficient. Resolve specific contradictions at their source;
missing raw arrays do not invalidate legitimate supplied results.

### 7. Establish contribution and motivation

Form the smallest useful set of evidence-backed contribution options. Let the
user choose when the direction is not explicitly delegated; in an explicitly
delegated automatic run, record the delegation and rationale. Connect the
unresolved problem, the design response, the evidence that tests it and the
claim boundary. Keep external findings attributed to their sources.

Check and use: compare the saved choice or explicit delegation with the
outline's main claim and its evidence boundary. If they diverge, repair the
outline/claim or obtain the genuinely missing choice, not a new approval for
an already delegated decision.

### 8. Complete the analysis needed by the question

Perform justified statistical, computational or conceptual work within the
saved scope. Prefer a complete, reproducible result set over a quick summary
plot. Add robustness, uncertainty, controls, ablations, subgroup or sensitivity
views when the data and question support them. If the supplied results are all
that may be used, faithfully expose their useful structure and state what is
not testable. Never manufacture a stronger result to make a figure or claim
look more advanced.

Check and use: inspect result tables and authorized analysis output, then
trace the comparison and uncertainty into Results and figures. Reuse supplied
results in materials_only; repair a concrete inconsistency without inventing
analyses, controls or stronger conclusions.

### 9. Plan the paper's evidence and figure story

Before drawing, map the full result inventory to the paper's questions. Decide
the jobs of the main figures, mechanism/conceptual figure, tables and
supplement. If the available evidence supports multiple complementary visual
arguments, do not compress them into one convenient chart. Merge redundancy,
but retain informative comparisons, negative findings, distributions,
uncertainty and validation. There is no arbitrary panel quota; the article
type, evidence and venue determine the final count.

Check and use: map available results to actual panel jobs, captions and
manuscript positions. Identify missing useful evidence and redundant panels by
comparing the plan with the result inventory; repair that gap, not a panel
quota. Reuse this map in drawing and drafting rather than a second form.

### 10. Deconstruct strong reference figures

For each important figure job, actually open a structurally matched reference
figure. Inspect the complete composition before looking at individual
components: information layers, visual hierarchy, panel grammar, alignment,
color, typography, annotations, uncertainty display, mechanism arrows and
caption relationship. Record what is transferred as a design principle and
what cannot transfer because the present data or domain differs.

Reference learning and old/new regression comparison are separate. Keep
published references, prior local figures and current candidates in distinct
folders and labels. Never transfer source numbers, patient details or
conclusions.

Check and use: view the cited reference page/figure and compare its
scientific job with the current figure. Identify a specific transferable
structure and its limits. If the match is superficial, choose a better matched
reference or revise the composition; extra reference filenames do not fix it.

### 11. Build complete figure candidates

Generate the whole figure composition first when the figure is a mechanism,
conceptual framework, workflow, method architecture or multi-panel result.
Only after the whole composition has a coherent hierarchy may the host generate
or redraw difficult internal components separately. The component must be
placed back into the whole figure and checked for consistent scale, baseline,
line weight, palette and semantics. Do not replace an evidence-rich figure by
a generic flowchart merely because it is easy to draw.

For data figures, use the strongest chart form supported by the result: show
the underlying structure, comparison and uncertainty rather than decorating a
simple chart. For mechanisms, ground arrows and labels in the study or
identified literature and distinguish association from causation. Keep editable
vector/source assets, data inputs and figure notes.

Check and use: inspect each complete candidate at final placed size, open
its editable source and compare labels/arrows/data with the evidence and
caption. Repair collisions or unsupported relations in the producing source,
then inspect the assembled figure, not just an attractive isolated component.

### 12. Present and consume user choices

In guided work, publish real candidate files under the task's discovered
figure roots and open the same task Web choice surface. Show the complete
figure and each selectable subfigure with clear labels. Wait for the actual
saved selection and comments. Never turn an Agent proposal into “user
confirmed”, and never use a previous task's choice. In automatic work, use only
the saved delegated-choice authority. Read back every selected panel before
assembly.

Check and use: read the same task's saved file/panel choices and comments,
then compare them with the assets actually assembled. A request to modify is
not adoption. Repair a wrong assembly while preserving valid choices; never
label host-selected candidates as user-confirmed clicks.

### 13. Draft one semantic manuscript

Apply [reference-guided-writing.md](reference-guided-writing.md) for full-paper
drafting/reconstruction: own evidence-led outline, complementary exemplar roles,
direct supported prose and fresh-context writing with the complete evidence
packet when available. Do not reduce the saved literature-learning set or
manufacture sentence correspondences. Local edits use only applicable parts.

Write the complete article from the confirmed contribution, evidence ledger,
result/figure plan and learned target style. The paper must have a readable
argument, complete Methods, Results and Discussion, limitations, captions,
tables and relevant supplements. Do not expose planning labels, task states,
review logistics, status notes or internal workflow narration in the manuscript.

Keep assistant workflow chatter and internal production provenance out of
reader-facing scientific prose. Preserve genuine study methods, software/model
identities, citations, ethics statements and factual disclosures required by
the applicable venue or explicitly requested by the user. Do not invent an AI
notice or delete a truthful required disclosure to make the paper look clean;
keep detailed execution logs in the private work package.

Check and use: read the current article end to end and trace primary
claims, numbers, selected objects, captions and bibliography into that semantic
source. Repair argument gaps or unsupported language there; a complete section
list or several exported formats does not prove a complete paper.

### 14. Resolve citations and object references

Apply the target citation style at the semantic source. Every cited key must
exist, be used in the intended context and resolve to the correct bibliography
entry. Every figure, table and equation needs a stable ID, caption and body
cross-reference. Use native citation/cross-reference fields or commands so
links survive reordering and DOCX editing. Check DOI links separately. Do not
repair one exported PDF by typing numbers or running a whole-document regex.

Check and use: resolve cited keys and object IDs in the actual source and
follow their intended targets in outputs; verify citation context against the
source publication. Repair the wrong key/destination/claim, regenerate and
recheck; a reference count or a working DOI alone is not enough.

### 15. Build submission and reading surfaces from the same source

Use the verified official venue template when available. Keep an explicit
submission-oriented surface and a clean reading surface only when their
purposes differ. Both must contain identical scientific text, numbers,
citations, captions and selected figures; differences in columns, line numbers
or float placement must be documented venue/layout differences. Generate DOCX
and its faithful rendered proof when requested; do not call a separately built
TeX PDF a Word rendering.

Record actual engine, template, class/style, CSL, fonts, filters and build
command. Rebuild after every substantive source, figure, citation or layout
change. Never leave a stale PDF beside a newer TeX or Word source.

Check and use: compare current scientific text, numbers, citations,
captions and selected figures in the source, PDF and requested DOCX/proof.
Hashes/mtimes identify files but cannot establish semantic parity. Regenerate
stale outputs from the canonical source and inspect them; do not patch an
export alone or call a TeX PDF a Word rendering.

### 16. Inspect, independently review and repair

Render every PDF page and every complete figure at final placed size. Check
reading order, page density, blank or nearly blank pages/columns, large voids,
stranded headings, float gaps, caption placement, clipping, missing glyphs,
font size, citations, references and final-page rhythm. Inspect the actual DOCX
or a faithful Word rendering as a separate surface. Check browser links and
downloaded files when the task reaches delivery.

Give the current source, current renders, current figures and local target PDFs
to an independent reviewer with a specific request covering science,
argument, literature learning, figure design, format and delivery. The writer's
own check is not independent. For every finding, fix the producing source or
method, regenerate affected formats and re-review the affected pages and
figures. Reuse valid checks for unchanged bytes, but never inherit approval
from an older revision.

Check and use: open every current rendered page and final-size figure;
use direct page diagnostics to locate likely gaps, not to replace reading.
Bind findings to the actual revision and exact location. Repair the source,
regenerate affected surfaces and obtain affected-scope re-review; unchanged
work may retain its checks. A blank report is not evidence of independence.

### 17. Package, deliver and support same-task revision

Create the complete local work package and the requested shareable package.
Include the current sources, bibliography, used template assets, editable
figures, permitted scripts/data and build instructions. Exclude private raw
material by default. Build the package copy, extract it into a new temporary
directory and rebuild there when portability is claimed; fix absolute paths or
missing dependencies at the source.

Open the same task's preview and exercise the actual browser download. Confirm
that downloaded bytes belong to the reviewed revision and that the package
contains the files promised by the UI. On later feedback, preserve the prior
revision, read the new feedback, change affected work, regenerate and repeat
steps 14–17 in the same task. A user request to update a paper does not create
a new task or erase valid prior work.

Check and use: extract the actual downloaded package, compare its promised
members with the reviewed revision and open those files. Test a clean rebuild
only when claiming portability. Fix stale/missing members at the packaging
source; save same-task continuation/feedback without relabeling an unreviewed
or not-yet-downloaded draft as delivered.

## Quality time budget and stopping rule

PaperSpine should spend time where quality is gained. After the first complete
draft, reserve work for at least one evidence/argument pass, one figure/layout
pass and one independent review/repair pass whenever the inputs support them.
Use additional passes when a review finds a primary-claim, figure, citation,
format or cross-output defect. Continue until the current requested quality is
met; do not stop because a first PDF compiled or because a nominal round count
was reached.

Parallelize genuinely independent work when authorized. Use the defect-based
repair rule above, not another supervisor service or fixed round counter.
A repaired dependency or new user choice can justify retrying a formerly
blocked action; a changed hash or note without an improved result cannot. If model quota or another external
provider interrupts work, persist the same task's continuation state and resume
the unfinished step; do not create a replacement task or call a partial draft
complete.

The final status must separately state: scientific quality (including actual
independent-review scope), editorial/visual quality, technical portability,
local delivery and submission readiness. State what was and was not checked;
none is guaranteed by the existence of this protocol. External submission or
publication requires separate authorization.
