# RDR-002 Run Manifest

Run ID: RDR-002
Run type: Diagnostic validation
ATE version: ATE v2.1
VolatilityEngine version: 1.0.0-draft
Status: Completed
Generated: 2026-07-03T16:35:42.891564+00:00

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-002-volatility-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Summary.csv`
- Duration CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Durations.csv`
- Transition CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Transitions.csv`
- Class summary CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Class_Summary.csv`
- Shock examples CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Shock_Examples.csv`
- Charts directory: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/`
- Reproduction script: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`

## Source Code

- Pine release file: `pine/releases/ATE_v2.1.pine`
- Pine release SHA256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: daily OHLC, period 10y, filtered to dates from 2018-01-01 where available
- Timeframe: Daily
- Raw cache: generated locally by `run_rdr002_validation.py`; not committed under RDR-001 raw-data policy.

## Reproduction Environment

- Python: 3.9.6 on macOS during this run
- Required Python packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Example setup: `python3 -m venv .venv-rdr002 && .venv-rdr002/bin/python -m pip install pandas numpy yfinance matplotlib tabulate`
- Example rerun: `.venv-rdr002/bin/python backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`

## Assets

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

## Parameters

```json
{
  "atrLength": 14,
  "atrBaselineLength": 100,
  "bbLength": 20,
  "bbStdDev": 2.0,
  "bbBaselineLength": 100,
  "shockLookback": 20,
  "shockMultiplier": 2.5,
  "compressionThreshold": 0.75,
  "normalUpperThreshold": 1.25,
  "elevatedThreshold": 1.75,
  "unstableThreshold": 2.5,
  "volSlopeLookback": 5,
  "pivotLen": 5,
  "rsiLen": 14,
  "macdFast": 12,
  "macdSlow": 26,
  "macdSignal": 9,
  "adxLen": 14,
  "adxSmooth": 14
}
```

## Known Limitations

- Yahoo Finance data may differ from TradingView data.
- This is a Python research port of the diagnostic calculations, not a Pine compiler.
- No parameter optimisation was performed.
- No broker, paper-trading, or execution API was used.
- VolatilityEngine remains diagnostic-only.

## Result

Classification: Weakly Supported
Recommendation: Keep Diagnostic; retest thresholds after more observation
