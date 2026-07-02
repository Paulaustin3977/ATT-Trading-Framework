# Project Charter

## Mission

The Austin Trading Engine (ATE) is a modular, explainable, evidence-based market analysis framework that supports TradingView indicators, strategies, Hermes research validation, AI-assisted analysis, and future trading dashboards.

## Scope

**In scope**

- Pine Script v6 indicators and strategies
- Daily-timeframe analysis as the primary horizon
- Multi-asset coverage: Gold, Silver, Gilts, Forex
- Hermes-driven backtesting and validation
- Spec-driven engine design
- Decision support, not autonomous execution

**Out of scope**

- Live trade execution (research framework only)
- Broker connectivity
- High-frequency or sub-second strategies
- Repainting logic

## Core Principles

1. **Explainability.** Every output can be traced back to its inputs and rules.
2. **Evidence.** Claims are supported by data, not narrative.
3. **Modularity.** Engines are independent and composable.
4. **Non-repainting.** No future-data references, ever.
5. **Versioned.** Every release is reproducible from a tagged commit.

## Stakeholders

| Role             | Responsibility                                           |
|------------------|----------------------------------------------------------|
| Project owner    | Austin Trading Team lead                                 |
| Engine authors   | Each engine has a named author in its specification      |
| Reviewers        | Verify evidence and standards compliance                 |
| Researchers      | Maintain `research/` and run Hermes validation cycles    |

## Success Criteria

- All eight engines specified, implemented, validated, and documented
- Hermes backtests archived per asset class
- Zero repainting, zero lookahead violations in regression
- Clear handoff from research to (potential future) strategy layer

## Non-Goals

- Predicting markets
- Promising returns
- Replacing human judgement