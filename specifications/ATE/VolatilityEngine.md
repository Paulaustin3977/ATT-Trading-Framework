# VolatilityEngine

## Purpose

Classify the current volatility regime and detect contraction/expansion cycles.

## Status

Specification draft. Implementation pending.

## Inputs

- OHLC daily bars
- ATR lookback length
- Regime comparison window

## Outputs

- `atrValue`: current ATR in price units
- `volatilityState`: one of `CONTRACTION`, `EXPANSION`, `NEUTRAL`
- `regimeConfidence`: numeric in `[0, 1]`

## Method (placeholder)

ATR normalised by an average over the regime comparison window. Contraction is flagged when current ATR is below the lower threshold; expansion when above the upper threshold.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`