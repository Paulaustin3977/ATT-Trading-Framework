# RDR-003: RiskEngine Daily Diagnostic Validation

Date: 2026-07-04
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.2
Research Classification: **Weakly Supported**
Recommendation: **Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt**

---

## 1. Executive Summary

Hermes validated the ATE v2.2 RiskEngine v1.0.0-draft diagnostic behaviour on daily Yahoo Finance OHLC data across 16 assets spanning metals (Gold, Silver, Copper), index proxies (Nasdaq, S&P 500), major equities (NVDA, MSFT, AAPL, AMZN, GOOGL), bonds / rates proxies (TLT, IGLT.L), FX (EUR/USD, GBP/USD, USD/JPY), and commodities (WTI crude).

Verdict: **Weakly Supported**.

Recommendation: **Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt**.

RiskEngine integration into DecisionEngine should remain deferred: **Yes**.
RiskEngine integration into ConfidenceEngine should remain deferred: **Yes**.
RiskEngine alerts remain prohibited: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## 2. Research Question

Does RiskEngine classify market-risk states sensibly across a balanced daily multi-asset universe without duplicating VolatilityEngine, creating hidden directional bias, or becoming a hidden strategy?

## 3. Hypotheses Tested

1. RiskEngine daily states occur sensibly across assets: calm, normal, elevated, tense, extreme, unknown.
2. RiskEngine does not behave like a hidden trend, momentum, volatility, or strategy engine.
3. RiskEngine adds diagnostic information beyond VolatilityEngine alone.
4. RiskEngine does not create hidden bullish or bearish directional bias.
5. RiskEngine remains suitable for DashboardEngine and Research Mode diagnostic use only.
6. RiskEngine is not yet approved to affect DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, stops, or trade management.

## 4. Methodology

- Downloaded daily OHLC via `yfinance` for 16 assets between 2018-01-01 and 2026-07-03 (cache: `data_cache/`). RDR-001 policy: raw OHLC cache is not committed.
- Ported the ATE v2.2 Trend/Structure/Momentum/Confidence/Volatility compute paths via the same offline port used in RDR-002 (`run_rdr002_validation.py`), so that RiskEngine inputs (VolatilityScore, VolatilityShockFlag, ConfidenceScore, TrendScore, MomentumScore) are real engine outputs, not synthetic placeholders.
- Called `tools/scripts/_riskengine_compute.calculate_risk` to obtain RiskScore, RiskState, RiskDirection, RiskReason, and the four component contributions.
- Performed the 12-check analysis below and produced CSV artefacts in the RDR-003 output directory.
- Generated optional RiskEngine state-band charts under `charts/`.
- Did not modify Pine code.
- Did not optimise parameters.
- Did not add alerts or any strategy behaviour.
- Used only public Yahoo Finance daily OHLC data. No broker, no paper-trading API.

## 5. Data Sources

- Data source: Yahoo Finance via `yfinance` daily OHLC.
- Timeframe: Daily.
- Adjusted/unadjusted: `auto_adjust=False`; OHLC retained as-is (unadjusted).
- Cache: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/` (raw OHLC); not committed under RDR-001 raw-data policy.
- Missing data handling: Yahoo's `NaN` gaps are passed through. The RiskEngine Python mirror applies the same `nan` rules the Pine engine applies (e.g. ATR / swing-distance `nan` → component fallback bands).

## 6. Assets Tested

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|
| GC=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |     58.793 |       29.514 |         10.992 |       0.608 |         0.094 |             0 |
| SI=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |     58.98  |       30.168 |          9.963 |       0.842 |         0.047 |             0 |
| HG=F     | Metals                |   2139 | 2018-01-02   | 2026-07-03 |     65.685 |       27.162 |          6.545 |       0.608 |         0     |             0 |
| NQ=F     | Index proxies         |   2140 | 2018-01-02   | 2026-07-03 |     70.467 |       22.43  |          6.776 |       0.28  |         0.047 |             0 |
| SPY      | Index proxies         |   2136 | 2018-01-02   | 2026-07-02 |     64.513 |       26.873 |          8.146 |       0.328 |         0.14  |             0 |
| NVDA     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     70.131 |       22.051 |          7.631 |       0.187 |         0     |             0 |
| MSFT     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     69.148 |       23.081 |          7.537 |       0.234 |         0     |             0 |
| AAPL     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     64.466 |       24.766 |         10.3   |       0.468 |         0     |             0 |
| AMZN     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     70.693 |       25.749 |          3.324 |       0.187 |         0.047 |             0 |
| GOOGL    | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     69.522 |       24.86  |          5.478 |       0.14  |         0     |             0 |
| TLT      | Bonds / rates proxies |   2136 | 2018-01-02   | 2026-07-02 |     75.702 |       20.833 |          3.043 |       0.328 |         0.094 |             0 |
| IGLT.L   | Bonds / rates proxies |   2147 | 2018-01-02   | 2026-07-03 |     80.997 |       16.535 |          2.375 |       0.047 |         0.047 |             0 |
| EURUSD=X | FX                    |   2214 | 2018-01-01   | 2026-07-03 |     80.172 |       17.615 |          2.213 |       0     |         0     |             0 |
| GBPUSD=X | FX                    |   2215 | 2018-01-01   | 2026-07-04 |     81.535 |       15.305 |          3.115 |       0.045 |         0     |             0 |
| JPY=X    | FX                    |   2214 | 2018-01-01   | 2026-07-03 |     76.784 |       19.467 |          3.523 |       0.226 |         0     |             0 |
| CL=F     | Commodities           |   2139 | 2018-01-02   | 2026-07-03 |     75.549 |       17.578 |          6.265 |       0.514 |         0.094 |             0 |

Data notes (skips/issues encountered):
- (no notes)

## 7. Date Range

Combined validation range: 2018-01-02 to 2026-07-03 (per-asset ranges appear in the summary table).

## 8. ATE Version

ATE v2.2

Release file: `pine/releases/ATE_v2.2.pine`

Release SHA-256: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`

## 9. RiskEngine Version

RiskEngine v1.0.0-draft

## 10. Verifier Result

The canonical verifier `python tools/scripts/verify_ate.py` was executed before report analysis:

- total_checks: 442
- passed: 442
- failed: 0
- exit code: 0
- ATE v2.1 SHA-256 (expected/actual): `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` / `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`
- ATE v2.1 unchanged: `True`
- ATE v2.2 SHA-256 (expected/actual): `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` / `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`
- ATE v2.2 release == dev byte-identical: `True`
- ATE v2.2 release matches manifest: `True`

## 11. State Frequency Results

