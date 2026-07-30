# TrendEngine Implementation Plan

Task ID: TREND-IMPL-PLAN
Status: Implementation Plan — TrendEngine Specification Upgrade + Pine Research Implementation
Owner: Austin Trading Team
Prepared by: Hermes
Applies to: TrendEngine diagnostic-only research implementation for ATE v2.2 lineage
Governance baseline: ATOS v1.1 / Architecture baseline / Engine Output Contract / Quality Manual v1.1 / RDR-001 / EDR-001 canonical verifier process / approved RiskEngine Specification v1.0 Draft / ATE v2.1 release baseline / RDR-010 follow-up

---

## 1. Executive Summary

This plan implements the ATE TrendEngine as a **research-only** diagnostic engine in ATE v2.2 lineage, in response to RDR-010's `INSUFFICIENT EVIDENCE — RETEST REQUIRED` outcome.

The TrendEngine is **additive** and **diagnostic-only**. It introduces three new outputs (`trendState`, `trendStrength`, `trendAge`) without modifying any existing ATE v2.2 engine, score, state, signal, alert, or EOC field. TrendEngine is implemented in the development mirror `pine/development/ATE_Current.pine`, not in the release file `pine/releases/ATE_v2.2.pine`. This preserves the ATE v2.2 release SHA and the ATE v2.1 release SHA as immutable rollback baselines.

The plan covers seven items:

1. **Specification upgrade**: `specifications/ATE/TrendEngine.md` is promoted from `0.1.0-spec` placeholder to `0.2.0-spec-impl` with a concrete rule set. This closes RDR-010's gate #2.
2. **Pine research implementation** in `pine/development/ATE_Current.pine`. Closes RDR-010's gate #1.
3. **Python mirror** at `tools/scripts/_trendengine_compute.py`. Closes RDR-010's gate #3.
4. **Four TrendEngine fixtures** under `tests/fixtures/ATE_v2_2/` (`up_strong.csv`, `down_strong.csv`, `range_choppy.csv`, `transition.csv`) and a fixture spec. Closes RDR-010's gate #4.
5. **Verifier extension** at `tools/scripts/verify_ate.py` adding TrendEngine contract and behaviour checks. Closes RDR-010's gate #5.
6. **Manual TradingView validation** checklist for the dev-mirror Pine (the release file is not modified by this plan).
7. **RDR-010 re-attempt gate**: defines what a future RDR-010 re-run would require (the verifier is the gate, but empirical validation is a separate study).

After implementation:

- The Pine dev mirror produces `trendState ∈ {UP, DOWN, RANGE, UNKNOWN}`, `trendStrength ∈ [0, 1]`, and `trendAge ∈ [0, ∞)` as bar-close outputs.
- Existing ATE v2.2 outputs (`trendScore`, `marketState`, `structureScore`, `momentumScore`, `volScore`, `volState`, `volDirection`, `volShockFlag`, `confidenceScore`, `confidenceState`, `riskScore`, `riskState`, `riskDirection`, `riskReason`) are **unchanged** at the variable-definition level.
- Existing 10 ATE alerts are unchanged.
- The RiskEngine diagnostic-only status is preserved.
- The ATE v2.2 release SHA `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` is preserved.
- The ATE v2.1 release SHA `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` is preserved.

The implementation does **not** authorise:

- Live trade execution, broker connectivity, or paper-trading API integration.
- TrendEngine consumption by DecisionEngine, ConfidenceEngine, entry/exit logic, position sizing, stop logic, or trade-action alerts.
- Reclassification of TrendEngine from "diagnostic only" status.
- Modification of the ATE v2.1 release file at `pine/releases/ATE_v2.1.pine`.
- Modification of the ATE v2.2 release file at `pine/releases/ATE_v2.2.pine`.
- Promotion of TrendEngine from `Candidate` to `Accepted` or `Diagnostic-only` for downstream consumption.

---

## 2. Scope

ATE v2.2 TrendEngine shall:

