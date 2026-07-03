# RiskEngine Specification

Version: 1.0 Draft
Status: Draft for Review
Related ATE Release: ATE v2.2 candidate
Owner: Austin Trading Team
Applies To: Austin Trading Engine
Governance Baseline: ATOS v1.1 / Architecture baseline / Engine Output Contract / Quality Manual v1.1 / RDR-001 / approved VolatilityEngine Specification / RDR-002 lessons learned / EDR-001

---

## 1. Purpose

RiskEngine classifies how risky the current market environment is. It publishes diagnostic evidence only.

It does not:

- generate buy or sell signals,
- approve, reject, or block trades,
- size positions,
- set stop levels,
- influence ConfidenceEngine, DecisionEngine, or any other engine.

RiskEngine answers:

```text
How risky is the current market environment?
```

It must never be confused with ConfidenceEngine, which answers:

```text
How strong is the market evidence?
```

A market can be high-confidence and high-risk at the same time. The two engines measure different things and must remain independent.

---

## 2. Scope and Non-Scope

### 2.1 Scope

ATE v2.2 RiskEngine shall:

- Classify market risk into six diagnostic states.
- Publish a contract-compliant engine output.
- Provide diagnostics for audit, dashboard display, and research validation.
- Use bar-close-only logic.
- Remain deterministic and reproducible from the same inputs and bar.
- Operate in parallel to ConfidenceEngine, DecisionEngine, and VolatilityEngine.

### 2.2 Non-Scope

ATE v2.2 RiskEngine shall not:

- Produce bullish or bearish direction.
- Produce buy or sell signals.
- Generate entry logic, exit logic, or alerts.
- Approve, reject, qualify, or block trades.
- Define position size.
- Define stop distance.
- Define trade probability.
- Mutate upstream engine outputs.
- Define action suitability or unsuitability.
- Use position-account-risk-percentage, broker, or execution integration.
- Be a hidden strategy.

---

## 3. Design Principle

Risk is not confidence. Confidence is strength of market evidence. Risk is suitability of the current environment for any action.

Risk shall not increase or decrease confidence in ATE v2.2.

RiskEngine is diagnostic-only in ATE v2.2. It may consume VolatilityEngine, TrendEngine, StructureEngine, and MomentumEngine inputs for diagnostic classification. It must not publish outputs that any other engine consumes for decision logic.

---

## 4. Allowed Direction Values

Allowed `direction` values:

- none
- elevated
- conflict
- stable
- indeterminate

Direction here describes risk state, not market price. RiskEngine must never emit `bullish` or `bearish` for `direction`. It must not emit `bullish` or `bearish` for `state` either.

---

## 5. Engine Output Contract

RiskEngine must publish the standard Engine Output Contract.

| Field | Required Behaviour |
|---|---|
| `score` | Numeric 0–100 score where higher = more orderly/diagnostic-friendly environment, lower = more disordered/higher diagnostic concern. Score represents diagnostic risk condition, not trade confidence, position size, stop distance, trade approval, or trade probability. |
| `state` | One of: `calm`, `normal`, `elevated`, `tense`, `extreme`, `unknown`. |
| `direction` | One of: `none`, `elevated`, `conflict`, `stable`, `indeterminate`. Must never be `bullish` or `bearish`. |
| `reason` | Short deterministic explanation of the current risk classification. |
| `diagnostics` | Supporting values for audit, dashboard display, and research validation. |
| `version` | Semantic engine version matching this specification and implementation. Initial implementation target: `1.0.0-draft`. |

## 5.1 Score Meaning

Higher score means:

- environment is orderly,
- risk components are aligned,
- diagnostic evidence is sufficient.

Lower score means:

- risk components disagree,
- volatility is contracting into an extreme range,
- structure breaks conflict with momentum,
- diagnostic usefulness is reduced.

Score must not mean:

- trade approval,
- trade rejection,
- position size,
- stop distance,
- trade probability,
- buy/sell indication.

## 5.2 State Model

Allowed `state` values:

| State | Meaning |
|---|---|
| `calm` | All four risk components are low. |
| `normal` | Risk components are within expected range with mild disagreement. |
| `elevated` | At least one risk component is materially elevated. |
| `tense` | Multiple risk components are elevated, or one is extreme. |
| `extreme` | At least one risk component is extreme OR conflict risk is dominant. |
| `unknown` | Insufficient data prevents a reliable classification. |

State precedence:

1. unknown
2. extreme
3. tense
4. elevated
5. normal
6. calm

## 5.3 Required Diagnostics

- `volRiskContribution`
- `extRiskContribution`
- `structRiskContribution`
- `conflictRiskContribution`
- `volRiskComponentState`
- `extRiskComponentState`
- `structRiskComponentState`
- `conflictRiskComponentState`
- `volRiskScoreRaw`
- `extRiskScoreRaw`
- `structRiskScoreRaw`
- `conflictRiskScoreRaw`
- `volVolatilityScore` (the upstream `volScore` consumed)
- `smoothedRiskScore`

## 5.4 Direction Semantics

| Condition | Direction |
|---|---|
| Insufficient data | `none` |
| Conflict component is dominant and volatile | `conflict` |
| Risk trend rising sharply | `elevated` |
| Risk stable across all components | `stable` |
| Multiple components disagree and one is extreme | `indeterminate` |
| Fallback | `stable` |

---

## 6. Inputs with Defaults and Allowed Ranges

| Input | Default | Allowed Range | Purpose |
|---|---:|---:|---|
| `volRiskElevatedScore` | 25 | 0–100 | ATE `volScore` threshold above which volatility counts as risk. |
| `extensionAtrLow` | 1.5 | 0.5–5.0 | Low-end ATR multiple for low-extension risk. |
| `extensionAtrHigh` | 3.0 | 1.0–10.0 | High-end ATR multiple for high-extension risk. |
| `swingRiskAtr` | 2.0 | 0.5–6.0 | ATR multiple where a swing distance becomes risky. |
| `confidenceRiskHigh` | 80 | 50–100 | Confidence threshold above which extreme confidence becomes a risk signal. |
| `confidenceRiskLow` | 20 | 0–50 | Confidence threshold below which both strong bull and strong bear equally become risk signals. |
| `riskSmoothingLength` | 3 | 1–20 | Bars over which the risk score is smoothed. |

Constraints:

- All inputs must be documented Pine `input.*`.
- `maxval` constraints must be literal constants.
- Defaults must not be silent.
- Missing or insufficient-history values must produce explicit `unknown` state and missing-data diagnostics.

---

## 7. Component Scoring

RiskEngine score is the sum of four component contributions, then normalised.

| Component | Max Points | Source |
|---|---:|---|
| Volatility risk | 35 | ATE `volScore` plus `volShockFlag`. |
| Extension risk | 30 | Bar distance versus ATR multiple. |
| Structure risk | 20 | Swing distance versus ATR multiple. |
| Conflict risk | 15 | ConfidenceEngine score extremes AND disagreement across engines. |

The raw component score starts at 0 (low risk) up to its component max.

## 7.1 Volatility Risk Component (max 35)

A high `volScore` indicates an orderly volatility regime. Risk arises when volatility regime is at either end: extreme compression (potential for breakout) or extreme shock.

| Condition | Points |
|---|---:|
| `volScore < 25` (extreme compression) and `volShockFlag` for last N bars | 25 |
| `volScore < 25` and no recent shock | 10 |
| `volScore >= 25` and `<=` 75 | 0 |
| `volScore > 75` and `volScore < 90` | 5 |
| `volScore >= 90` | 15 |
| `volShockFlag` is true on current bar | +20 |

The component state is:

| Points | Component state |
|---|---|
| 0–5 | `volLow` |
| 6–15 | `volElev` |
| 16–25 | `volTense` |
| 26–35 | `volExtreme` |

## 7.2 Extension Risk Component (max 30)

Extension measures how far the current bar extends in ATR units. Excessive range is a diagnostic risk signal.

