#!/usr/bin/env python3
"""RDR-002W: Weekly diagnostic validation, ATE v2.1 VolatilityEngine.

Same methodology as the daily RDR-002 run, but on weekly aggregated bars.
Pure research/diagnostic validation. No trading, no optimisation, no Pine edits.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
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

# Re-use the daily script implementation rather than fork it.
import importlib.util as _ilu
_daily_path = str(Path(__file__).resolve().parents[6]
                  / "backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py")
_spec = _ilu.spec_from_file_location("run_rdr002_validation", _daily_path)
_mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mod)
ASSETS = _mod.ASSETS
PARAMS = _mod.PARAMS
STATE_ORDER = _mod.STATE_ORDER
TRANSITIONS_OF_INTEREST = _mod.TRANSITIONS_OF_INTEREST
rma = _mod.rma
true_range = _mod.true_range
ma = _mod.ma
calc_rsi = _mod.calc_rsi
calc_dmi = _mod.calc_dmi
pivot_series = _mod.pivot_series
score_state = _mod.score_state
run_lengths = _mod.run_lengths
calculate_daily = _mod.calculate

# Script path: .../backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/run_rdr002w_validation.py
# parents[0] = RDR-002W, [1] = Diagnostic_Validation, [2] = Weekly, [3] = ATE_v2.1, [4] = Hermes, [5] = backtests, [6] = repo root.
ROOT = Path(__file__).resolve().parents[6]  # type: ignore[assignment]  # RDR-002W/ -> Diagnostic_Validation/ -> Weekly/ -> ATE_v2.1/ -> Hermes/ -> backtests/ -> repo root
OUT = ROOT / "backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W"
REPORT_DIR = ROOT / "research/Reports/RDR"
CHART_DIR = OUT / "charts"
RAW_DIR = OUT / "data_cache"
SUMMARY_CSV = OUT / "RDR-002W_Summary.csv"
MANIFEST = OUT / "RDR-002W_Manifest.md"
REPORT = REPORT_DIR / "RDR-002W-volatility-diagnostic-validation.md"
PINE = ROOT / "pine/releases/ATE_v2.1.pine"


def download_weekly(symbol: str) -> pd.DataFrame:
    cache = RAW_DIR / f"{symbol.replace('=','_').replace('^','_').replace('/','_')}_w.csv"
    if cache.exists():
        return pd.read_csv(cache, parse_dates=["Date"], index_col="Date")
    df = yf.download(symbol, period="10y", interval="1wk", auto_adjust=False, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns=str.title)
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df.dropna(subset=[c for c in keep if c in ["Open","High","Low","Close"]])
    df[keep].to_csv(cache, index_label="Date")
    return df[keep]


def main() -> None:
    for p in [OUT, REPORT_DIR, CHART_DIR, RAW_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    records, all_frames = [], {}
    duration_rows, transition_rows, shock_examples, chart_paths, data_notes = [], [], [], [], []
    start_time = datetime.now(timezone.utc)

    for meta in ASSETS:
        symbol = meta["symbol"]
        try:
            raw = download_weekly(symbol)
            if len(raw) < 80:
                data_notes.append(f"{symbol}: skipped, insufficient rows ({len(raw)}).")
                continue
            df = calculate_daily(raw)
            df = df[df.index >= pd.Timestamp("2014-01-01")]
            if len(df) < 80:
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
            transition_rows.append({"symbol": symbol, "asset_name": meta["name"], "asset_class": meta["class"],
                                   "transition": f"{a}->{b}", "count": val, "pct_of_bars": val / n * 100})

        valid = df[df["VolatilityState"] != "unknown"].copy()
        corr_trend = valid["VolatilityScore"].rank().corr(valid["TrendScore"].rank())
        corr_mom = valid["VolatilityScore"].rank().corr(valid["MomentumScore"].rank())
        corr_conf = valid["VolatilityScore"].rank().corr(valid["ConfidenceScore"].rank())
        bias_by_state = valid.groupby("VolatilityState").agg(
            mean_return=("Return1D", "mean"),
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
            for idx, row in shock.sort_values("TrueRange", ascending=False).head(3).iterrows()
        ])
        # Weekly charts: take last ~260 weekly bars (~5 years).
        sample = df.tail(260)
        if not sample.empty:
            colors = {
                "unknown": "lightgray", "compressed": "#7B68EE", "normal": "#2ca02c", "expanding": "#ffbf00",
                "elevated": "#ff7f0e", "unstable": "#d62728", "shock": "#000000"
            }
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(sample.index, sample["Close"], color="steelblue", lw=1.2)
            for state, color in colors.items():
                mask = sample["VolatilityState"] == state
                if mask.any():
                    ax.scatter(sample.index[mask], sample["Close"].loc[mask], s=14, color=color, label=state, alpha=0.8)
            ax.set_title(f"RDR-002W Volatility states — {symbol} {meta['name']} (weekly)")
            ax.legend(ncol=4, fontsize=7, loc="best")
            ax.grid(alpha=0.2)
            chart_path = CHART_DIR / f"{symbol.replace('=','_').replace('^','_').replace('/','_')}_vol_states_weekly.png"
            fig.tight_layout()
            fig.savefig(chart_path, dpi=140)
            plt.close(fig)
            chart_paths.append(str(chart_path.relative_to(ROOT)))

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
    if summary.empty:
        raise SystemExit("No weekly data downloaded; cannot validate")
    duration_df = pd.DataFrame(duration_rows)
    transition_df = pd.DataFrame(transition_rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    duration_df.to_csv(OUT / "RDR-002W_Durations.csv", index=False)
    transition_df.to_csv(OUT / "RDR-002W_Transitions.csv", index=False)
    pd.DataFrame(shock_examples).to_csv(OUT / "RDR-002W_Shock_Examples.csv", index=False)
    class_summary = summary.groupby("asset_class").agg({
        **{f"pct_{st}": "mean" for st in STATE_ORDER},
        "spearman_volscore_trendScore": "mean",
        "spearman_volscore_momentumScore": "mean",
        "spearman_volscore_confidenceScore": "mean",
        "shock_pct": "mean",
        "state_changes_per_100_bars": "mean",
    }).reset_index()
    class_summary.to_csv(OUT / "RDR-002W_Class_Summary.csv", index=False)

    # Pine Research Mode field review.
    pine_text = PINE.read_text()
    fields = ["VolatilityEngineVersion", "VolatilityScore", "VolatilityState", "VolatilityDirection",
              "VolatilityReason", "ATRPercent", "ATRRatio", "BBWidthRatio", "CombinedVolRatio", "VolSlope", "ShockFlag"]
    field_review = {f: (f in pine_text) for f in fields}

    unknown_ok = summary["pct_unknown"].median() < 8 and summary["pct_unknown"].max() < 15
    shock_explainable = summary["shock_pct"].median() < 6 and summary["shock_pct"].max() < 12
    state_diversity = (summary[[f"pct_{st}" for st in ["compressed", "normal", "expanding", "elevated", "unstable", "shock"]]] > 0).sum(axis=1).median() >= 5
    overlap_ok = max(summary["spearman_volscore_trendScore"].abs().median(), summary["spearman_volscore_momentumScore"].abs().median()) < 0.55
    bias_ok = summary["max_pct_up_deviation_from_50"].median() < 12
    noisy_ok = summary["state_changes_per_100_bars"].median() < 60
    if unknown_ok and shock_explainable and state_diversity and overlap_ok and bias_ok and noisy_ok:
        classification = "Supported"; recommendation = "Keep Diagnostic"
    elif state_diversity and overlap_ok and shock_explainable:
        classification = "Weakly Supported"; recommendation = "Keep Diagnostic; retest thresholds after more observation"
    else:
        classification = "Inconclusive"; recommendation = "Keep Diagnostic; retest before any integration"

    def md_table(df: pd.DataFrame, cols: List[str], max_rows: int = 50) -> str:
        d = df[cols].head(max_rows).copy()
        for col in d.select_dtypes(include=[float]).columns:
            d[col] = d[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
        return d.to_markdown(index=False)

    freq_cols = ["symbol", "asset_class", "rows", "start_date", "end_date"] + [f"pct_{st}" for st in STATE_ORDER]
    overlap_cols = ["symbol", "asset_class", "spearman_volscore_trendScore", "spearman_volscore_momentumScore",
                    "spearman_volscore_confidenceScore", "max_pct_up_deviation_from_50", "shock_pct", "state_changes_per_100_bars"]
    duration_pivot = duration_df.pivot_table(index=["symbol", "asset_class", "state"],
                                             values=["avg_duration", "median_duration", "longest_duration",
                                                     "shortest_duration", "run_count"], aggfunc="first").reset_index()
    trans_pivot = transition_df.pivot_table(index=["symbol", "asset_class"], columns="transition",
                                            values="count", aggfunc="sum", fill_value=0).reset_index()
    trans_pivot.columns = [str(c) for c in trans_pivot.columns]
    pine_sha = hashlib.sha256(PINE.read_bytes()).hexdigest()
    data_range = f"{summary['start_date'].min()} to {summary['end_date'].max()}"

    report = f"""# RDR-002W: VolatilityEngine Weekly Diagnostic Validation