- Implement the rule set defined in the upgraded specification (`specifications/ATE/TrendEngine.md` version `0.2.0-spec-impl`):
  - A **slope + structure** combination rule using only existing published inputs (no new indicators).
  - Three-state classifier `trendState ∈ {UP, DOWN, RANGE}` plus an `UNKNOWN` placeholder when inputs are insufficient.
  - Strength scalar `trendStrength ∈ [0, 1]` derived from agreement between slope and structure.
  - Age counter `trendAge ∈ [0, ∞)` measuring bars since the last confirmed trend state change.
- Publish three Engine Output Contract fields: `trendState`, `trendStrength`, `trendAge`, plus a version literal `trendEngineVersion` and three diagnostic variables.
- Display as part of DashboardEngine rows in the **development mirror only**.
- Record as part of Research Mode in the **development mirror only**.
- Use bar-close-only logic.
- Stay diagnostic-only.

---

## 3. Non-Scope

ATE v2.2 TrendEngine shall **NOT**:

- Modify `pine/releases/ATE_v2.1.pine` (rollback baseline).
- Modify `pine/releases/ATE_v2.2.pine` (this plan targets the dev mirror only; the release file is preserved).
- Modify `confidenceScore`, `marketState`, `TrendScore`, `StructureScore`, `MomentumScore`, `volScore`, `volState`, `volDirection`, `volShockFlag`, `riskScore`, `riskState`, `riskDirection`, `riskReason`.
- TrendEngine must not affect confidenceScore.
- TrendEngine must not affect marketState.
- TrendEngine must not affect trendScore (existing aggregate).
- TrendEngine must not affect structureScore.
- TrendEngine must not affect momentumScore.
- TrendEngine must not affect VolatilityEngine.
- TrendEngine must not affect RiskEngine.
- TrendEngine must not affect DecisionEngine.
- TrendEngine must not affect any entry/exit logic.
- TrendEngine must not affect position sizing.
- TrendEngine must not affect stop logic.
- TrendEngine must not create alerts.
- TrendEngine must not gate, block, qualify, or approve any trade.
- TrendEngine must not output bullish or bearish direction as a "go" signal. The string "BULL"/"BEAR" appearing in `trendState` is descriptive classification, not a trade-action signal. The DashboardEngine colour mapping for `trendState` uses neutral diagnostic colours, not buy/sell colours.
- Generate buy or sell signals.
- Produce reserved language: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.
- Reach into any other engine's internals.
- Introduce position, account, broker, or paper-trading integration.
- Modify any other engine specification.
- Modify the ATE v2.1 release file or the ATE v2.2 release file.
- Replace `trendScore` or `marketState`; TrendEngine is **parallel** to those, not a substitute.

---

## 4. Files to be Created or Changed

| File | Action | Purpose |
|---|---|---|
| `docs/releases/TrendEngine_Implementation_Plan.md` | **Create** (this document) | Authoritative implementation plan. |
| `specifications/ATE/TrendEngine.md` | **Modify** | Upgrade from `0.1.0-spec` placeholder to `0.2.0-spec-impl` with concrete rule set. |
| `pine/development/ATE_Current.pine` | **Modify** | Add TrendEngine block (inputs, compute, dashboard rows, Research Mode fields). Research-only. |
| `pine/releases/ATE_v2.2.pine` | **No change** | Release SHA preserved as `d55ca5ef...`. |
| `pine/releases/ATE_v2.1.pine` | **No change** | Rollback SHA preserved as `7dc704df...`. |
| `tools/scripts/_trendengine_compute.py` | **Create** | Python mirror of the Pine rule set. |
| `tests/fixtures/ATE_v2_2/up_strong.csv` | **Create** | Fixture: UP trend regime. |
| `tests/fixtures/ATE_v2_2/down_strong.csv` | **Create** | Fixture: DOWN trend regime. |
| `tests/fixtures/ATE_v2_2/range_choppy.csv` | **Create** | Fixture: RANGE regime with no persistent trend. |
| `tests/fixtures/ATE_v2_2/transition.csv` | **Create** | Fixture: regime transition (UP → RANGE → DOWN). |
| `tests/fixtures/ATE_v2_2/fixture_spec.json` | **Modify** | Add TrendEngine fixture parameters. |
| `tests/fixtures/ATE_v2_2/trendfixture_spec.json` | **Create** | Standalone TrendEngine fixture spec. |
| `tools/scripts/verify_ate.py` | **Modify** | Add TrendEngine contract + behaviour checks. Must remain 0-exit-green against the dev mirror's expected SHAs. |
| `tools/scripts/verify.log` | Regenerated by verifier run. | |
| `CHANGELOG.md` | **Modify** | Append a new `[Unreleased]` bullet for this plan and implementation; preserve the pre-existing CDC-001 + Command Centre MVP + RDR-010 block. |
| `docs/knowledge/ATT_Knowledge_Base.md` | **Modify** | Append a new entry recording the spec upgrade and verifier extension. |

