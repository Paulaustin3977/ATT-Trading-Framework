"""Pure-Python mirror of the TrendEngine v0.2.0-spec-impl rule set.

This is the TrendEngine verification compute path. The Pine implementation
in `pine/development/ATE_Current.pine` (research-only, dev mirror) must
replicate these rules byte-for-byte; see
`specifications/ATE/TrendEngine.md` (v0.2.0-spec-impl) for the authoritative
spec text and `tests/fixtures/ATE_v2_2/` for the seeded fixtures.

Fixture schema (CSV with Date index):
    - Open, High, Low, Close

The compute path follows `specifications/ATE/TrendEngine.md` sections 5 and 6:
- bar-close-only logic,
- no repainting,
- deterministic given the same OHLC series and bar index,
- trendState in {UP, DOWN, RANGE, UNKNOWN},
- trendStrength in [0, 1],
- trendAge in [0, trendAgeMax].
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Approved inputs (constants) per TrendEngine v0.2.0-spec-impl specification.
PARAMS = {
    "trendEmaLen": 50,
    "trendSlopeLookback": 5,
    "trendSlopeMin": 0.001,
    "trendSwingLen": 5,
    "trendStructureBars": 3,
    "trendStrengthScale": 50.0,
    "trendAgeMax": 250,
}

ALLOWED_STATE = {"UP", "DOWN", "RANGE", "UNKNOWN"}
ALLOWED_DIAG_BOOLS = {"higherHigh", "higherLow", "lowerHigh", "lowerLow"}


def ema(series: pd.Series, length: int) -> pd.Series:
    """Standard EMA matching Pine `ta.ema` defaults."""
    return series.ewm(span=length, adjust=False, min_periods=length).mean()


def _swing_pivots(df: pd.DataFrame, pivot_len: int) -> tuple[pd.Series, pd.Series]:
    """Compute last two confirmed swing highs and swing lows.

    Matches the Pine `ta.pivothigh(high, pivotLen, pivotLen)` /
    `ta.pivotlow(low, pivotLen, pivotLen)` semantics with the active
    `pivotLen` default of 5.

    Returns (last_high, prev_high, last_low, prev_low) as four series aligned
    to the DataFrame index.
    """
    n = len(df)
    highs = df["High"].values
    lows = df["Low"].values
    last_high = np.full(n, np.nan)
    last_low = np.full(n, np.nan)
    prev_high = np.full(n, np.nan)
    prev_low = np.full(n, np.nan)

    last_h = np.nan
    last_l = np.nan
    prev_h = np.nan
    prev_l = np.nan

    for i in range(2 * pivot_len, n):
        window_h = highs[i - 2 * pivot_len : i + 1]
        window_l = lows[i - 2 * pivot_len : i + 1]
        center = i - pivot_len
        if highs[center] == np.max(window_h):
            prev_h = last_h
            last_h = highs[center]
        if lows[center] == np.min(window_l):
            prev_l = last_l
            last_l = lows[center]
        last_high[i] = last_h
        last_low[i] = last_l
        prev_high[i] = prev_h
        prev_low[i] = prev_l

    return (
        pd.Series(last_high, index=df.index),
        pd.Series(prev_high, index=df.index),
        pd.Series(last_low, index=df.index),
        pd.Series(prev_low, index=df.index),
    )


def calculate_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the TrendEngine rule set to an OHLC dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Must have columns ``Open``, ``High``, ``Low``, ``Close``.
        Index may be anything (DatetimeIndex is conventional for fixtures).

    Returns
    -------
    pd.DataFrame
        Copy of ``df`` with TrendEngine columns appended:
        ``trendState``, ``trendStrength``, ``trendAge``,
        ``trendEngineVersion``, plus diagnostic columns
        ``trendDiagEmaSlope``, ``trendDiagAgreement``, ``trendDiagHigherHigh``,
        ``trendDiagHigherLow``, ``trendDiagLowerHigh``, ``trendDiagLowerLow``,
        ``trendDiagStateConfirmBars``, ``trendDiagInsufficientData``,
        ``trendStateChanged`` (boolean helper used by the Pine mirror).
    """
    out = df.copy()
    n = len(out)

    p_ema_len = PARAMS["trendEmaLen"]
    p_lookback = PARAMS["trendSlopeLookback"]
    p_slope_min = PARAMS["trendSlopeMin"]
    p_swing_len = PARAMS["trendSwingLen"]
    p_confirm = PARAMS["trendStructureBars"]
    p_scale = PARAMS["trendStrengthScale"]
    p_age_max = PARAMS["trendAgeMax"]

    # Step 1: insufficient data check
    insufficient = np.zeros(n, dtype=bool)
    for i in range(n):
        insufficient[i] = i < (p_ema_len + p_lookback)
    out["trendDiagInsufficientData"] = insufficient

    # Step 2: EMA slope
    ema_series = ema(out["Close"], p_ema_len)
    ema_prior = ema_series.shift(p_lookback)
    slope = np.where(
        insufficient,
        0.0,
        np.where(
            ema_prior.isna() | (ema_prior == 0),
            0.0,
            (ema_series - ema_prior) / ema_prior.replace(0, np.nan),
        ),
    )
    slope = pd.Series(np.nan_to_num(slope, nan=0.0), index=out.index)
    out["trendDiagEmaSlope"] = slope

    # Step 3: slope classification
    slope_up = (slope > p_slope_min).values
    slope_down = (slope < -p_slope_min).values
    slope_flat = ~(slope_up | slope_down)

    # Step 4: structure classification via swing pivots
    last_high, prev_high, last_low, prev_low = _swing_pivots(out, p_swing_len)
    hh = (last_high > prev_high).fillna(False).values
    hl = (last_low > prev_low).fillna(False).values
    lh = (last_high < prev_high).fillna(False).values
    ll = (last_low < prev_low).fillna(False).values
    out["trendDiagHigherHigh"] = hh
    out["trendDiagHigherLow"] = hl
    out["trendDiagLowerHigh"] = lh
    out["trendDiagLowerLow"] = ll
    struct_up = hh & hl
    struct_down = lh & ll
    struct_flat = ~(struct_up | struct_down)

    # Step 5: agreement metric
    agreement = np.zeros(n, dtype=float)
    for i in range(n):
        if insufficient[i]:
            agreement[i] = 0.0
        elif slope_up[i] and struct_up[i]:
            agreement[i] = 1.0
        elif slope_down[i] and struct_down[i]:
            agreement[i] = 1.0
        elif slope_up[i] and struct_flat[i]:
            agreement[i] = 0.6
        elif slope_flat[i] and struct_up[i]:
            agreement[i] = 0.6
        elif slope_down[i] and struct_flat[i]:
            agreement[i] = 0.6
        elif slope_flat[i] and struct_down[i]:
            agreement[i] = 0.6
        elif slope_flat[i] and struct_flat[i]:
            agreement[i] = 0.5
        else:
            agreement[i] = 0.0  # slope and structure disagree
    out["trendDiagAgreement"] = agreement

    # Step 6: candidate state
    candidate_up = slope_up & struct_up
    candidate_down = slope_down & struct_down
    candidate_is_up_or_down = candidate_up | candidate_down

    candidate_state = np.where(
        candidate_up,
        "UP",
        np.where(candidate_down, "DOWN", "RANGE"),
    )

    # Step 7: state confirmation
    # State adoption is sequential across bars. We compute it bar by bar.
    state = np.full(n, "UNKNOWN", dtype=object)
    confirm_bars = np.zeros(n, dtype=int)
    hold_count = 0  # number of consecutive bars the candidate has held
    last_candidate = None
    for i in range(n):
        if insufficient[i]:
            state[i] = "UNKNOWN"
            confirm_bars[i] = 0
            hold_count = 0
            last_candidate = None
            continue
        cand = candidate_state[i]
        # Update hold count: how many consecutive bars has `cand` held?
        if cand == last_candidate:
            hold_count += 1
        else:
            hold_count = 1
        last_candidate = cand
        confirm_bars[i] = hold_count if candidate_is_up_or_down[i] else 0

        if state[i - 1] == "UNKNOWN" if i > 0 else True:
            # First non-UNKNOWN state adopted immediately.
            state[i] = cand
        elif cand != state[i - 1] and confirm_bars[i] >= p_confirm:
            state[i] = cand
        else:
            state[i] = state[i - 1] if i > 0 else "UNKNOWN"
    out["trendDiagStateConfirmBars"] = confirm_bars

    # Step 8: strength
    strength = np.full(n, np.nan, dtype=float)
    for i in range(n):
        if insufficient[i]:
            strength[i] = np.nan
        elif candidate_is_up_or_down[i]:
            strength[i] = min(1.0, max(0.0, agreement[i] * p_scale / 100.0))
        else:
            strength[i] = 0.0
    out["trendStrength"] = strength

    # Step 9: age tracking — bars since current state was adopted.
    state_changed = np.zeros(n, dtype=bool)
    for i in range(n):
        if i == 0:
            state_changed[i] = True  # first bar's state is "adopted"
        else:
            state_changed[i] = state[i] != state[i - 1]

    age = np.zeros(n, dtype=int)
    last_change_idx = -1
    for i in range(n):
        if insufficient[i]:
            age[i] = -1  # sentinel: na
        elif state[i] == "UNKNOWN":
            age[i] = 0
        elif state_changed[i]:
            age[i] = 0
            last_change_idx = i
        else:
            if last_change_idx < 0:
                age[i] = 0
            else:
                age[i] = min(p_age_max, i - last_change_idx)

    age_out = np.where(age == -1, np.nan, age).astype(float)
    out["trendAge"] = age_out
    out["trendStateChanged"] = state_changed

    # Step 10: state and version
    out["trendState"] = state
    out["trendEngineVersion"] = "0.2.0-spec-impl"

    return out


def summarise(out: pd.DataFrame) -> dict:
    """Return a small summary dict suitable for verifier fixtures."""
    s = out["trendState"]
    counts = {str(k): int(v) for k, v in s.value_counts().items()}
    return {
        "n": int(len(out)),
        "states": counts,
        "trend_strength_mean": float(out["trendStrength"].dropna().mean())
            if out["trendStrength"].notna().any() else None,
        "trend_age_max": int(out["trendAge"].dropna().max())
            if out["trendAge"].notna().any() else None,
        "insufficient_bars": int(out["trendDiagInsufficientData"].sum()),
    }


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    df = pd.read_csv(p, parse_dates=["Date"], index_col="Date")
    out = calculate_trend(df)
    print(
        out[
            [
                "trendState",
                "trendStrength",
                "trendAge",
                "trendDiagAgreement",
                "trendDiagStateConfirmBars",
                "trendDiagInsufficientData",
                "trendEngineVersion",
            ]
        ].head(20).to_string()
    )
    print()
    print("Summary:", summarise(out))