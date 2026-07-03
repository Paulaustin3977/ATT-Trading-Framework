# RDR-002W Run Manifest

Run ID: RDR-002W
Run type: Diagnostic validation (weekly companion to RDR-002)
ATE version: ATE v2.1
VolatilityEngine version: 1.0.0-draft
Status: Completed
Generated: 2026-07-03T16:45:01.232871+00:00

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-002W-volatility-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Summary.csv`
- Duration CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Durations.csv`
- Transition CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Transitions.csv`
- Class summary CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Class_Summary.csv`
- Shock examples CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Shock_Examples.csv`
- Charts directory: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/`
- Reproduction script: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/run_rdr002w_validation.py`

## Source Code

- Pine release file: `pine/releases/ATE_v2.1.pine`
- Pine release SHA256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: weekly OHLC, period 10y, filtered to dates from 2014-01-01 where available
- Timeframe: Weekly
- Raw cache: generated locally by `run_rdr002w_validation.py`; not committed under RDR-001 raw-data policy.

## Reproduction Environment

- Python: 3.9.6 on macOS during this run
- Required Python packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Example setup: `python3 -m venv .venv-rdr002w && .venv-rdr002w/bin/python -m pip install pandas numpy yfinance matplotlib tabulate`
- Example rerun: `.venv-rdr002w/bin/python backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/run_rdr002w_validation.py`

## Assets

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
- This is a Python research port, not a Pine compiler.
- No parameter optimisation was performed.
- No broker, paper-trading, or execution API was used.
- VolatilityEngine remains diagnostic-only.

## Result

Classification: Weakly Supported
Recommendation: Keep Diagnostic; retest thresholds after more observation
