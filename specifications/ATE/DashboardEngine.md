# DashboardEngine — ATE v2.2 As-Built Diagnostic Specification

## Status

Implemented in the immutable `pine/releases/ATE_v2.2.pine` baseline and covered by release verification. It is a presentation surface, not an analytical or decision engine. This specification describes the release table exactly; development-only TrendEngine rows are not part of the immutable v2.2 dashboard.

## Rendering contract

- `showDash` defaults to `true`.
- A persistent `table` is created at `position.top_right` with 2 columns and 38 rows.
- On `barstate.islast`, rows `0..37` are cleared and, when `showDash` is true, repopulated.
- Column 0 contains labels; column 1 contains formatted source values.
- Formatting and colour do not mutate any engine value.

## Exact row map

| Row | Label | Value source |
|---:|---|---|
| 0 | `AUSTIN TRADING ENGINE` | `v2.2` |
| 1 | `Profile` | `profile` |
| 2 | `Timeframe` | `timeframe.period` |
| 3 | `Trend Score` | `trendScore / 100` |
| 4 | `Market State` | `marketState` |
| 5 | `Structure Score` | `structureScore / 100` |
| 6 | `Structure State` | `structureState` |
| 7 | `Momentum Score` | `momentumScore / 100` |
| 8 | `Momentum State` | `momentumState` |
| 9 | `Confidence Score` | `confidenceScore / 100` |
| 10 | `Confidence State` | `confidenceState` |
| 11 | `Volatility Score` | `volScore / 100` or `na` |
| 12 | `Volatility State` | `volState` |
| 13 | `Vol Direction` | `volDirection` |
| 14 | `ATR % / Ratio` | `volAtrPercent / volAtrRatio` |
| 15 | `BB Ratio` | `volBbWidthRatio` |
| 16 | `Combined Vol` | `volCombinedRatio` |
| 17 | `Shock Flag` | `TRUE` or `false` |
| 18 | `Vol Reason` | `volReason` |
| 19 | `Risk Score` | `riskScore / 100` or `na` |
| 20 | `Risk State` | `riskState` |
| 21 | `Risk Direction` | `riskDirection` |
| 22 | `Risk Reason` | `riskReason` |
| 23 | `Risk Engine` | `riskEngineVersion + " diagnostic"` |
| 24 | `Vol Risk State` | `riskVolState` |
| 25 | `Ext Risk State` | `riskExtState` |
| 26 | `Struct Risk State` | `riskStructState` |
| 27 | `Conflict Risk State` | `riskConflictState` |
| 28 | `Vol Risk Contrib` | `riskVolRaw / 35` |
| 29 | `Ext Risk Contrib` | `riskExtRaw / 30` |
| 30 | `Struct Risk Contrib` | `riskStructRaw / 20` |
| 31 | `Conflict Risk Contrib` | `riskConflictRaw / 15` |
| 32 | `Smoothed Risk Score` | `riskSmoothedRaw` |
| 33 | `Price Score` | `priceScore / 20` |
| 34 | `Slow Align` | `slowAlignScore / 30` |
| 35 | `Slope Score` | `slopeScore / 20` |
| 36 | `RSI/MACD/ADX` | `rsiScore/macdScore/adxScore` |
| 37 | `Vol Engine` | `volEngineVersion + " diagnostic"` |

## Related presentation surfaces in ATE v2.2

The same Pine indicator also renders nine configurable MA plots, a confidence-coloured background, ten signal/structure plot shapes, a one-cell bottom-right Research Mode text table, and ten preserved `alertcondition` calls. These are release presentation/export surfaces; DashboardEngine does not invent their source values.

RiskEngine contributes dashboard and Research Mode diagnostics but no plot shape or alert. DecisionEngine contributes nothing because it is not implemented. Development-only TrendEngine dashboard rows exist only in `pine/development/ATE_Current.pine` and are outside this release specification.

## Boundaries

DashboardEngine must remain read-only. It does not reinterpret, normalise, smooth, overwrite, approve, reject, or execute anything. No broker, order, position, stop, or DecisionEngine pathway exists in this dashboard.
