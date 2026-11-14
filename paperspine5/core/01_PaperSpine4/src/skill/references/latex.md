# LaTeX Stage

## Current host application

Assemble the requested source, PDF and editable Word without changing scientific
claims. Word remains a standard deliverable unless explicitly opted out. Apply
[journal-learning.md](journal-learning.md) and
[manuscript-format.md](manuscript-format.md) for the actual template, local-PDF
page design, semantic citations/cross-references and separate PDF/Word inspection.

Read and compile the applicable official sample for the requested year, article
type and output purpose before integrating manuscript content. Raw sample/class
files use their native build or a thin adapter preserving class, fonts and
geometry; only a compatible Pandoc template goes to `--template`, and a prepared
reference DOCX goes to `--reference-doc`. Follow manuscript-format.md for bounded
discovery/fallback and demo comparison. A generic class that compiles does not
demonstrate template adoption or learned publication design.

Use [round3-latex-polish.md](round3-latex-polish.md) for content-preserving
conversion and [round4-template-integration.md](round4-template-integration.md)
for integration, compilation and source/output comparison. Existing valid
preambles, equations, labels and citation keys should survive conversion; adapt
layout where current official requirements call for it. Use the template's real
title/front-matter and bibliography mechanisms, whether BibTeX, Biber or semantic
citeproc. Valid linked citeproc output does not require literal `\cite` commands.

Check every figure at the final physical PDF and Word sizes using
manuscript-format.md's placed-size method. Neither an image-count check nor keeping
the caption on its page permits unreadable labels. Fix placement, panel layout or
lettering in the producing assets, then inspect the actual affected renders.

For a supplied native TeX project that lacks Word, start with the shared exporter
described in [manuscript-format.md](manuscript-format.md), using `--source-format
latex`, the actual BibTeX/CSL and prepared reference DOCX. Use its existing
`--pandoc`, `--latexpand` and Word-only `--pdftocairo` dependency arguments as
needed; keep the native TeX tree intact. Check the supported import boundaries
there before conversion. Compare all table cells, formulae, captions and body
destinations, including explicit supplementary labels. A raw Pandoc conversion
or matching figure/table counts can silently lose numbers and numbering. Export
requested formats from the same processed semantic manuscript, then render and
inspect Word and PDF separately. Repair repeated reader failures in the shared
method/tool; do not replace it with a single-case parser or manually patch only
the delivered DOCX.

## Historical Runner compatibility

The remaining paths, manifests and guard commands document the historical Runner
contract. Use them only when maintaining a workflow that actually consumes those
files and after checking the installed tool's input/repair behavior. In the current
host, translate them to the same task's real source, requested formats, editable
assets and inspected renders; do not create alias files, JSON receipts, fixed
Chinese packages or a new PASS/approval chain just to satisfy this old inventory.
Current venue settings and manuscript-format.md take precedence over the legacy
title macros, fonts, page defaults and conversion recipes below. Useful diagnostics
can locate a repair; neither their PASS nor their fixed counts prove readability.

## Required Outputs

- `final_paper/main.tex`
- `final_paper/main.pdf` (compiled source PDF when TeX engine is available)
- `final_paper/paper.pdf` (must be a current copy of `main.pdf`)
- `final_paper/paper.docx` + `word_report.md`
- `final_paper/paper.zh.docx` + `word_report.zh.md` when `translation_package=zh`
- `latex_report.md`
- `final_artifact_manifest.md`
- `visual_audit_manifest.json` + `visual_readiness_check.md`
- `publication_surface_check.md`

## Scripts

```bash
python scripts/latex_guard.py paper_rewriting_output/final_paper/main.tex --markdown
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx --tex paper_rewriting_output/final_paper/main.tex --language en --fix-fonts
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx --tex paper_rewriting_output/final_paper/main.tex --language en --markdown --output paper_rewriting_output/word_report.md
python scripts/publication_surface_check.py paper_rewriting_output --markdown --write
python scripts/visual_readiness_check.py paper_rewriting_output --prepare --markdown --write
```

The visual prepare command intentionally returns failure while receipts are
pending. Inspect every listed render with a multimodal tool, complete the
manifest, then run the visual command again without `--prepare` and require
PASS. Read `visual-readiness-gate.md`; never write "visual inspection confirmed"
without the hash-bound page/figure receipts.

