"""
Reporting metrics — per-symbol and aggregated.

Annualisation: 252 for daily. CAGR/Sharpe/Sortino parameterised by `annual`.
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .engine import Result


def _max_drawdown(equity: pd.Series) -> tuple:
    if equity.empty:
        return 0.0, 0
    peak = equity.cummax()
    dd = equity / peak - 1.0
    max_dd = float(dd.min())
    # Max DD duration (bars)
    underwater = (dd < 0).astype(int)
    grp = (underwater != underwater.shift()).cumsum()
    durations = underwater.groupby(grp).sum()
    return max_dd, int(durations.max()) if len(durations) else 0


def per_symbol_metrics(result: Result, *, annual: int = 252, initial: float = 10_000.0) -> dict:
    eq = result.equity_curve
    if eq.empty:
        return {"symbol": result.symbol, "arm": result.arm, "n_trades": 0,
                "total_return": 0.0, "sharpe": 0.0, "max_dd": 0.0,
                "max_dd_duration": 0, "win_rate": 0.0, "profit_factor": 0.0}
    rets = eq.pct_change().dropna()
    n_bars = len(eq)
    final = float(eq.iloc[-1])
    total_return = final / initial - 1
    years = max(n_bars / annual, 1 / annual)
    cagr = (final / initial) ** (1 / years) - 1 if final > 0 else -1.0
    sharpe = float(rets.mean() / rets.std() * np.sqrt(annual)) if rets.std() > 0 else 0.0
    # Sortino
    downside = rets[rets < 0]
    downside_std = downside.std() if len(downside) > 1 else 0.0
    sortino = float(rets.mean() / downside_std * np.sqrt(annual)) if downside_std > 0 else 0.0
    max_dd, max_dd_dur = _max_drawdown(eq)

    ts = result.trades
    n = len(ts)
    if n == 0:
        return {"symbol": result.symbol, "arm": result.arm, "n_trades": 0,
                "total_return": total_return, "cagr": cagr, "sharpe": sharpe,
                "sortino": sortino, "max_dd": max_dd, "max_dd_duration": max_dd_dur,
                "win_rate": 0.0, "profit_factor": 0.0,
                "avg_trade_pnl": 0.0, "expectancy": 0.0,
                "pct_time_in_market": 0.0, "best_trade": 0.0, "worst_trade": 0.0}
    wins = [t.pnl for t in ts if t.pnl > 0]
    losses = [t.pnl for t in ts if t.pnl < 0]
    win_rate = len(wins) / n if n else 0.0
    gross_wins = sum(wins) if wins else 0.0
    gross_losses = abs(sum(losses)) if losses else 0.0
    pf = gross_wins / gross_losses if gross_losses > 0 else np.inf
    avg_trade = float(np.mean([t.pnl for t in ts]))
    expectancy = avg_trade
    pct_in_market = sum(t.bars_in_trade for t in ts) / max(n_bars, 1)
    best = max(t.pnl for t in ts)
    worst = min(t.pnl for t in ts)
    return {
        "symbol": result.symbol,
        "arm": result.arm,
        "n_trades": n,
        "total_return": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd": max_dd,
        "max_dd_duration": max_dd_dur,
        "win_rate": win_rate,
        "profit_factor": pf,
        "avg_trade_pnl": avg_trade,
        "expectancy": expectancy,
        "pct_time_in_market": pct_in_market,
        "best_trade": best,
        "worst_trade": worst,
    }


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("arm").agg(
        mean_return=("total_return", "mean"),
        median_return=("total_return", "median"),
        std_return=("total_return", "std"),
        mean_sharpe=("sharpe", "mean"),
        median_sharpe=("sharpe", "median"),
        mean_max_dd=("max_dd", "mean"),
        median_max_dd=("max_dd", "median"),
        mean_n_trades=("n_trades", "mean"),
        mean_win_rate=("win_rate", "mean"),
        mean_pf=("profit_factor", "mean"),
        pct_profitable=("total_return", lambda x: (x > 0).mean()),
    ).reset_index()
    return grp.sort_values("mean_sharpe", ascending=False)
