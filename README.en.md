# PaperSpine

[中文](README.md) | [English](README.en.md)

> 📢 **Maintenance paused (temporary) · 暂停维护**
> The author is heavily occupied and will be largely offline until **early July**. Issues / PRs / discussions may be delayed — queued, not ignored. Thanks for your patience 🙏
> 作者近期非常忙，**7 月初**前暂停日常维护，Issue / PR / 讨论会延迟回复，届时统一处理。感谢理解与支持 🙏


[**PaperSpine 使用讲解视频（Bilibili）**](https://www.bilibili.com/video/BV1rjVa6ZEYu)


PaperSpine is a motivation-driven paper and report writing skill suite for Codex, Claude Code, and OpenClaw.

It is designed for writing tasks where the target format matters: journal papers, conference papers, course or technical reports, reviews, and competition papers. The workflow asks the agent to learn the target scene and strong examples before writing, then records why each manuscript unit is planned or changed.

## Try It Online

Don't want to clone the repo, run `install.sh`, and restart Codex or Claude Code first? You can try a draft online: upload a paper draft, say whether it is a rewrite or a build-from-materials job and which venue you are targeting, and see the rewrite matrix and section blueprint PaperSpine produces. It is also easy to share with labmates — they just drop in their own draft to get results.

[![Try PaperSpine on Socialistic](https://socialistic.ai/api/embed/paperspine-paper-rewrite-suite-1668ae?lang=en)](https://socialistic.ai/skill/paperspine-paper-rewrite-suite-1668ae?utm_source=github&utm_medium=readme&utm_campaign=paperspine&utm_content=badge)

> The online entry is community-maintained; local installation below remains the source of truth.

## Repository Layout

```text
PaperSpine/
  dist/
    codex/
      skills/                   # Codex flat skill suite
      paper-spine/              # legacy Codex bundled fallback
    claude/
      skills/                   # Claude Code flat skill suite
        paper-spine/
        paper-spine-ui/
        paper-spine-intake/
        paper-spine-research/
        paper-spine-citation/
        paper-spine-rewrite/
        paper-spine-build/
        paper-spine-latex/
        paper-spine-audit/
        paper-spine-translate/
        paper-spine-humanize/
        paper-spine-update/
      commands/                 # Claude Code slash-command entry point
        paperspine.md
    openclaw/
      skills/                   # OpenClaw flat skill suite
  src/
    scripts/                    # shared deterministic helpers
    references/                 # shared workflow references
    agents/                     # shared agent metadata source
  .claude-plugin/               # Claude Code plugin metadata
  install.ps1                   # Windows installer
  install.sh                    # macOS / Linux installer
  README.md
  README.en.md
```

The `dist/` directory is the installable output. The `src/` directory keeps shared scripts and references readable for development.

## Quick Install

On Windows PowerShell:

```powershell
git clone https://github.com/WUBING2023/PaperSpine.git
cd PaperSpine
.\install.ps1 -Target all
```

Use a narrower target when needed:

```powershell
.\install.ps1 -Target codex
.\install.ps1 -Target claude
.\install.ps1 -Target openclaw
.\install.ps1 -Target all -CleanLegacy
```

`-CleanLegacy` removes common old PaperSpine folders that caused duplicate discovery, such as nested `PaperSpine`, `PaperSpineV2`, and old `paper-spine-*` copies.

After installing for Codex: **Restart Codex**. Then call the full workflow with `$paper-spine`, or call a branch such as `$paper-spine-research`, `$paper-spine-citation`, or `$paper-spine-latex`.

After installing for Claude Code: restart or reload Claude Code, then use `/paperspine`.

After installing for OpenClaw: restart or reload OpenClaw, then invoke `paper-spine` for the full workflow or any `paper-spine-*` branch skill for a single stage.

The installer writes the installed version to `~/.paperspine/install_state.json`
and preserves `~/.paperspine/config.json`, including UI language preferences.

## Manual Install

Codex now uses the same flat suite idea so each branch can be called directly:

```text
dist/codex/skills/*
```

Copy the folders to:

```text
~/.codex/skills/
```

The final Codex layout should be:

```text
~/.codex/skills/paper-spine/SKILL.md
~/.codex/skills/paper-spine-research/SKILL.md
~/.codex/skills/paper-spine-citation/SKILL.md
~/.codex/skills/paper-spine-latex/SKILL.md
~/.codex/skills/paper-spine-update/SKILL.md
```

`dist/codex/paper-spine` remains as a legacy bundled fallback for old installs,
but the recommended Codex install is `dist/codex/skills/*`.

Claude Code expects flat skill folders plus optional slash commands:

```text
dist/claude/skills/*
dist/claude/commands/*.md
```

Copy them to:

```text
~/.claude/skills/
~/.claude/commands/
```

The final Claude Code layout should include:

```text
~/.claude/skills/paper-spine/SKILL.md
~/.claude/skills/paper-spine-ui/SKILL.md
~/.claude/skills/paper-spine-intake/SKILL.md
~/.claude/skills/paper-spine-research/SKILL.md
~/.claude/skills/paper-spine-citation/SKILL.md
~/.claude/skills/paper-spine-update/SKILL.md
~/.claude/commands/paperspine.md
```

OpenClaw expects skill folders with `SKILL.md`:

```text
dist/openclaw/skills/*
```

Copy them to:

```text
~/.openclaw/skills/
```

The final OpenClaw layout should include:

```text
~/.openclaw/skills/paper-spine/SKILL.md
~/.openclaw/skills/paper-spine-research/SKILL.md
~/.openclaw/skills/paper-spine-citation/SKILL.md
~/.openclaw/skills/paper-spine-update/SKILL.md
```

## Claude Code Plugin Install

Claude Code can also use the plugin metadata in `.claude-plugin`.

```text
/plugin marketplace add https://github.com/WUBING2023/PaperSpine
/plugin install paper-spine
/reload-plugins
```

The plugin manifest points to the flat suite under `dist/claude/skills`, not to the Codex distribution.

## Codex vs Claude Code vs OpenClaw

| Host | Installable unit | Typical entry | Reason |
| --- | --- | --- | --- |
| Codex | `dist/codex/skills/*` | `$paper-spine` or `$paper-spine-*` | Codex can discover flat skill folders, so the full workflow and branch skills are both callable. |
| Claude Code | `dist/claude/skills/*` plus `dist/claude/commands/*` | `/paperspine` | Claude Code discovers skills as flat folders and supports slash-command helpers. |
| OpenClaw | `dist/openclaw/skills/*` | `paper-spine` or `paper-spine-*` | OpenClaw skills are directories containing `SKILL.md`, so the same flat suite is used. |

Do not copy the whole repository into a `skills` folder. That is the main cause of duplicated or missing skills.

## Main Workflow

PaperSpine has two equal first-class workflows:

1. **Rewrite Existing**: improve an existing manuscript without treating the task as simple polishing.
2. **Build From Materials**: build a manuscript or report from a folder containing notes, figures, PDFs, data summaries, partial drafts, and experiment descriptions.

Supported target scenes:

- `journal`: journal paper
- `conference`: conference paper
- `report/review`: course report, technical report, or review
- `competition`: competition paper or competition report

Research tiers:

- `flash`: 3 target-scene examples, 3 recent/high-quality same-field papers, and official requirements.
- `pro`: 6 target-scene examples, 6 recent/high-quality same-field papers, and official requirements.

Output languages:

- `English`
- `Chinese`

When English output is selected, PaperSpine can also generate a `translation_package` containing Chinese translations of intermediate artifacts and final Markdown outputs.

## Orchestrator And Branch Skills

PaperSpine is organized as one main orchestrator plus branch skills. The main
`paper-spine` skill routes the work stage by stage instead of directly patching
prose:

1. `paper-spine-ui`: opens the external terminal configuration UI.
2. `paper-spine-intake`: validates `paper_spine_config.json`.
3. `paper-spine-research`: learns the target scene, local/reference materials, and strong examples.
4. `paper-spine-citation`: builds a claim-level citation support bank.
5. `paper-spine-rewrite` or `paper-spine-build`: rewrites an existing manuscript or builds from materials.
6. `paper-spine-latex`: produces and checks LaTeX, PDF when possible, and optional Word output.
7. `paper-spine-audit`: checks completeness, rationale depth, citation bank quality, translation coverage, and artifact health.
8. `paper-spine-translate`: produces the complete `translation_zh/` package with row-by-row translation.
9. `paper-spine-update`: checks GitHub `main` for the latest PaperSpine version and updates local installs while preserving global config.

The same research, citation, rationale-matrix, LaTeX, translation, and audit
logic is shared by both `rewrite_existing` and `build_from_materials`.

Users can run the full workflow through `paper-spine`, or call only one branch:

- `paper-spine-ui`: configure a run.
- `paper-spine-intake`: validate or repair config.
- `paper-spine-research`: research target requirements and exemplar structure.
- `paper-spine-citation`: build the citation support bank only.
- `paper-spine-rewrite`: rewrite an existing manuscript using existing upstream artifacts.
- `paper-spine-build`: build from materials using existing upstream artifacts.
- `paper-spine-latex`: assemble/check LaTeX, PDF, and optional Word output.
- `paper-spine-translate`: produce the translation_zh/ package.
- `paper-spine-audit`: audit artifacts, translation coverage, and rationale depth.
- `paper-spine-update`: check or update the local PaperSpine installation.

## Updating PaperSpine

After the first install, use the update branch skill when you want to check for
new versions:

```text
$paper-spine-update
```

The update skill runs:

```powershell
python scripts/paperspine_update.py --yes
```

It compares the local version recorded in `~/.paperspine/install_state.json`
with the GitHub `main` manifest at `dist/paperspine_version.json`. If the local
copy is already current, it reports that no update is needed. If an update is
available, it downloads the GitHub archive, validates the PaperSpine layout,
updates Codex, Claude Code, and OpenClaw skill folders, and keeps
`~/.paperspine/config.json` intact.

For a non-mutating check:

```powershell
python scripts/paperspine_update.py --check-only
```

## Local Reference Reading

Reference collection is no longer network-only. The config field
`reference_mode` controls how PaperSpine starts literature and example reading:

- `local_first`: default. Index reference materials from the current working folder first, then supplement from the web when needed.
- `specified_paths`: index only the folders/files listed in `reference_paths`, then supplement according to the task.
- `web`: use web collection when the user has no local reference materials.

Local reference paths are written into:

```text
paper_rewriting_output/reference_materials/source_index.md
```

The helper script is:

```powershell
python src/scripts/reference_inventory.py . --output-dir paper_rewriting_output --mode local_first
```

PaperSpine may read user-provided PDFs, downloaded papers, BibTeX/RIS files,
templates, notes, and school or competition documents. It must not bypass
paywalls or private database access.

## Citation Support Bank

`paper-spine-citation` creates:

```text
paper_rewriting_output/citation_support_bank.md
```

This is separate from exemplar learning. Exemplar papers teach structure and
rhetoric; the citation support bank supplies candidate papers for Introduction,
Related Work, Discussion, limitations, applications, and background claims.

Default behavior:

- `citation_target_count`: `20`
- candidate pool: `citation_target_count * 3`, so the default is `60`
- recent-paper target: about `80%` of candidates should be from the last three years; in 2026 the simple threshold is 2023 or later
- each candidate row must include a reference/BibTeX-style entry, year, source, and one or two support sentences that can justify a manuscript statement

Check the bank with:

```powershell
python src/scripts/citation_bank_check.py paper_rewriting_output/citation_support_bank.md --target-count 20 --markdown
```

## Intake UI

Claude Code can launch the PaperSpine intake flow through:

```text
/paperspine
```

The command should launch the PaperSpine intake UI automatically when the host terminal allows it. The fallback is the Python wizard:

```powershell
python src/scripts/intake_wizard.py
```

The intake writes:

```text
paper_rewriting_output/paper_spine_config.json
paper_rewriting_output/paper_spine_config.md
```

## Required Artifacts

A complete PaperSpine run should produce a transparent audit trail, not just a final manuscript:

```text
paper_rewriting_output/
  paper_spine_config.json
  paper_spine_config.md
  reference_materials/
    source_index.md
  research_dossier.md
  exemplar_learning_dossier.md
  style_profile.md
  sota_gap_map.md
  motivation_options_after_research.md
  citation_support_bank.md
  confirmed_motivation.md
  source_inventory.md
  evidence_bank.md
  figure_asset_map.md
  claim_register.md
  section_blueprints.md
  writing_rationale_matrix.md
  rewrite_matrix.md
  logic_transfer_audit.md
  latex_report.md
  final_artifact_manifest.md
  final_paper/
    main.tex
    references.bib
    figures/
    paper.docx              # optional Word output
    paper.pdf               # generated when a LaTeX compiler is available
  translation_package/       # optional for English output
```

The central artifact is `writing_rationale_matrix.md`. It must explain the writing plan unit by unit: what the unit does, how it serves the confirmed motivation, what was learned from SOTA or target-scene examples, which evidence supports it, and what final text check should pass.

`citation_support_bank.md` is the second major reasoning artifact. It makes
every optional citation traceable to a concrete sentence-level claim before the
agent selects final references for the manuscript.

## Quality Checks

Run the artifact checker:

```powershell
python src/scripts/artifact_check.py paper_rewriting_output --markdown --write
```

For compatibility with copied skill scripts, the same command may appear in skill instructions as:

```powershell
python scripts/artifact_check.py paper_rewriting_output --markdown --write
```

Check LaTeX:

```powershell
python src/scripts/latex_guard.py paper_rewriting_output/final_paper/main.tex --markdown
```

Check Word output:

```powershell
python src/scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx --markdown
```

Check local reference indexing:

```powershell
python src/scripts/reference_inventory.py . --output-dir paper_rewriting_output --mode local_first
```

Check citation candidate coverage:

```powershell
python src/scripts/citation_bank_check.py paper_rewriting_output/citation_support_bank.md --target-count 20 --markdown
```

Run repository tests:

```powershell
python -m unittest discover -s tests
```

## What PaperSpine Tries To Prevent

- Direct sentence-by-sentence polishing with no logic change.
- Treating target journals, competitions, reports, and reviews as the same genre.
- Writing before confirming the motivation.
- Adding claims that are not supported by evidence.
- Producing only `main.tex` without explaining why the paper was written that way.
- Partial translation packages when the user requested translated intermediate and final artifacts.

## License

MIT License. See [LICENSE](LICENSE).

---

**Standalone download:** [paper-spine-humanize](https://github.com/WUBING2023/PaperSpine/tree/main/dist/claude/skills/paper-spine-humanize) — self-contained AI detection reduction skill, no dependencies on the full suite.
