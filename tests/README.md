# ATE Tests and Verification

This directory houses verification infrastructure for the Austin Trading Engine (ATE) releases.

`tools/scripts/verify_ate.py` is the canonical verification entry point created by ERP-001 / EDR-001.

## What this verifier does

For the active ATE release file (`pine/releases/ATE_vX.Y.pine`) it runs the ATE VolatilityEngine compute path against the seeded fixtures under `tests/fixtures/ATE_v2_1/`:

1. **Static contract checks** on the Pine release file:
   - All required Research Mode field labels are present.
   - Engine Output Contract fields (`score`, `state`, `direction`, `reason`, `diagnostics`, `version`) are represented in the Pine source.
   - `volDirection` is restricted to the approved values (`none`, `expanding`, `contracting`, `stable`, `unstable`) and never `bullish`/`bearish`.
   - VolatilityEngine version literal `1.0.0-draft` is present.
   - No `Volatility Buy` / `Volatility Sell` / `Volatility Entry` / `Volatility Exit` trade-action alerts are introduced.
   - VolatilityEngine variables (`volScore`, `volState`, `volDirection`) do not appear inside the `confidenceScore` computation block.
   - The ten preserved ATE v1.3 alerts remain present.

2. **Behavioural checks** on three deterministic fixtures:
   - `quiet`: small drift fixture; must not produce `shock` or `unstable`; must contain `normal` or warm-up `unknown`.
   - `normal`: moderate-drift fixture; must contain `normal` and may contain a small fraction of `expanding`.
   - `shock`: large-range periodic spikes; must flag at least one `shock` event.
   - The set of `VolatilityState` values is contained in the allowed set.
   - The set of `VolatilityDirection` values is contained in the allowed set.
   - No `bullish` / `bearish` direction appears.
   - `VolatilityScore` is in the range `0..100` or `NaN`.

3. **Determinism check** on the `normal` fixture (re-run and compare).

## What this verifier does NOT prove

This verifier is intentionally narrow. It is **not**:

- a full unit-test suite green validation,
- a TradingView Pine Script compiler,
- a strategy backtest,
- a performance/risk-improvement measurement,
- a parameter optimisation,
- a multi-asset universe test (RDR-002 covered that separately),
- proof that VolatilityEngine may feed `RiskEngine` or `ConfidenceEngine`,
- proof that future ATE releases are free of regressions outside the scope of the ATE v2.1 VolatilityEngine compute path.

The verifier only proves the **current** VolatilityEngine compute path is consistent with:

- the approved Engine Output Contract,
- the approved VolatilityEngine specification,
- the diagnostic-only boundary,
- the seeded regime behaviour expectations.

## How to run it

Prerequisites:

- Python 3.9+ available.
- `numpy` and `pandas` available in the Python environment that runs the verifier.

Recommended setup using a project-local venv (no system pollution):

```bash
python3 -m venv .venv-erp001 --system-site-packages
.venv-erp001/bin/pip install --upgrade pip
.venv-erp001/bin/pip install numpy pandas
```

Note: `--system-site-packages` lets the venv pick up the macOS system Python's pre-installed `numpy`/`pandas` to avoid a long install.

Run the verifier:

```bash
python tools/scripts/verify_ate.py
```

Optional: use the venv explicitly:

```bash
.venv-erp001/bin/python tools/scripts/verify_ate.py
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

- Every static contract check is satisfied for the active Pine release file.
- The three seeded fixtures produced the expected regime classification shapes.
- VolatilityEngine is still diagnostic-only.
- The preserved v1.3 alert set is intact.

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
4. Run `./.venv-erp001/bin/python tools/scripts/verify_ate.py` and capture the `verify.log`.