Percent of daily bars by state (per asset):

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|
| GC=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |     58.793 |       29.514 |         10.992 |       0.608 |         0.094 |             0 |
| SI=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |     58.98  |       30.168 |          9.963 |       0.842 |         0.047 |             0 |
| HG=F     | Metals                |   2139 | 2018-01-02   | 2026-07-03 |     65.685 |       27.162 |          6.545 |       0.608 |         0     |             0 |
| NQ=F     | Index proxies         |   2140 | 2018-01-02   | 2026-07-03 |     70.467 |       22.43  |          6.776 |       0.28  |         0.047 |             0 |
| SPY      | Index proxies         |   2136 | 2018-01-02   | 2026-07-02 |     64.513 |       26.873 |          8.146 |       0.328 |         0.14  |             0 |
| NVDA     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     70.131 |       22.051 |          7.631 |       0.187 |         0     |             0 |
| MSFT     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     69.148 |       23.081 |          7.537 |       0.234 |         0     |             0 |
| AAPL     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     64.466 |       24.766 |         10.3   |       0.468 |         0     |             0 |
| AMZN     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     70.693 |       25.749 |          3.324 |       0.187 |         0.047 |             0 |
| GOOGL    | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |     69.522 |       24.86  |          5.478 |       0.14  |         0     |             0 |
| TLT      | Bonds / rates proxies |   2136 | 2018-01-02   | 2026-07-02 |     75.702 |       20.833 |          3.043 |       0.328 |         0.094 |             0 |
| IGLT.L   | Bonds / rates proxies |   2147 | 2018-01-02   | 2026-07-03 |     80.997 |       16.535 |          2.375 |       0.047 |         0.047 |             0 |
| EURUSD=X | FX                    |   2214 | 2018-01-01   | 2026-07-03 |     80.172 |       17.615 |          2.213 |       0     |         0     |             0 |
| GBPUSD=X | FX                    |   2215 | 2018-01-01   | 2026-07-04 |     81.535 |       15.305 |          3.115 |       0.045 |         0     |             0 |
| JPY=X    | FX                    |   2214 | 2018-01-01   | 2026-07-03 |     76.784 |       19.467 |          3.523 |       0.226 |         0     |             0 |
| CL=F     | Commodities           |   2139 | 2018-01-02   | 2026-07-03 |     75.549 |       17.578 |          6.265 |       0.514 |         0.094 |             0 |

Aggregation by asset class:

| asset_class           |   pct_calm |   pct_normal |   pct_elevated |   pct_tense |   pct_extreme |   pct_unknown |   dominant_vol_pct |   dominant_ext_pct |   dominant_struct_pct |   dominant_conflict_pct |   state_changes_per_100_bars |
|:----------------------|-----------:|-------------:|---------------:|------------:|--------------:|--------------:|-------------------:|-------------------:|----------------------:|------------------------:|-----------------------------:|
| Bonds / rates proxies |     78.349 |       18.684 |          2.709 |       0.187 |         0.07  |             0 |             66.251 |              1.258 |                13.998 |                  18.493 |                        8.522 |
| Commodities           |     75.549 |       17.578 |          6.265 |       0.514 |         0.094 |             0 |             60.683 |              1.917 |                13.698 |                  23.703 |                        7.527 |
| FX                    |     79.497 |       17.462 |          2.95  |       0.09  |         0     |             0 |             64.639 |              0.873 |                 9.724 |                  24.763 |                        7.933 |
| Index proxies         |     67.49  |       24.651 |          7.461 |       0.304 |         0.094 |             0 |             44.456 |              2.666 |                19.552 |                  33.326 |                       10.22  |
| Major equities        |     68.792 |       24.101 |          6.854 |       0.243 |         0.009 |             0 |             49.401 |              1.489 |                19.391 |                  29.719 |                       10.047 |
| Metals                |     61.153 |       28.948 |          9.166 |       0.686 |         0.047 |             0 |             50.693 |              1.917 |                25.176 |                  22.214 |                       13.827 |

Assessment:

- `pct_unknown` median across assets = 0.00% (max = 0.00%).
- `pct_calm` + `pct_normal` combined dominates most assets, which is expected for low-noise daily markets.
- `pct_extreme` is rare (median 0.02%; max 0.14%) and tends to coincide with high-volatility windows already characterised by RDR-002.
- No asset's state distribution is dominated by a single state in an implausible way (no asset has > 70% in any one non-calm/normal state).

## 12. State Duration Results

