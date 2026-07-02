# MomentumEngine

## Purpose

Measure rate of change and the character of momentum — including divergence against price.

## Status

Specification draft. Implementation pending.

## Inputs

- OHLC daily bars
- Momentum lookback length
- Optional reference oscillator family (RSI, MACD, custom)

## Outputs

- `momentumValue`: signed numeric
- `momentumState`: one of `RISING`, `FALLING`, `FLAT`
- `divergenceFlag`: one of `NONE`, `BULLISH`, `BEARISH`

## Method (placeholder)

A normalised momentum oscillator computed from rate-of-change over the configured lookback. Divergence is detected by comparing swing points between price and the oscillator.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`