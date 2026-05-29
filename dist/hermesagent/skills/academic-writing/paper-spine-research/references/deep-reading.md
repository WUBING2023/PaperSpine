# Deep Reading & Cross-Paper Synthesis

## Contents
- Pass 1: Paper Skeleton + Context Map
- Pass 2: Templates A–H
- Pass 3: FAT Analysis
- Cross-Paper Convention Synthesis

---

## Pass 1: Paper Skeleton + Context Map (per paper)

**Goal**: Understand the paper's architecture without processing details.

```markdown
## Deep Reading Paper N: [Title] — [SOTA / Prior-SOTA / Adjacent-SOTA]

### Pass 1: Skeleton Map

**5Cs Revisited** (refined from survey pass):
| C | Detail |
|---|--------|
| Category | |
| Context | |
| Correctness | |
| Contributions | |
| Clarity | |

**Full Section Tree** (every section/subsection with approximate word count):
- Abstract (N words)
- 1. Introduction (N words)
- 2. Related Work / Background (N words)
- 3. Methods (N words)
  - 3.1 [Name] (N words)
- 4. Results (N words)
- 5. Discussion / Conclusion (N words)

**Figure/Table Inventory**:
| Fig/Table | Type | What it shows | Referenced from section |
|-----------|------|---------------|------------------------|

**Reading Plan** (5 most critical paragraphs for Pass 2):
1. [Location] — [Why critical]
2. ...
```

---

## Pass 2: Structured Deep Extraction (per paper)

**Goal**: Fill detailed extraction templates. Do NOT summarize — fill fields.

### Template A: Terminology Glossary

Extract 15-30 domain-specific terms per paper:

| Term | Frequency (est.) | Definition/Usage in paper | Our paper should use? |
|------|-------------------|---------------------------|----------------------|
| ... | ... | ... | yes/no/replace |

### Template B: Transition Phrase Bank

Collect transition phrases by function:

| Category | Phrases (verbatim) |
|----------|-------------------|
| Section openers | "In this section, we..."; "To address this challenge,..." |
| Paragraph transitions | "Building on this insight,..."; "A natural question is whether..." |
| Contrast/concession | "However,..."; "Nevertheless,..."; "In contrast,..." |
| Causal/reasoning | "This suggests that..."; "Taken together,..." |
| Result presentation | "We observed that..."; "As shown in Fig. X,..." |
| Limitation/hedging | "It is important to note that..."; "These results suggest..." |
| Contribution emphasis | "To the best of our knowledge,..."; "We introduce..." |

### Template C: Sentence Pattern Bank

Pick 5 critical paragraphs. Deconstruct every sentence:

**Paragraph location**: [e.g., Introduction P4 — Contribution statement]

| S# | Rhetorical Role | Subject | Main Verb | Word Count | Notable Pattern |
|----|-----------------|---------|-----------|------------|-----------------|
| 1 | Topic/claim | ... | ... | N | e.g., "By [verb-ing]..., we [verb]..." |

**Synthesize 3-5 reusable sentence templates** (with slots, not content):
1. `[Broad context], yet [specific gap] remains [unaddressed].`
2. `To [address this gap], we [developed] [method name], a [descriptor] framework for [task].`
3. `[Method] [outperforms] [comparison] on [benchmark], with [specific gain].`

### Template D: Argument Pattern Deconstruction

**Move 1 — Gap Establishment** (from Introduction):
```
Step 1: [broad importance sentence]
Step 2: [narrow to specific problem]
Step 3: [what prior work CAN do]
Step 4: [what prior work CANNOT do — the gap]
Step 5: [bridge gap to paper's solution]
```
Language signals: [hedging phrases, intensifiers, contrast markers]

**Move 2 — Claim → Evidence → Significance** (most important result):
```
Claim statement: [finding sentence]
Evidence presentation: [how data/numbers introduced]
Significance explanation: [WHY this finding matters]
```

**Move 3 — Limitation Handling** (from Discussion):
```
Limitation 1: [acknowledged] → [hedged/mitigated]
Limitation 2: ...
Future direction: [limitations → future work]
```

### Template E: Abstract Rhetorical Move Map

Deconstruct the abstract sentence by sentence. **Record information granularity** to prevent putting Results-level detail into the Abstract.

| S# | Rhetorical Move | Content Summary | Key Phrases | Granularity |
|----|-----------------|-----------------|-------------|-------------|
| 1 | Background/Context | ... | ... | qualitative |
| 2 | Problem/Gap | ... | ... | qualitative |
| 3 | Method/Approach | ... | ... | qualitative |
| 4 | Key Results | ... | ... | semi-quantitative or quantitative |
| 5 | Significance | ... | ... | qualitative |

**After filling, explicitly answer:**
- **Does this abstract contain specific numerical values?** [Yes/No — if Yes, list each]
- **What is the information ceiling of this abstract?** [e.g., "States outperforms but no numbers"]

### Template F: Figure/Table Design Patterns

| Aspect | Observation |
|--------|-------------|
| How figures introduced in text | |
| Caption style | title-first / description-only / title+description |
| Avg caption length (words) | |
| Table formatting | |
| Figure placement | in text flow / collected at end |
| Color usage | |

### Template G: Section-Level Information Conventions

**Critical for avoiding category errors** — putting Results-level detail into Abstract, or Abstract-level vagueness into Results.

