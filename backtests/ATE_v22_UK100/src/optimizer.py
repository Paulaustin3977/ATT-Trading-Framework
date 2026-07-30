"""Segmented chronological grid for the 6 ATE v2.2 arms across the panel.

Each parameter combination is evaluated on each of N non-overlapping time
segments. There is no train-time parameter selection, so this is not a true
walk-forward or out-of-sample optimisation despite legacy output filenames and
column names. Each (symbol, combo) accumulates segment-level metrics. Rules (per
`references/optimizer-robustness-filters.md` from the trading-strategy-backtest
skill):

    - OOS Sharpe > 0 on ≥60% of symbols (loosened for daily + 4-window harness)
    - Max DD < 35% on ≥50% of symbols
    - Total OOS return > 0 on ≥50% of symbols
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import multiprocessing as mp
from typing import Optional

import numpy as np
import pandas as pd

from .indicators import compute_all
from .strategies import ScoreStrategy, all_strategies, SCORE_ARMS
from .engine import simulate
from .reporting import per_symbol_metrics


@dataclass
class Combo:
    arm: str
    long_thr: float
    exit_thr: float


@dataclass
class WindowResult:
    arm: str
    long_thr: float
    exit_thr: float
    symbol: str
    window: int
    n_trades: int
    total_return: float
    sharpe: float
    max_dd: float


def _build_grid() -> list:
    """3×3 coarse grid × 6 arms = 18 combos."""
    grid = []
    for arm in SCORE_ARMS:
        for lt in (50.0, 60.0, 70.0):
            for et in (30.0, 40.0, 50.0):
                if lt <= et:
                    continue
                grid.append(Combo(arm=arm, long_thr=lt, exit_thr=et))
    return grid


def _score_on_quantile(score: pd.Series, quantile: float) -> float:
    """Map a quantile (0-100) → score threshold (used for inverted risk/vol arms)."""
    return float(score.quantile(quantile / 100.0))


def _combo_strategy(arm: str, long_thr: float, exit_thr: float, **kw) -> ScoreStrategy:
    return ScoreStrategy(arm=arm, score_col={
        "trend_long": "trend_score",
        "structure_long": "structure_score",
        "momentum_long": "momentum_score",
        "confidence_long": "confidence_score",
        "vol_long": "vol_score",
        "risk_long": "risk_score",
    }[arm], long_thr=long_thr, exit_thr=exit_thr, **kw)


def _evaluate_one(args):
    """Worker: compute one (symbol, combo, window) result."""
    scored_slice, combo, symbol, window = args
    strat = _combo_strategy(combo.arm, combo.long_thr, combo.exit_thr)
    res = simulate(scored_slice, strat, symbol=symbol)
    if not res.trades:
        return asdict(WindowResult(combo.arm, combo.long_thr, combo.exit_thr,
                                    symbol, window, 0, 0.0, 0.0, 0.0))
    m = per_symbol_metrics(res, annual=252)
    return asdict(WindowResult(combo.arm, combo.long_thr, combo.exit_thr,
                                symbol, window, m["n_trades"],
                                m["total_return"], m["sharpe"], m["max_dd"]))


def _split_windows(n: int, n_windows: int = 4) -> list:
    """Balanced, non-overlapping segments that cover ``range(n)`` exactly."""
    if n_windows <= 0:
        raise ValueError("n_windows must be positive")
    boundaries = np.linspace(0, n, n_windows + 1, dtype=int)
    return [(int(boundaries[k]), int(boundaries[k + 1])) for k in range(n_windows)]


def run_walkforward(workers: int = 4):
    from .data import fetch_all

    results = []
    print("Loading + scoring all symbols...")
    raw = fetch_all()
    scored = {sym: compute_all(df) for sym, df in raw.items()}

    grid = _build_grid()
    tasks = []
    for combo in grid:
        for sym, s_df in scored.items():
            windows = _split_windows(len(s_df))
            for w_idx, (start, end) in enumerate(windows):
                slice_ = s_df.iloc[start:end]
                tasks.append((slice_, combo, sym, w_idx))
    print(f"Running {len(tasks)} (symbol, combo, window) tasks on {workers} workers...")

    with mp.Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_evaluate_one, tasks)):
            results.append(r)
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(tasks)} done")

    df = pd.DataFrame(results)
    return df


def aggregate_phase(df: pd.DataFrame, label: str) -> tuple:
    """Per-combo robustness score across the universe."""
    grouped = df.groupby(["arm", "long_thr", "exit_thr"])
    rows = []
    for (arm, lt, et), g in grouped:
        per_sym = g.groupby("symbol").agg(
            mean_sharpe=("sharpe", "mean"),
            mean_return=("total_return", "mean"),
            mean_dd=("max_dd", "mean"),
            n_trades=("n_trades", "sum"),
        )
        n_sym = len(per_sym)
        n_pos_sharpe = (per_sym["mean_sharpe"] > 0).sum()
        n_pos_return = (per_sym["mean_return"] > 0).sum()
        n_dd_ok = (per_sym["mean_dd"] > -0.35).sum()
        robustness = (
            0.4 * (n_pos_sharpe / n_sym) +
            0.4 * (n_pos_return / n_sym) +
            0.2 * (n_dd_ok / n_sym)
        )
        rows.append({
            "arm": arm, "long_thr": lt, "exit_thr": et,
            "n_symbols": n_sym,
            "n_pos_oos_sharpe": n_pos_sharpe,
            "n_pos_oos_return": n_pos_return,
            "n_dd_under_35pct": n_dd_ok,
            "mean_oos_sharpe": float(per_sym["mean_sharpe"].mean()),
            "median_oos_sharpe": float(per_sym["mean_sharpe"].median()),
            "mean_oos_return": float(per_sym["mean_return"].mean()),
            "mean_oos_dd": float(per_sym["mean_dd"].mean()),
            "total_n_trades": int(per_sym["n_trades"].sum()),
            "robustness_score": float(robustness),
            "phase": label,
        })
    return pd.DataFrame(rows).sort_values("robustness_score", ascending=False), df


def main():
    out_dir = Path(__file__).resolve().parent.parent / "results" / "optimization"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = run_walkforward(workers=4)
    df.to_csv(out_dir / "walk_forward_results.csv", index=False)
    summary, _ = aggregate_phase(df, "phase1_walkforward")
    summary.to_csv(out_dir / "walk_forward_summary.csv", index=False)
    print("\n=== WALK-FORWARD ROBUSTNESS (sorted by robustness_score) ===")
    print(summary.head(15).to_string(index=False))

    # Per-symbol breakdown for the top combo
    if len(summary) > 0:
        best = summary.iloc[0]
        best_key = (best["arm"], best["long_thr"], best["exit_thr"])
        per_sym = df[(df["arm"] == best_key[0]) & (df["long_thr"] == best_key[1]) & (df["exit_thr"] == best_key[2])]
        per_sym_avg = per_sym.groupby("symbol").agg(
            mean_sharpe=("sharpe", "mean"),
            mean_return=("total_return", "mean"),
            mean_dd=("max_dd", "mean"),
            n_trades=("n_trades", "sum"),
        ).sort_values("mean_sharpe", ascending=False)
        per_sym_avg.to_csv(out_dir / "winner_per_symbol.csv")
        print(f"\n=== WINNER PER-SYMBOL ({best_key[0]} long>{best_key[1]} / exit<{best_key[2]}) ===")
        print(per_sym_avg.to_string())

        with open(out_dir / "winner.json", "w") as fh:
            json.dump({
                "arm": best_key[0],
                "long_thr": float(best_key[1]),
                "exit_thr": float(best_key[2]),
                "robustness_score": float(best["robustness_score"]),
                "n_symbols": int(best["n_symbols"]),
                "n_pos_oos_sharpe": int(best["n_pos_oos_sharpe"]),
                "mean_oos_sharpe": float(best["mean_oos_sharpe"]),
                "mean_oos_return": float(best["mean_oos_return"]),
                "mean_oos_dd": float(best["mean_oos_dd"]),
            }, fh, indent=2)


if __name__ == "__main__":
    main()
