# PaperSpine

[English](README.md) | [中文](README.zh-CN.md)

> 英文 README 和中文 README 作为内容等价版本维护。任意一边更新时，另一边也需要在同一次提交中同步更新。

PaperSpine 是一个面向 Codex、Claude Code、OpenClaw 和 HermesAgent 的、以 motivation 为主线的论文与报告写作 skill suite。

它适合目标格式很重要的写作任务：期刊论文、会议论文、课程或技术报告、综述、竞赛论文。它要求 agent 在写作前先学习目标场景和优秀样例，再记录每一个写作单元为什么这样规划或修改。

## 仓库结构

```text
PaperSpine/
  dist/
    codex/
      skills/                   # Codex 扁平 skill suite
      paper-spine/              # 旧版 Codex 自包含兼容包
    claude/
      skills/                   # Claude Code 扁平 skill suite
        paper-spine/
        paper-spine-ui/
        paper-spine-intake/
        paper-spine-research/
        paper-spine-citation/
        paper-spine-rewrite/
        paper-spine-build/
        paper-spine-latex/
        paper-spine-audit/
        paper-spine-translate/
        paper-spine-humanize/
        paper-spine-update/
      commands/                 # Claude Code slash-command 辅助入口
        paperspine.md
        paper-spine.md
        paperspine-legacy.md
    openclaw/
      skills/                   # OpenClaw 扁平 skill suite
    hermesagent/
      skills/
        academic-writing/        # HermesAgent 默认分类 skill suite
  src/
    scripts/                    # 共享的确定性辅助脚本
    references/                 # 共享工作流参考文档
    agents/                     # 共享 agent 元数据源
  .claude-plugin/               # Claude Code 插件元数据
  install.ps1                   # Windows 安装脚本
  install.sh                    # macOS / Linux 安装脚本
  README.md
  README.zh-CN.md
```

`dist/` 是真正用于安装的内容。`src/` 保留共享脚本和参考文档，便于开发与维护。

## 快速安装

Windows PowerShell:

```powershell
git clone https://github.com/WUBING2023/PaperSpine.git
cd PaperSpine
.\install.ps1 -Target all
```

也可以只安装某一端：

```powershell
.\install.ps1 -Target codex
.\install.ps1 -Target claude
.\install.ps1 -Target openclaw
.\install.ps1 -Target hermesagent
.\install.ps1 -Target all -CleanLegacy
```

`-CleanLegacy` 会清理常见的旧 PaperSpine 目录，例如嵌套的 `PaperSpine`、`PaperSpineV2` 和旧的 `paper-spine-*` 副本，避免重复发现或找不到 skill。

安装到 Codex 后：**Restart Codex**。然后用 `$paper-spine` 启动全流程，或单独调用 `$paper-spine-research`、`$paper-spine-citation`、`$paper-spine-latex` 等分支 skill。

安装到 Claude Code 后：重启或 reload Claude Code，然后使用 `/paperspine`。

安装到 OpenClaw 后：重启或 reload OpenClaw，然后用 `paper-spine` 启动全流程，或调用任意 `paper-spine-*` 分支 skill。

安装到 HermesAgent 后：重启或 reload HermesAgent，然后用 `/paper-spine` 启动全流程，或调用任意 `/paper-spine-*` 分支 skill。

安装脚本会把当前版本记录到 `~/.paperspine/install_state.json`，并保留 `~/.paperspine/config.json`，包括 UI 语言等全局配置。

## 手动安装

Codex 现在推荐使用扁平 suite，这样每个分支都可以被单独调用：

```text
dist/codex/skills/*
```

复制到：

```text
~/.codex/skills/
```

最终 Codex 布局应该是：

```text
~/.codex/skills/paper-spine/SKILL.md
~/.codex/skills/paper-spine-research/SKILL.md
~/.codex/skills/paper-spine-citation/SKILL.md
~/.codex/skills/paper-spine-latex/SKILL.md
~/.codex/skills/paper-spine-update/SKILL.md
```

