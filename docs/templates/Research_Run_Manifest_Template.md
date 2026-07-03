# <RUN_ID> Research Run Manifest

Run ID: <RUN_ID>
Date: <YYYY-MM-DD>
Researcher: Hermes
ATOS Version: <ATOS vX.X>
ATE Version: <ATE vX.X>
Strategy / Indicator Version: <version>
Engine Version(s): <version(s)>
Git Commit Hash: <commit>
Research Summary Schema Version: <v1 | v2 | CURRENT>

---

## 1. Purpose

<Why this run was performed.>

## 2. Classification Context

Test Type: <Backtest | Validation | Asset Qualification | Version Comparison | Market DNA | Negative Finding>
Direction Mode: <Long Only | Long Short | Short Only | None>
Timeframe: <Daily | Weekly | etc.>
Universe: <symbols / asset classes>

## 3. Data

| Field | Value |
|---|---|
| Data source |  |
| Download date |  |
| Symbol |  |
| Timeframe |  |
| Raw data path / storage location |  |
| Processed data path |  |
| Start date |  |
| End date |  |
| In-sample start/end |  |
| Out-of-sample start/end |  |
| Timezone/session assumptions |  |
| Adjusted/unadjusted |  |
| Adjustments |  |
| Missing-data handling |  |
| Transformations |  |
| Checksum if available |  |
| Known limitations |  |

## 4. Parameters

```yaml
parameters:
  example_parameter: value
```

## 5. Scripts / Tools

| Tool / Script | Version / Path | Notes |
|---|---|---|
|  |  |  |

## 6. Output Artefacts

| Artefact | Path |
|---|---|
| Human report |  |
| Summary CSV |  |
| Aggregate JSON |  |
| Charts |  |
| RDR |  |

## 7. Quality Gates

| Gate | Status | Notes |
|---|---|---|
| Data Quality |  |  |
| Research Validation |  |  |
| Reproducibility |  |  |
| Regression Evidence |  |  |
| Security and Scope |  |  |
| Knowledge Capture |  |  |

## 8. Reproducibility Notes

<Exact instructions to reproduce the run.>

## 9. Known Limitations

- <Limitation>

## 10. Schema Notes

- Schema file used:
- Schema version:
- New columns added after the locked core schema:
- Reason for additional columns:

## 11. Integrity Statement

No live trading, broker connectivity, paper-trading API, autonomous order placement, or broker credential handling was used in this research run.