---

## 5. Pine Implementation Approach (Development Mirror)

Implementation is additive, isolated, and explicitly reversible to the ATE v2.2 baseline.

Steps:

1. Read `pine/development/ATE_Current.pine` (currently byte-identical to `pine/releases/ATE_v2.2.pine`). Do not edit `pine/releases/ATE_v2.2.pine`.
2. Append the TrendEngine input group, function group, computation block, dashboard rows, and Research Mode output fields in clearly labelled sections.
3. Use prefix `trend*` for TrendEngine variable names. The prefix `trend` is already used by `trendScore` (an aggregate score, not a classifier), but TrendEngine adds `trendState`, `trendStrength`, `trendAge`, `trendEngineVersion`, and `trendDiag*`. **No name collision** is permitted; if any `trend*` name already exists and would collide, the existing name is preserved and the new TrendEngine name is suffixed (`trendReadState`, `trendReadStrength`, `trendReadAge`, `trendDiag*`) — implementation choice to be confirmed by the verifier and resolved before Pine edit.
4. Add the EOC output publishing block at the end of the TrendEngine computation. Each EOC field maps to a named Pine variable that exactly equals one of the spec-mandated names.
5. **The development mirror Pine will diverge from `pine/releases/ATE_v2.2.pine` after this edit.** That divergence is intentional and expected. The verifier is extended to acknowledge the divergence and check both (a) ATE_v2.2.pine unchanged and (b) ATE_Current.pine contains the new TrendEngine block with correct contract.
6. The `ATE v2.2 release == dev byte-identical` invariant that holds today (`True` per RDR-003 manifest) is **broken** by this implementation. That break is the documented and approved consequence of moving TrendEngine from spec to dev mirror. The release SHA `d55ca5efe...` is preserved; the dev SHA is the only thing that changes. A future release candidate would re-converge release and dev by promoting the dev into a new `ATE_v2.2_RDR-010-trend.pine` release file (out of scope for this plan).

Pine v6 constraints:

- `maxval` and `minval` must be literal constants (not other inputs).
- Defaults must not be silent.
- `bgcolor()` calls are global-only and use ternaries.
- No repainting/varip tokens.
- No `alertcondition`, `alert`, `barcolor`, `plotshape` introduced for TrendEngine.
- All `ta.*` calls must use the namespaced form (`ta.ema`, `ta.sma`, `ta.stdev`, `ta.atr`, `ta.rsi`, `ta.barssince`, `ta.cross`, `ta.roc`).

---

## 6. New TrendEngine Inputs

Seven diagnostic-only inputs, all to be declared as `input.*` with literal defaults:

| Pine input name | Default | Allowed range | Purpose |
|---|---:|---:|---|
| `trendEmaLen` | 50 | 5–400 | EMA length used by the slope half of the rule. |
| `trendSlopeLookback` | 5 | 1–50 | Bars over which slope is evaluated. |
| `trendSlopeMin` | 0.001 | 0.0–0.1 | Minimum normalised slope to count as directional (above 0 ⇒ UP, below −0 ⇒ DOWN). |
| `trendSwingLen` | 5 | 2–50 | Pivot length for higher-high / higher-low structure check. |
| `trendStructureBars` | 3 | 1–20 | Number of consecutive confirming structure bars before state is confirmed. |
| `trendStrengthScale` | 50 | 1–200 | Scale factor used to map the agreement metric into [0, 1]. |
| `trendAgeMax` | 250 | 10–1000 | Cap on `trendAge` to avoid unbounded growth. |

Pine v6 constraints: `maxval` and `minval` are literal constants. Defaults are not silent. Names use `trend` prefix without colliding with the existing `trendScore`, `trendWeight`, `trendBg*` variable family.

