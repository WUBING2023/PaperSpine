---
name: paper-spine
description: Develop a research topic or supplied results into evidence-bound papers, with scoped real research, scientific figures, independent review and same-task revision.
# Suite Update Authority; Blocks unsupported readiness claims.
---

# PaperSpine Orchestrator

Choose the current request before starting tools or loading detailed methods.
For whole-paper production or whole-task recovery, read
[paper-spine-production-protocol.md](references/paper-spine-production-protocol.md).
For an explicitly authorized local research-agent prototype, apply that protocol's
scientific quality/delivery requirements with the full-cycle and orchestration
routes below and its actual confirmed run brief/files. Launcher/public-schema
steps apply only when those services are used; never fabricate their execution.
For a focused edit, review or explanation, use the relevant route below and only
the applicable protocol steps; do not restart whole-paper production.

The current host Agent performs research, citation checking, interpretation,
writing, figures and revision, and arranges independent review. Web, local files
and small scripts support interaction, persistence, rendering and delivery.

When configuration is missing in ordinary guided paper production, launch the intake UI automatically before inspecting
materials; do not hand-write configuration or silently choose a paper root.
For a visible launcher action, use `require_escalated` as required by the host.
After the update preflight below, launch is the first guided-production action when configuration is missing.
For an explicitly authorized local research-agent prototype, use its actual confirmed run
brief and workspace as described in [agent-orchestration.md](references/agent-orchestration.md);
never fabricate Web configuration, clicks or workbench synchronization.

**Product outcome:** an evidence-bound, coherent paper with informative figures,
applicable venue format and editable sources. Learn from strong same-field and
venue papers. Let users configure, choose contribution/figures, preview,
download and revise the same task.

Tool success, hashes and task status do not establish scientific, editorial,
visual or submission readiness; assess the actual paper.

## Select the current action

| Current request | First applicable methods | Requested outcome |
| --- | --- | --- |
| Start from a research topic or perform new research | [research scope](references/research.md), [full research cycle](references/research-full-cycle.md) | A feasible question, real evidence and a paper within the confirmed research scope |
| Build a paper or substantially rewrite it | [production methods](references/paper-production-methods.md), [build](references/build.md) or [rewrite](references/rewrite.md) | Complete paper work within saved scope |
| Correct an existing figure, label or caption | [figure revision](references/figure-revision-decisions.md), relevant passages of [figure workflow](references/scientific-figure-workflow.md) | A repaired source and affected figure/caption; valid data, layout and choices retained |
| Revise prose or respond to manuscript feedback | [rewrite](references/rewrite.md), applicable writing/review sections in [production methods](references/paper-production-methods.md) | Same-task changes addressing actual feedback |
| Review or audit supplied files | [review policy](references/review-policy.md), [audit](references/audit.md) | Findings on the current files; editing only when requested |
| Translate or transfer an existing paper | [translation](references/translate.md) or [journal transfer](references/journal-transfer.md) | Requested language or venue adaptation, preserving valid science |
| Explain, inspect or maintain the Skill | The named local files and relevant methods | The requested explanation, audit or patch; paper launch/configuration do not apply |

Read only the methods relevant to the chosen action, fully when first applicable.
For full-paper drafting or reference-guided reconstruction, apply
[reference-guided writing](references/reference-guided-writing.md): an independent
study argument, complementary exemplar moves, direct evidence-matched prose,
and fresh-context writing/review when available. It is part of this Skill.
A shared workflow label does not turn a label correction into new research.
Recover saved task/configuration/choices on resume with [resume](references/resume.md).
For a material-read failure, use the intake section of the production methods:
identify the concrete file, continue supported work and isolate dependent claims.
For topic-first work, a missing existing dataset or manuscript is not a failed
material read: identify the proposed public sources or collection needs, and
confirm the new study workspace and research scope without inventing inputs.
Use [Agent orchestration](references/agent-orchestration.md) when authorized
delegation or the research-agent runtime is available; the same scientific
methods and real files apply when the host works alone.

## Authority and boundaries

1. The host Agent owns scholarly judgment and the current paper files.
2. The user's materials/results are authoritative for claims about this study.
   Never invent data, metrics, p-values, citations, figures, methods, authors,
   ethics, funding, permissions or review conclusions.
3. Use one task ID, one material/workspace binding and one continuous revision
   history. Never create a second task because a launcher, profile or transport
   failed. Never silently switch to another directory, profile, task or paper.
4. Web is the supported path for configuration, user choices, previews, downloads
   and feedback. It supports the configuration and choice boundaries below; existing confirmed
   scope permits independent local corrections during a Web outage.
5. Task status never authorizes uploads, publication, submission, payment,
   licensing, telemetry or external contact; obtain explicit authorization.
6. Private materials stay local unless explicitly authorized for sharing. Apply
   the saved research mode as described below; public literature reading is normal.

## Update once on invocation, then continue the paper

