# PaperSpine V6

[中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [Português](README.pt.md)

[V6 site and downloads](https://wubing2023.github.io/PaperSpine/v6/en/) · [Install, update, and uninstall](INSTALL-V6.en.md) · [GitHub Release](https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2)

Use `$paper-spine` in chat to work on a paper from a question, results, or a draft. V6 offers a full-workflow Skill, a modular Skills Pack, and an optional Web plugin.

Research, Followwriting, figures, review, and delivery can run independently. The Web plugin supports Windows x64 with Codex. The installer uses the V6 update channel and supports rollback and uninstall.

<details>
<summary>V5 usage and installation</summary>

## Community atlas

<p align="center">
  <a href="https://wubing2023.github.io/PaperSpine/v5/community/en.html">
    <img src="website/assets/community-atlas-preview.png" alt="PaperSpine public GitHub Stargazer community atlas">
  </a>
</p>

The image is a preview snapshot of self-reported locations and affiliations from public GitHub Stargazers. It shows public community distribution, not installs, active users, papers, product capabilities, or institutional adoption. Click it to open the [daily-refreshed interactive community atlas](https://wubing2023.github.io/PaperSpine/v5/community/en.html).

## Downloads

- Windows x64 suite: about 26.5 MB.
- Linux glibc x86_64 suite: about 56.2 MB.
- macOS Apple Silicon suite: about 40.6 MB.
- macOS Intel x86_64 suite: about 40.5 MB.

Every download is listed in the public release list and verified with SHA-256. Current version: `v0.4.0-alpha.3` prerelease.

<details>
<summary>Advanced / manual install</summary>

This release offers only the four full platform suites. The historical Skill-only ZIP has no Web core or runtime and cannot repair a missing suite pointer. Advanced users can manage the Skill from a verified full suite.

</details>

## Install and archive V3/V4 discovery conflicts

Windows x64:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target codex -CleanLegacy
```

macOS / Linux:

```sh
sh ./install.sh --target codex --clean-legacy
```

`-CleanLegacy` archives only known V3/V4 Skill discovery folders. It does not delete paper tasks, host settings, or unknown files. Both platform installers check the byte count, SHA-256, suite integrity, and a startup self-check.

## Check and apply updates

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File .\install.ps1 -CheckOnly
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target codex
```

```sh
# macOS / Linux
sh ./install.sh --check-only
sh ./install.sh --target codex
```

Rerunning the installer checks the version: it applies a rollback-safe update and startup check when a newer version is available, preserving task data. A complete current installation skips downloads and overwrites. Each Skill invocation checks for updates and upgrades the full suite and updater when needed; an explicit opt-out is respected.

## Boundaries

- All four suites passed archive and SHA-256 verification. Windows x64 passed local installation, update, and workspace checks; [post-release native CI](https://github.com/WUBING2023/PaperSpine/actions/runs/35944185453) passed old-updater upgrades and workspace startup on Windows, Linux x86_64, macOS arm64, and macOS x86_64. Linux arm64 and musl/Alpine are not claimed.
- macOS packages are not signed or notarized; first launch may require explicit user approval.
- This is an alpha prerelease without an independent cryptographic signature.
- Publishing the product never authorizes manuscript submission, private-data upload, payment, or external contact.
- The support surface is voluntary, unlocks no feature, and reads no payment state.

## Public repository layout

- `dist/codex/skills/paper-spine`, `dist/claude/skills/paper-spine`, and `dist/openclaw/skills/paper-spine`: host projections.
- `dist/claude/commands/paperspine.md`: Claude command entry.
- `install.ps1` and `install.sh`: installation boundaries.
- Key methods/tools: `writing_rationale_matrix`, `citation_support_bank`, `translation_package`, `artifact_check.py`, `reference_inventory.py`, `citation_bank_check.py`, `latex_guard.py`, and `word_guard.py`.

## Development

`src/` holds the Skill source code and `dist/` holds the public host projections. The public repository keeps source and tests, not local tasks, clinical data, caches, or development run logs.

MIT License.

</details>
