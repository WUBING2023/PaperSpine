# Install PaperSpine V6

Choose one ZIP from the [V6 download page](https://wubing2023.github.io/PaperSpine/v6/en/).

| Edition | How to use it |
| --- | --- |
| Full Workflow Skill | Use `$paper-spine` in chat with your question, materials, or existing manuscript. |
| Skills Pack | Use `$paper-spine`, or call `$paper-spine-study`, `$paper-spine-followwriting`, `$paper-spine-figures`, `$paper-spine-review`, or `$paper-spine-deliver` on its own. |
| Web Plugin | On Windows x64 with Codex, install the Skills Pack and open the local workbench using `$paper-spine-web:paper-spine-web`. |

Download `checksums.sha256` from the same page. Extract the ZIP, open a terminal in the extracted folder, and run:

```text
python -B edition_manager.py install "<path to the original ZIP>" --sha256 <SHA256 from checksums.sha256>
```

The installer runs on Python 3.12 or later and defaults to the current Codex Skill directory. The Windows x64 workbench archive includes its own Python under `runtime/runtime_vendor/windows-py312/python.exe`. The Web plugin also requires the `codex` CLI. For Skill-compatible hosts, pass `--skills-root <path>` before `install`, or copy the contents of the ZIP's `skills/` directory into your host's Skill directory. Start a new conversation to discover the installed Skills. Managed updates apply to installer-managed copies.

If an old `paper-spine` occupies the selected directory, you can choose another Skill directory or pass `--archive-existing` to archive that old directory. Uninstall restores the archived Skill. V6 Web tasks use a separate default profile. Automatic migration of historical V5 profiles has not been verified. You can still use your old profile in V5 or provide its paper files to the V6 chat workflow.

The command reports the installation's manager path. Use that manager with `status`, `check`, `update`, `auto-update off`, `auto-update on`, `rollback`, or `uninstall`. For example:

```text
python -B "<manager path>" check
python -B "<manager path>" uninstall
```

Managed V6 installs select the V6 beta channel automatically. Checks run on invocation at an interval and can be disabled. The manager validates the package and switches the selected edition as a group. A running workbench can postpone an automatic update. Uninstall preserves paper files and workbench task data.