| Section | Contains numbers? | Contains citations? | Claim specificity | Example |
|---------|-------------------|---------------------|-------------------|---------|
| Abstract | Yes/No | Yes/No | qualitative / semi-quant | [quote] |
| Introduction | Yes/No | Yes, N | qualitative | [...] |
| Methods | Yes (setup numbers) | Yes | quantitative for setup | [...] |
| Results | Yes (metrics, Δ, p) | Yes | quantitative | [...] |
| Discussion | Mostly no | Yes | semi-quantitative | [...] |

**After filling:**
- **Where do specific numerical metrics appear?** [Typically ONLY Results/Discussion]
- **What is the Abstract's information ceiling across all 3 papers?**
- **What information type is in Results but ABSENT from Abstract?**

### Template H: Rhetorical Move Analysis per Section

Map every paragraph to its rhetorical move. This is the core of deep reading.

**Introduction Moves** (CARS model, Swales 2004):
| Move | Communicative Purpose | Steps | Para # |
|------|-----------------------|-------|--------|
| **M1**: Establishing a territory | Claim centrality, review prior research | Centrality → Topic generalization → Literature review | |
| **M2**: Establishing a niche | Identify the gap | Gap indication, counter-claiming, question-raising | |
| **M3**: Occupying the niche | Present paper as filling gap | Outlining purpose → Announcing findings → Indicating structure | |

**Methods Moves** (Kanoksilapatham 2005; Lim 2006):
| Move | Communicative Purpose | Para # |
|------|-----------------------|--------|
| **M4**: Describing data/materials | Data sources, composition, selection criteria | |
| **M5**: Describing procedures | Step-by-step method, algorithm, architecture | |
| **M6**: Describing evaluation | Metrics, baselines, statistical tests, validation | |

**Results Moves** (Ruiying & Allison 2003):
| Move | Communicative Purpose | Para # |
|------|-----------------------|--------|
| **M7**: Reporting results | Presenting overall → Highlighting specifics → Generalizing | |
| **M8**: Commenting on results | Interpreting → Comparing with prior work → Explaining → Noting limitations | |

**Discussion/Conclusion Moves** (Yang & Allison 2003):
| Move | Communicative Purpose | Para # |
|------|-----------------------|--------|
| **M9**: Reviewing present study | Restating purpose/methods → Summarizing findings | |
| **M10**: Evaluating findings | Stating significance → Suggesting applications | |
| **M11**: Addressing limitations | Acknowledging limitations → Proposing future directions | |

**After filling each section, answer:**
1. Which moves are OBLIGATORY? (all 3 papers)
2. Which moves are OPTIONAL? (1-2 papers)
3. What is the move SEQUENCE?
4. Where does our draft DEVIATE from the consensus?

---

## Pass 3: Critical Synthesis — FAT Analysis (per paper)

```markdown
### Pass 3: FAT Analysis

#### F — Facts (objective restatement, no judgment)
- **Research question**: [1 sentence]
- **Key findings** (the data, not interpretation): [bullets]
- **Method** in one paragraph: [concise but complete]
- **Claims made** by authors: [bullets — what they assert, not whether true]

#### A — Appreciation (critical evaluation)
- **Strengths** (2-3): [specific + why it matters]
- **Weaknesses/Limitations** (2-3): [specific + why it matters]
- **Novelty assessment**: [incremental or significant? reasoning]
- **Evidence quality**: [claims adequately supported? missing controls?]
- **Overall assessment**: Strong / Adequate / Weak

#### T — Tie (relevance to our paper)
- **What we should adopt**: [techniques, terminology, argument structures, figure styles]
- **What we should avoid**: [weaknesses, overclaims, unclear presentations]
- **How it positions our work**: [competitor, complement, predecessor, superset]
- **Action items for Round 1**: [concrete changes based on this paper]
```

---

## Cross-Paper Convention Synthesis

**Mandatory before Round 1.** Compare all 3 deep-read papers across 8 dimensions.

### 1-4. Section Conventions (Abstract, Introduction, Results, Discussion)

For each section, fill:
| Dimension | Paper 1 (SOTA) | Paper 2 (Prior) | Paper 3 (Adjacent) | **FIELD CONSENSUS** |
|-----------|---------------|-----------------|---------------------|---------------------|

### 5. NON-NEGOTIABLE RULES

List every convention shared by ALL 3 papers. These are hard constraints. **Each rule must be traceable to a specific observation in the tables above.**

### 6. Section Information Ceilings

Derived strictly from the most information-dense of the 3 papers:
- **Abstract ceiling**: most specific claim in any abstract
- **Introduction ceiling**: most specific claim in any introduction
- **Results floor**: minimum specificity in any Results section

### 7. Move Structure Consensus (from Template H)

| Section | Obligatory Moves (all 3) | Optional Moves (1-2) | Consensus Sequence |
|---------|-------------------------|----------------------|--------------------|
| Introduction | | | M1→M2→M3 |
| Methods | | | |
| Results | | | |
| Discussion | | | |

### 8. Cross-Paper Motivation Thread Analysis

For each paper, trace:
| Element | Paper 1 | Paper 2 | Paper 3 |
|---------|---------|---------|---------|
| One-sentence red thread | | | |
| Problem statement location | | | |
| Research question location | | | |
| How Methods justifies fitness | | | |
| Discussion opening (verbatim) | | | |
| Discussion closing (verbatim) | | | |
| Narrative storyline type | | | |

**Consensus motivation pattern**: Where do ALL 3 place their problem statement? How explicitly do they state the research question? Do they "close the circle" in Discussion?