Before starting or resuming paper production through an installed Skill, run its
`scripts/paperspine_update.py --preflight --yes` with its verified Python.
This checks the official channel on every invocation: if current, continue;
if newer, transactionally update the Skill, Web/runtime and updater together.
Honor an explicit auto-update opt-out. An offline check may continue with the
existing installation and a clear notice; a failed install must retain the old
installation and report the actual error. Never repeatedly reinstall to repair
paper state. After a successful update, reread this installed SKILL and the
current public tool schemas, preserving the same task, profile and user files.
See [product-v1-workflow.md](references/product-v1-workflow.md) for entry details.

## Start, configure and continue the current paper

A read-only explanation, audit or plan ends with the requested result. Launch
and configuration below apply to paper production, not Skill inspection or plans.

Read [product-v1-workflow.md](references/product-v1-workflow.md) for the actual
public tool shapes and [intent-configuration.md](references/intent-configuration.md)
for first-message prefilling in guided Web work. An explicitly authorized local
research-agent prototype follows its actual confirmed brief and runtime schema instead;
do not launch or invent a Web service/profile for that run. The current Agent is
the scientific host; launching Web does not launch another writer. For guided
Web production, follow this sequence:

1. Resolve the user's named material folder. “This/current folder” explicitly
   selects the conversation working directory. Without such an instruction, do
   not assume an unrelated shell directory is the paper. Initially list names
   and identify candidate inputs; defer substantive analysis until configuration
   and the material choice are saved. Preserve original materials.
   A topic-only request may have no existing materials. Confirm the generated
   workspace and proposed source/collection scope through the same intake;
   do not require a fabricated material folder or another workflow/task identity.
2. Start the installed launcher with `launch --no-open`; it returns a service URL,
   not a paper or running AI. Open only the bound task URL once. In Codex prefer
   its available in-app browser unless the user chose another; never also open
   the external browser. Reuse that tab and the same profile for later choices.
3. Read public schemas with `host tools`. Resume the explicitly linked task only
   after checking its material roots against this paper. A remembered profile is
   a shared server preference, not the current paper ID. A recent/open browser
   tab is not task-selection authority. Two different papers have separate task
   IDs even in one profile. If this paper has no task, the current Agent calls
   `paperspine_open_task`; it must not wait for another host to create one.
4. For a new task supply a concise `title` and one-sentence `description` in the
   open-task payload, derived from the user's actual topic, inputs and requested
   output. Include the target venue when known; do not invent findings or expose
   absolute private paths. Preserve identity on resume. The task's workspace is
   for generated files; authorized material roots may correctly be elsewhere.
5. Prefill settings supported by the user's request as an AI proposal, including
   workflow, target, language, research mode, reading depth and delivery formats.
   Default to 3+3 papers or 6+6 for deeper literature learning; explicit counts
   prevail. Public-paper retrieval needs no permission toggle; private inputs
   stay local. Open the returned `skill_bridge.web_path` on the launched origin;
   verify the task title/ID and configuration/material cards. A homepage, stale
   task, blank page or printed URL is not a configuration handoff.
6. Await Web input with `host wait` (`product-v1-workflow.md`).
   Use same profile/task/version; follow its running exec session.
   Configuration needs `source=web_user`, `user_confirmed=true`,
   `readiness.ready=true`; choices need saved selections and comments.
   Prefills, old receipts and unrelated events are not answers. If pending,
   wait from `task_version`; stay responsive. Continue when valid;
   stop on cancellation/interruption. Web cannot wake a finished host turn.
7. Later motivation and figure choices follow the same request → Web save →
   read-back route. Respect existing explicit delegated-choice authorization;
   never label an Agent choice as a user click. On interruption, read the same
   task's snapshot and current pending input before continuing.

If startup fails, repair that concrete runtime/browser problem and retry the
same binding. Do not create a replacement task or infer missing configuration.
For an existing configured task, independent local corrections within its saved
scope can continue while Web is unavailable. New research/writing that depends
on pending configuration, material selection or figure decisions must wait.
If the user explicitly requests restarting from scratch, create fresh task state
for the same original inputs; do not silently resurrect deleted task IDs.

Use the chosen browser for paper decisions and results; keep internal grants,
receipts and Runner stages out of user chores.

## Work continuously within the confirmed scope

Use applicable protocol steps, not 17 forms or backend gates. Check artifacts
and downstream use; repair the source at the defect location and compare
outputs. After two unchanged attempts, change tactic, not notes/status/hash.
Reuse valid saved work.

