# Round 4: LaTeX Template Integration & Compilation — Detailed Instructions

## Contents
- Step 1: Set Up Output Directory
- Step 2: Template Integration Check
- Step 3: Compile and Fix
- Step 4: Content Integrity Verification (Mandatory)
- Step 5: Generate Plain Text Version

---

The Round 3 output is already a compilable `.tex` file. Round 4 ensures it compiles cleanly against the target journal's template, figures are correctly placed, and the bibliography resolves without errors. Round 4 is about integration, compilation, and verification.

## Step 1: Set Up the Output Directory

1. Copy the target journal's template files (`.cls`, `.sty`, `.bst`) to the output directory
2. Copy all figure files to the correct subdirectory (as specified by `\graphicspath{}` in the template)
3. Copy the `.bib` file
4. Copy the Round 3 `.tex` file as the main document

---

## Step 2: Template Integration Check

The Round 3 `.tex` file already contains the template preamble. Before compiling, verify:

1. **Preamble consistency**: Does the preamble match the official template files?
   - `\documentclass` options
   - Package imports (no missing or conflicting packages)
   - Custom macro definitions (`\newcommand` blocks) — preserved from Round 3

2. **Figure path alignment**: Verify `\graphicspath{}` matches the actual figure directory. Verify every `\includegraphics{}` filename exists.

3. **Bibliography setup**: Verify `\bibliographystyle{}` matches the journal's `.bst` file, and `\bibliography{}` references the correct `.bib` filename.

4. **Section structure**: Verify all required sections are present and in correct order.

---

## Step 3: Compile and Fix

Run the full compilation cycle. **Do not stop until the PDF compiles without errors.**

```bash
cd <output_directory>/
pdflatex -interaction=nonstopmode <main_tex_filename>.tex
bibtex <main_tex_filename>
pdflatex -interaction=nonstopmode <main_tex_filename>.tex
pdflatex -interaction=nonstopmode <main_tex_filename>.tex
```

If compilation fails:
- Read the `.log` file to identify the error
- Fix the `.tex` file
- Re-run the full compilation cycle
- Repeat until clean (`pdflatex` exits without fatal errors, `bibtex` resolves all citations)

Common issues:
- **Undefined citation warnings**: Citation key mismatch. Search `.bib` for correct key or add missing entry.
- **Undefined control sequence**: LaTeX macro misspelled or missing. Compare with original template.
- **Figure not found**: Path mismatch. Check `\graphicspath{}` and actual file locations.
- **Missing `$` / unbalanced braces**: Math mode or bracket mismatch. Trace from reported line number.

---

## Step 4: Content Integrity Verification (Mandatory)

After successful compilation, **verify that the compiled PDF contains ALL content from the Round 3 LaTeX file.** This is the most important verification in the entire pipeline.

1. **Read the compiled PDF** page by page
2. **Compare against the Round 3 `.tex` file** section by section:
   - Are all sections present? (Abstract, Introduction, Methods, Results, Discussion, Funding, Data Availability)
   - Are all subsections present with correct numbering?
   - Are all figures visible and correctly referenced in the text?
   - Are all equations rendered correctly?
   - Are all citations resolved (no `[?]` markers)?
   - Are all numerical values intact?
3. **If any content is missing or corrupted**, fix the `.tex` file, recompile, and re-verify.

---

## Step 5: Generate Plain Text Version

Extract the final text from the compiled PDF or `.tex` file to `plain_text_paper.md` for easy browsing.

---

## Output Structure

```
<paper_output_directory>/
├── <main_tex_filename>.tex    # Main LaTeX document (the filled template)
├── Fig/ or figures/            # Figure files
├── reference.bib               # Bibliography
├── [template files]            # cls, sty, bst files
├── supplementary.tex           # If applicable
└── paper_rewriting_output/     # All intermediate outputs
```
