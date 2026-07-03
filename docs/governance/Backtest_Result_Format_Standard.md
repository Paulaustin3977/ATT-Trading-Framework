# Backtest Result Format Standard

Task ID: RDR-001
Version: 1.0 Draft
Status: Draft for Paul Austin Review
Owner: Hermes, Quantitative Research Department
Applies To: Hermes backtests, validation runs, asset qualification tests, version comparisons, and ATE release-validation research.

---

# 1. Purpose

This standard defines the required format for all Austin Trading backtest and validation results.

Every material Hermes research/backtest run must produce:

1. Human-readable report: Markdown `.md`, optional PDF export.
2. Machine-readable summary: CSV `.csv`, optional JSON `.json`.
3. Reproducibility manifest: Markdown or JSON.

---

# 2. Required Human Report Sections

Every backtest report must include these sections. If a section does not apply, write `Not applicable` and explain why.

1. Executive Summary
2. Research Question
3. Hypothesis
4. ATE Version
5. Strategy / Indicator Version
6. Market Universe
7. Timeframe
8. Date Range
9. Data Source
10. Parameters Tested
11. Methodology
12. Entry / Exit Logic
13. Position Sizing
14. Transaction Costs
15. Slippage Assumptions
16. In-Sample Results
17. Out-of-Sample Results
18. Walk-Forward Results
19. Benchmark Comparison
20. Asset-by-Asset Results
21. Regime Breakdown where possible
22. Parameter Stability
23. Sensitivity Analysis
24. Drawdown Analysis
25. Trade Distribution
26. Failure Cases
27. Negative Findings
28. Limitations
29. Risk of Overfitting
30. Research Classification
31. Recommendation
32. Reproducibility Manifest
33. Git Commit Hash
34. Artefact Locations
35. Lessons Learned
36. Documentation Improvements
37. Research Integrity Statement

---

# 3. Research Classification Values

Use one of:

- `Supported`
- `Weakly Supported`
- `Inconclusive`
- `Falsified`
- `Operationally Rejected`

A result can be profitable and still be `Weakly Supported` or `Inconclusive` if evidence quality is insufficient.

A result can be unprofitable and still valuable if it identifies asset unsuitability, architecture limits, or false assumptions.

---

# 4. Recommendation Values

Use one of:

- `Promote` — evidence supports promotion to the next lifecycle state.
- `Modify` — evidence suggests value but changes are required.
- `Retest` — evidence is not sufficient; more validation required.
- `Reject` — evidence does not support continued use under current assumptions.

Hermes may recommend. Paul Austin approves final release/governance decisions.

---

# 5. Results Dashboard Format

Every human-readable report should open with this dashboard block.

```text
ATE Version:
Test Type:
Universe:
Timeframe:
Direction:
Classification:
Recommendation:
```

## Core Metrics Table

| Metric | Value | Notes |
|---|---:|---|
| Total Return |  |  |
| CAGR |  |  |
| Sharpe |  |  |
| Sortino |  |  |
| Max Drawdown |  |  |
| Win Rate |  |  |
| Profit Factor |  |  |
| Trade Count |  |  |
| Average Trade Duration |  |  |
| Time in Market |  |  |

## Asset Ranking Table

| Symbol | Asset Class | Return | Sharpe | Drawdown | Trades | Grade | Notes |
|---|---|---:|---:|---:|---:|---|---|
|  |  |  |  |  |  |  |  |

## Findings

- What worked:
- What failed:
- What was surprising:
- What should be retested:

## Decision

`Promote / Modify / Retest / Reject`

---

# 6. Machine-Readable CSV Standard

Use:

`docs/templates/Research_Summary_Table_Template.csv`

Required design rules:

- One row per symbol/test slice where practical.
- Use aggregate rows only with `symbol=ALL` and `asset_class=Aggregate`.
- Use ISO dates: `YYYY-MM-DD`.
- Store returns and rates as decimals, not strings: `0.125`, not `12.5%`.
- If unavailable, leave blank; do not use zero unless zero is the measured value.
- Use repository-relative paths for report and manifest links.
- Keep `run_id` stable and unique.

---

# 7. Required Metric Definitions

