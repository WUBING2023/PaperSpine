# Journal learning for the current host workflow

Use this during public literature learning, manuscript planning and revision in
the existing task. It applies in `materials_only` too: that setting prevents new
data analyses, experiments and model runs, not normal literature work. Honor an
explicit offline instruction. Keep private materials local.

## Saved preferences and two useful reading sets

Read the actual saved `configuration.target`, scene and `configuration.literature`
from the task/bridge. When literature preferences are absent, use these defaults:

| Field | Default | Meaning |
|---|---|---|
| `same_field_papers` | 3 | Strong papers addressing closely related questions |
| `target_venue_papers` | 3 | Representative papers of the intended type in the target venue |
| `reference_count_mode` | `venue_average` | Aim above the observed venue sample's mean bibliography size |
| `reference_count` | null | The user's positive count when mode is `custom` |
| `mechanism_figure` | `prefer` | Proactively consider a mechanism, conceptual framework or method architecture |

The user can choose 3+3, 6+6 or custom counts in chat or the workbench. Honor a saved choice.
Use six distinct papers for the default two sets; an overlapping role can be
noted, but three papers counted twice are not six papers learned. Prefer relevant,
strong research and communication at the target venue's level or above. Explain
the selection using topic, article type, contribution and figure quality; do not
equate availability, open access or an unverified venue ranking with quality.

If no venue is specified, do not silently turn an Agent-selected comparator
into the target. When the user has delegated venue selection, choose a scientifically
suitable journal with viewable published-PDF exemplars, explain the fit and save
that venue through the chosen configuration route before target-specific
assembly. Otherwise request one concise target decision and continue safe
venue-neutral work meanwhile. A provisional comparator may guide general quality,
but it cannot support a claim of target-format compliance. Respect explicit
non-journal scenes. When the user authorizes an open-access alternative, record
that target change through the same configuration workflow. If a non-OA
target prevents the requested learning, use that existing delegation to select
a suitable OA target and update its article requirements; do not repeatedly ask
for the same permission or quietly change an explicitly fixed venue. OA access
is a selection constraint, not evidence of scientific quality. Preserve useful
same-field work and broader non-OA citations supported by actual abstracts.
Read current official author instructions for the selected article type, including
length, abstract, sections, figures, reference style, required files and template.
Keep official rules distinct from stylistic patterns observed in published papers.

For each learning paper, note its identifier, role, parts actually read and a few
concrete lessons. Read accessible body sections to learn their argument and prose;
inspect the actual figures to learn visuals. Publisher previews, author manuscripts
and institutional copies can supply these parts. An abstract alone is not evidence
of having studied an unavailable figure or the full article's writing structure.
Choose a comparable viewable exemplar when necessary; do not restrict the broader
bibliography to open-access papers.

## Local target-venue PDFs and visible page design

Download every selected target-venue learning paper as a local PDF under the
same task's `paper/references/` or existing exemplar directory. Prefer the actual
publisher version of record, recording its source URL and article identity.
Open the PDF to confirm that it is the correct article, readable and complete;
an HTML error page with a PDF filename is not a download. XML/HTML remains useful
for searching and extracting text but does not replace the local learning PDF.

Use normal publisher, repository or authorized access. If the published PDF is
unavailable, distinguish any author-manuscript PDF from the publisher version;
do not print XML/HTML into a PDF and present it as original journal typography.
Seek a comparable published-PDF exemplar, documenting any substitution and keeping
the original scientific citation when useful. If access still fails, report that
specific learning gap and continue independent writing; do not silently count it
as completed PDF/format learning. This requirement applies to the target-venue
learning set, not to every item in the broader bibliography.

Before selecting or modifying the manuscript template, render and visually read
the target PDFs, including title/abstract, normal body pages, figures/tables,
captions and references. Compare page geometry, columns, fonts and sizes, leading,
heading hierarchy, paragraph spacing, citation appearance, float placement and
page density and the amount of intentional white space. Keep a concise comparison with page locators and actual source/current page views; text extraction, reference counts and a format checklist alone cannot establish page-design learning. Store two explicit decisions: the current official submission surface and the clean reading surface. A successful compile of a generic article class is not evidence that the target-venue format was applied.

