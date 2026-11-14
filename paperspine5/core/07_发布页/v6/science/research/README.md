# PaperSpine research collection / PaperSpine 科研案例

Three research papers on public measurements, each written in a field-appropriate journal layout. The source bundles include the paper, editable manuscript and figures, analysis code, and public input references.

| Study | Paper, figure and reproducibility package | Data |
| --- | --- | --- |
| Two black-hole mergers in public LIGO strain | [PDF](gravitational-waves/paper.pdf) · [Vector](gravitational-waves/figure.svg) · [Source](gravitational-waves/source.zip) | [GWOSC](https://doi.org/10.7935/82H3-HH23) |
| Catalog dependence of early aftershock decay at Ridgecrest | [PDF](ridgecrest/paper.pdf) · [Vector](ridgecrest/figure.svg) · [Source](ridgecrest/source.zip) | [USGS ComCat](https://earthquake.usgs.gov/fdsnws/event/1/) · [Shelly’s catalog](https://doi.org/10.5066/P9JN6H0N) |
| June smoke, two different footprints | [PDF](smoke/paper.pdf) · [Vector](smoke/figure.svg) · [Source](smoke/source.zip) | [EPA AirData](https://aqs.epa.gov/aqsweb/airdata/download_files.html) |

## How the runs were conducted

For each study, a GPT‑6.1 Sol Codex subagent started from the research question and original public measurements. It verified and installed the three released V6 `6.0.0-beta.2` archives in separate directories, followed the installed Skill instructions, then shared the study evidence across the three workflows.

| Study | Full Workflow Skill | Skills Pack | Web Plugin |
| --- | --- | --- | --- |
| LIGO strain | Paired lag analysis and draft | Preprocessing sensitivity and source package | Figure preview, feedback, revised PDF download |
| Ridgecrest | Catalog comparison and draft | Held-out check, figure, and source package | Figure zoom, feedback, revised PDF download |
| June wildfire smoke | Fixed monitor comparison and draft | Reference sensitivity, map, and source package | Manuscript preview, feedback, revised PDF download |

The nine edition runs cover these three studies. Each study carries its analysis and evidence through all three editions.

- The **Full Workflow Skill** guided the initial analysis and manuscript from a single entry.
- The **Skills Pack** used the installed study, Followwriting, figures, review and delivery instructions to work across real files and revise the manuscript.
- The **Web Plugin** used the released Windows workbench and an actual Chrome session. Each study saved its configuration and manuscript feedback, reopened the revised paper in the same task, and downloaded the revised PDF. Each downloaded file matched the corresponding paper byte for byte.

The authoring subagents explicitly loaded the installed Skill instructions. Each dataset supports a scoped retrospective finding. The manuscripts are research demonstrations and have had local evidence and visual checks. They have not been submitted to a journal or through independent peer review. The reproduction packages describe acceptable input and catalog revisions.

## 中文

三个 GPT‑6.1 Sol 子 Agent 分别使用公开数据，完成引力波、地震余震目录和烟霾监测三篇五页论文。每篇先由全流程 Skill 完成分析和初稿，再用 Skills 包按阶段复核、参考写作、制图与交付。Web 运行使用已发布的 Windows 插件和真实浏览器，在同一任务内提交返修意见、预览并下载修订稿。三个流程沿用同一项研究的证据，三篇各自附可编辑论文、矢量图及复现代码。稿件使用学科期刊常见版式并完成本地核查，尚未投稿或经过独立同行评审。
