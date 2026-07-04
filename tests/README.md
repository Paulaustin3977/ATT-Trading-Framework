# ATE Tests and Verification

This directory houses verification infrastructure for the Austin Trading Engine (ATE) releases.

`tools/scripts/verify_ate.py` is the canonical verification entry point created by ERP-001 / EDR-001.

## What this verifier does

The canonical verifier at `tools/scripts/verify_ate.py` operates on the **active ATE release files**, the **approved specifications**, and the **versioned fixtures** in this directory.

Current scope:

1. **ATE v2.1 VolatilityEngine compute path** against fixtures under `tests/fixtures/ATE_v2_1/` (legacy coverage; unchanged).
2. **ATE v2.2 RiskEngine planned compute path** against fixtures under `tests/fixtures/ATE_v2_2/` (Python mirror).
3. **ATE v2.2 release-file direct verification** (EDR-001 extension): directly loads `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` and asserts the contract recorded in the ATE v2.2 Release Manifest and the approved RiskEngine v1.0 specification. This includes file-integrity SHA verification, header/version, approved inputs, Engine Output Contract mapping, allowed states and directions, component cap clamps, dashboard labels, Research Mode labels, alert preservation, boundary discipline, and reserved-language absence.

### ATE v2.2 release-file direct checks (new)

Loads `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` and asserts:

- File integrity:
  - Both files exist.
  - Release SHA-256 matches the value recorded in `docs/releases/ATE_v2.2_Release_Manifest.md` (currently `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`).
  - Development mirror is byte-identical to release.
  - ATE v2.1 release file SHA-256 is unchanged at `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`.
- Header / version:
  - Indicator title contains `Austin Trading Engine v2.2`.
  - Research Mode `ATEVersion: v2.2`.
  - `riskEngineVersion = "1.0.0-draft"` literal in the source.
  - `volEngineVersion = "1.0.0-draft"` literal in the source.
- RiskEngine approved inputs (exact identifiers):
  `riskVolElevatedScore`, `riskExtensionAtrLow`, `riskExtensionAtrHigh`, `riskSwingAtr`, `riskConfidenceRiskHigh`, `riskConfidenceRiskLow`, `riskSmoothingLength`.
- RiskEngine Engine Output Contract variables:
  `riskScore`, `riskState`, `riskDirection`, `riskReason`, `riskEngineVersion`, plus component raw scores (`riskVolRaw`, `riskExtRaw`, `riskStructRaw`, `riskConflictRaw`), component states (`riskVolState`, `riskExtState`, `riskStructState`, `riskConflictState`), smoothed raw (`riskSmoothedRaw`), and diagnostic variables (`riskDiagVolScore`, `riskDiagVolShockFlag`, `riskDiagConfidenceScore`, `riskDiagExtBarRangeAtr`, `riskDiagStructLastSwingAtr`, `riskDiagConflictCross`, `riskDiagInsufficientData`).
- Allowed RiskState literal values in the assignment block: `calm`, `normal`, `elevated`, `tense`, `extreme`, `unknown`. No `bullish`/`bearish`.
- Allowed RiskDirection literal values in the assignment block: `none`, `elevated`, `conflict`, `stable`, `indeterminate`. No `bullish`/`bearish`.
- Component cap clamps in the RiskEngine block:
  `f_clamp(..., 0.0, 35.0)`, `f_clamp(..., 0.0, 30.0)`, `f_clamp(..., 0.0, 20.0)`, `f_clamp(..., 0.0, 15.0)` for `riskVolRaw`, `riskExtRaw`, `riskStructRaw`, `riskConflictRaw` respectively.
- Component dashboard caps render `"/ 35"`, `"/ 30"`, `"/ 20"`, `"/ 15"`.
- Total `riskScore` clamped to `[0.0, 100.0]`.
- Dashboard labels present in the DASHBOARD section:
  `Risk Score`, `Risk State`, `Risk Direction`, `Risk Reason`, `Risk Engine`,
  `Vol Risk State`, `Ext Risk State`, `Struct Risk State`, `Conflict Risk State`,
  `Vol Risk Contrib`, `Ext Risk Contrib`, `Struct Risk Contrib`, `Conflict Risk Contrib`,
  `Smoothed Risk Score`.
- Research Mode labels present in the RESEARCH MODE section body:
  `RiskEngineVersion`, `RiskScore`, `RiskState`, `RiskDirection`, `RiskReason`,
  `VolRiskContribution`, `ExtRiskContribution`, `StructRiskContribution`, `ConflictRiskContribution`,
  `VolRiskState`, `ExtRiskState`, `StructRiskState`, `ConflictRiskState`,
  `BarRangeATR`, `LastSwingATR`, `RiskInsufficientData`.
