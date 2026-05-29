# Orchestrator Branch Map

PaperSpine is a main-orchestrator workflow plus branch skills. The orchestrator
does not perform every operation itself; it calls branch skills in a fixed
order, verifies their artifacts, and routes back when a required artifact is
weak or missing.

## Branch Order

1. `paper-spine-ui`: open a real terminal UI window when configuration is
   missing or incomplete.
2. `paper-spine-intake`: write `paper_spine_config.json` and
   `paper_spine_config.md`.
3. `paper-spine-research`: ingest local references, collect official
   requirements, learn target examples/SOTA, and propose motivation options.
4. `paper-spine-citation`: build `citation_support_bank.md` for literature
   statements in Introduction/Discussion/background.
5. User confirmation: write `confirmed_motivation.md` only after the user
   chooses or revises the motivation.
6. `paper-spine-rewrite` or `paper-spine-build`: produce logic maps, evidence
   banks, section blueprints, and `writing_rationale_matrix.md`.
7. `paper-spine-latex`: assemble final LaTeX, optional PDF, and optional Word.
8. `paper-spine-audit`: check artifacts, rationale depth, citation bank,
   unsupported claims, translation coverage, LaTeX, and Word output.

## Loop Rule

If a branch output fails audit, route back to that branch. Do not patch the final
paper directly when the missing artifact should have been created earlier.

Examples:

- Missing local source paths: return to `paper-spine-research`.
- Too few citation candidates: return to `paper-spine-citation`.
- Shallow writing matrix: return to `paper-spine-rewrite` or
  `paper-spine-build`.
- Broken labels/citations in LaTeX: return to `paper-spine-latex`.
