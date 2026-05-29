---
name: paper-spine-ui
description: Launches the PaperSpine external terminal configuration UI for Codex and Claude Code.
---

# PaperSpine UI

Use this branch whenever `paper_spine_config.json` is missing, incomplete, or
the user asks to configure PaperSpine interactively.

## Required Behavior

The supported interaction is a real terminal window launched by
`scripts/launch_paperspine_ui.ps1`. Do not run `input()`-based Python inside a
hidden tool surface when the host cannot expose stdin.

In Claude Code, `/paperspine` must call this branch automatically when config is
missing. `/paperspine-legacy` is only a manual fallback.

In Codex, use the same launcher when PowerShell is available:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/launch_paperspine_ui.ps1 -OutputDir paper_rewriting_output
```

The UI writes:

```text
paper_rewriting_output/paper_spine_config.json
paper_rewriting_output/paper_spine_config.md
```

## UI Contract

- Open a separate interactive terminal window when possible.
- Provide a full-screen terminal UI when a real Windows terminal is available:
  centered welcome screen, white ridge wordmark, readable field/option panels,
  and a stable 30% field list plus 70% detail panel.
- Use Up/Down for field navigation, Left/Right for choice fields, Enter for
  text/list editing, `S` to save, and `Q` to quit.
- Show only one active field's reasoning and value details on the right panel;
  do not dump a long JSON-like checklist into the chat.
- Fall back to numbered terminal menus only when arrow-key UI is unavailable.
- Use chat questions only when terminal execution is impossible.
- Never require the user to manually write JSON.

Read `references/interactive-intake.md` for the question order and fallback
template.