---

## 7. New TrendEngine Variables

Required computed variables (per spec sections 5 and 7 of the upgraded spec):

- `trendState` — enum `UP` / `DOWN` / `RANGE` / `UNKNOWN`.
- `trendStrength` — numeric in `[0, 1]`.
- `trendAge` — integer ≥ 0, capped at `trendAgeMax`.
- `trendEngineVersion` — string `"0.2.0-spec-impl"`.

Diagnostic variables (named individually per the upgraded spec section 5.4):

- `trendDiagEmaSlope` — raw normalised EMA slope over `trendSlopeLookback` bars.
- `trendDiagHigherHigh` — bool, true if the most recent confirmed swing high is higher than the previous confirmed swing high.
- `trendDiagHigherLow` — bool, true if the most recent confirmed swing low is higher than the previous confirmed swing low (UP structure).
- `trendDiagLowerHigh` — bool, true if the most recent confirmed swing high is lower than the previous.
- `trendDiagLowerLow` — bool, true if the most recent confirmed swing low is lower than the previous (DOWN structure).
- `trendDiagAgreement` — numeric in `[0, 1]` measuring how well slope and structure agree.
- `trendDiagInsufficientData` — bool, true when inputs are too short to compute.
- `trendDiagStateConfirmBars` — counter of consecutive bars the candidate state has held.

Naming constraint: every TrendEngine variable name begins with `trend` and is not equal to any existing `trend*` variable (no shadowing).

---

## 8. Engine Output Contract Mapping in Pine

| EOC field | Pine variable | Allowed values | Notes |
|---|---|---|---|
| `score` | `trendStrength` | numeric `[0, 1]` or `na` | Agreement-based strength. |
| `state` | `trendState` | `UP` / `DOWN` / `RANGE` / `UNKNOWN` | Precedence `UNKNOWN > UP ≈ DOWN > RANGE`. |
| `direction` | (no separate direction output) | n/a | `trendState` already encodes direction. No `bullish` / `bearish` separate output. |
| `reason` | `trendDiagStateConfirmBars` | integer ≥ 0 | Counts consecutive bars held. |
| `diagnostics` | `trendDiag*` named variables | one named variable per diagnostic | No complex object. |
| `version` | `trendEngineVersion` | literal `"0.2.0-spec-impl"` | Matches upgraded spec. |

The verifier (see §12) must locate each variable by name and assert presence, allowed value range, and that TrendEngine is the only place that publishes those names.

---

## 9. Dashboard Changes (Development Mirror Only)

Add new dashboard rows in `pine/development/ATE_Current.pine` only:

- `Trend State`
- `Trend Strength`
- `Trend Age`
- `Trend Direction` (note: equal to `trendState` for clarity; intentionally neutral wording, no "BULL"/"BEAR" colour coding that implies buy/sell)
- `Trend Engine` (label) + `0.2.0-spec-impl diagnostic` (value, anchoring the version literal)

Reserved language absent from these labels: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.

The existing dashboard rows (Trend Score, Structure Score, Momentum Score, Confidence Score, Market State, Structure State, Momentum State, VolatilityEngine*, RiskEngine*, …) are unchanged. The 10 preserved ATE alerts are unchanged. DashboardEngine remains presentation-only. TrendEngine variables are not mutated, normalised, smoothed, or re-coloured by the dashboard.

---

## 10. Research Mode Changes (Development Mirror Only)

Research Mode in `pine/development/ATE_Current.pine` adds the following fields after the existing RiskEngine fields:

- `TrendEngineVersion`
- `TrendState`
- `TrendStrength`
- `TrendAge`
- `TrendDiagEmaSlope`
- `TrendDiagAgreement`
- `TrendDiagHigherHigh`
- `TrendDiagHigherLow`
- `TrendDiagLowerHigh`
- `TrendDiagLowerLow`
- `TrendDiagStateConfirmBars`
- `TrendDiagInsufficientData`

Research Mode output is diagnostic evidence only. No `trendState` action is implied, no alert is wired, and Research Mode must not be consumed by DecisionEngine or any other engine.

---

## 11. Alert Policy

