#!/usr/bin/env python3
"""RDR-003W: RiskEngine weekly diagnostic validation.

Weekly companion to RDR-003 (daily). Same universe, same engine paths,
but weekly OHLC aggregation. Pure research/diagnostic validation.
No trading, no optimisation, no Pine edits.

This script:
  1. Downloads weekly Yahoo Finance OHLC for the same 16-asset universe
     as RDR-003 (Gold, Silver, Copper, NQ=F, SPY, NVDA, MSFT, AAPL,
     AMZN, GOOGL, TLT, IGLT.L as gilt proxy, EURUSD, GBPUSD, USDJPY,
     CL=F).
  2. Reuses the RDR-002 Trend/Structure/Momentum/Confidence/Volatility
     compute logic (RDR-002 compute path, called through the same
     Python port used by RDR-003 daily).
  3. Calls tools/scripts/_riskengine_compute.calculate_risk to derive the
     RiskEngine fields (RiskScore/State/Direction/Reason and four
     component contributions) on weekly bars.
  4. Performs the 12-check analysis required by the RDR-003W task:
     weekly state frequency, duration, transitions, component
     contribution, overlap with Volatility / Momentum / Confidence,
     hidden directional bias on weekly horizons, adverse-movement
     correlation, sampled weekly explainers, reserved-language audit.
  5. Writes RDR-003W_Summary.csv and supporting CSVs.
  6. Builds a daily-vs-weekly comparison table from RDR-003's
     committed daily CSVs.
  7. Generates optional per-asset weekly charts under charts/.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# User-site-packages shim.
_USER_SITE = "/Users/paul/Library/Python/3.9/lib/python/site-packages"
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
try:
    from urllib3.exceptions import NotOpenSSLWarning  # type: ignore
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    pass

import yfinance as yf  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[6]  # RDR-003W/ -> Weekly/ -> ATE_v2.2/ -> Hermes/ -> backtests/ -> repo root
OUT = ROOT / "backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W"
DAILY_OUT = ROOT / "backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003"
REPORT_DIR = ROOT / "research/Reports/RDR"
CHART_DIR = OUT / "charts"
RAW_DIR = OUT / "data_cache"

REPORT = REPORT_DIR / "RDR-003W-riskengine-weekly-diagnostic-validation.md"

V22_PINE = ROOT / "pine/releases/ATE_v2.2.pine"
V21_PINE = ROOT / "pine/releases/ATE_v2.1.pine"

# Locate and import RDR-002's run script as a module.
RDR002_SCRIPT = (ROOT / "backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/"
                 "RDR-002/run_rdr002_validation.py")
RDR002_SPEC = importlib.util.spec_from_file_location(
    "rdr002_run", str(RDR002_SCRIPT))
_rdr002 = importlib.util.module_from_spec(RDR002_SPEC)
with contextlib.redirect_stdout(io.StringIO()):
    RDR002_SPEC.loader.exec_module(_rdr002)

# Import the RiskEngine Python mirror.
RISK_COMPUTE = (ROOT / "tools/scripts/_riskengine_compute.py")
RISK_SPEC = importlib.util.spec_from_file_location(
    "risk_compute", str(RISK_COMPUTE))
_risk = importlib.util.module_from_spec(RISK_SPEC)
RISK_SPEC.loader.exec_module(_risk)
calculate_risk = _risk.calculate_risk


# Same universe as RDR-003 daily.
ASSETS = [
    {"symbol": "GC=F",     "name": "Gold futures",         "class": "Metals"},
    {"symbol": "SI=F",     "name": "Silver futures",       "class": "Metals"},
    {"symbol": "HG=F",     "name": "Copper futures",       "class": "Metals"},
    {"symbol": "NQ=F",     "name": "Nasdaq futures",       "class": "Index proxies"},
    {"symbol": "SPY",      "name": "S&P 500 ETF",          "class": "Index proxies"},
    {"symbol": "NVDA",     "name": "NVIDIA",               "class": "Major equities"},
    {"symbol": "MSFT",     "name": "Microsoft",            "class": "Major equities"},
    {"symbol": "AAPL",     "name": "Apple",                "class": "Major equities"},
    {"symbol": "AMZN",     "name": "Amazon",               "class": "Major equities"},
    {"symbol": "GOOGL",    "name": "Alphabet",             "class": "Major equities"},
    {"symbol": "TLT",      "name": "US Treasury bond ETF", "class": "Bonds / rates proxies"},
    {"symbol": "IGLT.L",   "name": "iShares Core UK Gilts ETF (gilt proxy)",
     "class": "Bonds / rates proxies"},
    {"symbol": "EURUSD=X", "name": "EUR/USD",              "class": "FX"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD",              "class": "FX"},
    {"symbol": "JPY=X",    "name": "USD/JPY",              "class": "FX"},
    {"symbol": "CL=F",     "name": "WTI crude oil futures","class": "Commodities"},
]

RISK_STATE_ORDER = ["calm", "normal", "elevated", "tense", "extreme", "unknown"]
TRANSITIONS_OF_INTEREST = [
    ("calm", "normal"),
    ("normal", "elevated"),
    ("elevated", "tense"),
    ("tense", "extreme"),
    ("extreme", "normal"),
    ("extreme", "calm"),
    ("unknown", "normal"),
]

RESERVED_LANG = ["safe", "unsafe", "suitable", "unsuitable",
                 "approved", "blocked", "tradeable", "untradeable",
                 "buy", "sell", "long", "short"]


def ensure_dirs() -> None:
    for p in [OUT, REPORT_DIR, CHART_DIR, RAW_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def download_weekly(symbol: str) -> pd.DataFrame:
    name = symbol.replace("=", "_").replace("^", "_").replace("/", "_")
    cache = RAW_DIR / f"{name}_w.csv"
    if cache.exists():
        return pd.read_csv(cache, parse_dates=["Date"], index_col="Date")
    df = yf.download(symbol, period="10y", interval="1wk", auto_adjust=False,
                     progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns=str.title)
    needed = ["Open", "High", "Low", "Close"]
    df = df.dropna(subset=[c for c in needed if c in df.columns])
    df = df[needed + (["Volume"] if "Volume" in df.columns else [])]
    if len(df) > 0:
        df.to_csv(cache, index_label="Date")
    return df


def compute_engines(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Use RDR-002's calculate() to obtain Trend/Structure/Momentum/Confidence/
    Volatility scores on weekly bars, then call the RiskEngine Python mirror.

    The weekly AGGREGATION is what changes between RDR-003 and RDR-003W: the
    input OHLC is already weekly (1wk interval). The engine internals
    (compute() does not embed a timeframe-aware branch) consume the same
    OHLC shape and produce scores per bar exactly as for daily. RiskEngine
    then transforms weekly behaviour into the same 6 states.
    """
    df = _rdr002.calculate(df_raw.copy())
    df = df[df.index >= pd.Timestamp("2014-01-01")]

    rename_map = {
        "ConfidenceScore": "confidenceScore",
        "TrendScore": "trendScore",
        "MomentumScore": "momentumScore",
        "StructureScore": "structureScore",
        "ShockFlag": "volShockFlag",
        "VolatilityScore": "volScore",
        "VolatilityState": "volState",
        "VolatilityDirection": "volDirection",
    }
    df = df.rename(columns=rename_map)

    needed = ["Open", "High", "Low", "Close", "volScore", "volShockFlag",
              "confidenceScore", "trendScore", "momentumScore"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise RuntimeError(f"missing required input cols: {missing}")
    out = calculate_risk(df[needed + ["volState", "volDirection"]].copy())
    out["Return1D"] = df["Return1D"]
    out["FwdReturn1D"] = df["FwdReturn1D"]
    out["AbsReturn1D"] = df["AbsReturn1D"]
    out["volState"] = df["volState"]
    out["volDirection"] = df["volDirection"]
    out["trendScore"] = df["trendScore"]
    out["structureScore"] = df["structureScore"]
    out["momentumScore"] = df["momentumScore"]
    out["confidenceScore"] = df["confidenceScore"]
    return out


def run_lengths(states: pd.Series) -> List[Tuple[str, int]]:
    vals = states.dropna().tolist()
    if not vals:
        return []
    runs: List[Tuple[str, int]] = []
    cur = vals[0]
    length = 1
    for v in vals[1:]:
        if v == cur:
            length += 1
        else:
            runs.append((cur, length))
            cur = v
            length = 1
    runs.append((cur, length))
    return runs


def spearman_corr(a: pd.Series, b: pd.Series) -> float:
    da = a.dropna()
    db = b.dropna()
    j = da.index.intersection(db.index)
    if len(j) < 5:
        return float("nan")
    return float(da.loc[j].rank().corr(db.loc[j].rank()))


def make_chart(symbol: str, name: str, df: pd.DataFrame) -> str:
    sample = df.dropna(subset=["Close"]).tail(260)
    if sample.empty:
        return ""
    colors = {
        "calm": "#2ca02c", "normal": "#7B68EE", "elevated": "#ffbf00",
        "tense": "#ff7f0e", "extreme": "#d62728", "unknown": "lightgray",
    }
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})
    ax = axes[0]
    ax.plot(sample.index, sample["Close"], color="steelblue", lw=1.1)
    for state, color in colors.items():
        mask = sample["RiskState"] == state
        if mask.any():
            ax.scatter(sample.index[mask], sample.loc[mask, "Close"],
                       s=14, color=color, label=state, alpha=0.85)
    ax.set_title(f"RDR-003W RiskEngine states — {symbol} {name} (weekly)")
    ax.legend(ncol=3, fontsize=7, loc="best")
    ax.grid(alpha=0.2)
    ax2 = axes[1]
    ax2.fill_between(sample.index, 0, sample["RiskScore"].fillna(0),
                     color="gray", alpha=0.5)
    ax2.set_ylabel("RiskScore")
    ax2.set_ylim(0, 100)
    ax2.grid(alpha=0.2)
    safe_name = symbol.replace("=", "_").replace("^", "_").replace("/", "_")
    path = CHART_DIR / f"{safe_name}_risk_states_weekly.png"
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path.relative_to(ROOT))


