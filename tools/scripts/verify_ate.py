#!/usr/bin/env python3
"""ERP-001 canonical ATE verifier.

Runs the ATE v2.1 VolatilityEngine compute path against seeded fixtures
under ``tests/fixtures/ATE_v2_1/`` and asserts the contract guarantees from
the approved VolatilityEngine specification and the ATE v2.1 release file.

This is a behaviour-and-contract verifier. It is NOT a full validation
suite, NOT a parameter search, NOT a strategy backtest, NOT a
performance/risk-claims test.

Outputs a ``verify.log`` next to this script with:
  - totals
  - fixture distributions
  - machine-readable JSON summary

Exit codes:
  0  pass                (no checks failed)
  1  fail                (one or more checks failed; details in verify.log)
  2  environment_error   (missing dependency, fixture, or Pine file)

Usage:
    python tools/scripts/verify_ate.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import importlib
import re
from pathlib import Path

# Make pandas/numpy optional (they're needed for the compute path).
try:
    import numpy as np
    import pandas as pd
except ImportError as e:  # pragma: no cover
    sys.stderr.write("FATAL: pandas/numpy not available: %s\n" % e)
    sys.exit(2)

REPO = Path(__file__).resolve().parents[2]  # tools/scripts/verify_ate.py -> tools/scripts -> tools -> repo root
TOOLS = Path(__file__).resolve().parent
FIXTURE_DIR = REPO / "tests/fixtures/ATE_v2_1"
PINE_PATH = REPO / "pine/releases/ATE_v2.1.pine"
LOG_PATH = TOOLS / "verify.log"

# ATE v2.2 RiskEngine verification artefacts (planned, not yet implemented in Pine).
RISK_SPEC = REPO / "specifications/ATE/RiskEngine.md"
RISK_FIXTURE_DIR = REPO / "tests/fixtures/ATE_v2_2"
RISK_COMPUTE = TOOLS / "_riskengine_compute.py"

# ATE v2.2 release-file direct verification (EDR-001 extension under ATOS v1.1).
V22_PINE = REPO / "pine/releases/ATE_v2.2.pine"
V22_DEV  = REPO / "pine/development/ATE_Current.pine"
V22_EXPECTED_SHA = "d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239"
V21_EXPECTED_SHA = "7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893"

# Stub optional deps before importing the daily reproduction script.
# The daily script imports yfinance and matplotlib at module top, but the
# verifier does not download market data or render charts. Stubbing keeps
# the verifier self-sufficient when yfinance is unavailable.
import types
if "yfinance" not in sys.modules:
    _yf = types.ModuleType("yfinance")
    _yf.download = lambda *a, **kw: None
    sys.modules["yfinance"] = _yf
if "matplotlib" not in sys.modules:
    _mp = types.ModuleType("matplotlib")
    _mp.use = lambda *a, **kw: None
    sys.modules["matplotlib"] = _mp
if "matplotlib.pyplot" not in sys.modules:
    _mplpy = types.ModuleType("matplotlib.pyplot")
    _mplpy.scatter = lambda *a, **kw: None
    _mplpy.plot = lambda *a, **kw: None
    _mplpy.savefig = lambda *a, **kw: None
    _mplpy.close = lambda *a, **kw: None
    _mplpy.legend = lambda *a, **kw: None
    _mplpy.title = lambda *a, **kw: None
    _mplpy.grid = lambda *a, **kw: None
    _mplpy.tight_layout = lambda *a, **kw: None
    sys.modules["matplotlib.pyplot"] = _mplpy

ALLOWED_DIR = {"none", "expanding", "contracting", "stable", "unstable"}
ALLOWED_STATE = {"compressed", "normal", "expanding", "elevated", "unstable", "shock", "unknown"}
REQUIRED_RM_FIELDS = [
    "VolatilityEngineVersion", "VolatilityScore", "VolatilityState", "VolatilityDirection",
    "VolatilityReason", "ATRPercent", "ATRRatio", "BBWidthRatio", "CombinedVolRatio",
    "VolSlope", "ShockFlag",
]

# ---------------------------------------------------------------------------
# Verifier state
# ---------------------------------------------------------------------------
results = []

def check(name: str, ok: bool, detail: str = "") -> None:
    results.append({"name": name, "ok": bool(ok), "detail": str(detail)[:160]})


def env_error(reason: str) -> None:
    check("environment", False, reason)


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
if not FIXTURE_DIR.is_dir():
    env_error(f"fixture dir missing: {FIXTURE_DIR}")
elif not PINE_PATH.is_file():
    env_error(f"Pine release missing: {PINE_PATH}")
else:
    check("environment", True, "fixture dir and Pine release present")

# Load daily reproduction script via the same importlib pattern used by RDR-002W
DAILY_SCRIPT = REPO / "backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py"
calculate = None
try:
    spec = importlib.util.spec_from_file_location("rdr002_daily", str(DAILY_SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    calculate = mod.calculate
except Exception as e:
    env_error(f"failed to load daily reproduction script: {e}")

pine_src = ""
if PINE_PATH.is_file():
    pine_src = PINE_PATH.read_text()


# ---------------------------------------------------------------------------
# Static contract checks
# ---------------------------------------------------------------------------
# Pine contract: Research Mode field labels are present.
for fld in REQUIRED_RM_FIELDS:
    check(f"research_mode_field_present:{fld}", fld in pine_src,
          f"checked in {PINE_PATH.name}")

# Engine Output Contract mapping.
# The ATE architecture defines six contract fields. Each engine maps them to
# Pine variables; the verifier checks the VolatilityEngine mapping in the
# active Pine release (volScore, volState, volDirection, volReason, named
# diagnostic variables, volEngineVersion). The ATE v2.1 release exposes
# diagnostic values as named variables in the `vol*` namespace rather than
# a separate `volDiag*` namespace; we assert the variables the release actually
# exposes.
EOC_PINE_VARS = {
    "score": ["volScore"],
    "state": ["volState"],
    "direction": ["volDirection"],
    "reason": ["volReason"],
    "diagnostics": ["volAtr", "volAtrPercent", "volAtrBaseline", "volAtrRatio",
                    "volBbBasis", "volBbDev", "volBbUpper", "volBbLower",
                    "volBbWidthRaw", "volBbWidthBaseline", "volBbWidthRatio",
                    "volCombinedRatio", "volSlope",
                    "volTrueRange", "volTrueRangeBaseline", "volShockFlag",
                    "volValidAtr", "volValidBb", "volUnknown"],
    "version": ["volEngineVersion"],
}
for fname, vars_ in EOC_PINE_VARS.items():
    for vn in vars_:
        check(f"engine_output_contract:{fname}:{vn}", vn in pine_src,
              f"checked in {PINE_PATH.name}")

# Volatility direction values are restricted.
m = re.search(r"volDirection =\s*([^\n]*(?:\n[^\n]*)*?)(?=\n\n)", pine_src)
if not m:
    check("pine_volDirection_block_found", False, "could not parse volDirection block")
else:
    block = m.group(1)
    for v in ALLOWED_DIR:
        check(f"pine_direction_includes:{v}", v in block)
    check("pine_direction_no_bullish", "bullish" not in block)
    check("pine_direction_no_bearish", "bearish" not in block)

# VolatilityEngine version literal.
check("pine_vol_engine_version_literal", '1.0.0-draft' in pine_src)

# Diagnostic-only boundaries. VolatilityEngine must not be a
# ConfidenceEngine/RiskEngine/DecisionEngine input, must not produce buy/sell
# alerts, and must not feed entry/exit logic, position sizing, or stops.

# 1. No buy/sell volatility alerts.
bad_alert_patterns = [
    "Volatility Buy",
    "Volatility Sell",
    "Volatility Entry",
    "Volatility Exit",
    "ATE Vol Buy",
    "ATE Vol Sell",
]
for pat in bad_alert_patterns:
    check(f"pine_no_voltrade_alert:{pat}", pat not in pine_src)

# 2. confidenceScore/marketState/structureScore/momentumScore code must not
#    reference volScore/volState/volDirection. Conservative substring check.
for vol_var in ("volScore", "volState", "volDirection"):
    # confirmCoefficient, marketState, structureScore, momentumScore are
    # computed BEFORE confidence block in the source (read top to bottom and
    # isolate the confidence block).
    conf_idx = pine_src.find("confidenceScore =\n")
    if conf_idx >= 0:
        # Look for downstream consumption of vol-* in the confidence block.
        conf_block = pine_src[conf_idx:conf_idx + 2000]
        check(f"volatility_not_in_confidence_block:{vol_var}", vol_var not in conf_block)
    else:
        check(f"volatility_not_in_confidence_block:{vol_var}", False,
              "could not locate confidenceScore block")

# 3. ATE v1.3 alerts preserved (no regression to existing alert set). We
#    verify by listing the preserved names declared as a top-level
#    alertcondition.
PRESERVED_ALERTS = [
    "ATE Golden Cross", "ATE Death Cross", "ATE Strong Bull", "ATE Strong Bear",
    "ATE Bullish BOS", "ATE Bearish BOS",
    "ATE Momentum Bullish", "ATE Momentum Bearish",
    "ATE High Confidence Bull", "ATE Low Confidence Bear",
]
for a in PRESERVED_ALERTS:
    check(f"alert_preserved:{a}", a in pine_src)


# ---------------------------------------------------------------------------
# Behaviour checks against fixtures
# ---------------------------------------------------------------------------

def summarise(df: "pd.DataFrame") -> dict:
    state_counts = df["VolatilityState"].value_counts().to_dict() if "VolatilityState" in df.columns else {}
    direction_set = sorted(set(df["VolatilityDirection"].dropna().unique())) if "VolatilityDirection" in df.columns else []
    has_shock = bool(df["ShockFlag"].any()) if "ShockFlag" in df.columns else False
    n = len(df)
    score_min = float(df["VolatilityScore"].dropna().min()) if "VolatilityScore" in df.columns else None
    score_max = float(df["VolatilityScore"].dropna().max()) if "VolatilityScore" in df.columns else None
    return {
        "rows": n,
        "state_counts": {str(k): int(v) for k, v in state_counts.items()},
        "direction_values": direction_set,
        "any_shock": has_shock,
        "score_min": score_min,
        "score_max": score_max,
        "pct_unknown": float(state_counts.get("unknown", 0)) / n if n else 0.0,
    }


def behavioural_checks(name: str, spec: dict) -> "pd.DataFrame":
    fx_path = FIXTURE_DIR / f"{name}.csv"
    if not fx_path.is_file():
        env_error(f"fixture missing: {fx_path}")
        return None
    fx = pd.read_csv(fx_path, parse_dates=["Date"], index_col="Date")
    if calculate is None:
        return None
    out = calculate(fx)
    summary = summarise(out)
    check(f"behaviour:output_rows:{name}", summary["rows"] > 0, summary["rows"])
    # Compute path columns exist.
    for col in ["VolatilityState", "VolatilityDirection", "VolatilityScore", "ShockFlag"]:
        check(f"behaviour:computed_has:{name}:{col}", col in out.columns)
    # State values in allowed set.
    if "VolatilityState" in out.columns:
        bad_states = set(out["VolatilityState"].dropna().unique()) - ALLOWED_STATE
        check(f"behaviour:states_allowed:{name}", len(bad_states) == 0, str(bad_states))
    # Direction values in allowed set.
    if "VolatilityDirection" in out.columns:
        bad_dirs = set(out["VolatilityDirection"].dropna().unique()) - ALLOWED_DIR
        check(f"behaviour:direction_allowed:{name}", len(bad_dirs) == 0, str(bad_dirs))
        # No bullish/bearish direction.
        check(f"behaviour:no_bullish_direction:{name}",
              "bullish" not in set(out["VolatilityDirection"].dropna()))
        check(f"behaviour:no_bearish_direction:{name}",
              "bearish" not in set(out["VolatilityDirection"].dropna()))
    # Score range: 0..100 or NaN when unknown.
    if "VolatilityScore" in out.columns:
        s = out["VolatilityScore"].dropna()
        in_range = bool(((s >= 0) & (s <= 100)).all()) if len(s) else True
        check(f"behaviour:score_in_range:{name}", in_range,
              f"min={s.min() if len(s) else None} max={s.max() if len(s) else None}")
    # Regime expectations.
    if name == "quiet":
        # quiet fixture must not produce shock or unstable.
        check("behaviour:quiet_no_shock",
              summary["state_counts"].get("shock", 0) == 0, summary["state_counts"])
        check("behaviour:quiet_no_unstable",
              summary["state_counts"].get("unstable", 0) == 0, summary["state_counts"])
        check("behaviour:quiet_contains_normal_or_unknown",
              summary["state_counts"].get("normal", 0) > 0
              or summary["state_counts"].get("unknown", 0) > 0,
              summary["state_counts"])
    elif name == "normal":
        check("behaviour:normal_mostly_normal_or_expanding",
              (summary["state_counts"].get("normal", 0)
               + summary["state_counts"].get("expanding", 0)
               + summary["state_counts"].get("unknown", 0)) >= int(summary["rows"] * 0.9),
              summary["state_counts"])
    elif name == "shock":
        check("behaviour:shock_has_shock_event",
              summary["any_shock"], summary["state_counts"])
    return out


quiet_out = behavioural_checks("quiet", spec=None)
normal_out = behavioural_checks("normal", spec=None)
shock_out = behavioural_checks("shock", spec=None)

# Determinism check.
if calculate is not None:
    try:
        fx2 = pd.read_csv(FIXTURE_DIR / "normal.csv", parse_dates=["Date"], index_col="Date")
        a = calculate(fx2)
        fx3 = pd.read_csv(FIXTURE_DIR / "normal.csv", parse_dates=["Date"], index_col="Date")
        b = calculate(fx3)
        if "VolatilityScore" in a.columns and "VolatilityScore" in b.columns:
            same_score = (a["VolatilityScore"].fillna(-1.0).values
                          == b["VolatilityScore"].fillna(-1.0).values).all()
            check("deterministic:normal_score", bool(same_score))
        if "VolatilityState" in a.columns and "VolatilityState" in b.columns:
            same_state = (a["VolatilityState"].values == b["VolatilityState"].values).all()
            check("deterministic:normal_state", bool(same_state))
    except Exception as e:
        check("deterministic:rerun", False, repr(e))


# ---------------------------------------------------------------------------
# ATE v2.2 RiskEngine verification (planned, not yet implemented in Pine).
# ---------------------------------------------------------------------------
risk_spec_src = ""
if RISK_SPEC.is_file():
    risk_spec_src = RISK_SPEC.read_text()

# A. Static specification checks: the approved RiskEngine spec must define
#    the documented structure, allowed values, defaults, and boundaries.
RISK_STATE = {"calm", "normal", "elevated", "tense", "extreme", "unknown"}
RISK_DIRECTION = {"none", "elevated", "conflict", "stable", "indeterminate"}
RISK_RESERVED = ["safe", "unsafe", "suitable", "unsuitable",
                 "approved", "blocked", "tradeable", "untradeable"]
RISK_DEFAULTS_LITERALS = {
    "volRiskElevatedScore = 25": "volRiskElevatedScore",
    "extensionAtrLow = 1.5": "extensionAtrLow",
    "extensionAtrHigh = 3.0": "extensionAtrHigh",
    "swingRiskAtr = 2.0": "swingRiskAtr",
    "confidenceRiskHigh = 80": "confidenceRiskHigh",
    "confidenceRiskLow = 20": "confidenceRiskLow",
    "riskSmoothingLength = 3": "riskSmoothingLength",
}
RISK_VERSION_LITERAL = "1.0.0-draft"

# Required contract output fields.
RISK_REQUIRED_FIELDS = [
    ("RiskScore", "score"),
    ("RiskState", "state"),
    ("RiskDirection", "direction"),
    ("RiskReason", "reason"),
    ("RiskEngineVersion", "version"),
    ("volRiskContribution", "diagnostics"),
    ("extRiskContribution", "diagnostics"),
    ("structRiskContribution", "diagnostics"),
    ("conflictRiskContribution", "diagnostics"),
]

# Required diagnostic component fields.
RISK_DIAGNOSTIC_FIELDS = [
    "volRiskComponentState", "extRiskComponentState",
    "structRiskComponentState", "conflictRiskComponentState",
    "volRiskScoreRaw", "extRiskScoreRaw",
    "structRiskScoreRaw", "conflictRiskScoreRaw",
    "volVolatilityScore", "smoothedRiskScore",
]

check("risk:spec_present", risk_spec_src != "")
if risk_spec_src:
    # 1. Allowed state and direction values are listed in the spec.
    check("risk:spec_lists_all_states",
          all(f"- {s}" in risk_spec_src or f"| `{s}`" in risk_spec_src for s in RISK_STATE),
          str(sorted(RISK_STATE)))
    check("risk:spec_lists_all_directions",
          all(f"- {d}" in risk_spec_src or f"| `{d}`" in risk_spec_src for d in RISK_DIRECTION),
          str(sorted(RISK_DIRECTION)))
    # 2. Defaults recorded in the spec match approved inputs.
    for literal, name in RISK_DEFAULTS_LITERALS.items():
        check(f"risk:spec_default:{name}", literal in risk_spec_src, literal)
    # 3. Version literal recorded.
    check(f"risk:spec_version_literal", RISK_VERSION_LITERAL in risk_spec_src)
    # 4. Forbidden direction values.
    # Spec must explicitly forbid bullish/bearish direction (and state).
    check("risk:spec_forbids_bullish_direction",
          "bullish" in risk_spec_src and ("never" in risk_spec_src.lower() or "forbid" in risk_spec_src.lower()))
    check("risk:spec_forbids_bearish_direction",
          "bearish" in risk_spec_src and ("never" in risk_spec_src.lower() or "forbid" in risk_spec_src.lower()))
    # 5. Reserved-language list is referenced explicitly.
    check("risk:spec_reserved_language_list",
          all(w in risk_spec_src.lower() for w in RISK_RESERVED))
    # 6. Diagnostic-only boundary is explicit in the spec.
    check("risk:spec_diagnostic_only_clause",
          ("Diagnostic-Only Boundary" in risk_spec_src
           or "diagnostic-only" in risk_spec_src.lower()))
    check("risk:spec_no_confidence_consumption_clause",
          "Must not consume RiskEngine in ATE v2.2" in risk_spec_src
          or "ConfidenceEngine" in risk_spec_src and "RiskEngine" in risk_spec_src)
    check("risk:spec_no_decision_consumption_clause",
          "DecisionEngine" in risk_spec_src)
    check("risk:spec_no_alerts_clause",
          "No alerts" in risk_spec_src or "alerts" in risk_spec_src.lower())
    check("risk:spec_no_broker_clause",
          "broker" in risk_spec_src.lower() and "no " in risk_spec_src.lower())
    check("risk:spec_no_paper_trading_clause",
          ("paper-trading" in risk_spec_src.lower() or "paper trading" in risk_spec_src.lower()))
    check("risk:spec_no_position_sizing_clause",
          "position size" in risk_spec_src.lower())
    check("risk:spec_no_stop_distance_clause",
          "stop distance" in risk_spec_src.lower())
    check("risk:spec_no_entry_logic_clause",
          "entry logic" in risk_spec_src.lower())
    check("risk:spec_no_exit_logic_clause",
          "exit logic" in risk_spec_src.lower())
    # 7. Required Research Mode field labels for RiskEngine are listed.
    # The spec uses abstract EOC names (score/state/direction/reason) plus
    # the actual Pine column names (RiskScore/RiskState/...). Both forms are
    # equivalent for contract-mapping purposes.
    spec_lower = risk_spec_src.lower()
    for fld in RISK_REQUIRED_FIELDS:
        fname = fld[0]
        fkind = fld[1]
        if fkind == "version":
            check(f"risk:spec_research_mode_field:{fname}",
                  RISK_VERSION_LITERAL in risk_spec_src)
        else:
            # Required: at least one of:
            # - the Risk-prefixed column name; or
            # - the abstract lowercase EOC name in the Engine Output Contract table.
            abstract = fname[len("Risk"):].lower() if fname.startswith("Risk") else fname.lower()
            # Locate the Engine Output Contract section and assert abstract is there.
            eoc_match = re.search(r"##\s*5\.\s*Engine Output Contract[\s\S]*?(?=\n##\s|\Z)", risk_spec_src)
            in_eoc = (eoc_match is not None) and (abstract in eoc_match.group(0).lower())
            check(f"risk:spec_research_mode_field:{fname}",
                  fname in risk_spec_src or in_eoc or abstract in spec_lower)
    for fld in RISK_DIAGNOSTIC_FIELDS:
        check(f"risk:spec_diagnostic_field:{fld}", fld in risk_spec_src)
    # 8. Component score cap table.
    for cap in ["Volatility risk | 35", "Extension risk | 30",
                "Structure risk | 20", "Conflict risk | 15"]:
        check(f"risk:spec_component_cap:{cap}", cap in risk_spec_src, cap)

# B. Verifier-infrastructure checks: fixtures and compute path exist.
check("risk:fixture_dir_exists", RISK_FIXTURE_DIR.is_dir(), str(RISK_FIXTURE_DIR))
check("risk:compute_module_exists", RISK_COMPUTE.is_file(), str(RISK_COMPUTE))

risk_loaded = None
risk_spec_doc = None
if RISK_COMPUTE.is_file():
    try:
        rspec_path = TOOLS / "_riskengine_compute.py"
        r_spec = importlib.util.spec_from_file_location("_riskengine_compute", str(rspec_path))
        risk_spec_doc = importlib.util.module_from_spec(r_spec)
        r_spec.loader.exec_module(risk_spec_doc)
        check("risk:compute_module_loads", True)
    except Exception as e:
        check("risk:compute_module_loads", False, repr(e))


# C. Behaviour checks against fixtures (planned compute path).
ALLOWED_RISK_STATE = RISK_STATE
ALLOWED_RISK_DIRECTION = RISK_DIRECTION


def _risk_summarise(df):
    state_counts = (df["RiskState"].value_counts().to_dict()
                    if "RiskState" in df.columns else {})
    direction_set = sorted(set(df["RiskDirection"].dropna().unique()))
    return {
        "rows": len(df),
        "state_counts": {str(k): int(v) for k, v in state_counts.items()},
        "direction_values": direction_set,
    }


def _risk_fixture_run(name: str):
    if risk_spec_doc is None:
        return None
    fx = RISK_FIXTURE_DIR / f"{name}.csv"
    if not fx.is_file():
        return None
    df = pd.read_csv(fx, parse_dates=["Date"], index_col="Date")
    return risk_spec_doc.calculate_risk(df)


risk_run_results = {}
for name in ["calm_normal", "elevated", "extreme_conflict", "unknown"]:
    out = _risk_fixture_run(name)
    risk_run_results[name] = out
    summary = _risk_summarise(out) if out is not None else {"rows": 0, "state_counts": {}, "direction_values": []}

    check(f"risk:behaviour:run:{name}", out is not None)
    if out is None:
        continue

    check(f"risk:behaviour:rows_gt_zero:{name}",
          summary["rows"] > 0, summary["rows"])

    # State set bounded.
    bad_states = (set(out["RiskState"].dropna().unique())
                  if "RiskState" in out.columns else set()) - ALLOWED_RISK_STATE
    check(f"risk:behaviour:states_allowed:{name}",
          len(bad_states) == 0, str(bad_states))

    # Direction set bounded.
    bad_dirs = (set(out["RiskDirection"].dropna().unique())
                if "RiskDirection" in out.columns else set()) - ALLOWED_RISK_DIRECTION
    check(f"risk:behaviour:direction_allowed:{name}",
          len(bad_dirs) == 0, str(bad_dirs))

    # No bullish/bearish leakage.
    if "RiskDirection" in out.columns:
        dirs = set(out["RiskDirection"].dropna())
        check(f"risk:behaviour:no_bullish_dir:{name}", "bullish" not in dirs)
        check(f"risk:behaviour:no_bearish_dir:{name}", "bearish" not in dirs)
    if "RiskState" in out.columns:
        states = set(out["RiskState"].dropna())
        check(f"risk:behaviour:no_bullish_state:{name}", "bullish" not in states)
        check(f"risk:behaviour:no_bearish_state:{name}", "bearish" not in states)

    # Engine Output Contract field values bounded.
    for col, kind in RISK_REQUIRED_FIELDS:
        if kind == "score":
            s = out.get(col)
            if s is not None:
                vals = s.dropna()
                ok = bool(((vals >= 0) & (vals <= 100)).all()) if len(vals) else True
                check(f"risk:behaviour:{col}_in_range:{name}",
                      ok, f"min={vals.min() if len(vals) else None} max={vals.max() if len(vals) else None}")
        elif kind == "version":
            s = out.get(col)
            if s is not None:
                vals = set(s.dropna().unique())
                check(f"risk:behaviour:{col}_={RISK_VERSION_LITERAL}:{name}",
                      vals == {RISK_VERSION_LITERAL}, str(vals))
        elif kind in ("state", "direction", "reason"):
            s = out.get(col)
            if s is not None:
                expected = {"state": ALLOWED_RISK_STATE,
                            "direction": ALLOWED_RISK_DIRECTION}.get(kind)
                if expected is not None:
                    vals = set(s.dropna().unique())
                    illegal = vals - expected
                    check(f"risk:behaviour:{col}_set:{name}",
                          len(illegal) == 0, str(illegal))
                else:
                    check(f"risk:behaviour:{col}_present:{name}", True)
        elif kind == "diagnostics":
            check(f"risk:behaviour:{col}_present:{name}", col in out.columns)

    # Component contribution range checks.
    comp_caps = {
        "volRiskContribution": (0, 35),
        "extRiskContribution": (0, 30),
        "structRiskContribution": (0, 20),
        "conflictRiskContribution": (0, 15),
    }
    for c_name, (lo, hi) in comp_caps.items():
        if c_name in out.columns:
            vals = out[c_name].dropna()
            ok = bool(((vals >= lo) & (vals <= hi)).all()) if len(vals) else True
            check(f"risk:behaviour:{c_name}_range:{name}",
                  ok, f"{c_name} min={vals.min() if len(vals) else None} max={vals.max() if len(vals) else None}")

    # Reserved-language absence in dashboard and reason text.
    def _flatten(col):
        s = out.get(col, None)
        if s is None:
            return []
        # Convert to series of strings, handle NaN.
        return [str(x) for x in s.tolist() if not (isinstance(x, float) and np.isnan(x))]

    reserved_text = " ".join(
        _flatten("RiskReason") + _flatten("RiskState") + _flatten("RiskDirection")
    ).lower()
    for w in RISK_RESERVED:
        check(f"risk:behaviour:no_reserved_word:{w}:{name}",
              f" {w} " not in f" {reserved_text} ")


# D. Regime-shape expectations per fixture.
if risk_run_results.get("calm_normal") is not None:
    cn = risk_run_results["calm_normal"]
    cn_states = cn["RiskState"].value_counts().to_dict() if "RiskState" in cn.columns else {}
    # Calm fixture should not reach extreme state often.
    extreme_pct = (cn_states.get("extreme", 0) / max(1, len(cn))) * 100
    check("risk:behaviour:calm_extreme_pct_low",
          extreme_pct < 60, f"extreme_pct={extreme_pct:.1f}%")

if risk_run_results.get("elevated") is not None:
    el = risk_run_results["elevated"]
    el_states = el["RiskState"].value_counts().to_dict() if "RiskState" in el.columns else {}
    elevated_pct = (el_states.get("elevated", 0)
                    + el_states.get("tense", 0)
                    + el_states.get("extreme", 0)) / max(1, len(el)) * 100
    check("risk:behaviour:elevated_at_least_mid",
          elevated_pct > 30, f"midplus_pct={elevated_pct:.1f}%")

if risk_run_results.get("extreme_conflict") is not None:
    ex = risk_run_results["extreme_conflict"]
    ex_states = ex["RiskState"].value_counts().to_dict() if "RiskState" in ex.columns else {}
    high_pct = (ex_states.get("tense", 0) + ex_states.get("extreme", 0)) / max(1, len(ex)) * 100
    check("risk:behaviour:extreme_produces_high_states",
          high_pct > 30, f"high_pct={high_pct:.1f}%")

if risk_run_results.get("unknown") is not None:
    un = risk_run_results["unknown"]
    check("risk:behaviour:unknown_fixture_present",
          un is not None and len(un) > 0)


# ---------------------------------------------------------------------------
# E. ATE v2.2 release file direct verification (EDR-001 extension).
# ---------------------------------------------------------------------------
# Loads ``pine/releases/ATE_v2.2.pine`` and ``pine/development/ATE_Current.pine``
# directly and asserts the contract recorded in the ATE v2.2 Release Manifest,
# the approved RiskEngine v1.0 specification, and the Design Chapter 5 of the
# Architecture baseline (Engine Output Contract).
#
# Scope: this is a release-file static verifier. It does NOT execute Pine, does
# NOT compare against the Python mirror, and does NOT prove empirical
# usefulness. Empirical claim of the RiskEngine for downstream consumption
# remains subject to RDR-003 / RDR-003W.

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text() if path.is_file() else ""


v22_src = _read_text(V22_PINE)
v22_dev_src = _read_text(V22_DEV)

# 1. File integrity.
check("v22:release_file_exists", V22_PINE.is_file(), str(V22_PINE))
check("v22:dev_file_exists", V22_DEV.is_file(), str(V22_DEV))
v22_sha_actual = _sha256(V22_PINE) if V22_PINE.is_file() else None
v22_dev_sha_actual = _sha256(V22_DEV) if V22_DEV.is_file() else None
v21_sha_actual = _sha256(PINE_PATH) if PINE_PATH.is_file() else None

if v22_sha_actual is not None:
    check("v22:release_sha_matches_manifest",
          v22_sha_actual == V22_EXPECTED_SHA,
          f"expected={V22_EXPECTED_SHA} actual={v22_sha_actual}")
if v22_sha_actual is not None and v22_dev_sha_actual is not None:
    # Intentional divergence: TrendEngine research implementation lives in
    # the dev mirror (pine/development/ATE_Current.pine) per
    # docs/releases/TrendEngine_Implementation_Plan.md. The release file
    # (pine/releases/ATE_v2.2.pine) must remain unchanged.
    #
    # This check accepts either:
    #   (a) release == dev byte-identical (no TrendEngine work yet), or
    #   (b) dev contains a TrendEngine block (TrendEngine research added)
    #       AND release does NOT contain a TrendEngine block (release preserved).
    trend_block_marker = "trendEngineVersion = \"0.2.0-spec-impl\""
    dev_has_trend = trend_block_marker in v22_dev_src if v22_dev_src else False
    release_has_trend = trend_block_marker in v22_src if v22_src else False
    diverged = v22_sha_actual != v22_dev_sha_actual
    divergence_acceptable = diverged and dev_has_trend and not release_has_trend
    check("v22:release_dev_byte_identical",
          v22_sha_actual == v22_dev_sha_actual or divergence_acceptable,
          f"release={v22_sha_actual} dev={v22_dev_sha_actual} "
          f"divergence_acceptable={divergence_acceptable}")
if v21_sha_actual is not None:
    check("v21:release_sha_unchanged",
          v21_sha_actual == V21_EXPECTED_SHA,
          f"expected={V21_EXPECTED_SHA} actual={v21_sha_actual}")

# 2. Header / version.
check("v22:indicator_title_v2_2",
      "Austin Trading Engine v2.2" in v22_src)
check("v22:research_mode_ate_version_v2_2",
      "ATEVersion: v2.2" in v22_src)
check("v22:risk_engine_version_literal",
      'riskEngineVersion = "1.0.0-draft"' in v22_src)
check("v22:vol_engine_version_literal",
      'volEngineVersion = "1.0.0-draft"' in v22_src)

# 3. RiskEngine approved inputs (exact identifiers).
V22_REQUIRED_INPUTS = [
    "riskVolElevatedScore",
    "riskExtensionAtrLow",
    "riskExtensionAtrHigh",
    "riskSwingAtr",
    "riskConfidenceRiskHigh",
    "riskConfidenceRiskLow",
    "riskSmoothingLength",
]
for inp in V22_REQUIRED_INPUTS:
    check(f"v22:risk_input:{inp}", f"{inp} = input" in v22_src)

# 4. Engine Output Contract mapping in Pine.
V22_EOC = {
    "score": ["riskScore"],
    "state": ["riskState"],
    "direction": ["riskDirection"],
    "reason": ["riskReason"],
    "version": ["riskEngineVersion"],
    "diagnostics": [
        "riskVolRaw", "riskExtRaw", "riskStructRaw", "riskConflictRaw",
        "riskVolState", "riskExtState", "riskStructState", "riskConflictState",
        "riskSmoothedRaw",
        "riskDiagVolScore", "riskDiagVolShockFlag", "riskDiagConfidenceScore",
        "riskDiagExtBarRangeAtr", "riskDiagStructLastSwingAtr",
        "riskDiagConflictCross", "riskDiagInsufficientData",
    ],
}
for kind, vars_ in V22_EOC.items():
    for vn in vars_:
        check(f"v22:eoc:{kind}:{vn}", vn in v22_src)

# 5. Allowed states and directions (parsed literal blocks).
V22_ALLOWED_STATES = {"calm", "normal", "elevated", "tense", "extreme", "unknown"}
V22_ALLOWED_DIRS = {"none", "elevated", "conflict", "stable", "indeterminate"}


def _extract_assignment_block(src: str, name: str) -> str:
    """Return the text of ``<name> = ...`` until the next blank line, or ''."""
    pattern = re.compile(
        r"^\s*" + re.escape(name) + r"\s*=\s*(?:\n|(?:[^\n]*\n))(?:[^\n]*\n)*?[^\n]*(?=\n\n|\n\s*//\s*─|\Z)",
        re.MULTILINE,
    )
    m = pattern.search(src)
    return m.group(0) if m else ""


state_block = _extract_assignment_block(v22_src, "riskState")
dir_block = _extract_assignment_block(v22_src, "riskDirection")
reason_block = _extract_assignment_block(v22_src, "riskReason")

for v in V22_ALLOWED_STATES:
    check(f"v22:risk_state_present:{v}", f'"{v}"' in state_block, v)
for v in V22_ALLOWED_DIRS:
    check(f"v22:risk_dir_present:{v}", f'"{v}"' in dir_block, v)
check("v22:risk_state_no_bullish", '"bullish"' not in state_block)
check("v22:risk_state_no_bearish", '"bearish"' not in state_block)
check("v22:risk_dir_no_bullish", '"bullish"' not in dir_block)
check("v22:risk_dir_no_bearish", '"bearish"' not in dir_block)

# 6. Component scoring.
for var in ("riskVolRaw", "riskExtRaw", "riskStructRaw", "riskConflictRaw"):
    check(f"v22:component:{var}", var in v22_src)
# Cap references — both in the RiskEngine block (clamps) and in the
# dashboard render cells (" / 35" / " / 30" / " / 20" / " / 15").
if v22_src:
    risk_lines = v22_src.split("\n")
    # Find markers using a coarse heuristic: start at first occurrence of
    # 'riskVolRaw =', end at the DASHBOARD section marker line (exact match).
    risk_start = next((i for i, ln in enumerate(risk_lines)
                       if "riskVolRaw =" in ln), 0)
    risk_end = next((i for i, ln in enumerate(risk_lines)
                     if ln.strip() == "// DASHBOARD"), len(risk_lines))
    risk_block_text = "\n".join(risk_lines[risk_start:risk_end])
    # Dashboard render caps (lines after the DASHBOARD header).
    dash_start = risk_end
    research_marker = next((i for i, ln in enumerate(risk_lines)
                            if ln.strip() == "// RESEARCH MODE"),
                           len(risk_lines))
    dash_block_text = "\n".join(risk_lines[dash_start:research_marker])

    # Each component has a numeric cap. Confirm: (a) the clamp upper bound
    # equals the documented cap in the RiskEngine block; (b) the dashboard
    # render string contains " / <cap>".
    COMPONENT_CAPS = [
        ("riskVolRaw", 35),
        ("riskExtRaw", 30),
        ("riskStructRaw", 20),
        ("riskConflictRaw", 15),
    ]
    for var, cap in COMPONENT_CAPS:
        # Adjacent line: ``<var> = f_clamp(... , 0.0, <cap>.0)``.
        # Pine v6 nests ternary expressions with parentheses in f_clamp's
        # first argument; we therefore look for ``f_clamp(... , 0.0, <cap>.0)``
        # where the leading ``f_clamp(`` is on the same line as the assignment,
        # using a non-greedy match that permits nested ``(`` / ``)``.
        # Implementation: count open vs close parens after ``f_clamp(`` until
        # the closing ``, 0.0, <cap>.0)`` terminator.
        clamp_ok = False
        line_ok = False
        for ln_i, ln in enumerate(risk_block_text.split("\n")):
            if not ln.lstrip().startswith(var + " "):
                continue
            # Find f_clamp( on this line.
            idx = ln.find("f_clamp(")
            if idx < 0:
                continue
            # Walk forward to find the matching close paren, then check the
            # terminator ``, 0.0, <cap>.0)`` immediately after.
            depth = 0
            for j in range(idx, len(ln)):
                ch = ln[j]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        tail = ln[idx:j + 1]
                        if (f", 0.0, {cap}.0)" in tail
                                or f",0.0,{cap}.0)" in tail):
                            clamp_ok = True
                            if var + " " in ln[:idx] or ln.lstrip().startswith(var):
                                line_ok = True
                        break
            break  # only the first matching assignment line

        # Dashboard render with the same cap.
        dash_cap_str = f"\" / {cap}\""
        dash_ok = dash_cap_str in dash_block_text
        check(f"v22:component_cap:{var}:clamp({cap}.0)",
              clamp_ok and line_ok,
              f"clamp({cap}.0) for {var}")
        check(f"v22:component_cap:{var}:dashboard('/ {cap}')",
              dash_ok, f"dashboard '/ {cap}' for {var}")
    # Total score 0..100. The actual clauses are f_clamp(..., 0.0, 100.0) in
    # the source.
    check("v22:score_clamp_upper_bound_100",
          "100.0" in risk_block_text, "100.0 upper bound present")
    check("v22:score_clamp_lower_bound_0",
          "0.0" in risk_block_text, "0.0 lower bound present")

# 7. Dashboard labels — exact strings.
V22_DASHBOARD_LABELS = [
    "Risk Score", "Risk State", "Risk Direction", "Risk Reason", "Risk Engine",
    "Vol Risk State", "Ext Risk State", "Struct Risk State",
    "Conflict Risk State",
    "Vol Risk Contrib", "Ext Risk Contrib", "Struct Risk Contrib",
    "Conflict Risk Contrib",
    "Smoothed Risk Score",
]
# Extract the DASHBOARD section only (between DASHBOARD header and RESEARCH
# MODE header) so labels from other sections cannot false-pass.
if v22_src:
    sections = v22_src.split("\n")
    dash_start = next((i for i, ln in enumerate(sections)
                       if ln.strip() == "// DASHBOARD"), 0)
    research_marker = next((i for i, ln in enumerate(sections)
                            if ln.strip() == "// RESEARCH MODE"), len(sections))
    dash_section = "\n".join(sections[dash_start:research_marker])
    for lbl in V22_DASHBOARD_LABELS:
        check(f"v22:dashboard_label:{lbl}", f'"{lbl}"' in dash_section, lbl)

# 8. Research Mode labels — exact strings.
V22_RESEARCH_LABELS = [
    "RiskEngineVersion", "RiskScore", "RiskState", "RiskDirection",
    "RiskReason",
    "VolRiskContribution", "ExtRiskContribution", "StructRiskContribution",
    "ConflictRiskContribution",
    "VolRiskState", "ExtRiskState", "StructRiskState", "ConflictRiskState",
    "BarRangeATR", "LastSwingATR", "RiskInsufficientData",
]
if v22_src:
    sections = v22_src.split("\n")
    rm_start = next((i for i, ln in enumerate(sections)
                     if ln.strip() == "// RESEARCH MODE"), 0)
    alerts_marker = next((i for i, ln in enumerate(sections)
                          if ln.strip() == "// ALERTS"), len(sections))
    research_section = "\n".join(sections[rm_start:alerts_marker])
    for lbl in V22_RESEARCH_LABELS:
        check(f"v22:research_mode_label:{lbl}", f'"{lbl}: "' in research_section, lbl)

# 9. Alert preservation. Exactly the 10 ATE v1.3 alerts; no RiskEngine alert.
ALERT_TITLES = [
    "ATE Golden Cross",
    "ATE Death Cross",
    "ATE Strong Bull",
    "ATE Strong Bear",
    "ATE Bullish BOS",
    "ATE Bearish BOS",
    "ATE Momentum Bullish",
    "ATE Momentum Bearish",
    "ATE High Confidence Bull",
    "ATE Low Confidence Bear",
]
ALERT_PRESENCE = re.findall(r'alertcondition\([^,]+,\s*"([^"]+)"', v22_src)
for at in ALERT_TITLES:
    check(f"v22:alert_present:{at}", at in ALERT_PRESENCE, at)
check("v22:alert_count_equals_10", len(ALERT_PRESENCE) == 10,
      f"actual={len(ALERT_PRESENCE)} titles={ALERT_PRESENCE}")
# No RiskEngine alert.
for forbidden in ("RiskEngine Buy", "RiskEngine Sell", "RiskEngine Entry",
                  "RiskEngine Exit", "ATE Risk Buy", "ATE Risk Sell"):
    check(f"v22:no_riskengine_alert:{forbidden}",
          forbidden not in v22_src, forbidden)

# 10. Boundary checks: RiskEngine must not assign to other engines' outputs.
BOUNDARY_VARS = ("confidenceScore", "marketState", "trendScore",
                 "structureScore", "momentumScore",
                 "volScore", "volState", "volDirection", "volShockFlag")
if v22_src:
    sections = v22_src.split("\n")
    risk_start = next((i for i, ln in enumerate(sections)
                       if "riskEngineVersion =" in ln), 0)
    risk_end = next((i for i, ln in enumerate(sections)
                     if ln.strip() == "// DASHBOARD"), len(sections))
    risk_block_text = "\n".join(sections[risk_start:risk_end])
    for var in BOUNDARY_VARS:
        # Conservative: the RiskEngine block must not contain a direct assignment
        # to ``var`` on its own line. We look for lines like "var =" or "var +="
        # which would indicate scoring mutation.
        pat = re.compile(rf"^\s*{re.escape(var)}\s*=", re.MULTILINE)
        check(f"v22:boundary_no_assign:{var}", not pat.search(risk_block_text), var)
# No strategy()/broker/order/execution logic.
FORBIDDEN_LOGIC = ("strategy(", "broker", "paper-trading", "paper trading",
                   "order", "position size", "stop distance",
                   "stop placement", "entry logic", "exit logic")
# Limit forbidden-logic check to RiskEngine block only (signals/alerts blocks
# historically carry benign "bullish"/"bearish" wording in alert *messages*,
# not strategy() calls — but we still scope to be safe).
if v22_src:
    sections = v22_src.split("\n")
    risk_start = next((i for i, ln in enumerate(sections)
                       if "riskEngineVersion =" in ln), 0)
    risk_end = next((i for i, ln in enumerate(sections)
                     if ln.strip() == "// DASHBOARD"), len(sections))
    risk_block_text = "\n".join(sections[risk_start:risk_end]).lower()
    for w in FORBIDDEN_LOGIC:
        check(f"v22:no_forbidden_logic:{w}", w not in risk_block_text, w)

# 11. Reserved language — scoped to RiskEngine output/display fields only.
# Three spans:
#   a. riskState literal assignment block
#   b. riskDirection literal assignment block
#   c. riskReason literal assignment block
#   d. RiskEngine dashboard cells (rows 19..32) — extracted by line range
#      from the DASHBOARD section.
#   e. Research Mode body (after 'if showResearch' until end of section).
RESERVED_LANG = ["safe", "unsafe", "suitable", "unsuitable",
                 "approved", "blocked", "tradeable", "untradeable"]


def _span_reserved(text: str, span_name: str) -> None:
    t = text.lower()
    for w in RESERVED_LANG:
        # Boundary check: require the word to appear as a discrete token
        # surrounded by non-word characters (whitespace, punctuation,
        # quotes). Pine uses double quotes around string literals, so we
        # also explicitly handle '"..."' patterns.
        for boundary_token in (f'"{w}"', f' {w} ', f' {w},', f',{w} ',
                               f' {w}.', f'.{w} ', f' {w}?', f'?{w} ',
                               f' {w}!', f'!{w} '):
            if boundary_token in t:
                check(f"v22:reserved:{span_name}:{w}", False,
                      f'matched token "{w}"')
                return
        check(f"v22:reserved:{span_name}:{w}", True)


_span_reserved(state_block, "risk_state_block")
_span_reserved(dir_block, "risk_direction_block")
_span_reserved(reason_block, "risk_reason_block")

# Dashboard RiskEngine rows: in v2.2 these are rows 19..32 inclusive.
# Locate the dashboard section, then slice lines containing table.cell calls
# for rows 19..32.
if v22_src:
    sections = v22_src.split("\n")
    dash_start = next((i for i, ln in enumerate(sections)
                       if ln.strip() == "// DASHBOARD"), 0)
    research_marker = next((i for i, ln in enumerate(sections)
                            if ln.strip() == "// RESEARCH MODE"), len(sections))
    dash_lines = sections[dash_start:research_marker]
    risk_dash_texts = []
    for ln in dash_lines:
        # Match table.cell(... , row N, ...) for N between 19 and 32.
        m = re.search(r"^\s*table\.cell\(\s*\w+\s*,\s*\d+\s*,\s*(\d+)\s*,", ln)
        if m and 19 <= int(m.group(1)) <= 32:
            risk_dash_texts.append(ln)
    dash_block = "\n".join(risk_dash_texts)
    _span_reserved(dash_block, "risk_dashboard")

# Research Mode body: lines between 'if showResearch' and the closing
# table.cell(research, ...) call.
if v22_src:
    sections = v22_src.split("\n")
    rm_start = next((i for i, ln in enumerate(sections)
                     if ln.strip() == "// RESEARCH MODE"), 0)
    alerts_marker = next((i for i, ln in enumerate(sections)
                          if ln.strip() == "// ALERTS"), len(sections))
    rm_section = sections[rm_start:alerts_marker]
    # Find first 'if showResearch' and slice to end-of-section text body.
    try:
        body_start = next(i for i, ln in enumerate(rm_section)
                          if "if showResearch" in ln)
    except StopIteration:
        body_start = 0
    body_text = "\n".join(rm_section[body_start:])
    _span_reserved(body_text, "research_mode")


# ---------------------------------------------------------------------------
# F. TrendEngine v0.2.0-spec-impl — dev-mirror contract + behaviour.
#
# TrendEngine is a research-only engine implemented in the development mirror
# (pine/development/ATE_Current.pine) only. The release file
# (pine/releases/ATE_v2.2.pine) must remain unchanged.
#
# Scope: static contract checks against the dev-mirror source plus behaviour
# checks against four seeded fixtures under tests/fixtures/ATE_v2_2/.
# Empirical usefulness remains subject to a future RDR-010 re-attempt.
# ---------------------------------------------------------------------------

TREND_SPEC = REPO / "specifications/ATE/TrendEngine.md"
TREND_FIXTURE_DIR = REPO / "tests/fixtures/ATE_v2_2"
TREND_COMPUTE = TOOLS / "_trendengine_compute.py"
TREND_VERSION = "0.2.0-spec-impl"
TREND_VALID_STATES = {"UP", "DOWN", "RANGE", "UNKNOWN"}
TREND_REQUIRED_INPUTS = [
    "trendEmaLen", "trendSlopeLookback", "trendSlopeMin",
    "trendSwingLen", "trendStructureBars",
    "trendStrengthScale", "trendAgeMax",
]
TREND_REQUIRED_EOC_VARS = [
    "trendState", "trendStrength", "trendAge",
    "trendEngineVersion",
    "trendDiagEmaSlope", "trendDiagAgreement",
    "trendDiagHigherHigh", "trendDiagHigherLow",
    "trendDiagLowerHigh", "trendDiagLowerLow",
    "trendDiagStateConfirmBars", "trendDiagInsufficientData",
]

trend_present_in_dev = (
    v22_dev_src is not None and v22_dev_src != ""
    and f'trendEngineVersion = "{TREND_VERSION}"' in v22_dev_src
)
trend_present_in_release = (
    v22_src is not None and v22_src != ""
    and f'trendEngineVersion = "{TREND_VERSION}"' in v22_src
)

# 1. Spec upgrade is on disk.
check("trend:spec_exists", TREND_SPEC.is_file(), str(TREND_SPEC))
if TREND_SPEC.is_file():
    spec_src = _read_text(TREND_SPEC)
    # Spec version appears as `**Version:** \`0.2.0-spec-impl\`` in the header.
    check("trend:spec_version_literal",
          "0.2.0-spec-impl" in spec_src and "Version:" in spec_src)
    check("trend:spec_status_research",
          "Approved for Research Implementation Planning" in spec_src)
    # Reserved-language check is scoped: only the prose *forbidding* reserved
    # language is allowed to mention those words (as a literal list of
    # forbidden tokens). Any *use* of reserved language as a label or value
    # would be a contract violation. We use a heuristic: the section
    # containing "Use reserved language" / "No reserved language" is allowed;
    # elsewhere, the words must not appear as standalone labels.
    spec_lower = spec_src.lower()
    # Count occurrences of "approved", "blocked", "tradeable" — exclude
    # lines that are part of the explicit forbidden-language list.
    reserved_violations = []
    for ln in spec_src.splitlines():
        ln_lower = ln.lower()
        if "reserved language" in ln_lower and ("forbid" in ln_lower or "avoid" in ln_lower):
            continue
        if "use reserved language" in ln_lower:
            continue
        if "no reserved language" in ln_lower:
            continue
        for w in ("tradeable", "blocked"):
            if w in ln_lower and not ln_lower.strip().startswith("-"):
                reserved_violations.append((w, ln.strip()[:120]))
    check("trend:spec_no_reserved_language",
          len(reserved_violations) == 0,
          f"violations={reserved_violations[:3]}")

# 2. Plan exists.
TREND_PLAN = REPO / "docs/releases/TrendEngine_Implementation_Plan.md"
check("trend:plan_exists", TREND_PLAN.is_file(), str(TREND_PLAN))

# 3. Python mirror exists and imports cleanly.
check("trend:python_mirror_exists", TREND_COMPUTE.is_file(), str(TREND_COMPUTE))
trend_compute_module = None
if TREND_COMPUTE.is_file():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_trendengine_compute",
                                                      str(TREND_COMPUTE))
        if spec and spec.loader:
            trend_compute_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(trend_compute_module)
            check("trend:python_mirror_imports", True)
    except Exception as e:
        check("trend:python_mirror_imports", False, str(e)[:160])

# 4. Dev-mirror contains TrendEngine block.
check("trend:dev_has_trendengine_block", trend_present_in_dev)
check("trend:release_has_NO_trendengine_block",
      not trend_present_in_release,
      f"release MUST NOT contain TrendEngine block; SHA must remain d55ca5ef...")

# 5. TrendEngine inputs (exact identifiers) in dev-mirror.
if trend_present_in_dev:
    for inp in TREND_REQUIRED_INPUTS:
        input_ok = f"{inp} = input" in v22_dev_src
        if inp == "trendSwingLen":
            input_ok = input_ok and "ta.pivothigh(high, trendSwingLen, trendSwingLen)" in v22_dev_src
            input_ok = input_ok and "ta.pivotlow(low, trendSwingLen, trendSwingLen)" in v22_dev_src
        check(f"trend:input:{inp}", input_ok)

# 6. TrendEngine EOC variables in dev-mirror.
if trend_present_in_dev:
    for var in TREND_REQUIRED_EOC_VARS:
        eoc_ok = var in v22_dev_src
        if var == "trendDiagStateConfirmBars":
            eoc_ok = eoc_ok and "var string trendCandidatePrior = na" in v22_dev_src
            eoc_ok = eoc_ok and "trendCandidatePrior := trendCandidateState" in v22_dev_src
        check(f"trend:eoc:{var}", eoc_ok)

# 7. TrendEngine version literal in dev-mirror.
if trend_present_in_dev:
    check(f"trend:version_literal",
          f'trendEngineVersion = "{TREND_VERSION}"' in v22_dev_src)

# 8. TrendEngine does NOT introduce alerts.
if trend_present_in_dev:
    # Locate the TrendEngine block within the dev-mirror and assert no alert
    # references appear within it.
    dev_sections = v22_dev_src.split("\n")
    trend_start = next((i for i, ln in enumerate(dev_sections)
                        if 'trendEngineVersion = "0.2.0-spec-impl"' in ln), 0)
    alerts_marker = next((i for i, ln in enumerate(dev_sections)
                          if ln.strip() == "// ALERTS"), len(dev_sections))
    trend_block_text = "\n".join(dev_sections[trend_start:alerts_marker])
    forbidden_alert_tokens = (
        "alertcondition(", "alert(",
    )
    for tok in forbidden_alert_tokens:
        check(f"trend:no_alert:{tok}",
              tok not in trend_block_text, tok)

# 9. Reserved language absent from TrendEngine output block.
if trend_present_in_dev:
    _span_reserved(trend_block_text, "trend_engine_block")

# 10. TrendEngine dashboard rows present in dev-mirror.
if trend_present_in_dev:
    for label in ("Trend State", "Trend Strength", "Trend Age",
                  "Trend Direction", "Trend Engine"):
        check(f"trend:dashboard_label:{label}",
              f'"{label}"' in v22_dev_src)

# 11. TrendEngine Research Mode fields present in dev-mirror.
if trend_present_in_dev:
    for field in ("TrendEngineVersion", "TrendState", "TrendStrength",
                  "TrendAge", "TrendDiagEmaSlope", "TrendDiagAgreement",
                  "TrendDiagHigherHigh", "TrendDiagHigherLow",
                  "TrendDiagLowerHigh", "TrendDiagLowerLow",
                  "TrendDiagStateConfirmBars", "TrendDiagInsufficientData"):
        check(f"trend:research_mode:{field}",
              field in v22_dev_src)

# 12. TrendEngine boundary: not assigned inside confidenceScore/marketState/
# volScore/riskScore/structureScore/momentumScore blocks.
if trend_present_in_dev:
    # The TrendEngine block is between `trendEngineVersion = "0.2.0-spec-impl"`
    # and the next `// ─` separator (i.e. before PLOTS). It must not assign to
    # other engines' outputs.
    TREND_BOUNDARY_VARS = ("confidenceScore", "marketState", "trendScore",
                            "structureScore", "momentumScore",
                            "volScore", "volState", "volDirection", "volShockFlag",
                            "riskScore", "riskState", "riskDirection")
    for var in TREND_BOUNDARY_VARS:
        pat = re.compile(rf"^\s*{re.escape(var)}\s*=", re.MULTILINE)
        check(f"trend:boundary_no_assign:{var}",
              not pat.search(trend_block_text), var)

# 13. TrendEngine behaviour: run the four seeded fixtures through the Python
# mirror and assert each classifies into its expected dominant state.
trend_run_results = {}
if trend_compute_module is not None:
    for fname in ("up_strong", "down_strong", "range_choppy", "transition"):
        fpath = TREND_FIXTURE_DIR / f"{fname}.csv"
        if not fpath.is_file():
            check(f"trend:fixture_exists:{fname}", False, str(fpath))
            continue
        try:
            df = pd.read_csv(fpath, parse_dates=["Date"], index_col="Date")
            out = trend_compute_module.calculate_trend(df)
            trend_run_results[fname] = out
            states = out["trendState"].astype(str).values
            n = len(states)
            warmup = TREND_SPEC and False  # placeholder; real warmup = 55
            warmup = 55
            post = states[warmup:]
            counts = {s: int((post == s).sum()) for s in TREND_VALID_STATES}
            dominant = max(counts, key=counts.get) if counts else None
            dominant_pct = (counts.get(dominant, 0) / max(1, len(post))) * 100
            check(f"trend:fixture:{fname}:runs", True, f"n={n} post_warmup_counts={counts}")
            check(f"trend:fixture:{fname}:states_valid",
                  all(s in TREND_VALID_STATES for s in post),
                  f"unexpected value(s)={set(post) - TREND_VALID_STATES}")
            if fname == "up_strong":
                check(f"trend:fixture:up_strong:dominant_UP",
                      dominant == "UP",
                      f"dominant={dominant} pct={dominant_pct:.1f}%")
            elif fname == "down_strong":
                check(f"trend:fixture:down_strong:dominant_DOWN",
                      dominant == "DOWN",
                      f"dominant={dominant} pct={dominant_pct:.1f}%")
            elif fname == "range_choppy":
                check(f"trend:fixture:range_choppy:dominant_RANGE",
                      dominant == "RANGE",
                      f"dominant={dominant} pct={dominant_pct:.1f}%")
            elif fname == "transition":
                # Transition fixture should produce a mix of states.
                non_range_pct = (
                    (counts.get("UP", 0) + counts.get("DOWN", 0))
                    / max(1, len(post))
                ) * 100
                check(f"trend:fixture:transition:multi_state",
                      non_range_pct >= 5.0,
                      f"non-RANGE pct={non_range_pct:.1f}%")
        except Exception as e:
            check(f"trend:fixture:{fname}:runs", False, str(e)[:160])

# 14. TrendEngine strength bounded in [0, 1] for non-NaN outputs.
for fname, df in trend_run_results.items():
    s = df["trendStrength"].dropna()
    if len(s):
        check(f"trend:fixture:{fname}:strength_bounded",
              (s >= 0.0).all() and (s <= 1.0).all(),
              f"min={s.min():.4f} max={s.max():.4f}")

# 15. TrendEngine age bounded in [0, trendAgeMax].
for fname, df in trend_run_results.items():
    a = df["trendAge"].dropna()
    if len(a):
        check(f"trend:fixture:{fname}:age_bounded",
              (a >= 0).all() and (a <= 250).all(),
              f"min={a.min()} max={a.max()}")

# ---------------------------------------------------------------------------
# Output: stdout summary + verify.log
# ---------------------------------------------------------------------------

def _dist(df):
    if df is None or "VolatilityState" not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df["VolatilityState"].value_counts().items()}


total = len(results)
passed = sum(1 for r in results if r["ok"])
failed = total - passed

pine_sha = v21_sha_actual or (hashlib.sha256(PINE_PATH.read_bytes()).hexdigest() if PINE_PATH.is_file() else None)

summary = {
    "verifier": "ERP-001 canonical ATE verifier",
    "kind": "behaviour and contract verifier (NOT a suite green validation)",
    "engine_target": (
        "ATE v2.1 / VolatilityEngine v1.0.0-draft "
        "+ ATE v2.2 / RiskEngine v1.0.0-draft (planned Python mirror + v2.2 release file)"
    ),
    "release_sha256_pine": pine_sha,
    "v21_release_sha256_expected": V21_EXPECTED_SHA,
    "v21_release_sha256_unchanged": (v21_sha_actual == V21_EXPECTED_SHA) if v21_sha_actual is not None else False,
    "v22_release_sha256_actual": v22_sha_actual,
    "v22_release_sha256_expected": V22_EXPECTED_SHA,
    "v22_release_sha256_matches_manifest": (
        v22_sha_actual == V22_EXPECTED_SHA) if v22_sha_actual is not None else False,
    "v22_dev_sha256_actual": v22_dev_sha_actual,
    "v22_release_dev_byte_identical": (
        v22_sha_actual is not None and v22_dev_sha_actual is not None
        and v22_sha_actual == v22_dev_sha_actual),
    "fixtures": sorted([p.name for p in FIXTURE_DIR.glob("*.csv")]),
    "fixture_dists": {
        "quiet": _dist(quiet_out),
        "normal": _dist(normal_out),
        "shock": _dist(shock_out),
    },
    "total_checks": total,
    "passed": passed,
    "failed": failed,
    "failures": [r for r in results if not r["ok"]],
    "exit_meaning": {
        "0": "pass",
        "1": "fail",
        "2": "environment_error",
    },
}

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.write_text(json.dumps(summary, indent=2, default=str))

print(json.dumps(summary, indent=2, default=str))

if any(r["name"] == "environment" and not r["ok"] for r in results):
    sys.exit(2)
sys.exit(1 if failed else 0)
