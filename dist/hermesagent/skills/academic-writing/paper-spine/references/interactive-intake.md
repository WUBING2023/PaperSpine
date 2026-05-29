# Interactive Intake

Use this reference when PaperSpine needs workflow configuration.

## Question Order

Ask these fields in order:

1. Workflow: `rewrite_existing` or `build_from_materials`.
2. Scene: `journal`, `conference`, `report_review`, or `competition`.
3. Tier: `flash` or `pro`.
4. Output language: `en` or `zh`.
5. Target name: journal, conference, course, report type, or competition name.
6. Draft path for `rewrite_existing`, or materials directory for
   `build_from_materials`.
7. User motivation, if known.
8. Official URLs, if known.
9. Special requirements.
10. Optional Word output: `none` or `docx`.
11. Optional translated artifact package for English output: `none` or `zh`.

## Supported Command-Line UI

Claude Code and Codex do not guarantee a native graphical picker for skills.
The supported PaperSpine UI is the bundled terminal wizard. In Claude Code, use
the `/paperspine` command when installed, or launch the PowerShell wrapper so
the wizard runs in a real interactive terminal window:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/launch_paperspine_ui.ps1 -OutputDir paper_rewriting_output
```

For a user-run terminal, the direct wizard command is:

```bash
python scripts/intake_wizard.py --output-dir paper_rewriting_output
```

Do not run the direct Python wizard inside a hidden agent Bash/tool execution
surface, because stdin may not be connected and the command can hang. The wizard
shows numbered menus, option descriptions, free-text fields, a final review
screen, and an edit loop before writing config files.

For first-time setup or changing interface language:

```bash
python scripts/intake_wizard.py --setup-global --output-dir paper_rewriting_output
```

Use native structured questions only when the host exposes them reliably in the
current session. The result must still be written to the same JSON/Markdown
config files.

## Last-Resort Chat Fallback

Use this only when neither terminal execution nor native structured questions
are available. Ask the user to paste this:

```text
workflow:
scene:
tier:
output_language:
target_name:
draft_path:
materials_dir:
user_motivation:
official_urls:
special_requirements:
word_output:
translation_package:
```

The JSON is the source of truth for later skills.
