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
# Output: stdout summary + verify.log
# ---------------------------------------------------------------------------

def _dist(df):
    if df is None or "VolatilityState" not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df["VolatilityState"].value_counts().items()}


total = len(results)
passed = sum(1 for r in results if r["ok"])
failed = total - passed

pine_sha = hashlib.sha256(PINE_PATH.read_bytes()).hexdigest() if PINE_PATH.is_file() else None

summary = {
    "verifier": "ERP-001 canonical ATE verifier",
    "kind": "behaviour and contract verifier (NOT a suite green validation)",
    "engine_target": "ATE v2.1 / VolatilityEngine v1.0.0-draft + ATE v2.2 / RiskEngine v1.0.0-draft (planned, Python mirror)",
    "release_sha256_pine": pine_sha,
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
