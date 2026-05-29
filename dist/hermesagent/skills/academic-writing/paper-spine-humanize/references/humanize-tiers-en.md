# AI Humanization Writing Directives (English)

Aligned with the 5 core detection dimensions used by major AIGC detection
systems (sentence-length distribution, paragraph structure similarity,
information density, connector frequency/distribution, term-context matching).

## Detection Dimensions

| Dim | What It Measures | AI Text Signature |
|-----|-----------------|-------------------|
| D1-Sentence Length | Histogram of sentence lengths | AI: 15-25 words, single-peak bell curve; Human: multi-peak (5-8 + 15-25 + 40+) |
| D2-Paragraph Structure | Cosine similarity of paragraph "grammar skeletons" | AI: 0.7-0.9 (every paragraph = claim-explain-example-summary); Human: 0.2-0.5 |
| D3-Information Density | Independent information points per 100 words | AI: 65%-75% flat; Human: 40%-85% fluctuating |
| D4-Connector Freq/Dist | Connectors per 1000 words + paragraph-start ratio | AI: 8-15/1k, uniform distribution; Human: 2-6/1k, clustered at key turns |
| D5-Term-Context Match | Ratio of terms appearing in "most standard" context | AI: ~100% standard; Human: occasional colloquial substitution |

## Universal Rules (all tiers)

1. Preserve all LaTeX commands, citation keys, equations, file paths, numeric values
2. Do not change factual content (data, results, conclusions)
3. Do not add evidence the author has not provided
4. Keep technical terms as-is (unless heavy tier allows substitution)
5. **Ban long dash separators** (e.g. "————" or 3+ consecutive em-dashes/hyphens).
   Academic papers do not use decorative dash lines as section breaks. Use blank lines or section headings instead.
6. **Produce humanize_matrix.md in parallel**: one row per writing unit processed

## humanize_matrix.md Format

| Row ID | Manuscript Unit | AI Pattern Found | Detection Dim | Severity | Applied Change | Expected Effect | Teaching Note |
|--------|----------------|------------------|---------------|----------|---------------|-----------------|---------------|
| 1 | Abstract | 3 consecutive sentences 18-22 words | D1-Sentence Length | High | Split sentence 2 into 5-word + 25-word | Breaks bell-curve distribution | D1 is the strongest detection signal — fix first |
| 2 | Intro P1 | Claim-explain-example-summary pattern | D2-Paragraph Structure | High | Rewrite as question-first, no concluding sentence | Grammar skeleton diverges from template | AI paragraph similarity 0.7-0.9 vs human 0.2-0.5 |

Every row must fill all 8 columns. Severity: High / Medium / Low. Detection Dim: D1-D5.

---

## light

**Targets**: D4-Connectors, D1-Sentence Length

### D4 Connectors
Ban: Firstly/Secondly/Finally, In conclusion/To sum up, Furthermore/Moreover/Additionally, It is worth noting/It should be pointed out. Replace with natural logical flow. Keep under 6 connectors per 1000 words.

### D1 Sentence Length
Every 3-4 sentences, one must differ significantly (≤ 8 words or ≥ 30 words). No 3 consecutive sentences with length difference under 6 words.

---

## medium (includes all of light + below)

**Targets**: D2-Paragraph Structure, D3-Information Density, D1-Strengthened

### D2 Paragraph Structure
Use different templates per paragraph. Ban "claim→explain→example→summary" loop:
- Question-driven: question→analysis→conclusion
- Compare-judge: view A→view B→differentiate→position
- Causal chain: observation→cause→inference→verification
- Abrupt end: deep argument, then stop — no summary
- Position-counter-synthesis

Each template used at most twice. Adjacent paragraphs must differ.

### D3 Information Density
- Core argument paragraphs: density 70%-85%, each claim backed by evidence
- Transition paragraphs: density 40%-50%, 1-2 sentences
- Density difference between consecutive paragraphs ≥ 15%

### D1 Strengthened
- No 3 consecutive sentences with length difference under 6 words
- Mix declarative, rhetorical (1-2/section), and hypothetical constructions
- Two length-distribution peaks: 6-12 words + 25-35 words

### First-Person
"We / Our study found / We observed" at method explanations and result analyses. ≥ 2 per 2000 words.

---

## heavy (includes all of medium + below)

**Targets**: D5-Term-Context, D2-Structural Variation, D3-Density Variation

### D5 Term-Context Breaking
At least 1 colloquial-but-accurate substitution per 800 words. Allow occasional informal expression ("in other words", "to put it plainly"). Allow personal commentary after result analyses.

### D2 Structural Variation
Introduction: may lead with core problem, not "background→gap→approach→contributions". Methods: may interleave rationale with description. Discussion: may leave 1-2 questions open.

### D3 Density Variation
Label every paragraph density (high/medium/low). No 3 consecutive at same level. Allow 1-2 intuitive leaps.

### Low-Frequency Vocabulary
At least 1 uncommon-but-precise academic term per 800 words. Accuracy over frequency.

### Connectors Tightened
Under 4 per 1000 words. Clustered at 2-3 critical turns only.
