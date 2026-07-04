# RDR-003W Run Manifest

Run ID: RDR-003W
Run type: Diagnostic validation (weekly companion to RDR-003)
ATE version: ATE v2.2
RiskEngine version: 1.0.0-draft
Status: Completed
Generated: 2026-07-04T17:39:59+0000

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-003W-riskengine-weekly-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/RDR-003W_Summary.csv`
- Duration CSV: `RDR-003W_Durations.csv`
- Transition CSV: `RDR-003W_Transitions.csv`
- Class summary CSV: `RDR-003W_Class_Summary.csv`
- Overlap CSV: `RDR-003W_Overlap.csv`
- Hidden bias CSV: `RDR-003W_HiddenBias.csv`
- Adverse movement CSV: `RDR-003W_Adverse.csv`
- Sampled explainers CSV: `RDR-003W_Sampled_Explainers.csv`
- Reserved-language audit CSV: `RDR-003W_Reserved_Language_Audit.csv`
- Charts directory: `charts/`
- Reproduction script: `run_rdr003w_validation.py`

## Source Code

- ATE v2.2 release file: `pine/releases/ATE_v2.2.pine`
- ATE v2.2 release SHA-256: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`
- ATE v2.1 release file (unchanged): `pine/releases/ATE_v2.1.pine`
- ATE v2.1 release SHA-256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`
- RiskEngine Python mirror: `tools/scripts/_riskengine_compute.py`
- Engine-input Python mirror: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`
- Daily RDR-003 baseline (used for the daily-vs-weekly comparison): `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: weekly OHLC, period 10y, filtered to dates from 2014-01-01 where available
- Timeframe: Weekly (`1wk` interval)
- Raw cache: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/` (not committed under RDR-001 raw-data policy)

## Reproduction Environment

- Python: 3.9 on macOS during this run
- Required packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Setup:
  ```bash
  python3 -m pip install --user yfinance matplotlib tabulate
  ```
- Re-run:
  ```bash
  python3 backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/run_rdr003w_validation.py
  ```

## Assets Tested

16 assets passed the minimum-80-row filter after the 2014-01-01 cutoff. See `RDR-003W_Summary.csv`.

Data notes:
- (no notes)

## Verifier Pre-Flight

```
$ python tools/scripts/verify_ate.py
total_checks = 442
passed = 442
failed = 0
exit = 0
v22 release SHA matches manifest: True
v22 release == dev byte-identical: True
v21 unchanged: True
```

## Daily vs Weekly Comparison Outcome


| metric | daily (RDR-003) | weekly (RDR-003W) | weekly − daily |
|---|---|---|---|
| state_changes_per_100_bars median | 9.892 | 10.153 | +0.261 |
| median dominant_vol_pct | 51.287 | 48.084 | -3.203 |
| assets with dominant_vol_pct > 60 | 6 | 4 | -2 |
| median pct_calm | 70.299 | 68.038 | -2.261 |
| median pct_unknown | 0.000 | 0.000 | +0.000 |
| max pct_unknown | 0.000 | 0.000 | +0.000 |
| median abs Spearman RiskScore vs VolScore | 0.167 | 0.212 | +0.045 |
| median abs Spearman RiskScore vs Momentum | 0.309 | 0.258 | -0.052 |
| median abs Spearman RiskScore vs Confidence | 0.425 | 0.405 | -0.020 |
| median max \|pct_up−50\| per state (pp) | 4.517 | 7.484 | +2.967 |


## Classification Rules Outcome

- `unknown_ok`: **True**
- `overlap_vol_median_ok`: **True**
- `overlap_mom_ok`: **True**
- `overlap_conf_ok`: **True**
- `vol_dominance_median_ok`: **True**
- `vol_dominance_count_ok`: **True**
- `state_changes_ok`: **True**
- `bias_ok`: **True**

## Result

Classification: **Supported**
Recommendation: **Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred**
