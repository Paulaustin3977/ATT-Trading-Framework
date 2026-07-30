"""Deterministic Pine-parity and execution-accounting regression tests."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine import Result, Trade, simulate
from src.indicators import compute_all, risk_score, rma, structure_score
from src.optimizer import _split_windows
from src.reporting import per_symbol_metrics
from src.strategies import ScoreStrategy


def ohlc(n: int, *, price: float = 100.0) -> pd.DataFrame:
    index = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {
            "open": np.full(n, price),
            "high": np.full(n, price + 1.0),
            "low": np.full(n, price - 1.0),
            "close": np.full(n, price),
            "volume": np.full(n, 1_000.0),
        },
        index=index,
    )


def test_rma_uses_pine_sma_seed():
    source = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    expected = pd.Series([np.nan, np.nan, 2.0, 8.0 / 3.0, 31.0 / 9.0])
    pd.testing.assert_series_equal(rma(source, 3), expected)


def test_structure_preserves_previous_distinct_confirmed_pivot():
    df = ohlc(7)
    df["high"] = [1.0, 3.0, 1.0, 4.0, 1.0, 2.0, 1.0]
    df["low"] = [0.0, 1.0, 0.5, 1.0, 0.5, 1.0, 0.0]

    scored = structure_score(df, pivot_len=1)

    # Pivot highs at bars 1 and 3 are confirmed at bars 2 and 4. Pine's var
    # state keeps lastHigh=4 and prevHigh=3 after bar 4, including bar 5.
    assert scored.loc[df.index[5], "last_high"] == 4.0
    assert scored.loc[df.index[5], "prev_high"] == 3.0
    assert scored.loc[df.index[5], "structure_score"] >= 65.0


def test_indicator_prefix_is_unchanged_by_future_bars():
    rng = np.random.default_rng(7)
    n = 260
    close = 100 + rng.normal(0, 1, n).cumsum()
    df = ohlc(n)
    df["close"] = close
    df["open"] = close + rng.normal(0, 0.1, n)
    df["high"] = np.maximum(df["open"], close) + rng.uniform(0.1, 1.0, n)
    df["low"] = np.minimum(df["open"], close) - rng.uniform(0.1, 1.0, n)

    prefix = compute_all(df.iloc[:230])
    full = compute_all(df)
    cols = [
        "trend_score", "structure_score", "momentum_score",
        "vol_score", "risk_score", "confidence_score",
    ]
    pd.testing.assert_frame_equal(prefix[cols], full.loc[prefix.index, cols])


def test_risk_score_stays_nan_until_pine_inputs_are_available():
    # Pine riskDiagInsufficientData keeps riskScore=na until ATR and a confirmed
    # swing are available; it must not be silently converted to zero/calm.
    scored = compute_all(ohlc(10))
    assert scored["risk_score"].isna().all()


def test_risk_conflict_base_and_inclusive_barssince_match_pine():
    df = ohlc(25)
    vol = pd.DataFrame(
        {"vol_score": 50.0, "vol_state": "normal"}, index=df.index
    )
    struct = pd.DataFrame(
        {"last_high": 100.0, "last_low": 100.0}, index=df.index
    )
    conf = pd.Series(85.0, index=df.index)
    trend = pd.Series(40.0, index=df.index)
    momentum = pd.Series(50.0, index=df.index)
    trend.iloc[15:] = 60.0  # diff crosses zero between bars 14 and 15

    scored = risk_score(
        df, vol, struct, conf, trend, momentum, risk_smoothing_length=1
    )

    # Confidence contributes 10 throughout. ta.barssince(cross)<=1 adds five
    # on the crossing bar and one following bar, then expires.
    assert scored["risk_score"].iloc[14:18].tolist() == [10.0, 15.0, 15.0, 10.0]


def test_intrabar_stop_precedes_close_signal_next_open():
    df = ohlc(22)
    df["score"] = 0.0
    df.loc[df.index[15:17], "score"] = 70.0
    df.loc[df.index[17]:, "score"] = 30.0
    df.loc[df.index[17], "low"] = 95.0
    df.loc[df.index[18], "open"] = 200.0  # must not be used after bar-17 stop
    strat = ScoreStrategy("test", "score", 60.0, 40.0)

    result = simulate(df, strat, commission_bps=0.0, slippage_bps=0.0)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "trailing_stop"
    assert trade.exit_bar == 17
    assert trade.exit_date == df.index[17]
    assert trade.exit_price == pytest.approx(97.0)


def test_trade_ledger_uses_fill_dates_and_charges_both_commissions():
    df = ohlc(22)
    df["score"] = 0.0
    df.loc[df.index[15:17], "score"] = 70.0
    df.loc[df.index[17]:, "score"] = 30.0
    df.loc[df.index[18], "open"] = 110.0
    strat = ScoreStrategy("test", "score", 60.0, 40.0)

    result = simulate(
        df,
        strat,
        commission_bps=100.0,
        slippage_bps=0.0,
        trail_atr_mult=5.0,
    )

    trade = result.trades[0]
    assert trade.entry_bar == 16
    assert trade.entry_date == df.index[16]
    assert trade.exit_bar == 18
    assert trade.exit_date == df.index[18]
    expected = (110.0 - 100.0) * trade.qty - (100.0 + 110.0) * trade.qty * 0.01
    assert trade.pnl == pytest.approx(expected)


def test_final_equity_includes_last_bar_open_position_mark():
    df = ohlc(20)
    df["score"] = 0.0
    df.loc[df.index[15]:, "score"] = 70.0
    df.loc[df.index[19], "close"] = 110.0
    df.loc[df.index[19], "high"] = 111.0
    strat = ScoreStrategy("test", "score", 60.0, 40.0)

    result = simulate(
        df,
        strat,
        commission_bps=0.0,
        slippage_bps=0.0,
        trail_atr_mult=5.0,
    )

    assert result.final_equity > 10_000.0


def test_profit_factor_is_infinite_when_there_are_wins_and_no_losses():
    index = pd.date_range("2020-01-01", periods=2, freq="D")
    trade = Trade(
        symbol="SYM", arm="test", entry_bar=0,
        entry_date=cast(pd.Timestamp, pd.Timestamp("2020-01-01")),
        entry_price=100.0, exit_bar=1,
        exit_date=cast(pd.Timestamp, pd.Timestamp("2020-01-02")), exit_price=110.0,
        qty=1.0, pnl=10.0, pnl_pct=0.10, bars_in_trade=1,
        exit_reason="signal_exit",
    )
    result = Result(
        symbol="SYM", arm="test", trades=[trade],
        equity_curve=pd.Series([10_000.0, 10_010.0], index=index),
    )

    assert per_symbol_metrics(result)["profit_factor"] == np.inf


def test_segment_windows_cover_history_once_with_balanced_sizes():
    windows = _split_windows(103, n_windows=4)
    covered = [i for start, end in windows for i in range(start, end)]
    sizes = [end - start for start, end in windows]
    assert covered == list(range(103))
    assert max(sizes) - min(sizes) <= 1
