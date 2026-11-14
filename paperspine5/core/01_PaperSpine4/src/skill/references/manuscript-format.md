# Target-venue manuscript assembly

Read this before choosing the document template, converting a manuscript, or
reviewing a format revision. Apply it to the same task and its saved article type,
language and formats. A successful export is only the start of the format check.

## Establish the intended format

Use the current official instructions and the local learning PDFs from
[journal learning](journal-learning.md). First verify that the venue is the saved
target or was selected under explicit delegated authority. If it is only a
provisional comparator, keep the output venue-neutral and do not label it
target-compliant. In the existing working notes, retain the official source/date
and the exemplar pages used for decisions. Resolve:

- Article type, title page and author information; abstract structure and limit,
  keywords, section hierarchy, declarations and supplementary files.
- Page geometry, columns, fonts, leading and paragraph/heading spacing.
- Citation system, marker position relative to punctuation, spacing, consecutive
  ranges and mixed groups; reference ordering, author initials/truncation, title
  case, journal abbreviation, volume/pages or article number and DOI display.
- Figure/table numbering, captions, panel labels, units and footnotes, editable
  table requirements, placement, graphical abstract and separate upload files.

Do not infer these details from the word "Vancouver" or apply a universal numeric
style to every journal. Use an official template/CSL when available and inspect
what it actually renders. An old publisher PDF may show a former design; current
explicit requirements govern submission. If a requirement remains unavailable,
state the specific uncertainty and use a justified observed convention for the
draft. Do not claim verified official compliance for that detail.

The user's reading PDF should visibly apply the learned page design. If current
submission instructions require different column or float placement, produce
the appropriate submission files from the same semantic manuscript and identify
their purposes clearly. A different reading layout must not silently change the
text, references, numbers, selected figures or scientific captions. Keep the
scientific caption and accessibility description as separate semantic fields.
Some venues require labelled alternative text below legends in the submission
manuscript while excluding it from the visible typeset article. Apply that
verified rule per output purpose; preserve the description in the required
submission files and use supported accessibility metadata in the reading output.
Do not remove it indiscriminately from every format, duplicate it in reading
captions, or claim a tagged accessible PDF without verifying the emitted file.
Do not invent author,
affiliation, ethics, funding, journal branding or publication metadata to fill
the template. Keep missing submission facts explicit without filling the body
with engineering review notes.

Before placing manuscript content in a template, apply
[publication-surface.md](publication-surface.md). A title-page author note,
draft-status field, footer or supplementary page is still reader-facing text.
Transfer the scientific manuscript and required declarations; keep task choices,
reviewer progress and delivery notes in the local work package. Do not preserve
an earlier production-status paragraph as if it were immutable scientific text.

## Verify and actually use official templates

Inspect the current venue's author instructions, conference-year paper kit when
applicable, and the publisher's author/LaTeX resources. Follow their official
template links; if a link is absent or broken, make a focused search of the
official venue/publisher resources. Check the requested year, article type,
current publisher and review/submission/camera-ready purpose. An older year's
class or a generic publisher class is applicable only when the current guidance
supports it. Do not infer this from a familiar filename or third-party listing.

Download the applicable package locally and actually read its README/instructions,
sample source, class options and relevant style settings. Identify its engine,
fonts, geometry, title/author macros, anonymity options, bibliography workflow
and required assets. Classify what was obtained before selecting a tool:

| Asset | Correct use | What it does not establish |
|---|---|---|
| Raw official LaTeX sample plus `.cls`/`.sty`/bibliography assets | Compile an untouched local copy with its documented build, then fill a working copy through native TeX or a thin adapter. | A complete sample document is **not** a Pandoc template; never pass it directly to `--template`. |
| Pandoc LaTeX template | Use `--template` only for Pandoc template syntax that consumes the body (directly or through partials/conditionals) and supplies the metadata/support constructs needed by the emitted TeX. Test with the manuscript's actual metadata and content. | A `.tex` suffix or adding `$body$` alone does not make a raw sample compatible. |
| Word template/reference document | Read the official instructions and styles. For Pandoc, prepare a compatible reference DOCX and pass `--reference-doc`; copy styles/section properties from an official Word sample as needed. | A reference DOCX supplies styles/properties, not its sample body, title page, boilerplate or a TeX layout; `.dotx` is not directly a reference DOCX. |

