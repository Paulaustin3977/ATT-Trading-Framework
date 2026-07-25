# StructureEngine — ATE v2.2 As-Built Diagnostic Specification

## Status

Implemented in the immutable `pine/releases/ATE_v2.2.pine` baseline and covered by release verification. No dedicated StructureEngine RDR classification or separate downstream/action approval is recorded. This document describes the source as built; it is not a proposal to change Pine logic.

## Purpose and inputs

StructureEngine classifies confirmed pivot progression and close-based breaks of the latest confirmed swing. Inputs are daily-or-chart-timeframe OHLC bars, `showStructure` (default `true`), and `pivotLen` (default `5`, range `2..20`).

## Method

- `swingHigh = ta.pivothigh(high, pivotLen, pivotLen)` and `swingLow = ta.pivotlow(low, pivotLen, pivotLen)`.
- On each confirmed pivot, `lastHigh`/`lastLow` move to the new pivot and their prior values move to `prevHigh`/`prevLow`.
- `higherHigh`, `lowerHigh`, `higherLow`, and `lowerLow` compare the latest two confirmed pivots of each type.
- `bullStructure = higherHigh and higherLow`; `bearStructure = lowerHigh and lowerLow`.
- `bosBull = not na(lastHigh) and close > lastHigh`; `bosBear = not na(lastLow) and close < lastLow`.

Pivot markers are plotted back on the pivot bar with `offset=-pivotLen`; the underlying pivot is not known until `pivotLen` bars later. Break-of-structure conditions use the current close and latest confirmed level.

## Score and state

Evaluation order is exact and first-match wins:

| Condition | `structureScore` |
|---|---:|
| Engine disabled | 50 |
| `bullStructure and bosBull` | 100 |
| `bullStructure` | 80 |
| `higherLow or higherHigh` | 65 |
| `bearStructure and bosBear` | 0 |
| `bearStructure` | 20 |
| `lowerLow or lowerHigh` | 35 |
| Fallback | 50 |

| Score condition | `structureState` |
|---|---|
| `>= 80` | `BULLISH STRUCTURE` |
| `>= 60` | `LEANING BULLISH` |
| `> 40` | `NEUTRAL` |
| `> 20` | `LEANING BEARISH` |
| Otherwise | `BEARISH STRUCTURE` |

## Published/consumed values

The release exposes `swingHigh`, `swingLow`, `lastHigh`, `prevHigh`, `lastLow`, `prevLow`, the four progression booleans, `bullStructure`, `bearStructure`, `bosBull`, `bosBear`, `structureScore`, and `structureState`. It has no separate version literal, reason field, or diagnostics object.

- ConfidenceEngine consumes `structureScore`.
- RiskEngine reads the nearest of `lastHigh` and `lastLow` for a diagnostic ATR-distance component.
- Dashboard rows show Structure Score and Structure State.
- Research Mode emits `StructureScore` and `StructureState`.
- Plot markers show confirmed swings and bullish/bearish BOS.
- Existing alerts: `ATE Bullish BOS` and `ATE Bearish BOS`.

## Boundaries

StructureEngine is descriptive chart diagnostics. It does not place orders, size positions, set stops, approve trades, or activate DecisionEngine. Its alerts report BOS conditions only and do not constitute execution instructions.
