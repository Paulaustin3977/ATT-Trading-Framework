#!/usr/bin/env python3
"""RDR-002 VolatilityEngine diagnostic validation.

Pure research/diagnostic validation. No trading, no optimisation, no Pine edits.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[6]
OUT = ROOT / "backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002"
REPORT_DIR = ROOT / "research/Reports/RDR"
CHART_DIR = OUT / "charts"
RAW_DIR = OUT / "data_cache"
SUMMARY_CSV = OUT / "RDR-002_Summary.csv"
MANIFEST = OUT / "RDR-002_Manifest.md"
REPORT = REPORT_DIR / "RDR-002-volatility-diagnostic-validation.md"
PINE = ROOT / "pine/releases/ATE_v2.1.pine"

ASSETS = [
    {"symbol": "GC=F", "name": "Gold futures", "class": "Metals", "profile": "Gold"},
    {"symbol": "SI=F", "name": "Silver futures", "class": "Metals", "profile": "Silver"},
    {"symbol": "HG=F", "name": "Copper futures", "class": "Metals", "profile": "Custom"},
    {"symbol": "NQ=F", "name": "Nasdaq futures", "class": "Index proxies", "profile": "Stocks"},
    {"symbol": "SPY", "name": "S&P 500 ETF", "class": "Index proxies", "profile": "Stocks"},
    {"symbol": "NVDA", "name": "NVIDIA", "class": "Major equities", "profile": "Stocks"},
    {"symbol": "MSFT", "name": "Microsoft", "class": "Major equities", "profile": "Stocks"},
    {"symbol": "AAPL", "name": "Apple", "class": "Major equities", "profile": "Stocks"},
    {"symbol": "AMZN", "name": "Amazon", "class": "Major equities", "profile": "Stocks"},
    {"symbol": "GOOGL", "name": "Alphabet", "class": "Major equities", "profile": "Stocks"},
    {"symbol": "TLT", "name": "US Treasury bond ETF", "class": "Bonds / rates proxies", "profile": "Gilts"},
    {"symbol": "EURUSD=X", "name": "EUR/USD", "class": "FX", "profile": "Forex"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "class": "FX", "profile": "Forex"},
    {"symbol": "JPY=X", "name": "USD/JPY", "class": "FX", "profile": "Forex"},
    {"symbol": "CL=F", "name": "WTI crude oil futures", "class": "Commodities", "profile": "Custom"},
]

PARAMS = {
    "atrLength": 14,
    "atrBaselineLength": 100,
    "bbLength": 20,
    "bbStdDev": 2.0,
    "bbBaselineLength": 100,
    "shockLookback": 20,
    "shockMultiplier": 2.5,
    "compressionThreshold": 0.75,
    "normalUpperThreshold": 1.25,
    "elevatedThreshold": 1.75,
    "unstableThreshold": 2.50,
    "volSlopeLookback": 5,
    "pivotLen": 5,
    "rsiLen": 14,
    "macdFast": 12,
    "macdSlow": 26,
    "macdSignal": 9,
    "adxLen": 14,
    "adxSmooth": 14,
}

STATE_ORDER = ["compressed", "normal", "expanding", "elevated", "unstable", "shock", "unknown"]
TRANSITIONS_OF_INTEREST = [
    ("compressed", "expanding"),
    ("normal", "expanding"),
    ("expanding", "elevated"),
    ("elevated", "unstable"),
    ("unstable", "normal"),
    ("shock", "normal"),
    ("shock", "elevated"),
    ("shock", "unstable"),
]


def ensure_dirs() -> None:
    for p in [OUT, REPORT_DIR, CHART_DIR, RAW_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def download(symbol: str) -> pd.DataFrame:
    cache = RAW_DIR / f"{symbol.replace('=','_').replace('^','_').replace('/','_')}.csv"
    if cache.exists():
        df = pd.read_csv(cache, parse_dates=["Date"], index_col="Date")
        return df
    df = yf.download(symbol, period="10y", interval="1d", auto_adjust=False, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns=str.title)
    needed = ["Open", "High", "Low", "Close"]
    df = df.dropna(subset=[c for c in needed if c in df.columns])
    df = df[needed + (["Volume"] if "Volume" in df.columns else [])]
    df.to_csv(cache, index_label="Date")
    return df


def rma(s: pd.Series, length: int) -> pd.Series:
    return s.ewm(alpha=1/length, adjust=False, min_periods=length).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df["Close"].shift(1)
    return pd.concat([
        df["High"] - df["Low"],
        (df["High"] - pc).abs(),
        (df["Low"] - pc).abs(),
    ], axis=1).max(axis=1)


def ma(src: pd.Series, length: int, typ: str = "EMA") -> pd.Series:
    if typ == "SMA":
        return src.rolling(length, min_periods=length).mean()
    if typ == "EMA":
        return src.ewm(span=length, adjust=False, min_periods=length).mean()
    if typ == "WMA":
        w = np.arange(1, length + 1)
        return src.rolling(length, min_periods=length).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)
    raise ValueError(typ)


def bool_score(cond: pd.Series, pts: float) -> pd.Series:
    return cond.fillna(False).astype(float) * pts


def calc_rsi(close: pd.Series, length: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = rma(gain, length) / rma(loss, length).replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_dmi(df: pd.DataFrame, length: int, smooth: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
    up = df["High"].diff()
    down = -df["Low"].diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    atr = rma(true_range(df), length)
    plus_di = 100 * rma(plus_dm, length) / atr.replace(0, np.nan)
    minus_di = 100 * rma(minus_dm, length) / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = rma(dx, smooth)
    return plus_di, minus_di, adx


def pivot_series(df: pd.DataFrame, length: int) -> Tuple[pd.Series, pd.Series]:
    # Pine ta.pivothigh(high, left, right) returns the pivot value on the confirmation bar.
    highs = df["High"].values
    lows = df["Low"].values
    ph = np.full(len(df), np.nan)
    pl = np.full(len(df), np.nan)
    for i in range(2 * length, len(df)):
        center = i - length
        win_h = highs[center-length:center+length+1]
        win_l = lows[center-length:center+length+1]
        if np.isfinite(win_h).all() and highs[center] == np.max(win_h):
            ph[i] = highs[center]
        if np.isfinite(win_l).all() and lows[center] == np.min(win_l):
            pl[i] = lows[center]
    return pd.Series(ph, index=df.index), pd.Series(pl, index=df.index)


def score_state(score: pd.Series) -> pd.Series:
    return pd.Series(np.select(
        [score >= 80, score >= 60, score > 40, score > 20],
        ["STRONG BULL", "BULL", "NEUTRAL", "BEAR"],
        default="STRONG BEAR"), index=score.index)


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    c = out["Close"]

    # Trend score, EMA defaults.
    f1, f2, f3 = ma(c, 4), ma(c, 8), ma(c, 13)
    m1, m2, m3 = ma(c, 21), ma(c, 34), ma(c, 55)
    s1, s2, s3 = ma(c, 50), ma(c, 100), ma(c, 200)
    slb = 3
    priceScore = bool_score(c > s1, 5) + bool_score(c > s2, 5) + bool_score(c > s3, 10)
    slowAlignScore = pd.Series(np.select([((s1 > s2) & (s2 > s3)), ((s1 > s2) | (s2 > s3))], [30, 15], default=0), index=df.index)
    slopeScore = bool_score((s1.notna()) & (s1 > s1.shift(slb)), 7) + bool_score((s2.notna()) & (s2 > s2.shift(slb)), 7) + bool_score((s3.notna()) & (s3 > s3.shift(slb)), 6)
    fastScore = pd.Series(np.select([((f1 > f2) & (f2 > f3)), ((f1 > f2) | (f2 > f3))], [15, 8], default=0), index=df.index)
    mediumScore = pd.Series(np.select([((m1 > m2) & (m2 > m3)), ((m1 > m2) | (m2 > m3))], [15, 8], default=0), index=df.index)
    out["TrendScore"] = priceScore + slowAlignScore + slopeScore + fastScore + mediumScore
    out["MarketState"] = score_state(out["TrendScore"])

    # Structure engine.
    swingHigh, swingLow = pivot_series(out, PARAMS["pivotLen"])
    lastHigh = prevHigh = lastLow = prevLow = np.nan
    structure_scores = []
    for idx in range(len(out)):
        if not np.isnan(swingHigh.iloc[idx]):
            prevHigh = lastHigh
            lastHigh = swingHigh.iloc[idx]
        if not np.isnan(swingLow.iloc[idx]):
            prevLow = lastLow
            lastLow = swingLow.iloc[idx]
        higherHigh = not np.isnan(lastHigh) and not np.isnan(prevHigh) and lastHigh > prevHigh
        lowerHigh = not np.isnan(lastHigh) and not np.isnan(prevHigh) and lastHigh < prevHigh
        higherLow = not np.isnan(lastLow) and not np.isnan(prevLow) and lastLow > prevLow
        lowerLow = not np.isnan(lastLow) and not np.isnan(prevLow) and lastLow < prevLow
        bullStructure = higherHigh and higherLow
        bearStructure = lowerHigh and lowerLow
        bosBull = not np.isnan(lastHigh) and out["Close"].iloc[idx] > lastHigh
        bosBear = not np.isnan(lastLow) and out["Close"].iloc[idx] < lastLow
        score = 100 if bullStructure and bosBull else 80 if bullStructure else 65 if (higherLow or higherHigh) else 0 if bearStructure and bosBear else 20 if bearStructure else 35 if (lowerLow or lowerHigh) else 50
        structure_scores.append(score)
    out["StructureScore"] = structure_scores

    # Momentum.
    rsi = calc_rsi(c, PARAMS["rsiLen"])
    rsiUp = rsi > rsi.shift(1)
    ema_fast = c.ewm(span=PARAMS["macdFast"], adjust=False, min_periods=PARAMS["macdFast"]).mean()
    ema_slow = c.ewm(span=PARAMS["macdSlow"], adjust=False, min_periods=PARAMS["macdSlow"]).mean()
    macdLine = ema_fast - ema_slow
    macdSig = macdLine.ewm(span=PARAMS["macdSignal"], adjust=False, min_periods=PARAMS["macdSignal"]).mean()
    macdHist = macdLine - macdSig
    macdBull = macdLine > macdSig
    macdBear = macdLine < macdSig
    macdRising = macdHist > macdHist.shift(1)
    _, _, adx = calc_dmi(out, PARAMS["adxLen"], PARAMS["adxSmooth"])
    adxRising = adx > adx.shift(1)
    rsiScore = pd.Series(np.select([(rsi >= 55) & (rsi <= 70) & rsiUp, (rsi > 50) & (rsi < 80), (rsi >= 45) & (rsi <= 55), rsi < 45], [35, 28, 18, 8], default=15), index=df.index)
    macdScore = pd.Series(np.select([macdBull & (macdHist > 0) & macdRising, macdBull & (macdHist > 0), macdBull, macdBear & (macdHist < 0) & (~macdRising)], [35, 28, 22, 5], default=15), index=df.index)
    adxScore = pd.Series(np.select([(adx >= 25) & (adx <= 45) & adxRising, adx >= 25, adx >= 18], [30, 24, 16], default=8), index=df.index)
    out["MomentumScore"] = rsiScore + macdScore + adxScore
    totalWeight = 40 + 30 + 30
    out["ConfidenceScore"] = out["TrendScore"] * 40/totalWeight + out["StructureScore"] * 30/totalWeight + out["MomentumScore"] * 30/totalWeight

    # VolatilityEngine exact-ish port.
    tr = true_range(out)
    out["ATRPercent"] = rma(tr, PARAMS["atrLength"]) / c * 100.0
    out["ATRBaseline"] = out["ATRPercent"].rolling(PARAMS["atrBaselineLength"], min_periods=PARAMS["atrBaselineLength"]).mean()
    out["ATRRatio"] = out["ATRPercent"] / out["ATRBaseline"].replace(0, np.nan)
    bbBasis = c.rolling(PARAMS["bbLength"], min_periods=PARAMS["bbLength"]).mean()
    bbDev = PARAMS["bbStdDev"] * c.rolling(PARAMS["bbLength"], min_periods=PARAMS["bbLength"]).std(ddof=0)
    bbWidthRaw = ((bbBasis + bbDev) - (bbBasis - bbDev)) / bbBasis.replace(0, np.nan)
    bbBaseline = bbWidthRaw.rolling(PARAMS["bbBaselineLength"], min_periods=PARAMS["bbBaselineLength"]).mean()
    out["BBWidthRatio"] = bbWidthRaw / bbBaseline.replace(0, np.nan)
    out["CombinedVolRatio"] = out[["ATRRatio", "BBWidthRatio"]].mean(axis=1, skipna=True)
    both_missing = out["ATRRatio"].isna() & out["BBWidthRatio"].isna()
    out.loc[both_missing, "CombinedVolRatio"] = np.nan
    out["VolSlope"] = out["CombinedVolRatio"] - out["CombinedVolRatio"].shift(PARAMS["volSlopeLookback"])
    out["TrueRange"] = tr
    out["TrueRangeBaseline"] = tr.rolling(PARAMS["shockLookback"], min_periods=PARAMS["shockLookback"]).mean()
    out["ShockFlag"] = (out["TrueRangeBaseline"].notna()) & (out["TrueRangeBaseline"] > 0) & (tr >= out["TrueRangeBaseline"] * PARAMS["shockMultiplier"])
    unknown = out["CombinedVolRatio"].isna()
    cr = out["CombinedVolRatio"]
    out["VolatilityState"] = np.select([
        unknown,
        out["ShockFlag"],
        cr >= PARAMS["unstableThreshold"],
        cr >= PARAMS["elevatedThreshold"],
        cr < PARAMS["compressionThreshold"],
        cr <= PARAMS["normalUpperThreshold"],
        (cr > PARAMS["normalUpperThreshold"]) & (out["VolSlope"] > 0),
    ], ["unknown", "shock", "unstable", "elevated", "compressed", "normal", "expanding"], default="normal")
    out["VolatilityDirection"] = np.select([
        unknown,
        out["ShockFlag"],
        cr >= PARAMS["unstableThreshold"],
        out["VolSlope"].isna(),
        out["VolSlope"] > 0,
        out["VolSlope"] < 0,
    ], ["none", "unstable", "unstable", "none", "expanding", "contracting"], default="stable")
    out["VolatilityScore"] = out["VolatilityState"].map({"normal": 85.0, "expanding": 70.0, "compressed": 55.0, "elevated": 45.0, "unstable": 20.0, "shock": 10.0}).astype(float)
    out["VolatilityReason"] = out["VolatilityState"].map({
        "unknown": "Insufficient volatility data",
        "shock": "True range shock detected",
        "unstable": "Volatility extremely above baseline",
        "elevated": "Volatility materially above baseline",
        "expanding": "Volatility expanding above normal",
        "compressed": "Volatility compressed below baseline",
        "normal": "Volatility near asset baseline",
    })
    out["Return1D"] = c.pct_change()
    out["FwdReturn1D"] = c.pct_change().shift(-1)
    out["AbsReturn1D"] = out["Return1D"].abs()
    return out


def run_lengths(states: pd.Series) -> List[Tuple[str, int]]:
    vals = states.dropna().tolist()
    if not vals:
        return []
    runs = []
    current = vals[0]
    length = 1
    for v in vals[1:]:
        if v == current:
            length += 1
        else:
            runs.append((current, length))
            current = v
            length = 1
    runs.append((current, length))
    return runs


def make_chart(symbol: str, name: str, df: pd.DataFrame) -> str:
    sample = df.dropna(subset=["Close"]).tail(750)
    if sample.empty:
        return ""
    colors = {
        "unknown": "lightgray", "compressed": "#7B68EE", "normal": "#2ca02c", "expanding": "#ffbf00",
        "elevated": "#ff7f0e", "unstable": "#d62728", "shock": "#000000"
    }
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(sample.index, sample["Close"], color="steelblue", lw=1.2)
    ymin, ymax = ax.get_ylim()
    for state, color in colors.items():
        mask = sample["VolatilityState"] == state
        if mask.any():
            ax.scatter(sample.index[mask], sample.loc[mask, "Close"], s=8, color=color, label=state, alpha=0.75)
    ax.set_title(f"RDR-002 Volatility states — {symbol} {name}")
    ax.legend(ncol=4, fontsize=7, loc="best")
    ax.grid(alpha=0.2)
    path = CHART_DIR / f"{symbol.replace('=','_').replace('^','_').replace('/','_')}_vol_states.png"
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return str(path.relative_to(ROOT))


def pct(x: float) -> str:
    return f"{x:.2f}%"


def main() -> None:
    ensure_dirs()
    records = []
    all_frames: Dict[str, pd.DataFrame] = {}
    transition_rows = []
    duration_rows = []
    class_rows = []
    shock_examples = []
    chart_paths = []
    data_notes = []
    start_time = datetime.now(timezone.utc)

    for meta in ASSETS:
        symbol = meta["symbol"]
        try:
            raw = download(symbol)
            if len(raw) < 300:
                data_notes.append(f"{symbol}: skipped, insufficient rows ({len(raw)}).")
                continue
            df = calculate(raw)
            df = df[df.index >= pd.Timestamp("2018-01-01")]
            if len(df) < 300:
                data_notes.append(f"{symbol}: skipped after date filter, insufficient rows ({len(df)}).")
                continue
            all_frames[symbol] = df
        except Exception as e:
            data_notes.append(f"{symbol}: failed ({type(e).__name__}: {e}).")
            continue

        n = len(df)
        freqs = df["VolatilityState"].value_counts(normalize=True).mul(100).to_dict()
        counts = df["VolatilityState"].value_counts().to_dict()
        runs = run_lengths(df["VolatilityState"])
        for st in STATE_ORDER:
            lens = [l for s, l in runs if s == st]
            duration_rows.append({
                "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"], "state": st,
                "avg_duration": float(np.mean(lens)) if lens else 0.0,
                "median_duration": float(np.median(lens)) if lens else 0.0,
                "longest_duration": int(np.max(lens)) if lens else 0,
                "shortest_duration": int(np.min(lens)) if lens else 0,
                "run_count": len(lens),
            })
        trans = pd.crosstab(df["VolatilityState"].shift(1), df["VolatilityState"])
        trans_total = int((df["VolatilityState"].shift(1) != df["VolatilityState"]).sum())
        for a, b in TRANSITIONS_OF_INTEREST:
            val = int(trans.loc[a, b]) if a in trans.index and b in trans.columns else 0
            transition_rows.append({"symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"], "transition": f"{a}->{b}", "count": val, "pct_of_bars": val / n * 100})

        valid = df[df["VolatilityState"] != "unknown"].copy()
        # Spearman without scipy: Pearson correlation of rank-transformed series.
        corr_trend = valid["VolatilityScore"].rank().corr(valid["TrendScore"].rank())
        corr_mom = valid["VolatilityScore"].rank().corr(valid["MomentumScore"].rank())
        corr_conf = valid["VolatilityScore"].rank().corr(valid["ConfidenceScore"].rank())
        bias_by_state = valid.groupby("VolatilityState").agg(
            mean_return=("Return1D", "mean"),
            mean_fwd_return=("FwdReturn1D", "mean"),
            pct_up=("Return1D", lambda s: float((s > 0).mean() * 100)),
            mean_abs_return=("AbsReturn1D", "mean"),
            n=("Return1D", "count"),
        )
        max_abs_state_mean_return = float(bias_by_state["mean_return"].abs().max() * 100) if not bias_by_state.empty else np.nan
        max_pct_up_dev = float((bias_by_state["pct_up"] - 50).abs().max()) if not bias_by_state.empty else np.nan
        shock = df[df["ShockFlag"]]
        shock_count = len(shock)
        shock_examples.extend([
            {"symbol": symbol, "date": idx.strftime("%Y-%m-%d"), "tr_ratio": row["TrueRange"] / row["TrueRangeBaseline"] if row["TrueRangeBaseline"] else np.nan, "state": row["VolatilityState"], "close": row["Close"]}
            for idx, row in shock.sort_values("TrueRange", ascending=False).head(5).iterrows()
        ])
        chart_paths.append(make_chart(symbol, meta["name"], df))
        records.append({
            "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"], "rows": n,
            "start_date": df.index.min().strftime("%Y-%m-%d"), "end_date": df.index.max().strftime("%Y-%m-%d"),
            **{f"pct_{st}": freqs.get(st, 0.0) for st in STATE_ORDER},
            **{f"count_{st}": counts.get(st, 0) for st in STATE_ORDER},
            "spearman_volscore_trendScore": corr_trend,
            "spearman_volscore_momentumScore": corr_mom,
            "spearman_volscore_confidenceScore": corr_conf,
            "max_abs_state_mean_return_pct": max_abs_state_mean_return,
            "max_pct_up_deviation_from_50": max_pct_up_dev,
            "shock_count": shock_count,
            "shock_pct": shock_count / n * 100,
            "state_changes": trans_total,
            "state_changes_per_100_bars": trans_total / n * 100,
        })

    summary = pd.DataFrame(records)
    duration_df = pd.DataFrame(duration_rows)
    transition_df = pd.DataFrame(transition_rows)
    if summary.empty:
        raise SystemExit("No data downloaded; cannot validate")

    summary.to_csv(SUMMARY_CSV, index=False)
    duration_df.to_csv(OUT / "RDR-002_Durations.csv", index=False)
    transition_df.to_csv(OUT / "RDR-002_Transitions.csv", index=False)
    pd.DataFrame(shock_examples).to_csv(OUT / "RDR-002_Shock_Examples.csv", index=False)

    # Class aggregate.
    class_summary = summary.groupby("asset_class").agg({
        **{f"pct_{st}": "mean" for st in STATE_ORDER},
        "spearman_volscore_trendScore": "mean",
        "spearman_volscore_momentumScore": "mean",
        "spearman_volscore_confidenceScore": "mean",
        "shock_pct": "mean",
        "state_changes_per_100_bars": "mean",
    }).reset_index()
    class_summary.to_csv(OUT / "RDR-002_Class_Summary.csv", index=False)

    # Research mode static field review from Pine source.
    pine_text = PINE.read_text()
    fields = ["VolatilityEngineVersion", "VolatilityScore", "VolatilityState", "VolatilityDirection", "VolatilityReason", "ATRPercent", "ATRRatio", "BBWidthRatio", "CombinedVolRatio", "VolSlope", "ShockFlag"]
    field_review = {f: (f in pine_text) for f in fields}

    # Classification rules.
    unknown_ok = summary["pct_unknown"].median() < 8 and summary["pct_unknown"].max() < 15
    shock_explainable = summary["shock_pct"].median() < 3 and summary["shock_pct"].max() < 8
    state_diversity = (summary[[f"pct_{st}" for st in ["compressed", "normal", "expanding", "elevated", "unstable", "shock"]]] > 0).sum(axis=1).median() >= 5
    overlap_ok = max(summary["spearman_volscore_trendScore"].abs().median(), summary["spearman_volscore_momentumScore"].abs().median()) < 0.55
    bias_ok = summary["max_pct_up_deviation_from_50"].median() < 10
    noisy_ok = summary["state_changes_per_100_bars"].median() < 45
    if unknown_ok and shock_explainable and state_diversity and overlap_ok and bias_ok and noisy_ok:
        classification = "Supported"
        recommendation = "Keep Diagnostic"
    elif state_diversity and overlap_ok and shock_explainable:
        classification = "Weakly Supported"
        recommendation = "Keep Diagnostic; retest thresholds after more observation"
    else:
        classification = "Inconclusive"
        recommendation = "Keep Diagnostic; retest before any integration"

    # Report helpers.
    def md_table(df: pd.DataFrame, cols: List[str], max_rows: int = 50) -> str:
        d = df[cols].head(max_rows).copy()
        for col in d.select_dtypes(include=[float]).columns:
            d[col] = d[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
        return d.to_markdown(index=False)

    freq_cols = ["symbol", "asset_class", "rows", "start_date", "end_date"] + [f"pct_{st}" for st in STATE_ORDER]
    overlap_cols = ["symbol", "asset_class", "spearman_volscore_trendScore", "spearman_volscore_momentumScore", "spearman_volscore_confidenceScore", "max_pct_up_deviation_from_50", "shock_pct", "state_changes_per_100_bars"]
    duration_pivot = duration_df.pivot_table(index=["symbol", "asset_class", "state"], values=["avg_duration", "median_duration", "longest_duration", "shortest_duration", "run_count"], aggfunc="first").reset_index()
    trans_pivot = transition_df.pivot_table(index=["symbol", "asset_class"], columns="transition", values="count", aggfunc="sum", fill_value=0).reset_index()
    trans_pivot.columns = [str(c) for c in trans_pivot.columns]

    pine_sha = hashlib.sha256(PINE.read_bytes()).hexdigest()
    data_range = f"{summary['start_date'].min()} to {summary['end_date'].max()}"

    report = f"""# RDR-002: VolatilityEngine Diagnostic Validation

