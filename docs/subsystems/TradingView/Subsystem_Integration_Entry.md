## Suggested CHANGELOG entry

Add under `[Unreleased]` → `Added`:

- Recognised TradingView as a governed ATT Trading Framework subsystem
  (companion repository).
- Added OANDA XAUUSD Optimized 5m research strategy v1.0 in
  `Paulaustin3977/OANDA-XAUUSD-Optimized-5m` (v1.0 tag, 2026-07-31).
- Added TradingView subsystem integration note at
  `docs/subsystems/TradingView/Subsystem_Integration.md`.
- Recorded the 60-day OANDA practice optimization results:
  frozen development +$3,506.41 (PF 1.549, 53.0% win),
  untouched test +$322.51 (PF 1.094, 47.1% win) on selected UTC hours,
  untouched test all hours -$2,424.19 (PF 0.851).
- Classified v1.0 as research-only and not approved for live trading.
- Verified that the canonical ATE verifier (`tools/scripts/verify_ate.py`)
  remains green after the doc-only addition (no Pine code changed).