Read `execution-efficiency.md`. Preflight PDF and DOCX renderers once, then use
`execution_receipt.py` for expensive DOCX rendering or conversion. The visual
prepare command is itself exact-reuse aware: when the bound PDF, TeX,
`figure_requests.json`, figure assets, existing renders, and DPI are unchanged,
it preserves the current manifest and completed review instead of rerendering.
Any difference invalidates reuse and creates a new pending inspection surface.
Do not invoke an unavailable LibreOffice or Word backend repeatedly.

## Key Rules

**PDF alias (hard rule):** after compiling `final_paper/main.pdf`, copy it to
`final_paper/paper.pdf` in the same run. `paper.pdf` must match `main.pdf`;
never leave an older `paper.pdf` beside a newer `main.pdf`.
`artifact_check.py` fails stale or mismatched `paper.pdf`.

**Citation mechanism:** Bind every in-text citation to a real bibliography key through the semantic manuscript and the target's citation processor. Preserve the venue's numeric, author-year or superscript style, punctuation and links in PDF and DOCX. Do not type inert citation numbers. Interpret legacy latex_guard findings against the actual citation mechanism; valid citeproc output does not require literal \cite text.

**Title (hard rule):** `main.tex` must contain `\title{...}` (with the paper's
title) and `\maketitle` after `\begin{document}`. Word output must begin with
the paper title on the first page, not Abstract, Keywords, Introduction, or
body paragraphs. `latex_guard.py` checks the TeX source; `word_guard.py`
checks the .docx.

- Preserve citation keys and labels.
- Copy approved images into `figures/` with stable labels.
- When figures are active, read `figure_body_contract.json`; use its asset,
  caption, label, Results mapping, and claim boundary instead of inferring them
  from filenames. Preserve `final_paper/figure_sources/` as the editable-source
  handoff and ensure the prose contains a real `\ref`, `\autoref`, or `\cref`
  to every assembled figure.
- For Chinese: prefer XeLaTeX + CJK-capable template.
- If no TeX engine: keep `.tex`, record skipped compilation.
- If compilation fails: keep `.tex`, write first fatal error, do not claim pass.
- Word output is mandatory by default. If `word_output` is missing, treat it as
  `docx`. Only explicit `word_output=none` opts out.
- If Word is requested and the selected conversion backend is unavailable, use another available faithful document pipeline. Report the Word deliverable as incomplete only while no valid requested DOCX can be produced; preserve the source and the actual diagnostic.
- A successful compile or `latex_guard.py` report proves source integrity, not
  reader-visible integrity. Page cropping, blank/float-only pages, figure label
  conflicts, and caption/figure mismatches belong to the visual gate.

## English Word Output

From `final_paper/`:

```bash
pandoc main.tex -o paper.docx --from latex --to docx \
  --resource-path=. --extract-media=./media \
  --number-sections --citeproc --bibliography=references.bib \
  --metadata reference-section-title=References --metadata nocite=@*
```

Flatten `\input`/`\include` with `latexpand` first. Expand or remove
`\newcommand` macros. Treat the Word conversion as a separate reader surface:
create a task-local Pandoc input without changing canonical `main.tex`, replace
custom citation macros with Pandoc-recognized citations bound to the actual
`.bib`, remove equation-only labels, and rewrite unsupported math into equivalent
TeXMath, a clear linear equation, or a genuinely rendered equation image. A
Pandoc warning about citation or math conversion is a failed Word build, not a
successful conversion.

Scientific figures have a separate Word-media rule. Preserve the canonical PDF
figure files and their hashes for LaTeX/PDF; for the Word-only intermediate
source, deterministically rasterize each selected PDF figure to PNG and record
the source SHA-256, output SHA-256, figure ID, and conversion scope. The final
DOCX must reference one real `word/media/*.png` object per selected figure.
`word/media/*.pdf` objects are unsupported by the delivery contract because
Microsoft Word may render them as blank frames; their presence fails
image-complete even when all canonical PDF figures still exist. Run
`word_guard.py` with `--tex main.tex` so it compares the number of visible PNG
relationships with the canonical `\includegraphics` inventory. A page-render
receipt remains mandatory; package members or media filenames alone do not
prove reader-visible figures.

Round-trip the DOCX to plain text before visual review. Require an explicit
`References` heading, at least the material-profile reference count after that
heading, non-empty in-text citations, and no raw `\cite`,
`$$\begin{equation}`, or related TeX environment text. Then render the DOCX to
PDF and inspect every page; do not use a complete PDF to excuse an incomplete
Word artifact.

