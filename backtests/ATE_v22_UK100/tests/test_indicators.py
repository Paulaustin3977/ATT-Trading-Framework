"""Deterministic smoke tests for the ATE v2.2 research indicator port."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.indicators import compute_all, ema, rma, structure_score, trend_score


def synthetic_ohlc(n: int = 320, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0.04, 0.8, n))
    open_ = close + rng.normal(0.0, 0.15, n)
    index = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) + rng.uniform(0.1, 1.0, n),
            "low": np.minimum(open_, close) - rng.uniform(0.1, 1.0, n),
            "close": close,
            "volume": rng.integers(10_000, 50_000, n),
        },
        index=index,
    )


def test_wilders_rma_uses_sma_seed_and_recursion():
    source = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    expected = pd.Series([np.nan, np.nan, 2.0, 8.0 / 3.0, 31.0 / 9.0])
    pd.testing.assert_series_equal(rma(source, 3), expected)


def test_ema_uses_span():
    source = pd.Series(np.sin(np.linspace(0, 10, 50)) + 1.0)
    expected = source.ewm(span=14, adjust=False).mean()
    np.testing.assert_allclose(ema(source, 14), expected, rtol=1e-9)


def test_compute_all_runs_and_scores_stay_in_range():
    scored = compute_all(synthetic_ohlc())
    for col in [
        "trend_score", "structure_score", "momentum_score",
        "vol_score", "risk_score", "confidence_score",
    ]:
        assert col in scored.columns, f"missing {col}"
        values = scored[col].dropna()
        assert len(values) > 100, f"{col} only has {len(values)} non-NaN values"
        assert values.between(0, 100).all(), f"{col} out of range"


def test_trend_score_has_a_non_degenerate_distribution():
    scores = trend_score(synthetic_ohlc())["trend_score"].dropna()
    assert scores.nunique() > 5
    assert scores.between(0, 100).all()


def test_structure_uses_confirmed_pivots_without_out_of_range_values():
    scored = structure_score(synthetic_ohlc(), pivot_len=5)
    assert scored["last_high"].notna().any()
    assert scored["last_low"].notna().any()
    assert scored["structure_score"].between(0, 100).all()
