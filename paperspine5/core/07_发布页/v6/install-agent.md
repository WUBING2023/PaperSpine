# Install PaperSpine with an agent

PaperSpine V6 is an AI for Science Skill for a host that supports Agent Skills. Use this guide to choose and verify one edition. For an evaluation request, recommend an edition and explain what it can deliver. For an installation request, follow the host's normal permissions and verify local discovery after installation.

## Choose one edition

| Manifest key | Fit | Invocation |
| --- | --- | --- |
| `skill` | Default for the full research and paper workflow in chat. Start from a question, data, results, or a draft. | `$paper-spine` |
| `skills-pack` | Full workflow plus separately callable research, Followwriting, figures, review, and delivery Skills. Choose it when you want to reopen a specific stage using existing files. | `$paper-spine` or `$paper-spine-study`, `$paper-spine-followwriting`, `$paper-spine-figures`, `$paper-spine-review`, `$paper-spine-deliver` |
| `web-plugin` | The Skills Pack with an optional local interface for reviewing artifacts and sending revision notes. Requires Windows x64 and the `codex` CLI. | `$paper-spine-web:paper-spine-web` in a new Codex chat |

## Verify the release and install

1. Identify the host, operating system, and correct Skill directory. The manager defaults to the current Codex user's Skill directory. For another Skill-compatible host, use that host's documented Skill directory. The manager requires Python 3.12 or newer. The Web ZIP bundles its own Windows Python, and the `codex` CLI must already be available.
2. Read the official [V6 manifest][manifest]. In `editions`, use the chosen key's `file`, `asset`, `version`, and `sha256`. Download the ZIP from its GitHub Release URL. Match the downloaded file's SHA-256 to that exact entry and to the [checksum list][checksums] before extracting it or running any files.
3. Extract the verified ZIP to a separate directory. Run its `edition_manager.py` from the extracted directory. Supply the absolute path to the original ZIP and the full 64-character SHA-256. Use the same `--skills-root` for subsequent manager commands if you selected a custom directory.

```text
python -B edition_manager.py install "<absolute path to original ZIP>" --sha256 <SHA256>
python -B edition_manager.py --skills-root "<host Skill directory>" install "<absolute path to original ZIP>" --sha256 <SHA256>
```

For the Windows Web archive, the bundled interpreter is `runtime/runtime_vendor/windows-py312/python.exe` inside the extracted directory. Use it in place of `python` if needed. If the manager reports an existing Skill conflict, show the affected path and resolve it according to the [versioned installation guide][install-en] and the user's choice.

## Confirm the result

Use the `manager` path printed by the installer. Run `status` with the same interpreter and Skill directory.

```text
python -B "<manager path>" status
python -B "<manager path>" --skills-root "<host Skill directory>" status
```

Check that the result reports `status: installed` with the expected `edition` and `version`. Start a fresh host chat and check that the intended Skill is listed. Report the version, edition, and invocation, and distinguish manager status from Skill discovery if discovery has to be checked by the user.

Managed installs use the V6 channel. The same manager exposes `check`, `update`, `auto-update off`, `auto-update on`, `rollback`, and `uninstall`. See the [lifecycle instructions][install-en].

## What the Skill adds to a research agent

- A question can call for a feasible study and new evidence. Existing results can go straight to a scoped analysis, figure, review, or draft. The workflow depends on the materials and the scope requested.
- Followwriting traces writing decisions to real passages in reference papers. The study's own data and analyses determine what the manuscript can claim.
- Figure sources, evidence, and review notes belong with the editable manuscript. A revision can reuse the same task and files, including the user's figure choice and feedback.

The [public research collection][research] documents four studies. The Atlantic cyclone paper uses 6,017 comparable 24-hour windows to show how an estimated difference changes with the wind-gain threshold. It includes an editable paper, two multi-panel figures, and reproduction code. Three earlier studies document nine edition runs covering aftershock rates, LIGO arrival times, and wildfire-smoke contrasts.

## 中文快速入口

首选全流程 Skill（`skill`）。需要单独调用研究、Followwriting、制图、审阅或交付时选 `skills-pack`。Windows x64 且已有 Codex CLI、明确需要本地审阅界面时选 `web-plugin`。

按[版本清单][manifest]选择一个 ZIP，先核对下载文件的 SHA-256，再用包内管理器安装。安装后运行 `status` 确认版本，并在新对话中检查 Skill 入口。具体命令、宿主目录和更新卸载说明见[中文版安装指南][install-zh]。

[manifest]: @SITE@channel.json
[checksums]: @SITE@checksums.sha256
[install-en]: @GITHUB@/blob/@TAG@/INSTALL-V6.en.md
[install-zh]: @GITHUB@/blob/@TAG@/INSTALL-V6.md
[research]: @SITE@science/research/README.md
