# Evidence-led writing with complementary references

Apply this method when building a full paper, substantially reconstructing an
existing draft, or fulfilling a requested reference-guided/逐句对标 rewrite. It is
shared by the PaperSpine full-paper and standalone Followwriting stages.
A short local correction uses only the affected
passages and claims; a full-paper request must inspect all sections and produce
the actual revised manuscript. A diagnosis or writing map is not that manuscript.

Read [assertive-scientific-writing.md](assertive-scientific-writing.md) before
actual drafting. Lead with the scientific question, contribution, supported
finding and value. Retain qualifications where removing them would misstate the
object, comparison, independence or inference. Non-defensive writing never
licenses hiding strong controls, important negative results or uncertainty.

## Establish the study's own argument first

Reuse the current draft, source/figure binding and existing evidence notes. Keep
the baseline and protected data, equations, protocols, figures and layout. A
writing task does not authorize unlocking them or rerunning experiments.

Before choosing a reference structure, identify:

- The scientific object, relationship and observable endpoint being studied.
- The specific limitation of prior work, checked against its actual input,
  architecture, objective and task. No explicit input is not proof that a model
  cannot learn related information; an effective ablation does not explain why
  every competing method fails.
- The strategy that answers that limitation, what the overall evidence supports,
  and the resulting scientific or practical use.
- The contribution hierarchy: study identity, principal support, explanatory or
  identification analyses, scope tests and supplementary diagnostics. A recent
  experiment or best-looking example must not redefine the entire paper.
- For primary claims, their source, control, endpoint, statistical unit, effect
  and uncertainty, scope, and development/test exposure. Include substantive
  contrary evidence. Missing facts remain missing rather than being invented.

Build an independent outline from those questions and evidence. Use each
section for a reader-facing job: motivation and verified gap; data/target before
method information flow; one question and decisive comparison per Results unit;
then synthesis, prior-work contrast, meaning, alternatives and consequential
limits in Discussion. These are jobs, not compulsory headings or paragraph counts.
Follow the saved author-expression preference and venue requirements.

### Keep the comparison recoverable for the reader

Turn the contribution hierarchy into the actual result sequence. Distinguish
the principal comparison supporting the headline claim from analyses explaining
it, tests of its scope and supplementary diagnostics. Several designs or
endpoints in one study need not become one undifferentiated result or ranking.
Give each comparison its scientific job and make relevant differences in data,
coverage, representation, training/evaluation conditions or measurement explicit
where the reader first needs them. Do not imply that comparisons conducted under
different conditions form a single matched test.

While drafting and again from the main manuscript alone, try to recover: what
was compared with what, under which conditions, on which measured endpoint, what
was observed, and which inference that observation supports. If answering these
requires holding many dispersed qualifications or designs in memory, repair the
reader's burden in the article. Use a compact comparison diagram/table or a
scientifically justified grouping when it makes those relationships easier to
recover. Place it at the first relevant discussion of the comparisons, cite it
in the prose, and check its actual rendered position. A private evidence ledger,
a late supplement or a floating table that interrupts a later argument does not
solve a main-text navigation problem. Simple comparisons may be clearest in
prose; this is neither a table quota nor an instruction to copy an exemplar's
organization.

Keep design details needed to interpret the result beside it; place routine
module exposition and reproducibility detail in the appropriate Methods or
supplementary location without dropping necessary information. Make Discussion
synthesize what the combined evidence teaches and how it relates to prior work,
rather than repeating the result sequence or reintroducing routine modules.
This organization check uses existing evidence; it does not authorize new data
analysis or supply facts missing from the study.

## Learn complementary moves from real papers

Keep [journal-learning.md](journal-learning.md)'s saved learning-set sizes
(normally 3 same-field + 3 target-venue papers). From that pool, use the one or
two-to-three most relevant papers as detailed writing exemplars; this role
selection does not reduce the learning requirement or add another quota. Do not
count one paper twice or add weak references merely to fill roles. A single
suitable reference is usable when that is the actual available scope; disclose
any unmet saved learning requirement.

For each exemplar record its stable ID, real full-text file/version, read pages,
useful writing responsibilities and non-transferable content. Roles may overlap:
scientific motivation, method explanation, evidence organization and Discussion
synthesis. No fixed first paper governs the whole draft. One paragraph may learn
from several papers when each contributes a distinct useful move. First decide
the paragraph's own purpose and evidence, then select a move that serves it.
Do not rotate sources sentence by sentence, average their styles or reproduce
their special result order, innovation list, examples or distinctive phrasing.
Conventional IMRaD or a venue-mandated structure is not a copying defect.

