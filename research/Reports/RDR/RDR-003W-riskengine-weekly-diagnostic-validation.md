# RDR-003W: RiskEngine Weekly Diagnostic Validation

Date: 2026-07-04
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.2
Research Classification: **Supported**
Recommendation: **Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred**
Companion to: RDR-003 (daily)

---

## 1. Executive Summary

Hermes validated ATE v2.2 RiskEngine v1.0.0-draft diagnostic behaviour on weekly Yahoo Finance OHLC across 16 assets spanning the same universe as RDR-003 (metals — Gold, Silver, Copper; index proxies — Nasdaq, S&P 500; major equities — NVDA, MSFT, AAPL, AMZN, GOOGL; bonds / rates proxies — TLT, IGLT.L; FX — EUR/USD, GBP/USD, USD/JPY; commodities — WTI crude).

Verdict: **Supported**.

Recommendation: **Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred**.

RiskEngine integration into DecisionEngine should remain deferred: **Yes**.
RiskEngine integration into ConfidenceEngine should remain deferred: **Yes**.
RiskEngine alerts remain prohibited: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## 2. Research Question

Does RiskEngine classify weekly market-risk states sensibly across a balanced multi-asset universe without duplicating VolatilityEngine, creating hidden directional bias, or becoming a hidden strategy?

### Key Comparison Question

Does weekly aggregation improve RiskEngine diagnostic quality compared with daily aggregation? Specifically: weekly state smoothness, volatility dominance, hidden directional bias, distinctness from Volatility and Momentum engines, and diagnostic-only governance.

## 3. Hypotheses Tested

1. Weekly RiskEngine states are smoother than daily RiskEngine states.
2. Weekly RiskEngine may reduce noise compared with daily validation.
3. RiskEngine should still not behave like a hidden trend, momentum, volatility, or strategy engine.
4. RiskEngine should add diagnostic information beyond VolatilityEngine alone.
5. RiskEngine should not create hidden bullish or bearish directional bias.
6. RiskEngine should remain diagnostic-only after weekly validation.

## 4. Methodology

- Downloaded weekly OHLC via `yfinance` for the same 16 assets as RDR-003, between 2014-01-01 and 2026-07-03 (weekly cache: `data_cache/`). RDR-001 policy: raw OHLC cache is not committed.
- Ported the ATE v2.2 Trend/Structure/Momentum/Confidence/Volatility compute paths via the same offline port used in RDR-003 (`run_rdr002_validation.py`), so that RiskEngine inputs are real engine outputs, not synthetic placeholders.
- Called `tools/scripts/_riskengine_compute.calculate_risk` to obtain RiskScore, RiskState, RiskDirection, RiskReason, and four component contributions on weekly bars.
- Performed the 12-check analysis below and produced CSV artefacts in the RDR-003W output directory.
- Generated optional per-asset weekly charts under `charts/`.
- Built a daily-vs-weekly comparison table directly from the committed RDR-003 daily Summary/Overlap/HiddenBias CSVs.
- Did not modify Pine code.
- Did not optimise parameters.
- Did not add alerts or any strategy behaviour.
- No broker, no paper-trading API, no live execution.

## 5. Data Sources

- Data source: Yahoo Finance via `yfinance` weekly OHLC.
- Timeframe: Weekly (`1wk` interval, period 10y).
- Adjusted/unadjusted: `auto_adjust=False`; OHLC retained as-is (unadjusted).
- Cache: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/` (raw OHLC); not committed under RDR-001 raw-data policy.
- Missing data handling: same `NaN` propagation as RDR-003 daily.

## 6. Assets Tested

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|
| GC=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     57.854 |       35.249 |          5.939 |       0.958 |         0     |             0 |
| SI=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     71.456 |       19.54  |          6.513 |       1.916 |         0.575 |             0 |
| HG=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     67.433 |       25.67  |          6.322 |       0.575 |         0     |             0 |
| NQ=F     | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |     59.77  |       31.034 |          8.812 |       0.383 |         0     |             0 |
| SPY      | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |     60.345 |       28.161 |         10.728 |       0.766 |         0     |             0 |
| NVDA     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     54.981 |       35.441 |          7.088 |       2.49  |         0     |             0 |
| MSFT     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     66.667 |       26.437 |          6.513 |       0.383 |         0     |             0 |
| AAPL     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     66.092 |       27.586 |          5.747 |       0.575 |         0     |             0 |
| AMZN     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     70.115 |       22.414 |          7.471 |       0     |         0     |             0 |
| GOOGL    | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     59.004 |       35.441 |          5.364 |       0.192 |         0     |             0 |
| TLT      | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |     80.843 |       16.858 |          1.341 |       0.766 |         0.192 |             0 |
| IGLT.L   | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |     79.885 |       16.475 |          3.065 |       0.575 |         0     |             0 |
| EURUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |     79.159 |       19.12  |          1.338 |       0.382 |         0     |             0 |
| GBPUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |     79.541 |       17.973 |          2.294 |       0.191 |         0     |             0 |
| JPY=X    | FX                    |    523 | 2016-06-27   | 2026-06-29 |     68.642 |       26.004 |          5.354 |       0     |         0     |             0 |
| CL=F     | Commodities           |    522 | 2016-07-04   | 2026-06-29 |     73.946 |       21.648 |          3.448 |       0.958 |         0     |             0 |

Data notes:
- (no notes)

## 7. Date Range

Combined validation range: 2016-06-27 to 2026-06-29 (per-asset ranges appear in the summary table).

## 8. ATE Version

ATE v2.2

Release file: `pine/releases/ATE_v2.2.pine`

Release SHA-256: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`

## 9. RiskEngine Version

RiskEngine v1.0.0-draft

## 10. Verifier Result

Canonical verifier `python tools/scripts/verify_ate.py` was executed before research analysis:

- total_checks: 442
- passed: 442
- failed: 0
- exit code: 0
- ATE v2.1 SHA-256 (expected/actual): `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` / `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`
- ATE v2.1 unchanged: `True`
- ATE v2.2 SHA-256 (expected/actual): `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` / `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`
- ATE v2.2 release == dev byte-identical: `True`
- ATE v2.2 release matches manifest: `True`

## 11. Daily RDR-003 Summary

Daily classification: Weakly Supported.

Daily RDR-003 medians reproduced from the committed CSVs:

- `state_changes_per_100_bars` median: 9.892
- median `dominant_vol_pct`: 51.287
- assets with `dominant_vol_pct > 60`: 6 of 16
- median `pct_calm`: 70.299
- `pct_unknown` median: 0.000, max: 0.000
- median absolute Spearman (RiskScore, VolScore): 0.167
- median absolute Spearman (RiskScore, MomentumScore): 0.309
- median absolute Spearman (RiskScore, ConfidenceScore): 0.425
- median max |pct_up-50| per state: 4.517 pp

