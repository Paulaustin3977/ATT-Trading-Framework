# Austin M15 Scalper — Development Journal

## Task

Integrate Austin M15 Scalper v1.0 as a governed MT5 subsystem in ATT-Trading-Framework.

## Tools used

- MetaEditor
- MetaTrader 5 Strategy Tester
- Git
- GitHub
- MQL5
- ChatGPT-assisted specification and code generation

## Outcome

- v1.0 compiled with no errors.
- The first XAUUSD M15 backtest completed successfully.
- Risk-based sizing, completed-candle logic, spread protection, daily controls, and single-position behaviour were exercised.
- Baseline performance was negative and statistically inconclusive because only seven trades occurred.

## Things that worked

- Clean compilation
- Successful Strategy Tester execution
- Broker-side stops and targets
- Low drawdown
- Expected winner/loss ratio close to the configured 1.5R target
- No evidence of runaway position opening

## Things that did not work

- Signal frequency was too low for meaningful evaluation.
- Baseline profitability was negative.
- Current diagnostics are insufficient to determine which filters block the most opportunities.

## Learning points

- Do not optimise from seven trades.
- Preserve the risk foundation.
- Add research-grade decision logging before changing the strategy substantially.
- Separate release source from development source.
- Require evidence before promotion to demo or live status.

## Next proposed task

Version 1.1 research diagnostics:
- CSV signal logging
- accepted/rejected setup fields
- per-filter state
- score-based experimental mode kept separate from strict v1.0 logic
