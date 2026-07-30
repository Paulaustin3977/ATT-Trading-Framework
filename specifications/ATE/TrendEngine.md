# TrendEngine

> **Status:** **Approved for Research Implementation Planning** (RDR-010 follow-up, 2026-07-07).
> **Version:** `0.2.0-spec-impl` (upgraded from `0.1.0-spec` placeholder).
> **Previous version:** `0.1.0-spec` (placeholder; preserved for history in git).
> **Owner:** Austin Trading Team.
> **Applies to:** ATE v2.2 lineage; dev-mirror implementation only. Not promoted to release file by this version.
> **Governance baseline:** ATOS v1.1 / Architecture baseline / Engine Output Contract / Quality Manual v1.1 / RDR-001 / EDR-001 canonical verifier process / approved RiskEngine Specification v1.0 Draft / ATE v2.1 release baseline / RDR-010 follow-up.

---

## 1. Purpose

TrendEngine classifies the prevailing market trend on the basis of two orthogonal signals:

1. **Slope** of a single moving average over a configurable lookback.
2. **Structure** of recent swing pivots: higher-high + higher-low (UP), lower-high + lower-low (DOWN), or neither (RANGE).

The two signals must agree to count as a confirmed trend. Disagreement or insufficient data defaults to `RANGE` (or `UNKNOWN` when inputs are too short to compute).

TrendEngine answers:

```text
Is the market in a confirmed UP, DOWN, or RANGE trend right now, and how strong is that trend?
```

It must never be confused with ConfidenceEngine (which answers "how strong is the evidence?") or RiskEngine (which answers "how risky is the environment?"). A market can be high-confidence and high-risk and in a RANGE state at the same time. The three engines measure different things and must remain independent.

---

## 2. Scope

ATE v2.2 TrendEngine shall:

- Classify market trend into four diagnostic states: `UP`, `DOWN`, `RANGE`, `UNKNOWN`.
- Publish the Engine Output Contract fields: `trendState`, `trendStrength`, `trendAge`, `trendEngineVersion`, plus named diagnostic variables.
- Provide diagnostics for dashboard display (dev-mirror only) and research validation.
- Use bar-close-only logic.
- Remain deterministic and reproducible from the same inputs and bar index.
- Operate in parallel to ConfidenceEngine, DecisionEngine, RiskEngine, and VolatilityEngine.

---

## 3. Non-Scope

ATE v2.2 TrendEngine shall **NOT**:

- Produce buy or sell signals.
- Approve, reject, qualify, or block trades.
- Size positions.
- Set stop levels.
- Influence ConfidenceEngine, DecisionEngine, RiskEngine, or any other engine.
- Replace the existing `trendScore` aggregate or the existing `marketState`. TrendEngine is **parallel** to those, not a substitute.
- Use reserved language: `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.
- Create alerts.
- Output bullish or bearish direction as a "go" signal. The strings "UP" and "DOWN" in `trendState` are descriptive classification, not a trade-action signal.
- Repaint, lookahead, or use `varip` tokens.

---

## 4. Inputs

TrendEngine consumes only inputs that already exist in ATE v2.2. It does not add new external data feeds. The seven diagnostic-only **operator inputs** are:

| Pine input name | Default | Allowed range | Purpose |
|---|---:|---:|---|
| `trendEmaLen` | 50 | 5–400 | EMA length used by the slope half of the rule. |
| `trendSlopeLookback` | 5 | 1–50 | Bars over which the EMA slope is evaluated. |
| `trendSlopeMin` | 0.001 | 0.0–0.1 | Minimum normalised absolute slope to count as directional. |
| `trendSwingLen` | 5 | 2–50 | Pivot length for higher-high / higher-low structure check. |
| `trendStructureBars` | 3 | 1–20 | Number of consecutive confirming structure bars before a state change is confirmed. |
| `trendStrengthScale` | 50 | 1–200 | Scale factor used to map the agreement metric into `[0, 1]`. |
| `trendAgeMax` | 250 | 10–1000 | Cap on `trendAge` to avoid unbounded growth. |

Pine v6 constraints: `maxval` and `minval` are literal constants (not other inputs). Defaults are not silent.

### 4.1 Internal inputs (existing ATE v2.2 outputs TrendEngine reads)

TrendEngine reads the following existing published variables. It does not write to any of them.

- `close`
- `high`
- `low`
- TrendEngine-owned confirmed swing-high and swing-low history, computed from `high` and `low` with `trendSwingLen`. It does not inherit StructureEngine's independently configurable `pivotLen` or mutate StructureEngine state.

---

## 5. Outputs

### 5.1 EOC fields (Engine Output Contract)

| EOC field | Pine variable | Allowed values |
|---|---|---|
| `score` | `trendStrength` | numeric in `[0, 1]`, or `na` when `UNKNOWN` |
| `state` | `trendState` | `UP` / `DOWN` / `RANGE` / `UNKNOWN` |
| `direction` | (no separate direction output) | n/a — `trendState` already encodes direction |
| `reason` | `trendDiagStateConfirmBars` | integer ≥ 0 — directional-candidate confirmation streak; `0` for a `RANGE` candidate |
| `diagnostics` | `trendDiag*` named variables | one named variable per diagnostic |
| `version` | `trendEngineVersion` | literal `"0.2.0-spec-impl"` |

State precedence: `UNKNOWN` beats everything. Among the three non-UNKNOWN states, `UP` and `DOWN` are mutually exclusive; `RANGE` is the fallback when slope and structure disagree or when neither signal fires.

### 5.2 Required computed variables

- `trendState` — enum `UP` / `DOWN` / `RANGE` / `UNKNOWN`.
- `trendStrength` — numeric in `[0, 1]`.
- `trendAge` — integer ≥ 0, capped at `trendAgeMax`.
- `trendEngineVersion` — string `"0.2.0-spec-impl"`.

### 5.3 Diagnostic variables

- `trendDiagEmaSlope` — raw normalised EMA slope over `trendSlopeLookback` bars.
- `trendDiagHigherHigh` — bool, true if the most recent confirmed swing high is higher than the previous confirmed swing high.
- `trendDiagHigherLow` — bool, true if the most recent confirmed swing low is higher than the previous confirmed swing low.
- `trendDiagLowerHigh` — bool, true if the most recent confirmed swing high is lower than the previous confirmed swing high.
- `trendDiagLowerLow` — bool, true if the most recent confirmed swing low is lower than the previous confirmed swing low.
- `trendDiagAgreement` — numeric in `[0, 1]` measuring how well slope and structure agree.
- `trendDiagInsufficientData` — bool, true when inputs are too short to compute.
- `trendDiagStateConfirmBars` — counter of consecutive bars the candidate state has held.

### 5.4 Naming constraint

Every TrendEngine variable name begins with `trend`. The implementation **must not** collide with existing ATE v2.2 names:

- `trendScore` — existing aggregate (0–100), NOT replaced.
- `trendWeight` — existing ConfidenceEngine input.
- `trendBg*` — existing visual group references.

If any new `trend*` name would collide, the implementation must use the suffix `Read` (`trendReadState`, `trendReadStrength`, `trendReadAge`) or move to `trendDiag*` for diagnostics.

---

## 6. Method

### 6.1 Step 1 — Insufficient data check

If `close` history is shorter than `trendEmaLen + trendSlopeLookback + 1` bars, TrendEngine returns:

- `trendState = "UNKNOWN"`
- `trendStrength = na`
- `trendAge = na`
- `trendDiagInsufficientData = true`

All `trendDiag*` values are `na` or `false`.

### 6.2 Step 2 — Compute EMA slope

```
trendEma        = ta.ema(close, trendEmaLen)
trendDiagEmaSlope = (trendEma - trendEma[trendSlopeLookback]) / trendEma[trendSlopeLookback]
```

`trendDiagEmaSlope` is normalised by the prior EMA value. Sign and magnitude are both meaningful.

### 6.3 Step 3 — Slope classification

```
slopeIsUp    = trendDiagEmaSlope >  trendSlopeMin
slopeIsDown  = trendDiagEmaSlope < -trendSlopeMin
slopeIsFlat  = not slopeIsUp and not slopeIsDown
```

`trendSlopeMin` is the dead-zone. A slope inside `[-trendSlopeMin, +trendSlopeMin]` counts as flat.

### 6.4 Step 4 — Structure classification

The structure half computes its own confirmed swing pivots with `trendSwingLen`. The implementation finds the most recent confirmed swing high and the previous confirmed swing high, and similarly for swing lows. It then evaluates:

```
trendDiagHigherHigh = lastHigh > prevHigh
trendDiagHigherLow  = lastLow  > prevLow
trendDiagLowerHigh  = lastHigh < prevHigh
trendDiagLowerLow   = lastLow  < prevLow