When an actual Word check finds malformed equations or unresolved links, repair the producing semantic source and regenerate the affected DOCX. Use a deterministic repair helper only after confirming that it preserves valid internal links and the requested editability; its success alone does not establish a readable or complete Word surface.

```bash
python scripts/word_surface_repair.py \
  --docx final_paper/paper.docx \
  --tex final_paper/main.tex \
  --output final_paper/paper.repaired.docx
```

The repair renders display equations from the canonical LaTeX as images,
linearizes remaining inline Office Math for portable readers, repairs only demonstrably unresolved internal
links while preserving valid citation and figure/table targets; if the helper cannot
preserve those targets, repair the semantic source and regenerate instead, and constrains oversized images.
Re-run the plain-text, PDF, page-image, bibliography, and visual checks affected
by the repaired DOCX; the repair receipt is evidence, not a replacement for
review. Run one complete final pass after all reader surfaces are frozen.

If its image-size constraints make a scientific figure too small, repair the
venue placement or figure composition using manuscript-format.md's final-size
method. Do not accept the constrained result solely because the helper passed.

After conversion, run `word_guard.py --fix-fonts` first, then run
`word_guard.py --markdown --output ...` and require PASS before proceeding.
The repair also writes explicit A4 page size and margins when the source DOCX
omits `w:pgSz` or `w:pgMar`; this is required for deterministic page rendering.
Use the current target venue's approved Word styles and fonts. Treat Times New Roman
as a fallback only when the target is unspecified; do not run font normalization
that overwrites a valid venue style. Verify actual Word rendering after any repair.

Font repair requires `lxml` (also a dependency of the Word surface repair's
`python-docx`). Preflight it in the selected Python runtime; if unavailable,
stop the repair without changing the document. Do not fall back to an XML
serializer that removes namespace declarations: Office compatibility attributes
such as `mc:Ignorable` refer to prefixes in their values. Font repair preserves
those declarations, rejects unresolved compatibility prefixes and DTDs, retains
unrelated ZIP members, and preserves the first `.bak_fonts` backup. Successful
font normalization still requires an actual DOCX open/export and page review;
an XML or font check alone does not prove that Word can display the document.

```bash
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx \
  --tex paper_rewriting_output/final_paper/main.tex \
  --language en --fix-fonts
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx \
  --tex paper_rewriting_output/final_paper/main.tex \
  --language en --markdown --output paper_rewriting_output/word_report.md
```

If numbered headings render as `1Introduction` or `2Methods`, regenerate or
repair the Word file so headings read `1 Introduction`, `2 Methods`, etc.
`word_guard.py` fails glued English heading numbers.

## Final Chinese Word Output

When `translation_package=zh` and `word_output` is not explicitly `none`, the
final Chinese deliverable is a single Word document, not a folder of Markdown
files:

- Required final file: `paper_rewriting_output/final_paper/paper.zh.docx`
- Required check report: `paper_rewriting_output/word_report.zh.md`

Generate it from `translation_zh/full_paper_translation.zh.md` after the
translation stage:

```bash
pandoc paper_rewriting_output/translation_zh/full_paper_translation.zh.md \
  -o paper_rewriting_output/final_paper/paper.zh.docx
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.zh.docx \
  --tex paper_rewriting_output/final_paper/main.tex \
  --language zh --fix-fonts
python scripts/word_guard.py paper_rewriting_output/final_paper/paper.zh.docx \
  --tex paper_rewriting_output/final_paper/main.tex \
  --language zh --markdown --output paper_rewriting_output/word_report.zh.md
```

`translation_zh/` remains the translation audit/intermediate package. Do not
list it as the only Chinese deliverable.
Chinese Word must use SimSun/宋体 for East Asian text and Times New Roman for
Latin text. If the font gate fails, repair the docx and re-run the report.

**Chinese abstract heading:** In a Chinese `main.tex`, author the abstract as
`\section*{摘要}` followed by the abstract paragraph rather than the LaTeX
`abstract` environment. pandoc renders `\begin{abstract}` as an English
"Abstract" heading in the .docx even for a Chinese paper (the `lang` variable
does not localize it); `\section*{摘要}` produces 摘要 in both the ctex PDF and
the Word file.
