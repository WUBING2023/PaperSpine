# One study, three workflows / 三种版本实跑

Three Codex subagents installed the three public PaperSpine V6 `6.0.0-beta.2` ZIPs in isolated environments. Each ran the same question from the [UCI Dry Bean measurements](https://doi.org/10.24432/C50S4B) without a supplied manuscript or results.

## Research result

Does standardizing the 16 measurements change performance for a fixed 7-nearest-neighbor classifier? The test kept 13,543 of 13,611 records after exact row deduplication. Both arms used the same five shuffled stratified folds, seed 42, Euclidean distance, and uniform votes. Each fold’s scaling parameters were estimated on its training rows and applied to its held-out rows.

Mean balanced accuracy rose from **71.62% to 93.46%**, a paired increase of **21.84 percentage points**. All five pairs agreed in direction (+21.45 to +22.23 points). This is one dataset and one model. An independently acquired measurement batch is needed to test transfer.

[Fold-level data and confusion matrices](scaling-results.json) · [Editable SVG](scaling-figure.svg) · [Reading PDF, LaTeX, and reproduction code](scaling-study-source.zip)

## Edition evidence

| Edition | User workflow exercised |
| --- | --- |
| Full Workflow Skill | One installed `paper-spine` took the question through analysis, reference-guided writing, editable figures, and revision of a two-page manuscript. |
| Skills Pack | The installed research, Followwriting, figure, review, and delivery Skills each consumed the previous stage’s files. The resulting LaTeX was rebuilt and the analysis was rerun from the exported bundle. |
| Web Plugin | An actual local Windows Codex workbench saved the configuration, previewed and downloaded PDF and Word files, and sent manuscript feedback back to the host. The host revised the Methods and Limitations and published both revised files in the same task. Browser downloads matched the host’s files byte for byte. |

[Revised Web PDF](scaling-workbench.pdf) · [Editable Web Word document](scaling-workbench.docx) · [Short same-task revision capture](revision-hd.gif)

Fresh Codex CLI discovery verified the installed chat Skills. A fresh Codex app-server verified discovery of the namespaced Web Skill. The executing subagents explicitly opened the installed `SKILL.md` files. The Web Followwriting pass used an accessible abstract for its reference comparison. The paper checks focused on the reported evidence, rendering, and reproducibility.

Managed uninstall in the isolated Full Workflow Skill and Web Plugin installs preserved the study files. Reinstalling the Web Plugin reopened the original task and downloaded the revised paper again. The update switch worked in both directions. The network channel was offline during this trial, so the test resumed from the installed release.

## 中文

三个 Codex 子 Agent 分别从公开发布的 `6.0.0-beta.2` ZIP 隔离安装，从同一问题和公开测量数据起步。先去掉 68 条完全重复的记录，再用 13,543 条记录评估固定的 7 近邻分类器。两个条件共用五折，标准化参数只用各训练折拟合。平均平衡准确率由 **71.62% 升至 93.46%**，配对增加 **21.84 个百分点**。五折方向一致，结论限于这批数据和这个设置。

- **全流程 Skill** 从题目推进到经审查修订的两页稿、图源和分析代码。
- **Skills 包** 逐项使用研究、Followwriting、制图、审阅、交付，解压交付包后可复算和重新编译。
- **Web 插件** 在实际 Windows 工作台保存设置，预览和下载 PDF、Word，提交反馈后沿原任务返修并再次下载。

独立的新 Codex 进程验证了 Skills 发现，Web 入口经 app-server 验证。执行任务的子 Agent 直接读取这些已安装的技能文件。Web 版参考写作使用可访问的论文摘要。质量检查覆盖本次论文的结果、渲染和复算。

隔离卸载全流程版和 Web 版后，研究文件都得以保留。Web 版重装同一 ZIP 后再次打开原任务并下载返修稿。自动更新开关已实测，网络更新检查返回离线，本轮继续使用已安装的版本。

[论文及源码包](scaling-study-source.zip) · [拆分结果](scaling-results.json) · [Web 返修稿 PDF](scaling-workbench.pdf) · [Web 可编辑 Word](scaling-workbench.docx)
