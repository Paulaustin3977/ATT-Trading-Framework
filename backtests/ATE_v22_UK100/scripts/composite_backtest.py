#!/usr/bin/env python3
"""Composite-gate segmented chronological evaluation + robustness scoring.

Grid: 18 with-risk-filter combos + 9 no-risk-filter combos (ablation).
Sweep: 27 combos × 6 symbols × 4 time segments = 648 evaluations.

There is no train-time parameter selection. Legacy result filenames retain
``walk_forward`` for compatibility, but these metrics are not OOS evidence.

We run the full default-threshold-first vs risk-filter-on comparison:
1) Default no-filter trends+confirmation only (T>C baseline)
2) + risk ceiling (R_max = 30 or 40) on entry
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json
import multiprocessing as mp
from dataclasses import asdict

import numpy as np
import pandas as pd

from src.data import fetch_all
from src.indicators import compute_all
from src.composite import composite_grid, Composite
from src.composite_engine import simulate_composite
from src.reporting import per_symbol_metrics
from src.optimizer import _split_windows

RESULTS = ROOT / "results" / "composite"
RESULTS.mkdir(parents=True, exist_ok=True)


def _job(args):
    scored_slice, comp, symbol, window = args
    res = simulate_composite(scored_slice, comp, symbol=symbol)
    if not res.trades:
        return {
            "name": comp.name, "require_risk_filter": comp.require_risk_filter,
            "T_enter": comp.T_enter, "C_enter": comp.C_enter, "R_max": comp.R_max,
            "symbol": symbol, "window": window,
            "n_trades": 0, "total_return": 0.0, "sharpe": 0.0, "max_dd": 0.0,
        }
    m = per_symbol_metrics(res, annual=252)
    return {
        "name": comp.name, "require_risk_filter": comp.require_risk_filter,
        "T_enter": comp.T_enter, "C_enter": comp.C_enter, "R_max": comp.R_max,
        "symbol": symbol, "window": window,
        "n_trades": m["n_trades"], "total_return": m["total_return"],
        "sharpe": m["sharpe"], "max_dd": m["max_dd"],
    }


def main():
    raw = fetch_all()
    scored = {sym: compute_all(df) for sym, df in raw.items()}
    grid = composite_grid()
    print(f"Composite grid: {len(grid)} combos × 6 symbols × 4 windows = {len(grid)*6*4} tasks")
    tasks = []
    for comp in grid:
        for sym, s_df in scored.items():
            for w_idx, (start, end) in enumerate(_split_windows(len(s_df))):
                slice_ = s_df.iloc[start:end]
                tasks.append((slice_, comp, sym, w_idx))

    with mp.Pool(4) as pool:
        rows = []
        for i, r in enumerate(pool.imap_unordered(_job, tasks)):
            rows.append(r)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(tasks)} done")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "walk_forward_raw.csv", index=False)

    # Per-symbol aggregate per combo
    per_sym = df.groupby(["name", "symbol"]).agg(
        mean_sharpe=("sharpe", "mean"),
        mean_return=("total_return", "mean"),
        mean_dd=("max_dd", "mean"),
        n_trades=("n_trades", "sum"),
    ).reset_index()
    per_sym.to_csv(RESULTS / "walk_forward_per_symbol.csv", index=False)

    # Per-combo robustness score
    grouped = df.groupby("name")
    rows = []
    for name, g in grouped:
        per_s = g.groupby("symbol").agg(
            mean_sharpe=("sharpe", "mean"),
            mean_return=("total_return", "mean"),
            mean_dd=("max_dd", "mean"),
        )
        n_sym = len(per_s)
        n_pos_sharpe = (per_s["mean_sharpe"] > 0).sum()
        n_pos_return = (per_s["mean_return"] > 0).sum()
        n_dd_ok = (per_s["mean_dd"] > -0.35).sum()
        # NEW: combined risk filter tag carries as 1.0 / 1.1 / 1.2 multiplier only if positive impact
        robustness = (
            0.4 * (n_pos_sharpe / n_sym)
            + 0.4 * (n_pos_return / n_sym)
            + 0.2 * (n_dd_ok / n_sym)
        )
        risk_filter = bool(g["require_risk_filter"].iloc[0])
        rows.append({
            "name": name, "require_risk_filter": risk_filter,
            "T_enter": float(g["T_enter"].iloc[0]), "C_enter": float(g["C_enter"].iloc[0]),
            "R_max": float(g["R_max"].iloc[0]),
            "n_symbols": n_sym,
            "n_pos_oos_sharpe": int(n_pos_sharpe),
            "n_pos_oos_return": int(n_pos_return),
            "n_dd_under_35pct": int(n_dd_ok),
            "mean_oos_sharpe": float(per_s["mean_sharpe"].mean()),
            "median_oos_sharpe": float(per_s["mean_sharpe"].median()),
            "mean_oos_return": float(per_s["mean_return"].mean()),
            "mean_oos_dd": float(per_s["mean_dd"].mean()),
            "robustness_score": float(robustness),
        })
    summary = pd.DataFrame(rows).sort_values("robustness_score", ascending=False)
    summary.to_csv(RESULTS / "walk_forward_summary.csv", index=False)
    print("\n=== COMPOSITE WALK-FORWARD ROBUSTNESS (sorted) ===")
    print(summary.head(15).to_string(index=False))

    # HEADLINE: split by risk filter
    if len(summary) > 0:
        best = summary.iloc[0]
        print(f"\nBest combo: {best['name']} (robust={best['robustness_score']:.3f}, "
              f"mean_oos_sharpe={best['mean_oos_sharpe']:+.3f}, "
              f"mean_oos_return={best['mean_oos_return']:+.3%})")

    # Risk-filter lift: average mean Sharpe across all combos WITH vs WITHOUT risk filter
    with_r = summary[summary["require_risk_filter"] == True]["mean_oos_sharpe"]
    no_r   = summary[summary["require_risk_filter"] == False]["mean_oos_sharpe"]
    print(f"\n=== RISK-FILTER LIFT (mean OOS Sharpe, average across combos) ===")
    print(f"  WITH risk filter:    {with_r.mean():+.3f}  (n={len(with_r)} combos)")
    print(f"  WITHOUT risk filter: {no_r.mean():+.3f}  (n={len(no_r)} combos)")
    print(f"  Δ = {with_r.mean() - no_r.mean():+.3f}")
    pd.DataFrame({
        "filter": ["with_risk_filter", "without_risk_filter"],
        "mean_oos_sharpe": [with_r.mean(), no_r.mean()],
        "median_oos_sharpe": [with_r.median(), no_r.median()],
        "n_combos": [len(with_r), len(no_r)],
    }).to_csv(RESULTS / "risk_filter_lift.csv", index=False)

    # Save winner metadata
    if len(summary) > 0:
        best = summary.iloc[0]
        with open(RESULTS / "winner.json", "w") as fh:
            json.dump({
                "name": best["name"],
                "require_risk_filter": bool(best["require_risk_filter"]),
                "T_enter": float(best["T_enter"]),
                "C_enter": float(best["C_enter"]),
                "R_max":   float(best["R_max"]),
                "robustness_score": float(best["robustness_score"]),
                "n_symbols": int(best["n_symbols"]),
                "n_pos_oos_sharpe": int(best["n_pos_oos_sharpe"]),
                "n_pos_oos_return": int(best["n_pos_oos_return"]),
                "n_dd_under_35pct": int(best["n_dd_under_35pct"]),
                "mean_oos_sharpe": float(best["mean_oos_sharpe"]),
                "median_oos_sharpe": float(best["median_oos_sharpe"]),
                "mean_oos_return": float(best["mean_oos_return"]),
                "mean_oos_dd": float(best["mean_oos_dd"]),
            }, fh, indent=2)

        # Per-symbol breakdown for the winner
        winner_rows = per_sym[per_sym["name"] == best["name"]].sort_values(
            "mean_sharpe", ascending=False)
        winner_rows.to_csv(RESULTS / "winner_per_symbol.csv", index=False)
        print(f"\n=== WINNER PER-SYMBOL ===")
        print(winner_rows.to_string(index=False))


if __name__ == "__main__":
    main()