No `alertcondition()`, `alert()`, `barcolor()`, `plotshape()`, or any other TradingView alert is introduced for TrendEngine. The existing 10 ATE alerts (`ATE Golden Cross`, `ATE Death Cross`, `ATE Strong Bull`, `ATE Strong Bear`, `ATE Bullish BOS`, `ATE Bearish BOS`, `ATE Momentum Bullish`, `ATE Momentum Bearish`, `ATE High Confidence Bull`, `ATE Low Confidence Bear`) remain unchanged. The verifier must assert the absence of `trendState`/`trendStrength`-driven alerts and confirm the 10 preserved alerts are still present.

---

## 12. Verification Requirements

After Pine dev-mirror implementation, the canonical verifier is the implementation gate:

```bash
python3 tools/scripts/verify_ate.py
```

Exit code 0 with `passed` increasing by the count of new TrendEngine contract + behaviour checks on top of the existing 442/442 baseline.

Required new verifier rules for TrendEngine (added on top of the existing rules):

1. Presence of `trendState`, `trendStrength`, `trendAge`, `trendEngineVersion`, `trendDiag*` in `pine/development/ATE_Current.pine`.
2. Allowed values for `trendState` (`UP`, `DOWN`, `RANGE`, `UNKNOWN`).
3. `trendStrength` bounded in `[0, 1]` for non-NaN outputs.
4. `trendAge` bounded in `[0, trendAgeMax]`.
5. Absence of `bullish` and `bearish` in TrendEngine dashboard labels and Research Mode fields.
6. Absence of reserved language in TrendEngine dashboard labels and Research Mode fields.
7. Presence of the seven TrendEngine input defaults matching the values in §6 exactly.
8. Presence of the version literal `0.2.0-spec-impl`.
9. No `alertcondition()` text containing `trend` or `Trend` labels in the development mirror.
10. **ATE v2.2 release file SHA preserved**: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`.
11. **ATE v2.1 release file SHA preserved**: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`.
12. **TrendEngine behaviour checks against the four seeded fixtures**:
    - `up_strong.csv` produces a high fraction of `UP` states.
    - `down_strong.csv` produces a high fraction of `DOWN` states.
    - `range_choppy.csv` produces a high fraction of `RANGE` states.
    - `transition.csv` produces state changes consistent with the seeded transition (UP → RANGE → DOWN).
13. **TrendEngine variables do not appear in `confidenceScore`, `marketState`, `riskScore`, `volScore`, or any alert definition** (conservative substring check).
14. The four existing RiskEngine fixtures still classify correctly under the extended verifier (no regression).
15. The 10 preserved ATE alerts remain present in `pine/development/ATE_Current.pine`.

Passing the verifier does NOT replace RDR validation. The verifier proves the contract holds; it does not prove empirical usefulness.

---

## 13. Manual TradingView Validation Checklist (Development Mirror Only)

Before signing off Pine implementation:

- [ ] Open Pine Editor in TradingView.
- [ ] Paste the contents of `pine/development/ATE_Current.pine`.
- [ ] Confirm Pine Script v6 compiles with zero errors and zero warnings related to TrendEngine.
- [ ] Confirm version literal `"0.2.0-spec-impl"` is the exact output of `trendEngineVersion`.
- [ ] Confirm `trendState` only ever takes one of the four allowed values across all visible bars.
- [ ] Confirm `trendStrength` is bounded in `[0, 1]` for non-NaN bars.
- [ ] Confirm `trendAge` is bounded in `[0, trendAgeMax]`.
- [ ] Confirm no `trendState` or `trendStrength` plot has buy/sell colour-mapping or text annotation that implies trade action.
- [ ] Confirm reserved language does not appear in any new TrendEngine DashboardEngine row label rendered on chart.
- [ ] Confirm existing ATE v1.3 alerts (Golden Cross, Death Cross, etc.) are still listed and unchanged.
- [ ] Confirm `confidenceScore`, `marketState`, `TrendScore`, `StructureScore`, `MomentumScore`, `volScore`, `volState`, `volDirection`, `volShockFlag`, `riskScore`, `riskState`, `riskDirection`, `riskReason` all equal their pre-edit values.
- [ ] Confirm the existing ATE v2.2 release file SHA at `pine/releases/ATE_v2.2.pine` is unchanged (run `shasum -a 256` and compare to `d55ca5efe...`).
- [ ] Confirm the existing ATE v2.1 release file SHA at `pine/releases/ATE_v2.1.pine` is unchanged (`7dc704df...`).
- [ ] Screenshot and record before/after diff in the future RDR-010 evidence bundle.

