# PaperSpine Project Memory

## Project Purpose

PaperSpine is a motivation-driven paper and report writing skill suite (12 skills)
for Claude Code, Codex, OpenClaw, and HermesAgent.  The workflow researches the target scene,
confirms the controlling motivation with the user, builds a writing rationale
matrix, then writes/rewrites with LaTeX/PDF output.

## Repository Shape

- `dist/claude/skills/*`: Claude Code flat skill suite (12 skills)
- `dist/claude/commands/*.md`: Claude Code slash commands (3 commands)
- `dist/codex/skills/*`: Codex flat skill suite
- `dist/codex/paper-spine`: legacy Codex bundled fallback
- `dist/openclaw/skills/*`: OpenClaw flat skill suite
- `dist/hermesagent/skills/academic-writing/*`: HermesAgent default-category skill suite
- `src/scripts/*`: shared deterministic scripts (standard library only)
- `.claude-plugin/*`: Claude Code plugin metadata
- `tests/*`: 134 tests

## Suite Skills

- `paper-spine`: orchestrator
- `paper-spine-ui`: terminal configuration TUI
- `paper-spine-intake`: config collection
- `paper-spine-research`: target scene + exemplar learning (3-agent parallel)
- `paper-spine-citation`: citation support bank + quality audit
- `paper-spine-rewrite`: rewrite existing drafts
- `paper-spine-build`: build from materials
- `paper-spine-humanize`: AI detection reduction via tiered constraints
- `paper-spine-latex`: LaTeX/PDF/Word assembly
- `paper-spine-translate`: translation_zh/ package
- `paper-spine-audit`: integrity audit + structured review + artifact check
- `paper-spine-update`: check/update from GitHub

## Version

Canonical source: `dist/paperspine_version.json`.  Auto-propagated to
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` via
`sync_version_from_canonical()` in sync script.

## Development Rules

- Standard library only for Python scripts
- Keep dist copies synchronized across Claude/Codex/OpenClaw/HermesAgent
- README.md and README.zh-CN.md must stay content-equivalent
- Do not push to GitHub unless explicitly asked
- Run `python -m pytest tests` before claiming ready (expect 134 passed)

## Sync Commands

```powershell
# Project-internal dist sync (fast, without install targets)
python src/scripts/sync_local_installs.py --dist-only

# Full sync to install directories
python src/scripts/sync_local_installs.py --clean-legacy
```
