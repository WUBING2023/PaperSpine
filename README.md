# PaperSpine V6

[中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [Português](README.pt.md)

[V6 官网与下载](https://wubing2023.github.io/PaperSpine/v6/) · [安装、更新与卸载](INSTALL-V6.md) · [GitHub Release](https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2)

在对话里使用 `$paper-spine`，从研究问题、结果或稿件推进到可编辑论文。V6 有全流程 Skill、独立阶段 Skills 包和可选的 Web 插件三种下载。

阶段 Skills 覆盖研究、Followwriting 写作、科研制图、审阅和交付。Web 插件当前支持 Windows x64 Codex。安装器内置 V6 更新频道，可整包更新、回退和卸载。

<details>
<summary>V5 使用与安装说明</summary>

## 社区星图

<p align="center">
  <a href="https://wubing2023.github.io/PaperSpine/v5/community/">
    <img src="website/assets/community-atlas-preview.png" alt="PaperSpine 公开 GitHub Stargazer 社区星图">
  </a>
</p>

上图是公开 GitHub Stargazer 自报地理位置与机构信息的预览快照。它反映公开社区分布，不代表安装量、活跃用户、论文数量、产品能力或机构采用。点击图片可打开[每日刷新的可交互社区星图](https://wubing2023.github.io/PaperSpine/v5/community/)。

## 下载

- Windows x64 套件：约 26.5 MB。
- Linux glibc x86_64 套件：约 56.2 MB。
- macOS Apple Silicon 套件：约 40.6 MB。
- macOS Intel x86_64 套件：约 40.5 MB。

所有下载都列在公开发布清单中，并用 SHA-256 校验。完整版本号为 `v0.4.0-alpha.3` 预发布。

<details>
<summary>高级 / 手动安装</summary>

当前发布仅提供四个平台的完整套件。历史约 0.70 MB 的 Skill-only ZIP 不含 Web 核心与运行时，不能用于首次安装或修复缺失套件指针。高级用户可从已验证的完整套件管理 Skill。

</details>

## 安装与旧版本迁移

Windows x64：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target codex -CleanLegacy
```

macOS / Linux：

```sh
sh ./install.sh --target codex --clean-legacy
```

`-CleanLegacy` 先只读预览，仅在发现旧版冲突时写归档；不删除论文任务数据、宿主设置或未知文件。两个平台安装器都会校验字节数、SHA-256、套件内部完整性和首次启动自检。

## 检查与应用更新

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

重新运行安装器会检查版本：有新版时执行可回滚更新，保留任务数据并做启动自检；已是最新版且 Skill 完整时直接继续，不重复下载或覆盖。每次调用 Skill 时检查更新，有新版则自动升级完整套件和更新器；尊重明确关闭自动更新的设置。

## 边界

- 四个平台套件均已通过归档和 SHA-256 校验。Windows x64 已通过本地安装、更新和工作台验证；[发版后原生 CI](https://github.com/WUBING2023/PaperSpine/actions/runs/35944185453) 在 Windows、Linux x86_64、macOS arm64 和 macOS x86_64 均通过旧更新器升级与工作台启动。Linux arm64、musl/Alpine 未声明支持。
- macOS 套件尚未签名或公证，首次运行可能需要用户明确允许。
- 当前为 alpha 预发布，无独立密码学签名。
- 产品发布不授权投稿、上传私有材料、付款或外部联系。
- 支持入口是自愿维护支持，不解锁功能，不读取支付状态。

## 公开仓库结构

- `dist/codex/skills/paper-spine`、`dist/claude/skills/paper-spine`、`dist/openclaw/skills/paper-spine`：宿主投影。
- `dist/claude/commands/paperspine.md`：Claude 命令入口。
- `install.ps1`、`install.sh`：安装边界。
- 关键方法/工具：`writing_rationale_matrix`、`citation_support_bank`、`translation_package`、`artifact_check.py`、`reference_inventory.py`、`citation_bank_check.py`、`latex_guard.py`、`word_guard.py`。

## 开发

`src/` 存放 Skill 源代码，`dist/` 是各宿主的公开投影。公开仓库保留源代码和测试，不保留本地任务、临床数据、缓存或开发运行日志。

MIT License。

</details>
