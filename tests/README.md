# ATE Tests and Verification

This directory houses verification infrastructure for the Austin Trading Engine (ATE) releases.

`tools/scripts/verify_ate.py` is the canonical verification entry point created by ERP-001 / EDR-001.

## What this verifier does

For the active ATE release file (`pine/releases/ATE_v2.1.pine`) it runs two engine compute paths against seeded fixtures:

1. The ATE v2.1 VolatilityEngine compute path against fixtures under `tests/fixtures/ATE_v2_1/`.
2. The ATE v2.2 RiskEngine planned compute path against fixtures under `tests/fixtures/ATE_v2_2/` (using a deterministic Python mirror of the approved RiskEngine v1.0 specification; Pine is not yet implemented).

### ATE v2.1 VolatilityEngine checks (existing)

- All required Research Mode field labels are present.
- Engine Output Contract fields (`score`, `state`, `direction`, `reason`, `diagnostics`, `version`) are represented in the Pine source.
- `volDirection` is restricted to the approved values (`none`, `expanding`, `contracting`, `stable`, `unstable`) and never `bullish`/`bearish`.
- VolatilityEngine version literal `1.0.0-draft` is present.
- No `Volatility Buy` / `Volatility Sell` / `Volatility Entry` / `Volatility Exit` trade-action alerts are introduced.
- VolatilityEngine variables do not appear inside the `confidenceScore` computation block.
- The ten preserved ATE v1.3 alerts remain present.
- Behavioural checks against the `quiet`, `normal`, `shock` fixtures.

### ATE v2.2 RiskEngine planned checks (new)

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
- a TradingView Pine Script compiler for the not-yet-implemented RiskEngine,
- a strategy backtest,
- a performance/risk-improvement measurement,
- a parameter optimisation,
- a multi-asset universe test (covered by RDR-002 and future RDRs),
- proof that VolatilityEngine may feed `RiskEngine` or `ConfidenceEngine`,
- proof that future ATE releases are free of regressions outside the ATE v2.1 VolatilityEngine compute path and the ATE v2.2 RiskEngine planned compute path,
- proof that the RiskEngine Pine implementation matches the deterministic Python mirror used here, until the actual Pine code is written and re-verified.

The verifier only proves that the **current** VolatilityEngine and RiskEngine-planned compute paths are consistent with:

- the approved Engine Output Contract,
- the approved VolatilityEngine and RiskEngine specifications,
- the diagnostic-only boundary,
- the seeded regime behaviour expectations.

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