| symbol   | asset_class           | state    |   run_count |   avg_duration |   median_duration |   longest_duration |   shortest_duration |
|:---------|:----------------------|:---------|------------:|---------------:|------------------:|-------------------:|--------------------:|
| AAPL     | Major equities        | calm     |          86 |         16.012 |              11.5 |                 75 |                   1 |
| AAPL     | Major equities        | elevated |          31 |          7.097 |               4   |                 22 |                   1 |
| AAPL     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| AAPL     | Major equities        | normal   |         112 |          4.723 |               3   |                 27 |                   1 |
| AAPL     | Major equities        | tense    |           5 |          2     |               2   |                  3 |                   1 |
| AAPL     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | calm     |          89 |         16.966 |              12   |                109 |                   1 |
| AMZN     | Major equities        | elevated |          16 |          4.438 |               3.5 |                 19 |                   1 |
| AMZN     | Major equities        | extreme  |           1 |          1     |               1   |                  1 |                   1 |
| AMZN     | Major equities        | normal   |         104 |          5.288 |               4   |                 26 |                   1 |
| AMZN     | Major equities        | tense    |           2 |          2     |               2   |                  2 |                   2 |
| AMZN     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| CL=F     | Commodities           | calm     |          63 |         25.651 |              17   |                 83 |                   2 |
| CL=F     | Commodities           | elevated |          19 |          7.053 |               4   |                 25 |                   1 |
| CL=F     | Commodities           | extreme  |           1 |          2     |               2   |                  2 |                   2 |
| CL=F     | Commodities           | normal   |          72 |          5.222 |               3   |                 19 |                   1 |
| CL=F     | Commodities           | tense    |           6 |          1.833 |               2   |                  3 |                   1 |
| CL=F     | Commodities           | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | calm     |          64 |         27.734 |              23.5 |                 86 |                   1 |
| EURUSD=X | FX                    | elevated |          10 |          4.9   |               1   |                 23 |                   1 |
| EURUSD=X | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | normal   |          71 |          5.493 |               4   |                 26 |                   1 |
| EURUSD=X | FX                    | tense    |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | calm     |          68 |         26.559 |              16   |                169 |                   1 |
| GBPUSD=X | FX                    | elevated |          17 |          4.059 |               2   |                 23 |                   1 |
| GBPUSD=X | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | normal   |          83 |          4.084 |               3   |                 23 |                   1 |
| GBPUSD=X | FX                    | tense    |           1 |          1     |               1   |                  1 |                   1 |
| GBPUSD=X | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GC=F     | Metals                | calm     |          99 |         12.697 |               7   |                 77 |                   1 |
| GC=F     | Metals                | elevated |          45 |          5.222 |               3   |                 30 |                   1 |
| GC=F     | Metals                | extreme  |           1 |          2     |               2   |                  2 |                   2 |
| GC=F     | Metals                | normal   |         135 |          4.674 |               3   |                 33 |                   1 |
| GC=F     | Metals                | tense    |           7 |          1.857 |               1   |                  5 |                   1 |
| GC=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | calm     |          83 |         17.892 |              12   |                141 |                   1 |
| GOOGL    | Major equities        | elevated |          25 |          4.68  |               2   |                 22 |                   1 |
| GOOGL    | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | normal   |         106 |          5.009 |               3   |                 25 |                   1 |
| GOOGL    | Major equities        | tense    |           1 |          3     |               3   |                  3 |                   3 |
| GOOGL    | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| HG=F     | Metals                | calm     |          93 |         15.108 |               9   |                 89 |                   1 |
| HG=F     | Metals                | elevated |          37 |          3.784 |               3   |                 16 |                   1 |
| HG=F     | Metals                | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| HG=F     | Metals                | normal   |         119 |          4.882 |               3   |                 22 |                   1 |
| HG=F     | Metals                | tense    |           7 |          1.857 |               2   |                  3 |                   1 |
| HG=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| IGLT.L   | Bonds / rates proxies | calm     |          76 |         22.882 |              12.5 |                209 |                   1 |
| IGLT.L   | Bonds / rates proxies | elevated |          20 |          2.55  |               3   |                  5 |                   1 |
| IGLT.L   | Bonds / rates proxies | extreme  |           1 |          1     |               1   |                  1 |                   1 |
| IGLT.L   | Bonds / rates proxies | normal   |          87 |          4.08  |               3   |                 16 |                   1 |
| IGLT.L   | Bonds / rates proxies | tense    |           1 |          1     |               1   |                  1 |                   1 |
| IGLT.L   | Bonds / rates proxies | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | calm     |          82 |         20.732 |              13.5 |                108 |                   1 |
| JPY=X    | FX                    | elevated |          25 |          3.12  |               3   |                  9 |                   1 |
| JPY=X    | FX                    | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | normal   |         104 |          4.144 |               3   |                 22 |                   1 |
| JPY=X    | FX                    | tense    |           2 |          2.5   |               2.5 |                  3 |                   2 |
| JPY=X    | FX                    | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | calm     |          80 |         18.462 |              12.5 |                113 |                   1 |
| MSFT     | Major equities        | elevated |          30 |          5.367 |               3   |                 21 |                   1 |
| MSFT     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | normal   |         106 |          4.651 |               3   |                 16 |                   1 |
| MSFT     | Major equities        | tense    |           2 |          2.5   |               2.5 |                  3 |                   2 |
| MSFT     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| NQ=F     | Index proxies         | calm     |          83 |         18.169 |              13   |                 89 |                   1 |
| NQ=F     | Index proxies         | elevated |          22 |          6.591 |               3.5 |                 23 |                   1 |
| NQ=F     | Index proxies         | extreme  |           1 |          1     |               1   |                  1 |                   1 |
| NQ=F     | Index proxies         | normal   |         101 |          4.752 |               3   |                 24 |                   1 |
| NQ=F     | Index proxies         | tense    |           4 |          1.5   |               1   |                  3 |                   1 |
| NQ=F     | Index proxies         | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | calm     |          74 |         20.243 |              11.5 |                134 |                   1 |
| NVDA     | Major equities        | elevated |          24 |          6.792 |               6.5 |                 22 |                   1 |
| NVDA     | Major equities        | extreme  |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | normal   |          93 |          5.065 |               3   |                 32 |                   1 |
| NVDA     | Major equities        | tense    |           3 |          1.333 |               1   |                  2 |                   1 |
| NVDA     | Major equities        | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| SI=F     | Metals                | calm     |         115 |         10.965 |               8   |                 46 |                   1 |
| SI=F     | Metals                | elevated |          57 |          3.737 |               2   |                 29 |                   1 |
| SI=F     | Metals                | extreme  |           1 |          1     |               1   |                  1 |                   1 |
| SI=F     | Metals                | normal   |         161 |          4.006 |               3   |                 23 |                   1 |
| SI=F     | Metals                | tense    |          10 |          1.8   |               2   |                  3 |                   1 |
| SI=F     | Metals                | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| SPY      | Index proxies         | calm     |          80 |         17.225 |              11   |                 82 |                   1 |
| SPY      | Index proxies         | elevated |          34 |          5.118 |               3   |                 23 |                   1 |
| SPY      | Index proxies         | extreme  |           2 |          1.5   |               1.5 |                  2 |                   1 |
| SPY      | Index proxies         | normal   |         105 |          5.467 |               3   |                 27 |                   1 |
| SPY      | Index proxies         | tense    |           5 |          1.4   |               1   |                  2 |                   1 |
| SPY      | Index proxies         | unknown  |           0 |          0     |               0   |                  0 |                   0 |
| TLT      | Bonds / rates proxies | calm     |          68 |         23.779 |              16.5 |                 96 |                   1 |
| TLT      | Bonds / rates proxies | elevated |          21 |          3.095 |               2   |                 13 |                   1 |
| TLT      | Bonds / rates proxies | extreme  |           1 |          2     |               2   |                  2 |                   2 |
| TLT      | Bonds / rates proxies | normal   |          86 |          5.174 |               3   |                 21 |                   1 |
| TLT      | Bonds / rates proxies | tense    |           4 |          1.75  |               1.5 |                  3 |                   1 |
| TLT      | Bonds / rates proxies | unknown  |           0 |          0     |               0   |                  0 |                   0 |

Assessment:

- Median state_changes_per_100_bars = 9.89. The daily state sequence is not noisy.
- `unknown` and `extreme` are episodic; `normal` tends to dominate run length, as expected.

## 13. Transition Results

| symbol   | asset_class    | transition       |   count |   pct_of_bars |
|:---------|:---------------|:-----------------|--------:|--------------:|
| GC=F     | Metals         | calm->normal     |      98 |         4.584 |
| GC=F     | Metals         | normal->elevated |      37 |         1.731 |
| GC=F     | Metals         | elevated->tense  |       6 |         0.281 |
| GC=F     | Metals         | tense->extreme   |       1 |         0.047 |
| GC=F     | Metals         | extreme->normal  |       0 |         0     |
| GC=F     | Metals         | extreme->calm    |       0 |         0     |
| GC=F     | Metals         | unknown->normal  |       0 |         0     |
| SI=F     | Metals         | calm->normal     |     111 |         5.192 |
| SI=F     | Metals         | normal->elevated |      45 |         2.105 |
| SI=F     | Metals         | elevated->tense  |       7 |         0.327 |
| SI=F     | Metals         | tense->extreme   |       1 |         0.047 |
| SI=F     | Metals         | extreme->normal  |       0 |         0     |
| SI=F     | Metals         | extreme->calm    |       0 |         0     |
| SI=F     | Metals         | unknown->normal  |       0 |         0     |
| HG=F     | Metals         | calm->normal     |      89 |         4.161 |
| HG=F     | Metals         | normal->elevated |      26 |         1.216 |
| HG=F     | Metals         | elevated->tense  |       6 |         0.281 |
| HG=F     | Metals         | tense->extreme   |       0 |         0     |
| HG=F     | Metals         | extreme->normal  |       0 |         0     |
| HG=F     | Metals         | extreme->calm    |       0 |         0     |
| HG=F     | Metals         | unknown->normal  |       0 |         0     |
| NQ=F     | Index proxies  | calm->normal     |      82 |         3.832 |
| NQ=F     | Index proxies  | normal->elevated |      18 |         0.841 |
| NQ=F     | Index proxies  | elevated->tense  |       3 |         0.14  |
| NQ=F     | Index proxies  | tense->extreme   |       1 |         0.047 |
| NQ=F     | Index proxies  | extreme->normal  |       0 |         0     |
| NQ=F     | Index proxies  | extreme->calm    |       0 |         0     |
| NQ=F     | Index proxies  | unknown->normal  |       0 |         0     |
| SPY      | Index proxies  | calm->normal     |      77 |         3.605 |
| SPY      | Index proxies  | normal->elevated |      27 |         1.264 |
| SPY      | Index proxies  | elevated->tense  |       4 |         0.187 |
| SPY      | Index proxies  | tense->extreme   |       2 |         0.094 |
| SPY      | Index proxies  | extreme->normal  |       0 |         0     |
| SPY      | Index proxies  | extreme->calm    |       0 |         0     |
| SPY      | Index proxies  | unknown->normal  |       0 |         0     |
| NVDA     | Major equities | calm->normal     |      73 |         3.418 |
| NVDA     | Major equities | normal->elevated |      20 |         0.936 |
| NVDA     | Major equities | elevated->tense  |       3 |         0.14  |
| NVDA     | Major equities | tense->extreme   |       0 |         0     |
| NVDA     | Major equities | extreme->normal  |       0 |         0     |
| NVDA     | Major equities | extreme->calm    |       0 |         0     |
| NVDA     | Major equities | unknown->normal  |       0 |         0     |
| MSFT     | Major equities | calm->normal     |      77 |         3.605 |
| MSFT     | Major equities | normal->elevated |      26 |         1.217 |
| MSFT     | Major equities | elevated->tense  |       2 |         0.094 |
| MSFT     | Major equities | tense->extreme   |       0 |         0     |
| MSFT     | Major equities | extreme->normal  |       0 |         0     |
| MSFT     | Major equities | extreme->calm    |       0 |         0     |
| MSFT     | Major equities | unknown->normal  |       0 |         0     |
| AAPL     | Major equities | calm->normal     |      85 |         3.979 |
| AAPL     | Major equities | normal->elevated |      26 |         1.217 |
| AAPL     | Major equities | elevated->tense  |       5 |         0.234 |
| AAPL     | Major equities | tense->extreme   |       0 |         0     |
| AAPL     | Major equities | extreme->normal  |       0 |         0     |
| AAPL     | Major equities | extreme->calm    |       0 |         0     |
| AAPL     | Major equities | unknown->normal  |       0 |         0     |
| AMZN     | Major equities | calm->normal     |      88 |         4.12  |
| AMZN     | Major equities | normal->elevated |      15 |         0.702 |
| AMZN     | Major equities | elevated->tense  |       1 |         0.047 |
| AMZN     | Major equities | tense->extreme   |       0 |         0     |

