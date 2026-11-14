# Research and supplied-evidence writing

The current Agent carries out this work. For chat-based work, use the user's
instructions and the same paper's notes and files. When the user chooses the
workbench, Web stores settings and choices and the public API exports the bridge
files. A research milestone records work the Agent actually performed.

Read the saved `research_mode`, materials inventory/authorized roots, task
question and any explicit offline instruction before deciding what work to do. Keep original
inputs unchanged. Record sources actually read and results actually computed.

## Starting from a topic

When the user requests a new study rather than writing from existing results,
read [research-full-cycle.md](research-full-cycle.md). It connects the topic to
prior-work checking, a testable question, design and fair comparisons, real
execution, analysis, scientific figures and the existing paper/review methods.
Confirm the same task's research scope and workspace; no existing manuscript or
dataset is required merely to propose a study. Obtain actual sources before making
dependent claims. Do not invent a new workflow enum or a second research authority:
the study's real outputs become materials for the existing build route.

`required` calls for the authorized research; `agent_decide` calls for a reasoned
choice and actual execution when chosen. `materials_only` still forbids new data
analysis and experiments: a topic in that mode can support literature-based
writing, but cannot silently become a new empirical study. Existing rewrite/review
requests retain their scope. Replication, descriptive and negative-result studies
are valid outcomes; novelty or publication is never guaranteed.

## materials_only — supplied results, with normal literature learning

Use supplied materials and existing results to develop the contribution and
write the paper. Extract text/tables, inspect relevant PDF/DOCX pages, check
units, provenance and internal consistency, and identify which existing result
supports each claim. Preserve existing analysis outputs and methods as reported.

Do not run new EDA, inferential tests, experiments, model fitting/evaluation,
data mining or rerun supplied scripts merely to produce reproducibility evidence.
Rendering a supplied result as a figure is allowed; computing a new statistical
outcome is not. Accept supplied figures and reported research without requiring
every original array. Resolve actual contradictions specifically; missing complete
reproduction inputs alone do not invalidate the result. Continue supported writing
and preserve good figures; do not fabricate outcomes or impose a new dossier.

Public literature learning, citation lookup, venue-format research and reference-
figure reading remain normal capabilities in this mode. Follow
[journal-learning.md](journal-learning.md) for the two saved reading-set counts,
bibliography target and narrative/figure learning. Read real abstracts and
overviews for the points they support; full-text availability is not a prerequisite
for every citation. Honor an explicit offline instruction. Describe actual reading
depth and do not claim independent reproduction of supplied scientific work.

The normal milestone summary can say "No new data analysis; reused these results
and learned from these papers", with genuine file locations and reading scope.
Then request supported contribution/motivation options and draft after the
user's choice. The configured literature counts guide actual reading, not a
separate approval chain. There is no mandatory analysis report, three-lens dossier,
Master attestation or Runner J4 acceptance for this route.

## required — perform the requested research and justified analysis

Start from the authorized material inventory and read files that affect the
claims. For tables/spreadsheets inspect column types, units, missingness,
formula errors and provenance. For PDF/DOCX extract and visually check the
source actually used. Define the scientific question and design before choosing
analysis. Use the narrowest justified method, check its assumptions, report
effect sizes and uncertainty where appropriate, and distinguish exploratory
from confirmatory work. For modelling split before fitting, avoid leakage and
preserve reproducible transformations, training/evaluation settings and scripts.
Do not invent data analysis for a task whose evidence is wholly qualitative.

For literature and venue research, use available literature MCP tools when
helpful, otherwise host browsing/retrieval tools; no extra MCP installation is
required. Public paper and reference-figure retrieval is a normal Skill capability,
with no separate networking checkbox or repeated authorization question. An old
profile's retired allow_network flag is not a gate for this capability. Respect
an explicit offline request and the selected research scope. Build the local source index
first when configured local-first; distinguish retrieval failure from no hits.
Keep source identity, version/date, accessible location, relevant passage and
claim context. Do not upload private materials without explicit authorization.

Use three useful research lenses proportionately: venue requirements and
audience, strong examples' argument/structure, and prior work versus the
proposed contribution. The Agent may handle them in one coherent pass. Follow
the saved same-field and target-venue exemplar counts in
[journal-learning.md](journal-learning.md); depth beyond those preferences
depends on the actual question and evidence gaps.
Never turn an exemplar's stylistic preference into a mandatory scientific rule.
Unknown submission facts need not prevent a supported local manuscript.

## agent_decide

Read the question, inventory and constraints, then explain whether new local
analysis will materially answer a gap. Normal literature learning remains part
of writing under all research modes. Choose the relevant
work above, including neither when existing results suffice. Record that reason
in the ordinary milestone summary. A saved refusal or explicit user instruction
takes precedence over Agent discretion. The choice persists through revision
until the user changes it or the permitted decision basis changes.

## Evidence handoff to writing and figures

Keep a compact source/result → claim → figure mapping alongside the real paper
under `task.workspace_root/paper/`; use existing notes and files where possible.
Store new analysis scripts/results there when analysis was selected. Record
limits, sources actually inspected and the work still needed through
`paperspine_commit_milestone`; do not directly edit derived bridge JSON.

Propose supported motivation/contribution options through the public decision
tool. After Web confirmation read the same task/choice file and continue normal
writing and figure tools. References teach method and visual communication and
may support attributed background, methods and mechanisms. Their empirical
findings must never be presented as this study's results. At figure planning/creation/assembly follow
the staged scientific reading guide in the main Skill.
