# PaperSpine research cases / 科研案例出处

## Dry Bean · Missingness shift

**Use in coverage** · A PaperSpine-assisted study used public seed measurements to test how missing data can become a prediction shortcut. It compared two classifiers across controlled changes in the relationship between missingness and class.

- **Source data** · Koklu and Özkan, [UCI Dry Bean dataset](https://doi.org/10.24432/C50S4B), CC BY 4.0. The original dataset contains 13,611 observations and 16 image-derived shape measurements across seven classes. The run removed 68 duplicate feature vectors with the same label.
- **Run and result** · The example comes from the C run of an October 2026 local study. It used two classifiers, three representations, three imposed missingness rates, two training-mask strengths and five test-mask strengths over 12 paired repetitions. The study recorded 2,160 evaluation conditions. At 30% imposed missingness with class-dependent training, matched and reversed test masks gave mean logistic-regression balanced-accuracy changes of +3.14 and −20.75 percentage points after adding indicators. The corresponding ExtraTrees changes were +0.68 and −23.72 points. Each pair compares adding explicit indicators with median-imputed values alone, at the same split and mask.
- **Scope** · Missingness was imposed on the public measurements. The paired repetitions overlap and the plotted ranges are descriptive. The result concerns a stress test on one dataset. The original local comparison of Skill methods did not establish a stable quality advantage. This page shares selected artifacts from the research run.
- **Artifacts** · [Reading manuscript](dry-bean-paper.pdf) · [Original result figure, SVG](dry-bean-figure.svg) · [Experimental design, SVG](dry-bean-design.svg) · [Selected aggregate values](dry-bean-results.json)

**中文图注** · 研究在 UCI Dry Bean 公开测量数据上引入人为缺失。匹配和反转训练与测试的缺失机制时，缺失指示变量的增量表现不同。曲线汇总相同划分和遮蔽下的配对差异，阴影为 12 次重复的取值范围。

## Bootstrap feature aggregation · Implementation diagnosis

**Use in coverage** · This PaperSpine-assisted study traces how feature-selection ties can change the prediction pipeline, even when the final refit uses the same feature IDs.

- **Inputs** · scikit-learn's [Digits](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html), [Wine](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html) and [Wisconsin diagnostic breast cancer benchmark](https://doi.org/10.24432/C5DW2B), plus one synthetic correlated-feature condition. This is an exploratory machine-learning implementation study.
- **Run and result** · The v2d manuscript documents repeated nested evaluation, with ten outer splits per condition and three inner folds. One Digits trace under column permutation changed the selected regularization C from 10 to 1 with identical final selected feature IDs. Eight predicted labels changed. The full-feature arm outperformed the reduced-feature arms in each of the studied datasets. The final analysis traced saved arrays and tuning decisions; the revisions did not independently refit the whole experiment.
- **Scope** · The study compares specific implementations on four conditions and reuses dependent folds. The Wisconsin data appear as a public benchmark. The published media contain aggregated charts and a manuscript. The results do not establish clinical performance.
- **Artifacts** · [Reading manuscript](feature-aggregation-paper.pdf) · [Tuning trace, SVG](feature-aggregation-figure.svg) · [Performance and full-feature baselines, SVG](feature-performance-figure.svg)

**中文图注** · 面板 A 显示会改变选集的阈值并列，面板 B 展示 Digits 一次划分的完整调参轨迹，面板 C 显示构造信息组的覆盖率。每个结果只对应稿件列出的数据、实现和划分。

## Scientific figure gallery / 图件设计案例

The solid-state battery interface is an illustrative schematic. The catalyst discovery figure visualizes synthetic screening data. Both were published in [PaperSpine Figure Studies 301–308](https://wubing2023.github.io/PaperSpine/v5/en/figure-studies/), which includes source vectors and full-resolution exports. These media demonstrate figure design.

固态电池界面图为机理示意。闭环催化图使用模拟筛选数据。可在 [Figure Studies 图件库](https://wubing2023.github.io/PaperSpine/v5/figure-studies/) 查到原尺寸图与矢量源文件。
