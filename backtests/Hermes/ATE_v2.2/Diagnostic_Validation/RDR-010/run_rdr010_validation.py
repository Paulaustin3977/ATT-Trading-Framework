#!/usr/bin/env python3
"""Deterministic RDR-010 TrendEngine diagnostic validation re-attempt.

This harness reuses the existing RDR-003/RDR-003W OHLC caches and the
research-only Python TrendEngine mirror. It performs no parameter search and
contains no trading, order, sizing, stop, alert, or engine-coupling logic.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
COMPUTE_PATH = REPO / "tools/scripts/_trendengine_compute.py"
HORIZONS = (1, 5, 20)
INSTRUMENTS = ("GC=F", "SI=F", "IGLT.L")
FILE_STEMS = {"GC=F": "GC_F", "SI=F": "SI_F", "IGLT.L": "IGLT.L"}
STATES = ("UNKNOWN", "UP", "DOWN", "RANGE")


def _load_compute():
    spec = importlib.util.spec_from_file_location("trendengine_compute", COMPUTE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import TrendEngine mirror: {COMPUTE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_forward_returns(frame: pd.DataFrame, horizons: Sequence[int] = HORIZONS) -> pd.DataFrame:
    """Add strict next-horizon close-to-close simple returns (no lookahead in signals)."""
    out = frame.copy()
    for horizon in horizons:
        out[f"fwd_ret_{horizon}"] = out["Close"].shift(-horizon) / out["Close"] - 1.0
    return out


def state_runs(states: pd.Series, dates: pd.Series | pd.Index | None = None) -> pd.DataFrame:
    """Return one row per contiguous state run."""
    values = states.astype(str).tolist()
    date_values = list(dates) if dates is not None else list(states.index)
    rows = []
    if not values:
        return pd.DataFrame(columns=["run_id", "state", "start", "end", "duration"])
    start = 0
    run_id = 1
    for i in range(1, len(values) + 1):
        if i == len(values) or values[i] != values[start]:
            rows.append({"run_id": run_id, "state": values[start], "start": date_values[start],
                         "end": date_values[i - 1], "duration": i - start})
            run_id += 1
            start = i
    return pd.DataFrame(rows)


def transition_counts(states: pd.Series) -> pd.DataFrame:
    """Count state changes; same-state bar-to-bar observations are not transitions."""
    values = states.astype(str).tolist()
    counts: dict[tuple[str, str], int] = {}
    for left, right in zip(values[:-1], values[1:]):
        if left != right:
            counts[(left, right)] = counts.get((left, right), 0) + 1
    rows = [{"from_state": k[0], "to_state": k[1], "count": v}
            for k, v in sorted(counts.items())]
    return pd.DataFrame(rows, columns=["from_state", "to_state", "count"])


def chronological_halves(eligible: pd.Series) -> pd.Series:
    """Split eligible rows by order into non-overlapping early and late halves."""
    labels = pd.Series("excluded", index=eligible.index, dtype=object)
    positions = np.flatnonzero(eligible.to_numpy(dtype=bool))
    cut = (len(positions) + 1) // 2
    labels.iloc[positions[:cut]] = "early"
    labels.iloc[positions[cut:]] = "late"
    return labels


def volatility_regimes(close: pd.Series, eligible: pd.Series) -> tuple[pd.Series, dict]:
    """Label low/mid/high using 20-bar trailing return-volatility sample tertiles."""
    rolling = close.pct_change().rolling(20, min_periods=20).std(ddof=1)
    sample = rolling[eligible.astype(bool) & rolling.notna()]
    q33 = float(sample.quantile(1.0 / 3.0)) if len(sample) else float("nan")
    q67 = float(sample.quantile(2.0 / 3.0)) if len(sample) else float("nan")
    regimes = pd.Series(np.nan, index=close.index, dtype=object)
    valid = rolling.notna() & eligible.astype(bool)
    regimes.loc[valid & (rolling <= q33)] = "low"
    regimes.loc[valid & (rolling > q33) & (rolling <= q67)] = "mid"
    regimes.loc[valid & (rolling > q67)] = "high"
    return regimes, {"window": 20, "q33": q33, "q67": q67, "n": int(len(sample))}


def directional_metric(frame: pd.DataFrame, horizon: int, model: str) -> dict:
    """Compute directional next-return diagnostics for one already-selected sample.

    TrendEngine uses +1 for UP and -1 for DOWN; RANGE/UNKNOWN are excluded.
    The no-TrendEngine benchmark is always-long (+1) on every eligible row.
    A false signal is explicitly a signed future return <= 0. Zero is a miss.
    """
    ret = frame[f"fwd_ret_{horizon}"]
    if model == "TrendEngine":
        direction = frame["trendState"].map({"UP": 1.0, "DOWN": -1.0})
    elif model == "No-TrendEngine benchmark":
        direction = pd.Series(1.0, index=frame.index)
    else:
        raise ValueError(f"unknown model: {model}")
    valid = direction.notna() & ret.notna()
    signed = (direction[valid] * ret[valid]).astype(float)
    n = int(len(signed))
    return {
        "model": model,
        "horizon": int(horizon),
        "n": n,
        "hit_rate": float((signed > 0).mean()) if n else np.nan,
        "false_signal_rate": float((signed <= 0).mean()) if n else np.nan,
        "expectancy": float(signed.mean()) if n else np.nan,
        "median_signed_return": float(signed.median()) if n else np.nan,
    }


def _source_path(timeframe: str, instrument: str) -> Path:
    stem = FILE_STEMS[instrument]
    if timeframe == "Daily":
        return REPO / "backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache" / f"{stem}.csv"
    return REPO / "backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache" / f"{stem}_w.csv"


def load_dataset(timeframe: str, instrument: str, compute) -> tuple[pd.DataFrame, dict]:
    path = _source_path(timeframe, instrument)
    raw = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Open", "High", "Low", "Close"}
    if not required.issubset(raw.columns):
        raise ValueError(f"{path} missing {sorted(required - set(raw.columns))}")
    if raw["Date"].duplicated().any() or not raw["Date"].is_monotonic_increasing:
        raise ValueError(f"{path} dates must be unique and increasing")
    indexed = raw.set_index("Date")
    out = compute.calculate_trend(indexed)
    out = add_forward_returns(out)
    out.insert(0, "Date", out.index)
    out.reset_index(drop=True, inplace=True)
    eligible = ~out["trendDiagInsufficientData"].astype(bool)
    out["sample_half"] = chronological_halves(eligible)
    regimes, thresholds = volatility_regimes(out["Close"], eligible)
    out["volatility_regime"] = regimes
    out["instrument"] = instrument
    out["timeframe"] = timeframe
    meta = {
        "path": str(path.relative_to(REPO)), "sha256": sha256(path), "rows": int(len(out)),
        "start": out["Date"].min().date().isoformat(), "end": out["Date"].max().date().isoformat(),
        "eligible_rows": int(eligible.sum()), "volatility_thresholds": thresholds,
    }
    return out, meta


def _state_distribution(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for (timeframe, instrument), frame in frames.items():
        for phase, sample in (("all", frame), ("post_warmup", frame[~frame["trendDiagInsufficientData"]])):
            counts = sample["trendState"].value_counts()
            total = int(len(sample))
            for state in STATES:
                count = int(counts.get(state, 0))
                rows.append({"timeframe": timeframe, "instrument": instrument, "phase": phase,
                             "state": state, "count": count, "fraction": count / total if total else np.nan})
    return pd.DataFrame(rows)


def _durations(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    pieces = []
    for (timeframe, instrument), frame in frames.items():
        runs = state_runs(frame["trendState"], frame["Date"])
        runs.insert(0, "instrument", instrument)
        runs.insert(0, "timeframe", timeframe)
        pieces.append(runs)
    return pd.concat(pieces, ignore_index=True)


def _transitions(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for (timeframe, instrument), frame in frames.items():
        for phase, sample in (("all", frame), ("post_warmup", frame[~frame["trendDiagInsufficientData"]])):
            table = transition_counts(sample["trendState"])
            total = int(table["count"].sum()) if len(table) else 0
            for rec in table.to_dict("records"):
                rec.update({"timeframe": timeframe, "instrument": instrument, "phase": phase,
                            "fraction_of_transitions": rec["count"] / total if total else np.nan})
                rows.append(rec)
    columns = ["timeframe", "instrument", "phase", "from_state", "to_state", "count", "fraction_of_transitions"]
    return pd.DataFrame(rows, columns=columns)


def _metric_rows(sample: pd.DataFrame, timeframe: str, instrument: str,
                 slice_type: str, slice_value: str) -> list[dict]:
    rows = []
    for horizon in HORIZONS:
        for model in ("TrendEngine", "No-TrendEngine benchmark"):
            row = directional_metric(sample, horizon, model)
            row.update({"timeframe": timeframe, "instrument": instrument,
                        "slice_type": slice_type, "slice_value": slice_value})
            rows.append(row)
    return rows


def _directional_metrics(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for (timeframe, instrument), frame in frames.items():
        eligible = frame[~frame["trendDiagInsufficientData"]].copy()
        rows.extend(_metric_rows(eligible, timeframe, instrument, "overall", "all"))
        for half in ("early", "late"):
            rows.extend(_metric_rows(eligible[eligible["sample_half"] == half], timeframe, instrument,
                                     "chronological_half", half))
        for regime in ("low", "mid", "high"):
            rows.extend(_metric_rows(eligible[eligible["volatility_regime"] == regime], timeframe, instrument,
                                     "volatility_regime", regime))
    for timeframe in ("Daily", "Weekly"):
        pooled = pd.concat([frame[~frame["trendDiagInsufficientData"]]
                            for (tf, _), frame in frames.items() if tf == timeframe], ignore_index=True)
        rows.extend(_metric_rows(pooled, timeframe, "POOLED", "overall", "all"))
        for half in ("early", "late"):
            rows.extend(_metric_rows(pooled[pooled["sample_half"] == half], timeframe, "POOLED",
                                     "chronological_half", half))
        for regime in ("low", "mid", "high"):
            rows.extend(_metric_rows(pooled[pooled["volatility_regime"] == regime], timeframe, "POOLED",
                                     "volatility_regime", regime))
    cols = ["timeframe", "instrument", "slice_type", "slice_value", "model", "horizon",
            "n", "hit_rate", "false_signal_rate", "expectancy", "median_signed_return"]
    return pd.DataFrame(rows)[cols]


def _stability(frames: dict[tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for (timeframe, instrument), frame in frames.items():
        eligible = frame[~frame["trendDiagInsufficientData"]]
        early = eligible[eligible["sample_half"] == "early"]["trendState"].value_counts(normalize=True)
        late = eligible[eligible["sample_half"] == "late"]["trendState"].value_counts(normalize=True)
        tv = 0.5 * sum(abs(float(early.get(s, 0.0)) - float(late.get(s, 0.0))) for s in ("UP", "DOWN", "RANGE"))
        for comparison, sample in [("early", eligible[eligible["sample_half"] == "early"]),
                                   ("late", eligible[eligible["sample_half"] == "late"]),
                                   ("vol_low", eligible[eligible["volatility_regime"] == "low"]),
                                   ("vol_mid", eligible[eligible["volatility_regime"] == "mid"]),
                                   ("vol_high", eligible[eligible["volatility_regime"] == "high"])]:
            counts = sample["trendState"].value_counts(normalize=True)
            trans = transition_counts(sample["trendState"])
            rows.append({"timeframe": timeframe, "instrument": instrument, "slice": comparison,
                         "n": int(len(sample)), "up_fraction": float(counts.get("UP", 0.0)),
                         "down_fraction": float(counts.get("DOWN", 0.0)),
                         "range_fraction": float(counts.get("RANGE", 0.0)),
                         "transitions_per_100_bars": 100.0 * float(trans["count"].sum()) / max(len(sample) - 1, 1),
                         "early_late_state_total_variation": tv})
    return pd.DataFrame(rows)


def _daily_weekly(metrics: pd.DataFrame) -> pd.DataFrame:
    overall = metrics[(metrics["slice_type"] == "overall") & (metrics["slice_value"] == "all")]
    idx = ["instrument", "model", "horizon"]
    value_cols = ["n", "hit_rate", "false_signal_rate", "expectancy"]
    wide = overall.pivot(index=idx, columns="timeframe", values=value_cols)
    rows = []
    for key, rec in wide.iterrows():
        row = dict(zip(idx, key))
        for col in value_cols:
            row[f"daily_{col}"] = rec.get((col, "Daily"), np.nan)
            row[f"weekly_{col}"] = rec.get((col, "Weekly"), np.nan)
            if col != "n":
                row[f"weekly_minus_daily_{col}"] = row[f"weekly_{col}"] - row[f"daily_{col}"]
        rows.append(row)
    return pd.DataFrame(rows)


def _save_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.12g", date_format="%Y-%m-%d")


def _charts(distribution: pd.DataFrame, metrics: pd.DataFrame, stability: pd.DataFrame, chart_dir: Path) -> list[Path]:
    chart_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 120, "font.size": 9})
    outputs = []
    post = distribution[distribution["phase"] == "post_warmup"]
    for timeframe in ("Daily", "Weekly"):
        pivot = post[post["timeframe"] == timeframe].pivot(index="instrument", columns="state", values="fraction")
        pivot = pivot.reindex(columns=["UP", "DOWN", "RANGE"], fill_value=0)
        ax = pivot.plot(kind="bar", stacked=True, figsize=(8, 4), color=["#2ca02c", "#d62728", "#7f7f7f"])
        ax.set_title(f"RDR-010 {timeframe} post-warmup TrendEngine state distribution")
        ax.set_ylabel("fraction of bars"); ax.set_xlabel(""); ax.legend(loc="upper right")
        plt.tight_layout()
        path = chart_dir / f"state_distribution_{timeframe.lower()}.png"
        plt.savefig(path, metadata={"Software": "RDR-010 deterministic harness"}); plt.close()
        outputs.append(path)
    pooled = metrics[(metrics["instrument"] == "POOLED") & (metrics["slice_type"] == "overall")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for model, group in pooled.groupby("model", sort=True):
        for timeframe, tf_group in group.groupby("timeframe", sort=True):
            axes[0].plot(tf_group["horizon"], tf_group["hit_rate"], marker="o", label=f"{model} / {timeframe}")
            axes[1].plot(tf_group["horizon"], tf_group["expectancy"], marker="o", label=f"{model} / {timeframe}")
    axes[0].axhline(0.5, color="black", lw=0.7, ls="--"); axes[0].set_title("Directional hit rate")
    axes[1].axhline(0.0, color="black", lw=0.7, ls="--"); axes[1].set_title("Signed-return expectancy")
    for ax in axes: ax.set_xlabel("bars ahead"); ax.legend(fontsize=7)
    plt.tight_layout(); path = chart_dir / "pooled_directional_metrics.png"
    plt.savefig(path, metadata={"Software": "RDR-010 deterministic harness"}); plt.close(); outputs.append(path)
    daily = stability[stability["timeframe"] == "Daily"]
    pivot = daily.pivot(index="instrument", columns="slice", values="transitions_per_100_bars")
    ax = pivot.reindex(columns=["early", "late", "vol_low", "vol_mid", "vol_high"]).plot(kind="bar", figsize=(9, 4))
    ax.set_title("Daily state-transition stability by chronological and volatility slice")
    ax.set_ylabel("state changes per 100 bars"); ax.set_xlabel(""); plt.tight_layout()
    path = chart_dir / "daily_stability_transitions.png"
    plt.savefig(path, metadata={"Software": "RDR-010 deterministic harness"}); plt.close(); outputs.append(path)
    return outputs


def run(output_dir: Path = HERE) -> dict:
    compute = _load_compute()
    frames: dict[tuple[str, str], pd.DataFrame] = {}
    sources = {}
    for timeframe in ("Daily", "Weekly"):
        for instrument in INSTRUMENTS:
            frame, meta = load_dataset(timeframe, instrument, compute)
            frames[(timeframe, instrument)] = frame
            sources[f"{timeframe}:{instrument}"] = meta

    columns = ["Date", "timeframe", "instrument", "Open", "High", "Low", "Close", "Volume",
               "trendState", "trendStrength", "trendAge", "trendDiagEmaSlope", "trendDiagAgreement",
               "trendDiagHigherHigh", "trendDiagHigherLow", "trendDiagLowerHigh", "trendDiagLowerLow",
               "trendDiagStateConfirmBars", "trendDiagInsufficientData", "trendStateChanged",
               "sample_half", "volatility_regime", "fwd_ret_1", "fwd_ret_5", "fwd_ret_20"]
    bars = pd.concat([f for f in frames.values()], ignore_index=True)[columns]
    distribution = _state_distribution(frames)
    durations = _durations(frames)
    transitions = _transitions(frames)
    metrics = _directional_metrics(frames)
    stability = _stability(frames)
    comparison = _daily_weekly(metrics)

    outputs = {
        "bar_outputs.csv": bars, "state_distribution.csv": distribution,
        "state_durations.csv": durations, "state_transitions.csv": transitions,
        "directional_metrics.csv": metrics, "stability_summary.csv": stability,
        "daily_weekly_comparison.csv": comparison,
    }
    for name, frame in outputs.items():
        _save_csv(frame, output_dir / name)
    chart_paths = _charts(distribution, metrics, stability, output_dir / "charts")

    overall = metrics[(metrics["slice_type"] == "overall") & (metrics["instrument"] == "POOLED")]
    findings = {
        "run_id": "RDR-010-deterministic-re-attempt",
        "scope": "diagnostic research only",
        "trendengine_version": str(compute.PARAMS) and "0.2.0-spec-impl",
        "fixed_parameters": compute.PARAMS,
        "horizons_bars": list(HORIZONS),
        "instruments": list(INSTRUMENTS),
        "timeframes": ["Daily", "Weekly"],
        "definitions": {
            "trend_direction": "UP=+1, DOWN=-1; RANGE and UNKNOWN excluded from TrendEngine directional samples",
            "next_return": "Close[t+h]/Close[t]-1 using h in {1,5,20}; the signal uses only information through t",
            "hit": "signed next return > 0",
            "false_signal": "directional observation with signed next return <= 0; zero return is a miss",
            "expectancy": "arithmetic mean signed next return; no costs and no trade simulation",
            "benchmark": "No-TrendEngine always-long observation on every post-warmup bar; same next-return target",
            "early_late": "non-overlapping chronological halves of post-warmup rows per instrument/timeframe",
            "volatility_regime": "20-bar trailing close-return sample standard deviation split at in-sample 33.3% and 66.7% quantiles per instrument/timeframe; descriptive, not optimized",
            "state_transition": "adjacent bar state change; same-state observations excluded",
            "state_duration": "contiguous bars in the same diagnostic state",
        },
        "sources": sources,
        "pooled_overall_metrics": overall.to_dict("records"),
        "early_late_state_total_variation": stability[["timeframe", "instrument", "early_late_state_total_variation"]].drop_duplicates().to_dict("records"),
        "limitations": [
            "Descriptive diagnostics only; overlapping horizon returns are not independent.",
            "No transaction costs, trades, drawdown, entries, exits, sizing, stops, alerts, or execution are modelled.",
            "The always-long benchmark is transparent but not a matched-frequency random or investable strategy benchmark.",
            "Volatility tertiles use full-sample descriptive quantiles and are not out-of-sample regime thresholds.",
            "Three instruments and two timeframes do not establish broad external validity.",
        ],
        "release_sha256": {
            "ATE_v2.2.pine": sha256(REPO / "pine/releases/ATE_v2.2.pine"),
            "ATE_v2.1.pine": sha256(REPO / "pine/releases/ATE_v2.1.pine"),
        },
    }
    artifact_hashes = {name: sha256(output_dir / name) for name in outputs}
    artifact_hashes.update({str(p.relative_to(output_dir)): sha256(p) for p in chart_paths})
    findings["artifact_sha256"] = artifact_hashes
    findings_path = output_dir / "Research_Findings.json"
    findings_path.write_text(json.dumps(findings, indent=2, sort_keys=True, allow_nan=False) + "\n")

    log_lines = [
        "RDR-010 deterministic TrendEngine validation execution log",
        "command: python3 backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/run_rdr010_validation.py",
        f"python: {platform.python_version()}", f"pandas: {pd.__version__}", f"numpy: {np.__version__}",
        f"matplotlib: {matplotlib.__version__}", "network_calls: 0", "parameter_search: none",
        "trading_or_execution_logic: none", f"datasets: {len(frames)}", f"bar_rows: {len(bars)}",
        f"directional_metric_rows: {len(metrics)}", f"charts: {len(chart_paths)}",
        f"Research_Findings.json sha256: {sha256(findings_path)}", "exit_code: 0",
    ]
    (output_dir / "execution.log").write_text("\n".join(log_lines) + "\n")
    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args(list(argv) if argv is not None else None)
    findings = run(args.output_dir.resolve())
    print(json.dumps({"run_id": findings["run_id"], "datasets": len(findings["sources"]),
                      "release_sha256": findings["release_sha256"], "exit_code": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
