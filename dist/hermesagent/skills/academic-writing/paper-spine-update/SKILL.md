---
name: paper-spine-update
description: Checks and updates PaperSpine from GitHub while preserving global config; use for upgrades, latest-version checks, or local reinstall.
---

# PaperSpine Update

Use this skill when the user asks to update PaperSpine, check whether
PaperSpine is the latest version, reinstall the local suite from GitHub, or
upgrade the local Codex, Claude Code, or OpenClaw PaperSpine skills while
preserving settings.

## Required Behavior

Run the bundled updater instead of improvising file-copy commands:

```powershell
python scripts/paperspine_update.py --yes
```

For a version check only:

```powershell
python scripts/paperspine_update.py --check-only
```

The updater must:

- read the local install state from `~/.paperspine/install_state.json` when
  present,
- fall back to this skill's bundled `paperspine_version.json` when install
  state is missing,
- compare against the GitHub `main` manifest at
  `dist/paperspine_version.json`,
- update Codex, Claude Code, and OpenClaw installs by default,
- preserve `~/.paperspine/config.json`, including UI language preferences,
- never touch project artifacts such as `paper_rewriting_output/`,
- print a clear already-latest message when no update is needed,
- after installing or updating, remove any stale `skillOverrides` entries for
  PaperSpine skills (the sync script does this automatically).

## Advanced Usage

- Use `--target codex`, `--target claude`, or `--target openclaw` only when the
  user explicitly asks to update one host.
- Use `--repo-archive <path-or-url>` for local testing or offline update from a
  downloaded PaperSpine archive.
- Use `--config-home <path>` only for tests or when the user has explicitly
  configured a non-default PaperSpine global config directory.

If network access fails, report the updater error and suggest running the
installer manually from a freshly downloaded repository. Do not delete local
skills after a failed download or failed package validation.