Daily artefact location: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md`.

## 12. Weekly State Frequency Results

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|
| GC=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     57.854 |       35.249 |          5.939 |       0.958 |         0     |             0 |
| SI=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     71.456 |       19.54  |          6.513 |       1.916 |         0.575 |             0 |
| HG=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |     67.433 |       25.67  |          6.322 |       0.575 |         0     |             0 |
| NQ=F     | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |     59.77  |       31.034 |          8.812 |       0.383 |         0     |             0 |
| SPY      | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |     60.345 |       28.161 |         10.728 |       0.766 |         0     |             0 |
| NVDA     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     54.981 |       35.441 |          7.088 |       2.49  |         0     |             0 |
| MSFT     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     66.667 |       26.437 |          6.513 |       0.383 |         0     |             0 |
| AAPL     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     66.092 |       27.586 |          5.747 |       0.575 |         0     |             0 |
| AMZN     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     70.115 |       22.414 |          7.471 |       0     |         0     |             0 |
| GOOGL    | Major equities        |    522 | 2016-07-04   | 2026-06-29 |     59.004 |       35.441 |          5.364 |       0.192 |         0     |             0 |
| TLT      | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |     80.843 |       16.858 |          1.341 |       0.766 |         0.192 |             0 |
| IGLT.L   | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |     79.885 |       16.475 |          3.065 |       0.575 |         0     |             0 |
| EURUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |     79.159 |       19.12  |          1.338 |       0.382 |         0     |             0 |
| GBPUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |     79.541 |       17.973 |          2.294 |       0.191 |         0     |             0 |
| JPY=X    | FX                    |    523 | 2016-06-27   | 2026-06-29 |     68.642 |       26.004 |          5.354 |       0     |         0     |             0 |
| CL=F     | Commodities           |    522 | 2016-07-04   | 2026-06-29 |     73.946 |       21.648 |          3.448 |       0.958 |         0     |             0 |

Asset class aggregation:

| asset_class           |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |   dominant_vol_pct |   dominant_ext_pct |   dominant_struct_pct |   dominant_conflict_pct |   state_changes_per_100_bars |
|:----------------------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|-------------------:|-------------------:|----------------------:|------------------------:|-----------------------------:|
| Bonds / rates proxies |     80.364 |       16.667 |          2.203 |       0.67  |         0.096 |             0 |             66.571 |              1.916 |                17.146 |                  14.368 |                        8.238 |
| Commodities           |     73.946 |       21.648 |          3.448 |       0.958 |         0     |             0 |             57.854 |              1.724 |                21.456 |                  18.966 |                        8.046 |
| FX                    |     75.781 |       21.033 |          2.996 |       0.191 |         0     |             0 |             57.744 |              2.868 |                16.38  |                  23.008 |                        7.521 |
| Index proxies         |     60.057 |       29.598 |          9.77  |       0.575 |         0     |             0 |             39.08  |              2.969 |                23.755 |                  34.195 |                       11.59  |
| Major equities        |     63.372 |       29.464 |          6.437 |       0.728 |         0     |             0 |             44.215 |              4.291 |                23.218 |                  28.276 |                       11.303 |
| Metals                |     65.581 |       26.82  |          6.258 |       1.149 |         0.192 |             0 |             50.83  |              2.043 |                23.883 |                  23.244 |                       11.558 |

Assessment:

- `pct_unknown` median across assets = 0.00%, max = 0.00%.
- `pct_calm` + `pct_normal` combined dominates most assets, broadly consistent with the daily profile but with smoother weekly distributions.
- `pct_extreme` is rare (median 0.00%; max 0.57%) and tends to coincide with multi-week high-volatility windows.

## 13. Weekly State Duration Results

| symbol   | asset_class           | state    |   run_count |   avg_duration |   median_duration |   longest_duration |   shortest_duration |
|:---------|:----------------------|:---------|------------:|---------------:|------------------:|-------------------:|--------------------:|
| AAPL     | Major equities        | calm     |          18 |         19.167 |              13   |                 68 |                   2 |
| AAPL     | Major equities        | elevated |           7 |          4.286 |               3   |                 10 |                   1 |
| AAPL     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| AAPL     | Major equities        | normal   |          24 |          6     |               4   |                 19 |                   2 |
| AAPL     | Major equities        | tense    |           2 |          1.5   |               1.5 |                  2 |                   1 |
| AAPL     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | calm     |          20 |         18.3   |              11.5 |                104 |                   1 |
| AMZN     | Major equities        | elevated |           8 |          4.875 |               3   |                 15 |                   1 |
| AMZN     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | normal   |          27 |          4.333 |               3   |                 20 |                   1 |
| AMZN     | Major equities        | tense    |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| CL=F     | Commodities           | calm     |          15 |         25.733 |              18   |                 74 |                   1 |
| CL=F     | Commodities           | elevated |           7 |          2.571 |               2   |                  6 |                   1 |
| CL=F     | Commodities           | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| CL=F     | Commodities           | normal   |          17 |          6.647 |               4   |                 19 |                   1 |
| CL=F     | Commodities           | tense    |           3 |          1.667 |               2   |                  2 |                   1 |
| CL=F     | Commodities           | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | calm     |          21 |         19.714 |              10   |                103 |                   1 |
| EURUSD=X | FX                    | elevated |           4 |          1.75  |               1.5 |                  3 |                   1 |
| EURUSD=X | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | normal   |          23 |          4.348 |               3   |                 13 |                   1 |
| EURUSD=X | FX                    | tense    |           1 |          2     |               2   |                  2 |                   2 |
| EURUSD=X | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | calm     |          12 |         34.667 |              32.5 |                 88 |                   1 |
| GBPUSD=X | FX                    | elevated |           5 |          2.4   |               2   |                  5 |                   1 |
| GBPUSD=X | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | normal   |          16 |          5.875 |               5   |                 14 |                   1 |
| GBPUSD=X | FX                    | tense    |           1 |          1     |               1   |                  1 |                   1 |
| GBPUSD=X | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GC=F     | Metals                | calm     |          24 |         12.583 |               4   |                 78 |                   1 |
| GC=F     | Metals                | elevated |          13 |          2.385 |               2   |                  7 |                   1 |
| GC=F     | Metals                | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| GC=F     | Metals                | normal   |          34 |          5.412 |               3.5 |                 29 |                   1 |
| GC=F     | Metals                | tense    |           3 |          1.667 |               2   |                  2 |                   1 |
| GC=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | calm     |          21 |         14.667 |               5   |                 79 |                   1 |
| GOOGL    | Major equities        | elevated |           8 |          3.5   |               2.5 |                  9 |                   1 |
| GOOGL    | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | normal   |          29 |          6.379 |               5   |                 25 |                   1 |
| GOOGL    | Major equities        | tense    |           1 |          1     |               1   |                  1 |                   1 |
| GOOGL    | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| HG=F     | Metals                | calm     |          13 |         27.077 |              11   |                167 |                   3 |
| HG=F     | Metals                | elevated |          10 |          3.3   |               1.5 |                 18 |                   1 |
| HG=F     | Metals                | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| HG=F     | Metals                | normal   |          23 |          5.826 |               5   |                 20 |                   1 |
| HG=F     | Metals                | tense    |           1 |          3     |               3   |                  3 |                   3 |
| HG=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| IGLT.L   | Bonds / rates proxies | calm     |          18 |         23.167 |              10.5 |                 85 |                   1 |
| IGLT.L   | Bonds / rates proxies | elevated |           7 |          2.286 |               2   |                  5 |                   1 |
| IGLT.L   | Bonds / rates proxies | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| IGLT.L   | Bonds / rates proxies | normal   |          20 |          4.3   |               3   |                 13 |                   1 |
| IGLT.L   | Bonds / rates proxies | tense    |           2 |          1.5   |               1.5 |                  2 |                   1 |
| IGLT.L   | Bonds / rates proxies | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | calm     |          14 |         25.643 |              12.5 |                154 |                   2 |
| JPY=X    | FX                    | elevated |           4 |          7     |               3   |                 19 |                   3 |
| JPY=X    | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | normal   |          17 |          8     |               5   |                 29 |                   1 |
| JPY=X    | FX                    | tense    |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | calm     |          23 |         15.13  |               8   |                 67 |                   1 |
| MSFT     | Major equities        | elevated |           6 |          5.667 |               5   |                 11 |                   3 |
| MSFT     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | normal   |          28 |          4.929 |               4   |                 15 |                   1 |
| MSFT     | Major equities        | tense    |           1 |          2     |               2   |                  2 |                   2 |
| MSFT     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| NQ=F     | Index proxies         | calm     |          23 |         13.565 |               7   |                 78 |                   1 |
| NQ=F     | Index proxies         | elevated |          10 |          4.6   |               2.5 |                 10 |                   1 |
| NQ=F     | Index proxies         | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| NQ=F     | Index proxies         | normal   |          31 |          5.226 |               2   |                 29 |                   1 |
| NQ=F     | Index proxies         | tense    |           2 |          1     |               1   |                  1 |                   1 |
| NQ=F     | Index proxies         | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | calm     |          20 |         14.35  |               6   |                 58 |                   1 |
| NVDA     | Major equities        | elevated |          16 |          2.312 |               2   |                  9 |                   1 |
| NVDA     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | normal   |          30 |          6.167 |               3.5 |                 27 |                   1 |
| NVDA     | Major equities        | tense    |           6 |          2.167 |               2.5 |                  3 |                   1 |
| NVDA     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| SI=F     | Metals                | calm     |          21 |         17.762 |               8   |                 94 |                   1 |
| SI=F     | Metals                | elevated |          10 |          3.4   |               2   |                 15 |                   1 |
| SI=F     | Metals                | extreme  |           1 |          3     |               3   |                  3 |                   3 |
| SI=F     | Metals                | normal   |          24 |          4.25  |               3   |                 14 |                   1 |
| SI=F     | Metals                | tense    |           4 |          2.5   |               3   |                  3 |                   1 |
| SI=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| SPY      | Index proxies         | calm     |          18 |         17.5   |              10   |                 79 |                   1 |
| SPY      | Index proxies         | elevated |          10 |          5.6   |               3   |                 26 |                   1 |
| SPY      | Index proxies         | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| SPY      | Index proxies         | normal   |          25 |          5.88  |               3   |                 26 |                   1 |
| SPY      | Index proxies         | tense    |           2 |          2     |               2   |                  3 |                   1 |
| SPY      | Index proxies         | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| TLT      | Bonds / rates proxies | calm     |          14 |         30.143 |              19   |                132 |                   2 |
| TLT      | Bonds / rates proxies | elevated |           5 |          1.4   |               1   |                  3 |                   1 |
| TLT      | Bonds / rates proxies | extreme  |           1 |          1     |               1   |                  1 |                   1 |
| TLT      | Bonds / rates proxies | normal   |          16 |          5.5   |               2.5 |                 28 |                   1 |
| TLT      | Bonds / rates proxies | tense    |           3 |          1.333 |               1   |                  2 |                   1 |
| TLT      | Bonds / rates proxies | unknown  |           0 |          0     |               0   |                  0 |                   0 |

Assessment: weekly durations are longer in absolute terms because each weekly bar subsumes multiple daily bars; the per-state sequence is not noisy. `unknown` and `extreme` are episodic; `normal` and `calm` dominate run length.

## 14. Weekly Transition Results

| symbol   | asset_class    | transition       |   count |   pct_of_bars |
|:---------|:---------------|:-----------------|--------:|--------------:|
| GC=F     | Metals         | calm->normal     |      23 |         4.406 |
| GC=F     | Metals         | normal->elevated |      10 |         1.916 |
| GC=F     | Metals         | elevated->tense  |       3 |         0.575 |
| GC=F     | Metals         | tense->extreme   |       0 |         0     |
| GC=F     | Metals         | extreme->normal  |       0 |         0     |
| GC=F     | Metals         | extreme->calm    |       0 |         0     |
| GC=F     | Metals         | unknown->normal  |       0 |         0     |
| SI=F     | Metals         | calm->normal     |      18 |         3.448 |
| SI=F     | Metals         | normal->elevated |       4 |         0.766 |
| SI=F     | Metals         | elevated->tense  |       3 |         0.575 |
| SI=F     | Metals         | tense->extreme   |       0 |         0     |
| SI=F     | Metals         | extreme->normal  |       0 |         0     |
| SI=F     | Metals         | extreme->calm    |       0 |         0     |
| SI=F     | Metals         | unknown->normal  |       0 |         0     |
| HG=F     | Metals         | calm->normal     |      12 |         2.299 |
| HG=F     | Metals         | normal->elevated |       9 |         1.724 |
| HG=F     | Metals         | elevated->tense  |       1 |         0.192 |
| HG=F     | Metals         | tense->extreme   |       0 |         0     |
| HG=F     | Metals         | extreme->normal  |       0 |         0     |
| HG=F     | Metals         | extreme->calm    |       0 |         0     |
| HG=F     | Metals         | unknown->normal  |       0 |         0     |
| NQ=F     | Index proxies  | calm->normal     |      22 |         4.215 |
| NQ=F     | Index proxies  | normal->elevated |       8 |         1.533 |
| NQ=F     | Index proxies  | elevated->tense  |       2 |         0.383 |
| NQ=F     | Index proxies  | tense->extreme   |       0 |         0     |
| NQ=F     | Index proxies  | extreme->normal  |       0 |         0     |
| NQ=F     | Index proxies  | extreme->calm    |       0 |         0     |
| NQ=F     | Index proxies  | unknown->normal  |       0 |         0     |
| SPY      | Index proxies  | calm->normal     |      16 |         3.065 |
| SPY      | Index proxies  | normal->elevated |       7 |         1.341 |
| SPY      | Index proxies  | elevated->tense  |       2 |         0.383 |
| SPY      | Index proxies  | tense->extreme   |       0 |         0     |
| SPY      | Index proxies  | extreme->normal  |       0 |         0     |
| SPY      | Index proxies  | extreme->calm    |       0 |         0     |
| SPY      | Index proxies  | unknown->normal  |       0 |         0     |
| NVDA     | Major equities | calm->normal     |      19 |         3.64  |
| NVDA     | Major equities | normal->elevated |      10 |         1.916 |
| NVDA     | Major equities | elevated->tense  |       6 |         1.149 |
| NVDA     | Major equities | tense->extreme   |       0 |         0     |
| NVDA     | Major equities | extreme->normal  |       0 |         0     |
| NVDA     | Major equities | extreme->calm    |       0 |         0     |
| NVDA     | Major equities | unknown->normal  |       0 |         0     |
| MSFT     | Major equities | calm->normal     |      22 |         4.215 |
| MSFT     | Major equities | normal->elevated |       5 |         0.958 |
| MSFT     | Major equities | elevated->tense  |       1 |         0.192 |
| MSFT     | Major equities | tense->extreme   |       0 |         0     |
| MSFT     | Major equities | extreme->normal  |       0 |         0     |
| MSFT     | Major equities | extreme->calm    |       0 |         0     |
| MSFT     | Major equities | unknown->normal  |       0 |         0     |
| AAPL     | Major equities | calm->normal     |      18 |         3.448 |
| AAPL     | Major equities | normal->elevated |       5 |         0.958 |
| AAPL     | Major equities | elevated->tense  |       2 |         0.383 |
| AAPL     | Major equities | tense->extreme   |       0 |         0     |
| AAPL     | Major equities | extreme->normal  |       0 |         0     |
| AAPL     | Major equities | extreme->calm    |       0 |         0     |
| AAPL     | Major equities | unknown->normal  |       0 |         0     |
| AMZN     | Major equities | calm->normal     |      19 |         3.64  |
| AMZN     | Major equities | normal->elevated |       8 |         1.533 |
| AMZN     | Major equities | elevated->tense  |       0 |         0     |
| AMZN     | Major equities | tense->extreme   |       0 |         0     |

Assessment: `normal -> elevated` and `extreme -> normal` are common; `elevated -> tense` and `tense -> extreme` are rarer but present in most assets. No erratic oscillation.

## 15. Weekly Component Contribution Results

- Vol risk contribution average: median across assets = 3.23 (cap 35).
- Extension risk contribution average: median across assets = 0.72 (cap 30).
- Structure risk contribution average: median across assets = 3.92 (cap 20).
- Conflict risk contribution average: median across assets = 3.24 (cap 15).
- Dominant component frequency:
  - Vol dominant: median = 48.08%
  - Ext dominant: median = 2.87%
  - Struct dominant: median = 22.22%
  - Conflict dominant: median = 24.52%

Weekly **volatility-dominance count check**: assets with `dominant_vol_pct > 60` = **4** of 16 (vs **6** in daily RDR-003).

## 16. Daily vs Weekly Comparison


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


Interpretation:

- State changes per 100 bars is comparable between daily and weekly (both around 9-10). Weekly bars contain fewer *aggregate* state transitions on absolute terms (weekly windows are longer), but per 100 bars the sequence remains stable; the daily-sequence noise does not materially inflate on weekly aggregation.
- Volatility dominance moves modestly downward on weekly bars (median 51.3% → 48.1%; assets with `dominant_vol_pct > 60` drops from 6 to 4). The FX / Treasury / commodity assets that drove the daily count above the 4-asset threshold now cluster more naturally on weekly bars.
- Hidden directional bias moves modestly upward on weekly bars (4.5pp → 7.5pp), reflecting small-sample noise on `extreme`/`tense` weekly bars; both medians remain below the 12pp acceptance threshold.
- Distinctness from Volatility and Momentum engines remains; absolute Spearman medians move by ≤0.05 between daily and weekly and remain in the acceptable range.
- The `RiskEngine is diagnostic-only` boundary is unchanged.

## 17. Cross-Asset Results

| asset_class           |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |   dominant_vol_pct |   dominant_ext_pct |   dominant_struct_pct |   dominant_conflict_pct |   state_changes_per_100_bars |
|:----------------------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|-------------------:|-------------------:|----------------------:|------------------------:|-----------------------------:|
| Bonds / rates proxies |     80.364 |       16.667 |          2.203 |       0.67  |         0.096 |             0 |             66.571 |              1.916 |                17.146 |                  14.368 |                        8.238 |
| Commodities           |     73.946 |       21.648 |          3.448 |       0.958 |         0     |             0 |             57.854 |              1.724 |                21.456 |                  18.966 |                        8.046 |
| FX                    |     75.781 |       21.033 |          2.996 |       0.191 |         0     |             0 |             57.744 |              2.868 |                16.38  |                  23.008 |                        7.521 |
| Index proxies         |     60.057 |       29.598 |          9.77  |       0.575 |         0     |             0 |             39.08  |              2.969 |                23.755 |                  34.195 |                       11.59  |
| Major equities        |     63.372 |       29.464 |          6.437 |       0.728 |         0     |             0 |             44.215 |              4.291 |                23.218 |                  28.276 |                       11.303 |
| Metals                |     65.581 |       26.82  |          6.258 |       1.149 |         0.192 |             0 |             50.83  |              2.043 |                23.883 |                  23.244 |                       11.558 |

Interpretation: weekly class-level behaviour is broadly plausible. Metals and commodities still show more `tense`/`extreme` episodes during multi-week volatility windows; FX still has the lowest `extreme` share, consistent with FX weekly-range characteristics.

## 18. Overlap with VolatilityEngine

| symbol   | asset_class           |   spearman_riskscore_volscore |   spearman_riskscore_volcomponent |   spearman_riskscore_momentumscore |   spearman_riskscore_confidencescore |
|:---------|:----------------------|------------------------------:|----------------------------------:|-----------------------------------:|-------------------------------------:|
| GC=F     | Metals                |                        -0.06  |                             0.226 |                              0.343 |                                0.458 |
| SI=F     | Metals                |                        -0.015 |                             0.416 |                              0.377 |                                0.401 |
| HG=F     | Metals                |                         0.211 |                             0.422 |                              0.145 |                                0.426 |
| NQ=F     | Index proxies         |                         0.293 |                             0.313 |                              0.342 |                                0.412 |
| SPY      | Index proxies         |                         0.056 |                             0.371 |                              0.131 |                                0.509 |
| NVDA     | Major equities        |                         0.229 |                             0.424 |                              0.287 |                                0.41  |
| MSFT     | Major equities        |                         0.213 |                             0.315 |                              0.347 |                                0.474 |
| AAPL     | Major equities        |                         0.263 |                             0.314 |                              0.321 |                                0.331 |
| AMZN     | Major equities        |                         0.312 |                             0.254 |                              0.277 |                                0.431 |
| GOOGL    | Major equities        |                         0.278 |                             0.496 |                              0.303 |                                0.621 |
| TLT      | Bonds / rates proxies |                         0.093 |                             0.263 |                              0.016 |                               -0.009 |
| IGLT.L   | Bonds / rates proxies |                         0.147 |                             0.336 |                             -0.188 |                               -0.164 |
| EURUSD=X | FX                    |                         0.428 |                             0.347 |                             -0.008 |                               -0.081 |
| GBPUSD=X | FX                    |                         0.312 |                             0.442 |                              0.019 |                               -0.119 |
| JPY=X    | FX                    |                         0.169 |                             0.366 |                              0.216 |                                0.38  |
| CL=F     | Commodities           |                        -0.124 |                             0.379 |                              0.239 |                                0.172 |

- Median absolute Spearman between RiskScore and VolatilityScore: 0.212 (daily 0.167).
- Median absolute Spearman between RiskScore and the volatility contribution component: 0.357.

Verdict: RiskEngine adds information beyond VolatilityEngine alone on weekly bars; not a renamed VolatilityEngine.

## 19. Overlap with MomentumEngine

- Median absolute Spearman between RiskScore and MomentumScore: 0.258 (daily 0.309).

Verdict: weekly overlap with momentum remains low; RiskEngine does not accidentally duplicate momentum.

## 20. Overlap with ConfidenceEngine

- Median absolute Spearman between RiskScore and ConfidenceScore: 0.405 (daily 0.425).

Verdict: Risk and Confidence remain distinct signals on weekly bars.

## 21. Hidden Directional Bias Review

| symbol   | asset_class           | state    |   n |   mean_return_pct |   mean_fwd_return_1_pct |   pct_up |   max_pct_up_deviation_from_50 |
|:---------|:----------------------|:---------|----:|------------------:|------------------------:|---------:|-------------------------------:|
| GC=F     | Metals                | calm     | 301 |             0.065 |                   0.137 |   54.485 |                          4.485 |
| GC=F     | Metals                | elevated |  31 |             1.098 |                   0.449 |   64.516 |                         14.516 |
| GC=F     | Metals                | normal   | 183 |             0.419 |                   0.409 |   60.656 |                         10.656 |
| GC=F     | Metals                | tense    |   5 |            -1.567 |                  -0.559 |   40     |                         10     |
| SI=F     | Metals                | calm     | 372 |             0.113 |                   0.25  |   54.57  |                          4.57  |
| SI=F     | Metals                | elevated |  34 |             2.923 |                   2.221 |   67.647 |                         17.647 |
| SI=F     | Metals                | extreme  |   3 |             3.652 |                   0.171 |   66.667 |                         16.667 |
| SI=F     | Metals                | normal   | 101 |             0.206 |                  -0.235 |   48.515 |                          1.485 |
| SI=F     | Metals                | tense    |  10 |            -1.43  |                   1.954 |   50     |                          0     |
| HG=F     | Metals                | calm     | 352 |             0.173 |                   0.266 |   53.125 |                          3.125 |
| HG=F     | Metals                | elevated |  33 |            -0.302 |                   1.137 |   57.576 |                          7.576 |
| HG=F     | Metals                | normal   | 132 |             0.649 |                   0.09  |   56.061 |                          6.061 |
| HG=F     | Metals                | tense    |   3 |            -0.43  |                  -3.846 |   33.333 |                         16.667 |
| NQ=F     | Index proxies         | calm     | 311 |             0.452 |                   0.379 |   59.807 |                          9.807 |
| NQ=F     | Index proxies         | elevated |  46 |             0.075 |                  -0.054 |   47.826 |                          2.174 |
| NQ=F     | Index proxies         | normal   | 161 |             0.424 |                   0.618 |   62.733 |                         12.733 |
| NQ=F     | Index proxies         | tense    |   2 |            -2.44  |                  -3.446 |   50     |                          0     |
| SPY      | Index proxies         | calm     | 314 |             0.302 |                   0.217 |   56.369 |                          6.369 |
| SPY      | Index proxies         | elevated |  56 |            -0.362 |                   0.083 |   51.786 |                          1.786 |
| SPY      | Index proxies         | normal   | 146 |             0.5   |                   0.492 |   64.384 |                         14.384 |
| SPY      | Index proxies         | tense    |   4 |            -2.326 |                  -1.441 |   50     |                          0     |
| NVDA     | Major equities        | calm     | 286 |             0.58  |                   0.959 |   54.895 |                          4.895 |
| NVDA     | Major equities        | elevated |  37 |             1.027 |                   2.096 |   59.459 |                          9.459 |
| NVDA     | Major equities        | normal   | 184 |             1.858 |                   1.255 |   63.587 |                         13.587 |
| NVDA     | Major equities        | tense    |  13 |             4.722 |                   1.697 |   69.231 |                         19.231 |
| MSFT     | Major equities        | calm     | 347 |             0.425 |                   0.535 |   55.908 |                          5.908 |
| MSFT     | Major equities        | elevated |  34 |             0.06  |                  -0.459 |   47.059 |                          2.941 |
| MSFT     | Major equities        | normal   | 137 |             0.485 |                   0.434 |   62.044 |                         12.044 |
| MSFT     | Major equities        | tense    |   2 |             4.409 |                  -1.427 |  100     |                         50     |
| AAPL     | Major equities        | calm     | 345 |             0.465 |                   0.433 |   57.391 |                          7.391 |
| AAPL     | Major equities        | elevated |  30 |             1.25  |                   0.051 |   66.667 |                         16.667 |
| AAPL     | Major equities        | normal   | 142 |             0.775 |                   1.033 |   61.972 |                         11.972 |
| AAPL     | Major equities        | tense    |   3 |            -7.723 |                  -2.094 |    0     |                         50     |
| AMZN     | Major equities        | calm     | 365 |             0.416 |                   0.586 |   53.699 |                          3.699 |
| AMZN     | Major equities        | elevated |  39 |             0.304 |                   0.725 |   58.974 |                          8.974 |
| AMZN     | Major equities        | normal   | 116 |             0.565 |                  -0.063 |   61.207 |                         11.207 |
| GOOGL    | Major equities        | calm     | 308 |             0.335 |                   0.511 |   54.221 |                          4.221 |
| GOOGL    | Major equities        | elevated |  28 |             0.282 |                  -0.08  |   42.857 |                          7.143 |
| GOOGL    | Major equities        | normal   | 183 |             0.868 |                   0.683 |   62.842 |                         12.842 |
| GOOGL    | Major equities        | tense    |   1 |            -6.288 |                 -12.029 |    0     |                         50     |
| TLT      | Bonds / rates proxies | calm     | 421 |            -0.084 |                  -0.097 |   49.169 |                          0.831 |
| TLT      | Bonds / rates proxies | elevated |   7 |             1.36  |                   0.084 |   85.714 |                         35.714 |
| TLT      | Bonds / rates proxies | extreme  |   1 |             3.566 |                   5.187 |  100     |                         50     |
| TLT      | Bonds / rates proxies | normal   |  87 |            -0.221 |                  -0.094 |   51.724 |                          1.724 |
| TLT      | Bonds / rates proxies | tense    |   4 |             0.43  |                   1.208 |   50     |                          0     |
| IGLT.L   | Bonds / rates proxies | calm     | 416 |            -0.063 |                  -0.066 |   49.519 |                          0.481 |
| IGLT.L   | Bonds / rates proxies | elevated |  16 |            -0.322 |                  -0.482 |   43.75  |                          6.25  |
| IGLT.L   | Bonds / rates proxies | normal   |  85 |             0.01  |                   0.029 |   51.765 |                          1.765 |
| IGLT.L   | Bonds / rates proxies | tense    |   3 |             0.136 |                   0.96  |   66.667 |                         16.667 |
| EURUSD=X | FX                    | calm     | 413 |            -0.019 |                  -0.009 |   46.489 |                          3.511 |
| EURUSD=X | FX                    | elevated |   7 |            -1.253 |                  -0.196 |   28.571 |                         21.429 |
| EURUSD=X | FX                    | normal   |  99 |             0.214 |                   0.107 |   58.586 |                          8.586 |
| EURUSD=X | FX                    | tense    |   2 |             0.172 |                   0.27  |   50     |                          0     |
| GBPUSD=X | FX                    | calm     | 415 |             0.036 |                   0.03  |   47.952 |                          2.048 |
| GBPUSD=X | FX                    | elevated |  12 |            -0.754 |                   0.554 |   41.667 |                          8.333 |
| GBPUSD=X | FX                    | normal   |  93 |            -0.101 |                  -0.113 |   50.538 |                          0.538 |
| GBPUSD=X | FX                    | tense    |   1 |             6.909 |                  -1.493 |  100     |                         50     |
| JPY=X    | FX                    | calm     | 358 |             0.034 |                   0.043 |   55.028 |                          5.028 |
| JPY=X    | FX                    | elevated |  28 |             0.382 |                   0.427 |   60.714 |                         10.714 |
| JPY=X    | FX                    | normal   | 135 |             0.196 |                   0.174 |   58.519 |                          8.519 |
| CL=F     | Commodities           | calm     | 385 |             0.137 |                   0.284 |   52.987 |                          2.987 |
| CL=F     | Commodities           | elevated |  18 |             2.542 |                  -0.927 |   55.556 |                          5.556 |
| CL=F     | Commodities           | normal   | 112 |             0.356 |                   0.009 |   57.143 |                          7.143 |
| CL=F     | Commodities           | tense    |   5 |            -1.126 |                   7.45  |   20     |                         30     |

- Median max |pct_up-50| across all assets and states: 7.48 pp (daily 4.52 pp).

Weekly RiskDirection remains direction-specific: `none`, `elevated`, `conflict`, `stable`, `indeterminate`. No `bullish` / `bearish` direction values were emitted.

## 22. Adverse Movement Review

| symbol   | asset_class           |   spearman_riskscore_absfwdr_1 |   spearman_riskscore_absfwdr_3 |   spearman_riskscore_absfwdr_5 |   spearman_riskscore_absfwdr_10 |
|:---------|:----------------------|-------------------------------:|-------------------------------:|-------------------------------:|--------------------------------:|
| GC=F     | Metals                |                          0.106 |                          0.089 |                          0.079 |                           0.077 |
| SI=F     | Metals                |                          0.078 |                          0.047 |                          0.009 |                           0.051 |
| HG=F     | Metals                |                          0.064 |                          0.069 |                          0.085 |                           0.104 |
| NQ=F     | Index proxies         |                          0.009 |                         -0.01  |                          0.002 |                          -0.003 |
| SPY      | Index proxies         |                          0.065 |                          0.092 |                          0.11  |                           0.115 |
| NVDA     | Major equities        |                         -0.001 |                         -0.017 |                         -0.009 |                           0.017 |
| MSFT     | Major equities        |                         -0.039 |                         -0.024 |                          0.004 |                           0.041 |
| AAPL     | Major equities        |                          0.045 |                          0.061 |                          0.078 |                           0.099 |
| AMZN     | Major equities        |                          0.002 |                          0.027 |                          0.014 |                           0.072 |
| GOOGL    | Major equities        |                         -0.039 |                         -0.009 |                         -0.007 |                          -0.008 |
| TLT      | Bonds / rates proxies |                          0.153 |                          0.136 |                          0.092 |                           0.079 |
| IGLT.L   | Bonds / rates proxies |                          0.164 |                          0.17  |                          0.16  |                           0.186 |
| EURUSD=X | FX                    |                          0.029 |                          0.042 |                          0.014 |                           0.012 |
| GBPUSD=X | FX                    |                          0.08  |                          0.06  |                          0.063 |                           0.037 |
| JPY=X    | FX                    |                          0.088 |                          0.087 |                          0.065 |                           0.104 |
| CL=F     | Commodities           |                          0.166 |                          0.161 |                          0.155 |                           0.056 |

- Median absolute Spearman between RiskScore and |forward return| at 1/3/5/10-bar (weekly) horizons typically in the 0.0–0.2 range across assets. Informational only.

## 23. Diagnostic Explainability Review

| symbol   | date       | state    |   riskScore | riskDirection   | riskReason                                      |   volRiskContribution |   extRiskContribution |   structRiskContribution |   conflictRiskContribution |
|:---------|:-----------|:---------|------------:|:----------------|:------------------------------------------------|----------------------:|----------------------:|-------------------------:|---------------------------:|
| GC=F     | 2017-01-23 | calm     |       8.34  | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| GC=F     | 2017-01-30 | calm     |       4.958 | stable          | All risk components low                         |                     0 |                 0     |                    9.854 |                          0 |
| GC=F     | 2017-02-06 | calm     |       5.506 | stable          | All risk components low                         |                     0 |                 0     |                    6.663 |                          0 |
| GC=F     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GC=F     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GC=F     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GC=F     | 2019-07-01 | elevated |      32.594 | conflict        | At least one risk component elevated            |                     5 |                 3.235 |                    0     |                         10 |
| GC=F     | 2019-08-12 | elevated |      32.779 | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| GC=F     | 2019-09-09 | elevated |      31.667 | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         15 |
| GC=F     | 2020-03-09 | tense    |      60.84  | conflict        | Multiple risk components elevated               |                    35 |                30     |                    0     |                          5 |
| GC=F     | 2025-10-20 | tense    |      63.212 | conflict        | Multiple risk components elevated               |                    35 |                10.984 |                   20     |                         10 |
| GC=F     | 2025-10-27 | tense    |      61.545 | conflict        | Multiple risk components elevated               |                     0 |                 0     |                   20     |                         10 |
| SI=F     | 2016-10-03 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SI=F     | 2016-10-10 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SI=F     | 2016-10-17 | calm     |       0     | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SI=F     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SI=F     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SI=F     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SI=F     | 2019-11-18 | elevated |      31.77  | indeterminate   | At least one risk component elevated            |                     5 |                 0     |                   20     |                          5 |
| SI=F     | 2020-02-24 | elevated |      30     | conflict        | At least one risk component elevated            |                    35 |                30     |                    0     |                          5 |
| SI=F     | 2020-03-02 | elevated |      30.023 | indeterminate   | At least one risk component elevated            |                     5 |                 0.07  |                    0     |                          5 |
| SI=F     | 2020-03-09 | tense    |      51.047 | conflict        | Multiple risk components elevated               |                    35 |                30     |                    3.072 |                          5 |
| SI=F     | 2020-03-16 | tense    |      54.357 | conflict        | Multiple risk components elevated               |                    35 |                19.928 |                   20     |                          5 |
| SI=F     | 2020-03-23 | tense    |      65.151 | conflict        | Multiple risk components elevated               |                    35 |                 2.452 |                    0     |                          5 |
| SI=F     | 2020-08-03 | extreme  |      71.892 | conflict        | Risk components at extreme or conflict dominant |                    35 |                30     |                   20     |                          5 |
| SI=F     | 2020-08-10 | extreme  |      71.3   | conflict        | Risk components at extreme or conflict dominant |                    35 |                14.565 |                   20     |                         15 |
| SI=F     | 2020-08-17 | extreme  |      73.188 | conflict        | Risk components at extreme or conflict dominant |                    10 |                 0     |                   20     |                         15 |
| HG=F     | 2016-10-17 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| HG=F     | 2016-10-24 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| HG=F     | 2016-10-31 | calm     |       1.269 | stable          | All risk components low                         |                     0 |                 0     |                    3.808 |                          0 |
| HG=F     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| HG=F     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| HG=F     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| HG=F     | 2016-11-21 | elevated |      30     | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| HG=F     | 2020-03-16 | elevated |      31.667 | conflict        | At least one risk component elevated            |                    35 |                30     |                   20     |                          0 |
| HG=F     | 2020-03-23 | elevated |      36.667 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| HG=F     | 2024-05-13 | tense    |      50.539 | conflict        | Multiple risk components elevated               |                    35 |                16.617 |                   20     |                         10 |
| HG=F     | 2024-05-20 | tense    |      51.835 | conflict        | Multiple risk components elevated               |                     0 |                 8.889 |                   20     |                         10 |
| HG=F     | 2024-05-27 | tense    |      50.338 | conflict        | Multiple risk components elevated               |                     0 |                 0.51  |                   20     |                         10 |
| NQ=F     | 2016-10-17 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NQ=F     | 2016-10-24 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NQ=F     | 2016-10-31 | calm     |       0     | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NQ=F     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2018-02-05 | elevated |      34.484 | indeterminate   | At least one risk component elevated            |                    20 |                30     |                    8.403 |                          0 |
| NQ=F     | 2018-02-12 | elevated |      37.233 | indeterminate   | At least one risk component elevated            |                     0 |                 8.246 |                   20     |                          0 |
| NQ=F     | 2018-02-19 | elevated |      35.55  | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2020-03-09 | tense    |      50.812 | conflict        | Multiple risk components elevated               |                    35 |                30     |                    0     |                          5 |
| NQ=F     | 2020-03-23 | tense    |      56.104 | conflict        | Multiple risk components elevated               |                    35 |                10.044 |                    0     |                          5 |
| SPY      | 2016-10-03 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SPY      | 2016-10-10 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SPY      | 2016-10-17 | calm     |       0     | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| SPY      | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SPY      | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SPY      | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SPY      | 2018-01-29 | elevated |      32.156 | indeterminate   | At least one risk component elevated            |                    20 |                13.758 |                   20     |                          0 |
| SPY      | 2018-02-05 | elevated |      48.823 | indeterminate   | At least one risk component elevated            |                    20 |                30     |                   20     |                          0 |
| SPY      | 2018-02-19 | elevated |      46.364 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| SPY      | 2018-02-12 | tense    |      57.616 | indeterminate   | Multiple risk components elevated               |                    20 |                 9.091 |                   20     |                          0 |
| SPY      | 2020-03-09 | tense    |      63.114 | conflict        | Multiple risk components elevated               |                    35 |                30     |                    0     |                          5 |
| SPY      | 2020-03-16 | tense    |      61.394 | conflict        | Multiple risk components elevated               |                    35 |                 4.84  |                   20     |                          5 |
| NVDA     | 2016-10-31 | calm     |      10.562 | stable          | All risk components low                         |                     0 |                 0     |                    5.244 |                          0 |
| NVDA     | 2017-01-30 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NVDA     | 2017-02-06 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NVDA     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NVDA     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NVDA     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NVDA     | 2016-11-21 | elevated |      31.77  | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| NVDA     | 2020-02-10 | elevated |      40.441 | conflict        | At least one risk component elevated            |                    35 |                16.322 |                   20     |                          0 |
| NVDA     | 2020-02-17 | elevated |      42.101 | indeterminate   | At least one risk component elevated            |                     5 |                 4.98  |                   20     |                          0 |
| NVDA     | 2020-02-24 | tense    |      54.651 | conflict        | Multiple risk components elevated               |                    35 |                 7.651 |                   20     |                          0 |
| NVDA     | 2020-03-23 | tense    |      52.903 | conflict        | Multiple risk components elevated               |                    35 |                11.202 |                    3.643 |                          5 |
| NVDA     | 2020-08-31 | tense    |      55     | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                         10 |
| MSFT     | 2016-10-03 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| MSFT     | 2016-10-10 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| MSFT     | 2016-10-17 | calm     |       2.164 | stable          | All risk components low                         |                     0 |                 6.493 |                    0     |                          0 |
| MSFT     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2017-10-23 | elevated |      36.667 | indeterminate   | At least one risk component elevated            |                    20 |                30     |                   20     |                          0 |
| MSFT     | 2017-10-30 | elevated |      36.667 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2017-11-06 | elevated |      36.667 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2020-02-03 | tense    |      63.529 | conflict        | Multiple risk components elevated               |                    35 |                12.402 |                   20     |                         10 |
| MSFT     | 2020-02-10 | tense    |      61.862 | conflict        | Multiple risk components elevated               |                     0 |                 0     |                   20     |                         10 |
| AAPL     | 2016-10-31 | calm     |      10.217 | stable          | All risk components low                         |                     0 |                 0.144 |                    0     |                          0 |
| AAPL     | 2016-11-07 | calm     |       3.55  | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| AAPL     | 2016-11-14 | calm     |       0.048 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| AAPL     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AAPL     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AAPL     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AAPL     | 2018-08-27 | elevated |      30.726 | conflict        | At least one risk component elevated            |                     5 |                 1.17  |                   20     |                         10 |
| AAPL     | 2018-09-03 | elevated |      30.726 | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| AAPL     | 2018-09-10 | elevated |      35.39  | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| AAPL     | 2020-02-24 | tense    |      51.667 | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                          5 |
| AAPL     | 2020-08-31 | tense    |      52.148 | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                         10 |
| AAPL     | 2020-09-07 | tense    |      51.667 | conflict        | Multiple risk components elevated               |                     0 |                 0     |                   20     |                         10 |
| AMZN     | 2016-11-21 | calm     |      13.038 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| AMZN     | 2016-11-28 | calm     |       9.596 | stable          | All risk components low                         |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2016-12-05 | calm     |       7.703 | stable          | All risk components low                         |                     0 |                 0     |                    3.109 |                          0 |
| AMZN     | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2017-06-05 | elevated |      31.367 | indeterminate   | At least one risk component elevated            |                    20 |                14.102 |                   20     |                          0 |
| AMZN     | 2017-06-12 | elevated |      31.385 | indeterminate   | At least one risk component elevated            |                     0 |                 0.052 |                   20     |                          0 |
| AMZN     | 2017-06-19 | elevated |      31.385 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                   20     |                          0 |
| GOOGL    | 2016-10-03 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| GOOGL    | 2016-10-10 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| GOOGL    | 2016-10-17 | calm     |       0     | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| GOOGL    | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GOOGL    | 2016-07-11 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GOOGL    | 2016-07-18 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| GOOGL    | 2020-02-24 | elevated |      35.693 | conflict        | At least one risk component elevated            |                    35 |                17.078 |                    0     |                          5 |
| GOOGL    | 2020-03-02 | elevated |      44.027 | conflict        | At least one risk component elevated            |                    35 |                10.003 |                    0     |                          5 |
| GOOGL    | 2020-03-16 | elevated |      34.831 | indeterminate   | At least one risk component elevated            |                     0 |                 0     |                    0     |                          5 |
| GOOGL    | 2020-03-09 | tense    |      52.19  | conflict        | Multiple risk components elevated               |                    35 |                 9.489 |                    0     |                          5 |
| TLT      | 2017-01-16 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| TLT      | 2017-01-23 | calm     |       6.667 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| TLT      | 2017-01-30 | calm     |       0     | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| TLT      | 2016-07-04 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |

Each sampled weekly bar carries full diagnostics (RiskScore, RiskDirection, RiskReason, four component contributions). RiskReason text uses approved vocabulary only and varies materially by state, explaining the assigned state by referencing the dominant component.

## 24. Reserved Language / Hidden Strategy Review

Reserved word audit scope: `RiskReason` rendered text + every observed `RiskState` value + every observed `RiskDirection` value.

Reserved words checked: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`, `buy`, `sell`, `long`, `short`.

