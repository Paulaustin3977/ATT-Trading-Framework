# TradingView Subsystem Integration

## Decision

Recognise TradingView as a governed subsystem of the Austin Trading Engine
research stack alongside the existing Pine Script daily-timeframe workstream
and the MetaTrader 5 subsystem recorded under
`ATT_MT5_Subsystem_Integration/`.

## Status

Draft. Not yet promoted through the governance cycle. Submission aligns
the proposed scope with the existing MT5 subsystem precedent.

## Companion repository

- Repo: `Paulaustin3977/OANDA-XAUUSD-Optimized-5m`
- URL: https://github.com/Paulaustin3977/OANDA-XAUUSD-Optimized-5m
- Initial release: v1.0 (tagged 2026-07-31)
- Component: OANDA XAUUSD Optimized 5m (Pine Script v6 strategy)
- Source session: `@session:default/20260731_204201_c616b5`

## Scope boundary

The TradingView subsystem:

- hosts Pine Script v6 strategies and indicators used for paper research;
- stores subsystem-specific specifications, test evidence, and acceptance
  criteria in its own repository;
- follows existing ATT governance principles (no broker connectivity, no
  live execution, no DecisionEngine coupling);
- remains separate from the canonical ATE Pine release directories at
  `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine`;
- does not alter the ATE daily-timeframe priority.

## Why a separate repository

The canonical ATE Pine verifier `tools/scripts/verify_ate.py` explicitly
forbids `strategy(...)` calls in the ATE indicator path. The OANDA XAUUSD
Optimized 5m strategy is a `strategy()` rather than an `indicator()` so it
can be deployed as a TradingView Strategy Tester backtest. Promoting it
into `ATT-Trading-Framework/pine/` would violate the canonical verifier.

The companion repository pattern mirrors the precedent set by the MT5
subsystem (`ATT_MT5_Subsystem_Integration/`), which also houses an
execution-capable artefact (MQL5 Expert Advisor) outside the Pine
indicator path.

## Directory map (companion repo)

- `pine/` — Pine Script v6 source (development and release mirrors)
- `specifications/` — governed TradingView specifications
- `backtests/` — Strategy Tester artefacts
- `research/` — development journals and findings
- `tests/` — acceptance and regression definitions
- `docs/governance/` — governance notes and decisions

## Initial component

- Name: OANDA XAUUSD Optimized 5m
- Platform: TradingView
- Language: Pine Script v6
- Primary research market: XAUUSD (OANDA feed)
- Timeframe: 5 minutes
- Initial release: v1.0
- Status: Research only; not approved for live trading

## Frozen parameters

- EMA 9 / 18
- RSI 14
- BB 20 (middle-band confirmation)
- ATR 14
- Stop 2.0x ATR
- Target 2.5x ATR
- Max hold: 3 bars
- Cooldown: 1 bar
- Units: 10
- UTC hour filter: {2, 8, 15, 18, 19, 21}

## Backtest headline

| Slice | Trades | Net ($) | Win rate | Profit factor |
|---|---:|---:|---:|---:|
| Development (frozen params) | 315 | +3,506.41 | 53.0% | 1.549 |
| Untouched test, selected hours | 172 | +322.51 | 47.1% | 1.094 |
| Untouched test, all hours | 709 | -2,424.19 | 42.6% | 0.851 |

The selected-hour filter is the majority of the edge. The untouched test
PF of 1.094 is too close to 1.0 to authorise a live deployment.

## Governance principles

- No live order routing
- No broker connectivity
- No webhook, alert, or alertcondition-driven execution
- Frozen parameters must be reproducible from the optimization report
- Live deployment requires a separate governance decision

## Promotion path

1. Companion repo currently hosts the Frozen Parameter Research baseline.
2. A future v1.1 may publish an `indicator()` envelope that passes the
   ATE canonical verifier, at which point a promotional RDR can be
   authored and the workstream can be considered for inclusion under
   `ATT-Trading-Framework/pine/`.
3. Live deployment of any TradingView subsystem component requires a
   separate governance decision and is not authorised by this document.
