# Research intake checks

## Reference skills

GitHub repository stars checked on 2026-11-15. Each link pins the Skill that
was read. PaperSpine uses the existing task notes and the host's available tools.

| Skill | Repository stars | Applied to PaperSpine |
| --- | ---: | --- |
| [Research Lookup](https://github.com/K-Dense-AI/scientific-agent-skills/blob/2d2065fb4520fa3f3f2bcf61cff26ec8b7eba4b5/skills/research-lookup/SKILL.md) | 57,258 | Preserve the difference between search leads and inspected evidence. Extract the comparison, outcome, uncertainty, and source location. |
| [Deep Research](https://github.com/affaan-m/ECC/blob/d2ef2680594f9a17526a6e1a2e18b3d242c5d17b/skills/deep-research/SKILL.md) | 303,404 | Search the decisions that need evidence separately and deep-read the sources able to change them. |
| [Research](https://github.com/danielmiessler/LifeOS/blob/f6ab5e0228bfb356c82edbf52b69344dbd585486/LifeOS/install/skills/Research/SKILL.md) | 19,892 | Scale lookup and corroboration to the question. Preserve unresolved conflicts in the evidence that reaches writing. |
| [Systematic Debugging](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md) | 317,778 | Pick a small check that can refute a consequential assumption. Change one relevant dependency at a time. |
| [QMD](https://github.com/tobi/qmd/blob/86d2365d17fc682e491c2c53d1e4a884aee8682a/skills/qmd/SKILL.md) | 31,135 | Retrieve the exact local file and cite the line or rendered passage supporting the claim. |

## Pilot design recorded before inspecting forecast scores

Would the preceding week's same-hour observation improve hourly Capital Bikeshare
demand prediction compared with a calendar-only baseline? The task assumes
earlier counts are available by the next week. A calendar-matched historical
median was chosen as a simple comparison. The [TRC 2024 forecasting study, Table 1](https://trc-30.epfl.ch/wp-content/uploads/2024/09/TRC-30_paper_89.pdf)
compares historical averages and prior-observation models for the same city at
service-point resolution. This pilot uses system-wide counts and evaluates its
own contrast.

Source and license are given in the [UCI Bike Sharing Dataset record](https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset).
Use `hour.csv` from the [official archive](https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip).
The data dictionary defines `cnt` as the total of the contemporaneous `casual`
and `registered` counts. Verify that identity on the pilot rows. A perfect
reconstruction would verify target leakage if those fields were used for future
prediction. Use only calendar fields and past observations for forecasts.

- Fit the baseline median by hour and workday flag using 2011 observations only.
- Use January–June 2012 as the pilot and July–December 2012 as the held-out period.
- Compare on the same observed hours. Count and exclude hours where an observed
  seven-day lag is missing. Compute mean absolute error in rentals per hour.
- A lower held-out MAE favors the corresponding simple predictor for this period.
  Break the paired differences into calendar weeks descriptively to check whether
  a few weeks drive the result. Keep the claim scoped to this city and period.

Run the two checks with Python 3 and the official ZIP. The program uses the
standard library and reads the archive without extracting or changing its files.

```text
python research_pilot.py /path/to/bike-sharing.zip pilot
python research_pilot.py /path/to/bike-sharing.zip holdout
```

## Results

The official ZIP SHA-256 is
`b70182d0d0508e9abbb79306ce5c0cec34869000f8220175ac83d11dbe845401`.
The SHA-256 of its `hour.csv` member is
`e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`.
The baseline used 8,645 observed training hours.

| Window | Paired hours | Missing week lag | Calendar median MAE | Weekly lag MAE | Weeks favoring the lag |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pilot, Jan–Jun 2012 | 4,347 | 11 | 86.33 | 58.06 | 17 of 27 |
| Held out, Jul–Dec 2012 | 4,337 | 39 | 118.87 | 63.17 | 24 of 28 |

The preceding week's count reduced held-out MAE by 55.71 rentals per hour
under the stated input-availability assumption. The calendar weeks are
descriptive, with partial weeks at the boundaries. This comparison covers
observed hours with paired inputs from one system and one held-out period.
The two contemporaneous components reconstructed every evaluated total
exactly. The input check ruled those fields out before forecasting. That
reconstruction was the leakage diagnostic and is absent from the forecast table.

For a supplied-results handoff, these numbers support a paired, local comparison
under the specified time split. The target reconstruction supports the data
availability explanation in Methods. The held-out table supports the forecasting
claim. Calendar-only and past-total inputs were the two measured predictors.