structIsUp   = trendDiagHigherHigh and trendDiagHigherLow
structIsDown = trendDiagLowerHigh  and trendDiagLowerLow
structIsFlat = not structIsUp and not structIsDown
```

If there are fewer than 2 confirmed pivots on either side, the corresponding `*Diag*` bool is `false` and `structIsFlat = true`.

### 6.5 Step 5 — Agreement metric

`trendDiagAgreement` is a numeric in `[0, 1]` measuring how well slope and structure agree:

| Slope | Structure | `trendDiagAgreement` |
|---|---|---|
| UP | UP | 1.0 |
| DOWN | DOWN | 1.0 |
| FLAT | FLAT | 0.5 (or close to it; below threshold) |
| UP | FLAT | 0.6 |
| FLAT | UP | 0.6 |
| DOWN | FLAT | 0.6 |
| FLAT | DOWN | 0.6 |
| UP | DOWN | 0.0 |
| DOWN | UP | 0.0 |
| UNKNOWN | any | 0.0 |

### 6.6 Step 6 — Candidate state

```
candidateUp   = (slopeIsUp   and structIsUp)
candidateDown = (slopeIsDown and structIsDown)
```

If `candidateUp`, the candidate state is `UP`. If `candidateDown`, the candidate state is `DOWN`. Otherwise the candidate state is `RANGE`.

### 6.7 Step 7 — State confirmation

A candidate state must hold for `trendStructureBars` consecutive bars before `trendState` adopts it. Until then, `trendState` retains its previous value. This prevents single-bar whipsaw from changing `trendState`.

If the previous `trendState` is `UNKNOWN` (e.g. on warm-up), the first non-UNKNOWN candidate is adopted immediately — no confirmation wait — because there is no prior state to lose.

`trendDiagStateConfirmBars` increments by 1 each bar the same `UP` or `DOWN` candidate holds, resets to 1 when the directional candidate changes, and reports 0 while the candidate is `RANGE`. It is reported regardless of whether the candidate has been adopted as `trendState`.

### 6.8 Step 8 — Strength calculation

```
strengthRaw = candidateUp or candidateDown ? trendDiagAgreement * trendStrengthScale : 0.0
trendStrength = strengthRaw > 0 ? math.min(1.0, strengthRaw) : 0.0
```

When the candidate is `RANGE` (no slope-structure agreement), `trendStrength = 0.0`. When the candidate is `UP` or `DOWN`, `trendStrength` is the agreement scaled into `[0, 1]`.

### 6.9 Step 9 — Age tracking

`trendAge` counts consecutive bars during which `trendState` has held its current value. It resets to 0 when `trendState` changes and is capped at `trendAgeMax`.

```
trendAge = trendState == trendState[1] ? math.min(trendAgeMax, trendAge[1] + 1) : 0
```

Special case: if `trendState[1]` is `UNKNOWN`, `trendAge = 0` (the state has just been adopted; we cannot count from a known starting bar).

### 6.10 Step 10 — Version literal

`trendEngineVersion = "0.2.0-spec-impl"` is set unconditionally and never changes within this version of the engine.

---

## 7. Constraints

- **Bar-close only.** No `close[1]` reads on the same bar as a `close` update. TrendEngine is purely a function of bar-close prices and the bar index.
- **No repainting.** All computations must be stable under replay from the same OHLC series.
- **Deterministic.** Given the same OHLC series and the same inputs, TrendEngine must produce the same output for every bar.
- **No reserved language.** Dashboard labels and Research Mode fields must avoid `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.
- **No buy/sell mapping.** Dashboard colour mapping for `trendState` must use neutral diagnostic colours, not buy/sell colours.
- **No alerts.** No `alertcondition`, `alert`, `barcolor`, `plotshape` introduced for TrendEngine.
- **No coupling.** TrendEngine variables must not be referenced by `confidenceScore`, `marketState`, `structureScore`, `momentumScore`, `volScore`, `riskScore`, `riskState`, `riskDirection`, `riskReason`, or any `alertcondition` body.

---

## 8. Engine Output Contract Mapping

| EOC field | Pine variable | Allowed values | Notes |
|---|---|---|---|
| `score` | `trendStrength` | numeric `[0, 1]` or `na` | Scaled agreement. |
| `state` | `trendState` | `UP` / `DOWN` / `RANGE` / `UNKNOWN` | Precedence `UNKNOWN > UP ≈ DOWN > RANGE`. |
| `direction` | (no separate direction output) | n/a | `trendState` already encodes direction. |
| `reason` | `trendDiagStateConfirmBars` | integer ≥ 0 | Directional-candidate confirmation streak; `0` for `RANGE`. |
| `diagnostics` | `trendDiag*` named variables | one named variable per diagnostic | No complex object. |
| `version` | `trendEngineVersion` | literal `"0.2.0-spec-impl"` | Matches this spec. |

