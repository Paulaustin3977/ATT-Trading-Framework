# RDR-003 Run Manifest

Run ID: RDR-003
Run type: Diagnostic validation
ATE version: ATE v2.2
RiskEngine version: 1.0.0-draft
Status: Completed
Generated: 2026-07-04T12:27:51+0000

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/RDR-003_Summary.csv`
- Duration CSV: `RDR-003_Durations.csv`
- Transition CSV: `RDR-003_Transitions.csv`
- Class summary CSV: `RDR-003_Class_Summary.csv`
- Overlap CSV: `RDR-003_Overlap.csv`
- Hidden bias CSV: `RDR-003_HiddenBias.csv`
- Adverse movement CSV: `RDR-003_Adverse.csv`
- Sampled explainers CSV: `RDR-003_Sampled_Explainers.csv`
- Reserved-language audit CSV: `RDR-003_Reserved_Language_Audit.csv`
- Charts directory: `charts/`
- Reproduction script: `run_rdr003_validation.py`

## Source Code

- ATE v2.2 release file: `pine/releases/ATE_v2.2.pine`
- ATE v2.2 release SHA-256: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`
- ATE v2.1 release file (unchanged): `pine/releases/ATE_v2.1.pine`
- ATE v2.1 release SHA-256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`
- RiskEngine Python mirror: `tools/scripts/_riskengine_compute.py`
- Engine-input Python mirror (Trend/Structure/Momentum/Confidence/Volatility): `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: daily OHLC, period 10y, filtered to dates from 2018-01-01 where available
- Timeframe: Daily
- Raw cache: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/` (not committed under RDR-001 raw-data policy)

## Reproduction Environment

- Python: 3.9 on macOS during this run
- Required packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Setup (system + user site-packages):
  ```bash
  python3 -m pip install --user yfinance matplotlib tabulate
  ```
- Re-run command:
  ```bash
  python3 backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/run_rdr003_validation.py
  ```

## Assets Tested

16 assets passed the minimum-300-row filter after the 2018-01-01 cutoff. See `RDR-003_Summary.csv` for the per-asset rows/start/end dates and asset class.

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

## Classification Rules Outcome

- `unknown_ok`: **True**
- `overlap_vol_median_ok`: **True**
- `overlap_vol_max_ok`: **True**
- `overlap_mom_ok`: **True**
- `overlap_conf_ok`: **True**
- `vol_dominance_median_ok`: **True**
- `vol_dominance_count_ok`: **False**
- `state_changes_ok`: **True**
- `bias_ok`: **True**

## Result

Classification: **Weakly Supported**
Recommendation: **Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt**
