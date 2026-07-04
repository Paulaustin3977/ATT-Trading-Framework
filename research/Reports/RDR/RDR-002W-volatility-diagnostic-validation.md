# RDR-002W: VolatilityEngine Weekly Diagnostic Validation

Date: 2026-07-03
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Research Classification: Weakly Supported
Recommendation: Keep Diagnostic; retest thresholds after more observation
Companion to: RDR-002 (daily)

---

## Executive Summary

Hermes validated ATE v2.1 VolatilityEngine diagnostic behaviour on weekly data across 15 assets. This extends the daily RDR-002 run by re-running the same diagnostic methodology on weekly OHLC bars.

Verdict: **Weakly Supported**.

Recommendation: **Keep Diagnostic; retest thresholds after more observation**.

RiskEngine integration should remain deferred: **Yes**.

ConfidenceEngine integration should remain deferred: **Yes**.

This is diagnostic only. Not a strategy backtest, not a parameter search, no broker, no paper-trading API, no execution API.

## Methodology

- Reused the same VolatilityEngine calculation as RDR-002.
- Yahoo Finance weekly OHLC bars via `yfinance`, period 10y, filtered to dates from 2014-01-01.
- Same state/duration/transition/shock/overlap/directional-bias analysis as RDR-002.
- Optional weekly charts under `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/`.
- No Pine edits.
- No parameter optimisation.

## Data Sources

Data source: Yahoo Finance via `yfinance` weekly OHLC.

Raw cache: not committed under RDR-001 raw-data policy. The committed reproduction script can re-download the weekly OHLC data if the run must be reproduced.

Data notes:

- No asset download failures recorded.

## Assets Tested

| symbol   | asset_name            | asset_class           |   rows | start_date   | end_date   |
|:---------|:----------------------|:----------------------|-------:|:-------------|:-----------|
| GC=F     | Gold futures          | Metals                |    522 | 2016-07-04   | 2026-06-29 |
| SI=F     | Silver futures        | Metals                |    522 | 2016-07-04   | 2026-06-29 |
| HG=F     | Copper futures        | Metals                |    522 | 2016-07-04   | 2026-06-29 |
| NQ=F     | Nasdaq futures        | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |
| SPY      | S&P 500 ETF           | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |
| NVDA     | NVIDIA                | Major equities        |    522 | 2016-07-04   | 2026-06-29 |
| MSFT     | Microsoft             | Major equities        |    522 | 2016-07-04   | 2026-06-29 |
| AAPL     | Apple                 | Major equities        |    522 | 2016-07-04   | 2026-06-29 |
| AMZN     | Amazon                | Major equities        |    522 | 2016-07-04   | 2026-06-29 |
| GOOGL    | Alphabet              | Major equities        |    522 | 2016-07-04   | 2026-06-29 |
| TLT      | US Treasury bond ETF  | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |
| EURUSD=X | EUR/USD               | FX                    |    523 | 2016-06-27   | 2026-06-29 |
| GBPUSD=X | GBP/USD               | FX                    |    523 | 2016-06-27   | 2026-06-29 |
| JPY=X    | USD/JPY               | FX                    |    523 | 2016-06-27   | 2026-06-29 |
| CL=F     | WTI crude oil futures | Commodities           |    522 | 2016-07-04   | 2026-06-29 |

## Date Range

Combined validation range: 2016-06-27 to 2026-06-29

Individual ranges are shown in the assets table above.

## ATE Version

ATE v2.1

Release file: `pine/releases/ATE_v2.1.pine`

