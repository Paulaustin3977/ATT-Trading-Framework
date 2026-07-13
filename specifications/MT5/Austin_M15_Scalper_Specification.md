# Austin M15 Scalper — Specification

## Identity

- Component: Austin M15 Scalper
- Platform: MetaTrader 5
- Language: MQL5
- Initial release: v1.0
- Primary symbol: XAUUSD
- Entry timeframe: M15
- Trend timeframe: H1
- Classification: Research Expert Advisor

## Purpose

Provide a controlled and explainable M15 trend-pullback research system with institutional-style risk and execution protections.

## Entry model

Long entries require:

1. Completed H1 close above H1 EMA 50.
2. H1 EMA 50 above H1 EMA 200.
3. H1 EMA 50 rising.
4. M15 EMA 9 above EMA 21.
5. M15 EMA 21 above EMA 50.
6. M15 EMA 21 rising.
7. Price above M15 EMA 50.
8. ADX inside the configured range.
9. +DI above -DI.
10. Candle 2 touches the EMA pullback zone.
11. Candle 1 closes back above EMA 9 with bullish recovery.

Short entries use the inverse conditions.

Signals are evaluated only on a new M15 bar using completed candles.

## Risk controls

- Percentage risk sizing
- Maximum risk cap
- Broker-side stop and target
- Daily loss limit
- Daily trade limit
- Consecutive-loss block
- Post-loss cooldown
- One-position mode
- Spread limits
- Margin validation
- Symbol-property validation

## Prohibited methods

- Martingale
- Grid averaging
- Recovery multipliers
- Hidden stop losses
- Risk increases after losses

## Initial exit model

- Stop: ATR multiple
- Target: fixed R multiple
- No partial close in v1.0
- No trailing stop in v1.0

## Approval status

v1.0 is approved for compilation, Strategy Tester research, and demo forward testing only. It is not approved for live-money trading.
