"""Pure-Python mirror of the approved RiskEngine v1.0 scoring rules.

This is the ATE v2.2 verification compute path. The actual Pine
implementation (not yet written) must replicate these rules byte-for-byte;
see specifications/ATE/RiskEngine.md for the authoritative spec text and
tests/fixtures/ATE_v2_2 for the seeded fixtures.

Fixture schema (CSV with Date index):
    - Open, High, Low, Close
    - volScore: numeric in 0..100 (downstream VolatilityEngine output).
    - volShockFlag: bool (downstream VolatilityEngine output).
    - confidenceScore: numeric in 0..100 (downstream ConfidenceEngine output).
    - trendScore: numeric in 0..100.
    - momentumScore: numeric in 0..100.

The compute path follows specifications/ATE/RiskEngine.md sections 7 and 8:
- four-component scoring with caps 35/30/20/15,
- state precedence `unknown > extreme > tense > elevated > normal > calm`,
- five-state model with allowed direction set.
"""
from __future__ import annotations

import hashlib
import json
import numpy as np
import pandas as pd

# Approved inputs (constants) per RiskEngine v1.0 specification.
PARAMS = {
    "volRiskElevatedScore": 25,
    "extensionAtrLow": 1.5,
    "extensionAtrHigh": 3.0,
    "swingRiskAtr": 2.0,
    "confidenceRiskHigh": 80,
    "confidenceRiskLow": 20,
    "riskSmoothingLength": 3,
}

ALLOWED_STATE = {"calm", "normal", "elevated", "tense", "extreme", "unknown"}
ALLOWED_DIRECTION = {"none", "elevated", "conflict", "stable", "indeterminate"}


def _safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.replace(0, np.nan)


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    pc = df["Close"].shift(1)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - pc).abs(),
        (df["Low"] - pc).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/length, adjust=False, min_periods=length).mean()


def last_swing_distance_atr(df: pd.DataFrame, atr_series: pd.Series) -> pd.Series:
    """Distance from current Close to last confirmed swing pivot, in ATR units.

    Uses a rolling pivot approximation: for each bar index i where i >= length
    (pivotLen), check whether high[i-length] is the maximum in a window
    [i-length*2..i]; similarly for low. Distance = |Close - pivot| / ATR.
    """
    length = 5  # pivotLen default in the active ATE engines
    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    atr_v = atr_series.values
    last_swing_high_dist = np.full(len(df), np.nan)
    last_swing_low_dist = np.full(len(df), np.nan)
    last_high = np.nan
    last_low = np.nan
    for i in range(2 * length, len(df)):
        window_h = highs[i-2*length:i+1]
        window_l = lows[i-2*length:i+1]
        center = i - length
        if highs[center] == np.max(window_h):
            last_high = highs[center]
        if lows[center] == np.min(window_l):
            last_low = lows[center]
        if not np.isnan(last_high) and atr_v[i] not in (0, np.nan):
            last_swing_high_dist[i] = abs(closes[i] - last_high) / atr_v[i]
        if not np.isnan(last_low) and atr_v[i] not in (0, np.nan):
            last_swing_low_dist[i] = abs(closes[i] - last_low) / atr_v[i]
    return pd.Series(
        np.fmin(np.nan_to_num(last_swing_high_dist, nan=np.inf),
                np.nan_to_num(last_swing_low_dist, nan=np.inf)),
        index=df.index,
    )


def component_vol_risk(volScore: pd.Series, volShockFlag: pd.Series) -> pd.Series:
    """Spec section 7.1."""
    p = pd.Series(0.0, index=volScore.index)
    p = p.where(~((volScore < 25) & volShockFlag), 25.0).fillna(25.0)
    # use element-wise construction
    n = len(volScore)
    out = np.zeros(n)
    vs = volScore.fillna(50).values
    sf = volShockFlag.fillna(False).astype(bool).values
    for i in range(n):
        score = vs[i]
        shock = sf[i]
        pts = 0.0
        if score < 25 and shock:
            pts = 25
        elif score < 25:
            pts = 10
        elif 25 <= score <= 75:
            pts = 0
        elif 75 < score < 90:
            pts = 5
        elif score >= 90:
            pts = 15
        if shock:
            pts += 20
        out[i] = min(35.0, pts)
    return pd.Series(out, index=volScore.index)


