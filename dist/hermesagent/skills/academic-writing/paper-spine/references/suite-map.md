# Suite Map

PaperSpine is split into task-focused skills:

| Skill | Responsibility |
|---|---|
| `paper-spine` | route the workflow |
| `paper-spine-ui` | launch external terminal configuration UI |
| `paper-spine-intake` | collect configuration |
| `paper-spine-research` | index local references, research target scene, and learn examples |
| `paper-spine-citation` | build citation support candidates |
| `paper-spine-rewrite` | rewrite an existing draft |
| `paper-spine-build` | build from a materials folder |
| `paper-spine-latex` | assemble and guard LaTeX |
| `paper-spine-translate` | produce complete translation_zh/ with row-by-row translation |
| `paper-spine-humanize` | reduce AI detection patterns via tiered stylistic constraints |
| `paper-spine-audit` | check completeness, integrity audit, structured review, and translation coverage |
| `paper-spine-update` | check and update local PaperSpine installs |

Use the orchestrator for end-to-end tasks. Use a child skill directly when the
user asks for that stage only.
