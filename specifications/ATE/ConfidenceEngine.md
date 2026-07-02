# ConfidenceEngine

## Purpose

Aggregate the reads from Trend, Structure, Momentum, and Volatility engines into a single confidence value that downstream layers can consume.

## Status

Specification draft. Implementation pending.

## Inputs

- `trendRead` from TrendEngine
- `structureRead` from StructureEngine
- `momentumRead` from MomentumEngine
- `volatilityRead` from VolatilityEngine
- Configurable weighting per engine

## Outputs

- `confidenceValue`: numeric in `[0, 1]`
- `agreementMap`: per-engine contribution breakdown

## Method (placeholder)

A weighted aggregation of directional agreement across the analytical engines, modulated by the volatility regime. Weightings are tuned via Hermes validation.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`