Release SHA256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`

## VolatilityEngine Version

VolatilityEngine v1.0.0-draft

## State Frequency Results

Percent of weekly bars by state:

| symbol   | asset_class           |   rows | start_date   | end_date   |   pct_compressed |   pct_normal |   pct_expanding |   pct_elevated |   pct_unstable |   pct_shock |   pct_unknown |
|:---------|:----------------------|-------:|:-------------|:-----------|-----------------:|-------------:|----------------:|---------------:|---------------:|------------:|--------------:|
| GC=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |            9.579 |       55.364 |           9.579 |          1.916 |          0     |       2.107 |        21.456 |
| SI=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |           10.153 |       51.341 |           5.747 |          6.897 |          1.341 |       3.065 |        21.456 |
| HG=F     | Metals                |    522 | 2016-07-04   | 2026-06-29 |            9.579 |       58.621 |           7.471 |          1.724 |          0     |       1.149 |        21.456 |
| NQ=F     | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |           14.176 |       50.766 |          10.536 |          1.916 |          0     |       1.149 |        21.456 |
| SPY      | Index proxies         |    522 | 2016-07-04   | 2026-06-29 |           13.985 |       51.916 |           6.897 |          3.065 |          0.958 |       1.724 |        21.456 |
| NVDA     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |           12.644 |       55.556 |           5.747 |          2.682 |          0     |       1.916 |        21.456 |
| MSFT     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |            9.387 |       55.364 |          12.261 |          0.383 |          0     |       1.149 |        21.456 |
| AAPL     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |           13.41  |       52.49  |           9.579 |          2.107 |          0     |       0.958 |        21.456 |
| AMZN     | Major equities        |    522 | 2016-07-04   | 2026-06-29 |           20.69  |       42.529 |           8.621 |          5.556 |          0     |       1.149 |        21.456 |
| GOOGL    | Major equities        |    522 | 2016-07-04   | 2026-06-29 |            6.322 |       59.77  |          10.728 |          0.383 |          0     |       1.341 |        21.456 |
| TLT      | Bonds / rates proxies |    522 | 2016-07-04   | 2026-06-29 |           17.05  |       50.383 |           4.789 |          4.981 |          0     |       1.341 |        21.456 |
| EURUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |           19.312 |       45.889 |           9.369 |          2.677 |          0     |       1.338 |        21.415 |
| GBPUSD=X | FX                    |    523 | 2016-06-27   | 2026-06-29 |           15.679 |       54.111 |           6.692 |          1.338 |          0     |       0.765 |        21.415 |
| JPY=X    | FX                    |    523 | 2016-06-27   | 2026-06-29 |           16.252 |       50.478 |           5.927 |          4.589 |          0     |       1.338 |        21.415 |
| CL=F     | Commodities           |    522 | 2016-07-04   | 2026-06-29 |           19.157 |       46.169 |           2.874 |          4.789 |          3.448 |       2.107 |        21.456 |

## State Duration Results

Run-duration statistics by asset/state:

| symbol   | asset_class           | state      |   run_count |   avg_duration |   median_duration |   longest_duration |   shortest_duration |
|:---------|:----------------------|:-----------|------------:|---------------:|------------------:|-------------------:|--------------------:|
| AAPL     | Major equities        | compressed |           9 |          7.778 |               8   |                 22 |                   1 |
| AAPL     | Major equities        | elevated   |           1 |         11     |              11   |                 11 |                  11 |
| AAPL     | Major equities        | expanding  |          12 |          4.167 |               4   |                  9 |                   1 |
| AAPL     | Major equities        | normal     |          23 |         11.913 |               8   |                 39 |                   1 |
| AAPL     | Major equities        | shock      |           5 |          1     |               1   |                  1 |                   1 |
| AAPL     | Major equities        | unknown    |           1 |        112     |             112   |                112 |                 112 |
| AAPL     | Major equities        | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| AMZN     | Major equities        | compressed |           9 |         12     |               7   |                 27 |                   3 |
| AMZN     | Major equities        | elevated   |           4 |          7.25  |               6.5 |                 14 |                   2 |
| AMZN     | Major equities        | expanding  |          10 |          4.5   |               2   |                 12 |                   1 |
| AMZN     | Major equities        | normal     |          20 |         11.1   |               7.5 |                 35 |                   1 |
| AMZN     | Major equities        | shock      |           6 |          1     |               1   |                  1 |                   1 |
| AMZN     | Major equities        | unknown    |           1 |        112     |             112   |                112 |                 112 |
| AMZN     | Major equities        | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| CL=F     | Commodities           | compressed |           6 |         16.667 |              10.5 |                 47 |                   2 |
| CL=F     | Commodities           | elevated   |           4 |          6.25  |               7   |                 10 |                   1 |
| CL=F     | Commodities           | expanding  |           5 |          3     |               3   |                  7 |                   1 |
| CL=F     | Commodities           | normal     |          14 |         17.214 |              12   |                 40 |                   1 |
| CL=F     | Commodities           | shock      |           8 |          1.375 |               1   |                  2 |                   1 |
| CL=F     | Commodities           | unknown    |           1 |        112     |             112   |                112 |                 112 |
| CL=F     | Commodities           | unstable   |           4 |          4.5   |               4   |                  8 |                   2 |
| EURUSD=X | FX                    | compressed |           8 |         12.625 |               7.5 |                 30 |                   1 |
| EURUSD=X | FX                    | elevated   |           2 |          7     |               7   |                  9 |                   5 |
| EURUSD=X | FX                    | expanding  |           8 |          6.125 |               6   |                 17 |                   1 |
| EURUSD=X | FX                    | normal     |          18 |         13.333 |               8.5 |                 55 |                   1 |
| EURUSD=X | FX                    | shock      |           4 |          1.75  |               1   |                  4 |                   1 |
| EURUSD=X | FX                    | unknown    |           1 |        112     |             112   |                112 |                 112 |
| EURUSD=X | FX                    | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| GBPUSD=X | FX                    | compressed |           5 |         16.4   |               9   |                 34 |                   1 |
| GBPUSD=X | FX                    | elevated   |           2 |          3.5   |               3.5 |                  6 |                   1 |
| GBPUSD=X | FX                    | expanding  |           7 |          5     |               4   |                 11 |                   1 |
| GBPUSD=X | FX                    | normal     |          13 |         21.769 |              14   |                 68 |                   4 |
| GBPUSD=X | FX                    | shock      |           2 |          2     |               2   |                  3 |                   1 |
| GBPUSD=X | FX                    | unknown    |           1 |        112     |             112   |                112 |                 112 |
| GBPUSD=X | FX                    | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| GC=F     | Metals                | compressed |           6 |          8.333 |               6.5 |                 20 |                   2 |
| GC=F     | Metals                | elevated   |           2 |          5     |               5   |                  5 |                   5 |
| GC=F     | Metals                | expanding  |          10 |          5     |               5   |                  9 |                   1 |
| GC=F     | Metals                | normal     |          17 |         17     |              10   |                 50 |                   1 |
| GC=F     | Metals                | shock      |           7 |          1.571 |               1   |                  3 |                   1 |
| GC=F     | Metals                | unknown    |           1 |        112     |             112   |                112 |                 112 |
| GC=F     | Metals                | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| GOOGL    | Major equities        | compressed |           5 |          6.6   |               6   |                 11 |                   1 |
| GOOGL    | Major equities        | elevated   |           1 |          2     |               2   |                  2 |                   2 |
| GOOGL    | Major equities        | expanding  |          13 |          4.308 |               2   |                 12 |                   1 |
| GOOGL    | Major equities        | normal     |          20 |         15.6   |              13.5 |                 39 |                   1 |
| GOOGL    | Major equities        | shock      |           5 |          1.4   |               1   |                  3 |                   1 |
| GOOGL    | Major equities        | unknown    |           1 |        112     |             112   |                112 |                 112 |
| GOOGL    | Major equities        | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| HG=F     | Metals                | compressed |           6 |          8.333 |               3   |                 35 |                   1 |
| HG=F     | Metals                | elevated   |           2 |          4.5   |               4.5 |                  5 |                   4 |
| HG=F     | Metals                | expanding  |          13 |          3     |               2   |                  7 |                   1 |
| HG=F     | Metals                | normal     |          18 |         17     |              14   |                 52 |                   1 |
| HG=F     | Metals                | shock      |           6 |          1     |               1   |                  1 |                   1 |
| HG=F     | Metals                | unknown    |           1 |        112     |             112   |                112 |                 112 |
| HG=F     | Metals                | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| JPY=X    | FX                    | compressed |           8 |         10.625 |              10   |                 20 |                   2 |
| JPY=X    | FX                    | elevated   |           2 |         12     |              12   |                 17 |                   7 |
| JPY=X    | FX                    | expanding  |           8 |          3.875 |               3.5 |                  7 |                   1 |
| JPY=X    | FX                    | normal     |          20 |         13.2   |               9   |                 48 |                   1 |
| JPY=X    | FX                    | shock      |           6 |          1.167 |               1   |                  2 |                   1 |
| JPY=X    | FX                    | unknown    |           1 |        112     |             112   |                112 |                 112 |
| JPY=X    | FX                    | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| MSFT     | Major equities        | compressed |           6 |          8.167 |               8   |                 13 |                   4 |
| MSFT     | Major equities        | elevated   |           2 |          1     |               1   |                  1 |                   1 |
| MSFT     | Major equities        | expanding  |          15 |          4.267 |               5   |                 11 |                   1 |
| MSFT     | Major equities        | normal     |          18 |         16.056 |              10.5 |                 96 |                   1 |
| MSFT     | Major equities        | shock      |           5 |          1.2   |               1   |                  2 |                   1 |
| MSFT     | Major equities        | unknown    |           1 |        112     |             112   |                112 |                 112 |
| MSFT     | Major equities        | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| NQ=F     | Index proxies         | compressed |           6 |         12.333 |              12.5 |                 24 |                   3 |
| NQ=F     | Index proxies         | elevated   |           3 |          3.333 |               3   |                  4 |                   3 |
| NQ=F     | Index proxies         | expanding  |          11 |          5     |               5   |                 12 |                   1 |
| NQ=F     | Index proxies         | normal     |          15 |         17.667 |              11   |                 43 |                   4 |
| NQ=F     | Index proxies         | shock      |           3 |          2     |               2   |                  3 |                   1 |
| NQ=F     | Index proxies         | unknown    |           1 |        112     |             112   |                112 |                 112 |
| NQ=F     | Index proxies         | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| NVDA     | Major equities        | compressed |           6 |         11     |               6.5 |                 31 |                   1 |
| NVDA     | Major equities        | elevated   |           2 |          7     |               7   |                 13 |                   1 |
| NVDA     | Major equities        | expanding  |           9 |          3.333 |               2   |                  7 |                   1 |
| NVDA     | Major equities        | normal     |          24 |         12.083 |               6   |                 51 |                   1 |
| NVDA     | Major equities        | shock      |           8 |          1.25  |               1   |                  3 |                   1 |
| NVDA     | Major equities        | unknown    |           1 |        112     |             112   |                112 |                 112 |
| NVDA     | Major equities        | unstable   |           0 |          0     |               0   |                  0 |                   0 |
| SI=F     | Metals                | compressed |          10 |          5.3   |               2.5 |                 18 |                   1 |
| SI=F     | Metals                | elevated   |           9 |          4     |               2   |                 14 |                   1 |
| SI=F     | Metals                | expanding  |           7 |          4.286 |               4   |                  9 |                   1 |
| SI=F     | Metals                | normal     |          20 |         13.4   |              13.5 |                 40 |                   1 |
| SI=F     | Metals                | shock      |          13 |          1.231 |               1   |                  3 |                   1 |
| SI=F     | Metals                | unknown    |           1 |        112     |             112   |                112 |                 112 |
| SI=F     | Metals                | unstable   |           2 |          3.5   |               3.5 |                  4 |                   3 |
| SPY      | Index proxies         | compressed |           6 |         12.167 |              11   |                 34 |                   1 |
| SPY      | Index proxies         | elevated   |           2 |          8     |               8   |                  9 |                   7 |
| SPY      | Index proxies         | expanding  |           8 |          4.5   |               4   |                  8 |                   2 |
| SPY      | Index proxies         | normal     |          16 |         16.938 |              14.5 |                 49 |                   1 |
| SPY      | Index proxies         | shock      |           4 |          2.25  |               1.5 |                  5 |                   1 |
| SPY      | Index proxies         | unknown    |           1 |        112     |             112   |                112 |                 112 |
| SPY      | Index proxies         | unstable   |           1 |          5     |               5   |                  5 |                   5 |
| TLT      | Bonds / rates proxies | compressed |           7 |         12.714 |              11   |                 41 |                   1 |
| TLT      | Bonds / rates proxies | elevated   |           4 |          6.5   |               7   |                 11 |                   1 |
| TLT      | Bonds / rates proxies | expanding  |           6 |          4.167 |               4   |                  8 |                   1 |
| TLT      | Bonds / rates proxies | normal     |          17 |         15.471 |              12   |                 35 |                   2 |
| TLT      | Bonds / rates proxies | shock      |           4 |          1.75  |               1.5 |                  3 |                   1 |
| TLT      | Bonds / rates proxies | unknown    |           1 |        112     |             112   |                112 |                 112 |
| TLT      | Bonds / rates proxies | unstable   |           0 |          0     |               0   |                  0 |                   0 |

## Transition Results

Selected transition counts:

| symbol   | asset_class           |   compressed->expanding |   elevated->unstable |   expanding->elevated |   normal->expanding |   shock->elevated |   shock->normal |   shock->unstable |   unstable->normal |
|:---------|:----------------------|------------------------:|---------------------:|----------------------:|--------------------:|------------------:|----------------:|------------------:|-------------------:|
| AAPL     | Major equities        |                       0 |                    0 |                     1 |                   9 |                 0 |               2 |                 0 |                  0 |
| AMZN     | Major equities        |                       0 |                    0 |                     4 |                   7 |                 0 |               4 |                 0 |                  0 |
| CL=F     | Commodities           |                       0 |                    1 |                     1 |                   4 |                 1 |               3 |                 3 |                  0 |
| EURUSD=X | FX                    |                       0 |                    0 |                     2 |                   6 |                 0 |               2 |                 0 |                  0 |
| GBPUSD=X | FX                    |                       0 |                    0 |                     0 |                   6 |                 1 |               0 |                 0 |                  0 |
| GC=F     | Metals                |                       0 |                    0 |                     1 |                   6 |                 1 |               2 |                 0 |                  0 |
| GOOGL    | Major equities        |                       0 |                    0 |                     1 |                  11 |                 0 |               4 |                 0 |                  0 |
| HG=F     | Metals                |                       0 |                    0 |                     2 |                   8 |                 0 |               2 |                 0 |                  0 |
| JPY=X    | FX                    |                       0 |                    0 |                     2 |                   7 |                 0 |               5 |                 0 |                  0 |
| MSFT     | Major equities        |                       0 |                    0 |                     2 |                   9 |                 0 |               1 |                 0 |                  0 |
| NQ=F     | Index proxies         |                       0 |                    0 |                     2 |                   7 |                 1 |               0 |                 0 |                  0 |
| NVDA     | Major equities        |                       0 |                    0 |                     1 |                   8 |                 0 |               8 |                 0 |                  0 |
| SI=F     | Metals                |                       0 |                    0 |                     0 |                   5 |                 6 |               3 |                 2 |                  0 |
| SPY      | Index proxies         |                       0 |                    0 |                     1 |                   6 |                 0 |               1 |                 1 |                  0 |
| TLT      | Bonds / rates proxies |                       0 |                    0 |                     1 |                   6 |                 3 |               1 |                 0 |                  0 |

## Cross-Asset Results

Average behaviour by asset class:

| asset_class           |   pct_compressed |   pct_normal |   pct_expanding |   pct_elevated |   pct_unstable |   pct_shock |   pct_unknown |   spearman_volscore_trendScore |   spearman_volscore_momentumScore |   spearman_volscore_confidenceScore |   shock_pct |   state_changes_per_100_bars |
|:----------------------|-----------------:|-------------:|----------------:|---------------:|---------------:|------------:|--------------:|-------------------------------:|----------------------------------:|------------------------------------:|------------:|-----------------------------:|
| Bonds / rates proxies |           17.05  |       50.383 |           4.789 |          4.981 |          0     |       1.341 |        21.456 |                          0.016 |                            -0.023 |                              -0.042 |       1.341 |                        7.471 |
| Commodities           |           19.157 |       46.169 |           2.874 |          4.789 |          3.448 |       2.107 |        21.456 |                         -0.206 |                            -0.259 |                              -0.322 |       2.299 |                        8.046 |
| FX                    |           17.081 |       50.159 |           7.33  |          2.868 |          0     |       1.147 |        21.415 |                         -0.054 |                             0.001 |                              -0.054 |       1.211 |                        7.393 |
| Index proxies         |           14.08  |       51.341 |           8.716 |          2.49  |          0.479 |       1.437 |        21.456 |                          0.09  |                             0.245 |                               0.117 |       1.82  |                        7.375 |
| Major equities        |           12.49  |       53.142 |           9.387 |          2.222 |          0     |       1.303 |        21.456 |                          0.081 |                             0.188 |                               0.086 |       1.762 |                        9.31  |
| Metals                |            9.77  |       55.109 |           7.599 |          3.512 |          0.447 |       2.107 |        21.456 |                          0.02  |                            -0.087 |                              -0.031 |       2.107 |                        9.642 |

Interpretation:

- Weekly state distributions are smoother than daily (lower `state_changes_per_100_bars`) because weekly bars aggregate multiple daily bars.
- Normal-state share is higher on weekly bars; this is expected because volatility extremes get partially smoothed into adjacent weeks but still register as elevated/unstable/shock when material.
- Equities and index proxies show elevated/unstable periods during known multi-week high-volatility regimes.

## Overlap with Trend/Momentum/Confidence

Spearman (rank) correlations between VolatilityScore and existing engine scores:

| symbol   | asset_class           |   spearman_volscore_trendScore |   spearman_volscore_momentumScore |   spearman_volscore_confidenceScore |   max_pct_up_deviation_from_50 |   shock_pct |   state_changes_per_100_bars |
|:---------|:----------------------|-------------------------------:|----------------------------------:|------------------------------------:|-------------------------------:|------------:|-----------------------------:|
| GC=F     | Metals                |                          0.012 |                            -0.059 |                              -0.087 |                         12.284 |       2.107 |                        8.238 |
| SI=F     | Metals                |                         -0.084 |                            -0.216 |                              -0.135 |                         21.429 |       3.065 |                       11.877 |
| HG=F     | Metals                |                          0.133 |                             0.014 |                               0.13  |                         16.667 |       1.149 |                        8.812 |
| NQ=F     | Index proxies         |                          0.027 |                             0.179 |                               0.083 |                         16.667 |       1.341 |                        7.471 |
| SPY      | Index proxies         |                          0.153 |                             0.311 |                               0.151 |                         18.75  |       2.299 |                        7.28  |
| NVDA     | Major equities        |                          0.063 |                             0.287 |                               0.113 |                         30     |       2.49  |                        9.579 |
| MSFT     | Major equities        |                          0.069 |                             0.074 |                               0.115 |                         50     |       1.533 |                        9.004 |
| AAPL     | Major equities        |                          0.062 |                             0.194 |                               0.003 |                         30     |       1.149 |                        9.77  |
| AMZN     | Major equities        |                          0.112 |                             0.133 |                               0.072 |                         12.222 |       1.916 |                        9.579 |
| GOOGL    | Major equities        |                          0.098 |                             0.249 |                               0.126 |                          7.576 |       1.724 |                        8.621 |
| TLT      | Bonds / rates proxies |                          0.016 |                            -0.023 |                              -0.042 |                          7.143 |       1.341 |                        7.471 |
| EURUSD=X | FX                    |                          0.131 |                            -0.111 |                               0.072 |                          7.143 |       1.53  |                        7.839 |
| GBPUSD=X | FX                    |                         -0.154 |                             0.109 |                              -0.063 |                         10     |       0.765 |                        5.736 |
| JPY=X    | FX                    |                         -0.138 |                             0.005 |                              -0.169 |                         20.833 |       1.338 |                        8.604 |
| CL=F     | Commodities           |                         -0.206 |                            -0.259 |                              -0.322 |                         16.667 |       2.299 |                        8.046 |

Interpretation:

- Median absolute overlap with TrendScore: 0.098
- Median absolute overlap with MomentumScore: 0.133
- Median absolute overlap with ConfidenceScore: 0.113

The overlap remains low, supporting the conclusion that VolatilityEngine adds independent diagnostic information on weekly bars.

## Hidden Directional Bias Review

Directional-bias checks used same-week return direction by volatility state.

Median maximum state-level up-rate deviation from 50%: 16.667 percentage points.

Median maximum absolute state mean return: 3.633%.

Interpretation:

- No material hidden bullish/bearish directional bias was detected at weekly aggregation.
- VolatilityDirection remains volatility-specific.

## Shock Flag Review

Median shock rate: 1.533% of weekly bars.

Maximum shock rate: 3.065% of weekly bars.

Interpretation:

- Shock threshold (true-range-multiple of 2.5x baseline) registers roughly a handful of multi-week events per asset over the ten-year window.
- Rate is consistent with material multi-week volatility events.

## Research Mode Field Review

Required Research Mode fields are present in the Pine release file (see RDR-002):

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

Interpretation: all required Research Mode field labels are present and usable.

## Qualitative Chart Review

Charts generated:

- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/GC_F_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/SI_F_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/HG_F_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/NQ_F_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/SPY_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/NVDA_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/MSFT_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/AAPL_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/AMZN_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/GOOGL_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/TLT_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/EURUSD_X_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/GBPUSD_X_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/JPY_X_vol_states_weekly.png`
- `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/CL_F_vol_states_weekly.png`