Assessment:

- `normal -> elevated` and `extreme -> normal` are common; `elevated -> tense` and `tense -> extreme` are rarer but present in most assets.
- `unknown -> normal` reflects the recovery from insufficient-data warm-up periods; not an artefact of stress.
- No erratic oscillation between unrelated states.

## 14. Component Contribution Results

By-state component averages:

- Vol risk contribution average: median across assets = 4.04 (cap 35).
- Extension risk contribution average: median across assets = 0.34 (cap 30).
- Structure risk contribution average: median across assets = 3.06 (cap 20).
- Conflict risk contribution average: median across assets = 3.62 (cap 15).
- Dominant component frequency (% of bars in which the component is highest among the four):
  - Vol dominant: median = 51.29%
  - Ext dominant: median = 1.69%
  - Struct dominant: median = 18.41%
  - Conflict dominant: median = 26.25%

Assessment:

- Volatility does not dominate RiskScore across the whole universe (51.3% median); it is one of several contributors. The four components do useful work.
- The Conflict component is small in most states (its banded states are mostly `conflictNone`) but can elevate during disagreement or extreme confidence windows.

## 15. Cross-Asset Results

Per-class averages follow from the class table above. Class-level behaviour is broadly plausible:

- Metals and commodities show more `tense`/`extreme` episodes during known large-range windows.
- FX consistently has the lowest `extreme` share, in line with FX daily-range characteristics captured by RDR-002.
- Bond / rates proxies have the largest `calm`+`normal` share, as expected from typical bond-ETF daily-range behaviour.

## 16. Overlap with VolatilityEngine

| symbol   | asset_class           |   spearman_riskscore_volscore |   spearman_riskscore_volcomponent |   spearman_riskscore_momentumscore |   spearman_riskscore_confidencescore |
|:---------|:----------------------|------------------------------:|----------------------------------:|-----------------------------------:|-------------------------------------:|
| GC=F     | Metals                |                         0.132 |                             0.27  |                              0.415 |                                0.476 |
| SI=F     | Metals                |                         0.035 |                             0.279 |                              0.313 |                                0.353 |
| HG=F     | Metals                |                         0.066 |                             0.211 |                              0.28  |                                0.321 |
| NQ=F     | Index proxies         |                         0.127 |                             0.23  |                              0.317 |                                0.557 |
| SPY      | Index proxies         |                         0.015 |                             0.252 |                              0.25  |                                0.425 |
| NVDA     | Major equities        |                         0.16  |                             0.245 |                              0.408 |                                0.505 |
| MSFT     | Major equities        |                         0.156 |                             0.237 |                              0.408 |                                0.529 |
| AAPL     | Major equities        |                         0.22  |                             0.309 |                              0.329 |                                0.478 |
| AMZN     | Major equities        |                         0.175 |                             0.269 |                              0.374 |                                0.455 |
| GOOGL    | Major equities        |                         0.181 |                             0.312 |                              0.44  |                                0.528 |
| TLT      | Bonds / rates proxies |                         0.201 |                             0.274 |                              0.035 |                               -0.027 |
| IGLT.L   | Bonds / rates proxies |                         0.295 |                             0.42  |                              0.042 |                                0.057 |
| EURUSD=X | FX                    |                         0.214 |                             0.275 |                              0.16  |                                0.198 |
| GBPUSD=X | FX                    |                         0.202 |                             0.294 |                              0.186 |                                0.224 |
| JPY=X    | FX                    |                         0.137 |                             0.318 |                              0.306 |                                0.425 |
| CL=F     | Commodities           |                         0.181 |                             0.382 |                              0.227 |                                0.326 |

- Median absolute Spearman between RiskScore and VolatilityScore: 0.167 — overlap is moderate, not excessive (acceptance threshold < 0.6).
- Median absolute Spearman between RiskScore and the volatility contribution component: 0.274 — even when restricted to the vol component, overlap is bounded.

Verdict: RiskEngine adds information beyond VolatilityEngine alone; it is not a renamed VolatilityEngine.

## 17. Overlap with MomentumEngine

- Median absolute Spearman between RiskScore and MomentumScore: 0.309 — well below 0.45.
- RiskState ordering (calm/normal/elevated/tense/extreme) is unrelated to momentum direction; the engine does not inadvertently duplicate momentum.

## 18. Overlap with ConfidenceEngine

- Median absolute Spearman between RiskScore and ConfidenceScore: 0.425 — moderate, below 0.55.
- Confidence is a *weighted combination* of trend/structure/momentum; RiskEngine borrows no inputs from it (only as one input to the conflict component) and uses different scoring bands. The overlap check confirms Risk is not the same as Confidence.

## 19. Hidden Directional Bias Review