Distinguish the venue's current submission instructions from its published page
design. Complete manuscript-format.md's bounded official-template discovery and sample
compilation, then use the applicable template for its intended purpose. For the
user-facing reading PDF, apply the learned journal layout where compatible with
the user's request and the intended artifact, instead of defaulting to a generic
report. If a submission manuscript must differ, keep its purpose explicit and
do not present format-neutral submission compliance as matching published design.
Do not imitate journal branding or invent DOI, volume, page or acceptance details.
Use present official requirements when older learning PDFs show a former design.

Apply [manuscript-format.md](manuscript-format.md) to turn these observations
into the actual template, citation style and editable document structure. Compare
markers, punctuation, cross-references and link behavior as well as typography;
do not count a readable PDF or an untested hyperlink as complete formatting.

## Broad, useful references without unnecessary full-text gates

Cover the problem's context, foundational methods, close competitors, recent work,
interpretations and relevant contrary findings. A source may support one basic
point; it need not be central to the paper to deserve a citation. Real abstracts
or overviews suffice for claims they actually support. Keep a compact identifier
and point-of-use note rather than an elaborate evidence form for every entry.
Use proportionate closer reading for pivotal, disputed or detailed claims.

The manuscript may draw a reasoned inference from a source. Label that as our
interpretation rather than attributing it to the cited authors as a demonstrated
result. Never invent inaccessible details, numerical results or a full-text read.

For `venue_average`, count bibliography entries in the selected comparable
target-venue papers, record those counts and their observed mean, and aim for at
least `floor(mean) + 1` useful references. This is an estimate from those articles,
not an exact journal-wide average; do not use cited-by counts. Prefer comparable
research articles over mixing reviews and letters. The user can override the
target with `custom`. An official article-type reference ceiling takes precedence
when the default cannot fit; explain the adjustment. Do not pad with irrelevant
references or create a numerical task-status gate. If a source's count remains
unavailable, mark the estimate provisional and continue useful reading/writing;
never manufacture a count or silently claim the default has been met.

Before completing the bibliography, compare the actual distinct cited entries
with the saved target and the source counts in the learning notes. If short,
inspect context, methods, close comparisons and alternative interpretations for
useful missing literature and continue that reading. "Avoid padding" is not by
itself a reason to abandon the target. A real scope or article-rule conflict may
justify a documented adjustment; report the actual shortfall and reason instead
of marking the preference fulfilled. This remains scientific work, not a new
numeric approval gate or a demand to read every cited paper in full.

Use a shortfall to inspect missing scientific roles: nearest prior result, method
definition, competing explanation, relevant failure case or practical consequence.
For each useful addition, change the passage it informs and check its actual
support. A larger candidate library does not close a used-reference shortfall;
neither does repeating citations to the same source. Keep the saved preference
and actual used count visible while judging contribution and validity separately.

## Transfer the learning into the actual manuscript

Apply both reading sets to the research-question framing, Introduction's argument,
Methods granularity, Results sequence, figure roles, Discussion, captions and
citation practice. Adapt these moves to the user's actual research and the venue;
do not copy sentences or import an exemplar's results into this study. Retain a
short map from selected lessons to current sections/figures in the existing notes.
Confirm the transfer in the artifacts themselves: the manuscript source should
show the chosen template/style and article structure, while representative rendered
pages should visibly reflect the learned hierarchy, density, captions and reference
practice. Notes about the venue without these source/page changes are research, not
applied formatting. No historical Runner stage, separate target-profile approval or
new dossier chain is required to perform this work.

Keep the existing article/figure plan aligned with the actual files during
assembly. When a graphical abstract, supplementary figure or other deliverable
is required or already planned, either complete its distinct scientific job or
record a concrete justified change to the plan. Do not silently leave it in a
"later" note at delivery or rename a mechanism schematic as a graphical abstract.
Reuse valid results and components; no additional data analysis is implied.

Use [assertive-scientific-writing.md](assertive-scientific-writing.md) for the
researcher's voice and proportionate qualification. State one central advance
relative to the actual prior work and support it consistently in the title,
Introduction's closing question, Results and conclusion. Organize the results
into a complete argument using the user's existing evidence: the method's
rationale, core findings, explanations and scope as appropriate to this study.
Do not force every field into the same fixed sequence or invent a new discovery
to make an incremental contribution sound larger.

When the contribution is vague, compare it with the closest work actually read:
what that work established, which question the present evidence answers, and
why the answer matters. Use the available results to distinguish a supported
increment from merely naming an activity such as "characterizing a profile."
Strengthen the framing where the evidence permits; do not demand new analyses
outside the saved scope to make the story appear more novel.