When an applicable official template is available, use it. Compile/render its
demo first, then a representative manuscript page through the chosen integration.
For a thin Pandoc adapter, preserve the official class, options, fonts, geometry
and title/abstract structure; translate content insertion and metadata, and add
only the support macros/packages actually needed by the writer. Keep the original
package beside the adapter and note the small changes. Do not silently replace
the class with `article`, overwrite its margins/fonts or discard it because the
exporter's stock command is easier. If adaptation conflicts with the class or
bibliography system, use its native build and produce the requested Word from
the same semantic content. Validate citation/object links in both outputs.

Compare the rendered manuscript with the official demo for the applicable mode:
title block, fonts, text area/columns, headings, captions and references. Check
that our actual text/figures replaced all sample content. Keep source URL/date,
package version/year, local assets, applicability decision, actual build command
and demo/current page locators in existing layout notes. Downloaded, read,
compiled-demo and applied-to-manuscript are distinct observations; only the last
with the rendered comparison supports a claim of actual template use. Demo
authors, affiliations, ethics and publication identifiers are never our facts.

If these sources yield no applicable package, record the actual URLs searched,
outcome (not found, inapplicable or inaccessible), remaining uncertainty and the
chosen fallback. Stop repeating the same failed lookup; continue with a standard
renderer adapted to verified current instructions and the local target PDFs.
A build failure with an available template calls for dependency diagnosis or a
native build, not a claim that the template does not exist. Report any remaining
build limitation and provisional fallback honestly. Normal retrieval, adaptation
and repair within the task need no new user approval or template/profile gate.

## Turn the learned format into reusable document assets

The host creates or adapts the layout as ordinary document work using the actual
target requirements. Do not wait for a developer to supply case-specific commands.
Before full assembly, compile a representative working sample containing the real
title/abstract structure, one body section, one figure/table caption and references;
compare its rendered pages with the learned exemplar pages and correct the source.
This sample is part of normal manuscript construction, not a new approval artifact.
Reuse a suitable official template first. Otherwise adapt the selected renderer's
standard template and reference DOCX using the observations above; do not infer
that a stock template already implements the target venue.

Use the installed shared manuscript exporter for supported source formats.
Inspect its help and existing template/filter arguments before writing a new
conversion program. If it has a repeated defect, fix that reusable capability;
if a native official TeX workflow is necessary, use its real build system and
document that reason. A journal layout is an asset, not a second manuscript
compiler or a hardcoded medical-paper generator.

Keep the venue layout separate from scientific content: page/section settings,
Word styles, TeX template, CSL and only necessary layout filters. Read the actual
template's styles and variables before editing. Store these assets and their
build invocation with the manuscript so another host can regenerate it. A venue
layout may be reused after checking article type and current requirements; never
embed a case's title, authors, numbers, conclusions or required figure count in
the shared exporter or promote its design into a rule for every field.

Apply the observed format in this order:

1. Establish page geometry, body fonts, leading and section/column structure.
   Handle title/abstract and full-width content as actual sections or layout
   constructs, keeping the underlying text and object IDs intact. A format-specific
   filter should handle absent optional metadata instead of assuming every paper
   supplies the same fields. Prefer the chosen engine/template's native column
   and float flow. Repeatedly balancing/restarting columns around forced in-place
   full-width objects can trade a reading-order defect for half-empty pages;
   changing every float to a fixed position is not a general repair. Check both
   flow and page occupancy after changing placement, including the title page.
2. Define title, headings, normal prose, captions, bibliography and table text
   styles. Inspect inherited borders, shading, paragraph spacing and pagination
   rules; changing the font alone may leave a stock template's decorations or
   body double-spacing inside tables. Retain editable tables. When applying a
   Word table style, check its actual `w:styleId` as well as the display name in
   `word/styles.xml`; the requested style must resolve in the emitted document.
   For a numbered bibliography, align the hanging indent and any tab stop with
   the emitted number/separator and the widest labels used. A hanging-indent
   value alone does not ensure that author text and continuation lines align.
   Narrow-column headings need appropriate alignment rather than stretched word
   spacing. Scope keep-with-next/keep-together rules to the smallest meaningful
   unit; avoid binding long sections or chains of paragraphs into large blocks.