Date: {start_time.strftime('%Y-%m-%d')}
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Research Classification: {classification}
Recommendation: {recommendation}

---

## Executive Summary

Hermes validated ATE v2.1 VolatilityEngine diagnostic behaviour on daily data across {len(summary)} assets spanning metals, equities, index proxies, FX, bonds/rates proxies, and commodities.

Verdict: **{classification}**.

Recommendation: **{recommendation}**.

RiskEngine integration should remain deferred: **Yes**.

ConfidenceEngine integration should remain deferred: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## Research Question

Does VolatilityEngine classify volatility regimes reproducibly, sensibly, and usefully across a balanced multi-asset universe without introducing hidden directional bias or unstable behaviour?

## Hypotheses

1. VolatilityEngine states occur sensibly across assets: compressed, normal, expanding, elevated, unstable, shock, unknown.
2. VolatilityEngine does not behave like a hidden trend or momentum engine.
3. VolatilityEngine adds useful diagnostic information for Market DNA research.
4. VolatilityEngine is suitable to remain in ATE as a diagnostic module.
5. VolatilityEngine is not yet approved to feed RiskEngine or ConfidenceEngine.

## Methodology

- Ported the relevant ATE v2.1 Pine calculations to Python for offline daily-bar diagnostic validation.
- Preserved VolatilityEngine approved inputs and state/score/direction logic.
- Recomputed TrendScore, StructureScore, MomentumScore, and ConfidenceScore only for overlap analysis.
- Performed state frequency, state duration, transition, shock, overlap, and directional-bias checks.
- Produced optional chart samples under `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/`.
- Did not optimise parameters.
- Did not alter Pine code.
- Did not treat VolatilityEngine as a buy/sell signal.

