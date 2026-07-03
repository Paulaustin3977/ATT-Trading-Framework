"""Build seeded RiskEngine v1.0 fixtures under tests/fixtures/ATE_v2_2/.

Each fixture has OHLCV plus the downstream-engine snapshot columns
(volScore, volShockFlag, confidenceScore, trendScore, momentumScore).

Regime design is tuned against the planned RiskEngine compute path so the
realised state distribution matches the fixture name:

- calm_normal:  volScore ~ 60 (no risk pts), bar_range ~ 0.7 ATR (no
  extension), confidence ~ 50 (no conflict). Expected: calm + normal;
  minimal elevated.
- elevated:      volScore ~ 22 with frequent shock flag, bar_range ~ 2.0
  ATR (extension in mid-band), confidence alternates so conflict_risk is
  active. Expected: elevated is dominant, with some tense/extreme.
- extreme_conflict:  volScore < 22 with very frequent shock flag
  (vol contribution approaches cap 35), bar_range ~ 3.5 ATR
  (extension ~30), confidence alternates so conflict_risk ~15. Total
  raw ~ 90+. Expected: extreme + tense dominate.
- unknown:       trendScore entirely NaN (insufficient data), small bars.
  Expected: python handle defaults may produce calm/normal but the
  deterministic engine does not error.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import json
import os
import sys
import hashlib
import pathlib

DEST = pathlib.Path('/Users/paul/ATT-Trading-Framework/tests/fixtures/ATE_v2_2')
DEST.mkdir(parents=True, exist_ok=True)

SPEC = {
    "fixture_set_version": "1.0.0",
    "engine_target": "ATE v2.2 / RiskEngine v1.0.0-draft",
    "fixtures": {
        # Realised bar_range_atr = 2 * bar_range_atr_param (since bar_range = 2 * half_range).
        # So set param = target / 2 to land on target realised ratio.
        "calm_normal": {"n": 240, "seed": 21,
                         "vol_score": 60.0, "vol_noise": 3.0, "shock_prob": 0.0,
                         "bar_range_atr": 0.4, "confidence": 50.0, "conf_noise": 5.0},
        "elevated": {"n": 240, "seed": 22,
                       "vol_score": 22.0, "vol_noise": 3.0, "shock_prob": 0.25,
                       "bar_range_atr": 1.5, "confidence": 70.0, "conf_noise": 6.0,
                       "alternating_conf": True},
        "extreme_conflict": {"n": 240, "seed": 23,
                              "vol_score": 15.0, "vol_noise": 1.0, "shock_prob": 0.8,
                              "bar_range_atr": 3.8, "confidence": 50.0, "conf_noise": 4.0,
                              "alternating_conf": True},
        "unknown": {"n": 80, "seed": 24,
                     "vol_score": 60.0, "vol_noise": 2.0, "shock_prob": 0.0,
                     "bar_range_atr": 0.3, "confidence": 50.0, "conf_noise": 1.0,
                     "trend_nan": True},
    },
    "params": {"volRiskElevatedScore": 25, "extensionAtrLow": 1.5, "extensionAtrHigh": 3.0,
               "swingRiskAtr": 2.0, "confidenceRiskHigh": 80, "confidenceRiskLow": 20,
               "riskSmoothingLength": 3},
    "engine_reference": "specifications/ATE/RiskEngine.md (v1.0 Draft Approved)",
}


def base_ohlcv(n, seed, atr_target, bar_range_atr):
    """Generate OHLCV where bar range ≈ bar_range_atr × atr_target.

    bar_range_atr = (high - low) / ATR where ATR ~ atr_target.
    So high-low ≈ bar_range_atr * atr_target.
    """
    rng = np.random.default_rng(seed)
    base = 1000.0
    step = rng.normal(0.0, atr_target * 0.5, n)  # moderate drift
    close = base + np.cumsum(step)
    body = rng.normal(0.0, atr_target * 0.2, n)
    half_range = bar_range_atr * atr_target * 0.5
    high = close + body + half_range
    low = close + body - half_range
    open_ = close + body
    dates = pd.bdate_range("2018-01-01", periods=n)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close},
                         index=pd.DatetimeIndex(dates, name="Date"))


def build_vol_score(n, mean, noise, shock_prob, rng):
    base = np.clip(rng.normal(mean, noise, n), 0, 100)
    shock = rng.random(n) < shock_prob
    return base, shock


def build_confidence(n, mean, noise, alternating, rng):
    if alternating:
        cs = np.zeros(n)
        for i in range(n):
            cs[i] = np.clip(rng.normal(85 if i % 3 == 0 else 15, 2.0), 0, 100)
        return cs
    return np.clip(rng.normal(mean, noise, n), 0, 100)


def build_trend_momentum(n, mean, noise, trend_nan, rng):
    if trend_nan:
        return np.full(n, np.nan), np.full(n, np.nan)
    ts = np.clip(rng.normal(mean, noise, n), 0, 100)
    ms = np.clip(rng.normal(mean, noise, n), 0, 100)
    return ts, ms


def assemble(name, cfg, atr_target=0.05):
    n = cfg["n"]; seed = cfg["seed"]
    rng = np.random.default_rng(seed)
    df = base_ohlcv(n=n, seed=seed, atr_target=atr_target,
                     bar_range_atr=cfg["bar_range_atr"])
    vol, shock = build_vol_score(n, cfg["vol_score"], cfg["vol_noise"], cfg["shock_prob"], rng)
    conf = build_confidence(n, cfg["confidence"], cfg["conf_noise"],
                            cfg.get("alternating_conf", False), rng)
    trend, momentum = build_trend_momentum(n, cfg["confidence"], cfg["conf_noise"],
                                           cfg.get("trend_nan", False), rng)
    df["volScore"] = vol
    df["volShockFlag"] = shock
    df["confidenceScore"] = conf
    df["trendScore"] = trend
    df["momentumScore"] = momentum
    return df


fixtures = {}
for name, cfg in SPEC["fixtures"].items():
    df = assemble(name, cfg, atr_target=0.05)
    fixtures[name] = df

# Write fixtures + spec.
for name, df in fixtures.items():
    df.to_csv(DEST / f"{name}.csv", index_label="Date")
with open(DEST / "fixture_spec.json", "w") as f:
    json.dump(SPEC, f, indent=2)

# Per-fixture SHA
for name in ["calm_normal", "elevated", "extreme_conflict", "unknown"]:
    p = DEST / f"{name}.csv"
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"{name}: {h}")
print("files:", sorted(os.listdir(DEST)))

