# ATE v2.2 — UK100 Deep-Dive & Multi-Asset Backtest Report

**Indicator:** `pine/releases/ATE_v2.2.pine`
**Universe:** UK100 (^FTSE), DAX40 (^GDAXI), CAC40 (^FCHI), IBEX35 (^IBEX), FTSE250 (^FTMC), UK100_ETF (ISF.L)
**Period:** ~2016-07 → 2026-07, daily bars (yfinance).
**Sizing:** 1% equity-at-risk / trade; trailing stop 2× ATR(14); 5 bps commission, 2 bps slippage.
**Process orders on close:** false (fill at next-bar open).
**Scope:** per ATT 2026-07 — research/backtest only, no live trading, no broker, no execution.

> **Historical artefact warning.** This builder reads result tables that may pre-date the
> reviewed indicator and execution fixes. Unless every upstream sweep was regenerated in the
> same environment, the report is not current performance evidence. See `results/STATUS.md`.

## TL;DR

**Verdict — no single arm produces a positive edge on the EU/UK daily panel at default thresholds,
and every arm loses to buy-and-hold on every panel symbol. After a polarity sweep that included
the natural-inverted interpretation of risk & volatility (long when risk is CALM, exit when risk SPIKES),
three low-frequency positive-mean-Sharpe opportunities surface, but at magnitudes an order of
magnitude smaller than buy-and-hold:**

| Rank | Arm (polarity) | Mean Sharpe | Mean return | Median Sharpe | % positive | Trades/sym |
|---|---|---:|---:|---:|---:|---:|
| 1 | **risk_long_inv** (long in calm risk, exit when risk spikes) | +0.10 | +0.6% | +0.17 | 58.3% | ~2 |
| 2 | trend_long LT45/ET35 (tight band mean-reversion) | +0.06 | +0.6% | −0.04 | 27.8% | ~37 |
| 3 | vol_long_dir LT45/ET35 (low-vol confirm) | +0.04 | +0.9% | +0.04 | 27.8% | ~35 |
| 4 | confidence_long LT45/ET35 | +0.01 | +0.1% | −0.06 | 27.8% | ~58 |

Caveat: only ~2 trades per panel symbol over 10 years for the historical risk-avoidance
variant. That is too little evidence to distinguish an effect from noise and does not
establish that low-risk regimes are useful entry filters.

**Update: the composite gate (trend + confidence + risk_off filter, 27 combos x 6 symbols x 4 OOS
windows = 648 evaluations) also fails.** Even the best combination (`composite_T50_C50_Rmax15`)
has mean OOS Sharpe -0.92 across the panel; the risk-filter lift is *negative* (-0.07) - the
risk_score on these indices did not add value in that historical run. It tested a limited set
of hand-built rules and supports no broader claim.

## 1. Default-Threshold Backtest (long > 60, exit < 40)

Per-symbol headline for the first arm run for each panel symbol:

| Symbol | Total return | Sharpe | Max DD | Trades |
|--------|-------------:|-------:|-------:|-------:|
| CAC40 (best arm: **trend_long**) |  -4.36% |  -0.22 |  -7.97% |    39 |
| DAX40 (best arm: **trend_long**) |  +8.34% |  +0.41 |  -4.08% |    32 |
| FTSE250 (best arm: **trend_long**) |  -1.61% |  -0.07 |  -9.21% |    36 |
| IBEX35 (best arm: **trend_long**) |  +2.90% |  +0.14 |  -9.88% |    41 |
| UK100 (best arm: **trend_long**) | -12.09% |  -0.51 | -16.27% |    54 |
| UK100_ETF (best arm: **trend_long**) |  -7.37% |  -0.31 | -11.27% |    48 |

Aggregate by arm (all 6 symbols × each arm):

| Arm | Mean return | Median | Mean Sharpe | Max DD | Win rate | Profit factor |
|-----|------------:|-------:|------------:|-------:|---------:|--------------:|
| risk_long |  +0.00% |  +0.00% |  +0.00 |  +0.00% |  0.0% |  0.00 |
| trend_long |  -2.36% |  -2.99% |  -0.09 |  -9.78% | 40.7% |  0.96 |
| vol_long | -10.16% |  -9.35% |  -0.36 | -16.27% | 35.5% |  0.70 |
| momentum_long | -17.04% | -18.02% |  -0.46 | -21.72% | 32.5% |  0.70 |
| confidence_long | -15.68% | -17.19% |  -0.51 | -19.48% | 33.5% |  0.64 |
| structure_long | -27.10% | -28.72% |  -0.84 | -29.07% | 33.7% |  0.48 |