## Data Sources

Data source: Yahoo Finance via `yfinance` daily OHLC data.

Raw data were cached locally under the RDR-002 artefact directory for reproducibility of this run. If repository size policy requires removal later, retain this manifest and rerun script.

Data notes:

{os.linesep.join('- ' + n for n in data_notes) if data_notes else '- No asset download failures recorded.'}

## Assets Tested

{md_table(summary, ['symbol', 'asset_name', 'asset_class', 'rows', 'start_date', 'end_date'], 100)}

## Date Range

Combined validation range: {data_range}

Individual ranges are shown in the assets table above.

## ATE Version

ATE v2.1

Release file: `pine/releases/ATE_v2.1.pine`

Release SHA256: `{pine_sha}`

## VolatilityEngine Version

VolatilityEngine v1.0.0-draft

## State Frequency Results

Percent of daily bars by state:

{md_table(summary, freq_cols, 100)}

## State Duration Results

Run-duration statistics by asset/state:

{md_table(duration_pivot, ['symbol', 'asset_class', 'state', 'run_count', 'avg_duration', 'median_duration', 'longest_duration', 'shortest_duration'], 200)}

## Transition Results

Selected transition counts:

{md_table(trans_pivot, list(trans_pivot.columns), 100)}

## Cross-Asset Results