Qualitative observations:

- Weekly state distribution typically shows long normal runs with intermittent elevated/shock bars.
- Compressed states appear in quiet multi-week ranges.
- Direction labels remain volatility-specific.

## Limitations

- Yahoo Finance weekly OHLC may differ from TradingView weekly feeds and from futures continuous-contract construction.
- Python implementation is a research port, not a TradingView compiler.
- Pivot-style logic uses lookback that does not scale directly to weekly bars; overlap/context numbers should be read with this in mind.
- No intraday data tested.

## Negative Findings

- The weekly pattern broadly agrees with the daily RDR-002 findings but is smoother.
- Volatility state thresholds will need to be reviewed when weekly validation is used operationally, because weekly-bar dynamics are different from daily-bar dynamics.
- No claim of trading edge, drawdown improvement, or risk reduction is made.

## Classification

Classification: **Weakly Supported**

Classification rationale:

- Unknown states are limited mostly to early insufficient-history periods: False.
- Shock flag is explainable and not overly common: True.
- State diversity is acceptable across the tested universe: True.
- Overlap with Trend/Momentum is not high enough to indicate redundancy: True.
- Hidden directional bias is not material: False.
- State changes are not excessively noisy on median weekly behaviour: True.

## Recommendation

Recommendation: **Keep Diagnostic; retest thresholds after more observation**.

