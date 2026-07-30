"""
Iterative state-machine backtester for the COMPOSITE-GATE strategy.

Distinct from `engine.simulate` because the gate involves AND/OR across 3
scores simultaneously and uses the *risk* score as an inverted entry ceiling.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

from .composite import Composite, signal_long
from .engine import _atr, Trade, Result


def simulate_composite(
    df: pd.DataFrame,
    composite: Composite,
    *,
    symbol: str = "SYM",
    initial_equity: float = 10_000.0,
    risk_per_trade: float = 0.01,
    commission_bps: float = 5.0,
    slippage_bps: float = 2.0,
    trail_atr_mult: float = 2.0,
) -> Result:
    trend = df["trend_score"].to_numpy(dtype=float)
    conf = df["confidence_score"].to_numpy(dtype=float)
    risk = df["risk_score"].to_numpy(dtype=float)
    opens = df["open"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)
    atr_values = _atr(df, 14)
    n = len(df)
    idx = df.index

    res = Result(symbol=symbol, arm=composite.name)
    realized_equity = initial_equity
    equity_path: list[float] = []
    score_at_entry: list[float] = []

    in_pos = False
    entry_price = 0.0
    entry_fee = 0.0
    qty = 0.0
    entry_bar = 0
    stop_price = 0.0
    trail_high = 0.0
    pending_entry = False
    pending_exit = False
    pending_entry_atr = np.nan
    pending_entry_score = np.nan

    for i in range(n):
        if pending_exit and in_pos:
            exit_price = opens[i] * (1 - slippage_bps / 10_000)
            exit_fee = exit_price * qty * (commission_bps / 10_000)
            gross = (exit_price - entry_price) * qty
            pnl = gross - entry_fee - exit_fee
            realized_equity += gross - exit_fee
            res.trades.append(Trade(
                symbol, composite.name, entry_bar, idx[entry_bar],
                entry_price, i, idx[i], exit_price, qty, pnl,
                (exit_price / entry_price - 1) - (commission_bps * 2 / 10_000),
                bars_in_trade=i - entry_bar, exit_reason="signal_exit",
            ))
            in_pos = False

        if pending_entry and not in_pos:
            entry_open = opens[i]
            atr_v = pending_entry_atr
            if not pd.isna(atr_v) and atr_v > 0 and entry_open > 0:
                stop_pct = (trail_atr_mult * atr_v) / entry_open
                if 0 < stop_pct < 0.20:
                    candidate_qty = realized_equity * risk_per_trade / (entry_open * stop_pct)
                    if candidate_qty > 0:
                        qty = candidate_qty
                        entry_price = entry_open * (1 + slippage_bps / 10_000)
                        entry_fee = entry_price * qty * (commission_bps / 10_000)
                        realized_equity -= entry_fee
                        entry_bar = i
                        score_at_entry.append(float(pending_entry_score))
                        trail_high = entry_price
                        stop_price = entry_price - trail_atr_mult * atr_v
                        in_pos = True

        pending_entry = False
        pending_exit = False

        if in_pos and lows[i] <= stop_price:
            raw_exit = opens[i] if opens[i] <= stop_price else stop_price
            exit_price = raw_exit * (1 - slippage_bps / 10_000)
            exit_fee = exit_price * qty * (commission_bps / 10_000)
            gross = (exit_price - entry_price) * qty
            pnl = gross - entry_fee - exit_fee
            realized_equity += gross - exit_fee
            res.trades.append(Trade(
                symbol, composite.name, entry_bar, idx[entry_bar],
                entry_price, i, idx[i], exit_price, qty, pnl,
                (exit_price / entry_price - 1) - (commission_bps * 2 / 10_000),
                bars_in_trade=i - entry_bar, exit_reason="trailing_stop",
            ))
            in_pos = False

        if in_pos:
            trail_high = max(trail_high, highs[i])
            atr_v = atr_values.iloc[i]
            if not pd.isna(atr_v) and atr_v > 0:
                stop_price = max(stop_price, trail_high - trail_atr_mult * atr_v)

        valid = not (
            np.isnan(trend[i]) or np.isnan(conf[i]) or
            (composite.require_risk_filter and np.isnan(risk[i]))
        )
        if valid and i + 1 < n:
            sig = signal_long(composite, float(trend[i]), float(conf[i]), float(risk[i]))
            if in_pos and sig == "exit":
                pending_exit = True
            elif not in_pos and sig == "enter":
                pending_entry = True
                pending_entry_atr = atr_values.iloc[i]
                pending_entry_score = min(float(trend[i]), float(conf[i]))

        mark = realized_equity
        if in_pos:
            mark += (closes[i] - entry_price) * qty
        equity_path.append(mark)

    res.equity_curve = pd.Series(equity_path, index=idx, dtype=float)
    res.score_at_entry = pd.Series(score_at_entry, dtype=float)
    return res
