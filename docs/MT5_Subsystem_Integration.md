# MT5 Subsystem Integration

## Decision

The ATT Trading Framework now recognises MetaTrader 5 development as a governed subsystem alongside the existing Pine Script and Hermes research workstreams.

## Scope boundary

The MT5 subsystem:

- hosts MQL5 Expert Advisors and related presets;
- stores MT5-specific specifications and test evidence;
- follows existing ATT governance and evidence principles;
- remains separate from Pine Script release directories;
- does not alter the Austin Trading Engine daily-timeframe priority.

## Directory map

- `mt5/` — MQL5 source and MT5 subsystem documentation
- `specifications/MT5/` — governed MT5 specifications
- `backtests/mt5/` — Strategy Tester artefacts
- `research/mt5/` — research journals and findings
- `tests/mt5/` — acceptance and regression definitions

## Initial component

Austin M15 Scalper v1.0 is the first integrated MT5 component.

Its initial status is research only.
