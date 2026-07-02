# TrendEngine

## Purpose

Determine the direction and persistence of the prevailing market trend.

## Status

Specification draft. Implementation pending.

## Inputs

- OHLC daily bars
- Configurable lookback length
- Optional higher-timeframe reference

## Outputs

- `trendState`: one of `UP`, `DOWN`, `RANGE`
- `trendStrength`: numeric in `[0, 1]`
- `trendAge`: bars since last confirmed trend change

## Method (placeholder)

A trend read combines a moving-average slope with a higher-high / higher-low structure check on the chosen lookback. The exact rule set is defined during implementation and validated via Hermes.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`