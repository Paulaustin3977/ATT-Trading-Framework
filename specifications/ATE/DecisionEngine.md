# DecisionEngine

## Purpose

Produce the final actionable signal from the upper stack: a direction, a level, or a no-action.

## Status

Specification draft. Implementation pending.

## Inputs

- `confidenceValue` from ConfidenceEngine
- `riskApproved` from RiskEngine
- Current `trendState` and `structureState`
- Minimum confidence threshold

## Outputs

- `decision`: one of `LONG`, `SHORT`, `NEUTRAL`
- `decisionConfidence`: numeric in `[0, 1]`
- `rationale`: short human-readable string

## Method (placeholder)

Decision is taken when confidence exceeds the threshold, the engines agree on direction, and RiskEngine approves the candidate. Otherwise, decision is `NEUTRAL`.

## Constraints

- No repainting.
- Bar-close only.
- Pure function of inputs and bar index.

## Version

`0.1.0-spec`