| Condition | Points |
|---|---:|
| `barRangeAtr <= extensionAtrLow` | 0 |
| `barRangeAtr > extensionAtrLow` and `<= extensionAtrHigh` | linear between 0 and 20 |
| `barRangeAtr > extensionAtrHigh` | 30 |

Where `barRangeAtr = (high - low) / ATR(atrLength)`.

Component state:

| Points | State |
|---|---|
| 0–5 | `extLow` |
| 6–15 | `extNorm` |
| 16–25 | `extStretch` |
| 26–30 | `extExtreme` |

## 7.3 Structure Risk Component (max 20)

Structure risk arises when the last confirmed swing distance is multiple-ATR-sized relative to recent swings.

| Condition | Points |
|---|---:|
| `lastSwingAtr <= 2.0` | 0 |
| `2.0 < lastSwingAtr <= 3.0` | linear 0 to 12 |
| `3.0 < lastSwingAtr <= swingRiskAtr` | linear 12 to 18 |
| `lastSwingAtr > swingRiskAtr` | 20 |

Where `lastSwingAtr = abs(lastSwingPrice - currentPrice) / ATR(atrLength)`.

Component state:

| Points | State |
|---|---|
| 0–4 | `structTight` |
| 5–10 | `structNorm` |
| 11–15 | `structStretch` |
| 16–20 | `structRisk` |

## 7.4 Conflict Risk Component (max 15)

Conflict risk arises when ConfidenceEngine score is extreme or when other engines disagree with each other. Conflict is a diagnostic signal, not a directional signal.

| Condition | Points |
|---|---:|
| `confidenceScore >= confidenceRiskHigh` | 10 |
| `confidenceScore <= confidenceRiskLow` | 10 |
| `trendScore - momentumScore` crosses zero inside last `riskSmoothingLength` bars | +5 |

Component state:

| Points | State |
|---|---|
| 0 | `conflictNone` |
| 1–5 | `conflictMild` |
| 6–10 | `conflictElevated` |
| 11–15 | `conflictHigh` |

## 7.5 Total Score and Smoothing

Raw total is the sum of the four component scores. The published `score` is the raw total smoothed over `riskSmoothingLength` bars with simple moving average.

Score range: 0–100. A higher risk diagnostic score = a more disordered environment. A lower score = an orderly environment.

---

## 8. Boundary Rules

RiskEngine must obey:

- Must not output `bullish` or `bearish` direction.
- Must not produce buy/sell signals.
- Must not produce trade-action alerts.
- Must not approve or reject trades.
- Must not increase or decrease ConfidenceEngine output.
- Must not alter DecisionEngine output.
- Must not feed entry or exit logic.
- Must not feed position size.
- Must not feed stop distance.
- Must not define trade probability.
- Must not mutate upstream or downstream engine outputs.
- Must remain a pure function of documented inputs and bar-close data.

The terms `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`, and `passive` are reserved for DecisionEngine / RiskEngine v3+ risk-authority work. They are forbidden in ATE v2.2 RiskEngine.

---

## 9. Downstream Consumption Rules

ATE v2.2 integration:

| Consumer | Allowed in ATE v2.2? | Notes |
|---|---:|---|
| DashboardEngine | Yes | May display RiskEngine outputs without alteration. |
| Research Mode | Yes | May record and analyse RiskEngine outputs. |
| ConfidenceEngine | No | Must not consume RiskEngine in ATE v2.2. |
| DecisionEngine | No | Must not consume RiskEngine in ATE v2.2. |
| Entry / exit / position / stop | No | Forbidden in ATE v2.2. |
| Alerts | No | Forbidden in ATE v2.2. |
| Strategy layer / broker / paper-trading | No | Forbidden in ATE v2.2. |

Future DecisionEngine consumption requires:

- A separate specification amendment.
- RDR-001 evidence of improvement in at least one of:
  - drawdown control,
  - false-signal filtering,
  - regime classification,
  - confidence reliability,
  - asset qualification quality.
- Updated EDR-001 canonical verifier pass.
- Updated acceptance criteria.
- RiskEngine reclassification under the new evidence.

---

## 10. Dashboard Fields

DashboardEngine may display:

- `score`
- `state`
- `direction`
- `reason`
- `version`
- `volRiskComponentState`
- `extRiskComponentState`
- `structRiskComponentState`
- `conflictRiskComponentState`
- `volRiskContribution`
- `extRiskContribution`
- `structRiskContribution`
- `conflictRiskContribution`
- `smoothedRiskScore`

DashboardEngine must remain presentation-only. It must not reinterpret, normalise, smooth, overwrite, or mutate RiskEngine values.

Display labels must use plain diagnostic words like `Component state: elevated` or `Contribution: 12 / 35`. They must not use words that imply trade permission such as `safe`, `blocked`, `approved`, `recommendation`, or `go`.

---

## 11. Research Mode Fields

Research Mode should record per bar where practical:

- timestamp / bar date
- symbol
- timeframe
- ATE version
- RiskEngine version
- inputs and defaults in use
- `score`
- `state`
- `direction`
- `reason`
- all four component scores
- all four component states
- `volScore` consumed from ATE VolatilityEngine
- `confidenceScore` consumed from ATE ConfidenceEngine
- `barRangeAtr`
- `lastSwingAtr`
- missing/invalid data flags

Research Mode output is diagnostic evidence only. It must not trigger entries, exits, sizing, stops, or alerts.

---

## 12. RDR-001 Validation Plan

### 12.1 Research Question

Does RiskEngine classify market risk into the six diagnostic states (`calm`, `normal`, `elevated`, `tense`, `extreme`, `unknown`) reproducibly, sensibly, and additively across a balanced multi-asset daily/weekly universe without introducing hidden directional bias, accidental duplication of VolatilityEngine, or unstable scoring?

### 12.2 Hypothesis

Combining volatility regime, bar-extension, swing-extension, and engine-conflict signals into a four-component risk score reproduces the established risk regimes observable on daily/weekly data and produces diagnostic information not already captured by VolatilityEngine alone.

### 12.3 Validation Universe

- Gold, Silver, Copper
- Nasdaq futures, S&P 500 ETF, large-cap equities
- Treasury / gilt proxy
- Major FX pairs
- WTI crude oil futures

### 12.4 Daily-First Approach

- Daily first.
- Weekly after daily diagnostic behaviour is reviewed.

### 12.5 Required Controls

- No lookahead bias.
- No repainting.
- Bar-close-only behaviour.
- No bullish/bearish direction leakage.
- No ConfidenceEngine, DecisionEngine, entry, exit, sizing, stop, or alert impact.
- Determinism across reruns.
- Sensitivity across allowed input ranges.
- Stability across asset classes.
- Cross-correlation with VolatilityEngine `volScore`.
- Cross-correlation with MomentumEngine `momentumScore`.
- Overlap diagnostics.
- Hidden directional bias review.

### 12.6 Required Artefacts

- Human-readable report under `research/Reports/RDR/`.
- Machine-readable summary CSV using approved schema.
- Run manifest recording schema version, data source, download date, symbols, timeframe, date range, adjustments, transformations, storage location, checksum, and limitations.
- Research Mode output files.
- Negative-result preservation.

### 12.7 Required Analyses

- State frequency by asset and asset class.
- State duration (average, median, longest, shortest).
- State transitions.
- Component contribution breakdown by state.
- Cross-asset behaviour comparison.
- Overlap with VolatilityEngine (target: low to medium).
- Overlap with MomentumEngine (target: low).
- Hidden directional bias by state.
- Relationship between RiskScore and short-horizon adverse movement (informationally, not as a trading claim).
- Diagnostics-to-state explanation quality.
- Negative findings preservation.

### 12.8 Result Classification

RDR result classifies RiskEngine evidence as one of:

- supported
- weakly supported
- inconclusive
- falsified
- operationally rejected

### 12.9 What It Must NOT Claim

- Drawdown improvement without RDR evidence.
- False-signal reduction without RDR evidence.
- Risk reduction without RDR evidence.
- Trading-edge implication.
- DecisionEngine authorisation.
- RiskEngine authority over trade permission.

---

## 13. Acceptance Criteria