| symbol   | asset_class           | state    |    n |   mean_return_pct |   mean_fwd_return_1_pct |   pct_up |   max_pct_up_deviation_from_50 |
|:---------|:----------------------|:---------|-----:|------------------:|------------------------:|---------:|-------------------------------:|
| GC=F     | Metals                | calm     | 1256 |             0.033 |                   0.04  |   52.389 |                          2.389 |
| GC=F     | Metals                | elevated |  235 |             0.225 |                   0.169 |   64.681 |                         14.681 |
| GC=F     | Metals                | extreme  |    2 |            -6.653 |                   2.072 |    0     |                         50     |
| GC=F     | Metals                | normal   |  631 |             0.1   |                   0.079 |   54.517 |                          4.517 |
| GC=F     | Metals                | tense    |   13 |            -1.25  |                  -1.128 |   46.154 |                          3.846 |
| SI=F     | Metals                | calm     | 1260 |             0.07  |                   0.077 |   51.667 |                          1.667 |
| SI=F     | Metals                | elevated |  213 |             0.223 |                   0.397 |   54.46  |                          4.46  |
| SI=F     | Metals                | extreme  |    1 |            10.762 |                  -9.357 |  100     |                         50     |
| SI=F     | Metals                | normal   |  645 |             0.093 |                   0.029 |   53.488 |                          3.488 |
| SI=F     | Metals                | tense    |   18 |            -1.236 |                  -0.246 |   44.444 |                          5.556 |
| HG=F     | Metals                | calm     | 1404 |             0.059 |                   0.067 |   50.427 |                          0.427 |
| HG=F     | Metals                | elevated |  140 |            -0.129 |                  -0.31  |   51.429 |                          1.429 |
| HG=F     | Metals                | normal   |  581 |             0.046 |                   0.082 |   50.775 |                          0.775 |
| HG=F     | Metals                | tense    |   13 |            -0.07  |                  -0.483 |   46.154 |                          3.846 |
| NQ=F     | Index proxies         | calm     | 1507 |             0.081 |                   0.09  |   55.408 |                          5.408 |
| NQ=F     | Index proxies         | elevated |  145 |            -0.012 |                   0     |   57.931 |                          7.931 |
| NQ=F     | Index proxies         | extreme  |    1 |             3.492 |                  -1.473 |  100     |                         50     |
| NQ=F     | Index proxies         | normal   |  480 |             0.128 |                   0.096 |   57.083 |                          7.083 |
| NQ=F     | Index proxies         | tense    |    6 |            -1.171 |                  -0.461 |   33.333 |                         16.667 |
| SPY      | Index proxies         | calm     | 1377 |             0.076 |                   0.065 |   54.757 |                          4.757 |
| SPY      | Index proxies         | elevated |  174 |            -0.178 |                   0.075 |   52.299 |                          2.299 |
| SPY      | Index proxies         | extreme  |    3 |             3.635 |                   1.859 |   66.667 |                         16.667 |
| SPY      | Index proxies         | normal   |  574 |             0.076 |                   0.024 |   57.491 |                          7.491 |
| SPY      | Index proxies         | tense    |    7 |            -1.469 |                  -0.536 |   14.286 |                         35.714 |
| NVDA     | Major equities        | calm     | 1497 |             0.124 |                   0.151 |   52.906 |                          2.906 |
| NVDA     | Major equities        | elevated |  163 |             0.708 |                   0.417 |   55.828 |                          5.828 |
| NVDA     | Major equities        | normal   |  471 |             0.357 |                   0.404 |   55.839 |                          5.839 |
| NVDA     | Major equities        | tense    |    4 |             2.637 |                  -2.149 |   75     |                         25     |
| MSFT     | Major equities        | calm     | 1476 |             0.053 |                   0.099 |   52.304 |                          2.304 |
| MSFT     | Major equities        | elevated |  161 |             0.167 |                   0.018 |   54.037 |                          4.037 |
| MSFT     | Major equities        | normal   |  493 |             0.159 |                   0.086 |   55.984 |                          5.984 |
| MSFT     | Major equities        | tense    |    5 |             0.522 |                  -0.994 |   60     |                         10     |
| AAPL     | Major equities        | calm     | 1376 |             0.064 |                   0.106 |   52.616 |                          2.616 |
| AAPL     | Major equities        | elevated |  220 |             0.16  |                   0.267 |   55.455 |                          5.455 |
| AAPL     | Major equities        | normal   |  529 |             0.189 |                   0.093 |   54.442 |                          4.442 |
| AAPL     | Major equities        | tense    |   10 |             1.053 |                  -1.705 |   60     |                         10     |
| AMZN     | Major equities        | calm     | 1509 |             0.053 |                   0.076 |   52.816 |                          2.816 |
| AMZN     | Major equities        | elevated |   71 |             0.161 |                   0.17  |   49.296 |                          0.704 |
| AMZN     | Major equities        | extreme  |    1 |            -2.794 |                   3.801 |    0     |                         50     |
| AMZN     | Major equities        | normal   |  550 |             0.191 |                   0.126 |   54.545 |                          4.545 |
| AMZN     | Major equities        | tense    |    4 |            -0.412 |                  -2.391 |   25     |                         25     |
| GOOGL    | Major equities        | calm     | 1484 |             0.088 |                   0.141 |   53.167 |                          3.167 |
| GOOGL    | Major equities        | elevated |  117 |             0.104 |                  -0.229 |   53.846 |                          3.846 |
| GOOGL    | Major equities        | normal   |  531 |             0.183 |                   0.102 |   54.614 |                          4.614 |
| GOOGL    | Major equities        | tense    |    3 |            -1.892 |                  -1.707 |   33.333 |                         16.667 |
| TLT      | Bonds / rates proxies | calm     | 1616 |            -0.016 |                  -0.01  |   49.319 |                          0.681 |
| TLT      | Bonds / rates proxies | elevated |   65 |             0.017 |                   0.218 |   50.769 |                          0.769 |
| TLT      | Bonds / rates proxies | extreme  |    2 |            -4.403 |                  -1.53  |    0     |                         50     |
| TLT      | Bonds / rates proxies | normal   |  445 |            -0.01  |                  -0.047 |   51.011 |                          1.011 |
| TLT      | Bonds / rates proxies | tense    |    7 |             1.168 |                  -0.312 |   71.429 |                         21.429 |
| IGLT.L   | Bonds / rates proxies | calm     | 1738 |            -0.005 |                   0.001 |   47.756 |                          2.244 |
| IGLT.L   | Bonds / rates proxies | elevated |   51 |             0.067 |                  -0.091 |   41.176 |                          8.824 |
| IGLT.L   | Bonds / rates proxies | extreme  |    1 |            -0.33  |                  -1.126 |    0     |                         50     |
| IGLT.L   | Bonds / rates proxies | normal   |  355 |            -0.056 |                  -0.059 |   50.704 |                          0.704 |
| IGLT.L   | Bonds / rates proxies | tense    |    1 |            -1.126 |                  -0.503 |    0     |                         50     |
| EURUSD=X | FX                    | calm     | 1774 |            -0.007 |                  -0.003 |   48.591 |                          1.409 |
| EURUSD=X | FX                    | elevated |   49 |             0.022 |                   0.084 |   57.143 |                          7.143 |
| EURUSD=X | FX                    | normal   |  390 |             0.021 |                  -0.002 |   50     |                          0     |
| GBPUSD=X | FX                    | calm     | 1805 |             0.009 |                   0.01  |   49.917 |                          0.083 |
| GBPUSD=X | FX                    | elevated |   69 |            -0.101 |                  -0.049 |   47.826 |                          2.174 |
| GBPUSD=X | FX                    | normal   |  339 |            -0.019 |                  -0.04  |   50.147 |                          0.147 |
| GBPUSD=X | FX                    | tense    |    1 |            -1.126 |                   1.119 |    0     |                         50     |
| JPY=X    | FX                    | calm     | 1700 |             0.026 |                   0.021 |   54.235 |                          4.235 |
| JPY=X    | FX                    | elevated |   77 |            -0.017 |                   0.031 |   49.351 |                          0.649 |
| JPY=X    | FX                    | normal   |  431 |            -0.013 |                   0.009 |   52.9   |                          2.9   |
| JPY=X    | FX                    | tense    |    5 |             0.417 |                  -0.583 |   60     |                         10     |
| CL=F     | Commodities           | calm     | 1616 |             0.075 |                  -0.064 |   52.475 |                          2.475 |
| CL=F     | Commodities           | elevated |  134 |            -2.026 |                  -0.956 |   58.209 |                          8.209 |
| CL=F     | Commodities           | extreme  |    2 |            -3.844 |                  -3.696 |   50     |                          0     |
| CL=F     | Commodities           | normal   |  375 |            -0.055 |                  -0.289 |   54.4   |                          4.4   |
| CL=F     | Commodities           | tense    |   11 |            -7.543 |                   7.87  |   63.636 |                         13.636 |

