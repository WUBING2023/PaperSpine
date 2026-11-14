[English](README.md) · **简体中文**

<a href="https://wubing2023.github.io/PaperSpine/v6/zh/"><img src="paperspine5/core/07_发布页/v6/science/cover-zh.webp" width="100%" alt="PaperSpine V6，AI for Science。Dry Bean 研究稿、原始结果图与折纸龙 Spine。"></a>

**做实验、画科研图，交付一篇能编辑、能核对证据的论文。** 给科研 Agent 一个问题、一份结果或一篇初稿，就可以开始。

[**选择下载**](#ways-to-work) · [实跑记录](#edition-field-test) · [科研案例](#research-cases) · [看动图](#feature-demos) · [**媒体素材**](#press-kit) · [中文官网](https://wubing2023.github.io/PaperSpine/v6/zh/)

<a id="ways-to-work"></a>

## 三种使用方式

| 版本 | 怎么开始 | 能拿到什么 |
| :--- | :--- | :--- |
| **全流程 Skill**<br>[下载 ZIP](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skill-6.0.0-beta.2.zip) | 在宿主对话里调用 `$paper-spine`，交给它题目、数据或初稿。 | 在约定范围内交付研究记录、分析、图件和可编辑稿件。 |
| **Skills 包**<br>[下载 ZIP](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skills-pack-6.0.0-beta.2.zip) | 调用 `$paper-spine` 跑全流程，或用 `$paper-spine-followwriting` 等入口只做一个环节。 | 按阶段拿到所需文件，保留出处和下一步所需证据。 |
| **Web 插件包**<br>[下载 ZIP](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-web-plugin-6.0.0-beta.2-windows-x64.zip) | 在 Windows x64 的 Codex 里用 `$paper-spine-web:paper-spine-web`。 | 整套 Skills 和本地工作台，可在同一任务里调整设置、放大图件、预览、下载和返修。 |

<details>
<summary><strong>五个阶段 Skill 和可以照着写的指令</strong></summary>

| Skill | 可以这样提需求 |
| --- | --- |
| `$paper-spine-study` | 用这份数据设计配对实验，保存每个划分的结果。 |
| `$paper-spine-followwriting` | 参考这两篇源论文调整 Results 的论证，保留我的估计值和结论范围。 |
| `$paper-spine-figures` | 用分析结果画矢量图，附上生成代码。 |
| `$paper-spine-review` | 核对证据能支撑哪些结论，指出薄弱处并修订。 |
| `$paper-spine-deliver` | 交付可编辑稿、阅读稿和支撑材料。 |

</details>

<a id="installation"></a>

## 安装、更新和卸载

解压选好的 ZIP，在解压目录运行随包附带的管理器。参数使用原 ZIP 路径及校验表里的 SHA-256。装完后打开新的宿主对话。

```text
python -B edition_manager.py install "<原 ZIP 路径>" --sha256 <SHA256>
```

管理器需要 Python 3.12 或更新版。Web 包含 Windows Python，还需要 Codex CLI。支持自动检查更新、手动升级、回退和卸载，保留论文、数据和本地任务。

[安装、更新及卸载说明](INSTALL-V6.md) · [SHA-256 校验文件](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/checksums.sha256) · [V6 Release](https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2)

<a id="edition-field-test"></a>

## 同一研究跑通三个版本

三个 Codex 子 Agent 分别安装了三个 V6 发行包，从同一批公开数据起步。对 Dry Bean 去重后的 13,543 条记录做五折配对评估，在训练折拟合标准化参数后，固定 7 近邻分类器的平均平衡准确率从 **71.62% 升至 93.46%**。

| 全流程 Skill | Skills 包 | Web 插件包 |
| :--- | :--- | :--- |
| 交付修订后的两页稿、可复算分析和可编辑图。 | 逐项跑完五个阶段，从交付包重新编译论文。 | 在工作台提交意见，原任务返修后重新下载 Word 和 PDF。 |

[**查看实跑记录**](paperspine5/core/07_发布页/v6/science/edition-field-test.md) · [论文及源码包](https://wubing2023.github.io/PaperSpine/v6/science/scaling-study-source.zip) · [Web 返修 PDF](paperspine5/core/07_发布页/v6/science/scaling-workbench.pdf) · [可编辑 Word](paperspine5/core/07_发布页/v6/science/scaling-workbench.docx)

<a id="research-cases"></a>

## 科研案例

这里展示 PaperSpine 参与的实际研究和作者产物。研究方法、结果与适用范围都可以打开原图和研究稿核对。

### Dry Bean · 缺失机制压力测试

Agent 使用公开的豆类形态测量数据设计压力测试，比较两个分类器在缺失机制一致和反转时的表现。

去重后分析 13,543 条记录，得到 2,160 个评估单元。人工缺失率为 30% 时，逻辑回归增加缺失指示变量，在机制一致时使平衡准确率提高 **3.14 个百分点**，在机制反转时下降 **20.75 个百分点**。结果适用于这一受控压力测试。

<a href="paperspine5/core/07_发布页/v6/science/dry-bean-figure.svg"><img src="paperspine5/core/07_发布页/v6/science/dry-bean.webp" width="760" alt="六个面板，展示两类模型在三种人工缺失率下加入缺失标记的配对效应。"></a>

[阅读研究稿](paperspine5/core/07_发布页/v6/science/dry-bean-paper.pdf) · [打开原始矢量图](paperspine5/core/07_发布页/v6/science/dry-bean-figure.svg) · [数据来源](https://doi.org/10.24432/C50S4B)

### Bootstrap 特征聚合 · 稳定性诊断

从实际调参记录追查一个小细节：并列特征的取舍会影响模型，即使最终选中的特征完全一样。

在 Digits 的一次划分中，调参从 **C = 10 变成 C = 1**，有 **八个样本预测标签变化**。稿件同时记录三个公开数据集和一个合成条件的实现诊断。

<a href="paperspine5/core/07_发布页/v6/science/feature-aggregation-figure.svg"><img src="paperspine5/core/07_发布页/v6/science/feature-aggregation.webp" width="760" alt="三个原生面板，展示阈值的并列情况、Digits 完整调参轨迹及构造信息组的覆盖率。"></a>

[阅读研究稿](paperspine5/core/07_发布页/v6/science/feature-aggregation-paper.pdf) · [打开原始矢量图](paperspine5/core/07_发布页/v6/science/feature-aggregation-figure.svg) · [案例证据与出处](paperspine5/core/07_发布页/v6/science/case-notes.md)

### 不同学科的可编辑制图

图件库里有 **固态电池界面机理图** 和 **闭环催化剂筛选图**，分别展示机理示意和模拟数据的多面板表达。

<p><a href="https://wubing2023.github.io/PaperSpine/v6/zh/#figures"><img src="paperspine5/core/07_发布页/v6/science/solid-state-interface.webp" alt="循环中硫化物固态电解质与锂金属界面的机理示意图。" width="435"><img src="paperspine5/core/07_发布页/v6/science/catalyst-workflow.webp" alt="用模拟数据绘制的多面板闭环催化剂筛选流程图。" width="435"></a></p>

[到 Figure Studies 下载原尺寸 PNG 和 SVG](https://wubing2023.github.io/PaperSpine/v5/figure-studies/)

<a id="paper-example"></a>
<a id="feature-demos"></a>

## 功能动图

<table><tr>
  <td width="50%"><a href="paperspine5/core/07_发布页/v6/science/followwriting-hd.gif"><picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/followwriting-hd-still.webp">
    <img src="paperspine5/core/07_发布页/v6/science/followwriting-hd.gif" width="385" alt="Followwriting">
  </picture></a><br><strong>Followwriting</strong></td>
  <td width="50%"><a href="paperspine5/core/07_发布页/v6/science/figures-hd.gif"><picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/figures-hd-still.webp">
    <img src="paperspine5/core/07_发布页/v6/science/figures-hd.gif" width="385" alt="科研图审阅">
  </picture></a><br><strong>科研图审阅</strong></td>
</tr><tr>
  <td width="50%"><a href="paperspine5/core/07_发布页/v6/science/workbench-hd.gif"><picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/workbench-hd-still.webp">
    <img src="paperspine5/core/07_发布页/v6/science/workbench-hd.gif" width="385" alt="论文预览">
  </picture></a><br><strong>论文预览</strong></td>
  <td width="50%"><a href="paperspine5/core/07_发布页/v6/science/revision-hd.gif"><picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/revision-hd-still.webp">
    <img src="paperspine5/core/07_发布页/v6/science/revision-hd.gif" width="385" alt="审阅与返修">
  </picture></a><br><strong>审阅与返修</strong></td>
</tr></table>

Followwriting 短片演示如何借鉴论证写法、用本研究的结果落笔。其余片段来自已发布的 Windows 工作台。[查看反馈到返修过程](https://wubing2023.github.io/PaperSpine/v6/zh/#revision) · [原尺寸工作台截图](https://wubing2023.github.io/PaperSpine/v6/zh/#examples)

<a id="press-kit"></a>

## 媒体与创作者素材

> PaperSpine 是一个开源的 AI for Science 工作流，帮助科研 Agent 做实验、绘制科研图、交付可编辑论文。研究者可以选一个全流程 Skill、分阶段调用，或在本地工作台审阅。

[**下载完整媒体包**](https://wubing2023.github.io/PaperSpine/v6/science/paperspine-v6-press-kit.zip) · [双语简介和图注](paperspine5/core/07_发布页/v6/science/press-copy.md) · [横版封面](paperspine5/core/07_发布页/v6/science/press-cover.png) · [竖版封面](paperspine5/core/07_发布页/v6/science/press-portrait.png) · [折纸龙 Spine 透明底](paperspine5/core/07_发布页/v6/science/spine.png)

## 开发与社区

[V6 源码](paperspine5/core/01_PaperSpine4/src/skill-editions/) · [安装管理器](paperspine5/core/06_插件化/release/edition_manager.py) · [官网源码](paperspine5/core/07_发布页/v6/) · [问题反馈](https://github.com/WUBING2023/PaperSpine/issues)

<details>
<summary>V5 文档与源码索引</summary>

- 方法与工作件 · [writing_rationale_matrix](src/skill/references/rewrite.md) · [citation_support_bank](src/skill/references/citation-support-bank.md) · [translation_package](src/skill/references/translation-package.md)
- 导出及验证工具 · [artifact_check.py](src/scripts/artifact_check.py) · [reference_inventory.py](src/scripts/reference_inventory.py) · [citation_bank_check.py](src/scripts/citation_bank_check.py) · [latex_guard.py](src/scripts/latex_guard.py) · [word_guard.py](src/scripts/word_guard.py)
- 旧版宿主投影 · [Codex](dist/codex/skills/paper-spine/) · [Claude](dist/claude/skills/paper-spine/) · [OpenClaw](dist/openclaw/skills/paper-spine/) · [Claude command](dist/claude/commands/paperspine.md)
- V5 安装器 · [install.ps1](install.ps1) · [install.sh](install.sh)

[V5 存档](https://wubing2023.github.io/PaperSpine/v5/?legacy=1) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [Português](README.pt.md)

</details>

## 许可证

[MIT](LICENSE) · [Instrument Serif](paperspine5/core/07_发布页/v6/fonts/instrument-OFL.txt) · [Noto Serif SC](paperspine5/core/07_发布页/v6/fonts/notoserifsc-OFL.txt)