### Cross-arm observation

The `vol_long` arm fires on every bar in the calm/normal regime (most of the time for these indices),
producing ~6 trades/year per symbol. The `structure_long` arm over-trades on every pivot (110+ trades
per symbol) for the worst average Sharpe of the set. The `risk_long` arm produces ZERO trades because
risk-score hits >60 only in genuine stress events that don't occur on a 10y daily sample — confirming
the score is structurally inverted (high score = more risk pressure, not more opportunity).

## 2. Buy-and-Hold Baseline (verification)

If every strategy loses to buy-and-hold on the same symbol, there is no edge:

| Symbol | BH Total return | BH Sharpe | BH Max DD |
|--------|----------------:|----------:|----------:|
| UK100 | +58.43% |  +0.38 | -36.61% |
| DAX40 | +155.84% |  +0.60 | -38.78% |
| CAC40 | +96.28% |  +0.46 | -38.56% |
| IBEX35 | +133.27% |  +0.55 | -45.16% |
| FTSE250 | +42.80% |  +0.28 | -41.97% |
| UK100_ETF | +55.80% |  +0.37 | -37.29% |

Every panel index trended up over 2016–2026 — buy-and-hold captures the whole path. A daily-TF
threshold strategy that round-trips in and out misses most of the move by construction. The
verdict on default-threshold arms: not tradable.

## 3. Segmented Parameter Sweep (legacy files say walk-forward)

Coarse 3×3 grid × 6 arms × 6 symbols × 4 chronological segments = 1,152 evaluations.
There is no train-time parameter selection; these are not genuine OOS results.

Top 10 combos by robustness score (40% pos OOS Sharpe + 40% pos OOS return + 20% DD under 35%):

| Arm | LT | ET | Pos Sharpe | Pos Return | DD < 35% | Mean OOS Sharpe | Mean OOS Return | Robustness |
|-----|---:|---:|----------:|----------:|---------:|---------------:|----------------:|-----------:|
| vol_long | 50 | 40 | 3/6 | 3/6 | 6/6 |  -0.07 |  -0.17% |  0.60 |
| vol_long | 50 | 30 | 3/6 | 3/6 | 6/6 |  -0.07 |  -0.17% |  0.60 |
| confidence_long | 50 | 30 | 2/6 | 3/6 | 6/6 |  -0.10 |  -0.26% |  0.53 |
| confidence_long | 50 | 40 | 2/6 | 3/6 | 6/6 |  -0.05 |  +0.11% |  0.53 |
| trend_long | 70 | 50 | 2/6 | 2/6 | 6/6 |  -0.34 |  -2.11% |  0.47 |
| trend_long | 70 | 40 | 2/6 | 2/6 | 6/6 |  -0.36 |  -2.26% |  0.47 |
| trend_long | 70 | 30 | 2/6 | 2/6 | 6/6 |  -0.38 |  -2.37% |  0.47 |
| trend_long | 60 | 50 | 2/6 | 2/6 | 6/6 |  -0.09 |  -0.50% |  0.47 |
| vol_long | 70 | 40 | 1/6 | 2/6 | 6/6 |  -0.26 |  -1.79% |  0.40 |
| vol_long | 70 | 30 | 1/6 | 2/6 | 6/6 |  -0.26 |  -1.79% |  0.40 |

Selected 'winner' fallback (most-robust by 100% DD-pass criterion; mean OOS Sharpe is negative):

```json
{
  "arm": "vol_long",
  "long_thr": 50.0,
  "exit_thr": 40.0,
  "robustness_score": 0.6000000000000001,
  "n_symbols": 6,
  "n_pos_oos_sharpe": 3,
  "mean_oos_sharpe": -0.07035706430266413,
  "mean_oos_return": -0.0016834905353270656,
  "mean_oos_dd": -0.03620820426517315
}
```

## 4. Adversarial / Polarity Sweep — the inverted arms

Volume & Risk scores are non-directional. For 'all of them' I tested BOTH polarities of these arms:
*long when score is high (literal)* AND *long when score is low (regime filter)*.