---

## 9. Dashboard Rules (Development Mirror Only)

TrendEngine rows in `pine/development/ATE_Current.pine` dashboard:

- `Trend State`
- `Trend Strength`
- `Trend Age`
- `Trend Engine` (label) + `0.2.0-spec-impl diagnostic` (value, anchoring the version literal)

Reserved language absent from these labels. Existing dashboard rows are unchanged. DashboardEngine remains presentation-only. TrendEngine variables are not mutated by the dashboard.

---

## 10. Research Mode Rules (Development Mirror Only)

TrendEngine fields appended to Research Mode in `pine/development/ATE_Current.pine`:

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

No `alertcondition()`, `alert()`, `barcolor()`, `plotshape()`, or any other TradingView alert is introduced for TrendEngine. Existing 10 ATE alerts are preserved unchanged.

---

## 12. Verification Requirements

After Pine dev-mirror implementation:

1. Run `python3 tools/scripts/verify_ate.py`. Exit code 0 with `passed` increasing by the count of new TrendEngine contract + behaviour checks on top of the existing 442/442 baseline.
2. Required new verifier rules for TrendEngine:
   - presence of `trendState`, `trendStrength`, `trendAge`, `trendEngineVersion`, `trendDiag*` in the dev mirror;
   - allowed values for `trendState` (`UP`, `DOWN`, `RANGE`, `UNKNOWN`);
   - `trendStrength` bounded in `[0, 1]` for non-NaN outputs;
   - `trendAge` bounded in `[0, trendAgeMax]`;
   - absence of `bullish` and `bearish` in TrendEngine dashboard labels and Research Mode fields;
   - absence of reserved language in TrendEngine dashboard labels and Research Mode fields;
   - presence of the seven TrendEngine input defaults matching §4 exactly;
   - presence of the version literal `"0.2.0-spec-impl"`;
   - no `alertcondition()` text containing `trend` or `Trend` labels;
   - ATE v2.2 release file SHA preserved at `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`;
   - ATE v2.1 release file SHA preserved at `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`;
   - TrendEngine behaviour checks against the four seeded fixtures (UP-heavy, DOWN-heavy, RANGE-heavy, transition).
3. The verifier must fail (exit 1) on any violation.

Passing the verifier does NOT replace RDR validation. The verifier only proves the contract holds; empirical usefulness is a separate study.

---

## 13. Versioning

This spec is at `0.2.0-spec-impl`. The version literal published in Pine is the same string. Promotion to `0.3.0-spec-prod` requires:

- Empirical validation by an RDR cycle (e.g. RDR-010 re-attempt).
- Approval by Paul Austin as Chief Systems Architect.
- A release manifest under `docs/releases/`.

Until then, `0.2.0-spec-impl` remains "Approved for Research Implementation Planning" status.

---

## 14. Version History

| Version | Date | Status | Notes |
|---|---|---|---|
| `0.1.0-spec` | (pre-RDR-010) | Specification draft, implementation pending. | Placeholder; left the rule set as "defined during implementation". 34 lines. Closed by RDR-010 as INSUFFICIENT EVIDENCE. |
| `0.2.0-spec-impl` | 2026-07-07 | Approved for Research Implementation Planning. | RDR-010 follow-up. Concrete rule set: slope + structure with `trendStructureBars`-bar confirmation. Inputs and outputs fully specified. Implements RDR-010 gates 1–6. |

---

## 15. Related Documents

- `docs/releases/TrendEngine_Implementation_Plan.md` — implementation plan for this spec.
- `research/Reports/RDR/RDR-010-trendengine-validation.md` — RDR that concluded TrendEngine was `INSUFFICIENT EVIDENCE` and defined the gates this spec closes.
- `specifications/ATE/RiskEngine.md` — RiskEngine v1.0 Draft, the closest sibling spec. RiskEngine diagnostic-only status is preserved by this version.
- `tools/scripts/_trendengine_compute.py` — Python mirror of this spec.
- `tests/fixtures/ATE_v2_2/` — TrendEngine fixtures.
- `tools/scripts/verify_ate.py` — extended verifier covering this spec.