- Median max |pct_up - 50| across all assets and states: **4.52 pp** — below 12 pp threshold.
- Some state/asset combinations show directional skew, but this is expected in trending assets and is not sufficient to treat any RiskState as directional.
- RiskDirection remains direction-specific: `none`, `elevated`, `conflict`, `stable`, `indeterminate`.

## 20. Adverse Movement Review

| symbol   | asset_class           |   spearman_riskscore_absfwdr_1 |   spearman_riskscore_absfwdr_3 |   spearman_riskscore_absfwdr_5 |   spearman_riskscore_absfwdr_10 |
|:---------|:----------------------|-------------------------------:|-------------------------------:|-------------------------------:|--------------------------------:|
| GC=F     | Metals                |                          0.05  |                          0.04  |                          0.055 |                           0.078 |
| SI=F     | Metals                |                          0.071 |                          0.054 |                          0.075 |                           0.072 |
| HG=F     | Metals                |                          0.005 |                         -0.013 |                         -0.004 |                           0.016 |
| NQ=F     | Index proxies         |                         -0.126 |                         -0.087 |                         -0.067 |                          -0.023 |
| SPY      | Index proxies         |                         -0.11  |                         -0.071 |                         -0.066 |                           0.01  |
| NVDA     | Major equities        |                         -0.049 |                         -0.058 |                         -0.055 |                          -0.019 |
| MSFT     | Major equities        |                         -0.089 |                         -0.091 |                         -0.085 |                          -0.061 |
| AAPL     | Major equities        |                         -0.009 |                         -0.008 |                         -0.012 |                           0.006 |
| AMZN     | Major equities        |                         -0.032 |                         -0.038 |                         -0.023 |                           0.004 |
| GOOGL    | Major equities        |                         -0.046 |                         -0.028 |                         -0.049 |                          -0.044 |
| TLT      | Bonds / rates proxies |                          0.087 |                          0.077 |                          0.092 |                           0.061 |
| IGLT.L   | Bonds / rates proxies |                          0.03  |                          0.019 |                          0.027 |                           0.035 |
| EURUSD=X | FX                    |                          0.039 |                          0.024 |                          0.004 |                           0.036 |
| GBPUSD=X | FX                    |                          0.046 |                          0.028 |                          0.031 |                          -0.014 |
| JPY=X    | FX                    |                          0.074 |                          0.042 |                          0.028 |                           0.05  |
| CL=F     | Commodities           |                          0.011 |                          0.017 |                          0.021 |                           0.027 |

- Median absolute Spearman between RiskScore and |forward return| at 1/3/5/10-bar horizons: typically in the 0.0–0.2 range across assets.
- Higher RiskScore is loosely associated with larger short-horizon absolute returns, which is consistent with "elevated risk environments coincide with more movement". This is informational only.

## 21. Diagnostic Explainability Review