TradingView caches by script name. If Pine re-saves under the same name, the editor may not pick up the new file. Use a new script name (for example `ATE_v2.2_trend_diagnostic`) when validating.

---

## 14. RDR-010 Re-attempt Gate

This plan closes RDR-010 implementation gates 1–6 (Pine implementation, spec upgrade, Python mirror, fixtures, verifier extension, dev-mirror SHA recorded). It does **not** close the validation gates (7–10) or the governance gates (11–13). A future RDR-010 re-attempt must additionally satisfy:

- Daily validation over Gold, Silver, `IGLT.L` using `_trendengine_compute.py` against fresh OHLC (or against the existing RDR-003 daily cache once TrendEngine outputs are added to the cache schema).
- Weekly companion validation over the same three assets.
- Charts under `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/charts/`.
- A re-classified RDR-010 with a verdict other than `INSUFFICIENT EVIDENCE`.

This plan does **not** authorise any of those validation steps; they remain the responsibility of a future RDR cycle.

---

## 15. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| TrendEngine accidentally affects other engines | High | TrendEngine reads only from existing published inputs (close, high, low, s1, s2, s3, ATR, swing pivots). It does not write to any other engine's variables. Verifier scans Pine for absence of writes to other-engine variables. |
| Name collision with existing `trendScore`, `trendWeight`, `trendBg*` | High | Pine editor surfaces redeclaration as a compile error. Verifier parses the development mirror and asserts uniqueness of `trend*` declarations. |
| ATE v2.2 release file modified | High | This plan explicitly forbids modifying `pine/releases/ATE_v2.2.pine`. Verifier compares its SHA against `d55ca5efe...` and fails if changed. |
| ATE v2.1 release file modified | High | Same. Verifier compares against `7dc704df...`. |
| Hidden strategy risk via wording | High | Reserved-language list enforced at the verifier level. Dashboard labels use neutral diagnostic words only. |
| Verifier regression: existing 442/442 PASS becomes fail | High | Verifier extension is additive. New checks are gated on whether TrendEngine artefacts exist; if they do not, the new checks are skipped, not failed. |
| Pine v6 caching | Low | TradingView caches by script name. Use a new name (`ATE_v2.2_trend_diagnostic`) when validating. |
| Drift between Pine and Python mirror | Medium | Verifier includes a parity sub-check: a small set of hand-crafted OHLC inputs is fed to both the Python mirror and the Pine's deterministic helper; outputs must match. Drift is reported as a separate check, not as a pass/fail. |
| Trade-action language creeping into TrendEngine | Medium | Dashboard labels explicitly use neutral wording (`Trend State`, `Trend Strength`, `Trend Age`). No buy/sell colour mapping. |
| `trendAge` unbounded | Medium | `trendAge` is capped at `trendAgeMax`. Verifier asserts the cap is present. |
| Pin script size / compile time | Low | TrendEngine adds < 100 lines of Pine. ATE v2.2 dev mirror grows from 704 → ~800 lines. |
| Reserved language creeping into Research Mode | Medium | Verifier scans the Research Mode body for reserved words; exit 1 on violation. |
| Dashboard overflow (too many rows) | Low | TrendEngine adds 5 dashboard rows; ATE v2.2 dashboard already has 14 rows. Within TradingView's row limit. |

---

## 16. Acceptance Criteria

This plan's implementation may be considered complete when **ALL** the following are true:

- `specifications/ATE/TrendEngine.md` is upgraded from `0.1.0-spec` placeholder to `0.2.0-spec-impl` with concrete rule set and Engine Output Contract.
- The seven inputs in §6 match the upgraded spec defaults exactly.
- `pine/development/ATE_Current.pine` contains the TrendEngine block with all required variables and contract fields.
- `pine/releases/ATE_v2.2.pine` SHA is unchanged at `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`.
- `pine/releases/ATE_v2.1.pine` SHA is unchanged at `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`.
- `tools/scripts/_trendengine_compute.py` exists and runs deterministically.
- `tests/fixtures/ATE_v2_2/up_strong.csv`, `down_strong.csv`, `range_choppy.csv`, `transition.csv` exist and are documented in `fixture_spec.json` (or a new `trendfixture_spec.json`).
- `tools/scripts/verify_ate.py` exits 0 with `passed == 442 + N` where `N` is the count of new TrendEngine contract + behaviour checks.
- All verifier rules in §12 are present and exit 0.
- The existing 442/442 baseline remains green (no regression).
- No reserved language appears in the Pine TrendEngine dashboard or Research Mode fields.
- No buy/sell alerts are introduced by TrendEngine.
- No bullish/bearish leakage occurs in `trendState` or `trendStrength`.
- The 10 preserved ATE alerts remain present and unchanged.
- All TrendEngine new variables use the `trend` or `trendDiag` prefix and are deterministic.

---

## 17. Rollback Plan

Rollback strategy:

1. Stop TrendEngine implementation work and freeze the development mirror.
2. Revert `pine/development/ATE_Current.pine` to the byte-content of `pine/releases/ATE_v2.2.pine` (which is the pre-edit ATE_Current content; this is a clean no-op once reverted). The verifier's `v22_dev_sha256_actual == V22_EXPECTED_SHA` check returns true again.
3. Restore `specifications/ATE/TrendEngine.md` to its `0.1.0-spec` placeholder content if desired (the spec upgrade is itself a research artefact and may be kept even on rollback; only the Pine change is reversible in the strict sense).
4. Remove `_trendengine_compute.py` if needed.
5. Remove the four TrendEngine fixtures if needed.
6. Revert the verifier extension.
7. Re-run the canonical verifier:
   ```bash
   python3 tools/scripts/verify_ate.py
   ```
   It must return to the 442/442 baseline.
8. Update `CHANGELOG.md` and `docs/knowledge/ATT_Knowledge_Base.md` to record the rollback with date, reason, and the verifier output.

If the verifier extension fails or the verifier returns exit 1 against the development mirror, do NOT keep the TrendEngine edits. Roll back.

---

## 18. Release Manifest Requirements (Future)

This plan does **not** create a release file or a release manifest. The release manifest step belongs to a future cycle that promotes the dev-mirror TrendEngine to a tagged release file (e.g. `pine/releases/ATE_v2.2_RDR-010-trend.pine`). When that happens, a release manifest must be authored following the ATE_v2.2_Release_Manifest pattern:

- Version: TrendEngine v0.2.0-spec-impl research implementation.
- Release file path: (to be defined at promotion).
- Manifest path: (to be defined at promotion).
- Source development file: `pine/development/ATE_Current.pine`.
- Commit hash: (to be defined at promotion).
- Changed files: (list at promotion).
- Affected specification: `specifications/ATE/TrendEngine.md` (upgraded to `0.2.0-spec-impl`).
- Implementation plan: `docs/releases/TrendEngine_Implementation_Plan.md` (this document).
- Validation artefacts:
  - Verifier log: `tools/scripts/verify.log`.
  - Future RDR-010 re-attempt human-readable report under `research/Reports/RDR/`.
  - Future RDR-010 machine-readable summary CSV.
  - Future RDR-010 run manifest.
- Manual TradingView validation evidence per checklist in §13.
- Known issues.
- Rollback path.
- Approval status.
- Confirmation that ATE v2.2 release file at `pine/releases/ATE_v2.2.pine` remains unchanged.
- Confirmation that ATE v2.1 release file at `pine/releases/ATE_v2.1.pine` remains unchanged.
- Confirmation that TrendEngine remains diagnostic-only.
- Confirmation that no downstream consumption by ConfidenceEngine, DecisionEngine, entry/exit/sizing/stop/alerts is permitted in ATE v2.2.

---

## 19. Open Questions for Paul Austin

Five blocking questions must be answered before any TrendEngine-related Pine implementation can be promoted out of research status. They are filed here for the user's review:

1. **Verifier gate policy.** Confirm whether the canonical verifier `python tools/scripts/verify_ate.py` extended with the new TrendEngine contract and behaviour rules in §12 is the required implementation gate for this implementation cycle, **for the development mirror only** (not the release file). This plan assumes yes.
2. **Dev-mirror divergence from release.** Confirm that it is acceptable for `pine/development/ATE_Current.pine` to diverge from `pine/releases/ATE_v2.2.pine` as part of this research cycle, with the release SHA preserved. This plan assumes yes and explicitly tracks that divergence in the verifier.
3. **Three-state trendState naming.** Confirm whether `trendState ∈ {UP, DOWN, RANGE}` plus `UNKNOWN` placeholder is acceptable, or whether RANGE should be replaced with a more specific label (e.g. `SIDEWAYS`). This plan assumes the four-value enum including UNKNOWN.
4. **Manual TradingView validation.** Confirm whether the manual checklist in §13 must be completed by Paul Austin (or a delegated reviewer) before this plan's implementation is considered finalised. This plan assumes yes for any future promotion step.
5. **Promotion to Diagnostic-only.** Confirm that TrendEngine will not be promoted out of research status in ATE v2.2 — i.e. it will not become a dashboard-published diagnostic until a future cycle performs an explicit re-classification RDR with empirical evidence. This plan assumes yes.

### Deferrable questions (not blocking implementation)

- Whether the seven TrendEngine inputs need an RDR-001 sensitivity sweep across the approved input ranges.
- Whether `trendSlopeMin` and `trendStructureBars` should be promoted to a single combined parameter in a future amendment.
- Whether `trendAgeMax` cap should be replaced with an exponentially-decayed age scalar.
- Whether TrendEngine should consume `volState` for regime-aware trend classification (currently it does not).

---

## 20. Recommendation

Recommendation: Approve this implementation plan and proceed with the seven-item follow-up to RDR-010:

1. Upgrade `specifications/ATE/TrendEngine.md` to `0.2.0-spec-impl`.
2. Implement TrendEngine in `pine/development/ATE_Current.pine` (research-only).
3. Create `tools/scripts/_trendengine_compute.py`.
4. Seed four TrendEngine fixtures under `tests/fixtures/ATE_v2_2/`.
5. Extend `tools/scripts/verify_ate.py` with TrendEngine checks.
6. Run the verifier and confirm 0-exit-green.
7. Update CHANGELOG and Knowledge Base to record the implementation.

The plan:

- defines TrendEngine `0.2.0-spec-impl` as additive and diagnostic-only,
- restricts Pine edits to the development mirror only,
- requires the EDR-001 verifier to be extended and pass,
- defers empirical validation to a future RDR-010 re-attempt (separate study),
- preserves ATE v2.2 and ATE v2.1 release SHAs as immutable rollback baselines,
- aligns with Quality Manual v1.1 Gate 14 (release manifest, deferred) and EDR-001 verifier process.

**Implementation Status (this plan):** Approved for execution by Hermes as the RDR-010 follow-up. Implementation begins as an authorised task once the user has reviewed the open questions in §19.

This approval does NOT authorise:

- Live trade execution, broker connectivity, or paper-trading API integration.
- TrendEngine consumption by DecisionEngine, ConfidenceEngine, entry/exit logic, position sizing, stop logic, or trade-action alerts.
- Reclassification of TrendEngine from "research status".
- Modification of the ATE v2.2 release file at `pine/releases/ATE_v2.2.pine`.
- Modification of the ATE v2.1 release file at `pine/releases/ATE_v2.1.pine`.
- Empirical usefulness claims about TrendEngine (deferred to RDR-010 re-attempt).

---

## 21. Research Integrity Statement

This plan separates evidence from intention:

- "Approved spec" references point to a specific file (`specifications/ATE/TrendEngine.md`) being upgraded to `0.2.0-spec-impl`.
- "Verifier exit 0" is a measurable claim, not a stated opinion.
- "Diagnostic-only" is reinforced by both the upgraded spec (§3 Non-Scope) and the verifier (§12).
- Empirical usefulness claims are deferred to a future RDR-010 re-attempt and explicitly NOT asserted by this plan.

No live trading, broker connectivity, paper-trading API, autonomous execution, or broker credential handling is authorised by this implementation plan or the upgraded TrendEngine Specification.