# Host judgment and bounded Agent execution

Use only when delegation is available and authorized, or the user explicitly
requests the research-agent product. A single host can perform the same work.
This method belongs to the one paper-spine Skill; the runtime dispatches jobs and
preserves their files, not a second scientific workflow or quality authority.
Follow [research-full-cycle.md](research-full-cycle.md) when new research applies.

## What stays with the host

The host decides research scope, the scientific question and design, comparability,
claim strength, useful next work and acceptance of actual outputs. Keep the saved
user direction, research mode, choices, workspace and existing manuscript identity.
Workers may identify gaps or propose a change; they cannot add experiments in
materials_only, invent permissions, change the selected direction or self-approve
scientific quality. Runtime job completion is separate from host interpretation
and independent review.

Guided production uses the conversation or, when selected, the Web configuration/choice route.
An explicitly authorized local research-agent prototype can use its actual
user-approved run brief and generated workspace. Record the real authorization
source; do not fabricate web_user configuration, user clicks, a profile or a new
paper identity. Product runs and direct Skill use read the same method sources
and produce the same research/manuscript files. A local runtime run ID identifies
execution within that paper, not a replacement paper task or scientific state.

## Decide whether to split the next work

Before delegating, name the concrete paper outcome, smallest useful bounded task
and evidence needed to inspect its result. Split only when the work is independent,
needs a separate reviewer context or benefits from specialized execution. The
host can combine roles and carry out short work directly; no fixed team or seventeen
role calls is required.

For example, prior-work retrieval and venue-PDF learning can proceed in parallel
with distinct writes; execution needs the chosen design; interpretation needs
actual results; independent review needs the current files it is asked to judge.
Method notes can begin before execution completes, but result claims cannot.
Use the real available concurrency and CPU/memory budget, not the number of
possible persona labels. Keep dependent work waiting on its needed evidence.

## Shared file handoff

Use the runtime's actual plan and command schema; inspect its current help/source
instead of inventing a new adapter, receipt format or hidden worker service.
The thin research-agent plan uses jobs with `id`, `role`, `instruction`,
`depends_on`, absolute `inputs`, relative `outputs`, optional `response_artifact`,
`timeout_seconds` and `read_only`. Use its actual enclosing workspace/resource
fields and verified CLI. Native host delegation carries the same information in
the task message and actual output paths; no JSON is required merely to spawn a
worker. Do not copy scientific methods into runtime role prompts as a separate
maintained source: give the canonical Skill path and the applicable method links.

The local prototype entry is
`<product-root>/06_插件化/research-agent/research_agent.py`:

```text
python <entry> init --plan <plan.json> --workspace <execution-directory>
python <entry> run --workspace <execution-directory>
python <entry> status --workspace <execution-directory>
python <entry> resume --workspace <execution-directory>
python <entry> cancel --workspace <execution-directory>
```

The actual plan's top level has `task_id`, `skill_path`, `method_paths`, `model`,
`codex_executable`, `backend`, `sandbox`, `budget` and `jobs`. The execution
directory retains `plan.json`, `state.json` and `jobs/<id>/<attempt>/`; it does
not replace the confirmed research workspace. `job:ID/file` refers to an output
of an explicit dependency. Budget fields are `max_calls_per_run`,
`max_calls_total`, `max_job_seconds`, `max_run_seconds`, `cpu_threads` and
`max_log_bytes`. Choose values for the actual task and reserve review capacity;
defaults do not grant extra compute or calls. Inspect current CLI help for an
affected rerun and host-result handoff. `codex` executes real fresh CLI sessions;
`host` prepares instructions until an actual executor returns its files and
evidence. Neither backend's status establishes scientific acceptance.

A useful instruction states:

- The question or defect being addressed and its scientific role in this paper.
- The actual request/configuration, design, inputs and current revision/locators
  needed for that task; preserve private/source materials and exclude unrelated
  profiles, transcripts or another paper's data.
- What may change, explicit output ownership, what must be retained and any
  research/choice/authorization boundary. Tell workers they are not alone and
  must accommodate other edits without reverting them.
- The actual deliverable the host will inspect, time/compute/call limits and the
  concrete condition to stop or return a blocked dependency.

`depends_on` expresses data/work dependencies; it is not a publication-quality
gate. Absolute input paths identify files, not proof they were read. Use current
revision or source/run locators in the instruction; optional hashes can distinguish
bytes but do not establish source meaning. Relative output paths must resolve
inside the confirmed workspace and the worker's assigned write scope. Independent
workers do not write each other's files or concurrently replace the semantic
manuscript. The host merges accepted changes or assigns a single owner.

The return must point to actual output files and state what was done, applicable
methods actually used, producing commands/runs where relevant, claim support,
failures, checks performed and unresolved dependencies. `response_artifact` is a
summary of that work, never a substitute for results, images, code or review.
Do not require an invented scientific PASS or a fixed form before returning usable
work. Preserve unsuccessful outcomes and the previous valid revision.