Before asserting that earlier work missed a relationship or perspective, check
the relevant Results, tables/figures and Discussion of the closest current
same-field paper. An older introduction's gap statement or a retained learning
summary may no longer describe what is known. Separate an already established
association from the particular distribution, comparison or explanation this
study actually adds; a different display or grouping is not automatically a new
scientific finding. If new reading changes that distinction, revise the title,
abstract, closing Introduction and conclusion together, preserving useful results.

Give the Discussion scientific substance: compare findings with relevant work,
explain agreements or differences, consider alternative explanations and develop
practical or theoretical implications with clear boundaries. Attribute reasoned
inferences honestly. Concentrate consequential limitations where they change
interpretation, rather than repeating an apology in each paragraph. The title
and abstract should foreground the question, key method, important findings and
meaning; omit file-validation trivia and secondary-result inventories.

Give each main figure a clear scientific question. Use panel hierarchy, consistent
color meanings, comparable scales and readable annotations to connect evidence
and interpretation. Preserve and develop meaningful multi-panel complexity when the evidence supports
it. Follow the whole-paper planning and complex-reference selection in
[scientific-figure-workflow.md](scientific-figure-workflow.md); avoid reducing a rich
research story to a single easy summary plot. Extra panels must add scientific
content rather than duplicate numbers or introduce unsupported statistical symbols. Preserve high-quality supplied content while
adapting its communication to the two reading sets and the manuscript's argument.

Use supplied research results, methods and good figures as the user's reported
evidence. Inspect them, preserve their scientific content and fix specific factual
conflicts. Missing complete raw arrays or reproduction inputs alone do not justify
discarding a supplied ablation, motif, conservation or mechanism figure. Do not
claim independent reproduction when only writing and visualization occurred.

With `mechanism_figure: prefer`, actively identify the best explanatory figure for
this study after inspecting whether and how the exemplars use one. Follow
[scientific-figure-workflow.md](scientific-figure-workflow.md), including finding
an actual explanatory-figure reference when the initial sets contain only data
plots and selecting tools by component before generation. A biological
mechanism, social/physical conceptual framework and computational architecture
serve different purposes. Map elements to supplied results, cited knowledge or
explicit hypotheses. Reuse a good existing diagram first. For newly generated
mechanistic/schematic raster artwork, use the prescribed GPT Image 2 capability;
retain editable scientific labels and a readable final figure. Keep quantitative
plots tied to their data and deterministic plotting sources. `auto` requires an explicit usefulness decision: produce the complete explanatory
candidate when it materially clarifies the paper and sources support it, or retain
the concrete reason for omission in the existing figure plan. `omit` respects the
user's preference. The explanatory candidate supplements rather than displaces
necessary data figures. Do not turn `prefer` into a random probability or an
obligation to imply proven causality.

## Independent editorial review of the actual new paper

When delegating this review, provide the current manuscript and actual renders,
the retained learning-PDF paths and page lessons, the closest current work and
parts actually read, and the saved preferences with unresolved learning items.
Include the exemplar bibliography counts and the current citation processor's
distinct used-entry count; a candidate library is not the manuscript bibliography.
Reuse the existing files and notes in the handoff rather than making a new form.
This lets the reviewer assess the requested comparison instead of inferring it
from a numerically valid result or an earlier limited review.

Alongside numeric, citation and render checks, independently assess whether a
reader can state the contribution in one sentence, whether the evidence supports
the complete argument, whether the Discussion adds insight, and whether each
main figure earns its place and whether the complete set adequately represents the
provided results. Identify valuable results lost during simplification and compare
the information depth, panel hierarchy and connections with the actual exemplars. Compare the relevant prose and figures with specific
exemplars actually read. Open the local target-venue PDFs beside the current PDF
to assess page design, and use actual mechanism references for mechanism review.
Locate weaknesses in a paragraph, section or figure and
give a concrete revision that addresses them; an unsupported general impression
is not an adequate review finding.

State which requirements improved the manuscript and which remain incomplete.
Keep scientific validity, editorial quality and technical file delivery distinct.
A fixed score, long bibliography, diagram, matching fonts or error-free package
does not establish journal-level quality. Review the current revision's actual
files rather than carrying forward an older paper's approval. Do not impose new
experiments or analyses outside the saved scope to enforce a preferred storyline.