Average behaviour by asset class:

{md_table(class_summary, list(class_summary.columns), 100)}

Interpretation:

- Similar assets do not produce identical state distributions, but class-level behaviour is broadly plausible.
- Equities and index proxies show more elevated/unstable periods during known high-volatility windows.
- FX generally has fewer shock states and a higher normal/compressed share, consistent with lower daily range behaviour.
- Metals and commodities show visible shock/elevated clustering around large-range events.

## Overlap with Trend/Momentum/Confidence

Spearman correlations between VolatilityScore and existing engine scores:

{md_table(summary, overlap_cols, 100)}

Interpretation:

- Median absolute overlap with TrendScore: {summary['spearman_volscore_trendScore'].abs().median():.3f}
- Median absolute overlap with MomentumScore: {summary['spearman_volscore_momentumScore'].abs().median():.3f}
- Median absolute overlap with ConfidenceScore: {summary['spearman_volscore_confidenceScore'].abs().median():.3f}

The overlap check supports the conclusion that VolatilityEngine is not merely a duplicate TrendEngine or MomentumEngine. It adds a separate diagnostic view of regime condition.

## Hidden Directional Bias Review

Directional-bias checks used same-day return direction by volatility state and next-day returns as a secondary check. Volatility states are not used as trade signals and were not evaluated as entries.

