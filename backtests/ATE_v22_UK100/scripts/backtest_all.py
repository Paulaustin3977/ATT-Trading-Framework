#!/usr/bin/env python3
"""Default-params sweep: 6 symbols × 6 arms with thresholds 60/40.

Outputs:
    results/per_symbol.csv  — one row per (symbol, arm)
    results/aggregate.csv   — summary per arm
    results/per_arm/<arm>.png — per-arm equity curves for the panel
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.data import fetch_all  # noqa: E402
from src.indicators import compute_all  # noqa: E402
from src.strategies import all_strategies  # noqa: E402
from src.engine import simulate  # noqa: E402
from src.reporting import per_symbol_metrics, aggregate  # noqa: E402

RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)
(RESULTS / "per_arm").mkdir(exist_ok=True)


def main():
    print("Fetching data...")
    raw = fetch_all()
    strategies = all_strategies()

    rows = []
    arms_curves = {a: {} for a in strategies}

    for sym, df in raw.items():
        print(f"\n[{sym}] {len(df)} bars | {df.index[0].date()} → {df.index[-1].date()}")
        scored = compute_all(df)
        for arm_name, strat in strategies.items():
            res = simulate(scored, strat, symbol=sym)
            m = per_symbol_metrics(res, annual=252)
            rows.append(m)
            arms_curves[arm_name][sym] = res.equity_curve
            print(f"  {arm_name:<18s} trades={m['n_trades']:>4d}  ret={m['total_return']:>7.2%}  "
                  f"sharpe={m['sharpe']:>+5.2f}  dd={m['max_dd']:>7.2%}  "
                  f"wr={m['win_rate']:>5.1%}  pf={m['profit_factor']:>5.2f}")

    ps = pd.DataFrame(rows)
    ps.to_csv(RESULTS / "per_symbol.csv", index=False)
    ag = aggregate(ps)
    ag.to_csv(RESULTS / "aggregate.csv", index=False)
    print("\n=== AGGREGATE (by arm, sorted by mean Sharpe) ===")
    print(ag.to_string(index=False))

    # Per-arm equity-curve panels
    for arm_name, curves in arms_curves.items():
        if not curves:
            continue
        fig, ax = plt.subplots(figsize=(11, 5.5))
        for sym, eq in curves.items():
            if eq is None or eq.empty:
                continue
            ax.plot(eq.index, eq.values, label=sym, linewidth=1.1)
        ax.set_yscale("log")
        ax.set_title(f"ATE v2.2 — {arm_name} (long-thr=60, exit-thr=40) | £10k → log10")
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity (log)")
        ax.legend(loc="lower left", fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(RESULTS / "per_arm" / f"{arm_name}.png", dpi=110)
        plt.close(fig)

    # Aggregate by-class: best arm per symbol
    best = ps.loc[ps.groupby("symbol")["total_return"].idxmax(), ["symbol", "arm", "total_return", "sharpe", "max_dd"]]
    best = best.sort_values("total_return", ascending=False)
    best.to_csv(RESULTS / "best_per_symbol.csv", index=False)
    print("\n=== BEST ARM PER SYMBOL ===")
    print(best.to_string(index=False))

    print(f"\nWrote results/per_symbol.csv + aggregate.csv + per_arm/*.png")


if __name__ == "__main__":
    main()