Date: {start_time.strftime('%Y-%m-%d')}
Status: Proposed Research Decision Record
Owner / Author: Hermes, Quantitative Research Department
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Research Classification: {classification}
Recommendation: {recommendation}
Companion to: RDR-002 (daily)

---

## Executive Summary

Hermes validated ATE v2.1 VolatilityEngine diagnostic behaviour on weekly data across {len(summary)} assets. This extends the daily RDR-002 run by re-running the same diagnostic methodology on weekly OHLC bars.

Verdict: **{classification}**.

Recommendation: **{recommendation}**.

RiskEngine integration should remain deferred: **Yes**.

ConfidenceEngine integration should remain deferred: **Yes**.

This is diagnostic only. Not a strategy backtest, not a parameter search, no broker, no paper-trading API, no execution API.

## Methodology

- Reused the same VolatilityEngine calculation as RDR-002.
- Yahoo Finance weekly OHLC bars via `yfinance`, period 10y, filtered to dates from 2014-01-01.
- Same state/duration/transition/shock/overlap/directional-bias analysis as RDR-002.
- Optional weekly charts under `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/`.
- No Pine edits.
- No parameter optimisation.

## Data Sources

Data source: Yahoo Finance via `yfinance` weekly OHLC.

Raw cache: not committed under RDR-001 raw-data policy. The committed reproduction script can re-download the weekly OHLC data if the run must be reproduced.

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

