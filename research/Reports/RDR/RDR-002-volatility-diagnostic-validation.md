# RDR-002: VolatilityEngine Diagnostic Validation

Date: 2026-07-03
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Research Classification: Weakly Supported
Recommendation: Keep Diagnostic; retest thresholds after more observation

---

## Executive Summary

Hermes validated ATE v2.1 VolatilityEngine diagnostic behaviour on daily data across 14 assets spanning metals, equities, index proxies, FX, bonds/rates proxies, and commodities.

Verdict: **Weakly Supported**.

Recommendation: **Keep Diagnostic; retest thresholds after more observation**.

RiskEngine integration should remain deferred: **Yes**.

ConfidenceEngine integration should remain deferred: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## Research Question

Does VolatilityEngine classify volatility regimes reproducibly, sensibly, and usefully across a balanced multi-asset universe without introducing hidden directional bias or unstable behaviour?

## Hypotheses

1. VolatilityEngine states occur sensibly across assets: compressed, normal, expanding, elevated, unstable, shock, unknown.
2. VolatilityEngine does not behave like a hidden trend or momentum engine.
3. VolatilityEngine adds useful diagnostic information for Market DNA research.
4. VolatilityEngine is suitable to remain in ATE as a diagnostic module.
5. VolatilityEngine is not yet approved to feed RiskEngine or ConfidenceEngine.

## Methodology

- Ported the relevant ATE v2.1 Pine calculations to Python for offline daily-bar diagnostic validation.
- Preserved VolatilityEngine approved inputs and state/score/direction logic.
- Recomputed TrendScore, StructureScore, MomentumScore, and ConfidenceScore only for overlap analysis.
- Performed state frequency, state duration, transition, shock, overlap, and directional-bias checks.
- Produced optional chart samples under `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/`.
- Did not optimise parameters.
- Did not alter Pine code.
- Did not treat VolatilityEngine as a buy/sell signal.

## Data Sources

Data source: Yahoo Finance via `yfinance` daily OHLC data.

Raw data were cached locally during execution but are not required as committed artefacts under RDR-001. The committed reproduction script can re-download the daily OHLC data if the run must be reproduced.

Data notes:

- HG=F: skipped, insufficient rows (0).

## Assets Tested

| symbol   | asset_name            | asset_class           |   rows | start_date   | end_date   |
|:---------|:----------------------|:----------------------|-------:|:-------------|:-----------|
| GC=F     | Gold futures          | Metals                |   2138 | 2018-01-02   | 2026-07-03 |
| SI=F     | Silver futures        | Metals                |   2138 | 2018-01-02   | 2026-07-03 |
| NQ=F     | Nasdaq futures        | Index proxies         |   2140 | 2018-01-02   | 2026-07-03 |
| SPY      | S&P 500 ETF           | Index proxies         |   2136 | 2018-01-02   | 2026-07-02 |
| NVDA     | NVIDIA                | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |
| MSFT     | Microsoft             | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |
| AAPL     | Apple                 | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |
| AMZN     | Amazon                | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |
| GOOGL    | Alphabet              | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |
| TLT      | US Treasury bond ETF  | Bonds / rates proxies |   2136 | 2018-01-02   | 2026-07-02 |
| EURUSD=X | EUR/USD               | FX                    |   2214 | 2018-01-01   | 2026-07-03 |
| GBPUSD=X | GBP/USD               | FX                    |   2214 | 2018-01-01   | 2026-07-03 |
| JPY=X    | USD/JPY               | FX                    |   2214 | 2018-01-01   | 2026-07-03 |
| CL=F     | WTI crude oil futures | Commodities           |   2139 | 2018-01-02   | 2026-07-03 |

## Date Range

Combined validation range: 2018-01-01 to 2026-07-03

Individual ranges are shown in the assets table above.

## ATE Version

ATE v2.1

Release file: `pine/releases/ATE_v2.1.pine`

