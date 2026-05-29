# LaTeX Source Control Workflow

Use this reference when the manuscript is already in LaTeX or must end as LaTeX.

## Goal

Prevent LaTeX repair from consuming the paper-writing task. Separate prose revision from structural LaTeX changes and verify the source early.

## First Rule

If the user provides a LaTeX project, keep the original project as the structural source of truth. Do not convert to Markdown and back unless the user explicitly asks or the LaTeX source is unusable.

## Step 0: Baseline Guard

Before rewriting:

```bash
python scripts/latex_guard.py path/to/main.tex --bib path/to/references.bib --markdown > paper_rewriting_output/latex_baseline.md
```

If a TeX engine is available, also compile the original project. Record whether failures existed before revision.

## Step 1: Identify Protected Regions

Do not edit these unless the task is specifically about LaTeX repair:

- preamble,
- document class and packages,
- macro definitions,
- theorem environments,
- equations,
- figure/table floats,
- `\label{}`,
- `\ref{}`, `\autoref{}`, `\cref{}`,
- citation commands,
- bibliography commands,
- supplementary file includes.

## Step 2: Revise Prose Safely

When editing `.tex`:

- Rewrite paragraphs between commands.
- Keep citations in place unless the citation itself is wrong.
- Preserve line breaks around environments.
- Escape literal special characters introduced in prose: `%`, `&`, `_`, `#`, `$`.
- Do not rename labels during prose polishing.
- Do not reformat the whole file.

## Step 3: After Each Major Section

Run:

```bash
python scripts/latex_guard.py path/to/main.tex --bib path/to/references.bib --markdown
```

Fix errors before moving on. Warnings can be collected for the final LaTeX pass.

## Step 4: Compile Late, But Smoke-Test Early

Use this order:

1. Baseline compile original project if possible.
2. Rewrite one section.
3. Guard check.
4. Continue section by section.
5. Compile after all content edits, or earlier if guard warnings suggest structural damage.

If compilation fails, read the first fatal error in the log. Do not blindly rewrite surrounding content.

## Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---|---|---|
| Undefined control sequence | macro removed or package missing | compare with original preamble |
| Undefined citation | citation key changed or missing in `.bib` | restore key or add verified bib entry |
| Figure not found | path changed or graphicspath mismatch | restore file path or copy figure |
| Runaway argument | unbalanced brace in prose or command | inspect nearby paragraph |
| Misplaced alignment tab | unescaped `&` in prose | replace with `\&` |
| Missing `$` inserted | math symbol used in text | wrap math or escape literal |

## Final LaTeX Report

Save as `paper_rewriting_output/latex_report.md`:

```markdown
# LaTeX Report

## Baseline

- Original project compiled: yes/no/not attempted
- Baseline errors:

## Guard Checks

| Checkpoint | Errors | Warnings | Fixed? |
|---|---:|---:|---|

## Compilation

- Engine:
- Command:
- Status:
- First fatal error, if any:
- Remaining warnings:

## Content Integrity

- All sections present:
- Figures present:
- Tables present:
- Equations present:
- Citations resolved:
- Known author tasks:
```