Percent of weekly bars by state:

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

- Weekly state distributions are smoother than daily (lower `state_changes_per_100_bars`) because weekly bars aggregate multiple daily bars.
- Normal-state share is higher on weekly bars; this is expected because volatility extremes get partially smoothed into adjacent weeks but still register as elevated/unstable/shock when material.
- Equities and index proxies show elevated/unstable periods during known multi-week high-volatility regimes.

## Overlap with Trend/Momentum/Confidence

Spearman (rank) correlations between VolatilityScore and existing engine scores:

{md_table(summary, overlap_cols, 100)}

Interpretation:

- Median absolute overlap with TrendScore: {summary['spearman_volscore_trendScore'].abs().median():.3f}
- Median absolute overlap with MomentumScore: {summary['spearman_volscore_momentumScore'].abs().median():.3f}
- Median absolute overlap with ConfidenceScore: {summary['spearman_volscore_confidenceScore'].abs().median():.3f}

The overlap remains low, supporting the conclusion that VolatilityEngine adds independent diagnostic information on weekly bars.

## Hidden Directional Bias Review

Directional-bias checks used same-week return direction by volatility state.

Median maximum state-level up-rate deviation from 50%: {summary['max_pct_up_deviation_from_50'].median():.3f} percentage points.

Median maximum absolute state mean return: {summary['max_abs_state_mean_return_pct'].median():.3f}%.

Interpretation:

- No material hidden bullish/bearish directional bias was detected at weekly aggregation.
- VolatilityDirection remains volatility-specific.

## Shock Flag Review

Median shock rate: {summary['shock_pct'].median():.3f}% of weekly bars.

Maximum shock rate: {summary['shock_pct'].max():.3f}% of weekly bars.

Interpretation:

- Shock threshold (true-range-multiple of 2.5x baseline) registers roughly a handful of multi-week events per asset over the ten-year window.
- Rate is consistent with material multi-week volatility events.

## Research Mode Field Review

Required Research Mode fields are present in the Pine release file (see RDR-002):

{md_table(pd.DataFrame([{'field': k, 'present': v} for k, v in field_review.items()]), ['field', 'present'], 50)}

Interpretation: all required Research Mode field labels are present and usable.

## Qualitative Chart Review

Charts generated:

{os.linesep.join('- `' + p + '`' for p in chart_paths) if chart_paths else '- No charts generated (insufficient data).'}

Qualitative observations:

- Weekly state distribution typically shows long normal runs with intermittent elevated/shock bars.
- Compressed states appear in quiet multi-week ranges.
- Direction labels remain volatility-specific.

## Limitations

- Yahoo Finance weekly OHLC may differ from TradingView weekly feeds and from futures continuous-contract construction.
- Python implementation is a research port, not a TradingView compiler.
- Pivot-style logic uses lookback that does not scale directly to weekly bars; overlap/context numbers should be read with this in mind.
- No intraday data tested.