| Metric | Definition |
|---|---|
| Total Return | Ending equity / starting equity - 1 |
| CAGR | Annualised compound growth over test date range |
| Sharpe | Annualised excess-return Sharpe; annualisation must match timeframe |
| Sortino | Annualised downside-risk metric; annualisation must match timeframe |
| Max Drawdown | Maximum peak-to-trough equity decline |
| Profit Factor | Gross profit / absolute gross loss |
| Expectancy | Average expected return per trade |
| Win Rate | Winning trades / total trades |
| Average Trade Duration | Mean holding period in bars or days, specified in manifest |
| Percent Time in Market | Bars in position / total bars |
| Benchmark Return | Comparable buy-and-hold or approved benchmark return |
| Benchmark Sharpe | Sharpe for benchmark over same period/frequency |

---

# 8. Bias and Robustness Controls

Performance claims require review of:

- Overfitting.
- Data snooping.
- Lookahead.
- Repainting.
- Survivorship bias.
- Parameter stability.
- Benchmark comparison.
- Regime dependence.
- Transaction costs where trading performance is claimed.
- Slippage assumptions.
- Asset-universe selection bias.

If any control is missing, classification cannot be `Supported` unless Paul Austin explicitly approves a waiver.

---

# 9. Asset Qualification Standard

Assets are graded as:

## Tier A: Production Candidate

Minimum evidence:

- Positive out-of-sample evidence.
- Acceptable drawdown relative to target use.
- Adequate trade count for timeframe.
- Parameter stability across nearby values.
- Robustness across at least two market regimes where data permits.
- Transaction-cost sensitivity acceptable.
- Benchmark comparison reasonable.
- Behavioural explanation exists.
- No evidence that result is a one-off historical anomaly.

## Tier B: Promising / Needs More Validation

Minimum evidence:

- Some positive OOS or time-split support.
- Limitations are clear.
- Parameter stability not yet fully proven.
- Needs additional data, regimes, or retesting.

## Tier C: Research Only

Minimum evidence:

- Interesting behaviour or market insight.
- Not enough evidence for promotion.
- May be useful for feature design or future research.

## Tier D: Not Suitable Under Current Architecture

Evidence may include:

- Poor OOS performance.
- Unacceptable drawdown.
- Too few trades.
- Fragile parameters.
- Excessive cost sensitivity.
- No behavioural explanation.
- Result depends on one exceptional historical episode.

Exceptional historical cases, such as NVDA's unusual AI/chip-driven rise, must not be overvalued unless the test shows repeatable behaviour beyond the exceptional episode.

---

# 10. Version Comparison Standard

ATE version comparisons must answer:

- What changed?
- What improved?
- What got worse?
- Did the new version outperform across multiple assets or only one?
- Did drawdown improve?
- Did trade quality improve?
- Did parameter stability improve?
- Did explainability improve?
- Did complexity increase?
- Is the improvement statistically credible?
- Should the version be promoted, modified, retested, or rejected?

Comparison reports must include side-by-side metrics and per-asset deltas.

A version should not be promoted solely because one exceptional asset improved.

---

# 11. Negative, Weak, Failed, and Inconclusive Results

Preserve results when they show:

- A false hypothesis.
- Asset unsuitability.
- Engine weakness.
- Data-quality issue.
- Excessive overfitting risk.
- Parameter fragility.
- Unacceptable drawdown.
- Cost sensitivity.
- Benchmark underperformance.

Store such reports in:

`research/Reports/Negative_Findings/`

Create an RDR if the finding changes project direction or prevents likely repeated testing.

---

# 12. Reproducibility Standard

Every material report must link a manifest containing:

- Run ID.
- Date/time.
- Researcher.
- ATOS version.
- ATE version.
- Strategy/indicator version.
- Git commit hash.
- Data source.
- Data date range.
- Parameters.
- Scripts/tools used.
- Output files.
- Known limitations.

If a run cannot be reproduced exactly, state why.

---

# 13. Research Integrity Statement

Every report must end with a statement confirming:

- Evidence, interpretation, recommendation, and decision are separated.
- No live trading, broker connectivity, or paper-trading API was used.
- Known limitations and negative findings were reported.
- Hermes recommendation is not final governance approval.
