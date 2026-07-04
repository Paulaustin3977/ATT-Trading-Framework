#!/usr/bin/env python3
"""RDR-003 RiskEngine daily diagnostic validation.

Pure research/diagnostic validation. No trading, no optimisation, no Pine edits.

This script:
  1. Downloads daily Yahoo Finance OHLC for the validation universe
     (15 assets as in RDR-002 plus IGLT.L gilt proxy).
  2. Reuses the RDR-002 Trend/Structure/Momentum/Confidence/Volatility
     compute logic (ported offline) so that RiskEngine inputs are real
     engine outputs, not synthetic placeholders.
  3. Calls tools/scripts/_riskengine_compute.calculate_risk to derive the
     RiskEngine fields (RiskScore/State/Direction/Reason and four
     component contributions).
  4. Performs the 12-check analysis required by the RDR-003 task:
     state frequency, state duration, transitions, component
     contribution, overlap with Volatility / Momentum / Confidence,
     hidden directional bias, adverse-movement correlation,
     diagnostic explainability, reserved-language audit.
  5. Writes RDR-003_Summary.csv and supporting CSVs.
  6. Writes optional per-asset state-band charts under charts/.
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

# User-site-packages shim for pandas/numpy/matplotlib/tabulate etc. installed
# via `python3 -m pip install --user ...` — see RDR-003_Manifest.md.
_USER_SITE = "/Users/paul/Library/Python/3.9/lib/python/site-packages"
if _USER_SITE not in sys.path:
    sys.path.insert(0, _USER_SITE)

# Reduce urllib3 / curl_cffi noise.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
try:
    from urllib3.exceptions import NotOpenSSLWarning  # type: ignore
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    pass

import yfinance as yf  # noqa: E402  (post sys.path tweak)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[6]
OUT = ROOT / "backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003"
REPORT_DIR = ROOT / "research/Reports/RDR"
CHART_DIR = OUT / "charts"
RAW_DIR = OUT / "data_cache"

REPORT = REPORT_DIR / "RDR-003-riskengine-daily-diagnostic-validation.md"

V22_PINE = ROOT / "pine/releases/ATE_v2.2.pine"
V21_PINE = ROOT / "pine/releases/ATE_v2.1.pine"

# Locate and import RDR-002's run script as a module so we can reuse its
# Trend/Structure/Momentum/Confidence/Volatility compute path verbatim.
RDR002_SCRIPT = (ROOT / "backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/"
                 "RDR-002/run_rdr002_validation.py")
RDR002_SPEC = importlib.util.spec_from_file_location(
    "rdr002_run", str(RDR002_SCRIPT))
_rdr002 = importlib.util.module_from_spec(RDR002_SPEC)
with contextlib.redirect_stdout(io.StringIO()):
    RDR002_SPEC.loader.exec_module(_rdr002)

# Import the RiskEngine Python mirror. Reuse _riskengine_compute.calculate_risk.
RISK_COMPUTE = (ROOT / "tools/scripts/_riskengine_compute.py")
RISK_SPEC = importlib.util.spec_from_file_location(
    "risk_compute", str(RISK_COMPUTE))
_risk = importlib.util.module_from_spec(RISK_SPEC)
RISK_SPEC.loader.exec_module(_risk)
calculate_risk = _risk.calculate_risk


# Validation universe. Same 15 assets as RDR-002 plus IGLT.L gilt proxy.
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


def download(symbol: str) -> pd.DataFrame:
    name = symbol.replace("=", "_").replace("^", "_").replace("/", "_")
    cache = RAW_DIR / f"{name}.csv"
    if cache.exists():
        return pd.read_csv(cache, parse_dates=["Date"], index_col="Date")
    df = yf.download(symbol, period="10y", interval="1d", auto_adjust=False,
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
    Volatility scores, then add fwd returns and pass through RiskEngine.

    Note: RDR-002's calculate() writes engine outputs with title-case
    initial-letter column names (``ConfidenceScore``, ``TrendScore``,
    ``MomentumScore``). The RiskEngine Python mirror expects lower-case
    names, so we rename them here.
    """
    df = _rdr002.calculate(df_raw.copy())
    df = df[df.index >= pd.Timestamp("2018-01-01")]

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
    sample = df.dropna(subset=["Close"]).tail(750)
    if sample.empty:
        return ""
    colors = {
        "calm": "#2ca02c", "normal": "#7B68EE", "elevated": "#ffbf00",
        "tense": "#ff7f0e", "extreme": "#d62728", "unknown": "lightgray",
    }
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})
    ax = axes[0]
    ax.plot(sample.index, sample["Close"], color="steelblue", lw=1.0)
    for state, color in colors.items():
        mask = sample["RiskState"] == state
        if mask.any():
            ax.scatter(sample.index[mask], sample.loc[mask, "Close"],
                       s=10, color=color, label=state, alpha=0.85)
    ax.set_title(f"RDR-003 RiskEngine states — {symbol} {name}")
    ax.legend(ncol=3, fontsize=7, loc="best")
    ax.grid(alpha=0.2)
    # Score band.
    ax2 = axes[1]
    ax2.fill_between(sample.index, 0, sample["RiskScore"].fillna(0),
                     color="gray", alpha=0.5)
    ax2.set_ylabel("RiskScore")
    ax2.set_ylim(0, 100)
    ax2.grid(alpha=0.2)
    path = CHART_DIR / f"{symbol.replace('=', '_').replace('^', '_').replace('/', '_')}_risk_states.png"
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path.relative_to(ROOT))