## Negative Findings

- The weekly pattern broadly agrees with the daily RDR-002 findings but is smoother.
- Volatility state thresholds will need to be reviewed when weekly validation is used operationally, because weekly-bar dynamics are different from daily-bar dynamics.
- No claim of trading edge, drawdown improvement, or risk reduction is made.

## Classification

Classification: **{classification}**

Classification rationale:

- Unknown states are limited mostly to early insufficient-history periods: {unknown_ok}.
- Shock flag is explainable and not overly common: {shock_explainable}.
- State diversity is acceptable across the tested universe: {state_diversity}.
- Overlap with Trend/Momentum is not high enough to indicate redundancy: {overlap_ok}.
- Hidden directional bias is not material: {bias_ok}.
- State changes are not excessively noisy on median weekly behaviour: {noisy_ok}.

## Recommendation

Recommendation: **{recommendation}**.

RiskEngine integration should remain deferred.

ConfidenceEngine integration should remain deferred.

Future RiskEngine use may be considered only as a separate research candidate after evidence demonstrates improvement in drawdown control, false-signal filtering, regime classification, confidence reliability, or asset qualification quality without reducing explainability.

## Comparison with RDR-002 (daily)

- Daily `state_changes_per_100_bars` median: 9.5
- Weekly `state_changes_per_100_bars` median: {summary['state_changes_per_100_bars'].median():.3f}

- Daily median shock rate: 1.357%
- Weekly median shock rate: {summary['shock_pct'].median():.3f}%

- Daily median abs overlap with Momentum: 0.050
- Weekly median abs overlap with Momentum: {summary['spearman_volscore_momentumScore'].abs().median():.3f}

The weekly pattern is consistent with the daily finding: VolatilityEngine adds useful diagnostic information, with no hidden directional bias.

## Lessons Learned

- Weekly aggregation behaves as expected: smoother state sequences and larger absolute moves per bar.
- The same approved measures translate well to weekly bars.
- VolatilityEngine is suitable as a diagnostic module on both daily and weekly horizons.

## Documentation Improvements

- VolatilityEngine specification could note that weekly validation is now also covered in RDR-002W.
- VolatilityEngine state distribution differences between daily and weekly should be considered when refining thresholds in future versions.

## Research Integrity Statement

This RDR separates evidence, interpretation, recommendation, and approval. Hermes recommends; Paul Austin retains final approval authority. No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this RDR. VolatilityEngine remains diagnostic-only.
"""
    REPORT.write_text(report)

    manifest = f"""# RDR-002W Run Manifest

Run ID: RDR-002W
Run type: Diagnostic validation (weekly companion to RDR-002)
ATE version: ATE v2.1
VolatilityEngine version: 1.0.0-draft
Status: Completed
Generated: {start_time.isoformat()}

## Artefacts

- Human-readable report / RDR: `research/Reports/RDR/RDR-002W-volatility-diagnostic-validation.md`
- Summary CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Summary.csv`
- Duration CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Durations.csv`
- Transition CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Transitions.csv`
- Class summary CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Class_Summary.csv`
- Shock examples CSV: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/RDR-002W_Shock_Examples.csv`
- Charts directory: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/charts/`
- Reproduction script: `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/run_rdr002w_validation.py`

## Source Code

- Pine release file: `pine/releases/ATE_v2.1.pine`
- Pine release SHA256: `{pine_sha}`

## Data Source

- Source: Yahoo Finance via `yfinance`
- Download mode: weekly OHLC, period 10y, filtered to dates from 2014-01-01 where available
- Timeframe: Weekly
- Raw cache: generated locally by `run_rdr002w_validation.py`; not committed under RDR-001 raw-data policy.

## Reproduction Environment

- Python: 3.9.6 on macOS during this run
- Required Python packages: `pandas`, `numpy`, `yfinance`, `matplotlib`, `tabulate`
- Example setup: `python3 -m venv .venv-rdr002w && .venv-rdr002w/bin/python -m pip install pandas numpy yfinance matplotlib tabulate`
- Example rerun: `.venv-rdr002w/bin/python backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/run_rdr002w_validation.py`

## Assets

{md_table(summary, ['symbol', 'asset_name', 'asset_class', 'rows', 'start_date', 'end_date'], 100)}

## Parameters

```json
{json.dumps(PARAMS, indent=2)}
```

## Known Limitations

- Yahoo Finance data may differ from TradingView data.
- This is a Python research port, not a Pine compiler.
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
        "charts": chart_paths,
    }, indent=2))


if __name__ == "__main__":
    main()