def component_ext_risk(df: pd.DataFrame, atr_series: pd.Series) -> pd.Series:
    """Spec section 7.2."""
    n = len(df)
    out = np.zeros(n)
    bar_range = (df["High"] - df["Low"]).values
    atr_v = atr_series.values
    low = PARAMS["extensionAtrLow"]
    high = PARAMS["extensionAtrHigh"]
    max_cap = 30.0
    for i in range(n):
        if atr_v[i] is None or np.isnan(atr_v[i]) or atr_v[i] == 0:
            out[i] = 0.0
            continue
        r = bar_range[i] / atr_v[i]
        if r <= low:
            pts = 0.0
        elif r > high:
            pts = max_cap
        else:
            pts = (r - low) / (high - low) * 20.0
        out[i] = min(max_cap, pts)
    return pd.Series(out, index=df.index)


def component_struct_risk(last_atr_dist: pd.Series) -> pd.Series:
    """Spec section 7.3."""
    n = len(last_atr_dist)
    out = np.zeros(n)
    swing = PARAMS["swingRiskAtr"]
    vals = last_atr_dist.fillna(0).values
    cap = 20.0
    for i in range(n):
        d = vals[i]
        if np.isnan(d) or d <= 2.0:
            pts = 0.0
        elif d <= 3.0:
            pts = (d - 2.0) / (3.0 - 2.0) * 12.0
        elif d <= swing:
            pts = 12.0 + (d - 3.0) / (swing - 3.0) * 6.0
        else:
            pts = cap
        out[i] = min(cap, pts)
    return pd.Series(out, index=last_atr_dist.index)


def component_conflict_risk(confidenceScore: pd.Series, trendScore: pd.Series, momentumScore: pd.Series) -> pd.Series:
    """Spec section 7.4."""
    n = len(confidenceScore)
    out = np.zeros(n)
    cs = confidenceScore.fillna(50).values
    ts = trendScore.fillna(50).values
    ms = momentumScore.fillna(50).values
    high_thr = PARAMS["confidenceRiskHigh"]
    low_thr = PARAMS["confidenceRiskLow"]
    cap = 15.0
    cross_window = PARAMS["riskSmoothingLength"]
    for i in range(n):
        pts = 0.0
        if cs[i] >= high_thr or cs[i] <= low_thr:
            pts = 10.0
        # disagreement flip over cross_window bars
        if i >= cross_window:
            # `ts` and `ms` are numpy arrays here; slice window.
            window_diff = ts[i-cross_window:i+1] - ms[i-cross_window:i+1]
            signs = np.sign(window_diff)
            if not np.any(signs == 0):
                for j in range(1, len(signs)):
                    if signs[j] != 0 and signs[j-1] != 0 and signs[j] != signs[j-1]:
                        pts += 5.0
                        break
        out[i] = min(cap, pts)
    return pd.Series(out, index=confidenceScore.index)


def determine_state_component(name: str, contribution: pd.Series) -> pd.Series:
    """Per spec section 7 each component has its own state taxonomy.

    For verifier simplicity we tag by contribution bands:
      volRiskComponentState:    [0,6) volLow, [6,16) volElev, [16,26) volTense, [26,35] volExtreme
      extRiskComponentState:    [0,6) extLow, [6,16) extNorm, [16,26) extStretch, [26,30] extExtreme
      structRiskComponentState: [0,5) structTight, [5,11) structNorm, [11,16) structStretch, [16,20] structRisk
      conflictRiskComponentState: [0,1) conflictNone, [1,6) conflictMild, [6,11) conflictElevated, [11,15] conflictHigh
    """
    def _bin(series: pd.Series, edges: list, names: list) -> pd.Series:
        out = pd.Series(["unknown"] * len(series), index=series.index)
        v = series.fillna(-1).values
        out_arr = np.array(out.values, dtype=object)
        for i in range(len(v)):
            x = v[i]
            if x is None or np.isnan(x):
                out_arr[i] = "unknown"
                continue
            placed = False
            for k in range(len(edges)):
                if x < edges[k]:
                    out_arr[i] = names[k]
                    placed = True
                    break
            if not placed:
                out_arr[i] = names[-1]
        return pd.Series(out_arr, index=series.index)

    if name == "vol":
        return _bin(contribution, [6, 16, 26], ["volLow", "volElev", "volTense", "volExtreme"])
    if name == "ext":
        return _bin(contribution, [6, 16, 26], ["extLow", "extNorm", "extStretch", "extExtreme"])
    if name == "struct":
        return _bin(contribution, [5, 11, 16], ["structTight", "structNorm", "structStretch", "structRisk"])
    if name == "conflict":
        return _bin(contribution, [1, 6, 11], ["conflictNone", "conflictMild", "conflictElevated", "conflictHigh"])
    raise ValueError(name)