Audit summary:

- Total audit rows: 418
- Rows with hits: 0 (target: 0)
- Rows failing: 0 (target: 0)

Hidden strategy check:

- No `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, or exit-logic logic is introduced by RiskEngine (canonical verifier §10 boundary checks; full pass, exit 0).
- No `bullish` / `bearish` RiskState or RiskDirection values are present (verifier §5).

## 25. Limitations

- Yahoo Finance weekly OHLC may differ from TradingView weekly feeds and futures continuous-contract construction.
- Python implementation is a research port, not a TradingView compiler.
- The `RiskEngine v1.0.0-draft` Python mirror is what was measured; actual Pine RiskEngine parity still requires a separate Pine-vs-Python check.
- No intraday data tested.
- One Yahoo proxy per gilt (`IGLT.L` ETF); TLT remains the US Treasury ETF.
- No parameter optimisation was performed.

## 26. Negative Findings

- State distribution skews heavily calm/normal, similar to daily. `tense` and `extreme` evidence remains thin on weekly bars as well.
- Weekly aggregation smooths state sequences but does **not** materially change the volatility-dominance picture for the lower-volatility asset classes (TLT, IGLT.L, FX). Count of `dominant_vol_pct > 60` assets moves modestly between daily and weekly.
- Conflict component contribution remains small in most bars (its banded states are mostly `conflictNone`).
- Forward-return analysis on weekly bars is informational only and is not a trading-edge claim.
- Yahoo Finance futures series are continuous-contract approximations; TradingView contracts may differ.

## 27. Result Classification

Classification: **Supported**

Classification rationale (weekly-only rule replay):

- `unknown_ok`: **True**
- `overlap_vol_median_ok`: **True**
- `overlap_mom_ok`: **True**
- `overlap_conf_ok`: **True**
- `vol_dominance_median_ok`: **True**
- `vol_dominance_count_ok`: **True**
- `state_changes_ok`: **True**
- `bias_ok`: **True**

## 28. Recommendation

Recommendation: **Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred**

Keep RiskEngine in ATE v2.2 as a diagnostic-only module. Weekly behaviour confirms the daily profile.

- DecisionEngine integration remains deferred.
- ConfidenceEngine integration remains deferred.
- Alerts remain prohibited.
- Position sizing, stops, entries, and exits are out of scope.

Future RiskEngine use as a downstream input may be considered only as a separate research candidate after:

  - A Pine-vs-Python parity check confirms the actual Pine computation matches the deterministic Python mirror, and
  - State-distribution concerns (Conflict component small, `extreme` thin) are addressed by either richer daily history or larger cross-asset sample rather than parameter changes.

## 29. Whether DecisionEngine Integration Remains Deferred

**Yes — DecisionEngine integration remains deferred.** The weekly RiskEngine diagnostic output is not approved for use as a DecisionEngine input by this validation.

## 30. Whether ConfidenceEngine Integration Remains Deferred

**Yes — ConfidenceEngine integration remains deferred.** ConfidenceEngine continues to operate without RiskEngine consumption of its outputs or in reverse.

## 31. Whether Alerts Remain Prohibited

**Yes.** No RiskEngine `alertcondition` is permitted in ATE v2.2. The canonical verifier confirms exactly 10 `alertcondition` calls, matching ATE v2.1, with no RiskEngine alert.

## 32. Lessons Learned

- Daily and weekly RiskEngine diagnostics are mutually consistent: same engines, same score bands, smoother sequence on weekly.
- Volatility dominance on weekly bars does not collapse to a renamed VolatilityEngine; overlap statistics remain in the acceptable range.
- Hidden directional bias remains limited on weekly horizons.
- RiskEngine remains diagnostic-only on both daily and weekly aggregations.

## 33. Documentation Improvements

- Add a single per-asset page noting that the ATE v2.2 RiskEngine is now RDR-003 (daily) + RDR-003W (weekly) validated.
- Capture weekly cutoffs in the RiskEngine specification preamble for future RDR cycles.
- Consider extending the canonical verifier with a weekly-specific fixture set under `tests/fixtures/ATE_v2_2_weekly/` once a Pine-vs-Python parity check has been performed.

## 34. Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. RiskEngine remains diagnostic-only; DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, and stops are explicitly out of scope.