- Alert preservation: exactly the 10 ATE v1.3 alertcondition titles from `pine/releases/ATE_v2.1.pine`. No RiskEngine alertcondition or trade-action alert.
- Boundary discipline: the RiskEngine block does not assign to `confidenceScore`, `marketState`, `trendScore`, `structureScore`, `momentumScore`, `volScore`, `volState`, `volDirection`, `volShockFlag`. It does not introduce `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, or exit-logic logic.
- Reserved-language absence — scoped to:
  - `riskState` literal assignment block;
  - `riskDirection` literal assignment block;
  - `riskReason` literal assignment block;
  - RiskEngine dashboard cells (rows 19..32 of the DASHBOARD section);
  - Research Mode body lines.
  Reserved words checked: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.

### ATE v2.1 VolatilityEngine checks (existing)

- All required Research Mode field labels are present.
- Engine Output Contract fields (`score`, `state`, `direction`, `reason`, `diagnostics`, `version`) are represented in the Pine source.
- `volDirection` is restricted to the approved values (`none`, `expanding`, `contracting`, `stable`, `unstable`) and never `bullish`/`bearish`.
- VolatilityEngine version literal `1.0.0-draft` is present.
- No `Volatility Buy` / `Volatility Sell` / `Volatility Entry` / `Volatility Exit` trade-action alerts are introduced.
- VolatilityEngine variables do not appear inside the `confidenceScore` computation block.
- The ten preserved ATE v1.3 alerts remain present.
- Behavioural checks against the `quiet`, `normal`, `shock` fixtures.

### ATE v2.2 RiskEngine planned checks (spec + Python mirror)

The verifier reads the approved `specifications/ATE/RiskEngine.md` and confirms it defines:

- All six Engine Output Contract fields (`RiskScore`, `RiskState`, `RiskDirection`, `RiskReason`, `RiskEngineVersion`, plus diagnostic component fields).
- Allowed states: `calm`, `normal`, `elevated`, `tense`, `extreme`, `unknown`.
- Allowed directions: `none`, `elevated`, `conflict`, `stable`, `indeterminate`.
- No bullish/bearish in direction or state.
- Reserved-language list absent: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.
- Approved defaults: `volRiskElevatedScore = 25`, `extensionAtrLow = 1.5`, `extensionAtrHigh = 3.0`, `swingRiskAtr = 2.0`, `confidenceRiskHigh = 80`, `confidenceRiskLow = 20`, `riskSmoothingLength = 3`.
- Version literal `1.0.0-draft`.
- Diagnostic-only boundary clause (no ConfidenceEngine, DecisionEngine, entry/exit, position sizing, stop logic, broker/paper-trading, alerts impact).
- Four-component cap table: `volatility 35 / extension 30 / structure 20 / conflict 15`.

Behavioural checks for the planned compute path against fixtures under `tests/fixtures/ATE_v2_2/`:

- `calm_normal` produces `calm` + `normal` states with negligible elevated.
- `elevated` produces ≥ 30% `elevated` + `tense` + `extreme` states combined.
- `extreme_conflict` produces ≥ 30% `tense` + `extreme` states combined.
- Component contribution ranges: `volRiskContribution 0..35`, `extRiskContribution 0..30`, `structRiskContribution 0..20`, `conflictRiskContribution 0..15`.
- `RiskScore` always within `0..100`.
- `RiskEngineVersion` always equals `1.0.0-draft`.
- `RiskDirection` set is contained in the allowed five values.
- `RiskState` set is contained in the allowed six values.
- No bullish/bearish leakage into state or direction.
- Reserved-language absence in dashboard text fields.

## What this verifier does NOT prove

This verifier is intentionally narrow. It is **not**:

- a full unit-test suite green validation,
- a TradingView Pine Script compiler,
- a strategy backtest,
- a performance/risk-improvement measurement,
- a parameter optimisation,
- a multi-asset universe test (covered by RDR-002, RDR-002W, and future RDRs including RDR-003 / RDR-003W),
- proof that VolatilityEngine may feed `RiskEngine` or `ConfidenceEngine`,
- proof that future ATE releases are free of regressions outside the ATE v2.1 VolatilityEngine compute path, the ATE v2.2 RiskEngine planned compute path, and the ATE v2.2 release-file direct checks,
- proof of empirical usefulness of the RiskEngine — RDR-003 / RDR-003W remain required for any future diagnostic-to-downstream change.

The verifier only proves that:

- the ATE v2.1 VolatilityEngine compute path is consistent with the approved Engine Output Contract and VolatilityEngine specification,
- the ATE v2.2 RiskEngine specification defines the approved states, directions, defaults, and diagnostic-only boundary,
- the deterministic Python mirror of the approved RiskEngine is consistent with the spec under the seeded regimes,
- the actual ATE v2.2 release file `pine/releases/ATE_v2.2.pine` defines the contract recorded in the ATE v2.2 Release Manifest, preserves the 10 v1.3 alerts, and contains no RiskEngine alerts or downstream execution.

## How to run it

Prerequisites:

- Python 3.9+ available.
- `numpy` and `pandas` available in the Python environment that runs the verifier.

Recommended setup using a project-local venv (no system pollution):

```bash
python3 -m venv .venv-verify --system-site-packages
.venv-verify/bin/pip install --upgrade pip
.venv-verify/bin/pip install numpy pandas
```

Note: `--system-site-packages` lets the venv pick up the macOS system Python's pre-installed `numpy`/`pandas` to avoid a long install.

Run the verifier:

```bash
python tools/scripts/verify_ate.py
```

Optional: use the venv explicitly:

```bash
.venv-verify/bin/python tools/scripts/verify_ate.py
```

The verifier writes `tools/scripts/verify.log` next to itself with a machine-readable JSON summary.

## How to interpret pass/fail results

Exit codes:

| Exit code | Meaning |
|---|---|
| 0 | pass — no checks failed |
| 1 | fail — one or more contract or behaviour checks failed |
| 2 | environment_error — fixture file missing, Pine release missing, or dependency missing |

A run is considered "green" only if exit code is `0`.

A pass means:

- Every ATE v2.1 VolatilityEngine static contract check is satisfied.
- The three ATE v2.1 seeded fixtures produced the expected regime classification shapes.
- ATE v2.1 VolatilityEngine is still diagnostic-only.
- The preserved v1.3 alert set is intact.
- ATE v2.2 RiskEngine spec defines the approved states, directions, defaults, and diagnostic-only boundary.
- The seeded ATE v2.2 RiskEngine fixtures (calm_normal, elevated, extreme_conflict, unknown) produced the expected regime classification shapes.
- The actual ATE v2.2 release file `pine/releases/ATE_v2.2.pine` satisfies every release-file direct check listed above. The release SHA-256 matches the value recorded in `docs/releases/ATE_v2.2_Release_Manifest.md`; the development mirror is byte-identical; ATE v2.1 SHA-256 is unchanged.

A fail means:

- One of the checks above failed.
- Do NOT interpret the run as a positive signal of performance or trading improvement.
- Read the failure details, then decide whether to amend the spec, amend the Pine release, or amend the verifier.

A `environment_error` means:

- The verifier could not run because some input was missing.
- Fix the environment (install dependencies, restore the Pine release file, restore the fixtures) and re-run.

## Why this is a canonical verification entry point

Before ERP-001 / EDR-001, RDR-002 and RDR-002W each invented their own temporary verifier under `/var/folders/0b/8y8rvw6d53q2y6gt96zb6kz00000gn/T/hermes-verify-<slug>/`. That worked for one research run but is:

- not version-controlled,
- not reproducible by other contributors,
- not stable for CI/CD.

This verifier fixes both problems by living in the repository under a stable path with versioned fixtures and a documented command.

## Adding a new ATE release verifier

When a new ATE release ships:

1. Update `tests/fixtures/ATE_vN_M_1/` with new fixtures or extend the existing set.
2. Update the active release file reference inside `verify_ate.py` if the verifier needs to operate on multiple releases.
3. Add per-release notes to the active EDR file.
4. Run `./.venv-verify/bin/python tools/scripts/verify_ate.py` and capture the `verify.log`.

## ATE v2.2 specific notes

- The expected SHA-256 constant `V22_EXPECTED_SHA` is hard-coded in `verify_ate.py`. If the v2.2 release is rebuilt after a plan-approved Pine change, update both `V22_EXPECTED_SHA` and `docs/releases/ATE_v2.2_Release_Manifest.md` to the new SHA in the same commit.
- The boundary check (no assignment from RiskEngine into `confidenceScore`/`marketState`/etc.) is a top-level block-scoped substring test on the RiskEngine line range, not a full Pine semantic analysis. A future update should consider embedding a small parser if more complex changes land.
- The reserved-language check is scoped to literal displayed text inside RiskEngine fields. Reserved words appearing in Pine comments, MD docs, or CHANGELOG are explicitly ignored by design and will not fail the verifier.