def determine_state(total: pd.Series) -> pd.Series:
    """Spec 5.2 precedence: unknown > extreme > tense > elevated > normal > calm."""
    arr = []
    for x in total.values:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            arr.append("unknown"); continue
        if x >= 70:
            arr.append("extreme")
        elif x >= 50:
            arr.append("tense")
        elif x >= 30:
            arr.append("elevated")
        elif x >= 15:
            arr.append("normal")
        else:
            arr.append("calm")
    return pd.Series(arr, index=total.index)


def determine_direction(vol_contrib: pd.Series, conflict_contrib: pd.Series, total: pd.Series, volScore: pd.Series, volShockFlag: pd.Series) -> pd.Series:
    """Spec 5.4."""
    n = len(total)
    out = []
    for i in range(n):
        v = total.iat[i]
        if v is None or (isinstance(v, float) and np.isnan(v)):
            out.append("none"); continue
        if conflict_contrib.iat[i] >= 6 or (volShockFlag.iat[i] and volScore.iat[i] is not None and not (isinstance(volScore.iat[i], float) and np.isnan(volScore.iat[i])) and volScore.iat[i] < 25):
            out.append("conflict")
            continue
        if v >= 60:
            out.append("elevated")
        elif v <= 20:
            out.append("stable")
        else:
            out.append("indeterminate")
    return pd.Series(out, index=total.index)


def determine_reason(state: pd.Series) -> pd.Series:
    reasons = {
        "unknown": "Insufficient risk data",
        "calm": "All risk components low",
        "normal": "Risk components within expected range",
        "elevated": "At least one risk component elevated",
        "tense": "Multiple risk components elevated",
        "extreme": "Risk components at extreme or conflict dominant",
    }
    return state.map(reasons).fillna("Risk evidence present")


def calculate_risk(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    atr_series = atr(df)
    last_d = last_swing_distance_atr(df, atr_series)

    vol_c = component_vol_risk(out["volScore"], out["volShockFlag"])
    ext_c = component_ext_risk(out, atr_series)
    struct_c = component_struct_risk(last_d)
    conflict_c = component_conflict_risk(out["confidenceScore"], out["trendScore"], out["momentumScore"])

    out["volRiskContribution"] = vol_c
    out["extRiskContribution"] = ext_c
    out["structRiskContribution"] = struct_c
    out["conflictRiskContribution"] = conflict_c

    out["volRiskComponentState"] = determine_state_component("vol", vol_c)
    out["extRiskComponentState"] = determine_state_component("ext", ext_c)
    out["structRiskComponentState"] = determine_state_component("struct", struct_c)
    out["conflictRiskComponentState"] = determine_state_component("conflict", conflict_c)

    out["volRiskScoreRaw"] = vol_c
    out["extRiskScoreRaw"] = ext_c
    out["structRiskScoreRaw"] = struct_c
    out["conflictRiskScoreRaw"] = conflict_c

    total_raw = vol_c + ext_c + struct_c + conflict_c
    smoothed = total_raw.rolling(window=PARAMS["riskSmoothingLength"], min_periods=1).mean()
    out["smoothedRiskScore"] = smoothed
    out["RiskScore"] = smoothed.clip(0, 100)
    out["RiskState"] = determine_state(smoothed)
    out["RiskDirection"] = determine_direction(vol_c, conflict_c, smoothed, out["volScore"], out["volShockFlag"])
    out["RiskReason"] = determine_reason(out["RiskState"])
    out["RiskEngineVersion"] = "1.0.0-draft"
    return out


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    df = pd.read_csv(p, parse_dates=["Date"], index_col="Date")
    out = calculate_risk(df)
    print(out[["RiskScore", "RiskState", "RiskDirection", "RiskReason",
               "volRiskContribution", "extRiskContribution", "structRiskContribution",
               "conflictRiskContribution", "RiskEngineVersion"]].head().to_string())