3. Implement article-specific placement: figures inline or at the end, separate
   figure legends if required, table notes, supplementary material and graphical
   abstract convention. Derive an end-of-manuscript legend list from the same
   captions; do not maintain two independently typed caption sets. Verify both
   figure and legend navigation after a layout transformation. Keep a short
   table with its caption and notes; for a multipage table, keep its final rows
   with the notes and apply the venue's continuation convention. Moving all
   tables to dedicated pages is appropriate only for the intended output's
   requirements, not a universal cure for pagination failures.
4. Check fonts in the actual PDF and Word render. A requested font family in
   metadata is not proof that either engine used it; inspect substitutions and
   glyph coverage and retain the real fonts/dependency notes. Use an available,
   appropriate font when needed and disclose a material format difference.
5. In a real Word instance or an equivalent faithful editor, update caption and
   reference fields, repaginate, save the resulting DOCX and export its PDF proof.
   Use an owned document/application session and close only those resources.
   Do not pass the separately generated TeX PDF off as a Word rendering.

If the venue requests a word count, establish exactly which parts it includes
before counting. Calculate from the current complete manuscript, including the
specified abstract, captions, tables, references or notes. Exclude running headers,
line/page numbers and duplicated layout-only legend copies as the rule requires.
Do not treat Markdown tokens or an unexamined Word total as the official count.
After substantive edits, refresh the displayed count and inspect the final title
page. When the official counting scope is unavailable, label the actual scope used.

### Apply the local published-PDF learning to pages

