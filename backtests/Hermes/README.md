# Hermes Backtests

This folder stores Hermes-generated Austin Trading backtest and validation artefacts.

Human-readable reports normally live under `research/Reports/`. This folder stores machine-readable results, manifests, aggregate files, tables, and charts that support those reports.

## Canonical Structure

```text
backtests/Hermes/
├── README.md
├── ATE_v2.0/
│   ├── Daily/
│   ├── Weekly/
│   ├── Long_Only/
│   ├── Long_Short/
│   ├── Asset_Qualification/
│   └── Version_Comparison/
├── ATE_v2.1/
└── Archive/
```

Material runs should use:

```text
backtests/Hermes/ATE_vX.X/<Timeframe>/<Test_Type>/<RUN_ID>/
├── <RUN_ID>_Summary.csv
├── <RUN_ID>_Manifest.md
├── <RUN_ID>_Aggregate.json
├── charts/
└── tables/
```

## Required Outputs

Every material Hermes backtest/validation run should produce:

1. Human-readable report: Markdown, stored under `research/Reports/`.
2. Machine-readable summary: CSV, stored in the run folder.
3. Reproducibility manifest: Markdown or JSON, stored in the run folder or `data/manifests/`.
4. Optional aggregate JSON and charts.

## Classification Values

Use the Quality Manual v1.1 classifications:

- `Supported`
- `Weakly Supported`
- `Inconclusive`
- `Falsified`
- `Operationally Rejected`

## Recommendation Values

- `Promote`
- `Modify`
- `Retest`
- `Reject`

## Integrity Rules

- Do not overwrite historical run folders.
- Do not delete failed or negative findings if they influenced a decision.
- Do not report in-sample performance as the headline decision metric.
- Use timeframe-correct annualisation.
- Link every material run to its report and manifest.
- No live trading, broker connectivity, paper-trading APIs, or autonomous execution are permitted.
