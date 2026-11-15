<div align="center">

[English](README.md) · **简体中文**

</div>

<p align="center">
  <a href="https://wubing2023.github.io/PaperSpine/v6/zh/"><img src="paperspine5/core/07_发布页/v6/readme/v6-editorial-cover.webp" width="100%" alt="PaperSpine，面向科研 Agent 的开源 AI for Science Skill。封面组合了 LIGO 论文原页、六联图与折纸龙 Spine。"></a>
</p>

<p align="center">
  <a href="https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2"><img alt="V6 公测版" height="20" src="https://img.shields.io/github/v/release/WUBING2023/PaperSpine?include_prereleases&amp;filter=v6.0.0-beta.2&amp;display_name=tag&amp;style=flat&amp;logo=github&amp;color=346457"></a>&nbsp;<a href="LICENSE"><img alt="MIT 许可证" height="20" src="https://img.shields.io/github/license/WUBING2023/PaperSpine?style=flat&amp;color=455b55"></a>
  <a href="https://github.com/WUBING2023/PaperSpine/actions/workflows/validate.yml"><img alt="GitHub Actions · Skill 校验状态" height="20" src="https://github.com/WUBING2023/PaperSpine/actions/workflows/validate.yml/badge.svg?branch=main"></a>&nbsp;<a href="https://github.com/WUBING2023/PaperSpine/stargazers"><img alt="GitHub 星标" height="20" src="https://img.shields.io/github/stars/WUBING2023/PaperSpine?style=flat&amp;color=455b55"></a>
</p>

<p align="center">
  在对话里调用 <code>$paper-spine</code>，从题目、数据或初稿开始。<br>
  交付可编辑论文，同时附上核对结论所需的证据、分析和图件。
</p>

<p align="center">
  <a href="#install-with-ai"><strong>让 AI 帮你安装</strong></a> · <a href="#start-with-skill">安装 Skill</a> · <a href="#research-cases">查看科研案例</a>
</p>

<a id="install-with-ai"></a>

## 让 AI 帮你安装

把下方指令发给你正在使用的 AI 助手。

```text
请在我当前使用的 AI 宿主里安装 PaperSpine。先读官方安装入口。
https://wubing2023.github.io/PaperSpine/v6/llms.txt

按我的用途和环境选择一种版本，核对 ZIP 的 SHA-256，安装后确认版本并告诉我怎么调用 Skill。
```

