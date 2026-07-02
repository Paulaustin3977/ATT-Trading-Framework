# Architecture

## Overview

The Austin Trading Engine is composed of eight independent engines, each responsible for a single analytical concern. Engines communicate through well-defined value interfaces, never by reaching into each other's internals.

## Engine Map

```
                  ┌──────────────────┐
                  │  DashboardEngine │  ← presentation only
                  └──────────────────┘
                            ▲
                  ┌──────────────────┐
                  │  DecisionEngine  │  ← final action layer
                  └──────────────────┘
                            ▲
                  ┌──────────────────┐
                  │  ConfidenceEngine│
                  └──────────────────┘
                            ▲
                  ┌──────────────────┐
                  │   RiskEngine     │
                  └──────────────────┘
                            ▲
   ┌───────────┬───────────┬───────────┬───────────┐
   │ TrendEng. │Struct.Eng.│Moment.Eng.│Volatil.Eng│  ← analytical layer
   └───────────┴───────────┴───────────┴───────────┘
```

## Engines

| Engine             | Concern                                                      |
|--------------------|--------------------------------------------------------------|
| TrendEngine        | Direction and persistence of the prevailing move             |
| StructureEngine    | Market structure: highs, lows, breakouts, range behaviour    |
| MomentumEngine     | Rate of change and momentum characteristics                 |
| VolatilityEngine   | Volatility regime and contraction/expansion cycles           |
| ConfidenceEngine   | Aggregated confidence in the current read                   |
| RiskEngine         | Position sizing, exposure, and protective rules              |
| DecisionEngine     | Final actionable signal from the upper stack                 |
| DashboardEngine    | Visual presentation and information density                  |

## Data Flow

1. **Inputs.** Price, volume, and any derived series feed the four analytical engines.
2. **Aggregation.** Trend, Structure, Momentum, and Volatility each publish their read to the upper stack.
3. **Confidence.** The ConfidenceEngine weighs the agreement across the analytical engines.
4. **Risk.** The RiskEngine adjusts any candidate action by current regime and exposure rules.
5. **Decision.** The DecisionEngine produces the final signal: a level, a bias, or a no-action.
6. **Dashboard.** The DashboardEngine renders the entire state for human inspection.

## Constraints

- **One-way data flow.** Engines do not call back into their predecessors.
- **Pure functions.** Given the same inputs and the same bar, an engine must produce the same output.
- **No silent defaults.** Every tunable has a documented default and a documented range.
- **Bar-close only.** No intra-bar decisions. The decision for bar *t* is finalised at the close of bar *t*.

## Versioning

- Each engine carries a semantic version in its specification.
- Breaking changes to an engine's interface require a major bump and a documented migration note.