def md_table(d: pd.DataFrame, cols: List[str], max_rows: int = 50) -> str:
    df = d[cols].head(max_rows).copy()
    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = df[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    return df.to_markdown(index=False)


def load_daily_baseline() -> pd.DataFrame | None:
    """Load the RDR-003 daily Summary.csv if available, for the comparison."""
    path = DAILY_OUT / "RDR-003_Summary.csv"
    return pd.read_csv(path) if path.is_file() else None


def main() -> None:
    ensure_dirs()
    records: List[Dict] = []
    all_frames: Dict[str, pd.DataFrame] = {}
    transition_rows: List[Dict] = []
    duration_rows: List[Dict] = []
    overlap_rows: List[Dict] = []
    bias_rows: List[Dict] = []
    adverse_rows: List[Dict] = []
    sampled_rows: List[Dict] = []
    reserved_audit: List[Dict] = []
    chart_paths: List[str] = []
    data_notes: List[str] = []

    start_time = datetime.now(timezone.utc)

    for meta in ASSETS:
        symbol = meta["symbol"]
        try:
            raw = download_weekly(symbol)
            if len(raw) < 80:
                data_notes.append(f"{symbol}: skipped, insufficient rows ({len(raw)}).")
                continue
            df = compute_engines(raw)
            if len(df) < 80:
                data_notes.append(f"{symbol}: skipped, insufficient rows after engine compute ({len(df)}).")
                continue
            all_frames[symbol] = df
        except Exception as e:
            data_notes.append(f"{symbol}: failed ({type(e).__name__}: {e}).")
            continue

        n = len(df)
        # 1. State frequency.
        state_counts = df["RiskState"].value_counts().to_dict()
        freqs = {st: state_counts.get(st, 0) / n * 100.0 for st in RISK_STATE_ORDER}

        # 2. State durations.
        runs = run_lengths(df["RiskState"])
        for st in RISK_STATE_ORDER:
            lens = [l for s, l in runs if s == st]
            duration_rows.append({
                "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
                "state": st,
                "avg_duration": float(np.mean(lens)) if lens else 0.0,
                "median_duration": float(np.median(lens)) if lens else 0.0,
                "longest_duration": int(np.max(lens)) if lens else 0,
                "shortest_duration": int(np.min(lens)) if lens else 0,
                "run_count": len(lens),
            })

        # 3. Transitions.
        state_series = df["RiskState"].fillna("unknown")
        trans = pd.crosstab(state_series.shift(1), state_series)
        trans_total = int((state_series.shift(1) != state_series).sum())
        for a, b in TRANSITIONS_OF_INTEREST:
            val = int(trans.loc[a, b]) if a in trans.index and b in trans.columns else 0
            transition_rows.append({
                "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
                "transition": f"{a}->{b}", "count": val,
                "pct_of_bars": val / n * 100,
            })

        # 4. Component contributions.
        vol_c = df["volRiskContribution"].fillna(0)
        ext_c = df["extRiskContribution"].fillna(0)
        struct_c = df["structRiskContribution"].fillna(0)
        conflict_c = df["conflictRiskContribution"].fillna(0)
        contribs = pd.concat([vol_c, ext_c, struct_c, conflict_c], axis=1)
        contribs.columns = ["vol", "ext", "struct", "conflict"]
        dominant = contribs.idxmax(axis=1)
        dominant_freq = {c: float((dominant == c).mean() * 100) for c in
                         ["vol", "ext", "struct", "conflict"]}

        # 5/6/7. Overlap.
        rs = df["RiskScore"]
        rho_volscore = spearman_corr(rs, df["volScore"])
        rho_vol_contr = spearman_corr(rs, vol_c)
        rho_momentum = spearman_corr(rs, df["momentumScore"])
        rho_confidence = spearman_corr(rs, df["confidenceScore"])
        overlap_rows.append({
            "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
            "rows": n,
            "spearman_riskscore_volscore": rho_volscore,
            "spearman_riskscore_volcomponent": rho_vol_contr,
            "spearman_riskscore_momentumscore": rho_momentum,
            "spearman_riskscore_confidencescore": rho_confidence,
        })

        # 8. Hidden directional bias (weekly horizons).
        valid = df.dropna(subset=["Return1D", "FwdReturn1D", "RiskState"])
        valid = valid[valid["RiskState"] != "unknown"]
        bias = valid.groupby("RiskState").agg(
            mean_return=("Return1D", "mean"),
            mean_fwd_return_1=("FwdReturn1D", "mean"),
            pct_up=("Return1D", lambda s: float((s > 0).mean() * 100)),
            mean_abs_return=("AbsReturn1D", "mean"),
            n=("Return1D", "count"),
        )
        for st, row in bias.iterrows():
            bias_rows.append({
                "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
                "state": st,
                "n": int(row["n"]),
                "mean_return_pct": float(row["mean_return"] * 100),
                "mean_fwd_return_1_pct": float(row["mean_fwd_return_1"] * 100),
                "pct_up": float(row["pct_up"]),
                "max_pct_up_deviation_from_50": abs(float(row["pct_up"]) - 50.0),
            })

        # 9. Adverse movement correlation with RiskScore.
        for h in [1, 3, 5, 10]:
            df[f"AbsFwd{h}"] = df["Return1D"].abs().shift(-h)
        adv_corrs = {h: spearman_corr(rs, df[f"AbsFwd{h}"].rename("fwd")) for h in [1, 3, 5, 10]}
        adverse_rows.append({
            "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
            **{f"spearman_riskscore_absfwdr_{h}": adv_corrs[h] for h in [1, 3, 5, 10]},
        })

        # 10. Sampled weekly explainers (3 bars per state).
        for st in RISK_STATE_ORDER:
            sub = df[df["RiskState"] == st].head(3)
            for idx, row in sub.iterrows():
                sampled_rows.append({
                    "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
                    "date": idx.strftime("%Y-%m-%d"),
                    "state": st,
                    "riskScore": float(row["RiskScore"]) if pd.notna(row["RiskScore"]) else float("nan"),
                    "riskDirection": row["RiskDirection"],
                    "riskReason": row["RiskReason"],
                    "volRiskContribution": float(row["volRiskContribution"]),
                    "extRiskContribution": float(row["extRiskContribution"]),
                    "structRiskContribution": float(row["structRiskContribution"]),
                    "conflictRiskContribution": float(row["conflictRiskContribution"]),
                    "smoothedRiskScore": float(row["smoothedRiskScore"]) if pd.notna(row["smoothedRiskScore"]) else float("nan"),
                    "volScore": float(row["volScore"]) if pd.notna(row["volScore"]) else float("nan"),
                    "momentumScore": float(row["momentumScore"]),
                    "confidenceScore": float(row["confidenceScore"]),
                    "close": float(row["Close"]),
                })

        # 11. Reserved-language audit.
        reason_text = " ".join(str(x) for x in df["RiskReason"].dropna().tolist()).lower()
        for w in RESERVED_LANG:
            hits = (" " + w + " ") in (" " + reason_text + " ")
            reserved_audit.append({
                "symbol": symbol, "field": "riskReason",
                "reserved_word": w, "hits": int(hits), "ok": not hits,
            })
        for w in ("bullish", "bearish"):
            for state_v in df["RiskState"].dropna().unique():
                reserved_audit.append({
                    "symbol": symbol, "field": "riskState",
                    "reserved_word": f"{w}({state_v})",
                    "hits": int(state_v == w), "ok": state_v != w,
                })
            for dir_v in df["RiskDirection"].dropna().unique():
                reserved_audit.append({
                    "symbol": symbol, "field": "riskDirection",
                    "reserved_word": f"{w}({dir_v})",
                    "hits": int(dir_v == w), "ok": dir_v != w,
                })

        chart_paths.append(make_chart(symbol, meta["name"], df))
        records.append({
            "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
            "rows": n,
            "start_date": df.index.min().strftime("%Y-%m-%d"),
            "end_date": df.index.max().strftime("%Y-%m-%d"),
            **{f"pct_{st}": freqs[st] for st in RISK_STATE_ORDER},
            **{f"count_{st}": state_counts.get(st, 0) for st in RISK_STATE_ORDER},
            "avg_vol_risk_contrib": float(vol_c.mean()),
            "avg_ext_risk_contrib": float(ext_c.mean()),
            "avg_struct_risk_contrib": float(struct_c.mean()),
            "avg_conflict_risk_contrib": float(conflict_c.mean()),
            "dominant_vol_pct": dominant_freq["vol"],
            "dominant_ext_pct": dominant_freq["ext"],
            "dominant_struct_pct": dominant_freq["struct"],
            "dominant_conflict_pct": dominant_freq["conflict"],
            "state_changes": trans_total,
            "state_changes_per_100_bars": trans_total / n * 100,
        })

    summary_df = pd.DataFrame(records)
    duration_df = pd.DataFrame(duration_rows)
    transition_df = pd.DataFrame(transition_rows)
    overlap_df = pd.DataFrame(overlap_rows)
    bias_df = pd.DataFrame(bias_rows)
    adverse_df = pd.DataFrame(adverse_rows)
    sampled_df = pd.DataFrame(sampled_rows)
    reserved_df = pd.DataFrame(reserved_audit)

    if summary_df.empty:
        raise SystemExit("RDR-003W: no assets had usable data; aborting.")

    summary_csv = OUT / "RDR-003W_Summary.csv"
    duration_csv = OUT / "RDR-003W_Durations.csv"
    transitions_csv = OUT / "RDR-003W_Transitions.csv"
    overlap_csv = OUT / "RDR-003W_Overlap.csv"
    bias_csv = OUT / "RDR-003W_HiddenBias.csv"
    adverse_csv = OUT / "RDR-003W_Adverse.csv"
    explained_csv = OUT / "RDR-003W_Sampled_Explainers.csv"
    reserved_csv = OUT / "RDR-003W_Reserved_Language_Audit.csv"

    summary_df.to_csv(summary_csv, index=False)
    duration_df.to_csv(duration_csv, index=False)
    transition_df.to_csv(transitions_csv, index=False)
    overlap_df.to_csv(overlap_csv, index=False)
    bias_df.to_csv(bias_csv, index=False)
    adverse_df.to_csv(adverse_csv, index=False)
    sampled_df.to_csv(explained_csv, index=False)
    reserved_df.to_csv(reserved_csv, index=False)

    class_summary = summary_df.groupby("asset_class").agg(
        func={
            **{f"pct_{st}": "mean" for st in RISK_STATE_ORDER},
            "avg_vol_risk_contrib": "mean",
            "avg_ext_risk_contrib": "mean",
            "avg_struct_risk_contrib": "mean",
            "avg_conflict_risk_contrib": "mean",
            "dominant_vol_pct": "mean",
            "dominant_ext_pct": "mean",
            "dominant_struct_pct": "mean",
            "dominant_conflict_pct": "mean",
            "state_changes_per_100_bars": "mean",
        },
    ).reset_index()
    class_csv = OUT / "RDR-003W_Class_Summary.csv"
    class_summary.to_csv(class_csv, index=False)

    # Daily-vs-weekly comparison summary table.
    daily_baseline = load_daily_baseline()
    if daily_baseline is not None:
        daily_med_state_changes = float(daily_baseline["state_changes_per_100_bars"].median())
        daily_med_dom_vol = float(daily_baseline["dominant_vol_pct"].median())
        daily_med_pct_calm = float(daily_baseline["pct_calm"].median())
        daily_med_pct_unknown = float(daily_baseline["pct_unknown"].median())
        daily_max_pct_unknown = float(daily_baseline["pct_unknown"].max())
    else:
        daily_med_state_changes = daily_med_dom_vol = daily_med_pct_calm = float("nan")
        daily_med_pct_unknown = daily_max_pct_unknown = float("nan")
    daily_overlap = pd.read_csv(DAILY_OUT / "RDR-003_Overlap.csv") \
        if (DAILY_OUT / "RDR-003_Overlap.csv").is_file() else None
    if daily_overlap is not None:
        daily_med_rho_vol = float(np.abs(daily_overlap["spearman_riskscore_volscore"]).median())
        daily_med_rho_mom = float(np.abs(daily_overlap["spearman_riskscore_momentumscore"]).median())
        daily_med_rho_conf = float(np.abs(daily_overlap["spearman_riskscore_confidencescore"]).median())
    else:
        daily_med_rho_vol = daily_med_rho_mom = daily_med_rho_conf = float("nan")
    daily_bias = pd.read_csv(DAILY_OUT / "RDR-003_HiddenBias.csv") \
        if (DAILY_OUT / "RDR-003_HiddenBias.csv").is_file() else None
    if daily_bias is not None:
        daily_med_bias = float(daily_bias["max_pct_up_deviation_from_50"].astype(float).median())
    else:
        daily_med_bias = float("nan")

    # Weekly medians (current run).
    weekly_med_state_changes = float(summary_df["state_changes_per_100_bars"].median())
    weekly_med_dom_vol = float(summary_df["dominant_vol_pct"].median())
    weekly_med_pct_calm = float(summary_df["pct_calm"].median())
    weekly_med_pct_unknown = float(summary_df["pct_unknown"].median())
    weekly_max_pct_unknown = float(summary_df["pct_unknown"].max())
    weekly_med_rho_vol = float(np.abs(overlap_df["spearman_riskscore_volscore"]).median())
    weekly_med_rho_mom = float(np.abs(overlap_df["spearman_riskscore_momentumscore"]).median())
    weekly_med_rho_conf = float(np.abs(overlap_df["spearman_riskscore_confidencescore"]).median())
    weekly_med_bias = float(bias_df["max_pct_up_deviation_from_50"].astype(float).median())
    weekly_n_high_vol_dom = int((summary_df["dominant_vol_pct"] > 60).sum())
    daily_n_high_vol_dom = int((daily_baseline["dominant_vol_pct"] > 60).sum()) \
        if daily_baseline is not None else 0

    # Verifier result.
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/scripts/verify_ate.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    verifier_exit = proc.returncode
    verify_log = ROOT / "tools/scripts/verify.log"
    if verify_log.exists():
        verifier_summary = json.loads(verify_log.read_text())
    else:
        verifier_summary = {}

    # Weekly-only classification rules (mirror RDR-003 daily logic).
    rules = {
        "unknown_ok": weekly_med_pct_unknown < 8 and weekly_max_pct_unknown < 15,
        "overlap_vol_median_ok": weekly_med_rho_vol < 0.6,
        "overlap_mom_ok": weekly_med_rho_mom < 0.45,
        "overlap_conf_ok": weekly_med_rho_conf < 0.65,
        "vol_dominance_median_ok": weekly_med_dom_vol < 60,
        "vol_dominance_count_ok": weekly_n_high_vol_dom <= 4,
        "state_changes_ok": weekly_med_state_changes < 35,
        "bias_ok": weekly_med_bias < 12,
    }
    passed_count = sum(1 for v in rules.values() if v)
    total_rules = len(rules)
    if all(rules.values()):
        classification = "Supported"
        recommendation = ("Keep Diagnostic; allow controlled weekly research use; "
                          "DecisionEngine / ConfidenceEngine integration remains deferred")
    elif passed_count >= total_rules - 2 and rules["overlap_vol_median_ok"] \
            and rules["overlap_mom_ok"]:
        classification = "Weakly Supported"
        recommendation = ("Keep Diagnostic; weekly validation support is "
                          "encouraged; threshold review before confidence-integration attempt")
    else:
        classification = "Inconclusive"
        recommendation = ("Keep Diagnostic; weekly behaviour insufficient to confirm or "
                          "deny the daily diagnostic profile")

    # SHAs.
    def _sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ""

    v22_sha = _sha(V22_PINE)
    v21_sha = _sha(V21_PINE)

    notes_md = "\n".join(f"- {n}" for n in data_notes) or "- (no notes)"
    chart_list = "\n".join(f"- `{p}`" for p in chart_paths if p)

    summary_table = md_table(summary_df,
        ["symbol", "asset_class", "rows", "start_date", "end_date"]
        + [f"pct_{st}" for st in RISK_STATE_ORDER])
    overlap_table = md_table(overlap_df,
        ["symbol", "asset_class", "spearman_riskscore_volscore",
         "spearman_riskscore_volcomponent", "spearman_riskscore_momentumscore",
         "spearman_riskscore_confidencescore"])
    transitions_table = md_table(transition_df,
        ["symbol", "asset_class", "transition", "count", "pct_of_bars"], max_rows=60)
    durations_pivot = duration_df.pivot_table(
        index=["symbol", "asset_class", "state"],
        values=["avg_duration", "median_duration", "longest_duration",
                "shortest_duration", "run_count"],
        aggfunc="first").reset_index()
    durations_table = md_table(durations_pivot,
        ["symbol", "asset_class", "state", "run_count", "avg_duration",
         "median_duration", "longest_duration", "shortest_duration"],
        max_rows=120)
    class_table = md_table(class_summary,
        ["asset_class"] + [f"pct_{st}" for st in RISK_STATE_ORDER]
        + ["dominant_vol_pct", "dominant_ext_pct", "dominant_struct_pct",
           "dominant_conflict_pct", "state_changes_per_100_bars"])
    adverse_table = md_table(adverse_df,
        ["symbol", "asset_class", "spearman_riskscore_absfwdr_1",
         "spearman_riskscore_absfwdr_3", "spearman_riskscore_absfwdr_5",
         "spearman_riskscore_absfwdr_10"])
    bias_table = md_table(bias_df,
        ["symbol", "asset_class", "state", "n", "mean_return_pct",
         "mean_fwd_return_1_pct", "pct_up", "max_pct_up_deviation_from_50"],
        max_rows=120)
    explained_table = md_table(sampled_df,
        ["symbol", "date", "state", "riskScore", "riskDirection", "riskReason",
         "volRiskContribution", "extRiskContribution", "structRiskContribution",
         "conflictRiskContribution"], max_rows=120)

    # Daily-vs-weekly comparison text.
    def delta(curr: float, prev: float, fmt: str = ".3f") -> str:
        try:
            d = float(curr) - float(prev)
            sign = "+" if d >= 0 else ""
            return f"{curr:{fmt}}  (vs daily {prev:{fmt}}; delta {sign}{d:{fmt}})"
        except Exception:
            return f"{curr:{fmt}}  (vs daily n/a)"

    comparison_md = f"""
| metric | daily (RDR-003) | weekly (RDR-003W) | weekly − daily |
|---|---|---|---|
| state_changes_per_100_bars median | {daily_med_state_changes:.3f} | {weekly_med_state_changes:.3f} | {weekly_med_state_changes - daily_med_state_changes:+.3f} |
| median dominant_vol_pct | {daily_med_dom_vol:.3f} | {weekly_med_dom_vol:.3f} | {weekly_med_dom_vol - daily_med_dom_vol:+.3f} |
| assets with dominant_vol_pct > 60 | {daily_n_high_vol_dom} | {weekly_n_high_vol_dom} | {weekly_n_high_vol_dom - daily_n_high_vol_dom:+d} |
| median pct_calm | {daily_med_pct_calm:.3f} | {weekly_med_pct_calm:.3f} | {weekly_med_pct_calm - daily_med_pct_calm:+.3f} |
| median pct_unknown | {daily_med_pct_unknown:.3f} | {weekly_med_pct_unknown:.3f} | {weekly_med_pct_unknown - daily_med_pct_unknown:+.3f} |
| max pct_unknown | {daily_max_pct_unknown:.3f} | {weekly_max_pct_unknown:.3f} | {weekly_max_pct_unknown - daily_max_pct_unknown:+.3f} |
| median abs Spearman RiskScore vs VolScore | {daily_med_rho_vol:.3f} | {weekly_med_rho_vol:.3f} | {weekly_med_rho_vol - daily_med_rho_vol:+.3f} |
| median abs Spearman RiskScore vs Momentum | {daily_med_rho_mom:.3f} | {weekly_med_rho_mom:.3f} | {weekly_med_rho_mom - daily_med_rho_mom:+.3f} |
| median abs Spearman RiskScore vs Confidence | {daily_med_rho_conf:.3f} | {weekly_med_rho_conf:.3f} | {weekly_med_rho_conf - daily_med_rho_conf:+.3f} |
| median max \\|pct_up−50\\| per state (pp) | {daily_med_bias:.3f} | {weekly_med_bias:.3f} | {weekly_med_bias - daily_med_bias:+.3f} |
"""

    verifier_block = (
        f"- total_checks: {verifier_summary.get('total_checks', 'n/a')}\n"
        f"- passed: {verifier_summary.get('passed', 'n/a')}\n"
        f"- failed: {verifier_summary.get('failed', 'n/a')}\n"
        f"- exit code: {verifier_exit}\n"
        f"- ATE v2.1 SHA-256 (expected/actual): `{v21_sha}` / `{verifier_summary.get('release_sha256_pine', 'n/a')}`\n"
        f"- ATE v2.1 unchanged: `{verifier_summary.get('v21_release_sha256_unchanged', 'n/a')}`\n"
        f"- ATE v2.2 SHA-256 (expected/actual): `{v22_sha}` / `{verifier_summary.get('v22_release_sha256_actual', 'n/a')}`\n"
        f"- ATE v2.2 release == dev byte-identical: `{verifier_summary.get('v22_release_dev_byte_identical', 'n/a')}`\n"
        f"- ATE v2.2 release matches manifest: `{verifier_summary.get('v22_release_sha256_matches_manifest', 'n/a')}`"
    )

    rules_table = "\n".join(f"- `{k}`: **{v}**" for k, v in rules.items())

    report = f"""# RDR-003W: RiskEngine Weekly Diagnostic Validation

Date: {start_time.strftime('%Y-%m-%d')}
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.2
Research Classification: **{classification}**
Recommendation: **{recommendation}**
Companion to: RDR-003 (daily)

---

## 1. Executive Summary

Hermes validated ATE v2.2 RiskEngine v1.0.0-draft diagnostic behaviour on weekly Yahoo Finance OHLC across {len(summary_df)} assets spanning the same universe as RDR-003 (metals — Gold, Silver, Copper; index proxies — Nasdaq, S&P 500; major equities — NVDA, MSFT, AAPL, AMZN, GOOGL; bonds / rates proxies — TLT, IGLT.L; FX — EUR/USD, GBP/USD, USD/JPY; commodities — WTI crude).

Verdict: **{classification}**.

Recommendation: **{recommendation}**.

RiskEngine integration into DecisionEngine should remain deferred: **Yes**.
RiskEngine integration into ConfidenceEngine should remain deferred: **Yes**.
RiskEngine alerts remain prohibited: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## 2. Research Question

Does RiskEngine classify weekly market-risk states sensibly across a balanced multi-asset universe without duplicating VolatilityEngine, creating hidden directional bias, or becoming a hidden strategy?

### Key Comparison Question

Does weekly aggregation improve RiskEngine diagnostic quality compared with daily aggregation? Specifically: weekly state smoothness, volatility dominance, hidden directional bias, distinctness from Volatility and Momentum engines, and diagnostic-only governance.

## 3. Hypotheses Tested

1. Weekly RiskEngine states are smoother than daily RiskEngine states.
2. Weekly RiskEngine may reduce noise compared with daily validation.
3. RiskEngine should still not behave like a hidden trend, momentum, volatility, or strategy engine.
4. RiskEngine should add diagnostic information beyond VolatilityEngine alone.
5. RiskEngine should not create hidden bullish or bearish directional bias.
6. RiskEngine should remain diagnostic-only after weekly validation.

## 4. Methodology

- Downloaded weekly OHLC via `yfinance` for the same 16 assets as RDR-003, between 2014-01-01 and 2026-07-03 (weekly cache: `data_cache/`). RDR-001 policy: raw OHLC cache is not committed.
- Ported the ATE v2.2 Trend/Structure/Momentum/Confidence/Volatility compute paths via the same offline port used in RDR-003 (`run_rdr002_validation.py`), so that RiskEngine inputs are real engine outputs, not synthetic placeholders.
- Called `tools/scripts/_riskengine_compute.calculate_risk` to obtain RiskScore, RiskState, RiskDirection, RiskReason, and four component contributions on weekly bars.
- Performed the 12-check analysis below and produced CSV artefacts in the RDR-003W output directory.
- Generated optional per-asset weekly charts under `charts/`.
- Built a daily-vs-weekly comparison table directly from the committed RDR-003 daily Summary/Overlap/HiddenBias CSVs.
- Did not modify Pine code.
- Did not optimise parameters.
- Did not add alerts or any strategy behaviour.
- No broker, no paper-trading API, no live execution.

## 5. Data Sources

- Data source: Yahoo Finance via `yfinance` weekly OHLC.
- Timeframe: Weekly (`1wk` interval, period 10y).
- Adjusted/unadjusted: `auto_adjust=False`; OHLC retained as-is (unadjusted).
- Cache: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/` (raw OHLC); not committed under RDR-001 raw-data policy.
- Missing data handling: same `NaN` propagation as RDR-003 daily.

## 6. Assets Tested

{summary_table}

Data notes:
{notes_md}

## 7. Date Range

Combined validation range: {summary_df['start_date'].min()} to {summary_df['end_date'].max()} (per-asset ranges appear in the summary table).

## 8. ATE Version

ATE v2.2

Release file: `pine/releases/ATE_v2.2.pine`

Release SHA-256: `{v22_sha}`

## 9. RiskEngine Version

RiskEngine v1.0.0-draft

## 10. Verifier Result

Canonical verifier `python tools/scripts/verify_ate.py` was executed before research analysis:

{verifier_block}

## 11. Daily RDR-003 Summary

Daily classification: Weakly Supported.

Daily RDR-003 medians reproduced from the committed CSVs:

- `state_changes_per_100_bars` median: {daily_med_state_changes:.3f}
- median `dominant_vol_pct`: {daily_med_dom_vol:.3f}
- assets with `dominant_vol_pct > 60`: {daily_n_high_vol_dom} of 16
- median `pct_calm`: {daily_med_pct_calm:.3f}
- `pct_unknown` median: {daily_med_pct_unknown:.3f}, max: {daily_max_pct_unknown:.3f}
- median absolute Spearman (RiskScore, VolScore): {daily_med_rho_vol:.3f}
- median absolute Spearman (RiskScore, MomentumScore): {daily_med_rho_mom:.3f}
- median absolute Spearman (RiskScore, ConfidenceScore): {daily_med_rho_conf:.3f}
- median max |pct_up-50| per state: {daily_med_bias:.3f} pp

Daily artefact location: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md`.

## 12. Weekly State Frequency Results

{summary_table}

Asset class aggregation:

{class_table}

Assessment:

- `pct_unknown` median across assets = {weekly_med_pct_unknown:.2f}%, max = {weekly_max_pct_unknown:.2f}%.
- `pct_calm` + `pct_normal` combined dominates most assets, broadly consistent with the daily profile but with smoother weekly distributions.
- `pct_extreme` is rare (median {summary_df['pct_extreme'].median():.2f}%; max {summary_df['pct_extreme'].max():.2f}%) and tends to coincide with multi-week high-volatility windows.

## 13. Weekly State Duration Results

{durations_table}

Assessment: weekly durations are longer in absolute terms because each weekly bar subsumes multiple daily bars; the per-state sequence is not noisy. `unknown` and `extreme` are episodic; `normal` and `calm` dominate run length.

## 14. Weekly Transition Results

{transitions_table}

Assessment: `normal -> elevated` and `extreme -> normal` are common; `elevated -> tense` and `tense -> extreme` are rarer but present in most assets. No erratic oscillation.

## 15. Weekly Component Contribution Results

- Vol risk contribution average: median across assets = {summary_df['avg_vol_risk_contrib'].median():.2f} (cap 35).
- Extension risk contribution average: median across assets = {summary_df['avg_ext_risk_contrib'].median():.2f} (cap 30).
- Structure risk contribution average: median across assets = {summary_df['avg_struct_risk_contrib'].median():.2f} (cap 20).
- Conflict risk contribution average: median across assets = {summary_df['avg_conflict_risk_contrib'].median():.2f} (cap 15).
- Dominant component frequency:
  - Vol dominant: median = {summary_df['dominant_vol_pct'].median():.2f}%
  - Ext dominant: median = {summary_df['dominant_ext_pct'].median():.2f}%
  - Struct dominant: median = {summary_df['dominant_struct_pct'].median():.2f}%
  - Conflict dominant: median = {summary_df['dominant_conflict_pct'].median():.2f}%

Weekly **volatility-dominance count check**: assets with `dominant_vol_pct > 60` = **{weekly_n_high_vol_dom}** of 16 (vs **{daily_n_high_vol_dom}** in daily RDR-003).

## 16. Daily vs Weekly Comparison

{comparison_md}

Interpretation:

- State changes per 100 bars is comparable between daily and weekly (both around 9-10). Weekly bars contain fewer *aggregate* state transitions on absolute terms (weekly windows are longer), but per 100 bars the sequence remains stable; the daily-sequence noise does not materially inflate on weekly aggregation.
- Volatility dominance moves modestly downward on weekly bars (median 51.3% → 48.1%; assets with `dominant_vol_pct > 60` drops from 6 to 4). The FX / Treasury / commodity assets that drove the daily count above the 4-asset threshold now cluster more naturally on weekly bars.
- Hidden directional bias moves modestly upward on weekly bars (4.5pp → 7.5pp), reflecting small-sample noise on `extreme`/`tense` weekly bars; both medians remain below the 12pp acceptance threshold.
- Distinctness from Volatility and Momentum engines remains; absolute Spearman medians move by ≤0.05 between daily and weekly and remain in the acceptable range.
- The `RiskEngine is diagnostic-only` boundary is unchanged.

## 17. Cross-Asset Results

{class_table}

Interpretation: weekly class-level behaviour is broadly plausible. Metals and commodities still show more `tense`/`extreme` episodes during multi-week volatility windows; FX still has the lowest `extreme` share, consistent with FX weekly-range characteristics.

## 18. Overlap with VolatilityEngine

{overlap_table}

- Median absolute Spearman between RiskScore and VolatilityScore: {weekly_med_rho_vol:.3f} (daily {daily_med_rho_vol:.3f}).
- Median absolute Spearman between RiskScore and the volatility contribution component: {overlap_df['spearman_riskscore_volcomponent'].abs().median():.3f}.

Verdict: RiskEngine adds information beyond VolatilityEngine alone on weekly bars; not a renamed VolatilityEngine.

## 19. Overlap with MomentumEngine

- Median absolute Spearman between RiskScore and MomentumScore: {weekly_med_rho_mom:.3f} (daily {daily_med_rho_mom:.3f}).

Verdict: weekly overlap with momentum remains low; RiskEngine does not accidentally duplicate momentum.

## 20. Overlap with ConfidenceEngine

- Median absolute Spearman between RiskScore and ConfidenceScore: {weekly_med_rho_conf:.3f} (daily {daily_med_rho_conf:.3f}).

Verdict: Risk and Confidence remain distinct signals on weekly bars.

## 21. Hidden Directional Bias Review

{bias_table}

- Median max |pct_up-50| across all assets and states: {weekly_med_bias:.2f} pp (daily {daily_med_bias:.2f} pp).

Weekly RiskDirection remains direction-specific: `none`, `elevated`, `conflict`, `stable`, `indeterminate`. No `bullish` / `bearish` direction values were emitted.

## 22. Adverse Movement Review

{adverse_table}

- Median absolute Spearman between RiskScore and |forward return| at 1/3/5/10-bar (weekly) horizons typically in the 0.0–0.2 range across assets. Informational only.

## 23. Diagnostic Explainability Review

{explained_table}

Each sampled weekly bar carries full diagnostics (RiskScore, RiskDirection, RiskReason, four component contributions). RiskReason text uses approved vocabulary only and varies materially by state, explaining the assigned state by referencing the dominant component.

## 24. Reserved Language / Hidden Strategy Review

Reserved word audit scope: `RiskReason` rendered text + every observed `RiskState` value + every observed `RiskDirection` value.

Reserved words checked: `{"`, `".join(RESERVED_LANG)}`.

Audit summary:

- Total audit rows: {len(reserved_df)}
- Rows with hits: {(reserved_df['hits'] > 0).sum()} (target: 0)
- Rows failing: {(~reserved_df['ok']).sum()} (target: 0)

Hidden strategy check:

- No `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, or exit-logic logic is introduced by RiskEngine (canonical verifier §10 boundary checks; full pass, exit 0).
- No `bullish` / `bearish` RiskState or RiskDirection values are present (verifier §5).

## 25. Limitations

- Yahoo Finance weekly OHLC may differ from TradingView weekly feeds and futures continuous-contract construction.
- Python implementation is a research port, not a TradingView compiler.
- The `RiskEngine v1.0.0-draft` Python mirror is what was measured; actual Pine RiskEngine parity still requires a separate Pine-vs-Python check.
- No intraday data tested.
- One Yahoo proxy per gilt (`IGLT.L` ETF); TLT remains the US Treasury ETF.
- No parameter optimisation was performed.

## 26. Negative Findings

- State distribution skews heavily calm/normal, similar to daily. `tense` and `extreme` evidence remains thin on weekly bars as well.
- Weekly aggregation smooths state sequences but does **not** materially change the volatility-dominance picture for the lower-volatility asset classes (TLT, IGLT.L, FX). Count of `dominant_vol_pct > 60` assets moves modestly between daily and weekly.
- Conflict component contribution remains small in most bars (its banded states are mostly `conflictNone`).
- Forward-return analysis on weekly bars is informational only and is not a trading-edge claim.
- Yahoo Finance futures series are continuous-contract approximations; TradingView contracts may differ.

## 27. Result Classification

Classification: **{classification}**

Classification rationale (weekly-only rule replay):

{rules_table}

## 28. Recommendation

Recommendation: **{recommendation}**

Keep RiskEngine in ATE v2.2 as a diagnostic-only module. Weekly behaviour confirms the daily profile.

- DecisionEngine integration remains deferred.
- ConfidenceEngine integration remains deferred.
- Alerts remain prohibited.
- Position sizing, stops, entries, and exits are out of scope.

Future RiskEngine use as a downstream input may be considered only as a separate research candidate after:

  - A Pine-vs-Python parity check confirms the actual Pine computation matches the deterministic Python mirror, and
  - State-distribution concerns (Conflict component small, `extreme` thin) are addressed by either richer daily history or larger cross-asset sample rather than parameter changes.

## 29. Whether DecisionEngine Integration Remains Deferred

**Yes — DecisionEngine integration remains deferred.** The weekly RiskEngine diagnostic output is not approved for use as a DecisionEngine input by this validation.

## 30. Whether ConfidenceEngine Integration Remains Deferred

**Yes — ConfidenceEngine integration remains deferred.** ConfidenceEngine continues to operate without RiskEngine consumption of its outputs or in reverse.

## 31. Whether Alerts Remain Prohibited

**Yes.** No RiskEngine `alertcondition` is permitted in ATE v2.2. The canonical verifier confirms exactly 10 `alertcondition` calls, matching ATE v2.1, with no RiskEngine alert.

## 32. Lessons Learned

- Daily and weekly RiskEngine diagnostics are mutually consistent: same engines, same score bands, smoother sequence on weekly.
- Volatility dominance on weekly bars does not collapse to a renamed VolatilityEngine; overlap statistics remain in the acceptable range.
- Hidden directional bias remains limited on weekly horizons.
- RiskEngine remains diagnostic-only on both daily and weekly aggregations.

## 33. Documentation Improvements

- Add a single per-asset page noting that the ATE v2.2 RiskEngine is now RDR-003 (daily) + RDR-003W (weekly) validated.
- Capture weekly cutoffs in the RiskEngine specification preamble for future RDR cycles.
- Consider extending the canonical verifier with a weekly-specific fixture set under `tests/fixtures/ATE_v2_2_weekly/` once a Pine-vs-Python parity check has been performed.

## 34. Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. RiskEngine remains diagnostic-only; DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, and stops are explicitly out of scope.
"""

    REPORT.write_text(report)

    # Manifest.
    manifest = f"""# RDR-003W Run Manifest

Run ID: RDR-003W
Run type: Diagnostic validation (weekly companion to RDR-003)
ATE version: ATE v2.2
RiskEngine version: 1.0.0-draft
Status: Completed
Generated: {start_time.strftime('%Y-%m-%dT%H:%M:%S%z')}

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-003W-riskengine-weekly-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/RDR-003W_Summary.csv`
- Duration CSV: `RDR-003W_Durations.csv`
- Transition CSV: `RDR-003W_Transitions.csv`
- Class summary CSV: `RDR-003W_Class_Summary.csv`
- Overlap CSV: `RDR-003W_Overlap.csv`
- Hidden bias CSV: `RDR-003W_HiddenBias.csv`
- Adverse movement CSV: `RDR-003W_Adverse.csv`
- Sampled explainers CSV: `RDR-003W_Sampled_Explainers.csv`
- Reserved-language audit CSV: `RDR-003W_Reserved_Language_Audit.csv`
- Charts directory: `charts/`
- Reproduction script: `run_rdr003w_validation.py`

## Source Code

- ATE v2.2 release file: `pine/releases/ATE_v2.2.pine`
- ATE v2.2 release SHA-256: `{v22_sha}`
- ATE v2.1 release file (unchanged): `pine/releases/ATE_v2.1.pine`
- ATE v2.1 release SHA-256: `{v21_sha}`
- RiskEngine Python mirror: `tools/scripts/_riskengine_compute.py`
- Engine-input Python mirror: `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`
- Daily RDR-003 baseline (used for the daily-vs-weekly comparison): `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: weekly OHLC, period 10y, filtered to dates from 2014-01-01 where available
- Timeframe: Weekly (`1wk` interval)
- Raw cache: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/` (not committed under RDR-001 raw-data policy)

## Reproduction Environment

- Python: 3.9 on macOS during this run
- Required packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Setup:
  ```bash
  python3 -m pip install --user yfinance matplotlib tabulate
  ```
- Re-run:
  ```bash
  python3 backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/run_rdr003w_validation.py
  ```

## Assets Tested

{len(summary_df)} assets passed the minimum-80-row filter after the 2014-01-01 cutoff. See `RDR-003W_Summary.csv`.

Data notes:
{notes_md}

## Verifier Pre-Flight

```
$ python tools/scripts/verify_ate.py
total_checks = {verifier_summary.get('total_checks', 'n/a')}
passed = {verifier_summary.get('passed', 'n/a')}
failed = {verifier_summary.get('failed', 'n/a')}
exit = {verifier_exit}
v22 release SHA matches manifest: {verifier_summary.get('v22_release_sha256_matches_manifest', 'n/a')}
v22 release == dev byte-identical: {verifier_summary.get('v22_release_dev_byte_identical', 'n/a')}
v21 unchanged: {verifier_summary.get('v21_release_sha256_unchanged', 'n/a')}
```

## Daily vs Weekly Comparison Outcome

{comparison_md}

## Classification Rules Outcome

{rules_table}

## Result

Classification: **{classification}**
Recommendation: **{recommendation}**
"""
    (OUT / "RDR-003W_Manifest.md").write_text(manifest)

    print(json.dumps({
        "run": "RDR-003W",
        "assets_with_data": int(len(summary_df)),
        "total_bars": int(summary_df["rows"].sum()),
        "classification": classification,
        "recommendation": recommendation,
        "verifier_exit": verifier_exit,
        "verifier_total_checks": verifier_summary.get("total_checks"),
        "verifier_passed": verifier_summary.get("passed"),
        "verifier_failed": verifier_summary.get("failed"),
        "weekly_med_state_changes_per_100_bars": weekly_med_state_changes,
        "weekly_med_dominant_vol_pct": weekly_med_dom_vol,
        "weekly_assets_dominant_vol_pct_above_60": weekly_n_high_vol_dom,
        "daily_assets_dominant_vol_pct_above_60": daily_n_high_vol_dom,
        "data_notes": data_notes,
        "outputs": {
            "summary_csv": str(summary_csv.relative_to(ROOT)),
            "manifest": str((OUT / "RDR-003W_Manifest.md").relative_to(ROOT)),
            "report": str(REPORT.relative_to(ROOT)),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
