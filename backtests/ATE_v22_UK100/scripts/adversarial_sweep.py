#!/usr/bin/env python3
"""Adversarial sweep: tests the "inverted polarity" hypothesis for vol/risk
since the literal long>60 / exit<40 interpretation can produce zero trades
when risk>50 tends to dominate.

Strategy here:
  - vol_long:  LONG when vol is LOW-CALM (long when score < 40, exit when score > 60)
  - risk_long: LONG when risk is LOW-CALM (long when score < 30, exit when score > 50)
Plus the directional baselines.

Goal: surface whether ANY polarity of these non-directional scores yields edge.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from multiprocessing import Pool

from src.data import fetch_all
from src.indicators import compute_all
from src.engine import simulate
from src.reporting import per_symbol_metrics


# Both polarities for each arm
POLARITY_GRID = []
for arm, col in [
    ("trend_long",       "trend_score"),
    ("structure_long",   "structure_score"),
    ("momentum_long",    "momentum_score"),
    ("confidence_long",  "confidence_score"),
    ("vol_long_dir",     "vol_score"),       # long when high (current)
    ("vol_long_inv",     "vol_score"),       # long when LOW (anti-trend: enter calm, exit chaos)
    ("risk_long_dir",    "risk_score"),      # long when high (literally inverted already)
    ("risk_long_inv",    "risk_score"),      # long when LOW (low-risk regime)
]:
    for lt in (45.0, 55.0, 65.0):
        for et in (35.0, 45.0, 55.0):
            if lt <= et:
                continue
            POLARITY_GRID.append((arm, col, lt, et))


def _job(args):
    scored, sym, arm, col, lt, et = args
    from src.strategies import ScoreStrategy
    strat = ScoreStrategy(arm=arm, score_col=col, long_thr=lt, exit_thr=et)
    res = simulate(scored, strat, symbol=sym)
    m = per_symbol_metrics(res, annual=252)
    return {
        "symbol": sym, "arm": arm, "long_thr": lt, "exit_thr": et,
        "n_trades": m["n_trades"], "total_return": m["total_return"],
        "sharpe": m["sharpe"], "max_dd": m["max_dd"],
        "pct_time_in_market": m["pct_time_in_market"],
    }


def main():
    out_dir = ROOT / "results"
    print("Loading + scoring all symbols...")
    raw = fetch_all()
    scored = {sym: compute_all(df) for sym, df in raw.items()}

    # Inverse-polarity arms have SEMANTIC INVERSION (only for *_inv arms):
    # we want long when LOW, exit when HIGH — implemented via COL-sense flip in the engine.
    # Quickest path: pass (-1*lt, -1*et) as the threshold pair for *_inv arms so
    # long_thr < exit_thr flips to its inverse. But simpler: just simulate the
    # LONG-WHEN-LOW case by negating scores in the dataflow.

    tasks = []
    for sym, s_df in scored.items():
        for arm, col, lt, et in POLARITY_GRID:
            data = s_df.copy()
            if arm.endswith("_inv"):
                # semantic inversion: long when SCORE < lt, exit when SCORE > et.
                # We model this by negating the score AND using thresholds in the
                # standard ordering (lt > et) on the negated axis:
                #     long_enter on -score > -et  (i.e. score < et)
                #     exit        on -score < -lt  (i.e. score > lt)
                # We pick engine thresholds (long>lt_eff, exit<et_eff) so that
                # what actually fires is "lt_eff < score_orig < et_eff" semantically.
                # Simplest: keep numeric threshold ordering convention by using
                # the complementary "et as long, lt as exit" pair.
                data[col] = -data[col]
                lt_eff, et_eff = -et, -lt  # swap + negate so lt_eff > et_eff still
            else:
                lt_eff, et_eff = lt, et
            tasks.append((data, sym, arm, col, lt_eff, et_eff))

    print(f"Running {len(tasks)} (symbol, combo) tasks on 4 workers...")
    with Pool(4) as pool:
        rows = []
        for i, r in enumerate(pool.imap_unordered(_job, tasks)):
            rows.append(r)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(tasks)} done")

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "adversarial_per_symbol.csv", index=False)

    summary = df.groupby("arm").agg(
        n_symbols=("symbol", "nunique"),
        mean_return=("total_return", "mean"),
        median_return=("total_return", "median"),
        mean_sharpe=("sharpe", "mean"),
        median_sharpe=("sharpe", "median"),
        mean_dd=("max_dd", "mean"),
        mean_n_trades=("n_trades", "mean"),
        pct_positive=("total_return", lambda x: (x > 0).mean()),
        pct_pos_sharpe=("sharpe", lambda x: (x > 0).mean()),
    ).reset_index().sort_values("mean_sharpe", ascending=False)

    summary.to_csv(out_dir / "adversarial_summary.csv", index=False)
    print("\n=== ADVERSARIAL POLARITY SWEEP (sorted by mean Sharpe) ===")
    print(summary.to_string(index=False))

    # Top combos across all arms × thresholds, ranked by mean Sharpe
    top = df.groupby(["arm", "long_thr", "exit_thr"]).agg(
        n_symbols=("symbol", "nunique"),
        mean_sharpe=("sharpe", "mean"),
        mean_return=("total_return", "mean"),
        median_sharpe=("sharpe", "median"),
        mean_dd=("max_dd", "mean"),
        mean_n_trades=("n_trades", "mean"),
    ).reset_index().sort_values("mean_sharpe", ascending=False)
    top.to_csv(out_dir / "adversarial_top_combos.csv", index=False)
    print("\n=== TOP 15 COMBOS (mean Sharpe) ===")
    print(top.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