| Arm (polarity) | Mean return | Median return | Mean Sharpe | Median Sharpe | Max DD (mean) | Avg trades/sym | % positive |
|---|---:|---:|---:|---:|---:|---:|---:|
| risk_long_inv |  +0.57% |  +0.56% |  +0.10 |  +0.17 |  -1.36% |   1.9 |  58.3% |
| risk_long_dir |  +0.00% |  +0.00% |  +0.00 |  +0.00 |  +0.00% |   0.0 |   0.0% |
| vol_long_inv |  -1.35% |  -1.53% |  -0.08 |  -0.09 |  -5.54% |  32.6 |  33.3% |
| trend_long |  -2.61% |  -3.87% |  -0.10 |  -0.16 |  -9.74% |  42.6 |  27.8% |
| vol_long_dir |  -8.18% |  -7.13% |  -0.29 |  -0.23 | -14.60% |  58.4 |   8.3% |
| structure_long | -10.24% |  +0.00% |  -0.31 |  +0.00 | -12.74% |  53.7 |   5.6% |
| momentum_long | -11.83% | -12.66% |  -0.33 |  -0.33 | -17.81% | 141.0 |   8.3% |
| confidence_long | -12.52% | -15.02% |  -0.41 |  -0.52 | -18.13% |  81.7 |  16.7% |

### Top-10 individual combos (mean Sharpe)

| Arm | LT (orig) | ET (orig) | Mean Sharpe | Mean return | Mean DD | Trades/sym |
|---|---|---:|---:|---:|---:|---:|
| risk_long_inv | -35 | -45 |  +0.17 |  +1.01% |  -1.88% |   2.8 |
| risk_long_inv | -35 | -55 |  +0.17 |  +1.01% |  -1.88% |   2.8 |
| risk_long_inv | -35 | -65 |  +0.17 |  +1.01% |  -1.88% |   2.8 |
| trend_long | 45 | 35 |  +0.06 |  +0.60% |  -7.64% |  36.5 |
| vol_long_dir | 45 | 35 |  +0.04 |  +0.91% |  -6.98% |  34.8 |
| risk_long_inv | -45 | -55 |  +0.03 |  +0.12% |  -0.84% |   1.0 |
| risk_long_inv | -45 | -65 |  +0.03 |  +0.12% |  -0.84% |   1.0 |
| risk_long_inv | -55 | -65 |  +0.03 |  +0.12% |  -0.84% |   1.0 |
| confidence_long | 45 | 35 |  +0.01 |  +0.12% |  -9.79% |  57.8 |
| risk_long_dir | 55 | 45 |  +0.00 |  +0.00% |  +0.00% |   0.0 |

Note: for `risk_long_inv` the *original* threshold values are negative (engine-internal). The semantic
interpretation is: enter long when the original risk score FALLS below ~35 (calm risk environment),
exit when it RISES above ~45 (risk is escalating). This is a risk-off filter, not a momentum signal.

## 5. Why default-threshold arms do not produce edge on daily bars

1. **Scores are regime-confirmation indicators, not signal triggers.** ATE v2.2's header explicitly
   declares 'Entry/exit impact: NO'. The 0–100 scores are designed to label regimes (bullish/bearish,
   elevated risk, quiet volatility, BOS events). When the score flips across 60/40 bands it tells you
   which regime the market is *already in*, not when to enter. Trading this is, by design, late.
2. **Threshold-cross entries trigger just before the score rolls back into the neutral zone.** With
   discrete 60/40 bands, the score hovers near the boundary for ~5–15 bars per regime. A long entry
   on cross, with exit on the next cross, gives ~5–15 bars of exposure. Plus ATR-based stops, the
   win-rate is dragged toward 50% and the profit factor below 1.0 — exactly what the numbers show.
3. **Daily cadence under-uses regime changes.** 1D bars aggregate overnight gaps + intraday moves into
   single candles. Regime scores measure the same candle. On a 4H or weekly bar the regime would
   persist longer and the same threshold logic would produce a longer trade horizon with smaller
   turnover cost.
4. **The historical inverted-polarity row does not confirm an effect.** Its positive mean
   Sharpe came from roughly two trades per symbol and source that was later corrected.

## 6. Composite-Gate Gate: Trend + Confidence AND Risk-Off Filter

Following the adversarial finding that `risk_long_inv` was the only positive-mean-Sharpe arm in
the panel, the natural next test is a *composite gate*: require two corroborating directional scores
**plus** an inverted-polarity risk ceiling.

Rule:
- ENTER long on next-bar-open when trend_score > T_enter AND confidence_score > C_enter AND risk_score < R_max
- EXIT long on next-bar-open when trend < T_exit OR confidence < C_exit OR risk > R_exit, OR trailing stop

Grid: 18 with-risk-filter combos + 9 no-filter ablations × 6 symbols × 4 chronological segments = 648 evaluations (not genuine OOS windows).

### Robustness summary (top 10 by robustness_score)