`dist/codex/paper-spine` 仍保留为旧版自包含兼容包，但推荐的新安装方式是 `dist/codex/skills/*`。

Claude Code 需要扁平 skill 文件夹和可选 slash commands：

```text
dist/claude/skills/*
dist/claude/commands/*.md
```

复制到：

```text
~/.claude/skills/
~/.claude/commands/
```

最终 Claude Code 布局应该包含：

```text
~/.claude/skills/paper-spine/SKILL.md
~/.claude/skills/paper-spine-ui/SKILL.md
~/.claude/skills/paper-spine-intake/SKILL.md
~/.claude/skills/paper-spine-research/SKILL.md
~/.claude/skills/paper-spine-citation/SKILL.md
~/.claude/skills/paper-spine-update/SKILL.md
~/.claude/commands/paperspine.md
```

OpenClaw 需要包含 `SKILL.md` 的 skill 文件夹：

```text
dist/openclaw/skills/*
```

复制到：

```text
~/.openclaw/skills/
```

最终 OpenClaw 布局应该包含：

```text
~/.openclaw/skills/paper-spine/SKILL.md
~/.openclaw/skills/paper-spine-research/SKILL.md
~/.openclaw/skills/paper-spine-citation/SKILL.md
~/.openclaw/skills/paper-spine-update/SKILL.md
```

HermesAgent 需要把 skill 文件夹放在默认 skill 根目录的分类目录下：

```text
dist/hermesagent/skills/academic-writing/*
```

复制到：

```text
~/.hermes/skills/academic-writing/
```

最终 HermesAgent 布局应该包含：

```text
~/.hermes/skills/academic-writing/paper-spine/SKILL.md
~/.hermes/skills/academic-writing/paper-spine-research/SKILL.md
~/.hermes/skills/academic-writing/paper-spine-citation/SKILL.md
~/.hermes/skills/academic-writing/paper-spine-update/SKILL.md
```

## Claude Code 插件安装

Claude Code 也可以使用 `.claude-plugin` 中的插件元数据：

```text
/plugin marketplace add https://github.com/WUBING2023/PaperSpine
/plugin install paper-spine
/reload-plugins
```

插件 manifest 指向 `dist/claude/skills` 下的扁平 suite，而不是 Codex 的单 skill 目录。

## Codex、Claude Code、OpenClaw 与 HermesAgent 的差异

| 宿主 | 安装单元 | 常用入口 | 原因 |
| --- | --- | --- | --- |
| Codex | `dist/codex/skills/*` | `$paper-spine` 或 `$paper-spine-*` | Codex 可以发现扁平 skill 文件夹，因此全流程和子 skill 都能调用。 |
| Claude Code | `dist/claude/skills/*` 加 `dist/claude/commands/*` | `/paperspine` | Claude Code 按扁平文件夹发现 skills，并支持 slash-command 辅助入口。 |
| OpenClaw | `dist/openclaw/skills/*` | `paper-spine` 或 `paper-spine-*` | OpenClaw skill 也是包含 `SKILL.md` 的目录，因此使用同一套扁平 suite。 |
| HermesAgent | `dist/hermesagent/skills/academic-writing/*` | `/paper-spine` 或 `/paper-spine-*` | HermesAgent 按默认的 `~/.hermes/skills/<category>/` 布局发现包含 `SKILL.md` 的技能目录。 |

不要把整个仓库直接复制进 `skills` 文件夹。这是重复或缺失 skill 的主要原因。

## 主工作流

PaperSpine 有两条平级主流程：

1. **Rewrite Existing**：改进已有论文或报告，但不把任务降级成简单润色。
2. **Build From Materials**：从素材文件夹构筑论文或报告，素材可以包括说明文档、图片、PDF、数据摘要、部分初稿和实验描述。

支持四类目标场景：

- `journal`：期刊论文
- `conference`：会议论文
- `report/review`：课程报告、技术报告或综述
- `competition`：竞赛论文或竞赛报告

研究深度：

- `flash`：3 篇目标场景样例、3 篇近期/高质量同领域论文和官方要求。
- `pro`：6 篇目标场景样例、6 篇近期/高质量同领域论文和官方要求。