RiskEngine v1.0 Draft may proceed to ATE v2.2 diagnostic-only implementation planning only if:

- The specification is approved by Paul Austin as Product Owner.
- Chief Systems Architect has no architecture-impact objections.
- EDR-001 canonical verifier has been extended to cover the ATE v2.2 RiskEngine compute path.
- Engine Output Contract is published.

The implemented RiskEngine may be accepted for ATE v2.2 diagnostic use only if:

- It compiles under Pine Script v6.
- It publishes all Engine Output Contract fields.
- It uses bar-close-only logic.
- It introduces no lookahead or repainting behaviour.
- It uses only the inputs and ranges in this specification.
- It uses asset-normalised or boundary-safe thresholds.
- It never outputs bullish/bearish direction.
- It does not affect ConfidenceEngine, DecisionEngine, entry/exit logic, position sizing, stop placement, or trade-action alerts.
- It produces diagnostics that explain state and score.
- EDR-001 verifier covers the RiskEngine compute path and passes.
- Its RDR-001 validation plan is executed and produces a non-falsified result classification.

---

## 14. Rejection Criteria

RiskEngine v1.0 Draft or implementation should be rejected or revised if it:

- Violates the Engine Output Contract.
- Produces bullish or bearish direction or state.
- Generates buy/sell signals.
- Authorises or refuses trades.
- Influences ConfidenceEngine, DecisionEngine, entry/exit logic, position sizing, stop placement, or alerts in ATE v2.2.
- Introduces reserved language (`safe`, `unsafe`, `approved`, `blocked`, `tradeable`, `untradeable`, `suitable`, `unsuitable`) in dashboard or Research Mode.
- Uses undocumented defaults.
- Cannot explain state and score from diagnostics.
- Duplicates TrendEngine by measuring direction/persistence.
- Duplicates VolatilityEngine without adding unique risk information.
- Duplicates MomentumEngine by measuring directional rate-of-change.
- Adds parameter clutter without evidence.
- Creates unstable scoring.
- Introduces lookahead or repainting risk.
- Claims performance, drawdown, or risk reduction without RDR-001 evidence.
- Reduces explainability.

---

## 15. Versioning and Migration Impact

Initial implementation target: `1.0.0-draft`.

This specification introduces a new diagnostic engine contract for ATE v2.2. It does not change existing TrendEngine, StructureEngine, MomentumEngine, ConfidenceEngine, DecisionEngine, DashboardEngine, or VolatilityEngine contracts.

Any future change that allows RiskEngine to be consumed by DecisionEngine, ConfidenceEngine, entry logic, exit logic, position sizing, stop placement, or alerts requires:

- Specification amendment.
- Architecture impact review.
- RDR-001 evidence where research claims are made.
- EDR where interface or engine-flow changes are material.
- Regression evidence.
- Product Owner review where scope or risk is affected.
- EDR-001 verifier extension.

---

## 16. Changelog Note

RiskEngine v1.0 Draft drafted for ATE v2.2 review, applying RDR-002 lessons learned and EDR-001 verifier process:

- Stated diagnostic-only boundary explicitly.
- Excluded bullish/bearish direction and reserved action-suitability language.
- Defined six-state diagnostic risk model with state precedence.
- Defined four-component scoring (volatility 35, extension 30, structure 20, conflict 15) with deterministic, explainable rules.
- Defined diagnostics sufficient for audit and Research Mode.
- Defined RDR-001 validation plan with required artefacts, controls, and result classification.
- Defined acceptance and rejection criteria enforceable by the EDR-001 canonical verifier.
- Defined future evidence thresholds before any DecisionEngine consumption.

---

## 17. Approval Status

This specification is a Draft for Review. It is not yet approved for ATE v2.2 implementation planning.

Approval requires:

- Paul Austin / Product Owner review and approval of diagnostic-only status.
- Chief Systems Architect review of engine-separation boundaries.
- Completion of any blocking questions.

Recommendation: Approve with amendments as listed in the Specification Review Report. When amendments are applied, the revised specification may proceed to ATE v2.2 diagnostic-only implementation planning.
