#!/usr/bin/env python3
"""Build the verdict report for ATE v2.2 UK100 deep-dive + backtest."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = ROOT / "results"


def fetch_only(sym: str) -> pd.DataFrame:
    from src.data import fetch
    return fetch(sym)


def buy_and_hold_row(df: pd.DataFrame, sym: str) -> dict:
    p_open = df["open"].iloc[0]
    p_close = df["close"].iloc[-1]
    initial = 10_000.0
    qty = initial / p_open
    final = qty * p_close
    rets = df["close"].pct_change().dropna()
    sharpe = float(rets.mean() / rets.std() * (252 ** 0.5)) if rets.std() else 0.0
    eq = pd.Series(qty * df["close"].values, index=df.index)
    peak = eq.cummax()
    dd = (eq / peak - 1).min()
    return {"symbol": sym, "total_return": final / initial - 1, "sharpe": sharpe, "max_dd": float(dd)}


def build_equity_panel():
    from src.data import fetch_all
    from src.indicators import compute_all
    from src.strategies import all_strategies
    from src.engine import simulate

    print("Building equity-panel chart...")
    raw = fetch_all()
    strats = all_strategies()
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.ravel()
    colours = {"UK100": "C0", "DAX40": "C1", "CAC40": "C2",
               "IBEX35": "C3", "FTSE250": "C4", "UK100_ETF": "C5"}
    for i, (arm_name, strat) in enumerate(strats.items()):
        ax = axes[i]
        for sym, df in raw.items():
            s = compute_all(df)
            r = simulate(s, strat, symbol=sym)
            eq = r.equity_curve
            if eq.empty:
                continue
            ax.plot(eq.index, eq.values, label=sym, color=colours.get(sym), linewidth=1.0)
        ax.axhline(10000, color="black", linewidth=0.7, linestyle="--", alpha=0.5)
        ax.set_yscale("log")
        ax.set_title(f"{arm_name}", fontsize=11)
        ax.set_xlabel("")
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.legend(loc="lower left", fontsize=8)
    fig.suptitle("ATE v2.2 — 6 Arms × 6 EU/UK Indices | £10k → log10 (default thresholds 60/40)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    out = RESULTS / "equity_panel.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print(f"  wrote {out}")


def build_report_md():
    per_sym = pd.read_csv(RESULTS / "per_symbol.csv")
    agg = pd.read_csv(RESULTS / "aggregate.csv")
    bh_rows = []
    from src.data import fetch_all
    for sym, df in fetch_all().items():
        bh_rows.append(buy_and_hold_row(df, sym))
    bh_df = pd.DataFrame(bh_rows)

    opt_summary = pd.read_csv(RESULTS / "optimization" / "walk_forward_summary.csv")
    opt_winner_path = RESULTS / "optimization" / "winner.json"
    opt_winner = json.load(open(opt_winner_path)) if opt_winner_path.exists() else {}

    adv_per = pd.read_csv(RESULTS / "adversarial_per_symbol.csv")
    adv_summ = pd.read_csv(RESULTS / "adversarial_summary.csv")
    adv_top = pd.read_csv(RESULTS / "adversarial_top_combos.csv")

    lines = []
    add = lines.append
    add("# ATE v2.2 — UK100 Deep-Dive & Multi-Asset Backtest Report")
    add("")
    add("**Indicator:** `pine/releases/ATE_v2.2.pine`")
    add("**Universe:** UK100 (^FTSE), DAX40 (^GDAXI), CAC40 (^FCHI), IBEX35 (^IBEX), FTSE250 (^FTMC), UK100_ETF (ISF.L)")
    add("**Period:** ~2016-07 → 2026-07, daily bars (yfinance).")
    add("**Sizing:** 1% equity-at-risk / trade; trailing stop 2× ATR(14); 5 bps commission, 2 bps slippage.")
    add("**Process orders on close:** false (fill at next-bar open).")
    add("**Scope:** per ATT 2026-07 — research/backtest only, no live trading, no broker, no execution.")
    add("")
    add("> **Historical artefact warning.** This builder reads result tables that may pre-date the")
    add("> reviewed indicator and execution fixes. Unless every upstream sweep was regenerated in the")
    add("> same environment, the report is not current performance evidence. See `results/STATUS.md`.")
    add("")
    add("## TL;DR")
    add("")
    add("**Verdict — no single arm produces a positive edge on the EU/UK daily panel at default thresholds,")
    add("and every arm loses to buy-and-hold on every panel symbol. After a polarity sweep that included")
    add("the natural-inverted interpretation of risk & volatility (long when risk is CALM, exit when risk SPIKES),")
    add("three low-frequency positive-mean-Sharpe opportunities surface, but at magnitudes an order of")
    add("magnitude smaller than buy-and-hold:**")
    add("")
    add("| Rank | Arm (polarity) | Mean Sharpe | Mean return | Median Sharpe | % positive | Trades/sym |")
    add("|---|---|---:|---:|---:|---:|---:|")
    add("| 1 | **risk_long_inv** (long in calm risk, exit when risk spikes) | +0.10 | +0.6% | +0.17 | 58.3% | ~2 |")
    add("| 2 | trend_long LT45/ET35 (tight band mean-reversion) | +0.06 | +0.6% | −0.04 | 27.8% | ~37 |")
    add("| 3 | vol_long_dir LT45/ET35 (low-vol confirm) | +0.04 | +0.9% | +0.04 | 27.8% | ~35 |")
    add("| 4 | confidence_long LT45/ET35 | +0.01 | +0.1% | −0.06 | 27.8% | ~58 |")
    add("")
    add("Caveat: only ~2 trades per panel symbol over 10 years for the historical risk-avoidance")
    add("variant. That is too little evidence to distinguish an effect from noise and does not")
    add("establish that low-risk regimes are useful entry filters.")
    add("")
    add('**Update: the composite gate (trend + confidence + risk_off filter, 27 combos x 6 symbols x 4 OOS')
    add('windows = 648 evaluations) also fails.** Even the best combination (`composite_T50_C50_Rmax15`)')
    add('has mean OOS Sharpe -0.92 across the panel; the risk-filter lift is *negative* (-0.07) - the')
    add('risk_score on these indices did not add value in that historical run. It tested a limited set')
    add('of hand-built rules and supports no broader claim.')
    add("")
    add("## 1. Default-Threshold Backtest (long > 60, exit < 40)")
    add("")
    add("Per-symbol headline for the first arm run for each panel symbol:")
    add("")
    add("| Symbol | Total return | Sharpe | Max DD | Trades |")
    add("|--------|-------------:|-------:|-------:|-------:|")
    # One-row-per-symbol aggregated across the worst-default arm + best-default arm
    for sym in sorted(per_sym["symbol"].unique()):
        sub = per_sym[per_sym.symbol == sym]
        # Pick the row from each default-arm with the best return
        best = sub.loc[sub["total_return"].idxmax()] if (sub["total_return"] > 0).any() else sub.iloc[0]
        add(f"| {sym} (best arm: **{best['arm']}**) | {best['total_return']:>+7.2%} | "
            f"{best['sharpe']:>+6.2f} | {best['max_dd']:>+7.2%} | {int(best['n_trades']):>5d} |")
    add("")
    add("Aggregate by arm (all 6 symbols × each arm):")
    add("")
    add("| Arm | Mean return | Median | Mean Sharpe | Max DD | Win rate | Profit factor |")
    add("|-----|------------:|-------:|------------:|-------:|---------:|--------------:|")
    for _, r in agg.iterrows():
        add(f"| {r['arm']} | {r['mean_return']:>+7.2%} | {r['median_return']:>+7.2%} | "
            f"{r['mean_sharpe']:>+6.2f} | {r['mean_max_dd']:>+7.2%} | "
            f"{r['mean_win_rate']:>5.1%} | {r['mean_pf']:>5.2f} |")
    add("")
    add("### Cross-arm observation")
    add("")
    add("The `vol_long` arm fires on every bar in the calm/normal regime (most of the time for these indices),")
    add("producing ~6 trades/year per symbol. The `structure_long` arm over-trades on every pivot (110+ trades")
    add("per symbol) for the worst average Sharpe of the set. The `risk_long` arm produces ZERO trades because")
    add("risk-score hits >60 only in genuine stress events that don't occur on a 10y daily sample — confirming")
    add("the score is structurally inverted (high score = more risk pressure, not more opportunity).")
    add("")

    add("## 2. Buy-and-Hold Baseline (verification)")
    add("")
    add("If every strategy loses to buy-and-hold on the same symbol, there is no edge:")
    add("")
    add("| Symbol | BH Total return | BH Sharpe | BH Max DD |")
    add("|--------|----------------:|----------:|----------:|")
    for _, r in bh_df.iterrows():
        add(f"| {r['symbol']} | {r['total_return']:>+7.2%} | {r['sharpe']:>+6.2f} | {r['max_dd']:>+7.2%} |")
    add("")
    add("Every panel index trended up over 2016–2026 — buy-and-hold captures the whole path. A daily-TF")
    add("threshold strategy that round-trips in and out misses most of the move by construction. The")
    add("verdict on default-threshold arms: not tradable.")
    add("")

    add("## 3. Segmented Parameter Sweep (legacy files say walk-forward)")
    add("")
    add("Coarse 3×3 grid × 6 arms × 6 symbols × 4 chronological segments = 1,152 evaluations.")
    add("There is no train-time parameter selection; these are not genuine OOS results.")
    add("")
    add("Top 10 combos by robustness score (40% pos OOS Sharpe + 40% pos OOS return + 20% DD under 35%):")
    add("")
    add("| Arm | LT | ET | Pos Sharpe | Pos Return | DD < 35% | Mean OOS Sharpe | Mean OOS Return | Robustness |")
    add("|-----|---:|---:|----------:|----------:|---------:|---------------:|----------------:|-----------:|")
    for _, r in opt_summary.head(10).iterrows():
        add(f"| {r['arm']} | {int(r['long_thr'])} | {int(r['exit_thr'])} | "
            f"{int(r['n_pos_oos_sharpe'])}/{int(r['n_symbols'])} | "
            f"{int(r['n_pos_oos_return'])}/{int(r['n_symbols'])} | "
            f"{int(r['n_dd_under_35pct'])}/{int(r['n_symbols'])} | "
            f"{r['mean_oos_sharpe']:>+6.2f} | {r['mean_oos_return']:>+7.2%} | "
            f"{r['robustness_score']:>5.2f} |")
    add("")
    if opt_winner:
        add("Selected 'winner' fallback (most-robust by 100% DD-pass criterion; mean OOS Sharpe is negative):")
        add("")
        add("```json")
        add(json.dumps(opt_winner, indent=2))
        add("```")
    add("")

    add("## 4. Adversarial / Polarity Sweep — the inverted arms")
    add("")
    add("Volume & Risk scores are non-directional. For 'all of them' I tested BOTH polarities of these arms:")
    add("*long when score is high (literal)* AND *long when score is low (regime filter)*.")
    add("")
    add("| Arm (polarity) | Mean return | Median return | Mean Sharpe | Median Sharpe | Max DD (mean) | Avg trades/sym | % positive |")
    add("|---|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in adv_summ.sort_values("mean_sharpe", ascending=False).iterrows():
        add(f"| {r['arm']} | {r['mean_return']:>+7.2%} | {r['median_return']:>+7.2%} | "
            f"{r['mean_sharpe']:>+6.2f} | {r['median_sharpe']:>+6.2f} | {r['mean_dd']:>+7.2%} | "
            f"{r['mean_n_trades']:>5.1f} | {r['pct_positive']:>6.1%} |")
    add("")
    add("### Top-10 individual combos (mean Sharpe)")
    add("")
    add("| Arm | LT (orig) | ET (orig) | Mean Sharpe | Mean return | Mean DD | Trades/sym |")
    add("|---|---|---:|---:|---:|---:|---:|")
    for _, r in adv_top.head(10).iterrows():
        add(f"| {r['arm']} | {int(r['long_thr'])} | {int(r['exit_thr'])} | "
            f"{r['mean_sharpe']:>+6.2f} | {r['mean_return']:>+7.2%} | "
            f"{r['mean_dd']:>+7.2%} | {r['mean_n_trades']:>5.1f} |")
    add("")
    add("Note: for `risk_long_inv` the *original* threshold values are negative (engine-internal). The semantic")
    add("interpretation is: enter long when the original risk score FALLS below ~35 (calm risk environment),")
    add("exit when it RISES above ~45 (risk is escalating). This is a risk-off filter, not a momentum signal.")
    add("")
    add("## 5. Why default-threshold arms do not produce edge on daily bars")
    add("")
    add("1. **Scores are regime-confirmation indicators, not signal triggers.** ATE v2.2's header explicitly")
    add("   declares 'Entry/exit impact: NO'. The 0–100 scores are designed to label regimes (bullish/bearish,")
    add("   elevated risk, quiet volatility, BOS events). When the score flips across 60/40 bands it tells you")
    add("   which regime the market is *already in*, not when to enter. Trading this is, by design, late.")
    add("2. **Threshold-cross entries trigger just before the score rolls back into the neutral zone.** With")
    add("   discrete 60/40 bands, the score hovers near the boundary for ~5–15 bars per regime. A long entry")
    add("   on cross, with exit on the next cross, gives ~5–15 bars of exposure. Plus ATR-based stops, the")
    add("   win-rate is dragged toward 50% and the profit factor below 1.0 — exactly what the numbers show.")
    add("3. **Daily cadence under-uses regime changes.** 1D bars aggregate overnight gaps + intraday moves into")
    add("   single candles. Regime scores measure the same candle. On a 4H or weekly bar the regime would")
    add("   persist longer and the same threshold logic would produce a longer trade horizon with smaller")
    add("   turnover cost.")
    add("4. **The historical inverted-polarity row does not confirm an effect.** Its positive mean")
    add("   Sharpe came from roughly two trades per symbol and source that was later corrected.")
    add("")

    add("## 6. Composite-Gate Gate: Trend + Confidence AND Risk-Off Filter")
    add("")
    add("Following the adversarial finding that `risk_long_inv` was the only positive-mean-Sharpe arm in")
    add("the panel, the natural next test is a *composite gate*: require two corroborating directional scores")
    add("**plus** an inverted-polarity risk ceiling.")
    add("")
    add("Rule:")
    add("- ENTER long on next-bar-open when trend_score > T_enter AND confidence_score > C_enter AND risk_score < R_max")
    add("- EXIT long on next-bar-open when trend < T_exit OR confidence < C_exit OR risk > R_exit, OR trailing stop")
    add("")
    add("Grid: 18 with-risk-filter combos + 9 no-filter ablations × 6 symbols × 4 chronological segments = 648 evaluations (not genuine OOS windows).")
    add("")
    add("### Robustness summary (top 10 by robustness_score)")
    add("")
    add("| Combo | Risk filter | T | C | R_max | Pos OOS Sharpe | Pos OOS Return | Mean OOS Sharpe | Mean OOS Return |")
    add("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    summ = pd.read_csv(RESULTS / "composite" / "walk_forward_summary.csv")
    for _, r in summ.head(10).iterrows():
        rf = "✓" if r["require_risk_filter"] else "—"
        add(f"| {r['name']} | {rf} | {int(r['T_enter'])} | {int(r['C_enter'])} | "
            f"{int(r['R_max'])} | "
            f"{int(r['n_pos_oos_sharpe'])}/{int(r['n_symbols'])} | "
            f"{int(r['n_pos_oos_return'])}/{int(r['n_symbols'])} | "
            f"{r['mean_oos_sharpe']:>+6.2f} | {r['mean_oos_return']:>+7.2%} |")
    add("")
    add("### Risk-filter lift")
    add("")
    lift = pd.read_csv(RESULTS / "composite" / "risk_filter_lift.csv")
    for _, r in lift.iterrows():
        add(f"- {r['filter']}: mean OOS Sharpe **{r['mean_oos_sharpe']:+.3f}** "
            f"(median {r['median_oos_sharpe']:+.3f}, n={int(r['n_combos'])} combos)")
    add("")
    add(f"Δ = {lift.iloc[0]['mean_oos_sharpe'] - lift.iloc[1]['mean_oos_sharpe']:+.3f}")
    add("")
    add("**Negative Δ** = the risk filter makes things slightly worse. The risk_score distribution on these")
    add("indices is heavily skewed low (median 5, 90th percentile 8); when the filter does fire it cuts")
    add("positions that would otherwise be winners, while letting most risk events through untouched.")
    add("")
    add("### Verdict on composite gate")
    add("")
    add("No combo produces a positive OOS Sharpe across the 6-symbol panel. The best combination is")
    add("`composite_T50_C50_Rmax15` with a mean OOS Sharpe of -0.92 (every symbol loses money OOS).")
    add("")
    add("Looking across the 27 combos as a whole: every single one has identical robustness_score")
    add("(0.2) because they all tie on the DD<35% floor criterion (DD is small for a 1%-riskper-trade")
    add("strategy) and have zero positive-OOS-Sharpe symbols. The headline metric (mean OOS Sharpe) is")
    add("negative for all combos.")
    add("")
    add("**Confirmation of the underlying diagnosis: a daily-candles confirmation-indicator strategy is the")
    add("wrong shape for a 2016-2026 bull-market window.** The expected next step (per the project")
    add("methodology) is the multi-timeframe extension — i.e. test on 4H / weekly bars.")
    add("")
    add("Charts: `results/composite/equity_panel.png` (4 selected combos × 6 indices) and")
    add("`results/composite/oos_sharpe_bars.png` (mean OOS Sharpe across all 27 combos with vs without")
    add("the risk filter).")
    add("")

    add("## 7. Recommendations")
    add("")
    add("1. **Do not promote `risk_long_inv`.** Roughly two trades per symbol, multiple searched")
    add("   thresholds, and corrected source defects provide no credible promotion evidence.")
    add("2. **If research continues, pre-register a holdout design.** Test only a separately governed,")
    add("   diagnostic hypothesis with leakage-safe held-out data; this study authorises no score coupling or action rule.")
    add("3. **Do not paper-trade any of the per-arm threshold strategies as-is.** Their DD is moderate")
    add("   (typically 10–35%) but their legacy segmented Sharpe is zero or negative on most symbols.")
    add("4. **Do not assume another timeframe will improve results.** A 4H/weekly extension is a new")
    add("   hypothesis and needs leakage-safe, genuinely held-out evaluation.")
    add("5. **The ATE v2.2 release is a diagnostic indicator, not a strategy.** This historical study")
    add("   does not recommend adding signals, entries, exits, sizing, stops, alerts, or execution to a future release.")
    add("")

    add("## 8. Caveats")
    add("")
    add("- 6-symbol panel, ~2,500 daily bars per symbol = ~15,000 total bars. Statistically thin.")
    add("- Legacy 'OOS windows' were segments with no train-time selection; they are not OOS evidence.")
    add("- All commissions/slippage are applied per-side at fill. Spread costs not modelled.")
    add("- For UK/EU indices via yfinance, fills at next-bar open ignore pre-open auction moves; add")
    add("  ~0.5–1.5 bps extra slippage for real-world trading on index CFDs.")
    add("- Historical riskScore tables pre-date conflict and missing-data fixes and are invalidated.")
    add("- No multi-TF extension in this round.")
    add("")

    (RESULTS / "report.md").write_text("\n".join(lines))
    print(f"  wrote {RESULTS / 'report.md'}")


if __name__ == "__main__":
    build_equity_panel()
    build_report_md()
