# Intake Stage

Use the current conversation and paper files for chat intake. The saved
same-task configuration and public tools apply when the user selects Web.

## Purpose

Read the user's request and existing material roots, then propose a coherent,
editable configuration using `intent-configuration.md`. Reuse a confirmed current
configuration when resuming; a new workflow label does not erase valid choices.
For initial intake, establish the actual materials and authorized scientific work
in the chosen interface. Read back the saved result for Web tasks.

## Current output and scope

For Web use the public configuration schema, exported `01_configuration.json`
and material inventory. In chat, keep a short note when continuity needs it.
Preserve explicit language, target and output choices. Where the
request leaves an ordinary preference open, propose a suitable value and explain
it in the host handoff; do not infer author facts or external-action permissions.

For Web, `research_mode` defaults to `agent_decide`: decide and explain whether new analysis
is useful and feasible within the confirmed scope, then carry it out when chosen.
`required` means perform the requested research, with actual tools and evidence.
`materials_only` preserves supplied analyses and prohibits new analysis; it still
allows authorized public literature/venue learning and evidence-based writing.
Do not turn “materials supplied” or “draft first” into `materials_only`.

## Legacy configuration record (migration reference only)

Older tasks may retain these two files. They are not additional current outputs:

- `paper_rewriting_output/paper_spine_config.json`
- `paper_rewriting_output/paper_spine_config.md`

## Legacy config fields

| Field | Allowed Values | Default |
|---|---|---|
| `workflow` | `rewrite_existing`, `build_from_materials` | — |
| `scene` | `journal`, `conference`, `report_review`, `competition` | — |
| `tier` | `flash`, `pro` | `flash` |
| `output_language` | `en`, `zh` | `en` for journal/conference; `zh` for Chinese requests |
| `target_name` | free text | — |
| `materials_dir` | path or empty | — |
| `draft_path` | path or empty | — |
| `user_motivation` | free text or empty | — |
| `official_urls` | list | `[]` |
| `special_requirements` | list | `[]` |
| `word_output` | `none`, `docx` | `docx` |
| `translation_package` | `none`, `zh` | `none` |
| `reference_mode` | `local_first`, `specified_paths`, `web` | `local_first` |
| `reference_paths` | list of local paths | `["."]` |
| `citation_target_count` | integer | `20` |
| `author_voice_restoration` | `off`, `standard`, `strict` | `off` |
| `humanize_tier` | legacy compatibility: `none`, `light`, `medium`, `heavy` | `none` |
| `detection_platform` | legacy observation label only: `cnki`, `weipu`, `general` | `general` |
| `requested_scope` | `manuscript`, `local_delivery`, `submission_package` | `local_delivery` |
| `interaction.mode` | `guided`, `delegated_local_test` | `guided` |

`author_voice_restoration` enables the evidence-bound Authorial Voice
Restoration stage. The legacy `humanize_tier` values enable the same stage when
non-`none`; they no longer select sentence-burstiness targets, synonym
variation, or detector thresholds. `detection_platform` may label an external
observation supplied by the author, but it is never a readiness gate.

`tier` selects research/example breadth and optional process depth. It never
changes the requested deliverable type, necessary scientific argument, venue
structure, or manuscript length. A `flash` journal run still produces a full
journal manuscript; it simply researches fewer examples than `pro`.

`review_policy` selects review rigor and is not an autonomy permission. For old
`delegated_local_test`, collect one explicit initial authorization and construct
the exact typed grant described in `interaction-policy.md`. Bind it to the
current task, material snapshot, local requested scope, expiry, reversible
decision classes, authenticated host/user actor, and canonical hashes. Do not
accept a producer Boolean as user authority. Submission scope, author facts,
licences/fees, and external actions always remain human gates.

## Web workbench intake

- Use the same profile/task in the public Web workspace for normal intake.
- `launch_paperspine_ui.ps1` or `launch_paperspine_ui.sh` opens that workspace;
  the current host performs research. Launch success is not a Runner/Agent job.
- Host chat/typed questions are only for precise confirmations that the Web issue
  marks as requiring user authority; persist the answer through the same task API.
- `intake_wizard.py` is retained for historical migration and developer diagnostics,
  not as a supported user frontend or fallback.
- Never require the user to hand-write JSON.

## Scripts

```bash
python scripts/paperspine5_web.py launch --profile-root <existing-profile>
python scripts/paperspine5_web.py status --profile-root <existing-profile>
```