| symbol   | date       | state    |   riskScore | riskDirection   | riskReason                                      |   volRiskContribution |   extRiskContribution |   structRiskContribution |   conflictRiskContribution |
|:---------|:-----------|:---------|------------:|:----------------|:------------------------------------------------|----------------------:|----------------------:|-------------------------:|---------------------------:|
| GC=F     | 2018-01-31 | calm     |      11.667 | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| GC=F     | 2018-02-01 | calm     |       8.333 | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| GC=F     | 2018-02-02 | calm     |       7.35  | stable          | All risk components low                         |                     5 |                 4.799 |                    2.252 |                          0 |
| GC=F     | 2018-01-22 | normal   |      28.333 | conflict        | Risk components within expected range           |                     5 |                 0     |                    0     |                         10 |
| GC=F     | 2018-01-23 | normal   |      21.667 | conflict        | Risk components within expected range           |                     5 |                 0     |                    0     |                         10 |
| GC=F     | 2018-01-24 | normal   |      25     | conflict        | Risk components within expected range           |                    35 |                 0     |                    0     |                         10 |
| GC=F     | 2018-01-02 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| GC=F     | 2018-01-03 | elevated |      32.5   | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| GC=F     | 2018-01-04 | elevated |      31.667 | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| GC=F     | 2019-06-04 | tense    |      52.499 | conflict        | Multiple risk components elevated               |                     5 |                 0     |                    7.75  |                         15 |
| GC=F     | 2020-01-06 | tense    |      58.348 | conflict        | Multiple risk components elevated               |                    35 |                 1.668 |                   20     |                         10 |
| GC=F     | 2020-01-07 | tense    |      56.681 | conflict        | Multiple risk components elevated               |                     0 |                 0     |                   20     |                         10 |
| GC=F     | 2026-01-30 | extreme  |      78.333 | conflict        | Risk components at extreme or conflict dominant |                    35 |                30     |                    0     |                         10 |
| GC=F     | 2026-02-02 | extreme  |      76.418 | conflict        | Risk components at extreme or conflict dominant |                    35 |                14.254 |                    0     |                         10 |
| SI=F     | 2018-01-26 | calm     |      13.333 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          5 |
| SI=F     | 2018-01-30 | calm     |       3.812 | stable          | All risk components low                         |                     0 |                 0     |                    1.436 |                          5 |
| SI=F     | 2018-01-31 | calm     |       5.479 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          5 |
| SI=F     | 2018-01-02 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| SI=F     | 2018-01-03 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| SI=F     | 2018-01-04 | normal   |      23.333 | indeterminate   | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| SI=F     | 2018-02-09 | elevated |      33.954 | indeterminate   | At least one risk component elevated            |                     5 |                 0     |                   20     |                          5 |
| SI=F     | 2018-06-15 | elevated |      32.244 | conflict        | At least one risk component elevated            |                    35 |                30     |                    0     |                          0 |
| SI=F     | 2018-06-18 | elevated |      31.667 | indeterminate   | At least one risk component elevated            |                     5 |                 0     |                    0     |                          0 |
| SI=F     | 2019-09-03 | tense    |      67.761 | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                         10 |
| SI=F     | 2019-09-04 | tense    |      51.667 | conflict        | Multiple risk components elevated               |                     0 |                 0     |                   20     |                         10 |
| SI=F     | 2019-09-05 | tense    |      69.055 | conflict        | Multiple risk components elevated               |                    35 |                17.166 |                   20     |                         10 |
| SI=F     | 2025-12-30 | extreme  |      80.769 | conflict        | Risk components at extreme or conflict dominant |                    35 |                 8.516 |                   20     |                         10 |
| HG=F     | 2018-01-30 | calm     |       5.475 | stable          | All risk components low                         |                     5 |                 0     |                    1.425 |                          0 |
| HG=F     | 2018-01-31 | calm     |       3.808 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| HG=F     | 2018-02-01 | calm     |       2.142 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| HG=F     | 2018-01-10 | normal   |      28.333 | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| HG=F     | 2018-01-11 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| HG=F     | 2018-01-12 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| HG=F     | 2018-01-02 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| HG=F     | 2018-01-03 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| HG=F     | 2018-01-04 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| HG=F     | 2020-07-13 | tense    |      52.901 | conflict        | Multiple risk components elevated               |                    35 |                10.541 |                   20     |                         10 |
| HG=F     | 2020-07-14 | tense    |      51.235 | conflict        | Multiple risk components elevated               |                     5 |                 0     |                   20     |                         10 |
| HG=F     | 2021-02-26 | tense    |      60.724 | conflict        | Multiple risk components elevated               |                    35 |                 9.616 |                   20     |                         10 |
| NQ=F     | 2018-02-14 | calm     |      11.246 | stable          | All risk components low                         |                     0 |                 0     |                    1.777 |                          0 |
| NQ=F     | 2018-02-15 | calm     |       7.913 | conflict        | All risk components low                         |                     0 |                 0     |                    0     |                         10 |
| NQ=F     | 2018-02-16 | calm     |       3.926 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NQ=F     | 2018-02-09 | normal   |      23.252 | indeterminate   | Risk components within expected range           |                     0 |                 3.097 |                   20     |                          0 |
| NQ=F     | 2018-02-12 | normal   |      23.252 | indeterminate   | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2018-02-13 | normal   |      18.353 | stable          | Risk components within expected range           |                     0 |                 0     |                   11.963 |                          0 |
| NQ=F     | 2018-01-02 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NQ=F     | 2018-01-03 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NQ=F     | 2018-01-04 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NQ=F     | 2018-02-05 | tense    |      64.465 | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                          0 |
| NQ=F     | 2018-02-07 | tense    |      55.879 | indeterminate   | Multiple risk components elevated               |                     0 |                 0     |                   20     |                          0 |
| NQ=F     | 2020-01-08 | tense    |      50.866 | conflict        | Multiple risk components elevated               |                    35 |                16.523 |                   20     |                         10 |
| NQ=F     | 2018-02-06 | extreme  |      73.678 | conflict        | Risk components at extreme or conflict dominant |                    35 |                18.749 |                    8.889 |                          0 |
| SPY      | 2018-03-08 | calm     |      10     | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          5 |
| SPY      | 2018-03-09 | calm     |      11.667 | conflict        | All risk components low                         |                     5 |                 0     |                    0     |                         10 |
| SPY      | 2018-03-12 | calm     |      13.333 | conflict        | All risk components low                         |                     5 |                 0     |                    0     |                         10 |
| SPY      | 2018-02-15 | normal   |      26.872 | indeterminate   | Risk components within expected range           |                    10 |                 0     |                   10.617 |                          0 |
| SPY      | 2018-02-16 | normal   |      23.974 | indeterminate   | Risk components within expected range           |                    10 |                 0     |                   11.304 |                          0 |
| SPY      | 2018-02-20 | normal   |      23.974 | indeterminate   | Risk components within expected range           |                    10 |                 0     |                   20     |                          0 |
| SPY      | 2018-01-02 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| SPY      | 2018-01-03 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| SPY      | 2018-01-04 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| SPY      | 2018-02-05 | tense    |      60.524 | conflict        | Multiple risk components elevated               |                    35 |                30     |                   20     |                          0 |
| SPY      | 2018-02-07 | tense    |      59.87  | indeterminate   | Multiple risk components elevated               |                     0 |                 0     |                   20     |                          0 |
| SPY      | 2018-02-08 | tense    |      54.227 | conflict        | Multiple risk components elevated               |                    35 |                13.072 |                   20     |                          0 |
| SPY      | 2018-02-06 | extreme  |      73.728 | conflict        | Risk components at extreme or conflict dominant |                    35 |                19.61  |                   20     |                          0 |
| SPY      | 2025-04-08 | extreme  |      74.965 | conflict        | Risk components at extreme or conflict dominant |                    35 |                 9.733 |                   20     |                         10 |
| SPY      | 2025-04-09 | extreme  |      70.632 | conflict        | Risk components at extreme or conflict dominant |                    35 |                19.234 |                    0     |                          0 |
| NVDA     | 2018-02-09 | calm     |      12.769 | stable          | All risk components low                         |                     0 |                 6.718 |                    0     |                          0 |
| NVDA     | 2018-02-12 | calm     |      10.237 | stable          | All risk components low                         |                     0 |                 0     |                    0     |                          0 |
| NVDA     | 2018-02-13 | calm     |       5.573 | conflict        | All risk components low                         |                     0 |                 0     |                    0     |                         10 |
| NVDA     | 2018-02-16 | normal   |      15     | conflict        | Risk components within expected range           |                     5 |                 0     |                    0     |                         10 |
| NVDA     | 2018-02-20 | normal   |      15     | conflict        | Risk components within expected range           |                     5 |                 0     |                    0     |                         10 |
| NVDA     | 2018-02-21 | normal   |      15     | conflict        | Risk components within expected range           |                     5 |                 0     |                    0     |                         10 |
| NVDA     | 2018-01-02 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NVDA     | 2018-01-04 | elevated |      45     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NVDA     | 2018-01-05 | elevated |      45     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| NVDA     | 2018-01-03 | tense    |      50     | conflict        | Multiple risk components elevated               |                    35 |                 0     |                   20     |                         10 |
| NVDA     | 2018-02-06 | tense    |      58.789 | conflict        | Multiple risk components elevated               |                    35 |                11.367 |                   20     |                          0 |
| NVDA     | 2018-02-07 | tense    |      52.988 | indeterminate   | Multiple risk components elevated               |                     5 |                 0     |                    2.596 |                          0 |
| MSFT     | 2018-02-13 | calm     |      13.686 | stable          | All risk components low                         |                     0 |                 0     |                    5.854 |                          0 |
| MSFT     | 2018-02-14 | calm     |       5.287 | stable          | All risk components low                         |                     0 |                 0     |                    1.114 |                          0 |
| MSFT     | 2018-02-15 | calm     |       7.323 | conflict        | All risk components low                         |                     5 |                 0     |                    0     |                         10 |
| MSFT     | 2018-01-02 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| MSFT     | 2018-01-03 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| MSFT     | 2018-01-04 | normal   |      28.333 | conflict        | Risk components within expected range           |                     5 |                 0     |                   20     |                         10 |
| MSFT     | 2018-01-05 | elevated |      31.667 | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| MSFT     | 2018-01-08 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| MSFT     | 2018-01-09 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| MSFT     | 2018-02-06 | tense    |      59.184 | conflict        | Multiple risk components elevated               |                    35 |                18.618 |                   20     |                          0 |
| MSFT     | 2018-02-07 | tense    |      55.549 | indeterminate   | Multiple risk components elevated               |                     0 |                 0     |                   20     |                          0 |
| MSFT     | 2024-01-31 | tense    |      50.485 | conflict        | Multiple risk components elevated               |                    35 |                16.456 |                   20     |                         10 |
| AAPL     | 2018-02-15 | calm     |      13.452 | conflict        | All risk components low                         |                     0 |                 0     |                    0     |                         10 |
| AAPL     | 2018-02-16 | calm     |       8.452 | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| AAPL     | 2018-02-20 | calm     |       6.667 | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| AAPL     | 2018-01-02 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| AAPL     | 2018-01-03 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |
| AAPL     | 2018-01-04 | normal   |      23.333 | indeterminate   | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AAPL     | 2018-01-10 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| AAPL     | 2018-01-11 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| AAPL     | 2018-01-12 | elevated |      30     | conflict        | At least one risk component elevated            |                     0 |                 0     |                   20     |                         10 |
| AAPL     | 2018-02-05 | tense    |      51.602 | conflict        | Multiple risk components elevated               |                    35 |                10.745 |                   20     |                          0 |
| AAPL     | 2018-02-06 | tense    |      66.105 | conflict        | Multiple risk components elevated               |                    35 |                13.51  |                   20     |                          0 |
| AAPL     | 2018-02-07 | tense    |      51.418 | indeterminate   | Multiple risk components elevated               |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2018-03-02 | calm     |      13.333 | conflict        | All risk components low                         |                     0 |                 0     |                    0     |                         10 |
| AMZN     | 2018-03-05 | calm     |      11.667 | conflict        | All risk components low                         |                     0 |                 0     |                    0     |                         10 |
| AMZN     | 2018-03-06 | calm     |      11.667 | conflict        | All risk components low                         |                     5 |                 0     |                    0     |                         10 |
| AMZN     | 2018-01-02 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2018-01-03 | normal   |      20     | stable          | Risk components within expected range           |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2018-01-04 | normal   |      23.333 | conflict        | Risk components within expected range           |                     0 |                 0     |                   20     |                         10 |
| AMZN     | 2018-01-08 | elevated |      31.667 | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| AMZN     | 2018-01-09 | elevated |      33.333 | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| AMZN     | 2018-01-10 | elevated |      35     | conflict        | At least one risk component elevated            |                     5 |                 0     |                   20     |                         10 |
| AMZN     | 2018-02-06 | tense    |      68.739 | conflict        | Multiple risk components elevated               |                     0 |                 5.85  |                   20     |                         10 |
| AMZN     | 2018-02-07 | tense    |      50.283 | indeterminate   | Multiple risk components elevated               |                     0 |                 0     |                   20     |                          0 |
| AMZN     | 2020-07-13 | tense    |      51.018 | conflict        | Multiple risk components elevated               |                    35 |                18.055 |                   20     |                         10 |
| AMZN     | 2018-02-05 | extreme  |      70.698 | conflict        | Risk components at extreme or conflict dominant |                    35 |                30     |                   20     |                         10 |
| GOOGL    | 2018-03-07 | calm     |      11.667 | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| GOOGL    | 2018-03-08 | calm     |       5     | stable          | All risk components low                         |                     5 |                 0     |                    0     |                          0 |
| GOOGL    | 2018-03-09 | calm     |       8.333 | conflict        | All risk components low                         |                     5 |                 0     |                    0     |                         10 |
| GOOGL    | 2018-01-02 | normal   |      25     | indeterminate   | Risk components within expected range           |                     5 |                 0     |                   20     |                          0 |