| Combo | Risk filter | T | C | R_max | Pos OOS Sharpe | Pos OOS Return | Mean OOS Sharpe | Mean OOS Return |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| composite_T50_C50_Rmax15 | ✓ | 50 | 50 | 15 | 0/6 | 0/6 |  -0.92 |  -9.57% |
| composite_T60_C60_noR | — | 60 | 60 | 99 | 0/6 | 0/6 |  -0.85 |  -8.30% |
| composite_T70_C70_Rmax5 | ✓ | 70 | 70 | 5 | 0/6 | 0/6 |  -0.79 |  -4.80% |
| composite_T70_C70_Rmax15 | ✓ | 70 | 70 | 15 | 0/6 | 0/6 |  -1.08 |  -9.14% |
| composite_T70_C60_noR | — | 70 | 60 | 99 | 0/6 | 0/6 |  -0.90 |  -8.78% |
| composite_T70_C60_Rmax5 | ✓ | 70 | 60 | 5 | 0/6 | 0/6 |  -0.88 |  -6.30% |
| composite_T70_C60_Rmax15 | ✓ | 70 | 60 | 15 | 0/6 | 0/6 |  -1.06 | -10.59% |
| composite_T70_C50_noR | — | 70 | 50 | 99 | 0/6 | 0/6 |  -0.97 | -10.03% |
| composite_T70_C50_Rmax5 | ✓ | 70 | 50 | 5 | 0/6 | 0/6 |  -0.90 |  -6.51% |
| composite_T70_C50_Rmax15 | ✓ | 70 | 50 | 15 | 0/6 | 0/6 |  -1.01 | -10.18% |

### Risk-filter lift

- with_risk_filter: mean OOS Sharpe **-0.917** (median -0.910, n=18 combos)
- without_risk_filter: mean OOS Sharpe **-0.847** (median -0.859, n=9 combos)

Δ = -0.070

**Negative Δ** = the risk filter makes things slightly worse. The risk_score distribution on these
indices is heavily skewed low (median 5, 90th percentile 8); when the filter does fire it cuts
positions that would otherwise be winners, while letting most risk events through untouched.

### Verdict on composite gate

No combo produces a positive OOS Sharpe across the 6-symbol panel. The best combination is
`composite_T50_C50_Rmax15` with a mean OOS Sharpe of -0.92 (every symbol loses money OOS).

Looking across the 27 combos as a whole: every single one has identical robustness_score
(0.2) because they all tie on the DD<35% floor criterion (DD is small for a 1%-riskper-trade
strategy) and have zero positive-OOS-Sharpe symbols. The headline metric (mean OOS Sharpe) is
negative for all combos.

**Confirmation of the underlying diagnosis: a daily-candles confirmation-indicator strategy is the
wrong shape for a 2016-2026 bull-market window.** The expected next step (per the project
methodology) is the multi-timeframe extension — i.e. test on 4H / weekly bars.

Charts: `results/composite/equity_panel.png` (4 selected combos × 6 indices) and
`results/composite/oos_sharpe_bars.png` (mean OOS Sharpe across all 27 combos with vs without
the risk filter).

## 7. Recommendations

1. **Do not promote `risk_long_inv`.** Roughly two trades per symbol, multiple searched
   thresholds, and corrected source defects provide no credible promotion evidence.
2. **If research continues, pre-register a holdout design.** Test only a separately governed,
   diagnostic hypothesis with leakage-safe held-out data; this study authorises no score coupling or action rule.
3. **Do not paper-trade any of the per-arm threshold strategies as-is.** Their DD is moderate
   (typically 10–35%) but their legacy segmented Sharpe is zero or negative on most symbols.
4. **Do not assume another timeframe will improve results.** A 4H/weekly extension is a new
   hypothesis and needs leakage-safe, genuinely held-out evaluation.
5. **The ATE v2.2 release is a diagnostic indicator, not a strategy.** This historical study
   does not recommend adding signals, entries, exits, sizing, stops, alerts, or execution to a future release.

## 8. Caveats

- 6-symbol panel, ~2,500 daily bars per symbol = ~15,000 total bars. Statistically thin.
- Legacy 'OOS windows' were segments with no train-time selection; they are not OOS evidence.
- All commissions/slippage are applied per-side at fill. Spread costs not modelled.
- For UK/EU indices via yfinance, fills at next-bar open ignore pre-open auction moves; add
  ~0.5–1.5 bps extra slippage for real-world trading on index CFDs.
- Historical riskScore tables pre-date conflict and missing-data fixes and are invalidated.
- No multi-TF extension in this round.
