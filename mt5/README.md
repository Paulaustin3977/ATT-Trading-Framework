# MT5 Subsystem

This directory contains governed MetaTrader 5 Expert Advisors, indicators, presets, and supporting material for the ATT Trading Framework.

## Status

The MT5 subsystem is an extension of the Austin Trading Engine repository. It does not replace the Pine Script daily-timeframe workstream.

## Initial governed component

- Austin M15 Scalper
- Platform: MetaTrader 5
- Primary research market: XAUUSD
- Entry timeframe: M15
- Trend timeframe: H1
- Release: v1.0
- Status: Research only; not approved for live trading

## Governance principles

- No martingale
- No grid recovery
- No uncontrolled lot escalation
- Completed-candle signals by default
- Broker-side stop loss required
- Risk-based sizing
- Reproducible backtests
- Release and development files must be byte-identical at release time
- Live deployment requires a separate approval decision