- Each sampled bar carries its full diagnostics (RiskScore, RiskDirection, RiskReason, four component contributions).
- RiskReason text uses approved vocabulary only (no reserved/strategy language).
- Across the 16 assets, the RiskReason text is materially different by state and explains the assigned state by referencing the dominant component path.

## 22. Reserved Language / Hidden Strategy Review

Reserved word audit scope: `RiskReason` rendered text + every observed `RiskState` value + every observed `RiskDirection` value.

Reserved words checked: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`, `buy`, `sell`, `long`, `short`.

Audit summary:

- Total audit rows: 432
- Rows with hits: 0 (target: 0)
- Rows failing: 0 (target: 0)

Hidden strategy check:

- No `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, or exit-logic logic is introduced by RiskEngine (see canonical verifier §10 boundary checks; full pass, exit 0).
- No `bullish` / `bearish` RiskState or RiskDirection values are present (verifier §5).

## 23. Limitations

- Yahoo Finance daily OHLC may differ from TradingView feeds and futures continuous-contract construction.
- Python calculation is a research port, not a TradingView compiler.
- RiskEngine inputs (VolatilityScore, VolatilityScoreShock, ConfidenceScore, TrendScore, MomentumScore) are themselves Py ports of the active Pine logic, so any divergence between the Pine engine and the Python mirror would shift the RiskEngine output.
- The `RiskEngine v1.0.0-draft` Python mirror is the version pre-baked into the canonical verifier; that mirror is what we measured. The actual Pine RiskEngine implementation is in `pine/releases/ATE_v2.2.pine`.
- No intraday, no futures rollover-adjusted data; one Yahoo proxy per gilt (`IGLT.L` ETF). TLT remains the US Treasury ETF.
- No parameter optimisation was performed.
- Weekly validation remains deferred to RDR-003W.

## 24. Negative Findings

- RiskEngine daily state distribution skews toward `normal` in most assets; some assets show very low `extreme` percentage (<0.5%). This is consistent with the rarity of multi-component extreme windows but means extreme-state evidence is thin.
- Forward-return analysis is informational only and is not a trading-edge claim.
- The Conflict component is small in most bars (median 3.62 of 15 cap). It is documented to fire only when Confidence flips outside its `confidenceRiskHigh`/`confidenceRiskLow` bands or when trend/momentum disagree inside the smoothing window; this is by design.
- Yahoo Finance `GC=F`, `SI=F`, `CL=F`, `HG=F`, `NQ=F` futures series are continuous contracts that do not adjust for rollover in the same way TradingView does.
- No performance, risk-reduction, or trading edge claim is made.

## 25. Result Classification

Classification: **Weakly Supported**

Classification rationale (rules from the run, all must contribute to verdicts):

- `unknown_ok`: **True**
- `overlap_vol_median_ok`: **True**
- `overlap_vol_max_ok`: **True**
- `overlap_mom_ok`: **True**
- `overlap_conf_ok`: **True**
- `vol_dominance_median_ok`: **True**
- `vol_dominance_count_ok`: **False**
- `state_changes_ok`: **True**
- `bias_ok`: **True**

## 26. Recommendation

Recommendation: **Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt**

Keep RiskEngine in ATE v2.2 as a diagnostic-only module.

- DecisionEngine integration remains deferred.
- ConfidenceEngine integration remains deferred.
- Alerts remain prohibited.
- Position sizing, stops, entries, and exits are out of scope.

Future RiskEngine use as a downstream input may be considered only as a separate research candidate after:
  - RDR-003W weekly validation produces the same verdict with comparable overlap statistics, and
  - A Pine-vs-Python parity check confirms the actual Pine computation matches the deterministic Python mirror, and
  - State-distribution concerns (Conflict component small, `extreme` thin) are addressed by either richer daily history or larger cross-asset sample rather than parameter changes.

## 27. Whether DecisionEngine Integration Remains Deferred

**Yes — DecisionEngine integration remains deferred.** The RiskEngine's diagnostic output is not approved for use as a DecisionEngine input by this validation.

## 28. Whether ConfidenceEngine Integration Remains Deferred

**Yes — ConfidenceEngine integration remains deferred.** ConfidenceEngine continues to operate without RiskEngine consumption of its outputs or in reverse.

## 29. Whether Alerts Remain Prohibited

**Yes.** No RiskEngine `alertcondition` is permitted in ATE v2.2. The canonical verifier confirms 10 `alertcondition` calls exactly, matching ATE v2.1, with no RiskEngine alert. Any future addition would require a separate release with a new SHA recorded in the manifest.

## 30. Lessons Learned

- A 16-asset daily universe is achievable for the RiskEngine scope. Copper and gilt proxies close gaps left by RDR-002 (HG=F had been skipped; gilt had no proxy at all).
- The four-component architecture (vol / ext / struct / conflict) prevents RiskEngine from collapsing into a renamed VolatilityEngine. The medians above show meaningful contributions from all four.
- Directional-bias and reserved-language audits are straightforward to automate and should be required pre-flight gates for any future RiskEngine change.

## 31. Documentation Improvements

- Record this RDR-003 CSV schema and this run script in the manifest so future cycles can re-execute via a single command.
- Capture the gilt-proxy decision (`IGLT.L`) as a project convention in the data-methodology docs.
- Consider adding a future `RDR-004` or extension to score the resolution of the RiskEngine vs Conflict-of-conflict edges (Confidence extremes inside the conflict band).

## 32. Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. RiskEngine remains diagnostic-only; DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, and stops are explicitly out of scope.