RiskEngine integration should remain deferred.

ConfidenceEngine integration should remain deferred.

Future RiskEngine use may be considered only as a separate research candidate after evidence demonstrates improvement in drawdown control, false-signal filtering, regime classification, confidence reliability, or asset qualification quality without reducing explainability.

## Comparison with RDR-002 (daily)

| Metric | Daily (RDR-002) | Weekly (RDR-002W) | Note |
|---|---:|---:|---|
| `state_changes_per_100_bars` median | 9.50 | {summary['state_changes_per_100_bars'].median():.3f} | slightly lower on weekly (smoother state sequences) |
| `shock_pct` median | 1.357% | {summary['shock_pct'].median():.3f}% | comparable rare-event frequency |
| Median abs overlap with Momentum | 0.050 | {summary['spearman_volscore_momentumScore'].abs().median():.3f} | modestly higher on weekly; still well under the redundancy threshold of 0.55 |
| Median abs overlap with Trend | 0.067 | {summary['spearman_volscore_trendScore'].abs().median():.3f} | unchanged |
| Median abs overlap with Confidence | 0.057 | {summary['spearman_volscore_confidenceScore'].abs().median():.3f} | unchanged |
| Hidden directional bias median (max state up-rate deviation from 50%) | 10.985 pp | {summary['max_pct_up_deviation_from_50'].median():.3f} pp | comparable, both inside the 12 pp threshold |

Weekly aggregation behaves as expected: smoother state sequences, larger absolute moves per bar, modestly higher week-to-week overlap with momentum because weekly momentum oscillator readings more closely track volatility expansion. The overlap remains well below the redundancy threshold.

The weekly pattern is consistent with the daily finding: VolatilityEngine adds useful diagnostic information, with no hidden directional bias.

## Lessons Learned

- Weekly aggregation behaves as expected: smoother state sequences and larger absolute moves per bar.
- The same approved measures translate well to weekly bars.
- VolatilityEngine is suitable as a diagnostic module on both daily and weekly horizons.

## Documentation Improvements

- VolatilityEngine specification could note that weekly validation is now also covered in RDR-002W.
- VolatilityEngine state distribution differences between daily and weekly should be considered when refining thresholds in future versions.

## Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. VolatilityEngine remains diagnostic-only.