输出语言：

- `English`
- `Chinese`

选择英文输出时，PaperSpine 还可以生成 `translation_package`，把中间产物和最终 Markdown 产物翻译为中文。

## 主控与分支 Skill

PaperSpine 由一个主控 skill 加多个分支 skill 组成。主控 `paper-spine` 不直接修补句子，而是逐阶段路由：

1. `paper-spine-ui`：打开外部终端配置 UI。
2. `paper-spine-intake`：校验 `paper_spine_config.json`。
3. `paper-spine-research`：学习目标场景、本地/指定参考资料和优秀样例。
4. `paper-spine-citation`：构建逐句 claim 级别的引用支持库。
5. `paper-spine-rewrite` 或 `paper-spine-build`：改写已有论文，或从素材构筑论文。
6. `paper-spine-latex`：生成并检查 LaTeX、可用时生成 PDF，并处理可选 Word 输出。
7. `paper-spine-audit`：检查产物完整性、写作思路深度、引用库质量、翻译覆盖率和文件健康度。
8. `paper-spine-translate`：产出完整的 `translation_zh/` 翻译包，含逐行翻译。
9. `paper-spine-update`：检查 GitHub `main` 上的最新版，并在保留全局配置的前提下更新本地安装。

`rewrite_existing` 和 `build_from_materials` 共用研究、引用、写作思路矩阵、LaTeX、翻译和审计逻辑。

用户可以通过 `paper-spine` 运行全流程，也可以只调用某一个分支：

- `paper-spine-ui`：配置一次运行。
- `paper-spine-intake`：校验或修复配置。
- `paper-spine-research`：调研目标要求和优秀样例结构。
- `paper-spine-citation`：只构建引用支持库。
- `paper-spine-rewrite`：基于上游产物改写已有论文。
- `paper-spine-build`：基于上游产物从素材构筑论文。
- `paper-spine-latex`：组装/检查 LaTeX、PDF 和可选 Word。
- `paper-spine-translate`：产出 translation_zh/ 翻译包。
- `paper-spine-audit`：审计产物、翻译覆盖和写作思路深度。
- `paper-spine-update`：检查或更新本地 PaperSpine 安装。

## 更新 PaperSpine

第一次安装之后，如果想检查新版本，可以单独调用更新分支 skill：

```text
$paper-spine-update
```

更新 skill 会运行：

```powershell
python scripts/paperspine_update.py --yes
```

它会把本地 `~/.paperspine/install_state.json` 中记录的版本和 GitHub `main` 分支的 `dist/paperspine_version.json` 进行比较。如果已经是最新版，会直接提示无需更新。如果发现新版本，会下载 GitHub 压缩包，校验 PaperSpine 目录结构，然后同步更新 Codex、Claude Code、OpenClaw 和 HermesAgent 的 skill 文件夹，并保留 `~/.paperspine/config.json`。

如果只想检查而不修改本地安装，可以运行：

```powershell
python scripts/paperspine_update.py --check-only
```

## 本地参考文献读取

参考材料获取不再只依赖网络。配置字段 `reference_mode` 控制 PaperSpine 如何开始文献和样例读取：

- `local_first`：默认模式。先索引当前工作文件夹中的参考材料，再按需进行网络补充。
- `specified_paths`：只索引 `reference_paths` 中指定的文件夹或文件，再按任务需要补充。
- `web`：用户没有本地参考材料时使用网络收集。

本地参考路径会写入：

```text
paper_rewriting_output/reference_materials/source_index.md
```

辅助脚本：

```powershell
python src/scripts/reference_inventory.py . --output-dir paper_rewriting_output --mode local_first
```

PaperSpine 可以读取用户提供的 PDF、下载论文、BibTeX/RIS、模板、笔记、学校或竞赛文档。它不能绕过付费墙或私有数据库权限。

## 引用支持库

`paper-spine-citation` 会生成：

```text
paper_rewriting_output/citation_support_bank.md
```

