# ConfidenceEngine — ATE v2.2 As-Built Diagnostic Specification

## Status

Implemented in the immutable `pine/releases/ATE_v2.2.pine` baseline and covered by release verification. No dedicated ConfidenceEngine RDR classification or approval for action use is recorded. This document describes the immutable source exactly; it does not authorise new consumers.

## Purpose

ConfidenceEngine combines three existing 0–100 diagnostics into a weighted score. In ATE v2.2 it consumes only `trendScore`, `structureScore`, and `momentumScore`. VolatilityEngine and RiskEngine are explicitly excluded.

## Inputs

| Input | Default | Pine range |
|---|---:|---:|
| `showConfidence` | `true` | boolean |
| `trendWeight` | 40 | 0–100 |
| `structureWeight` | 30 | 0–100 |
| `momentumWeight` | 30 | 0–100 |

`totalWeight` is the sum of the three weights. Each normalised weight is its input weight divided by `totalWeight`, or `0.0` when the total is zero.

## Method and outputs

When enabled and `totalWeight > 0`:

```text
confidenceScore =
    trendScore     * (trendWeight / totalWeight) +
    structureScore * (structureWeight / totalWeight) +
    momentumScore  * (momentumWeight / totalWeight)
```

When disabled or all weights are zero, `confidenceScore = 50`.

| Score condition | `confidenceState` |
|---|---|
| `>= 80` | `HIGH CONFIDENCE` |
| `>= 60` | `GOOD CONFIDENCE` |
| `> 40` | `LOW / MIXED` |
| `> 20` | `BEARISH CONFIDENCE` |
| Otherwise | `STRONG BEARISH` |

The implementation exposes `confidenceScore`, `confidenceState`, and a score-derived colour. It has no separate version literal, direction field, reason field, agreement map, or diagnostics object. Its numeric scale is 0–100, not the placeholder-era `[0,1]` contract.

## Consumption and presentation

- RiskEngine snapshots `confidenceScore` only for its own diagnostic conflict component; RiskEngine does not write back to confidence.
- Dashboard shows Confidence Score and Confidence State.
- Research Mode emits `ConfidenceScore`.
- Chart background colour is derived from `confidenceScore` when enabled by the visual setting.
- Existing events: `confidenceBull` crosses upward through `75`; `confidenceBear` crosses downward through `30`. Alert titles are `ATE High Confidence Bull` and `ATE Low Confidence Bear`.

## Boundaries

Confidence is evidence aggregation, not probability, risk approval, or permission to act. ConfidenceEngine does not consume `volScore`, `riskScore`, any `riskApproved` value, or development-only TrendEngine outputs. It does not place orders, size positions, set stops, or activate DecisionEngine.
