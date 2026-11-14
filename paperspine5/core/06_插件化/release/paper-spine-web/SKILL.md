---
name: paper-spine-web
description: Open or resume the optional local PaperSpine workbench for a user who wants graphical configuration, contribution or figure choices, previews, downloads or feedback.
---

# PaperSpine Web workbench

Use the installed PaperSpine Skills Pack. Open the sibling `skills-root.json` in this plugin, follow its `skills_root`, and read `paper-spine/installation.json`. Use the manager path in that file. Run its `preflight` as described by the installed full-paper Skill. If it reports an update pending because Web is active, continue the current paper and let the user save their work before stopping or updating. Use the installed stage Skills for all research, Followwriting, figures, review and delivery.

Run the manager with `--skills-root "<skills_root>" web launch`. The result gives the local service and profile. Open or resume a task using the selected paper or user-supplied task ID. Use the public tools through `web host tools`, `web host snapshot` and `web host call` on the same manager and profile. Read [the existing task workflow](../../../01_PaperSpine4/src/skill/references/product-v1-workflow.md) for payload shapes and saved file handoffs. Substitute the manager's `web` command for the direct launcher in those instructions.

The host creates and recovers a task, verifies the material binding, proposes configuration and publishes real artifacts. Open the returned task URL once in the chosen browser. Use the saved configuration, motivations, figure choices and feedback to continue the same paper. Wait only for decisions needed by the next work. The workbench presents the files the stage Skills produce and returns the user's decisions; launching Web starts the local service.

If the user ends a Web session or requests maintenance, save current work before running `web stop`. When resuming without Web, use the actual paper files and saved decisions available to the host.