**Mandatory before the next work segment or stage:** verify that the previous
segment's real results have reached the same task's workbench in the guided Web
workflow. In an explicitly authorized local research-agent prototype, inspect and record
the preceding real files in that same run instead; this does not claim Web sync.
For the guided workflow, read the current
snapshot; publish any completed deliverable that the user should see; call
`paperspine_commit_milestone` with a factual summary, the appropriate existing
stage and actual artifact IDs. Then read back the same task/profile and current
version: confirm its stage, milestone summary, visible files and pending choices
match what actually happened. Only then begin the next dependent segment.
Several protocol steps may share one existing stage; do not create 17 backend
stages or write a milestone for every sentence/tool call. Reuse an already
matching checkpoint rather than duplicating it. On resume apply this check first.
Writing or publishing files alone does not advance the workbench. If read-back
fails, fix the concrete binding/sync error before claiming progression; keep
local results and continue only independent work within saved scope. Never fake
review/delivery completion to move a progress indicator. Follow the exact calls
in [product-v1-workflow.md](references/product-v1-workflow.md).

Read the saved `configuration.workflow` and `research_mode` before choosing work.
Use `build_from_materials` to develop the paper; `rewrite_existing` to improve the
existing argument and prose while retaining valid results; `audit` and `review`
to deliver findings on the supplied files; `revise` to address actual feedback;
and `transfer` to adapt the existing science to the new venue. Read the matching
playbook. Reuse valid configuration, choices and results: a workflow label does
not require another intake, new analyses, or an entirely new manuscript.

Choose tools, intermediate files, work order and repair tactics with scholarly
judgment. The route below describes the work the paper needs; it is not a rigid
sequence of approvals. Combine related work and run independent retrieval,
analysis or rendering in parallel when useful. Draft, figures and evidence can
inform each other while pending user choices remain unassumed.

Pause dependent work only for an actual missing user decision, indispensable
fact, or unavailable capability. Bundle related questions, reuse saved answers
and explicit delegated-choice authority, and continue unaffected work. Ordinary
search, template adaptation, wording, chart construction and local repairs within
the saved scope do not need another confirmation. Never silently skip the initial
Web configuration/material save or choose on the user's behalf in guided work.

Keep compact notes and valid outputs, not every example form or receipt. Read
applicable methods fully on first use. On resume, recover saved choices and the
next action; reopen needed original passages if their content was lost, even when
files are unchanged. A read marker is not retained knowledge.
When available and authorized, delegate bounded work with real inputs and disjoint
writes; inspect returned artifacts and manuscript use yourself. A worker's self-check
is not independent review. No fixed team is required.
Read [agent-orchestration.md](references/agent-orchestration.md) for dependencies,
bounded budgets, handoff, recovery and review independence; runtime completion
means a worker returned, not that its scientific claims were accepted.

Distinguish dependencies from permissions; retry with a concrete correction.
Recheck affected outputs and stop optional polish without useful improvement.

## Scientific methods for the current action

Use [paper-production-methods.md](references/paper-production-methods.md) for the
applicable research, contribution, drafting, figures, rendering, review and
delivery methods. Select the section for the current action; follow its original
method links. The scientific requirements remain active when applicable.

## Quality rules that always remain active

- Every substantive claim has source/result support and a bounded uncertainty.
- Citation identity and citation context are both checked; no fabricated or inert
  references. Author, ethics, permissions and external actions are confirmed,
  never inferred.
- User results are not silently reanalyzed, embellished or generalized.
- Figure story, pixels, caption, body reference and editable source agree.
- Use evidence-bound `author_voice_check.py`; `humanize_check.py` and detector
  scores are diagnostics, not paper-quality verdicts. Keep internal workflow
  chatter out of the paper, but preserve real study methods, software/model
  names, citations, ethics and factual venue-required or user-requested
  disclosures. Do not invent notices or remove truthful required disclosures.
  Keep detailed execution provenance in the private work package.
- Do not require historical Runner receipts, VERA acceptance, medical replay or
  a completed historical case suite as a general product prerequisite. The saved
  literature-learning counts remain active requirements for this paper.
- Unknown venue/author/ethics facts may limit submission readiness but do not
  block safe local drafting or correction.
- Report local delivery, scientific limitations, submission readiness and
  external authorization separately.

## Completion contract

Deliver the requested scope, not a publication guarantee. A focused edit returns
the repaired sources and affected requested outputs; full-paper PDF/DOCX and
package production apply when that delivery is in scope. Inspect affected
outputs and their relevant downstream use; report unavailable rendering or
independent review without inventing completion.

- Same task/material root; saved choices and limitations preserved.
- Arrange independent manuscript review. Correct scientific contradictions or
  narrow claims. If review is unavailable, deliver a usable draft with review
  pending, not a reviewed final. Optional style preferences need not block it.
- Requested figures, citations, PDF/DOCX and editable dependencies present;
  actual renders inspected, not merely hashed or built.
- Package contents and sharing scope explicit. Local draft delivery is not
  submission readiness; missing author/ethics/venue facts remain disclosed.
- External submission/publication requires separate authorization.

For resume/update/respond/translate/transfer/audit requests, read the specific
playbook first and keep the same task. Updates concern installation only and must
preserve task/data roots. Historical worker skill names and old Runner protocols
are not user entry points.

Use the user's language for progress and delivery. Keep reports concise and
truthful. The manuscript is the product; the task state is only its support.