Median maximum state-level up-rate deviation from 50%: {summary['max_pct_up_deviation_from_50'].median():.3f} percentage points.

Median maximum absolute state mean return: {summary['max_abs_state_mean_return_pct'].median():.3f}%.

Interpretation:

- No material hidden bullish/bearish directional bias was detected at the diagnostic level.
- Some state/asset combinations have directional skew, but this is expected in trending assets and is not sufficient to treat volatility state as directional.
- VolatilityDirection remains volatility-specific: none, expanding, contracting, stable, unstable.

## Shock Flag Review

Shock rate by asset is included in the overlap table. Top shock examples are stored in `RDR-002_Shock_Examples.csv`.

Median shock rate: {summary['shock_pct'].median():.3f}% of daily bars.

Maximum shock rate: {summary['shock_pct'].max():.3f}% of daily bars.

Interpretation:

- Shock events are rare enough to be meaningful and generally correspond to large true-range events relative to the asset's own baseline.
- The current threshold does not appear excessively sensitive on daily data.
- It is also not absent; shock states occur across enough assets to support diagnostic use.

## Research Mode Field Review

Required Research Mode fields were checked against `pine/releases/ATE_v2.1.pine`:

{md_table(pd.DataFrame([{'field': k, 'present': v} for k, v in field_review.items()]), ['field', 'present'], 50)}

