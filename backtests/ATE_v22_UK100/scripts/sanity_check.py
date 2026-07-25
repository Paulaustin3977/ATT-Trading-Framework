#!/usr/bin/env python3
"""Sanity check: buy-and-hold baseline for each symbol.

The cardinal verification from the trading-strategy-backtest skill:
the elegant strategy must beat buy-and-hold to be called an edge.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.data import fetch_all
from src.indicators import compute_all


def buy_and_hold(df: pd.DataFrame, *, initial: float = 10_000.0) -> dict:
    """Open the first bar; close the last bar. No sizing safety net."""
    p_open = df["open"].iloc[0]
    p_close = df["close"].iloc[-1]
    qty = initial / p_open
    final = qty * p_close
    rets = df["close"].pct_change().dropna()
    sharpe = float(rets.mean() / rets.std() * (252 ** 0.5)) if rets.std() else 0.0
    equity = [initial] + [qty * c for c in df["close"].values]
    # drop the first bar's "mark" since we hold from bar 1 → bar n, then final equity is last close
    equity = equity[1:]
    eq = pd.Series(equity, index=df.index)
    peak = eq.cummax()
    dd = (eq / peak - 1).min()
    return {
        "symbol": "BUY_HOLD",
        "arm": df.attrs.get("symbol", ""),
        "total_return": final / initial - 1,
        "sharpe": sharpe,
        "max_dd": float(dd),
        "n_trades": 1,
    }


def main():
    raw = fetch_all()
    rows = []
    for sym, df in raw.items():
        df.attrs["symbol"] = sym
        bh = buy_and_hold(df)
        bh["symbol"] = sym
        rows.append(bh)
    bh_df = pd.DataFrame(rows)
    print("\n=== BUY-AND-HOLD BASELINE (10y) ===")
    print(bh_df[["symbol", "total_return", "sharpe", "max_dd"]].to_string(index=False))
    print("\n  => If every strategy loses to this on the same symbol,")
    print("     there's no edge — the indicator is just adding noise.")


if __name__ == "__main__":
    main()