## Dispatch, inspect and take work back

With authorized native tools, spawn the bounded worker with its inputs, ownership
and budget, then continue independent host work. Wait for progress using the host's
available tools. With the thin CLI runtime, use its current init/run/status/resume/
cancel interface and explicitly selected backend. A host/prepared backend that
only writes instructions has not executed a researcher; a queued job or printed
command has not launched an Agent. Report backend availability and actual calls.

When a worker returns, open the real files before dependent use. For research,
inspect source passages and changed scientific decisions. For experiments,
inspect code/configuration, run logs, comparisons and raw result completeness.
For figures, inspect their full rendered pixels and editable scientific structure.
For prose, inspect the evidence, claims and actual manuscript integration. A
file list, exit zero or self-labeled result JSON confirms only its stated technical
scope. Record host conclusions and remaining limits in ordinary paper notes.

If the output is inconsistent, incomplete or outside scope, name the defect and
return one smaller correction with the needed evidence. If a worker drifts,
repeats an unchanged failure or spends budget without improving the paper, interrupt
it and take the dependency back: inspect inputs, narrow the task, repair locally
or reassign with a changed tactic. Stop the ineffective approach after two unchanged
attempts; new timestamps or hashes are not new tactics. Keep unaffected valid work.

## Budget, interruption and recovery

Use the runtime's actual run-call ceiling, per-job timeout and CPU/concurrency
limits; count retries against the same budget. Reserve capacity for inspection,
independent review and revision. Measure what tools expose: wall time, calls,
compute and reported token/cost data. Mark unavailable token/cost accounting as
unknown rather than estimating it as measured. A new local run or restart must
not silently reset exhausted authorized resources.

On timeout, quota interruption or cancellation, stop the real worker/process using
the supported tool, retain partial outputs/logs and record what may still be
running. A cancel status alone cannot prove process termination. Cancellation
does not delete input data or make partial science complete. Do not automatically
launch replacement calls after a user cancellation.

On resume, recover the same run brief, plan/design, input identity, output revision,
worker/process state and next unfinished dependency. Reuse inspected unchanged
results; do not rerun every successful experiment to refresh receipts. Validate
concrete missing/stale outputs before dependent use. An input/design change affects
only the relevant job and descendants; preserve their old revision, revise the
dependency and regenerate the affected subset. Do not inherit scientific acceptance
from another run or create a replacement paper because transport failed.

A role or CLI resume is not itself an experiment checkpoint. Inspect what the
scientific program actually saved, binding reuse to unchanged code, design and
data and verifying the completed units. Choose useful checkpoint blocks that
preserve expensive work without rewriting the entire growing prediction history
after each tiny operation. Continue the unfinished units; report which unsaved
work may repeat after an interruption. Keep earlier attempts immutable, and make
run notes reflect the actual current mode, completed and remaining work rather
than retaining canned pilot/partial descriptions after a completed main run.

## Independent review and affected revision

Use a fresh reviewer context distinct from the writer and experimental producer,
with read-only scientific inputs and an owned review-output location. Read-only
review means the reviewer does not edit research or manuscript files; its findings
can be returned in its own artifact. Give the original request/scope, frozen design,
current code/results/logs, actual source papers, manuscript, figures and renders
needed for the specified review. Exclude the producer's desired verdict, coaching
about a suspected issue or an inherited approval. An isolated workspace alone does
not establish independence if it inherits the writer's conclusions.

The reviewer applies [review-policy.md](review-policy.md) and the applicable
scientific/figure/venue methods from this Skill. Findings identify the current
file and paragraph/page/panel, evidence or requirement, interpretation consequence
and concrete remedy. Ask whether the controls and uncertainty justify the claim,
whether literature changed the design and argument, whether the figure explains
the actual science and whether learned venue layout reached the current pixels.
Do not force a criticism or demand acceptance after a fixed number of rounds.

The host maps findings to the smallest affected code, analysis, figure, wording
or format repair. Reopen the needed evidence, repair producing sources, regenerate
affected outputs and request affected-scope re-review. New research beyond scope
retains the user's decision boundary. A tool's success or a producer's response
cannot close a scientific finding; inspect the changed result. Preserve previous
versions and useful unchanged review. If independent review is unavailable or
cannot inspect required evidence, return the usable local draft with that precise
limitation instead of an independently reviewed final.

Retain a concise review boundary with the actual assignment, context/inheritance
mode when exposed by the host, reviewed revision and files/pages/calculations
actually inspected. Do not preserve whole private conversations merely for this
purpose or reconstruct missing tool calls afterward. An artifact-level correction
can demonstrate a repair despite missing historical logs; it cannot establish
unobserved full-context independence, every source retrieval or every page read.
When auditing prior work, separate a demonstrated defect, an unmet preference and
an unverified process claim. Missing records alone do not prove non-execution,
and a report's PASS alone does not prove scholarly acceptance.