它和优秀论文学习是两件事。样例论文用于学习结构和写法；引用支持库用于为 Introduction、Related Work、Discussion、局限性、应用背景等位置提供可选择的候选引用。

默认行为：

- `citation_target_count`: `20`
- 候选池：`citation_target_count * 3`，默认是 `60`
- 近期论文目标：约 `80%` 候选应来自近三年；在 2026 年，简单阈值是 2023 年及以后
- 每一行候选都必须包含参考文献/BibTeX 风格信息、年份、来源，以及一两句可以支撑正文论述的句子

检查引用库：

```powershell
python src/scripts/citation_bank_check.py paper_rewriting_output/citation_support_bank.md --target-count 20 --markdown
```

## 配置 UI

Claude Code 推荐使用：

```text
/paperspine
```

当宿主终端允许时，这个命令会自动启动 PaperSpine intake UI。兜底方式是 Python wizard：

```powershell
python src/scripts/intake_wizard.py
```

配置完成后会生成：

```text
paper_rewriting_output/paper_spine_config.json
paper_rewriting_output/paper_spine_config.md
```

## 关键产物

一次完整运行不应该只有最终论文，而应该留下完整的可审计写作轨迹：

```text
paper_rewriting_output/
  paper_spine_config.json
  paper_spine_config.md
  reference_materials/
    source_index.md
  research_dossier.md
  exemplar_learning_dossier.md
  style_profile.md
  sota_gap_map.md
  motivation_options_after_research.md
  citation_support_bank.md
  confirmed_motivation.md
  source_inventory.md
  evidence_bank.md
  figure_asset_map.md
  claim_register.md
  section_blueprints.md
  writing_rationale_matrix.md
  rewrite_matrix.md
  logic_transfer_audit.md
  latex_report.md
  final_artifact_manifest.md
  final_paper/
    main.tex
    references.bib
    figures/
    paper.docx              # 可选 Word 输出
    paper.pdf               # 本机有 LaTeX 编译器时生成
  translation_package/       # 英文输出时可选
```

最核心产物是 `writing_rationale_matrix.md`。它必须按照真实论文或报告结构逐单元解释：该单元承担什么功能，如何服务确认后的 motivation，学习了哪些 SOTA 或目标场景样例，使用了哪些证据，最终文本应通过什么检查。

`citation_support_bank.md` 是第二个重要推理产物。它让每个候选引用在进入正文前，都先绑定到一个具体句子级 claim。

## 检查命令

检查产物完整性：

```powershell
python src/scripts/artifact_check.py paper_rewriting_output --markdown --write
```

复制到 skill 内部后，也可能以这种形式出现：

```powershell
python scripts/artifact_check.py paper_rewriting_output --markdown --write
```

检查 LaTeX：

```powershell
python src/scripts/latex_guard.py paper_rewriting_output/final_paper/main.tex --markdown
```

检查 Word：

```powershell
python src/scripts/word_guard.py paper_rewriting_output/final_paper/paper.docx --markdown
```

检查本地参考材料索引：

```powershell
python src/scripts/reference_inventory.py . --output-dir paper_rewriting_output --mode local_first
```

检查引用候选覆盖：

```powershell
python src/scripts/citation_bank_check.py paper_rewriting_output/citation_support_bank.md --target-count 20 --markdown
```

运行项目测试：

```powershell
python -m unittest discover -s tests
```

## PaperSpine 试图避免的问题

- 只改句子，不改论文逻辑。
- 把期刊、会议、课程报告、综述、竞赛论文都按同一种风格写。
- 没确认 motivation 就开始写。
- 添加没有证据支撑的 claim。
- 只输出 `main.tex`，但不解释为什么这样设计文章。
- 用户要求翻译包时，只翻译一部分中间产物。

## License

MIT License. See [LICENSE](LICENSE).

---

**独立下载:** [paper-spine-humanize](https://github.com/WUBING2023/PaperSpine/tree/main/dist/claude/skills/paper-spine-humanize) — 自包含降 AI 检测率技能，无需完整套件即可独立使用。
