# Round 2: Journal-Conformity Revision — Detailed Instructions

## Contents
- Phase 0: The Three R's (CASPArS method)
- Phase 1: Build Style Conformity Checklist
- Phase 2: Checklist-Driven Revision

---

## Phase 0: The Three R's — Corpus-Based Style Calibration

The CASPArS method (Ohata, Martin & Ison, *J. Chem. Educ.*, 2025) calibrates writing at word, phrase, and structure level. Use the 3 deep-read journal papers as your corpus.

**R1 — Recalibration**: Align word usage with field standards.
- Compare your Round 1 draft against all 3 journal papers for each key term
- Does this word appear with the same frequency? Example: if journal papers use "demonstrate" 15× and "show" 2×, recalibrate toward "demonstrate"
- Check: verb+noun pairs, adjective+noun pairs, preposition choices

**R2 — Replacement**: Choose context-appropriate alternatives.
- For overused or non-standard words, use the journal papers' concordance to find field-preferred synonyms
- Example: if our draft says "important" 20× but journal papers use "critical", "essential", "fundamental", "central" contextually, replace accordingly
- Pay special attention to: hedging verbs (suggest vs. indicate vs. demonstrate), connectors (however vs. nevertheless vs. that said), intensifiers (notably vs. particularly vs. especially)

**R3 — Redevelopment**: Holistic revision from corpus insights.
- Read the revised draft alongside a randomly selected journal paper
- If the two texts feel like different journals, identify WHY at sentence and paragraph level
- Fix: sentence rhythm, paragraph density, transition patterns

**Output**: Save Three R's analysis in `restructuring_notes.md`:

| R | Target Word/Pattern | Our Usage | Journal Consensus | Action |
|---|---------------------|-----------|-------------------|--------|
| R1 | "show" vs "demonstrate" | "show" 25× | "demonstrate" 15×, "show" 2× | Replace most "show" → "demonstrate" |
| R2 | "important" | 20× | varied: "critical", "essential" | Diversify |
| R3 | sentence rhythm | avg 28 words/sentence | avg 22 words/sentence | Split longer sentences |

---

## Phase 1: Build the Style Conformity Checklist

From the 3 journal papers' Pass 2 and Pass 3 outputs, build a specific checklist:

```markdown
## Style Conformity Checklist

### Structural
- [ ] Section order matches journal convention [specify]
- [ ] Section length ratios within ±10% of journal averages [list targets]
- [ ] Abstract format: [structured/unstructured, N words max]
- [ ] Introduction length: [N words target]

### Openings/Closings
- [ ] Abstract opens like journal consensus: [pattern]
- [ ] Introduction opens like journal consensus: [pattern]
- [ ] Discussion opens like journal consensus: [pattern]
- [ ] Each section closes like journal consensus: [pattern]

### Claims
- [ ] Claim strength distribution matches journal averages (Strong: N%, Moderate: N%, Tentative: N%)
- [ ] Hedging phrases match Template JS-3 consensus

### Terminology
- [ ] All terms from Template JS-6 switched to journal consensus
- [ ] No terms used that are absent from journal papers

### Citations
- [ ] Citation density within journal range (N-N cites/page)
- [ ] Citation placement matches journal convention
- [ ] Reference format matches journal's bst/style

### Figures/Tables
- [ ] Captions use journal-consensus style
- [ ] Figure callouts match journal convention
- [ ] Table formatting matches journal convention

### Supplementary
- [ ] Supplementary material policy followed
```

---

## Phase 2: Checklist-Driven Revision

For each section, process in order:
1. Read the current draft section
2. Reference the relevant journal papers' corresponding sections (from Pass 2)
3. Identify deviations from the checklist
4. Rewrite to conform, explicitly addressing each checklist item
5. Mark checklist items as done

Output: `revision_2_journal_style.md` + completed checklist in `restructuring_notes.md`.