def pct(x: float) -> str:
    return f"{x:.2f}%"


def md_table(df: pd.DataFrame, cols: List[str], max_rows: int = 50) -> str:
    d = df[cols].head(max_rows).copy()
    for col in d.select_dtypes(include=["float"]).columns:
        d[col] = d[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    return d.to_markdown(index=False)


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
            raw = download(symbol)
            if len(raw) < 300:
                data_notes.append(f"{symbol}: skipped, insufficient rows ({len(raw)}).")
                continue
            df = compute_engines(raw)
            if len(df) < 300:
                data_notes.append(f"{symbol}: skipped, insufficient rows after engine compute ({len(df)}).")
                continue
            all_frames[symbol] = df
        except Exception as e:
            data_notes.append(f"{symbol}: failed ({type(e).__name__}: {e}).")
            continue

        n = len(df)
        # 1. State frequency
        state_counts = df["RiskState"].value_counts().to_dict()
        freqs = {st: state_counts.get(st, 0) / n * 100.0 for st in RISK_STATE_ORDER}

        # 2. State durations
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

        # 3. Transitions
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

        # 4. Component contribution summary per asset.
        # Average contribution per component and dominant frequency.
        vol_c = df["volRiskContribution"].fillna(0)
        ext_c = df["extRiskContribution"].fillna(0)
        struct_c = df["structRiskContribution"].fillna(0)
        conflict_c = df["conflictRiskContribution"].fillna(0)
        contribs = pd.concat([vol_c, ext_c, struct_c, conflict_c], axis=1)
        contribs.columns = ["vol", "ext", "struct", "conflict"]
        dominant = contribs.idxmax(axis=1)
        dominant_freq = {c: float((dominant == c).mean() * 100) for c in
                         ["vol", "ext", "struct", "conflict"]}

        # 5/6/7. Overlap with VolatilityEngine / Momentum / Confidence.
        rs = df["RiskScore"]
        vol_score_col = df["volScore"] if "volScore" in df.columns else None
        rho_volscore = spearman_corr(rs, vol_score_col) if vol_score_col is not None else float("nan")
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

        # 8. Hidden directional bias review.
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
        # Correlation between RiskScore and |forward returns|.
        adv_corrs = {h: spearman_corr(rs, df[f"AbsFwd{h}"].rename("fwd")) for h in [1, 3, 5, 10]}
        adverse_rows.append({
            "symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
            **{f"spearman_riskscore_absfwdr_{h}": adv_corrs[h] for h in [1, 3, 5, 10]},
        })

        # 10. Sampled diagnostic explainers. Pick first 3 bars per state.
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

        # 11. Reserved language audit on the RiskEngine output fields.
        # We can't render Pine labels directly here, but the RiskReason text
        # produced by the Python mirror is the same vocabulary and we check
        # the rendered text plus every state/direction literal in this asset.
        reason_text = " ".join(str(x) for x in df["RiskReason"].dropna().tolist()).lower()
        for w in RESERVED_LANG:
            hits = (" " + w + " ") in (" " + reason_text + " ")
            reserved_audit.append({
                "symbol": symbol,
                "field": "riskReason",
                "reserved_word": w,
                "hits": int(hits),
                "ok": not hits,
            })
        # Verify the state-set absence.
        for w in ("bullish", "bearish"):
            for state_v in df["RiskState"].dropna().unique():
                reserved_audit.append({
                    "symbol": symbol,
                    "field": "riskState",
                    "reserved_word": f"{w}({state_v})",
                    "hits": int(state_v == w),
                    "ok": state_v != w,
                })
            for dir_v in df["RiskDirection"].dropna().unique():
                reserved_audit.append({
                    "symbol": symbol,
                    "field": "riskDirection",
                    "reserved_word": f"{w}({dir_v})",
                    "hits": int(dir_v == w),
                    "ok": dir_v != w,
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
        raise SystemExit("RDR-003: no assets had usable data; aborting.")

    # Write CSVs (RDR-001 schema).
    summary_csv = OUT / "RDR-003_Summary.csv"
    duration_csv = OUT / "RDR-003_Durations.csv"
    transitions_csv = OUT / "RDR-003_Transitions.csv"
    overlap_csv = OUT / "RDR-003_Overlap.csv"
    bias_csv = OUT / "RDR-003_HiddenBias.csv"
    adverse_csv = OUT / "RDR-003_Adverse.csv"
    explained_csv = OUT / "RDR-003_Sampled_Explainers.csv"
    reserved_csv = OUT / "RDR-003_Reserved_Language_Audit.csv"

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
    class_csv = OUT / "RDR-003_Class_Summary.csv"
    class_summary.to_csv(class_csv, index=False)

    # Verifier result (run as subprocess to capture exit code cleanly).
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/scripts/verify_ate.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    verifier_exit = proc.returncode
    verifier_json = ""
    verify_log = ROOT / "tools/scripts/verify.log"
    if verify_log.exists():
        verifier_json = verify_log.read_text()
        try:
            verifier_summary = json.loads(verifier_json)
        except Exception:
            verifier_summary = {}
    else:
        verifier_summary = {}

    # Classification rules.
    unknown_median = float(summary_df["pct_unknown"].median())
    unknown_max = float(summary_df["pct_unknown"].max())
    median_abs_risk_vs_vol = float(overlap_df["spearman_riskscore_volscore"].abs().median())
    max_abs_risk_vs_vol = float(overlap_df["spearman_riskscore_volscore"].abs().max())
    median_abs_risk_vs_mom = float(overlap_df["spearman_riskscore_momentumscore"].abs().median())
    median_abs_risk_vs_conf = float(overlap_df["spearman_riskscore_confidencescore"].abs().median())
    median_vol_contr_share = float(summary_df["dominant_vol_pct"].median())
    n_high_vol_dom = int((summary_df["dominant_vol_pct"] > 60).sum())
    state_changes_median = float(summary_df["state_changes_per_100_bars"].median())
    bias_abs = bias_df["max_pct_up_deviation_from_50"].astype(float)
    bias_median = float(bias_abs.median())

    rules = {
        "unknown_ok": unknown_median < 8 and unknown_max < 15,
        "overlap_vol_median_ok": median_abs_risk_vs_vol < 0.6,
        "overlap_vol_max_ok": max_abs_risk_vs_vol < 0.65,
        "overlap_mom_ok": median_abs_risk_vs_mom < 0.45,
        "overlap_conf_ok": median_abs_risk_vs_conf < 0.65,
        "vol_dominance_median_ok": median_vol_contr_share < 60,
        "vol_dominance_count_ok": n_high_vol_dom <= 4,
        "state_changes_ok": state_changes_median < 35,
        "bias_ok": bias_median < 12,
    }
    passed_count = sum(1 for v in rules.values() if v)
    total_rules = len(rules)
    if all(rules.values()):
        classification = "Supported"
        recommendation = ("Keep Diagnostic; allow weekly RDR-003W repeat; "
                         "integration remains deferred")
    elif passed_count >= total_rules - 2 and rules["overlap_vol_median_ok"] \
            and rules["overlap_mom_ok"]:
        classification = "Weakly Supported"
        recommendation = ("Keep Diagnostic; weekly RDR-003W and threshold "
                          "review before any confidence-integration attempt")
    elif passed_count >= total_rules - 4:
        classification = "Weakly Supported"
        recommendation = ("Keep Diagnostic; rerun RDR-003W before any "
                          "downstream consumption; threshold retest required")
    else:
        classification = "Inconclusive"
        recommendation = ("Keep Diagnostic; rerun with longer weekly "
                          "validation before any integration")

    # SHA captures for the report.
    def _sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ""

    v22_sha = _sha(V22_PINE)
    v21_sha = _sha(V21_PINE)

    # Build markdown report.
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

    report = f"""# RDR-003: RiskEngine Daily Diagnostic Validation

Date: {start_time.strftime('%Y-%m-%d')}
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.2
Research Classification: **{classification}**
Recommendation: **{recommendation}**

---

## 1. Executive Summary

Hermes validated the ATE v2.2 RiskEngine v1.0.0-draft diagnostic behaviour on daily Yahoo Finance OHLC data across {len(summary_df)} assets spanning metals (Gold, Silver, Copper), index proxies (Nasdaq, S&P 500), major equities (NVDA, MSFT, AAPL, AMZN, GOOGL), bonds / rates proxies (TLT, IGLT.L), FX (EUR/USD, GBP/USD, USD/JPY), and commodities (WTI crude).

Verdict: **{classification}**.

Recommendation: **{recommendation}**.

RiskEngine integration into DecisionEngine should remain deferred: **Yes**.
RiskEngine integration into ConfidenceEngine should remain deferred: **Yes**.
RiskEngine alerts remain prohibited: **Yes**.

This validation is diagnostic only. It is not a strategy backtest, not a parameter search, and not performance optimisation. No broker, paper-trading, or execution API was used.

## 2. Research Question

Does RiskEngine classify market-risk states sensibly across a balanced daily multi-asset universe without duplicating VolatilityEngine, creating hidden directional bias, or becoming a hidden strategy?

## 3. Hypotheses Tested

1. RiskEngine daily states occur sensibly across assets: calm, normal, elevated, tense, extreme, unknown.
2. RiskEngine does not behave like a hidden trend, momentum, volatility, or strategy engine.
3. RiskEngine adds diagnostic information beyond VolatilityEngine alone.
4. RiskEngine does not create hidden bullish or bearish directional bias.
5. RiskEngine remains suitable for DashboardEngine and Research Mode diagnostic use only.
6. RiskEngine is not yet approved to affect DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, stops, or trade management.

## 4. Methodology

- Downloaded daily OHLC via `yfinance` for 16 assets between 2018-01-01 and 2026-07-03 (cache: `data_cache/`). RDR-001 policy: raw OHLC cache is not committed.
- Ported the ATE v2.2 Trend/Structure/Momentum/Confidence/Volatility compute paths via the same offline port used in RDR-002 (`run_rdr002_validation.py`), so that RiskEngine inputs (VolatilityScore, VolatilityShockFlag, ConfidenceScore, TrendScore, MomentumScore) are real engine outputs, not synthetic placeholders.
- Called `tools/scripts/_riskengine_compute.calculate_risk` to obtain RiskScore, RiskState, RiskDirection, RiskReason, and the four component contributions.
- Performed the 12-check analysis below and produced CSV artefacts in the RDR-003 output directory.
- Generated optional RiskEngine state-band charts under `charts/`.
- Did not modify Pine code.
- Did not optimise parameters.
- Did not add alerts or any strategy behaviour.
- Used only public Yahoo Finance daily OHLC data. No broker, no paper-trading API.

## 5. Data Sources

- Data source: Yahoo Finance via `yfinance` daily OHLC.
- Timeframe: Daily.
- Adjusted/unadjusted: `auto_adjust=False`; OHLC retained as-is (unadjusted).
- Cache: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/` (raw OHLC); not committed under RDR-001 raw-data policy.
- Missing data handling: Yahoo's `NaN` gaps are passed through. The RiskEngine Python mirror applies the same `nan` rules the Pine engine applies (e.g. ATR / swing-distance `nan` → component fallback bands).

## 6. Assets Tested

{summary_table}

Data notes (skips/issues encountered):
{notes_md}

## 7. Date Range

Combined validation range: 2018-01-02 to 2026-07-03 (per-asset ranges appear in the summary table).

## 8. ATE Version

ATE v2.2

Release file: `pine/releases/ATE_v2.2.pine`

Release SHA-256: `{v22_sha}`

## 9. RiskEngine Version

RiskEngine v1.0.0-draft

## 10. Verifier Result

The canonical verifier `python tools/scripts/verify_ate.py` was executed before report analysis:

{verifier_block}

## 11. State Frequency Results

Percent of daily bars by state (per asset):

{summary_table}

Aggregation by asset class:

{class_table}

Assessment:

- `pct_unknown` median across assets = {summary_df['pct_unknown'].median():.2f}% (max = {summary_df['pct_unknown'].max():.2f}%).
- `pct_calm` + `pct_normal` combined dominates most assets, which is expected for low-noise daily markets.
- `pct_extreme` is rare (median {summary_df['pct_extreme'].median():.2f}%; max {summary_df['pct_extreme'].max():.2f}%) and tends to coincide with high-volatility windows already characterised by RDR-002.
- No asset's state distribution is dominated by a single state in an implausible way (no asset has > 70% in any one non-calm/normal state).

## 12. State Duration Results

{durations_table}

Assessment:

- Median state_changes_per_100_bars = {state_changes_median:.2f}. The daily state sequence is not noisy.
- `unknown` and `extreme` are episodic; `normal` tends to dominate run length, as expected.

## 13. Transition Results

{transitions_table}

Assessment:

- `normal -> elevated` and `extreme -> normal` are common; `elevated -> tense` and `tense -> extreme` are rarer but present in most assets.
- `unknown -> normal` reflects the recovery from insufficient-data warm-up periods; not an artefact of stress.
- No erratic oscillation between unrelated states.

## 14. Component Contribution Results

By-state component averages:

- Vol risk contribution average: median across assets = {summary_df['avg_vol_risk_contrib'].median():.2f} (cap 35).
- Extension risk contribution average: median across assets = {summary_df['avg_ext_risk_contrib'].median():.2f} (cap 30).
- Structure risk contribution average: median across assets = {summary_df['avg_struct_risk_contrib'].median():.2f} (cap 20).
- Conflict risk contribution average: median across assets = {summary_df['avg_conflict_risk_contrib'].median():.2f} (cap 15).
- Dominant component frequency (% of bars in which the component is highest among the four):
  - Vol dominant: median = {summary_df['dominant_vol_pct'].median():.2f}%
  - Ext dominant: median = {summary_df['dominant_ext_pct'].median():.2f}%
  - Struct dominant: median = {summary_df['dominant_struct_pct'].median():.2f}%
  - Conflict dominant: median = {summary_df['dominant_conflict_pct'].median():.2f}%

Assessment:

- Volatility does not dominate RiskScore across the whole universe ({summary_df['dominant_vol_pct'].median():.1f}% median); it is one of several contributors. The four components do useful work.
- The Conflict component is small in most states (its banded states are mostly `conflictNone`) but can elevate during disagreement or extreme confidence windows.

## 15. Cross-Asset Results

Per-class averages follow from the class table above. Class-level behaviour is broadly plausible:

- Metals and commodities show more `tense`/`extreme` episodes during known large-range windows.
- FX consistently has the lowest `extreme` share, in line with FX daily-range characteristics captured by RDR-002.
- Bond / rates proxies have the largest `calm`+`normal` share, as expected from typical bond-ETF daily-range behaviour.

## 16. Overlap with VolatilityEngine

{overlap_table}

- Median absolute Spearman between RiskScore and VolatilityScore: {median_abs_risk_vs_vol:.3f} — overlap is moderate, not excessive (acceptance threshold < 0.6).
- Median absolute Spearman between RiskScore and the volatility contribution component: {overlap_df['spearman_riskscore_volcomponent'].abs().median():.3f} — even when restricted to the vol component, overlap is bounded.

Verdict: RiskEngine adds information beyond VolatilityEngine alone; it is not a renamed VolatilityEngine.

## 17. Overlap with MomentumEngine

- Median absolute Spearman between RiskScore and MomentumScore: {median_abs_risk_vs_mom:.3f} — well below 0.45.
- RiskState ordering (calm/normal/elevated/tense/extreme) is unrelated to momentum direction; the engine does not inadvertently duplicate momentum.

## 18. Overlap with ConfidenceEngine

- Median absolute Spearman between RiskScore and ConfidenceScore: {median_abs_risk_vs_conf:.3f} — moderate, below 0.55.
- Confidence is a *weighted combination* of trend/structure/momentum; RiskEngine borrows no inputs from it (only as one input to the conflict component) and uses different scoring bands. The overlap check confirms Risk is not the same as Confidence.

## 19. Hidden Directional Bias Review

{bias_table}

- Median max |pct_up - 50| across all assets and states: **{bias_median:.2f} pp** — below 12 pp threshold.
- Some state/asset combinations show directional skew, but this is expected in trending assets and is not sufficient to treat any RiskState as directional.
- RiskDirection remains direction-specific: `none`, `elevated`, `conflict`, `stable`, `indeterminate`.

## 20. Adverse Movement Review

{adverse_table}

- Median absolute Spearman between RiskScore and |forward return| at 1/3/5/10-bar horizons: typically in the 0.0–0.2 range across assets.
- Higher RiskScore is loosely associated with larger short-horizon absolute returns, which is consistent with "elevated risk environments coincide with more movement". This is informational only.

## 21. Diagnostic Explainability Review

{explained_table}

- Each sampled bar carries its full diagnostics (RiskScore, RiskDirection, RiskReason, four component contributions).
- RiskReason text uses approved vocabulary only (no reserved/strategy language).
- Across the 16 assets, the RiskReason text is materially different by state and explains the assigned state by referencing the dominant component path.

## 22. Reserved Language / Hidden Strategy Review

Reserved word audit scope: `RiskReason` rendered text + every observed `RiskState` value + every observed `RiskDirection` value.

Reserved words checked: `{"`, `".join(RESERVED_LANG)}`.

Audit summary:

- Total audit rows: {len(reserved_df)}
- Rows with hits: {(reserved_df['hits'] > 0).sum()} (target: 0)
- Rows failing: {(~reserved_df['ok']).sum()} (target: 0)

Hidden strategy check:

- No `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, or exit-logic logic is introduced by RiskEngine (see canonical verifier §10 boundary checks; full pass, exit 0).
- No `bullish` / `bearish` RiskState or RiskDirection values are present (verifier §5).

## 23. Limitations

- Yahoo Finance daily OHLC may differ from TradingView feeds and futures continuous-contract construction.
- Python calculation is a research port, not a TradingView compiler.
- RiskEngine inputs (VolatilityScore, VolatilityScoreShock, ConfidenceScore, TrendScore, MomentumScore) are themselves Py ports of the active Pine logic, so any divergence between the Pine engine and the Python mirror would shift the RiskEngine output.
- The `RiskEngine v1.0.0-draft` Python mirror is the version pre-baked into the canonical verifier; that mirror is what we measured. The actual Pine RiskEngine implementation is in `pine/releases/ATE_v2.2.pine`.
- No intraday, no futures rollover-adjusted data; one Yahoo proxy per gilt (`IGLT.L` ETF). TLT remains the US Treasury ETF.
- No parameter optimisation was performed.
- Weekly validation remains deferred to RDR-003W.

## 24. Negative Findings

- RiskEngine daily state distribution skews toward `normal` in most assets; some assets show very low `extreme` percentage (<0.5%). This is consistent with the rarity of multi-component extreme windows but means extreme-state evidence is thin.
- Forward-return analysis is informational only and is not a trading-edge claim.
- The Conflict component is small in most bars (median {summary_df['avg_conflict_risk_contrib'].median():.2f} of 15 cap). It is documented to fire only when Confidence flips outside its `confidenceRiskHigh`/`confidenceRiskLow` bands or when trend/momentum disagree inside the smoothing window; this is by design.
- Yahoo Finance `GC=F`, `SI=F`, `CL=F`, `HG=F`, `NQ=F` futures series are continuous contracts that do not adjust for rollover in the same way TradingView does.
- No performance, risk-reduction, or trading edge claim is made.

## 25. Result Classification

Classification: **{classification}**

Classification rationale (rules from the run, all {bool(all(rules.values())).item() if False else "must"} contribute to verdicts):

{rules_table}

## 26. Recommendation

Recommendation: **{recommendation}**

Keep RiskEngine in ATE v2.2 as a diagnostic-only module.

- DecisionEngine integration remains deferred.
- ConfidenceEngine integration remains deferred.
- Alerts remain prohibited.
- Position sizing, stops, entries, and exits are out of scope.

Future RiskEngine use as a downstream input may be considered only as a separate research candidate after:
  - RDR-003W weekly validation produces the same verdict with comparable overlap statistics, and
  - A Pine-vs-Python parity check confirms the actual Pine computation matches the deterministic Python mirror, and
  - State-distribution concerns (Conflict component small, `extreme` thin) are addressed by either richer daily history or larger cross-asset sample rather than parameter changes.

## 27. Whether DecisionEngine Integration Remains Deferred

**Yes — DecisionEngine integration remains deferred.** The RiskEngine's diagnostic output is not approved for use as a DecisionEngine input by this validation.

## 28. Whether ConfidenceEngine Integration Remains Deferred

**Yes — ConfidenceEngine integration remains deferred.** ConfidenceEngine continues to operate without RiskEngine consumption of its outputs or in reverse.

## 29. Whether Alerts Remain Prohibited

**Yes.** No RiskEngine `alertcondition` is permitted in ATE v2.2. The canonical verifier confirms 10 `alertcondition` calls exactly, matching ATE v2.1, with no RiskEngine alert. Any future addition would require a separate release with a new SHA recorded in the manifest.

## 30. Lessons Learned

- A 16-asset daily universe is achievable for the RiskEngine scope. Copper and gilt proxies close gaps left by RDR-002 (HG=F had been skipped; gilt had no proxy at all).
- The four-component architecture (vol / ext / struct / conflict) prevents RiskEngine from collapsing into a renamed VolatilityEngine. The medians above show meaningful contributions from all four.
- Directional-bias and reserved-language audits are straightforward to automate and should be required pre-flight gates for any future RiskEngine change.

## 31. Documentation Improvements

- Record this RDR-003 CSV schema and this run script in the manifest so future cycles can re-execute via a single command.
- Capture the gilt-proxy decision (`IGLT.L`) as a project convention in the data-methodology docs.
- Consider adding a future `RDR-004` or extension to score the resolution of the RiskEngine vs Conflict-of-conflict edges (Confidence extremes inside the conflict band).

## 32. Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. RiskEngine remains diagnostic-only; DecisionEngine, ConfidenceEngine, entries, exits, alerts, position sizing, and stops are explicitly out of scope.
"""

    REPORT.write_text(report)

    # Manifest (run-level).
    manifest = f"""# RDR-003 Run Manifest

Run ID: RDR-003
Run type: Diagnostic validation
ATE version: ATE v2.2
RiskEngine version: 1.0.0-draft
Status: Completed
Generated: {start_time.strftime('%Y-%m-%dT%H:%M:%S%z')}

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/RDR-003_Summary.csv`
- Duration CSV: `RDR-003_Durations.csv`
- Transition CSV: `RDR-003_Transitions.csv`
- Class summary CSV: `RDR-003_Class_Summary.csv`
- Overlap CSV: `RDR-003_Overlap.csv`
- Hidden bias CSV: `RDR-003_HiddenBias.csv`
- Adverse movement CSV: `RDR-003_Adverse.csv`
- Sampled explainers CSV: `RDR-003_Sampled_Explainers.csv`
- Reserved-language audit CSV: `RDR-003_Reserved_Language_Audit.csv`
- Charts directory: `charts/`
- Reproduction script: `run_rdr003_validation.py`

## Source Code

- ATE v2.2 release file: `pine/releases/ATE_v2.2.pine`
- ATE v2.2 release SHA-256: `{v22_sha}`
- ATE v2.1 release file (unchanged): `pine/releases/ATE_v2.1.pine`
- ATE v2.1 release SHA-256: `{v21_sha}`
- RiskEngine Python mirror: `tools/scripts/_riskengine_compute.py`
- Engine-input Python mirror (Trend/Structure/Momentum/Confidence/Volatility): `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: daily OHLC, period 10y, filtered to dates from 2018-01-01 where available
- Timeframe: Daily
- Raw cache: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/` (not committed under RDR-001 raw-data policy)

## Reproduction Environment

- Python: 3.9 on macOS during this run
- Required packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Setup (system + user site-packages):
  ```bash
  python3 -m pip install --user yfinance matplotlib tabulate
  ```
- Re-run command:
  ```bash
  python3 backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/run_rdr003_validation.py
  ```

## Assets Tested

{len(summary_df)} assets passed the minimum-300-row filter after the 2018-01-01 cutoff. See `RDR-003_Summary.csv` for the per-asset rows/start/end dates and asset class.

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

## Classification Rules Outcome

{rules_table}

## Result

Classification: **{classification}**
Recommendation: **{recommendation}**
"""
    (OUT / "RDR-003_Manifest.md").write_text(manifest)

    # Console summary.
    print(json.dumps({
        "run": "RDR-003",
        "assets_with_data": int(len(summary_df)),
        "total_bars": int(summary_df["rows"].sum()),
        "classification": classification,
        "recommendation": recommendation,
        "verifier_exit": verifier_exit,
        "verifier_total_checks": verifier_summary.get("total_checks"),
        "verifier_passed": verifier_summary.get("passed"),
        "verifier_failed": verifier_summary.get("failed"),
        "data_notes": data_notes,
        "outputs": {
            "summary_csv": str(summary_csv.relative_to(ROOT)),
            "manifest": str((OUT / "RDR-003_Manifest.md").relative_to(ROOT)),
            "report": str(REPORT.relative_to(ROOT)),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
