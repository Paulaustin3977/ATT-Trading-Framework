"""
Iterative state-machine backtester.

Research execution assumptions (the referenced Pine release is an indicator,
not a strategy):
    process_orders_on_close = FALSE   (fill at next bar's open)
    commission is per-side (we model 0.05% / side on the fill notional)
    slippage is a small basis-points haircut applied to fill price
    pyramid = 0   (at most one position open at a time)
    qty sizing = risk% of equity / ATR(14)-based stop

The ATR trailing stop and risk-based sizing are synthetic research rules. They
are not present in or authorised by ATE v2.2.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

from .strategies import ScoreStrategy


# ─────────────────────────────────────────────────────────────────────────────
# TRADE LEDGER
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Trade:
    symbol: str
    arm: str
    entry_bar: int
    entry_date: pd.Timestamp
    entry_price: float
    exit_bar: int
    exit_date: pd.Timestamp
    exit_price: float
    qty: float
    pnl: float
    pnl_pct: float
    bars_in_trade: int
    exit_reason: str


@dataclass
class Result:
    symbol: str
    arm: str
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    score_at_entry: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))

    @property
    def final_equity(self) -> float:
        return float(self.equity_curve.iloc[-1]) if len(self.equity_curve) else 1.0


# ─────────────────────────────────────────────────────────────────────────────
# ATR HELPER (recomputed locally to avoid circular import)
# ─────────────────────────────────────────────────────────────────────────────

def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Wilder ATR with the same SMA seed used by Pine ``ta.atr``."""
    from .indicators import rma

    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return rma(tr, n)


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATE
# ─────────────────────────────────────────────────────────────────────────────

def simulate(
    df: pd.DataFrame,
    strategy: ScoreStrategy,
    *,
    symbol: str = "SYM",
    initial_equity: float = 10_000.0,
    risk_per_trade: float = 0.01,   # 1% of equity at risk per trade
    commission_bps: float = 5.0,    # 5 bps per side
    slippage_bps: float = 2.0,      # 2 bps applied to fill (buy pays extra, sell loses extra)
    trail_atr_mult: float = 2.0,    # initial stop = entry − 2×ATR
) -> Result:
    """Score-driven long-only backtest.

    Long entry on bar i+1 (open) when score[i] crosses above long_thr
    (we use threshold-cross only; otherwise we'd enter every bar it's above).
    Exit on bar i+1 (open) when score[i] drops below exit_thr OR when
    trailing stop is hit.
    """
    scores = df[strategy.score_col]
    opens = df["open"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)
    atr_values = _atr(df, 14)
    n = len(df)
    idx = df.index

    res = Result(symbol=symbol, arm=strategy.arm)
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

    # Signals are evaluated at a bar's close and queued for the next bar open.
    # This avoids reading open[i+1] while still accounting on bar i.
    pending_entry = False
    pending_exit = False
    pending_entry_atr = np.nan
    pending_entry_score = np.nan
    prev_above = False
    prev_below = False

    for i in range(n):
        # 1) Execute prior-close orders at this bar's open.
        if pending_exit and in_pos:
            exit_price = opens[i] * (1 - slippage_bps / 10_000)
            exit_fee = exit_price * qty * (commission_bps / 10_000)
            gross = (exit_price - entry_price) * qty
            pnl = gross - entry_fee - exit_fee
            realized_equity += gross - exit_fee
            res.trades.append(
                Trade(
                    symbol, strategy.arm, entry_bar, idx[entry_bar],
                    entry_price, i, idx[i], exit_price, qty, pnl,
                    (exit_price / entry_price - 1) - (commission_bps * 2 / 10_000),
                    bars_in_trade=i - entry_bar, exit_reason="signal_exit",
                )
            )
            in_pos = False

        if pending_entry and not in_pos:
            entry_open = opens[i]
            atr_v = pending_entry_atr
            if not pd.isna(atr_v) and atr_v > 0 and entry_open > 0:
                stop_pct = (trail_atr_mult * atr_v) / entry_open
                if 0 < stop_pct < 0.20:
                    risk_dollars = realized_equity * risk_per_trade
                    candidate_qty = risk_dollars / (entry_open * stop_pct)
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

        # 2) Intrabar protective stop. A gap through the stop fills at the open;
        # otherwise the stop itself is the observable trigger price. Never use
        # the completed bar's low as a synthetic fill.
        if in_pos and lows[i] <= stop_price:
            raw_exit = opens[i] if opens[i] <= stop_price else stop_price
            exit_price = raw_exit * (1 - slippage_bps / 10_000)
            exit_fee = exit_price * qty * (commission_bps / 10_000)
            gross = (exit_price - entry_price) * qty
            pnl = gross - entry_fee - exit_fee
            realized_equity += gross - exit_fee
            res.trades.append(
                Trade(
                    symbol, strategy.arm, entry_bar, idx[entry_bar],
                    entry_price, i, idx[i], exit_price, qty, pnl,
                    (exit_price / entry_price - 1) - (commission_bps * 2 / 10_000),
                    bars_in_trade=i - entry_bar, exit_reason="trailing_stop",
                )
            )
            in_pos = False

        # 3) Update a surviving position's stop for subsequent bars.
        if in_pos:
            trail_high = max(trail_high, highs[i])
            atr_v = atr_values.iloc[i]
            if not pd.isna(atr_v) and atr_v > 0:
                stop_price = max(stop_price, trail_high - trail_atr_mult * atr_v)

        # 4) Evaluate this bar's closing score and queue next-open action.
        s = scores.iloc[i]
        if pd.isna(s):
            prev_above = False
            prev_below = False
        else:
            above = bool(s > strategy.long_thr)
            below = bool(s < strategy.exit_thr)
            cross_above = above and not prev_above
            cross_below = below and not prev_below
            prev_above = above
            prev_below = below
            if i + 1 < n:
                if in_pos and cross_below:
                    pending_exit = True
                elif not in_pos and cross_above:
                    pending_entry = True
                    pending_entry_atr = atr_values.iloc[i]
                    pending_entry_score = float(s)

        mark = realized_equity
        if in_pos:
            mark += (closes[i] - entry_price) * qty
        equity_path.append(mark)

    res.equity_curve = pd.Series(equity_path, index=idx, dtype=float)
    res.score_at_entry = pd.Series(score_at_entry, dtype=float)
    return res