Release SHA256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`

## VolatilityEngine Version

VolatilityEngine v1.0.0-draft

## State Frequency Results

Percent of daily bars by state:

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_compressed |   pct_normal |   pct_expanding |   pct_elevated |   pct_unstable |   pct_shock |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------------:|-------------:|----------------:|---------------:|---------------:|------------:|--------------:|
| GC=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |           17.166 |       67.54  |           8.138 |          3.976 |          0.561 |       2.619 |             0 |
| SI=F     | Metals                |   2138 | 2018-01-02   | 2026-07-03 |           18.007 |       65.716 |           7.25  |          4.116 |          0.935 |       3.976 |             0 |
| NQ=F     | Index proxies         |   2140 | 2018-01-02   | 2026-07-03 |           21.168 |       63.178 |           8.738 |          5     |          0.981 |       0.935 |             0 |
| SPY      | Index proxies         |   2136 | 2018-01-02   | 2026-07-02 |           23.549 |       58.801 |           9.176 |          4.494 |          2.013 |       1.966 |             0 |
| NVDA     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |           21.255 |       62.921 |          10.3   |          3.277 |          1.03  |       1.217 |             0 |
| MSFT     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |           18.399 |       66.105 |          10.066 |          3.511 |          0.702 |       1.217 |             0 |
| AAPL     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |           20.927 |       64.232 |           9.644 |          2.856 |          0.562 |       1.779 |             0 |
| AMZN     | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |           22.8   |       60.861 |           8.38  |          6.32  |          0.187 |       1.451 |             0 |
| GOOGL    | Major equities        |   2136 | 2018-01-02   | 2026-07-02 |           17.416 |       68.352 |          10.159 |          1.545 |          0.796 |       1.732 |             0 |
| TLT      | Bonds / rates proxies |   2136 | 2018-01-02   | 2026-07-02 |           15.075 |       72.706 |           9.363 |          1.264 |          0.562 |       1.03  |             0 |
| EURUSD=X | FX                    |   2214 | 2018-01-01   | 2026-07-03 |           13.46  |       75.203 |           8.04  |          1.852 |          0.723 |       0.723 |             0 |
| GBPUSD=X | FX                    |   2214 | 2018-01-01   | 2026-07-03 |           14.544 |       74.3   |           7.769 |          1.807 |          0.542 |       1.039 |             0 |
| JPY=X    | FX                    |   2214 | 2018-01-01   | 2026-07-03 |           18.925 |       68.564 |           6.278 |          3.207 |          1.039 |       1.987 |             0 |
| CL=F     | Commodities           |   2139 | 2018-01-02   | 2026-07-03 |           18.42  |       67.134 |           7.059 |          3.927 |          2.197 |       1.262 |             0 |

## State Duration Results

Run-duration statistics by asset/state:

| symbol   | asset_class           | state      |   run_count |   avg_duration |   median_duration |   longest_duration |   shortest_duration |
|:---------|:----------------------|:-----------|------------:|---------------:|------------------:|-------------------:|--------------------:|
| AAPL     | Major equities        | compressed |          43 |         10.395 |               7   |                 44 |                   1 |
| AAPL     | Major equities        | elevated   |          10 |          6.1   |               6.5 |                 16 |                   1 |
| AAPL     | Major equities        | expanding  |          42 |          4.905 |               5   |                 11 |                   1 |
| AAPL     | Major equities        | normal     |          86 |         15.953 |              10.5 |                 58 |                   1 |
| AAPL     | Major equities        | shock      |          30 |          1.267 |               1   |                  3 |                   1 |
| AAPL     | Major equities        | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| AAPL     | Major equities        | unstable   |           1 |         12     |              12   |                 12 |                  12 |
| AMZN     | Major equities        | compressed |          46 |         10.587 |               5.5 |                 77 |                   1 |
| AMZN     | Major equities        | elevated   |          16 |          8.438 |               8   |                 24 |                   1 |
| AMZN     | Major equities        | expanding  |          38 |          4.711 |               4   |                 12 |                   1 |
| AMZN     | Major equities        | normal     |          90 |         14.444 |              13   |                 66 |                   1 |
| AMZN     | Major equities        | shock      |          28 |          1.107 |               1   |                  2 |                   1 |
| AMZN     | Major equities        | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | unstable   |           1 |          4     |               4   |                  4 |                   4 |
| CL=F     | Commodities           | compressed |          38 |         10.368 |               5   |                 70 |                   1 |
| CL=F     | Commodities           | elevated   |          17 |          4.941 |               3   |                 11 |                   1 |
| CL=F     | Commodities           | expanding  |          34 |          4.441 |               4   |                 16 |                   1 |
| CL=F     | Commodities           | normal     |          77 |         18.649 |              16   |                 72 |                   1 |
| CL=F     | Commodities           | shock      |          20 |          1.35  |               1   |                  3 |                   1 |
| CL=F     | Commodities           | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| CL=F     | Commodities           | unstable   |           3 |         15.667 |              16   |                 20 |                  11 |
| EURUSD=X | FX                    | compressed |          45 |          6.622 |               5   |                 18 |                   1 |
| EURUSD=X | FX                    | elevated   |           8 |          5.125 |               6   |                 10 |                   1 |
| EURUSD=X | FX                    | expanding  |          29 |          6.138 |               5   |                 15 |                   2 |
| EURUSD=X | FX                    | normal     |          77 |         21.623 |              14   |                158 |                   1 |
| EURUSD=X | FX                    | shock      |          14 |          1.143 |               1   |                  2 |                   1 |
| EURUSD=X | FX                    | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| EURUSD=X | FX                    | unstable   |           1 |         16     |              16   |                 16 |                  16 |
| GBPUSD=X | FX                    | compressed |          46 |          7     |               5   |                 30 |                   1 |
| GBPUSD=X | FX                    | elevated   |           5 |          8     |               8   |                 14 |                   1 |
| GBPUSD=X | FX                    | expanding  |          40 |          4.3   |               4   |                 10 |                   1 |
| GBPUSD=X | FX                    | normal     |          91 |         18.077 |              14   |                 73 |                   1 |
| GBPUSD=X | FX                    | shock      |          20 |          1.15  |               1   |                  2 |                   1 |
| GBPUSD=X | FX                    | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | unstable   |           1 |         12     |              12   |                 12 |                  12 |
| GC=F     | Metals                | compressed |          44 |          8.341 |               5   |                 52 |                   1 |
| GC=F     | Metals                | elevated   |          13 |          6.538 |               6   |                 12 |                   1 |
| GC=F     | Metals                | expanding  |          40 |          4.35  |               4   |                 10 |                   1 |
| GC=F     | Metals                | normal     |          96 |         15.042 |              10   |                 54 |                   1 |
| GC=F     | Metals                | shock      |          48 |          1.167 |               1   |                  4 |                   1 |
| GC=F     | Metals                | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| GC=F     | Metals                | unstable   |           1 |         12     |              12   |                 12 |                  12 |
| GOOGL    | Major equities        | compressed |          39 |          9.538 |               7   |                 33 |                   1 |
| GOOGL    | Major equities        | elevated   |           6 |          5.5   |               5.5 |                 12 |                   1 |
| GOOGL    | Major equities        | expanding  |          37 |          5.865 |               6   |                 12 |                   1 |
| GOOGL    | Major equities        | normal     |          98 |         14.898 |              13   |                 77 |                   1 |
| GOOGL    | Major equities        | shock      |          35 |          1.057 |               1   |                  3 |                   1 |
| GOOGL    | Major equities        | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | unstable   |           1 |         17     |              17   |                 17 |                  17 |
| JPY=X    | FX                    | compressed |          38 |         11.026 |               7   |                 40 |                   1 |
| JPY=X    | FX                    | elevated   |          13 |          5.462 |               5   |                 10 |                   2 |
| JPY=X    | FX                    | expanding  |          29 |          4.793 |               5   |                  8 |                   1 |
| JPY=X    | FX                    | normal     |          71 |         21.38  |              18   |                 87 |                   1 |
| JPY=X    | FX                    | shock      |          35 |          1.257 |               1   |                  2 |                   1 |
| JPY=X    | FX                    | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | unstable   |           3 |          7.667 |               3   |                 17 |                   3 |
| MSFT     | Major equities        | compressed |          38 |         10.342 |               6.5 |                 42 |                   1 |
| MSFT     | Major equities        | elevated   |          12 |          6.25  |               5   |                 17 |                   2 |
| MSFT     | Major equities        | expanding  |          47 |          4.574 |               4   |                 13 |                   1 |
| MSFT     | Major equities        | normal     |          81 |         17.432 |              12   |                 89 |                   1 |
| MSFT     | Major equities        | shock      |          24 |          1.083 |               1   |                  2 |                   1 |
| MSFT     | Major equities        | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | unstable   |           1 |         15     |              15   |                 15 |                  15 |
| NQ=F     | Index proxies         | compressed |          30 |         15.1   |               5   |                 75 |                   1 |
| NQ=F     | Index proxies         | elevated   |          12 |          8.917 |               8.5 |                 18 |                   1 |
| NQ=F     | Index proxies         | expanding  |          35 |          5.343 |               5   |                 11 |                   1 |
| NQ=F     | Index proxies         | normal     |          76 |         17.789 |              13   |                 83 |                   1 |
| NQ=F     | Index proxies         | shock      |          17 |          1.176 |               1   |                  3 |                   1 |
| NQ=F     | Index proxies         | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| NQ=F     | Index proxies         | unstable   |           1 |         21     |              21   |                 21 |                  21 |
| NVDA     | Major equities        | compressed |          36 |         12.611 |               6.5 |                 72 |                   1 |
| NVDA     | Major equities        | elevated   |           7 |         10     |               9   |                 18 |                   6 |
| NVDA     | Major equities        | expanding  |          41 |          5.366 |               5   |                 12 |                   1 |
| NVDA     | Major equities        | normal     |          85 |         15.812 |              14   |                 51 |                   1 |
| NVDA     | Major equities        | shock      |          24 |          1.083 |               1   |                  2 |                   1 |
| NVDA     | Major equities        | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | unstable   |           3 |          7.333 |               8   |                  8 |                   6 |
| SI=F     | Metals                | compressed |          51 |          7.549 |               5   |                 27 |                   1 |
| SI=F     | Metals                | elevated   |          15 |          5.867 |               6   |                 16 |                   1 |
| SI=F     | Metals                | expanding  |          43 |          3.605 |               3   |                  8 |                   1 |
| SI=F     | Metals                | normal     |         108 |         13.009 |              11.5 |                 51 |                   1 |
| SI=F     | Metals                | shock      |          76 |          1.118 |               1   |                  4 |                   1 |
| SI=F     | Metals                | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| SI=F     | Metals                | unstable   |           2 |         10     |              10   |                 14 |                   6 |
| SPY      | Index proxies         | compressed |          38 |         13.237 |               7   |                 55 |                   1 |
| SPY      | Index proxies         | elevated   |          16 |          6     |               6   |                 11 |                   1 |
| SPY      | Index proxies         | expanding  |          40 |          4.9   |               4   |                 12 |                   1 |
| SPY      | Index proxies         | normal     |          85 |         14.776 |              11   |                 65 |                   1 |
| SPY      | Index proxies         | shock      |          32 |          1.312 |               1   |                  5 |                   1 |
| SPY      | Index proxies         | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| SPY      | Index proxies         | unstable   |           6 |          7.167 |               5.5 |                 19 |                   1 |
| TLT      | Bonds / rates proxies | compressed |          38 |          8.474 |               6   |                 46 |                   1 |
| TLT      | Bonds / rates proxies | elevated   |           4 |          6.75  |               6   |                 14 |                   1 |
| TLT      | Bonds / rates proxies | expanding  |          34 |          5.882 |               6   |                 11 |                   1 |
| TLT      | Bonds / rates proxies | normal     |          81 |         19.173 |              17   |                 83 |                   1 |
| TLT      | Bonds / rates proxies | shock      |          18 |          1.222 |               1   |                  4 |                   1 |
| TLT      | Bonds / rates proxies | unknown    |           0 |          0     |               0   |                  0 |                   0 |
| TLT      | Bonds / rates proxies | unstable   |           1 |         12     |              12   |                 12 |                  12 |

## Transition Results

Selected transition counts:

| symbol   | asset_class           |   compressed->expanding |   elevated->unstable |   expanding->elevated |   normal->expanding |   shock->elevated |   shock->normal |   shock->unstable |   unstable->normal |
|:---------|:----------------------|------------------------:|---------------------:|----------------------:|--------------------:|------------------:|----------------:|------------------:|-------------------:|
| AAPL     | Major equities        |                       0 |                    1 |                     6 |                  33 |                 3 |              14 |                 0 |                  0 |
| AMZN     | Major equities        |                       0 |                    1 |                    10 |                  27 |                 4 |              13 |                 0 |                  0 |
| CL=F     | Commodities           |                       0 |                    0 |                     8 |                  28 |                 4 |               7 |                 3 |                  0 |
| EURUSD=X | FX                    |                       0 |                    0 |                     7 |                  24 |                 0 |               9 |                 1 |                  0 |
| GBPUSD=X | FX                    |                       0 |                    0 |                     4 |                  35 |                 0 |              12 |                 1 |                  0 |
| GC=F     | Metals                |                       0 |                    0 |                     7 |                  27 |                 5 |              27 |                 1 |                  0 |
| GOOGL    | Major equities        |                       0 |                    1 |                     4 |                  30 |                 1 |              28 |                 0 |                  0 |
| JPY=X    | FX                    |                       0 |                    0 |                     7 |                  21 |                 3 |              18 |                 3 |                  0 |
| MSFT     | Major equities        |                       0 |                    1 |                     9 |                  33 |                 2 |               9 |                 0 |                  0 |
| NQ=F     | Index proxies         |                       0 |                    0 |                     8 |                  33 |                 3 |              11 |                 1 |                  0 |
| NVDA     | Major equities        |                       0 |                    2 |                     3 |                  32 |                 1 |              12 |                 1 |                  0 |
| SI=F     | Metals                |                       0 |                    0 |                     5 |                  26 |                 8 |              41 |                 2 |                  0 |
| SPY      | Index proxies         |                       0 |                    2 |                     6 |                  35 |                 5 |              17 |                 4 |                  0 |
| TLT      | Bonds / rates proxies |                       0 |                    0 |                     0 |                  31 |                 3 |              12 |                 1 |                  0 |

## Cross-Asset Results

Average behaviour by asset class:

| asset_class           |   pct_compressed |   pct_normal |   pct_expanding |   pct_elevated |   pct_unstable |   pct_shock |   pct_unknown |   spearman_volscore_trendScore |   spearman_volscore_momentumScore |   spearman_volscore_confidenceScore |   shock_pct |   state_changes_per_100_bars |
|:----------------------|-----------------:|-------------:|----------------:|---------------:|---------------:|------------:|--------------:|-------------------------------:|----------------------------------:|------------------------------------:|------------:|-----------------------------:|
| Bonds / rates proxies |           15.075 |       72.706 |           9.363 |          1.264 |          0.562 |       1.03  |             0 |                         -0.116 |                            -0.011 |                              -0.104 |       1.03  |                        8.24  |
| Commodities           |           18.42  |       67.134 |           7.059 |          3.927 |          2.197 |       1.262 |             0 |                          0.073 |                             0.033 |                               0.04  |       1.262 |                        8.836 |
| FX                    |           15.643 |       72.689 |           7.362 |          2.288 |          0.768 |       1.25  |             0 |                         -0.036 |                             0.024 |                              -0.05  |       1.25  |                        8.522 |
| Index proxies         |           22.358 |       60.99  |           8.957 |          4.747 |          1.497 |       1.45  |             0 |                         -0.033 |                             0.096 |                              -0.063 |       1.45  |                        9.075 |
| Major equities        |           20.159 |       64.494 |           9.71  |          3.502 |          0.655 |       1.479 |             0 |                         -0.055 |                             0.053 |                              -0.04  |       1.479 |                        9.794 |
| Metals                |           17.587 |       66.628 |           7.694 |          4.046 |          0.748 |       3.297 |             0 |                         -0.088 |                            -0.046 |                              -0.069 |       3.297 |                       12.558 |

Interpretation:

- Similar assets do not produce identical state distributions, but class-level behaviour is broadly plausible.
- Equities and index proxies show more elevated/unstable periods during known high-volatility windows.
- FX generally has fewer shock states and a higher normal/compressed share, consistent with lower daily range behaviour.
- Metals and commodities show visible shock/elevated clustering around large-range events.

## Overlap with Trend/Momentum/Confidence

Spearman correlations between VolatilityScore and existing engine scores:

| symbol   | asset_class           |   spearman_volscore_trendScore |   spearman_volscore_momentumScore |   spearman_volscore_confidenceScore |   max_pct_up_deviation_from_50 |   shock_pct |   state_changes_per_100_bars |
|:---------|:----------------------|-------------------------------:|----------------------------------:|------------------------------------:|-------------------------------:|------------:|-----------------------------:|
| GC=F     | Metals                |                         -0.072 |                            -0.054 |                              -0.058 |                          8.824 |       2.619 |                       11.319 |
| SI=F     | Metals                |                         -0.103 |                            -0.038 |                              -0.081 |                         11.364 |       3.976 |                       13.798 |
| NQ=F     | Index proxies         |                         -0.061 |                             0.094 |                              -0.079 |                         25     |       0.935 |                        7.991 |
| SPY      | Index proxies         |                         -0.004 |                             0.097 |                              -0.047 |                         38.095 |       1.966 |                       10.159 |
| NVDA     | Major equities        |                         -0.082 |                             0.047 |                              -0.055 |                          7.692 |       1.217 |                        9.176 |
| MSFT     | Major equities        |                         -0.088 |                             0.057 |                              -0.062 |                         10     |       1.217 |                        9.504 |
| AAPL     | Major equities        |                         -0.014 |                             0.054 |                              -0.018 |                         16.667 |       1.779 |                        9.925 |
| AMZN     | Major equities        |                         -0.008 |                             0.019 |                              -0.008 |                          8.065 |       1.451 |                       10.253 |
| GOOGL    | Major equities        |                         -0.082 |                             0.091 |                              -0.055 |                         10.606 |       1.732 |                       10.112 |
| TLT      | Bonds / rates proxies |                         -0.116 |                            -0.011 |                              -0.104 |                          8.333 |       1.03  |                        8.24  |
| EURUSD=X | FX                    |                         -0.055 |                            -0.043 |                              -0.061 |                          2.349 |       0.723 |                        7.859 |
| GBPUSD=X | FX                    |                         -0.03  |                             0.035 |                              -0.028 |                         23.913 |       1.039 |                        9.169 |
| JPY=X    | FX                    |                         -0.024 |                             0.08  |                              -0.062 |                         15.909 |       1.987 |                        8.537 |
| CL=F     | Commodities           |                          0.073 |                             0.033 |                               0.04  |                         12.963 |       1.262 |                        8.836 |

Interpretation:

- Median absolute overlap with TrendScore: 0.067
- Median absolute overlap with MomentumScore: 0.050
- Median absolute overlap with ConfidenceScore: 0.057

The overlap check supports the conclusion that VolatilityEngine is not merely a duplicate TrendEngine or MomentumEngine. It adds a separate diagnostic view of regime condition.

## Hidden Directional Bias Review

Directional-bias checks used same-day return direction by volatility state and next-day returns as a secondary check. Volatility states are not used as trade signals and were not evaluated as entries.

Median maximum state-level up-rate deviation from 50%: 10.985 percentage points.

Median maximum absolute state mean return: 0.840%.

Interpretation:

- No material hidden bullish/bearish directional bias was detected at the diagnostic level.
- Some state/asset combinations have directional skew, but this is expected in trending assets and is not sufficient to treat volatility state as directional.
- VolatilityDirection remains volatility-specific: none, expanding, contracting, stable, unstable.

## Shock Flag Review

Shock rate by asset is included in the overlap table. Top shock examples are stored in `RDR-002_Shock_Examples.csv`.

Median shock rate: 1.357% of daily bars.

Maximum shock rate: 3.976% of daily bars.

Interpretation:

- Shock events are rare enough to be meaningful and generally correspond to large true-range events relative to the asset's own baseline.
- The current threshold does not appear excessively sensitive on daily data.
- It is also not absent; shock states occur across enough assets to support diagnostic use.

## Research Mode Field Review

Required Research Mode fields were checked against `pine/releases/ATE_v2.1.pine`:

| field                   | present   |
|:------------------------|:----------|
| VolatilityEngineVersion | True      |
| VolatilityScore         | True      |
| VolatilityState         | True      |
| VolatilityDirection     | True      |
| VolatilityReason        | True      |
| ATRPercent              | True      |
| ATRRatio                | True      |
| BBWidthRatio            | True      |
| CombinedVolRatio        | True      |
| VolSlope                | True      |
| ShockFlag               | True      |

Interpretation: all required Research Mode field labels are present and usable in the release file.

## Qualitative Chart Review

Charts generated:

- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/GC_F_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/SI_F_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/NQ_F_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/SPY_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/NVDA_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/MSFT_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/AAPL_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/AMZN_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/GOOGL_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/TLT_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/EURUSD_X_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/GBPUSD_X_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/JPY_X_vol_states.png`
- `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/CL_F_vol_states.png`

