# PaperSpine5 V5 0.4.0-alpha.4

This maintenance release fixes [#17](https://github.com/WUBING2023/PaperSpine/issues/17), which could prevent local paper delivery when independent review rounds reused a finding ID.

- Resolve a finding with `review_id` and `finding_id`. Existing callers can omit `review_id` when only one matching finding is open. When multiple matches are open, the response lists the rounds to choose from.
- Replay older resolutions, including those written by the reported local hotfix, against the first open matching finding in the historical submission order. The original task event log is retained.
- The installation guide now links the separate Windows installer and explains how to reuse an existing ZIP. [Issue #16](https://github.com/WUBING2023/PaperSpine/issues/16)

On Windows, download [`install.ps1`](https://github.com/WUBING2023/PaperSpine/releases/download/v0.4.0-alpha.4/install.ps1) separately. To install or repair offline, place the script, [`manifest.json`](https://github.com/WUBING2023/PaperSpine/releases/download/v0.4.0-alpha.4/manifest.json), and the Windows suite ZIP together. Run this in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -ManifestPath .\manifest.json -BundlePath .\paperspine5-suite-0.4.0-alpha.4.zip -Target codex
```

If you had a custom V5 profile, pass the same path with `-ProfileRoot`. Restart the workbench and reload the host Skill after updating. Existing users should check that the originally resolved findings are still resolved before continuing their paper. A current reader is required to interpret newly written scoped resolutions correctly.

此版本可在原 V5 profile 上升级。已修复多轮审稿复用编号造成的交付阻塞，并按原热修规则回放旧事件。Windows 安装脚本需单独下载，已下载 ZIP 的用户可直接使用上方离线命令。