Use the saved target-venue set (three original local PDFs by default, or the
user's chosen count), following journal-learning.md's access and version rules.
Open each PDF; an author manuscript or HTML printout cannot stand in for the
publisher's typography. Identify the relevant publication year/design and article
type. For each exemplar, retain concrete page observations and their effect on
the current reading layout in the existing notes, for example:

| Exemplar file/version and page | Observed design | Adopt/adapt and producing asset, or reason to differ | Current rendered page |
|---|---|---|---|
| Actual local PDF and page locator | Measured/visually checked font, text width, caption or spacing choice | Template/style/section changed; current official rule if it takes precedence | Page where the change is visible |

Across the set, cover title/abstract, normal prose, a dense table when present,
main figure/caption, citations/bibliography and final-page rhythm. Record actual
font sizes and text/column widths where measurable. Build a small representative
page set early and place current and reference page views side by side at the
same physical scale; different fit-to-window zooms can conceal tiny text. Every
selected PDF must inform a concrete retained or revised layout decision, with
any inapplicable observation explained. A list of three papers or screenshots
without an applied design decision is not completed learning.

Use this comparison to refine the reading PDF's typography, column widths,
heading/caption hierarchy, float flow and page density. Use the official demo
to check template integration; published pages teach reading design and do not
override current submission rules. Keep necessary reading/submission differences
explicit. Never copy publisher logos, DOI, volume/issue, page ranges, acceptance
dates or other publication identity into an unpublished manuscript.

Inspect all finished pages. Fix stranded references, avoidable gaps, crowded
table/figure pages and uneven abstract hierarchy in the producing assets. Balance
columns/floats where permitted; do not delete references or shrink text to impose
an arbitrary page count. A repeated conversion defect belongs in the shared tool;
a typography or placement choice belongs in the reusable venue layout.

### Keep figures readable at their final placed size

Keeping a figure and its caption on one page is not sufficient acceptance. Check
each figure in the actual PDF and faithful Word render independently, including
the densest panel, smallest axis/legend label and symbols. Record the final placed
width/height and smallest effective label size in the layout notes. For uniform
scaling, `effective label pt = source label pt × placed width / source width`,
using the same width units; check the real output for cropping or further scaling.
For example, an 8 pt label in a 180 mm figure becomes 4.4 pt at 100 mm. Higher
image DPI cannot repair that physical text size. For raster-only artwork with
unknown source type size, measure the placed lettering and inspect it at physical
page scale; do not invent a precise source-font value or approve only a zoomed view.

Use the venue's final-size figure lettering rules and the learned page design to
set a readable working minimum before placement; if unspecified, choose and record
a practical target (often 8–10 pt for ordinary labels), then inspect readability.
This is a design target, not an invented journal rule or a fixed score gate.
Captions, lines and meaningful internal detail must remain readable too.

When figure plus caption does not fit, use an allowed full-width placement or
dedicated page, rearrange panels/remove wasted artwork margins, or redraw at the
intended size with larger labels. Shorten only redundant caption wording while
preserving definitions, units, evidence boundaries and necessary explanations.
If still necessary, split at meaningful panel boundaries with consistent IDs and
captions, or use an explicitly labelled continued caption where permitted. Keep
required separate submission legends derived from the same caption source.
Do not keep shrinking the whole figure, remove scientific structure or compress
caption text below readability just to satisfy keep-with-next. Rerender affected
PDF/Word pages, remeasure the placed figure, and recheck all pages that reflowed.

## Keep one semantic manuscript

### Apply the requested output language

Read the same task's `configuration.output_language` and the user's language
instructions. For `multilingual` or `other`, use the languages actually specified
in the conversation, materials or saved comments. If they remain unspecified,
ask only for the missing language choice while continuing language-independent
work; do not silently assume a language pair or claim multilingual completion.

Produce the complete manuscript in each requested language and requested format,
including title, abstract, body, captions, tables, notes and relevant supplements.
Use one scientific source with corresponding language versions and stable citation
keys/object IDs. Keep numbers, units, equations, evidence boundaries and references
equivalent; translations may differ in wording and layout, not findings. Keep a
small shared terminology list where ambiguity matters. Preserve bibliographic
identity and apply the venue's rules for translated titles instead of inventing
new references. Use fonts that cover the actual script.

Render and inspect each language's actual PDF/DOCX, checking for missing glyphs,
truncation, inconsistent caption labels and omitted passages. The translated
manuscript is a user-facing document, not a summary or a translation of internal
audit notes. Do not require the historical fixed Chinese audit-file inventory.

### Preserve citations and object references

Keep citations as stable bibliography keys and figures/tables/equations as stable
IDs. Generate visible numbers in their order of use. Use semantic citation and
cross-reference support in the chosen authoring system, such as Pandoc citeproc
and cross-reference handling, or native LaTeX citation/label commands. A valid
Pandoc citation is not defective merely because its emitted TeX uses
`\citeproc` instead of `\cite`.

Choose and apply the venue citation style before rendering PDF, DOCX and TeX.
Do not fix only one exported file by replacing bracketed text with superscripts,
typing reference numbers, or moving citation punctuation with a regex over the
whole TeX document. A deliberate citation-style transformation must operate on
the citation structure and preserve targets and the surrounding sentence.

Each figure and table needs a real caption and ID, plus a body cross-reference
to that ID. Preserve LaTeX caption/label/reference semantics. In DOCX, retain
editable captions and bookmark/field-based references so the target survives
normal editing; when using numbered caption fields, update those fields before
the final Word export. Typing "Figure 1" in both places does not create a link
or maintain the number when a figure is inserted. Preserve editable tables as
tables, not screenshots. Graphical abstracts follow the venue's own convention
and need not be forced into the main figure numbering.

Apply layout through the venue template and Word styles. Reuse the same source
content and bibliography across outputs. Keep the actual build command and the
template, CSL, filters, fonts/dependency notes and editable figure assets needed
to rebuild. A manuscript-specific layout adjustment may be appropriate; repeated
conversion or linking logic belongs in the installed reusable tools.

### Shared manuscript exporter

For Markdown, supported native LaTeX or Pandoc JSON, use the installed `scripts/manuscript_export.py`
with its adjacent `scripts/manuscript_refs.lua`. It processes citations once
with the selected CSL, then exports the same semantic content to DOCX and TeX
and compiles that TeX to PDF. Pandoc 3.8.3 is the tested version; 3.12 changed
DOCX bookmark names and fails the current reference checks even for the unchanged
Markdown path. Check an alternative version on real references before accepting
it. PDF additionally needs the selected local TeX engine. Check these actual
executables once; use an available equivalent authoring
system when the host has a different toolchain while preserving the semantics.

```text
python scripts/manuscript_export.py manuscript.md --bibliography references.bib --csl venue.csl --output-dir export --reference-doc venue-reference.docx --metadata-file venue.yaml --template venue-pandoc.tex --pdf-engine xelatex
```

For an existing TeX manuscript, preserve its native project and use
`--source-format latex`. Supply an existing `--latexpand /path/to/latexpand` when
it includes other files, especially table rows: the LaTeX reader can silently
collapse a nested table input. The exporter writes a separate flattened reader
input, keeps the first longtable header, removes only recognized continuation
furniture, and rejects scientific text in footers instead of deleting it. It
also removes the known `>{\raggedright\arraybackslash}` layout modifier from
that input because Pandoc otherwise consumes the first cell token. Compare
every table cell's median, interval, units and denominators with the native
source; object counts cannot detect this loss. Arbitrary macro-generated
tables, custom drawing environments and complex footer conventions are outside
this bounded import support. Diagnose them explicitly and retain the native
build rather than inventing a per-paper converter.
Flattened input is read in the export directory so local publisher style macros
do not replace scientific source macros or break the reader. This does not adopt
the publisher's native layout. Native labelled-equation links that the Word
writer cannot resolve are rejected by the destination check; they need a faithful
semantic equation adapter or the native authoring route, not a claim that all
TeX constructs are supported.

Native `\caption`/`\label` and `\ref` preserve linked figure/table references;
both `tab:` and `tbl:` table labels are supported. Native counter resets are
not inferred by the reader. Put explicit supplementary labels in the task's
metadata, for example `reference-labels: {fig:supp: S1, tab:supp: S1}`, then
check each caption and its body link in both outputs. Bibliography keys remain
bound to the supplied BibTeX and selected CSL. `--formats docx tex pdf` uses the
same processed AST for all three outputs; the generated TeX is a semantic
export, not a replacement of the native project's class/layout. `--source-format
json` accepts Pandoc AST JSON; surface checks cover emitted formats, not unused
JSON metadata. Do not describe that as an exhaustive source audit.

Use `--pandoc /path/to/pandoc` for a verified official portable executable when
Pandoc is absent from PATH; it need not be installed globally or bundled into
the Skill. For single-page PDF figures in Word, use an existing `--pdftocairo
/path/to/pdftocairo` with adjacent `pdfinfo`, or PyMuPDF in the selected runtime.
The Word-only AST uses 300-DPI PNGs with source/output hashes; the semantic AST
and TeX retain the PDF assets. Multipage PDFs need an explicit page selection
before export. Supply a prepared reference DOCX with real page geometry and
learned styles, and font metadata with actual glyph coverage for TeX/PDF. These
dependencies and layout choices belong in the editable work package; inspect
the actual Word render separately after updating its reference fields.
When the actual Word render splits a short table row, `--keep-table-rows` adds
`cantSplit` only where no explicit row rule exists. Keep captions/images together
through the reference DOCX styles and inspect tall rows rather than assuming
this flag proves good pagination. Use a reusable layout filter for wrapping
tables whose reader supplied no column widths; do not shrink or crop scientific
content to fit the stock writer. Page geometry and column proportions remain
task/venue layout choices.

The bibliography reader preserves an `eid` article identifier as CSL `page` when
the parsed entry has no page, and normalizes Unicode hyphens only within parsed
given names so citeproc retains both initials. Family and compound names and the
original BibTeX stay intact. Its reader-input JSON and change list make this
compatibility transformation visible. Check actual article identifiers, author
initials and style in both outputs; a bibliography count does not prove fidelity.

Keep BibTeX DOI and URL fields as raw identifiers, rather than TeX-escaping their
underscores or other URI characters as prose. Let the renderer handle display
escaping, then compare the actual PDF link targets and DOCX relationships with
the source identifiers; a correct-looking reference can still link incorrectly.

Here `venue-pandoc.tex` is a compatible Pandoc template, not a raw official sample;
`venue-reference.docx` is the prepared style reference. Select the engine actually
supported by the template; the example's XeLaTeX is not a venue requirement.
The reference DOCX, metadata file and Pandoc template are optional tool arguments;
for a venue-specific delivery, supply the appropriate learned layout instead of
claiming the default template matches that venue. Run from the working source
directory or use full paths. Keep the source, BibTeX, CSL and templates in the
editable package along with the resulting files and copied local image assets.

For custom `--template` in a TeX/PDF export, the exporter probes Pandoc with the
current AST metadata and a unique body marker before writing replacement outputs.
This uses Pandoc's native template processing, including partials and conditionals;
it does not merely search for a literal `$body$` in the top-level file. A template
that drops the body produces a located error and leaves existing manuscript
outputs intact. Repair the adapter's body insertion or use the official native
TeX build in the same task. Probe success proves body consumption only, not full
content integrity or correct layout; compare the real generated manuscript too.

The result's `format_inputs` records supplied `template`, `reference_doc`,
`metadata_file` and `csl` paths and SHA-256 values, with `applied` indicating use
for the requested formats. A TeX template is not applied to DOCX-only export; a
reference DOCX is not applied to TeX/PDF-only export. Use these details to check
which assets the build actually received. They do not prove official provenance,
article/year suitability, visible style fidelity or successful page review, and
do not require a new configuration field, user confirmation or JSON dossier.

Use `![Caption](figures/overview.png){#fig:overview}` for a numbered figure and
`: Caption {#tbl:summary}` for a table caption. Cite these objects in the body
as `@fig:overview` and `@tbl:summary`; keep bibliography citations as `[@key]`.
For an unnumbered graphical abstract, use a figure ID with `.unnumbered` and
`ref-label="Graphical abstract"`. Do not manually repeat "Figure 1" inside a
numbered caption. Keep bibliography citations and figure/table references in
separate groups. The exporter rejects missing/duplicate/wrong-kind destinations
so they can be corrected in the source.

Use its repeatable `--lua-filter` option for an article's layout transformations
when needed, preserving the shared citation keys, object IDs and source content.
Ship any such filter with the editable package. A layout filter must not replace
semantic captions or citations with manually numbered prose.

The exporter checks both the source and generated manuscript text for production
notes. Its result separates `conversion_succeeded`, `publication_surface` and
`render_diagnostics`. The final TeX log is checked for missing glyphs; findings
include the character/font warning and log location. `word_diagnostics` locates
repeated figure prefixes and measures actual image placements and effective DPI.
Its label-size result remains unknown without reliable source/render measurement;
pixel density is not a legibility pass. Repair repeated prefixes in the producing
source or reference label, preserving the valid link and scientific text.
Exit 2 means located text, missing glyphs or repeated Word references need
review/repair; exit 3 means text extraction was incomplete.
Generated paths remain available. Read the report and diagnostics, repair the
source, font/notation or extraction problem in the same task, then rerun the
affected export. Preserve scientific meaning; these are not new user
approval gates. If a match is legitimate research content, preserve it and
explain that specific finding in the real review instead of deleting it to make
a pattern check pass. Native TeX builds use publication-surface.md's explicit
source/output check as well. No-rule-matches does not replace full-page review.

After the DOCX writer and layout filters run, the shared exporter resolves a
table style's unique display name to its actual table style ID. Valid IDs remain
unchanged. If a style is missing, ambiguous or of the wrong type, correct the
named style in the reference DOCX/layout and rerun the affected export; do not
accept the silently unstyled table or turn a repairable format issue into a new
user approval step. Actual appearance still requires the rendering check.

Set `figure-title` and `table-title` in the metadata when the venue or language
uses different display labels, such as `Fig.`/`Tab.`. The same labels apply to
captions and body references in both formats; Word's internal sequence names
remain stable. The default labels are `Figure` and `Table`.

Place the citation node correctly in the semantic source. For a verified
sentence-final superscript convention, `Sentence.[@key]` attaches the marker
after the punctuation without an extra word space; the CSL supplies the actual
superscript. Other venues and sentence-internal citations can need different
placement. Inspect the rendered result rather than assuming the CSL moved the
source punctuation automatically.

## Inspect structure, pixels and reader interaction

For a template with known reserved header/footer bands, an optional read-only diagnostic is `python scripts/pdf_reserved_band_probe.py draft.pdf --footer-mm <millimetres> --report band-report.json`. Declare the actual template band; inspect any full-span furniture exemptions and flagged pages. Keep input and report paths distinct. The helper needs an existing PyMuPDF environment and explicitly rejects rotated pages. A tool/configuration failure leaves that check unverified: continue actual page inspection rather than treating it as a clean result or blocking research. No flags or exit0 establishes layout quality.

For likely whitespace/column problems, use the existing visual helper directly
on each current PDF (including a faithful DOCX proof when available):

```bash
python <installed-skill>/scripts/visual_readiness_check.py --inspect-pdf <current.pdf> --columns 2 --json
```

Choose `--columns 1` for a single-column surface. This read-only path requires
PyMuPDF; it reads page pixels and needs no legacy manifest, output directory,
form or task-state change. Exit 0 means no heuristic layout signals, 2 means
regions require visual review, and 3 means analysis incomplete. It reports the
actual PDF hash, pages, normalized regions and source-repair suggestions.
It does not prove source/output parity, human viewing or independent approval.
Sparse title pages/reference tails may be intentional; assess the actual page
and its neighbors instead of treating occupancy as a pass/fail quota. Missing
PyMuPDF does not block manual rendering/inspection using an available tool.

For an unintended gap, fix the source's float/column/page break, rebuild affected
surfaces and compare the same location. Do not shrink type, remove supported
content or rewrite an audit note to satisfy a metric. Two unchanged targeted
attempts require a different tactic, not a fresh retry count from a new hash.

These checks answer different questions and none replaces the others:

1. **Source and output correspondence.** Check all cited keys against the final
   bibliography, numbering in first-use order, missing/unused entries, and
   repeated/grouped/range citations. Check body figure/table references against
   the selected assets and actual captions. Compare PDF and DOCX content with
   the current source after conversion; counts alone cannot detect a swapped
   reference, changed number or omitted paragraph.
2. **Destination validity.** Inspect every internal citation and cross-reference
   destination in the emitted PDF/DOCX. It must identify the intended entry or
   caption, including entries in different columns on the same page. The mere
   existence of a hyperlink, or a destination at the beginning of References,
   is insufficient. For a figure, including an unnumbered graphical abstract,
   compare the destination position with the rendered visual block: landing
   below the image on the correct page is still wrong. Preserve a useful target
   at the block's beginning when moving captions or separating legends.
   A collapsed range may link only its displayed endpoints;
   its full cited set must still be correct. Check DOI URLs independently of
   internal bibliography navigation.
3. **Actual rendering.** Visually read every PDF page and the actual DOCX or a
   faithful Word rendering. Inspect title/abstract, ordinary body pages, dense
   tables, equations, all figure/caption pairs and references against the local
   target PDFs. Check marker size/baseline/punctuation/spacing, wrapping,
   clipping, float gaps, page density, heading order and final-page composition.
   In multi-column pages, read each complete column in the document language's
   normal direction before the next column. Check heading and paragraph
   continuity across full-width figures/tables and column restarts. A float
   moved to a later page must not leave separate column groups that appear to
   reverse the reading sequence; source order or PDF text extraction alone
   cannot establish this. Repair the layout, preserving content and the
   applicable template, then inspect the affected pages again.
   In native Word, inspect bibliography first-line and continuation alignment
   across different number widths and later pages, not just the first entry.
   Fix the producing source/template and rerender affected outputs.
4. **Actual reader interaction.** In the user's browser, click a single citation,
   a citation group/range, an entry in a later reference column/page, a figure or
   table reference, and a DOI. Verify the intended target and return to the task.
   Also check the downloaded file in a PDF/Word viewer when needed to distinguish
   file defects from Web preview defects. A raster page preview can look correct
   while discarding every PDF link; its appearance is not an interactive check.

Fix missing targets, wrong markers, rendering defects and preview defects at
their actual source. Reuse unchanged valid analysis and figures. An external
site being unavailable is different from a wrong DOI URL; report each accurately.

## Review and package the current revision

Give the independent reviewer the current rendered files, semantic source,
selected figures and local target-venue PDFs. Request specific findings on the
format and editorial criteria that apply, not a generic "all clear". Record what
was examined and any remaining concrete gap; do not inherit approval from a
different PDF or declare an adopted improvement implemented before it is visible.
When a reader identifies a defect in a previously approved file, reopen that
specific finding even if the file bytes have not changed. Give a fresh format
review the current outputs and representative target-page pairs, without using
the old PASS as evidence. Pagination changes can move content throughout a
document: inspect all reflowed pages, including tables/notes and the final page,
while reusing valid scientific checks and unchanged standalone figure checks.

Give one current set: rendered manuscripts, their exact sources, bibliography,
each current standalone figure and the scientific supplements, plus the saved
research scope and relevant exemplars. Ask for scientific validity, argument and
editorial quality, publication-surface cleanliness and actual layout separately.
The reviewer reads those files and submits their own real conclusions through
the public review entry. A report file alone does not register a review; listing
an artifact does not prove it was inspected. Reuse checks of unchanged bytes and
review changed or previously uncovered files without restarting all research.

After correction, regenerate every affected delivery format and both requested
packages. Confirm that their included files match the reviewed revision and that
editable dependencies are present. Exercise preview and actual Chrome download
through the same task. Separate verified formatting, scientific/editorial
quality and missing submission facts in the final report. Do not mark the paper
complete while a required or user-rejected figure remains unresolved.
