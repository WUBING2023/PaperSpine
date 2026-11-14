**English** · [中文](README.zh-CN.md)

<p align="center"><a href="https://wubing2023.github.io/PaperSpine/v6/"><img src="paperspine5/core/07_发布页/v6/science/press-cover.webp" width="100%" alt="PaperSpine V6, AI for Science, with the origami dragon Spine"></a></p>

**PaperSpine is an open-source AI for Science workflow.** Use it with your research agent to study literature, plan and run analyses, make scientific figures, and hand over an editable paper with its supporting evidence.

[**Website**](https://wubing2023.github.io/PaperSpine/v6/) · [Research cases](#research-cases) · [Installation](#installation) · [**Press kit**](#press-kit)

<a id="research-cases"></a>

## Research cases

These are selected artifacts from documented, PaperSpine-assisted research runs. Open the manuscripts and figures to see the methods, results, and scope.

### Missingness shift · Dry Bean

The agent designed a controlled experiment on public seed measurements and compared matched and reversed missingness across two classifiers.

The run used 13,543 records after deduplication and scored 2,160 evaluation conditions. At 30% imposed missingness, adding logistic-regression indicators changed balanced accuracy by **+3.14 pp** under matched masks and **−20.75 pp** under reversal. The result concerns this controlled stress test.

<a href="paperspine5/core/07_发布页/v6/science/dry-bean-figure.svg"><img src="paperspine5/core/07_发布页/v6/science/dry-bean.webp" width="760" alt="Six panels showing the paired effects of missingness indicators for two classifiers at three imposed missingness rates."></a>

[Read the paper](paperspine5/core/07_发布页/v6/science/dry-bean-paper.pdf) · [Open the original vector](paperspine5/core/07_发布页/v6/science/dry-bean-figure.svg) · [Dataset source](https://doi.org/10.24432/C50S4B)

### Bootstrap feature aggregation

This study traced how a tie in feature selection altered nested model tuning even with an unchanged final feature subset.

One Digits split changed the tuned regularization from **C = 10 to C = 1** and **eight predicted labels**. The manuscript also compares three public datasets and one synthetic condition. This is an implementation diagnosis.

<a href="paperspine5/core/07_发布页/v6/science/feature-aggregation-figure.svg"><img src="paperspine5/core/07_发布页/v6/science/feature-aggregation.webp" width="760" alt="Native three-panel figure showing ambiguous cutoffs, the Digits tuning trace, and group coverage."></a>

[Read the paper](paperspine5/core/07_发布页/v6/science/feature-aggregation-paper.pdf) · [Open the original vector](paperspine5/core/07_发布页/v6/science/feature-aggregation-figure.svg) · [Case evidence](paperspine5/core/07_发布页/v6/science/case-notes.md)

### Editable figures for other fields

The figure gallery includes a **solid-state battery interface schematic** and a **closed-loop catalyst-screening visualization**. These are an illustrative mechanism and a synthetic data example.

<p><a href="https://wubing2023.github.io/PaperSpine/v6/#figures"><img src="paperspine5/core/07_发布页/v6/science/solid-state-interface.webp" alt="Scientific schematic of a sulfide solid electrolyte and lithium-metal interface during cycling." width="435"><img src="paperspine5/core/07_发布页/v6/science/catalyst-workflow.webp" alt="Multi-panel visualization of a catalyst-screening workflow with synthetic data." width="435"></a></p>

[Full-resolution PNGs and SVGs in Figure Studies](https://wubing2023.github.io/PaperSpine/v5/en/figure-studies/)

<a id="ways-to-work"></a>

## Three ways to work

### Full Workflow Skill

Give your host a research question, a results folder, or a draft. Call $paper-spine and agree on the next research or writing step.

- **Start with** · `$paper-spine`
- **Expected output** · Research notes, analyses or documented evidence, figures, and an editable manuscript for the scope you set.
- **Requirements** · Skill-capable host

[Download Full Workflow Skill ↓](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skill-6.0.0-beta.2.zip)

### Skills Pack

Install the full workflow and five skills you can invoke individually. Start with existing evidence when you only need to revise a section or check a figure.

- **Start with** · `$paper-spine-followwriting`
- **Expected output** · A focused output such as a reference-guided rewrite, an editable figure, a review report, or a paper archive.
- **Requirements** · Skill-capable host

[Download Skills Pack ↓](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-skills-pack-6.0.0-beta.2.zip)

### Web Plugin

Open a paper with the host, then use the workbench to save settings, compare figures, preview files, and respond with revision notes.

- **Start with** · `$paper-spine-web:paper-spine-web`
- **Expected output** · A local record of selections, feedback, previews, and the same paper’s downloadable files.
- **Requirements** · Windows x64 · Codex

[Download Web Plugin ↓](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/paperspine-web-plugin-6.0.0-beta.2-windows-x64.zip)

**The Skills Pack includes**

- `$paper-spine-study` · Research and experiment design
- `$paper-spine-followwriting` · Reference-guided drafting
- `$paper-spine-figures` · Scientific figures
- `$paper-spine-review` · Evidence and manuscript review
- `$paper-spine-deliver` · Editable deliverables

<a id="installation"></a>

## Install and manage updates

Choose one ZIP and download the checksum list. Extract the archive, open a terminal in the extracted folder, and run the manager with the original ZIP and its SHA-256. Open a fresh agent chat after installation.

```text
python -B edition_manager.py install "<original ZIP path>" --sha256 <SHA256>
```

Requires Python 3.12+ for managed installation. The Web archive includes Windows Python and requires the Codex CLI. Install into a compatible host's Skill directory or follow the manual placement option in the guide.

Managed installs can check and apply updates, turn automatic checks off, roll back, or uninstall. Drafts and local tasks are retained. V5 continues on its own channel, and its saved profiles should be opened in V5 or carried forward using the manuscript files.

[Installation, updates and uninstall](INSTALL-V6.en.md) · [Release assets](https://github.com/WUBING2023/PaperSpine/releases/tag/v6.0.0-beta.2) · [Checksums](https://github.com/WUBING2023/PaperSpine/releases/download/v6.0.0-beta.2/checksums.sha256)

<a id="paper-example"></a>
<a id="feature-demos"></a>

## Feature demos

Three brief demonstrations. Followwriting is a workflow illustration. The figure zoom and PDF viewer clips use the released Windows workbench with the case loaded.

### Followwriting

Use reference papers for structure and argument, then write from your own evidence.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/followwriting-hd-still.webp">
  <img src="paperspine5/core/07_发布页/v6/science/followwriting-hd.gif" width="820" alt="Followwriting · feature demonstration">
</picture>

### Figure review

Open a scientific figure in the local workbench and inspect it at full size.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/figures-hd-still.webp">
  <img src="paperspine5/core/07_发布页/v6/science/figures-hd.gif" width="820" alt="Figure review · feature demonstration">
</picture>

### Manuscript preview

Open the same study’s reading manuscript in the workbench viewer.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="paperspine5/core/07_发布页/v6/science/workbench-hd-still.webp">
  <img src="paperspine5/core/07_发布页/v6/science/workbench-hd.gif" width="820" alt="Manuscript preview · feature demonstration">
</picture>

<a id="press-kit"></a>

## Press kit

Ready-to-quote copy, ready-to-crop graphics, and three clips. The kit includes the Spine artwork with a transparent background, 1920×1080 and 1080×1350 covers, original screenshots, selected research materials, and source captions.

> PaperSpine is an open-source AI for Science workflow for research agents. It brings literature, analysis, scientific figures, and editable manuscripts into one research project. Researchers can use one Skill, pick individual stages, or review the work in a local Codex workbench.

[**Download the press kit ↓**](https://wubing2023.github.io/PaperSpine/v6/science/paperspine-v6-press-kit.zip) · [Bilingual copy and captions](paperspine5/core/07_发布页/v6/science/press-copy.md) · [Study evidence](paperspine5/core/07_发布页/v6/science/case-notes.md) · [Full-size workbench PNG](paperspine5/core/07_发布页/v6/science/workbench-figures.png)

<a href="https://wubing2023.github.io/PaperSpine/v6/science/spine.png"><img src="paperspine5/core/07_发布页/v6/science/spine.webp" alt="Spine, PaperSpine's origami dragon" width="265"></a>

## Development and community

[V6 sources](paperspine5/core/01_PaperSpine4/src/skill-editions/) · [Install manager](paperspine5/core/06_插件化/release/edition_manager.py) · [Website source](paperspine5/core/07_发布页/v6/) · [Report an issue](https://github.com/WUBING2023/PaperSpine/issues)

<details>
<summary>V5 documentation and source index</summary>

- Methods and working artifacts · [writing_rationale_matrix](src/skill/references/rewrite.md) · [citation_support_bank](src/skill/references/citation-support-bank.md) · [translation_package](src/skill/references/translation-package.md)
- Export and verification tools · [artifact_check.py](src/scripts/artifact_check.py) · [reference_inventory.py](src/scripts/reference_inventory.py) · [citation_bank_check.py](src/scripts/citation_bank_check.py) · [latex_guard.py](src/scripts/latex_guard.py) · [word_guard.py](src/scripts/word_guard.py)
- Legacy host projections · [Codex](dist/codex/skills/paper-spine/) · [Claude](dist/claude/skills/paper-spine/) · [OpenClaw](dist/openclaw/skills/paper-spine/) · [Claude command](dist/claude/commands/paperspine.md)
- V5 installers · [install.ps1](install.ps1) · [install.sh](install.sh)

[V5 archive](https://wubing2023.github.io/PaperSpine/v5/en/?legacy=1) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Русский](README.ru.md) · [Português](README.pt.md)

</details>

## License

[MIT](LICENSE) · [Instrument Serif](paperspine5/core/07_发布页/v6/fonts/instrument-OFL.txt) · [Noto Serif SC](paperspine5/core/07_发布页/v6/fonts/notoserifsc-OFL.txt)
