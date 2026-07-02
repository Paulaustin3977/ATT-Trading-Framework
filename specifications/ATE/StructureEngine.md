# StructureEngine

## Purpose

Identify market structure: swing highs, swing lows, breakouts, and range behaviour.

## Status

Specification draft. Implementation pending.

## Inputs

- OHLC daily bars
- Swing-detection sensitivity
- Range vs. trend classification threshold

## Outputs

- `swingHigh`, `swingLow`: boolean series
- `structureState`: one of `BREAKOUT_UP`, `BREAKOUT_DOWN`, `RANGE`
- `lastSwingHighPrice`, `lastSwingLowPrice`

## Method (placeholder)

Pivot-based swing detection with a configurable lookback. Breakouts are confirmed on bar close using the most recent confirmed swing level.

## Constraints

- No repainting.
- Confirmation at bar close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`