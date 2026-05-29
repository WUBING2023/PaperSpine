---
name: paper-spine-intake
description: Collects PaperSpine workflow options and writes config for flash/pro, scene, language, and inputs.
---

# PaperSpine Intake

Use this skill before substantive PaperSpine work when the workflow is not yet
configured.

## Required Output

Create:

- `paper_rewriting_output/paper_spine_config.json`
- `paper_rewriting_output/paper_spine_config.md`

The JSON must contain:

```json
{
  "workflow": "rewrite_existing",
  "scene": "journal",
  "tier": "flash",
  "output_language": "en",
  "target_name": "",
  "materials_dir": "",
  "draft_path": "",
  "user_motivation": "",
  "official_urls": [],
  "special_requirements": [],
  "word_output": "none",
  "translation_package": "none",
  "reference_mode": "local_first",
  "reference_paths": ["."],
  "citation_target_count": 20
}
```

Allowed values:

- `workflow`: `rewrite_existing`, `build_from_materials`
- `scene`: `journal`, `conference`, `report_review`, `competition`
- `tier`: `flash`, `pro`
- `output_language`: `en`, `zh`
- `word_output`: `none`, `docx`
- `translation_package`: `none`, `zh`; use `zh` only when
  `output_language` is `en`
- `reference_mode`: `local_first`, `specified_paths`, `web`
- `reference_paths`: local folders/files to index for references; default `.`
- `citation_target_count`: final intended citation count; default `20`

## Interaction Rules

The command-line wizard is the supported UI for Claude Code and Codex CLI.
When a real terminal is available, route through `paper-spine-ui` and use the
bundled external terminal wizard; do not downgrade to asking the user to
hand-write JSON or type every option in chat.

In Claude Code, do not run `python scripts/intake_wizard.py` directly from an
agent Bash/tool call. That execution surface may not expose stdin and can hang.
Use `/paperspine` for normal work; it launches this intake UI automatically
when configuration is missing. The UI is a real terminal TUI with Up/Down option switching,
Left/Right field switching, Enter edit/confirm, and `S` save. Claude Code does
not currently expose a public third-party skill API for embedding this custom
keyboard UI inside the chat input box itself. If needed, run the launcher
relative to this skill directory:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/launch_paperspine_ui.ps1 -OutputDir paper_rewriting_output
```

This opens a separate interactive PowerShell window. For a user-run terminal,
this direct command is also supported:

```bash
python scripts/intake_wizard.py --output-dir paper_rewriting_output
```

The wizard provides arrow-key menus in a real terminal, falls back to numbered
menus when needed, shows descriptions for each option, runs a final review
screen and edit loop, and writes both JSON and Markdown config.

Use native structured questions only if the host exposes them reliably in the
current session. If neither terminal execution nor native questions are
available, then and only then ask the user to answer with the fallback template.

Read `references/interactive-intake.md` for the exact question order and
fallback template.

## Defaults

- `journal` and `conference` default to `en`.
- Chinese course, Chinese competition, and explicit Chinese writing requests
  default to `zh`.
- If the user has a draft, choose `rewrite_existing`.
- If the user has a folder of experiment settings, results, figures, notes,
  PDFs, Word files, or reports, choose `build_from_materials`.
- If the user does not choose tier, default to `flash`.
- If the user does not request Word output, default `word_output` to `none`.
- If the paper is English, offer `translation_package: zh` as an optional
  Chinese reading package for intermediate artifacts and final structure.
- Default `reference_mode` to `local_first`.
- Default `reference_paths` to `["."]` unless the user provides paths.
- Default `citation_target_count` to `20`.

## Global UI Language

On first setup, or when the user asks to change PaperSpine interface language,
run the wizard in global setup mode:

```bash
python scripts/intake_wizard.py --setup-global --output-dir paper_rewriting_output
```

Use the wizard's terminal UI for all config fields. Prefer the arrow-key UI in a
real terminal; use numbered command-line menus as fallback. Avoid asking the
user to manually type JSON/options unless terminal execution is impossible.