Keep writing-example use separate from scientific support: borrowing a method
paper's explanatory sequence does not make it evidence for this study's result.
Read the relevant full-text passages and context. An abstract, page title or
unseen figure cannot establish full-text or visual learning.

## Trace actual changes without manufacturing correspondence

Merge a compact writing map into existing notes. For every body paragraph,
check its function and evidence; clear passages may remain unchanged. Detailed
anchors concern actual rewritten sentences unless the user requests every
sentence. A useful row contains the current sentence ID/source location,
before (empty for a genuinely new sentence), complete final sentence, function,
study evidence, requirement addressed, and zero/one/multiple reference anchors.
Each anchor separately identifies paper/version, physical and printed page when
different, paragraph/sentence locator, a compliant short quote or specific
paraphrase, and the learned move. Respect source-wide quotation limits; do not
use many short excerpts to reproduce a paper.

Use an empty anchor list and mark study-specific sentences honestly. Never
invent a before sentence, combine several originals into a false quotation, or
claim 100% correspondence through generic phrases such as "Here, we present".
An authentic source/page is not enough: reread the final sentence and check that
the recorded move actually occurs there or in its paragraph. Remove or narrow
an unsupported anchor rather than distorting good science to retain it. Keep
this trace in work notes; the paper is independent prose with scientific citations.

## Fresh writing and independent review

For full-paper reconstruction, use a fresh writing Agent with
`fork_turns="none"` or equivalent isolation when available. Give it the current
whole draft/source structure, figures/captions/tables, complete supplementary
evidence index, actual user constraints/target/protected items, all used exemplar
full texts, and the evidence-backed question/hierarchy/outline as revisable
proposals. Include strong controls, contrary results and exposure boundaries.
Do not give recent conversational emphasis, a required winner, anticipated
scores or an acceptance answer. Assign writes only to a new revision directory;
tell it others share the codebase and not to revert their edits. The host inspects
the returned actual manuscript and its evidence use.

Use another fresh Agent for review, distinct from the writer. Give actual current
manuscript, figures/renders, all used references, complete relevant evidence and
user constraints. It writes only review files. Apply
[review-policy.md](review-policy.md) and additionally inspect:

- Whether the title, abstract, contribution, Results and Discussion express the
  same study identity with direct, evidence-matched language.
- Whether the main article makes principal, explanatory and scope comparisons
  recoverable: comparator, conditions, endpoint, observation and inference.
  Check any reader-facing comparison map at its actual first-use/rendered
  position, and distinguish a real memory burden from a stylistic preference
  for adding a table. Check that routine detail and repeated Discussion do not
  obscure the supported main finding.
- Whether negative controls and inference limits remain where readers need them.
- Whether each learned move is visible in the actual prose and each anchor is
  real; scientific support must not be replaced by a writing-example citation.
- Whether the organization follows this study's questions/evidence rather than
  unnecessarily copying one exemplar's special sequence; multiple references
  should contribute real, distinct learning without a patchwork author voice.
- Whether changes preserve protected facts, figures, equations, protocol and
  claim strength; distinguish reparable text from a need for new evidence.

For anonymous comparisons, randomize document codes/order, normalize identity
cues where feasible, keep the decoding key with the supervising host, and give
reviewers the same declared criteria and necessary evidence. Do not reveal
which version should win or provide author self-scores. Record unavoidable cues
(such as familiar published content) and separate writing/argument quality from
scientific evidence adequacy and novelty; scores are editorial judgments, not
statistical proof or a publication guarantee.

Preserve original review findings. The host repairs the smallest affected source
and records issue → actual change/location → verification → disposition. Recheck
headline sections after a core-claim change; obtain independent affected-scope
re-reading after revision. Do not change reviewers repeatedly to obtain a desired
score. Compile/render the changed sources and inspect actual pages before
updating the working pointer. Report concrete unclosed evidence/locked-item
limits separately from completed local improvements.

When fresh Agent contexts are unavailable, continue permitted writing and
explicitly labeled self-check. State that isolated writing, independent review
or independent post-revision verification was not performed, as applicable.
If independent review is a required deliverable, it remains open; self-check
cannot close it. This method adds no external upload, publication, message,
training or user-choice authority.
