# Architecture

Status: Active architecture baseline approved by Paul Austin

## Overview

The Austin Trading Engine is composed of eight independent engines, each responsible for a single analytical concern. Engines communicate through well-defined value interfaces, never by reaching into each other's internals.

This document preserves the core architecture rules: independent engines, one-way data flow, pure functions, no silent defaults, bar-close only decisions, and semantic versioning.

## Engine Map

```
   ┌───────────┬───────────┬───────────┬───────────┐
   │ TrendEng. │Struct.Eng.│Moment.Eng.│Volatil.Eng│  ← analytical evidence layer
   └───────────┴───────────┴───────────┴───────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ ConfidenceEngine │  ← strength of market evidence
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │    RiskEngine    │  ← safety/suitability filter
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  DecisionEngine  │  ← final action layer
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ DashboardEngine  │  ← presentation only
                  └──────────────────┘
```

## Engines

| Engine             | Concern                                                      |
|--------------------|--------------------------------------------------------------|
| TrendEngine        | Direction and persistence of the prevailing move             |
| StructureEngine    | Market structure: highs, lows, breakouts, range behaviour    |
| MomentumEngine     | Rate of change and momentum characteristics                  |
| VolatilityEngine   | Volatility regime and contraction/expansion cycles           |
| ConfidenceEngine   | Strength and agreement of the current market evidence        |
| RiskEngine         | Safety, suitability, exposure, and protective adjustment      |
| DecisionEngine     | Final actionable signal from confidence adjusted by risk      |
| DashboardEngine    | Visual presentation and information density                  |

## Data Flow

1. **Inputs.** Price, volume, and any derived series feed the four analytical engines.
2. **Evidence.** Trend, Structure, Momentum, and Volatility each publish their independent read.
3. **Confidence.** The ConfidenceEngine answers: "How strong is the market evidence?" It aggregates the evidence layer into a confidence assessment.
4. **Risk.** The RiskEngine answers: "Is this evidence safe or sensible to act on?" It adjusts, blocks, or qualifies candidate decisions based on current risk conditions.
5. **Decision.** The DecisionEngine produces the final signal: a level, a bias, or a no-action.
6. **Dashboard.** The DashboardEngine renders the complete engine state for human inspection.

Risk must adjust decisions; it must not create confidence. Confidence is an evidence-strength assessment. Risk is a safety and suitability assessment applied after confidence.

DashboardEngine is presentation-only. It must not alter, reinterpret, normalise, smooth, or overwrite engine values. Any display transformation must be clearly labelled as presentation formatting rather than engine logic.

## Engine Output Contract

Each engine publishes a standard output contract so downstream engines can consume values consistently and auditably.

| Field | Requirement |
|---|---|
| `score` | Numeric score from 0-100 where applicable. Use `na` or an explicitly documented null value where a score is not meaningful. |
| `state` | Human-readable state label, for example `trending`, `ranging`, `expanding volatility`, `risk elevated`, or `no action`. |
| `direction` | Direction label where applicable: `bullish`, `bearish`, `neutral`, or `none`. |
| `reason` | Short explanation of the main cause of the engine output. |
| `diagnostics` | Optional supporting values used for audit, debugging, and dashboard display. |
| `version` | Semantic engine version matching the engine specification. |

Contract rules:

- Every engine output must be reproducible from the same inputs and bar.
- Downstream engines may consume contract fields but must not mutate upstream values.
- Missing or unavailable values must be explicit; silent defaults are not permitted.
- Breaking changes to contract fields require a major version bump and migration note.

## Constraints

- **Independent engines.** Each engine owns one analytical concern and exposes only its output contract.
- **One-way data flow.** Engines do not call back into their predecessors.
- **Pure functions.** Given the same inputs and the same bar, an engine must produce the same output.
- **No silent defaults.** Every tunable has a documented default and a documented range. Missing outputs must be explicit.
- **Bar-close only.** No intra-bar decisions. The decision for bar *t* is finalised at the close of bar *t*.

## Versioning

- Each engine carries a semantic version in its specification.
- Breaking changes to an engine's interface or output contract require a major bump and a documented migration note.

## Approval Status

This architecture baseline was approved by Paul Austin. It is the active `Architecture.md` baseline.
