---
name: paper-spine-research
description: Researches target requirements, downloads reference materials, learns strong examples, and prepares motivation options.
---

# PaperSpine Research

Use this skill before motivation confirmation and before any scene-specific
writing. No target-scene research means no venue-specific writing advice.

Research runs in three stages: index locally, launch three parallel
specialist sub-agents, then merge findings into motivation options.

## Inputs

Read `paper_rewriting_output/paper_spine_config.json` when available. The
important fields are `scene`, `tier`, `target_name`, `official_urls`,
`materials_dir`, `draft_path`, `reference_mode`, `reference_paths`, and
`output_language`.

## Tier Rules

- `flash`: collect 3 target-scene examples and 3 recent high-quality field/SOTA
  examples.
- `pro`: collect 6 target-scene examples and 6 recent high-quality field/SOTA
  examples.

Users may override counts explicitly, but do not invent that override.

These learning examples are separate from `citation_support_bank.md`. Learning
examples teach structure and writing strategy. Citation-support papers support
individual literature statements later.

## Stage 1 — Index Local References (main thread)

Create the reference materials workspace:

```text
paper_rewriting_output/reference_materials/
  source_index.md
  official_requirements/
  target_examples/
  field_sota/
  templates/
  figures_images/
  extracted_notes/
```

Index all locally available references. Use `scripts/reference_inventory.py` or
produce the same `source_index.md` format:

| Source ID | Type | Title/Name | Origin/URL/Path | Why Included | Local File/Note | Used For |
|---|---|---|---|---|---|---|

Do NOT stop after indexing. Proceed immediately to Stage 2.

## Stage 2 — Parallel Specialist Agents

Launch the following **three sub-agents simultaneously** (single message, three
Agent tool calls). Each agent works independently and does not see the others'
outputs. Each agent is given only the context it needs — do not pass the full
conversation history.

### Agent A: Scene Analyst

**Goal:** Produce `paper_rewriting_output/research_dossier.md`

**Context to pass:**
- `scene`, `target_name`, `official_urls`, `output_language` from config
- `reference_materials/source_index.md` from Stage 1
- The scene-specific reference: `references/scenario-{journal|conference|report_review|competition}.md`

**Instructions:**
```
You are a Scene Analyst. Write research_dossier.md and stop.

LIMITS (must obey):
- Read the scene reference file, search official URLs at most TWICE
- Target output: 300-500 words total across 4 sections
- Do NOT enumerate every possible requirement — list only the top constraints
- Write the file immediately after gathering key facts, do NOT keep searching

Sections:
1. ## Venue Requirements — format rules (page limit, structure, anonymization)
2. ## Review Criteria — what reviewers evaluate
3. ## Accepted Paper Patterns — 1-2 structural patterns from scene reference
4. ## Constraints for This Paper

Output ONLY research_dossier.md. Do NOT produce other files.
```

### Agent B: Exemplar Learner

**Goal:** Produce `paper_rewriting_output/exemplar_learning_dossier.md`

**Context to pass:**
- `tier` from config (to know how many examples to analyze)
- `reference_materials/source_index.md` from Stage 1
- The scene scenario reference file path

**Instructions:**
```
You are an Exemplar Learner. Write exemplar_learning_dossier.md and stop.

LIMITS:
- Analyze at most 3 papers (flash) or 6 papers (pro) — do NOT exceed tier count
- For each paper: ONE paragraph summarizing structural patterns, NOT a full review
- Target output: 400-600 words total
- Write the file immediately after the last paper, do NOT keep adding

Sections:
1. ## Exemplar Inventory — table: title, venue, year, why selected
2. ## Structural Patterns — 2-3 reusable moves observed across exemplars
3. ## Rhetorical Patterns — 1-2 opening/closing techniques
4. ## Language Patterns — brief note on register and conventions

Output ONLY exemplar_learning_dossier.md. Do NOT copy claims/results.
```

### Agent C: SOTA Mapper

**Goal:** Produce `paper_rewriting_output/sota_gap_map.md`

**Context to pass:**
- `tier` from config
- `reference_materials/source_index.md` from Stage 1
- The user's `user_motivation` if set (treat as hypothesis, not confirmed)

**Instructions:**
```
You are a SOTA Mapper. Write sota_gap_map.md and stop.

LIMITS:
- Map at most 6 relevant SOTA papers — pick the most representative ones
- ONE line per paper in the table, do NOT write paragraphs per entry
- Target output: table with 4-6 rows + 2-3 gap summary lines
- If the user provided a motivation hypothesis, add it as ONE additional row

Table format:
| Candidate Contribution | What SOTA Already Does | User Evidence | Real Gap | Claim Strength | Risk |

Add a ## Gap Summary with the 2 most promising gaps. Output ONLY sota_gap_map.md.
```

### Agent launch checklist

- Launch all three in ONE message with three Agent tool calls.
- Each agent gets ONLY the context listed above — stripped-down, task-specific.
- Do NOT let agents see each other's instructions or outputs.
- All three write to `paper_rewriting_output/`.

## Stage 3 — Merge and Synthesize (main thread)

After all three agents complete, read their outputs and produce:

### style_profile.md

Merge exemplar language patterns with scene norms:

| Style Dimension | Target Venue Expectation | Exemplar Pattern | Applied To This Paper |
|---|---|---|---|

### motivation_options_after_research.md

Merge the dossier, exemplar analysis, and SOTA gap map into candidate
motivations:

| Option | One-Sentence Motivation | Core Innovation | Why It Is Not Overbroad | Required Evidence | Best-Fit Paper Arc |
|---|---|---|---|---|---|

Rules:
- Each option must be concise. Prefer one controlling contribution.
- If the real novelty is narrow, say so honestly.
- Cross-reference all three agents: a good motivation is one that fits the venue
  (Scene Analyst), follows exemplar structural patterns (Exemplar Learner),
  and occupies a real gap (SOTA Mapper).

### User Confirmation

Stop and present the motivation options to the user. Ask them to choose, revise,
or write their own. Only after confirmation, write `confirmed_motivation.md`:
- exact confirmed motivation,
- user confirmation status,
- rejected options and why,
- scope limits and forbidden overclaims.

## Required Outputs

- `paper_rewriting_output/reference_materials/source_index.md`
- `paper_rewriting_output/research_dossier.md`
- `paper_rewriting_output/exemplar_learning_dossier.md`
- `paper_rewriting_output/style_profile.md`
- `paper_rewriting_output/sota_gap_map.md`
- `paper_rewriting_output/motivation_options_after_research.md`
- `paper_rewriting_output/confirmed_motivation.md` only after user confirmation