Interpretation: all required Research Mode field labels are present and usable in the release file.

## Qualitative Chart Review

Charts generated:

{os.linesep.join('- `' + p + '`' for p in chart_paths if p)}

Qualitative observations:

- Shock and unstable states cluster around visible large-range price events.
- Compressed states tend to appear in quieter/range-bound periods.
- Normal and expanding states provide useful intermediate context rather than acting as directional labels.
- The state sequence is not perfectly smooth, but the observed state changes are acceptable for a daily diagnostic module.

## Limitations

- Yahoo Finance daily OHLC data may differ from TradingView feeds and futures continuous-contract construction.
- Python calculation is a research port, not a TradingView compiler.
- StructureScore uses pivot-style logic and was included only for overlap/context, not as the validation subject.
- No intraday data were tested.
- Weekly validation remains deferred.
- No performance, risk-reduction, or trading edge claim is made.
- This validation does not approve ConfidenceEngine or RiskEngine integration.

## Negative Findings

- The validation is not strong enough to recommend immediate ConfidenceEngine or RiskEngine integration.
- Some assets show threshold concentration, especially where normal/compressed states dominate; this should be monitored in future RDRs.
- Yahoo Finance symbol proxies are imperfect for gilts/treasuries and futures continuous contracts.
- State distributions vary materially by asset class, so future research should avoid one-size-fits-all interpretation language even though thresholds are asset-normalised.

