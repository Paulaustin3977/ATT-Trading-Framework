# RiskEngine

## Purpose

Apply position-sizing, exposure, and protective rules to a candidate action.

## Status

Specification draft. Implementation pending.

## Inputs

- Candidate direction from DecisionEngine (or analytical stack)
- Account risk parameters (per-trade risk percentage, max exposure)
- Current volatility read
- Recent action history

## Outputs

- `positionSize`: numeric in account-defined units
- `stopLevel`: price level
- `riskRewardRatio`: numeric
- `riskApproved`: boolean

## Method (placeholder)

Stop distance is derived from the volatility read. Position size is sized so that a stop hit equals the configured per-trade risk. Action is rejected if exposure limits are exceeded.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`