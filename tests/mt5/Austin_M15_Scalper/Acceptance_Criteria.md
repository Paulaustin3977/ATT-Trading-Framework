# Austin M15 Scalper — Acceptance Criteria

## Compilation

- [ ] Zero compiler errors
- [ ] Zero material compiler warnings
- [ ] Release and development files byte-identical at release

## Signal integrity

- [ ] Signals use completed candles
- [ ] No duplicate entry on the same M15 bar
- [ ] Long and short logic are symmetric where intended
- [ ] H1 confirmation uses completed H1 data
- [ ] Insufficient data blocks trading safely

## Risk and execution

- [ ] Position size reflects selected account risk
- [ ] Every position receives a valid broker-side stop
- [ ] Take profit is calculated from actual risk distance
- [ ] Broker volume step and limits are respected
- [ ] Insufficient margin blocks entry
- [ ] Invalid tick value blocks entry
- [ ] Spread filters operate
- [ ] One-position mode operates
- [ ] No martingale or grid behaviour exists

## Daily protection

- [ ] Maximum daily trades operates
- [ ] Maximum daily realised loss operates
- [ ] Consecutive-loss protection operates
- [ ] Cooldown after loss operates
- [ ] Protections reset on the intended broker day boundary

## Reproducibility

- [ ] Identical settings and data reproduce identical results
- [ ] Strategy Tester report saved
- [ ] `.set` file saved
- [ ] Broker, date range, commission, spread, and modelling mode documented

## Deployment status

- [ ] Research approval
- [ ] Demo forward-test approval
- [ ] Live approval requires a separate governance decision