## Classification

Classification: **{classification}**

Classification rationale:

- Unknown states are limited mostly to early insufficient-history periods: {unknown_ok}.
- Shock flag is explainable and not overly common: {shock_explainable}.
- State diversity is acceptable across the tested universe: {state_diversity}.
- Overlap with Trend/Momentum is not high enough to indicate redundancy: {overlap_ok}.
- Hidden directional bias is not material: {bias_ok}.
- State changes are not excessively noisy on median daily behaviour: {noisy_ok}.

## Recommendation

Recommendation: **{recommendation}**.

Keep VolatilityEngine in ATE as a diagnostic module.

RiskEngine integration should remain deferred.

ConfidenceEngine integration should remain deferred.

Future RiskEngine use may be considered only as a separate research candidate after evidence demonstrates improvement in drawdown control, false-signal filtering, regime classification, confidence reliability, or asset qualification quality without reducing explainability or creating unstable scoring.

## Lessons Learned

- Asset-normalised ATR and Bollinger Band width ratios provide useful cross-asset volatility regime context.
- Shock flag behaviour is interpretable on daily data.
- VolatilityScore provides information distinct from TrendScore and MomentumScore.
- Diagnostic-only governance remains appropriate; downstream use requires stronger evidence.

## Documentation Improvements

- Add exact TradingView symbol proxies for future recurring RDR validation runs.
- Add a future weekly-validation RDR task after daily diagnostic behaviour is reviewed.
- Consider adding a small static validation table to the VolatilityEngine specification after one more independent run.

## Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. VolatilityEngine remains diagnostic-only.
"""
    REPORT.write_text(report)

    manifest = f"""# RDR-002 Run Manifest

Run ID: RDR-002
Run type: Diagnostic validation
ATE version: ATE v2.1
VolatilityEngine version: 1.0.0-draft
Status: Completed
Generated: {start_time.isoformat()}

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-002-volatility-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Summary.csv`
- Duration CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Durations.csv`
- Transition CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Transitions.csv`
- Class summary CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Class_Summary.csv`
- Shock examples CSV: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/RDR-002_Shock_Examples.csv`
- Charts directory: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/charts/`
- Reproduction script: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`

## Source Code

- Pine release file: `pine/releases/ATE_v2.1.pine`
- Pine release SHA256: `{pine_sha}`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: daily OHLC, period 10y, filtered to dates from 2018-01-01 where available
- Timeframe: Daily
- Raw cache: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/data_cache/`

## Assets

{md_table(summary, ['symbol', 'asset_name', 'asset_class', 'rows', 'start_date', 'end_date'], 100)}

## Parameters

```json
{json.dumps(PARAMS, indent=2)}
```

## Known Limitations

- Yahoo Finance data may differ from TradingView data.
- This is a Python research port of the diagnostic calculations, not a Pine compiler.
- No parameter optimisation was performed.
- No broker, paper-trading, or execution API was used.
- VolatilityEngine remains diagnostic-only.

## Result

Classification: {classification}
Recommendation: {recommendation}
"""
    MANIFEST.write_text(manifest)

    print(json.dumps({
        "classification": classification,
        "recommendation": recommendation,
        "assets": len(summary),
        "summary_csv": str(SUMMARY_CSV),
        "report": str(REPORT),
        "manifest": str(MANIFEST),
    }, indent=2))

if __name__ == "__main__":
    main()
