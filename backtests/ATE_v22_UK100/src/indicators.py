"""
ATE v2.2 — research Python port of the diagnostic score engines.

Source reference: ../../../pine/releases/ATE_v2.2.pine (diagnostic-only release).
The deterministic tests cover selected parity-sensitive semantics; this module
is not a substitute for exported TradingView parity fixtures.

We do NOT trade the score outputs directly here; we synthesise 6 long-only
strategies from them (trend / structure / momentum / vol / risk / confidence)
in `strategies.py`.

Indicator conventions (Wilder):
    ta.rma(src, n)  = SMA seed, then Wilder recursion
    ta.ema(src, n)  = src.ewm(span=n,   adjust=False).mean()
    ta.atr(n)       = RMA(true_range, n)
    ta.dmi(n, s)    = Wilder RMA smoothing of DI
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TAUS = 252  # bars/year for daily


# ─────────────────────────────────────────────────────────────────────────────
# CORE WILDERS / TR FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def rma(s: pd.Series, n: int) -> pd.Series:
    """Wilder's smoothing (RMA): same as TradingView's `ta.rma`."""
    if n <= 0:
        raise ValueError("RMA length must be positive")
    source = s.astype(float)
    seed = source.rolling(n, min_periods=n).mean()
    out = pd.Series(np.nan, index=source.index, dtype=float)
    previous = np.nan
    alpha = 1.0 / n
    for i, value in enumerate(source.to_numpy()):
        if np.isnan(previous):
            candidate = seed.iloc[i]
            if not pd.isna(candidate):
                previous = float(candidate)
        elif not np.isnan(value):
            previous = alpha * float(value) + (1.0 - alpha) * previous
        else:
            previous = np.nan
        out.iloc[i] = previous
    return out


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def wma(s: pd.Series, n: int) -> pd.Series:
    """Linear-weighted moving average. `pandas.Series.rolling(...).apply(...)`."""
    weights = np.arange(1, n + 1, dtype=float)
    return s.rolling(n, min_periods=n).apply(lambda w: (w * weights).sum() / weights.sum(), raw=True)


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr


def atr(df: pd.DataFrame, n: int) -> pd.Series:
    return rma(true_range(df), n)


# ─────────────────────────────────────────────────────────────────────────────
# MA CLUSTER (8 MAs, configurable type)
# ─────────────────────────────────────────────────────────────────────────────

def f_ma(src: pd.Series, length: int, ma_type: str) -> pd.Series:
    half = max(1, length // 2)
    sqrt_len = max(1, int(round(np.sqrt(length))))
    if ma_type == "SMA":
        return sma(src, length)
    if ma_type == "EMA":
        return ema(src, length)
    if ma_type == "WMA":
        return wma(src, length)
    if ma_type == "Hull":
        return wma(2 * wma(src, half) - wma(src, length), sqrt_len)
    raise ValueError(f"Unknown MA type: {ma_type}")


# ─────────────────────────────────────────────────────────────────────────────
# TREND SCORE ENGINE  (Pine lines 194-210)
# ─────────────────────────────────────────────────────────────────────────────

def trend_score(
    df: pd.DataFrame,
    *,
    ma_type: str = "EMA",
    f_lens=(4, 8, 13),
    m_lens=(21, 34, 55),
    s_lens=(50, 100, 200),
    slope_lookback: int = 3,
) -> pd.DataFrame:
    src = df["close"]
    f1, f2, f3 = (f_ma(src, n, ma_type) for n in f_lens)
    m1, m2, m3 = (f_ma(src, n, ma_type) for n in m_lens)
    s1, s2, s3 = (f_ma(src, n, ma_type) for n in s_lens)

    def up(v):
        return v.notna() & (v > v.shift(slope_lookback))

    def dn(v):
        return v.notna() & (v < v.shift(slope_lookback))

    price_score = (
        (src > s1).astype(float) * 5.0
        + (src > s2).astype(float) * 5.0
        + (src > s3).astype(float) * 10.0
    )
    slow_align = np.where(s1 > s2, np.where(s2 > s3, 30.0, 15.0), np.where(s2 > s3, 15.0, 0.0))
    slope_score = up(s1).astype(float) * 7.0 + up(s2).astype(float) * 7.0 + up(s3).astype(float) * 6.0
    fast_score = np.where(f1 > f2, np.where(f2 > f3, 15.0, 8.0), np.where(f2 > f3, 8.0, 0.0))
    medium_score = np.where(m1 > m2, np.where(m2 > m3, 15.0, 8.0), np.where(m2 > m3, 8.0, 0.0))

    trend = price_score + slow_align + slope_score + fast_score + medium_score
    return pd.DataFrame(
        {
            "trend_score": trend,
            "market_state": pd.cut(
                trend,
                bins=[-np.inf, 20, 40, 60, 80, np.inf],
                labels=["STRONG BEAR", "BEAR", "NEUTRAL", "BULL", "STRONG BULL"],
            ),
            "s1": s1, "s2": s2, "s3": s3,
        },
        index=df.index,
    )


# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURE SCORE  (lines 219-261)
# ─────────────────────────────────────────────────────────────────────────────

def _pivots(s: pd.Series, n: int):
    """Find pivot highs/lows using a centred window of length 2n+1 (n left + n right).

    NaN where no pivot; value at the pivot bar.
    """
    rolling_max = s.rolling(window=2 * n + 1, center=True, min_periods=2 * n + 1).max()
    rolling_min = s.rolling(window=2 * n + 1, center=True, min_periods=2 * n + 1).min()
    is_pivot_high = (s == rolling_max) & s.notna()
    is_pivot_low = (s == rolling_min) & s.notna()
    highs = s.where(is_pivot_high)
    lows = s.where(is_pivot_low)
    # Pine's `ta.pivothigh(high, n, n)` returns the pivot from `n` bars *ago*;
    # the offset=-pivotLen in plotshape re-aligns it. We replicate by shifting right.
    highs = highs.shift(n)
    lows = lows.shift(n)
    return highs, lows


def structure_score(
    df: pd.DataFrame,
    *,
    pivot_len: int = 5,
    enabled: bool = True,
) -> pd.DataFrame:
    swing_highs, swing_lows = _pivots(df["high"], pivot_len), _pivots(df["low"], pivot_len)
    sh, sl = swing_highs
    out = pd.DataFrame(index=df.index)
    # Pine updates prevHigh/prevLow only when a *new confirmed pivot* arrives.
    # A shifted forward-fill incorrectly makes prev==last one bar later and
    # erases the structure state between pivots.
    def confirmed_state(pivots: pd.Series) -> tuple[pd.Series, pd.Series]:
        last_values = []
        previous_values = []
        last = np.nan
        previous = np.nan
        for pivot in pivots.to_numpy():
            if not np.isnan(pivot):
                previous = last
                last = float(pivot)
            last_values.append(last)
            previous_values.append(previous)
        return (
            pd.Series(last_values, index=df.index, dtype=float),
            pd.Series(previous_values, index=df.index, dtype=float),
        )

    out["last_high"], out["prev_high"] = confirmed_state(sh)
    out["last_low"], out["prev_low"] = confirmed_state(sl)

    higher_high = out["last_high"].notna() & out["prev_high"].notna() & (out["last_high"] > out["prev_high"])
    lower_high = out["last_high"].notna() & out["prev_high"].notna() & (out["last_high"] < out["prev_high"])
    higher_low = out["last_low"].notna() & out["prev_low"].notna() & (out["last_low"] > out["prev_low"])
    lower_low = out["last_low"].notna() & out["prev_low"].notna() & (out["last_low"] < out["prev_low"])

    bull_structure = higher_high & higher_low
    bear_structure = lower_high & lower_low
    bos_bull = out["last_high"].notna() & (df["close"] > out["last_high"])
    bos_bear = out["last_low"].notna() & (df["close"] < out["last_low"])

    if not enabled:
        ss = pd.Series(50.0, index=df.index)
    else:
        bull_bos = (bull_structure & bos_bull).values
        bull_only = (bull_structure & ~bos_bull).values
        lean_bull = ((~bull_structure) & (higher_low | higher_high)).values
        bear_bos = (bear_structure & bos_bear).values
        bear_only = (bear_structure & ~bos_bear).values
        lean_bear = ((~bear_structure) & (lower_low | lower_high)).values
        a = np.full(len(df), 50.0)
        a = np.where(bear_bos, 0.0, a)
        a = np.where(bear_only, 20.0, a)
        a = np.where(lean_bear, 35.0, a)
        a = np.where(lean_bull, 65.0, a)
        a = np.where(bull_only, 80.0, a)
        a = np.where(bull_bos, 100.0, a)
        ss = pd.Series(a, index=df.index)

    out["structure_score"] = ss
    out["bos_bull"] = bos_bull
    out["bos_bear"] = bos_bear
    return out


# ─────────────────────────────────────────────────────────────────────────────
# MOMENTUM SCORE  (lines 268-304)
# ─────────────────────────────────────────────────────────────────────────────

def momentum_score(
    df: pd.DataFrame,
    *,
    rsi_len: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    adx_len: int = 14,
    adx_smooth: int = 14,
    enabled: bool = True,
) -> pd.DataFrame:
    close = df["close"]
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = rma(gain, rsi_len)
    avg_loss = rma(loss, rsi_len)
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    rsi = rsi.mask((avg_gain == 0) & (avg_loss > 0), 0.0)
    rsi_up = rsi > rsi.shift(1)

    ema_fast = ema(close, macd_fast)
    ema_slow = ema(close, macd_slow)
    macd_line = ema_fast - ema_slow
    macd_sig = ema(macd_line, macd_signal)
    macd_hist = macd_line - macd_sig
    macd_bull = macd_line > macd_sig
    macd_bear = macd_line < macd_sig
    macd_rising = macd_hist > macd_hist.shift(1)

    tr = true_range(df)
    up_move = (df["high"] - df["high"].shift(1)).clip(lower=0.0)
    down_move = (df["low"].shift(1) - df["low"]).clip(lower=0.0)
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm = pd.Series(plus_dm, index=df.index)
    minus_dm = pd.Series(minus_dm, index=df.index)
    atr_tr = rma(tr, adx_len)
    plus_di = 100 * rma(plus_dm, adx_len) / atr_tr.replace(0, np.nan)
    minus_di = 100 * rma(minus_dm, adx_len) / atr_tr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx_val = rma(dx.fillna(0), adx_smooth)
    adx_rising = adx_val > adx_val.shift(1)

    def rsi_score(v):
        cond1 = (v >= 55) & (v <= 70) & rsi_up
        cond2 = (v > 50) & (v < 80)
        cond3 = (v >= 45) & (v <= 55)
        return np.where(cond1, 35.0,
                np.where(cond2, 28.0,
                 np.where(cond3, 18.0,
                  np.where(v < 45, 8.0, 15.0))))

    def macd_score_fn():
        return np.where(macd_bull & (macd_hist > 0) & macd_rising, 35.0,
                np.where(macd_bull & (macd_hist > 0), 28.0,
                 np.where(macd_bull, 22.0,
                  np.where(macd_bear & (macd_hist < 0) & ~macd_rising, 5.0, 15.0))))

    def adx_score_fn():
        return np.where((adx_val >= 25) & (adx_val <= 45) & adx_rising, 30.0,
                np.where(adx_val >= 25, 24.0,
                 np.where(adx_val >= 18, 16.0, 8.0)))

    if enabled:
        m_score = rsi_score(rsi) + macd_score_fn() + adx_score_fn()
    else:
        m_score = pd.Series(50.0, index=df.index)

    return pd.DataFrame(
        {"momentum_score": m_score, "rsi": rsi, "adx": adx_val},
        index=df.index,
    )


# ─────────────────────────────────────────────────────────────────────────────
# VOLATILITY ENGINE (diagnostic)  (lines 312-378)
# ─────────────────────────────────────────────────────────────────────────────

def volatility_score(
    df: pd.DataFrame,
    *,
    atr_length: int = 14,
    atr_baseline_length: int = 100,
    bb_length: int = 20,
    bb_stddev: float = 2.0,
    bb_baseline_length: int = 100,
    shock_lookback: int = 20,
    shock_multiplier: float = 2.5,
    compression_threshold: float = 0.75,
    normal_upper_threshold: float = 1.25,
    elevated_threshold: float = 1.75,
    unstable_threshold: float = 2.50,
    vol_slope_lookback: int = 5,
    enabled: bool = True,
) -> pd.DataFrame:
    close = df["close"]
    vol_atr = atr(df, atr_length)
    vol_atr_pct = np.where(close == 0, np.nan, vol_atr / close * 100.0)
    vol_atr_pct = pd.Series(vol_atr_pct, index=df.index)
    vol_atr_baseline = sma(vol_atr_pct, atr_baseline_length)
    vol_atr_ratio = vol_atr_pct / vol_atr_baseline.replace(0, np.nan)

    bb_basis = sma(close, bb_length)
    bb_dev = bb_stddev * close.rolling(bb_length, min_periods=bb_length).std(ddof=0)
    bb_upper = bb_basis + bb_dev
    bb_lower = bb_basis - bb_dev
    bb_width_raw = (bb_upper - bb_lower) / bb_basis.replace(0, np.nan)
    bb_width_baseline = sma(bb_width_raw, bb_baseline_length)
    bb_width_ratio = bb_width_raw / bb_width_baseline.replace(0, np.nan)

    valid_atr = vol_atr_ratio.notna()
    valid_bb = bb_width_ratio.notna()
    combined = np.where(
        valid_atr & valid_bb, (vol_atr_ratio + bb_width_ratio) / 2.0,
        np.where(valid_atr, vol_atr_ratio,
                 np.where(valid_bb, bb_width_ratio, np.nan)),
    )
    combined = pd.Series(combined, index=df.index)
    slope = combined - combined.shift(vol_slope_lookback)

    tr_now = true_range(df)
    tr_baseline = sma(tr_now, shock_lookback)
    shock_flag = tr_baseline.notna() & (tr_baseline > 0) & (tr_now >= tr_baseline * shock_multiplier)

    state = pd.Series("unknown", index=df.index)
    if enabled and combined.notna().any():
        c = combined
        state = state.mask(shock_flag, "shock")
        state = state.mask(state.eq("unknown") & (c >= unstable_threshold), "unstable")
        state = state.mask(state.eq("unknown") & (c >= elevated_threshold), "elevated")
        state = state.mask(state.eq("unknown") & (c < compression_threshold), "compressed")
        state = state.mask(state.eq("unknown") & (c <= normal_upper_threshold), "normal")
        state = state.mask(state.eq("unknown") & (c > normal_upper_threshold) & (slope > 0), "expanding")
        # Anything still "unknown" but combined notna falls back to "normal"
        state = state.mask(state.eq("unknown") & c.notna(), "normal")

    score_map = {"normal": 85.0, "expanding": 70.0, "compressed": 55.0,
                 "elevated": 45.0, "unstable": 20.0, "shock": 10.0, "unknown": np.nan}
    v_score = state.map(score_map).astype(float)

    return pd.DataFrame(
        {
            "vol_score": v_score,
            "vol_state": state,
            "combined_ratio": combined,
        },
        index=df.index,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE SCORE  (lines 386-403)
# ─────────────────────────────────────────────────────────────────────────────

def confidence_score(
    trend: pd.Series,
    structure: pd.Series,
    momentum: pd.Series,
    *,
    trend_weight: float = 40.0,
    structure_weight: float = 30.0,
    momentum_weight: float = 30.0,
    enabled: bool = True,
) -> pd.Series:
    total = trend_weight + structure_weight + momentum_weight
    if total == 0 or not enabled:
        return pd.Series(50.0, index=trend.index)
    ntw = trend_weight / total
    nsw = structure_weight / total
    nmw = momentum_weight / total
    return trend * ntw + structure * nsw + momentum * nmw


# ─────────────────────────────────────────────────────────────────────────────
# RISK SCORE (diagnostic — directionally inverted: higher = more risk)  (lines 411-522)
# ─────────────────────────────────────────────────────────────────────────────

def risk_score(
    df: pd.DataFrame,
    vol: pd.DataFrame,
    struct: pd.DataFrame,
    conf: pd.Series,
    trend: pd.Series,
    momentum,
    *,
    risk_vol_elevated_score: float = 25.0,
    risk_extension_atr_low: float = 1.5,
    risk_extension_atr_high: float = 3.0,
    risk_swing_atr: float = 2.0,
    risk_confidence_high: float = 80.0,
    risk_confidence_low: float = 20.0,
    risk_smoothing_length: int = 3,
    enabled: bool = True,
    structure_enabled: bool = True,
) -> pd.DataFrame:
    close, high, low = df["close"], df["high"], df["low"]
    atr14 = atr(df, 14)

    # Vol component
    vs = vol["vol_score"]
    vol_shock = vol["vol_state"] == "shock"
    risk_vol_base = np.where(
        vs.isna(), 10.0,
        np.where(vs < risk_vol_elevated_score, 10.0,
         np.where(vs <= 75, 0.0,
          np.where(vs < 90, 5.0, 15.0))),
    )
    risk_vol_raw = np.clip(risk_vol_base + np.where(vol_shock, 20.0, 0.0), 0.0, 35.0)

    # Extension component
    bar_range_atr = (high - low) / atr14.replace(0, np.nan)
    def lin(v, lo, hi, ol, oh):
        return np.where(np.isnan(v) | (hi == lo), np.nan, ol + ((v - lo) / (hi - lo)) * (oh - ol))

    ext_raw = np.where(
        bar_range_atr.isna(), 10.0,
        np.where(bar_range_atr <= risk_extension_atr_low, 0.0,
         np.where(bar_range_atr <= risk_extension_atr_high,
                  lin(bar_range_atr, risk_extension_atr_low, risk_extension_atr_high, 0.0, 20.0),
                  30.0)),
    )
    risk_ext_raw = np.clip(ext_raw, 0.0, 30.0)

    # Structure component
    last_high = struct["last_high"]
    last_low = struct["last_low"]
    has_h = last_high.notna()
    has_l = last_low.notna()
    nearest = np.where(
        has_h & has_l, np.minimum(np.abs(close - last_high), np.abs(close - last_low)),
        np.where(has_h, np.abs(close - last_high),
         np.where(has_l, np.abs(close - last_low), np.nan)),
    )
    nearest = pd.Series(nearest, index=df.index)
    last_swing_atr = nearest / atr14.replace(0, np.nan)
    swing_mid = risk_swing_atr * 1.5
    swing_high = risk_swing_atr * 2.0
    struct_raw = np.where(
        not structure_enabled, 0.0,
        np.where(last_swing_atr.isna(), 10.0,
         np.where(last_swing_atr <= risk_swing_atr, 0.0,
          np.where(last_swing_atr <= swing_mid, lin(last_swing_atr, risk_swing_atr, swing_mid, 0.0, 12.0),
           np.where(last_swing_atr <= swing_high, lin(last_swing_atr, swing_mid, swing_high, 12.0, 18.0), 20.0)))),
    )
    risk_struct_raw = np.clip(struct_raw, 0.0, 20.0)

    # Conflict component: exact boolean shape of ta.cross(diff, 0), followed by
    # ta.barssince(cross) <= riskSmoothingLength. The comparison is inclusive,
    # so the current bar plus N prior bars are eligible.
    trend_s = trend if isinstance(trend, pd.Series) else _trend_series(df)
    diff = trend_s - pd.Series(momentum, index=df.index)
    crossed = (((diff > 0) & (diff.shift(1) <= 0)) |
               ((diff < 0) & (diff.shift(1) >= 0))).fillna(False)
    cross_recent = crossed.rolling(risk_smoothing_length + 1, min_periods=1).max().astype(bool)
    risk_conflict_base = np.where(conf >= risk_confidence_high, 10.0,
                          np.where(conf <= risk_confidence_low, 10.0, 0.0))
    risk_conflict_raw = np.clip(
        risk_conflict_base + np.where(cross_recent, 5.0, 0.0), 0.0, 15.0
    )

    total_raw = risk_vol_raw + risk_ext_raw + risk_struct_raw + risk_conflict_raw
    smoothed = sma(pd.Series(total_raw, index=df.index), risk_smoothing_length)
    insufficient = (
        (not enabled)
        | atr14.isna()
        | bar_range_atr.isna()
        | last_swing_atr.isna()
        | conf.isna()
    )
    rscore = pd.Series(np.clip(np.asarray(smoothed), 0.0, 100.0), index=df.index)
    rscore = rscore.mask(insufficient)

    return pd.DataFrame({"risk_score": rscore}, index=df.index)


def _trend_series(df: pd.DataFrame) -> pd.Series:
    """Re-derive a simple trend series in 0-100 used as the conflict basis only."""
    src = df["close"]
    s50 = sma(src, 50)
    s200 = sma(src, 200)
    base = np.where(src > s50, 50.0, 30.0) + np.where(s50 > s200, 30.0, 0.0) + np.where(src > s200, 20.0, 0.0)
    return pd.Series(base, index=df.index).fillna(50.0)


# ─────────────────────────────────────────────────────────────────────────────
# ALL-IN-ONE COMPUTE
# ─────────────────────────────────────────────────────────────────────────────

def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the full ATE v2.2 score suite and return as a single DataFrame."""
    t = trend_score(df)
    s = structure_score(df)
    m = momentum_score(df)
    v = volatility_score(df)
    c = confidence_score(t["trend_score"], s["structure_score"], m["momentum_score"])
    r = risk_score(df, v, s, c, t["trend_score"], m["momentum_score"])
    out = df.copy()
    out["trend_score"] = t["trend_score"]
    out["structure_score"] = s["structure_score"]
    out["momentum_score"] = m["momentum_score"]
    out["vol_score"] = v["vol_score"]
    out["risk_score"] = r["risk_score"]
    out["confidence_score"] = c
    return out