[给 AI 读的安装指南](https://wubing2023.github.io/PaperSpine/v6/llms.txt) · [版本清单（JSON）](https://wubing2023.github.io/PaperSpine/v6/channel.json)

<a id="ways-to-work"></a>

## 三种使用方式

<a id="start-with-skill"></a>

### 新手上手 · 全流程 Skill

在宿主对话里调用 `$paper-spine`，交给它题目、数据或初稿。按约定范围交付研究记录、分析、科研图和可编辑稿件。

[**下载 ZIP**](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skill-6.0.0-beta.2.zip) · ![GitHub Release 下载次数](https://wubing2023.github.io/PaperSpine/v6/downloads-skill.svg?style=flat)

### 科研专家 · Skills 包

用 `$paper-spine` 跑全流程，也可以单独调用各个阶段。例如用 `$paper-spine-followwriting`，参照原论文的论证方式，用自己的实验结果改写一个章节。

[**下载 ZIP**](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skills-pack-6.0.0-beta.2.zip) · ![GitHub Release 下载次数](https://wubing2023.github.io/PaperSpine/v6/downloads-skills-pack.svg?style=flat)

### 满血插件 · 本地 Web 工作台

需要在浏览器里放大图、预览论文或提交返修意见时，可选装本地工作台。这个版本包含整套 Skills，在 Windows x64 的 Codex 里调用 `$paper-spine-web:paper-spine-web`。

[**下载 ZIP**](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-web-plugin-6.0.0-beta.2-windows-x64.zip) · ![GitHub Release 下载次数](https://wubing2023.github.io/PaperSpine/v6/downloads-web-plugin.svg?style=flat)

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

先按校验表核对原 ZIP 的 SHA-256。解压后，在解压目录运行随包附带的管理器，传入原 ZIP 路径和完整 SHA-256。装好后打开新的宿主对话。

```text
python -B edition_manager.py install "<原 ZIP 路径>" --sha256 <SHA256>
```

管理器需要 Python 3.12 或更新版。Web 包含 Windows Python，还需要 Codex CLI。支持自动检查更新、手动升级、回退和卸载，保留论文、数据和本地任务。

[安装、更新及卸载说明](INSTALL-V6.md) · [SHA-256 校验文件](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/checksums.sha256) · [V6 Release](https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2)

## PaperSpine 怎样把证据带进论文

- **从手头材料确定研究范围。** 只有研究问题时，先确认要补什么证据、做什么分析。已经有结果时，可直接推进指定的图、论证或审阅。后续阶段沿用已保存的材料和决策。
- **写作依据与科学依据各有出处。** Followwriting 保留影响结构和措辞的参考原文。本研究的证据决定论文可以主张什么，随稿附上可复核的分析、制图源文件和引用。
- **让审阅回到同一篇论文。** 保存选中的图和反馈。返修时沿用同一任务，回查证据，修改稿件及受影响的图，并保留改动记录。

LIGO 案例可以直接查验这条链路。从论文中的到达顺序，回查两台站的对齐应变与九种预处理结果。[LIGO 证据与源文件](https://wubing2023.github.io/PaperSpine/v6/zh/#gravitational-waves)

<a id="research-cases"></a>

## 北大西洋气旋的快速增强

这次使用独立全流程 Skill 分析了 NOAA 的 42 个气旋季。在 6,017 个可以对照的 24 小时窗口中，以 30 节为阈值，后期高 0.81 个百分点，按气旋季重采样的 95% 区间为 −1.69 至 +3.43。阈值换成 25 节后，点估计转为负值。六联图串起 484 条记录的 24 小时轨迹、三档不重叠的风速增量，以及九个阈值对应的点估计和区间。

<a href="https://wubing2023.github.io/PaperSpine/v6/zh/#showcase"><img src="paperspine5/core/07_发布页/v6/science/research/atlantic-ri/figure.webp" width="790" alt="大西洋气旋六联图，含 484 条轨迹、三档风速增量、九个阈值的差值和区间，以及起始条件与逐季差异。"></a>

[阅读论文](https://wubing2023.github.io/PaperSpine/v6/science/research/atlantic-ri/paper.pdf) · [主图 SVG](paperspine5/core/07_发布页/v6/science/research/atlantic-ri/figure.svg) · [稳健性图 SVG](paperspine5/core/07_发布页/v6/science/research/atlantic-ri/checks.svg) · [可编辑原稿和分析代码](https://wubing2023.github.io/PaperSpine/v6/science/research/atlantic-ri/source.zip)

调整风速阈值、分开查看两个时期，或点选一段轨迹查看每六小时的风速记录。 [探索气旋数据](https://wubing2023.github.io/PaperSpine/v6/zh/?v=interactive-atlantic#showcase)

<a id="edition-field-test"></a>

## 三篇研究，三种模式

三项研究均采用公开数据，使用 GPT‑6.1 Sol 各跑一遍全流程 Skill、阶段 Skills 和本地 Web 工作台，共有 [九次试跑记录](paperspine5/core/07_发布页/v6/science/research/README.md#how-the-runs-were-conducted)。每项研究附论文、原图、可复算代码与同稿返修记录。

[切换查看论文原页、主图和稳健性检验](https://wubing2023.github.io/PaperSpine/v6/zh/#showcase)

### 两次黑洞并合的毫秒级时延

两次公开 LIGO 事件中，汉福德相对利文斯顿分别滞后 7.36 和 7.75 毫秒。九种预处理设定下，时延方向一致。

<a href="paperspine5/core/07_发布页/v6/science/research/gravitational-waves/figure.svg"><img src="paperspine5/core/07_发布页/v6/science/research/gravitational-waves/figure.webp" width="790" alt="六个面板呈现两次事件的实测时频谱、双台站对齐应变和事件窗外的时延对照。"></a>

[读论文](https://wubing2023.github.io/PaperSpine/v6/science/research/gravitational-waves/paper.pdf) · [高清矢量图](paperspine5/core/07_发布页/v6/science/research/gravitational-waves/figure.svg) · [源稿与代码](https://wubing2023.github.io/PaperSpine/v6/science/research/gravitational-waves/source.zip) · [数据](https://doi.org/10.7935/82H3-HH23)

### 余震衰减估计随目录而变

在 Mw 7.1 主震后 1–72 小时、报告震级 ≥1.5 的相同口径下，ComCat 和 Shelly 重定位目录的拟合衰减指数分别为 0.55 与 0.48。

<a href="paperspine5/core/07_发布页/v6/science/research/ridgecrest/figure.svg"><img src="paperspine5/core/07_发布页/v6/science/research/ridgecrest/figure.webp" width="790" alt="两个目录的同尺度震中密度图、含留出区间的事件率对比，以及震级阈值与起算时间的敏感性分析。"></a>

[读论文](https://wubing2023.github.io/PaperSpine/v6/science/research/ridgecrest/paper.pdf) · [高清矢量图](paperspine5/core/07_发布页/v6/science/research/ridgecrest/figure.svg) · [源稿与代码](https://wubing2023.github.io/PaperSpine/v6/science/research/ridgecrest/source.zip) · [数据](https://doi.org/10.5066/P9JN6H0N)

### 六月烟霾，两种区域分布

以 6 月 20–22 日各站中位数为参照，大西洋沿岸与五大湖地区 PM₂.₅ 偏离量之差，从 6 月 6–8 日的 +74.1 反转为 27–29 日的 −69.1 µg/m³。

<a href="paperspine5/core/07_发布页/v6/science/research/smoke/figure.svg"><img src="paperspine5/core/07_发布页/v6/science/research/smoke/figure.webp" width="790" alt="EPA 站点地图、两组区域差值与逐日 PM₂.₅ 偏离量热图。"></a>

[读论文](https://wubing2023.github.io/PaperSpine/v6/science/research/smoke/paper.pdf) · [高清矢量图](paperspine5/core/07_发布页/v6/science/research/smoke/figure.svg) · [源稿与代码](https://wubing2023.github.io/PaperSpine/v6/science/research/smoke/source.zip) · [数据](https://aqs.epa.gov/aqsweb/airdata/download_files.html)

[三种模式证据](paperspine5/core/07_发布页/v6/science/research/README.md) · [早期安装试跑](paperspine5/core/07_发布页/v6/science/edition-field-test.md)

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

## 开发与社区

<a href="https://wubing2023.github.io/PaperSpine/zh.html"><img src="https://wubing2023.github.io/PaperSpine/atlas-preview-zh.svg" width="790" alt="PaperSpine 的 GitHub 社区星图，由公开城市信息聚合。"></a>

[查看各轮 V6 更新的贡献](https://wubing2023.github.io/PaperSpine/contributors/zh.html#v6-contributions) · [浏览社区星图](https://wubing2023.github.io/PaperSpine/zh.html)

[中文官网](https://wubing2023.github.io/PaperSpine/v6/zh/) · [V6 源码](paperspine5/core/01_PaperSpine4/src/skill-editions/) · [安装管理器](paperspine5/core/06_插件化/release/edition_manager.py) · [官网源码](paperspine5/core/07_发布页/v6/) · [问题反馈](https://github.com/WUBING2023/PaperSpine/issues) · <a id="press-kit"></a>[项目素材](https://wubing2023.github.io/PaperSpine/v6/science/paperspine-v6-press-kit.zip)

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
