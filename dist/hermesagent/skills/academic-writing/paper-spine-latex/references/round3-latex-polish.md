# Round 3: LaTeX Conversion + Native English Polishing — Detailed Instructions

## Contents
- Phase 0: Markdown → LaTeX Conversion (Template-First Approach)
- Phase 1: Language Polishing

---

## Phase 0: Markdown → LaTeX Conversion

**This is the bridge step that determines whether all prior revision work reaches the final paper.** The Round 2 draft is Markdown; the final output must be LaTeX. Work section by section, never in bulk.

**Template-first approach**: Copy the original `.tex` file from the user-provided draft as the base. Use targeted `Edit` operations on each section's prose. Preserve in place: preamble, `\newcommand` blocks, figure floats (with `\label{}` and `\caption{}`), equation environments, `\maketitle`, and bibliography commands. Only modify text paragraphs — never rewrite LaTeX scaffolding. This reduces effort by ~70% and eliminates transcription errors.

### Conversion Procedure

1. **Read the original template `.tex` file.** Extract and reuse:
   - All `\newcommand` definitions (e.g., `\figrefwhole`, `\citewhole`, `\citewholep`, `\figpanelref`)
   - The preamble structure (documentclass, packages, theorem styles, etc.)
   - Citation command conventions: which cite command does the template use? (`\citep{}`, `\citewhole{}`, `\citet{}`, etc.)
   - Cross-reference patterns: how are figures/sections/tables referenced?

2. **Convert each section sequentially.** For each section:
   - Write into LaTeX with proper `\section{}`/`\subsection{}` commands
   - Convert citations from Markdown "Author (Year)" to template's LaTeX cite commands
   - Convert figure references: `Fig. X` → proper `\figrefwhole{fig:figureX}` / `\figpanelref{fig:figureX}{A}`
   - Convert equations from plain text to `\begin{equation}...\end{equation}` or `\begin{align}...\end{align}`
   - Escape special characters: `%`, `&`, `_`, `$`, `#`, `{`, `}`
   - Preserve bold/italic formatting as `\textbf{}`/`\textit{}`

3. **After converting each major section**, run a verification check:
   - Count paragraphs in Markdown source vs LaTeX output — do they match?
   - Are all citation keys present and correctly formatted?
   - Are all numerical values preserved exactly?
   - Are all equation numbers and cross-reference labels consistent?

4. **Complete the LaTeX file** with:
   - Full preamble (copied from original template)
   - `\begin{document}` / `\end{document}`
   - All content sections in order
   - `\bibliographystyle{}` and `\bibliography{}` commands
   - Figure includes with correct paths

5. **Final verification**: Read the complete `.tex` file from start to finish. Compare against Round 2 Markdown draft section by section. Flag any missing content, mangled equations, or broken citations. **This verification is mandatory — do not skip it.**

---

## Phase 1: Language Polishing

With the LaTeX file complete and verified, polish the English prose. **Edit only the text content between LaTeX commands** — never modify macro names, labels, or command syntax.

### What to Fix

**1. Article usage (a/an/the)**
Check every noun phrase:
- First mention of a specific entity → "a/an"
- Previously mentioned or unique entity → "the"
- Generic/uncountable reference → no article
- Read each sentence aloud; if an article sounds missing or wrong, it is

**2. Prepositions**
Common corrections:
- "dependent of" → "dependent on"
- "consist with" → "consist of"
- "different to" → "different from"
- "result to" → "result in" (cause) / "result from" (be caused by)
- "compare with" (differences) vs "compare to" (similarities)
- "based in" → "based on"

**3. Sentence length and variety**
- Split run-on sentences (Chinese academic writing often fuses multiple ideas into one sentence)
- Vary sentence openings — do not start every sentence with "We", "The", or "This"
- Mix short punchy sentences with longer explanatory ones
- Maximum one complex idea per sentence

**4. Subject-verb agreement**
- "The data shows" → "The data show" (data is plural in formal academic English)
- "A set of features were" → "A set of features was" (set is singular)
- Compound subjects with "and" → plural verb

**5. Chinese→English structural pitfalls**
- 通过/采用/利用 → not always "through/using"; often better as "by", "with", or restructure
- 分别 → "respectively" is heavily overused; use only when genuinely mapping two lists 1:1
- 对...进行 → restructure rather than "conduct/carry out/performed on"
- 存在 → not always "exist"; often implicit in English
- 可以/可能 → "can/may" is overused; English often states directly
- Topic-comment structures: "The data, we analyzed them" → "We analyzed the data"
- Dangling modifiers: "Based on the results, the model..." → "On the basis of the results, the model..."
- Missing relative pronouns: "The method we proposed" → "The method that we proposed" (include in formal academic)

**6. Collocations and naturalness**
- Check verb+noun pairs: "make an experiment" → "conduct/perform an experiment"
- Check adjective+noun pairs: "strong relationship" vs "significant relationship" (different meanings)
- Avoid literal translations of Chinese four-character phrases (成语)

### Revision Process

1. Work paragraph by paragraph, not sentence by sentence — read the paragraph, understand the flow, then rewrite naturally
2. After rewriting each paragraph, read it aloud in your head. If any sentence feels awkward or hard to parse, rewrite it
3. Check each sentence against the pitfalls list above
4. After the full draft is polished, do a second pass on sentence variety:
   - Count sentences starting with "We" / "The" / "This" / "These"
   - If >40% start with one of these, vary the openings
   - Use adverbial openers ("Interestingly,..."), prepositional phrases ("In the context of X,..."), and inverted structures where appropriate

### Output

Save as `revision_3_native_english.tex` — a complete, compilable LaTeX file. Before declaring this round complete, verify: (a) every paragraph from Round 2 is present, (b) all numerical values match exactly, (c) all citation keys are correct, (d) all equation formatting is valid LaTeX.