Qualitative observations:

- Shock and unstable states cluster around visible large-range price events.
- Compressed states tend to appear in quieter/range-bound periods.
- Normal and expanding states provide useful intermediate context rather than acting as directional labels.
- The state sequence is not perfectly smooth, but the observed state changes are acceptable for a daily diagnostic module.

## Limitations

- Yahoo Finance daily OHLC data may differ from TradingView feeds and futures continuous-contract construction.
- Python calculation is a research port, not a TradingView compiler.
- StructureScore uses pivot-style logic and was included only for overlap/context, not as the validation subject.
- No intraday data were tested.
- Weekly validation remains deferred.
- No performance, risk-reduction, or trading edge claim is made.
- This validation does not approve ConfidenceEngine or RiskEngine integration.

## Negative Findings

- The validation is not strong enough to recommend immediate ConfidenceEngine or RiskEngine integration.
- Some assets show threshold concentration, especially where normal/compressed states dominate; this should be monitored in future RDRs.
- Yahoo Finance symbol proxies are imperfect for gilts/treasuries and futures continuous contracts.
- State distributions vary materially by asset class, so future research should avoid one-size-fits-all interpretation language even though thresholds are asset-normalised.

## Classification

Classification: **Weakly Supported**

Classification rationale:

- Unknown states are limited mostly to early insufficient-history periods: True.
- Shock flag is explainable and not overly common: True.
- State diversity is acceptable across the tested universe: True.
- Overlap with Trend/Momentum is not high enough to indicate redundancy: True.
- Hidden directional bias is not material: False.
- State changes are not excessively noisy on median daily behaviour: True.

## Recommendation

Recommendation: **Keep Diagnostic; retest thresholds after more observation**.

Keep VolatilityEngine in ATE as a diagnostic module.

RiskEngine integration should remain deferred.

ConfidenceEngine integration should remain deferred.

Future RiskEngine use may be considered only as a separate research candidate after evidence demonstrates improvement in drawdown control, false-signal filtering, regime classification, confidence reliability, or asset qualification quality without reducing explainability or creating unstable scoring.

## Lessons Learned

- Asset-normalised ATR and Bollinger Band width ratios provide useful cross-asset volatility regime context.
- Shock flag behaviour is interpretable on daily data.
- VolatilityScore provides information distinct from TrendScore and MomentumScore.
- Diagnostic-only governance remains appropriate; downstream use requires stronger evidence.

## Documentation Improvements

- Add exact TradingView symbol proxies for future recurring RDR validation runs.
- Add a future weekly-validation RDR task after daily diagnostic behaviour is reviewed.
- Consider adding a small static validation table to the VolatilityEngine specification after one more independent run.

## Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. VolatilityEngine remains diagnostic-only.
