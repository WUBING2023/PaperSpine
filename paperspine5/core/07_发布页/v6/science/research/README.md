# PaperSpine research collection / PaperSpine 科研案例

Four research papers on public measurements. The bundles include editable manuscripts and figures, analysis code, and public input references. Three studies were used for the edition runs described below.

| Study | Paper, figure and reproducibility package | Data |
| --- | --- | --- |
| Atlantic cyclone intensification across comparable starting conditions | [PDF](atlantic-ri/paper.pdf) · [Main figure](atlantic-ri/figure.svg) · [Sensitivity figure](atlantic-ri/checks.svg) · [Source](atlantic-ri/source.zip) | [NOAA NHC HURDAT2](https://www.nhc.noaa.gov/data/#hurdat) · [Natural Earth](https://github.com/nvkelso/natural-earth-vector/tree/v5.1.2) |
| Two black-hole mergers in public LIGO strain | [PDF](gravitational-waves/paper.pdf) · [Vector](gravitational-waves/figure.svg) · [Source](gravitational-waves/source.zip) | [GWOSC](https://doi.org/10.7935/82H3-HH23) |
| Catalog dependence of early aftershock decay at Ridgecrest | [PDF](ridgecrest/paper.pdf) · [Vector](ridgecrest/figure.svg) · [Source](ridgecrest/source.zip) | [USGS ComCat](https://earthquake.usgs.gov/fdsnws/event/1/) · [Shelly’s catalog](https://doi.org/10.5066/P9JN6H0N) |
| June smoke, two different footprints | [PDF](smoke/paper.pdf) · [Vector](smoke/figure.svg) · [Source](smoke/source.zip) | [EPA AirData](https://aqs.epa.gov/aqsweb/airdata/download_files.html) |

## Manuscript and figure previews

The website renders the first page and one results page from each PDF. The results previews show Atlantic cyclones page 2, LIGO page 3, Ridgecrest page 4, and smoke page 4. Use the link beneath the preview to open the corresponding PDF page or the editable SVG.

The Atlantic cyclone study followed the standalone V6 Skill. It compares 6,017 24-hour windows in 37 shared starting contexts. An independent implementation reproduced the seven main and sensitivity specifications. For the revised main plate, the reviewer matched 484 trajectories to the five original fixes per window, independently reproduced the nine exploratory threshold estimates and intervals, and checked the rendered plate and caption at the manuscript width.

The [research gallery](https://wubing2023.github.io/PaperSpine/v6/?v=research-gallery#showcase) rotates four study cards and presents each manuscript page and scientific plate as a static preview. The cyclone plate uses a Lambert conformal conic projection for the 484 twenty-four-hour tracks meeting the main 30-knot definition. The [archived track data](atlantic-ri/explorer.json) contain 1,826 recorded paths reaching the lowest exploratory threshold of 15 knots and can be rebuilt from the source bundle.

The sensitivity views use the [LIGO preprocessing figure](gravitational-waves/checks.svg) and [Ridgecrest catalog-count figure](ridgecrest/checks.svg) from their original source bundles. The [smoke sensitivity figure](smoke/checks.svg) plots the saved contrasts from `results.json` in the smoke bundle, including 27 leave-one-monitor-out and eight leave-one-county-group-out reruns. Its lines span those reruns. [Preview renderer](https://github.com/WUBING2023/PaperSpine/blob/main/paperspine5/core/07_发布页/v6/render_research_previews.py)

## How the runs were conducted

For each study in the table below, a GPT‑6.1 Sol Codex subagent started from the research question and original public measurements. It verified and installed the three released V6 `6.0.0-beta.2` archives in separate directories, followed the installed Skill instructions, then shared the study evidence across the three workflows.

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

北大西洋气旋案例使用独立全流程 Skill，对照 NOAA 的 42 个气旋季和 6,017 个可比窗口，提供五页研究稿、六联主图和四联稳健性图。独立复核从锁定版本的公开数据重算七套分析，并逐条核对新版主图的 484 段轨迹、九个探索性阈值及其区间。九次版本试跑来自已有三项研究。

三个 GPT‑6.1 Sol 子 Agent 分别使用公开数据，完成引力波、地震余震目录和烟霾监测三篇五页论文。每篇先由全流程 Skill 完成分析和初稿，再用 Skills 包按阶段复核、参考写作、制图与交付。Web 运行使用已发布的 Windows 插件和真实浏览器，在同一任务内提交返修意见、预览并下载修订稿。三个流程沿用同一项研究的证据，三篇各自附可编辑论文、矢量图及复现代码。稿件使用学科期刊常见版式并完成本地核查，尚未投稿或经过独立同行评审。
