# VolatilityEngine Specification

Version: 1.0 Draft
Status: Approved for Diagnostic-Only Implementation Planning
Related ATE Release: ATE v2.1
Owner: Austin Trading Team
Applies To: Austin Trading Engine
Governance Baseline: ATOS v1.1 / Architecture baseline / Engine Output Contract / Quality Manual v1.1 / RDR-001

---

# 1. Purpose

The VolatilityEngine classifies the current volatility regime of a market.

Its purpose is to answer:

```text
What volatility regime is the market currently in?
```

The VolatilityEngine is diagnostic-only in ATE v2.1. It publishes volatility condition evidence for DashboardEngine display and Research Mode analysis. It must not generate buy signals, sell signals, risk approval, confidence boosts, position sizing, stop levels, or final action decisions.

VolatilityEngine output may help humans and Hermes understand whether market movement is compressed, normal, expanding, elevated, unstable, or shock-like. Any decision about whether that condition is safe, favourable, dangerous, or actionable belongs to RiskEngine, ConfidenceEngine, DecisionEngine, or later validated governance amendments — not to VolatilityEngine v2.1.

---

# 2. Scope and Non-Scope

## 2.1 Scope

ATE v2.1 VolatilityEngine shall:

- Classify volatility regime using approved volatility measures.
- Publish a contract-compliant engine output.
- Provide diagnostics for audit, dashboard display, and research validation.
- Use asset-normalised volatility baselines where possible.
- Operate on bar-close data only.
- Remain deterministic and reproducible from the same inputs and bar.
- Support Research Mode validation under RDR-001.

## 2.2 Non-Scope

ATE v2.1 VolatilityEngine shall not:

- Produce bullish or bearish direction.
- Produce buy or sell signals.
- Change ConfidenceEngine output.
- Change RiskEngine output.
- Change DecisionEngine output.
- Affect entry logic.
- Affect exit logic.
- Approve or reject trades.
- Define position size.
- Define stop distance.
- Create or modify alerts that imply trade action.
- Define trade probability.
- Act as a hidden confidence booster.
- Use Keltner Channels.
- Use complex realised-volatility models.
- Use asset-specific fixed threshold tables.
- Use fixed absolute volatility thresholds as the primary classification method.

---

# 3. Design Principle

Volatility shall not automatically increase confidence.

The VolatilityEngine measures volatility condition.

The ConfidenceEngine measures strength and agreement of market evidence.

The RiskEngine interprets whether a potential action is safe, suitable, or requires adjustment.

The DecisionEngine determines final action or no-action.

Therefore, in ATE v2.1, VolatilityEngine is diagnostic-only. Its outputs may be displayed and researched, but must not be consumed by ConfidenceEngine, RiskEngine, or DecisionEngine.

---

# 4. Approved Measures for ATE v2.1

ATE v2.1 VolatilityEngine may use only the following measures:

1. ATR ratio / ATR%
2. Bollinger Band width ratio
3. True-range shock flag

The following are explicitly out of scope for ATE v2.1:

- Keltner Channels
- Complex realised-volatility models
- Asset-specific threshold tables
- Broker/execution-derived measures
- Intrabar volatility logic

---

# 5. Inputs with Defaults and Allowed Ranges

All inputs must be documented in Pine implementation and exposed only where useful. Defaults must not be silent.

| Input | Default | Allowed Range | Purpose |
|---|---:|---:|---|
| `atrLength` | 14 | 5–100 | ATR calculation length. |
| `atrBaselineLength` | 100 | 20–500 | Asset-normalised ATR baseline lookback. |
| `bbLength` | 20 | 10–100 | Bollinger Band basis and width length. |
| `bbStdDev` | 2.0 | 1.0–3.0 | Bollinger Band standard deviation multiplier. |
| `bbBaselineLength` | 100 | 20–500 | Asset-normalised BB width baseline lookback. |
| `shockLookback` | 20 | 5–100 | Lookback for true-range shock comparison. |
| `shockMultiplier` | 2.5 | 1.5–5.0 | Current true range multiple versus recent baseline required for shock flag. |
| `compressionThreshold` | 0.75 | 0.25–1.00 | Ratio below baseline indicating compression. |
| `normalUpperThreshold` | 1.25 | 1.00–1.75 | Ratio upper bound for normal volatility. |
| `elevatedThreshold` | 1.75 | 1.25–3.00 | Ratio indicating elevated volatility. |
| `unstableThreshold` | 2.50 | 1.75–5.00 | Ratio indicating unstable volatility. |
| `slopeLookback` | 5 | 2–20 | Lookback for expansion/contraction direction. |

Implementation notes:

- ATR ratio should compare current ATR% against the asset's own ATR% baseline.
- BB width ratio should compare current BB width against the asset's own BB width baseline.
- Thresholds are relative to each asset's own historical volatility behaviour where possible.
- Avoid fixed absolute volatility thresholds.
- Missing or insufficient-history values must produce explicit `unknown` state and documented diagnostics, not silent defaults.

---

# 6. Formal Engine Output Contract

VolatilityEngine must publish the standard Engine Output Contract.

| Field | Required Behaviour |
|---|---|
| `score` | Numeric 0–100 score representing volatility regime usefulness / condition quality. It must not represent trade confidence, bullishness, bearishness, position size, stop distance, or trade probability. |
| `state` | One of: `compressed`, `normal`, `expanding`, `elevated`, `unstable`, `shock`, `unknown`. |
| `direction` | One of: `none`, `expanding`, `contracting`, `stable`, `unstable`. It must never be `bullish` or `bearish`. |
| `reason` | Short deterministic explanation of the current volatility classification. |
| `diagnostics` | Supporting values for audit, dashboard display, and research validation. |
| `version` | Semantic engine version matching this specification and implementation. Initial implementation target: `1.0.0-draft`. |

## 6.1 Score Meaning

The `score` represents volatility regime usefulness / condition quality.

It must not mean:

- trade confidence
- bullishness
- bearishness
- position size
- stop distance
- trade probability

High score means the volatility regime is orderly and diagnostically useful.

Low score means the volatility regime is either too compressed, too unstable, shock-like, or insufficiently known to provide useful diagnostic context.

## 6.2 Direction Values

Allowed values:

- `none`
- `expanding`
- `contracting`
- `stable`
- `unstable`

Direction is volatility-direction only. It describes expansion, contraction, stability, or instability of volatility. It does not describe market price direction.

---

# 7. State Model

Allowed `state` values:

| State | Meaning |
|---|---|
| `compressed` | Volatility is materially below the asset's own baseline. |
| `normal` | Volatility is close to the asset's own baseline. |
| `expanding` | Volatility is rising from lower or normal levels but has not reached elevated/unstable classification. |
| `elevated` | Volatility is materially above the asset's own baseline but not shock-like. |
| `unstable` | Volatility is extremely elevated or erratic relative to baseline. |
| `shock` | Current true range triggers the shock flag. |
| `unknown` | Insufficient data or invalid input prevents reliable classification. |

State precedence:

1. `unknown`
2. `shock`
3. `unstable`
4. `elevated`
5. `expanding`
6. `compressed`
7. `normal`

---

# 8. Deterministic Scoring Logic

## 8.1 Derived Values

Implementation should derive:

- `atrPercent = ATR / close * 100`
- `atrBaseline = moving average of atrPercent over atrBaselineLength`
- `atrRatio = atrPercent / atrBaseline`
- `bbWidthRatioRaw = (upperBand - lowerBand) / basis`
- `bbWidthBaseline = moving average of bbWidthRatioRaw over bbBaselineLength`
- `bbWidthRatio = bbWidthRatioRaw / bbWidthBaseline`
- `combinedVolRatio = average of valid atrRatio and bbWidthRatio`
- `volSlope = combinedVolRatio - combinedVolRatio[slopeLookback]`
- `trueRangeBaseline = moving average of true range over shockLookback`
- `shockFlag = true range >= trueRangeBaseline * shockMultiplier`

If one derived ratio is unavailable but the other is valid, the valid ratio may be used and the missing value must be recorded in diagnostics.

If both primary ratios are unavailable, state must be `unknown` and score must be `na` or explicit null according to Pine implementation constraints.

## 8.2 Direction Logic

| Condition | Direction |
|---|---|
| Insufficient data | `none` |
| `shockFlag` true | `unstable` |
| `combinedVolRatio >= unstableThreshold` | `unstable` |
| `volSlope > 0` by implementation tolerance | `expanding` |
| `volSlope < 0` by implementation tolerance | `contracting` |
| Otherwise | `stable` |

## 8.3 State Logic

| Condition | State |
|---|---|
| Insufficient data or invalid denominator | `unknown` |
| `shockFlag` true | `shock` |
| `combinedVolRatio >= unstableThreshold` | `unstable` |
| `combinedVolRatio >= elevatedThreshold` | `elevated` |
| `combinedVolRatio < compressionThreshold` | `compressed` |
| `combinedVolRatio <= normalUpperThreshold` and not compressed | `normal` |
| `combinedVolRatio > normalUpperThreshold` and `volSlope > 0` | `expanding` |
| Fallback | `normal` |

## 8.4 Score Logic

Score must be deterministic and mapped from state and condition quality.

Initial ATE v2.1 scoring table:

| State | Base Score | Rationale |
|---|---:|---|
| `normal` | 85 | Orderly volatility near asset baseline. |
| `expanding` | 70 | Useful diagnostic regime but requires review. |
| `compressed` | 55 | Useful as compression evidence but lower immediate condition quality. |
| `elevated` | 45 | Volatility is high enough to reduce condition quality. |
| `unstable` | 20 | Volatility is too erratic for reliable diagnostic quality. |
| `shock` | 10 | Shock condition dominates normal classification. |
| `unknown` | `na` or explicit null | Insufficient evidence. |

Score may be adjusted only by simple documented modifiers in v2.1. Any future scoring complexity requires specification amendment and validation.

---

# 9. Boundary Rules

VolatilityEngine must obey the following boundaries:

- Must not output `bullish` or `bearish` direction.
- Must not generate buy/sell signals.
- Must not set confidence.
- Must not increase or decrease ConfidenceEngine output in ATE v2.1.
- Must not approve, reject, or modify RiskEngine output in ATE v2.1.
- Must not alter DecisionEngine output in ATE v2.1.
- Must not affect entry logic.
- Must not affect exit logic.
- Must not define position size.
- Must not define stop distance.
- Must not create or modify alerts that imply trade action.
- Must not define trade probability.
- Must not classify action as suitable/unsuitable.
- Must not mutate upstream or downstream engine values.
- Must remain a pure function of documented inputs and bar-close data.

Pine diagnostics should be implemented as individual named diagnostic variables rather than as a complex diagnostics object.

The phrase “unsuitable for action” is intentionally excluded from this specification. Action suitability belongs to RiskEngine or DecisionEngine.

---

# 10. Downstream Consumption Rules

ATE v2.1 integration:

| Consumer | Allowed in ATE v2.1? | Notes |
|---|---:|---|
| DashboardEngine | Yes | May display VolatilityEngine outputs without altering them. |
| Research Mode | Yes | May record and analyse VolatilityEngine outputs. |
| ConfidenceEngine | No | Must not consume VolatilityEngine in ATE v2.1. |
| RiskEngine | No | Must not consume VolatilityEngine in ATE v2.1. |
| DecisionEngine | No | Must not consume VolatilityEngine in ATE v2.1. |

Future ConfidenceEngine or RiskEngine integration requires a separate specification amendment, validation evidence, and governance review.

Minimum evidence before later RiskEngine or ConfidenceEngine integration:

Hermes must demonstrate improvement in at least one of:

- drawdown control
- false-signal filtering
- regime classification
- confidence reliability
- asset qualification quality

Any later integration must not materially reduce explainability or create unstable scoring.

---

# 11. Dashboard Fields

DashboardEngine may display the following VolatilityEngine fields:

- `score`
- `state`
- `direction`
- `reason`
- `version`
- `atrRatio`
- `atrPercent`
- `bbWidthRatio`
- `combinedVolRatio`
- `shockFlag`
- `volSlope`

Pine implementation should expose diagnostics as individual named variables suitable for dashboard display, not as a complex object.

DashboardEngine must remain presentation-only. It must not reinterpret, normalise, smooth, overwrite, or mutate VolatilityEngine values.

Display transformations, if any, must be clearly labelled as display formatting only.

---

# 12. Research Mode Fields

Research Mode should record the following fields per evaluated bar where practical:

- timestamp / bar date
- symbol
- timeframe
- VolatilityEngine version
- `score`
- `state`
- `direction`
- `reason`
- `atrLength`
- `atrBaselineLength`
- `atrPercent`
- `atrRatio`
- `bbLength`
- `bbStdDev`
- `bbBaselineLength`
- `bbWidthRatio`
- `combinedVolRatio`
- `volSlope`
- `shockLookback`
- `shockMultiplier`
- `shockFlag`
- missing/invalid data flags

Research Mode outputs must support reproducibility, RDR-001 artefact creation, and later review of whether VolatilityEngine should remain diagnostic-only or become a validated downstream input.

---

# 13. RDR-001 Validation Plan

## 13.1 Research Question

Does VolatilityEngine classify volatility regimes reproducibly and usefully across the approved ATE v2.1 daily validation universe without lookahead, repainting, or hidden directional bias?

## 13.2 Hypothesis

Asset-normalised ATR% and Bollinger Band width ratios, combined with a true-range shock flag, can classify volatility regimes into `compressed`, `normal`, `expanding`, `elevated`, `unstable`, `shock`, and `unknown` states in a reproducible and explainable way.

## 13.3 Initial Validation Universe

Use a balanced daily universe:

- Gold
- Silver
- Nasdaq / major equities
- S&P 500
- Treasury / gilt proxy
- Major FX pairs

Weekly validation may follow after daily diagnostic behaviour is reviewed.

## 13.4 Required Controls

Validation must check:

- No lookahead bias.
- No repainting.
- Bar-close-only behaviour.
- No bullish/bearish direction leakage.
- No ConfidenceEngine consumption.
- No RiskEngine consumption.
- No DecisionEngine consumption.
- Parameter sensitivity across approved ranges.
- Stability of state classification across assets.
- Whether classifications are explainable from diagnostics.
- Whether compressed/elevated/unstable/shock states correspond to observable volatility conditions.
- Whether outputs add diagnostic value without adding unjustified complexity.

## 13.5 Required Artefacts

Validation should produce:

- Human-readable report under `research/Reports/`.
- Machine-readable summary using the approved research summary schema.
- Run manifest recording schema version, data source, download date, symbols, timeframe, date range, adjustments, transformations, storage location, checksum if available, and known limitations.
- Research Mode output files where practical.
- Negative or inconclusive result capture.

## 13.6 Result Classification

RDR result must classify the evidence as one of:

- supported
- weakly supported
- inconclusive
- falsified
- operationally rejected

Performance or risk-improvement claims are not authorised by this specification. Any later claim that VolatilityEngine improves drawdown control, false-signal filtering, confidence reliability, or asset qualification quality requires separate RDR evidence.

---

# 14. Acceptance Criteria

VolatilityEngine v1.0 Draft may proceed to Pine implementation only if the implementation plan preserves this specification.

The implemented engine may be accepted for ATE v2.1 diagnostic use only if:

- It publishes all Engine Output Contract fields.
- It compiles under Pine Script v6.
- It uses bar-close-only logic.
- It introduces no lookahead or repainting behaviour.
- It uses only approved ATE v2.1 measures.
- It uses documented defaults and allowed ranges.
- It uses asset-normalised thresholds where possible.
- It avoids fixed absolute volatility thresholds as primary logic.
- It never outputs bullish/bearish direction.
- It does not affect ConfidenceEngine, RiskEngine, or DecisionEngine.
- It does not classify action suitability.
- It exposes dashboard fields without allowing DashboardEngine mutation.
- It records or supports Research Mode fields for validation.
- Its state and score are explainable from diagnostics.
- Its validation plan satisfies RDR-001 before any non-diagnostic promotion.

---

# 15. Rejection Criteria

VolatilityEngine v1.0 Draft or implementation should be rejected or revised if it:

- Violates the Engine Output Contract.
- Produces bullish or bearish direction.
- Generates buy/sell signals.
- Influences ConfidenceEngine, RiskEngine, or DecisionEngine in ATE v2.1.
- Uses Keltner Channels, complex realised-volatility models, or asset-specific threshold tables in v2.1.
- Uses undocumented defaults.
- Uses fixed absolute volatility thresholds as the primary classification method.
- Cannot explain state and score from diagnostics.
- Duplicates TrendEngine by measuring direction/persistence of price movement.
- Duplicates MomentumEngine by measuring directional rate-of-change rather than volatility regime.
- Adds parameter clutter without evidence.
- Creates unstable scoring.
- Introduces lookahead or repainting risk.
- Makes performance or risk-reduction claims without RDR-001 evidence.
- Reduces explainability.

---

# 16. Blocking vs Deferrable Open Questions

## 16.1 Blocking Questions

No blocking Product Owner / Chief Systems Architect questions remain for diagnostic-only ATE v2.1 specification drafting.

Implementation must still confirm Pine-specific feasibility for:

- Exact representation of null/`na` score for `unknown` state.
- Diagnostic container format for `diagnostics` within Pine constraints.
- Dashboard display layout.
- Research Mode export mechanism.

## 16.2 Deferrable Questions

The following are intentionally deferred until after daily diagnostic validation:

- Whether VolatilityEngine should later feed RiskEngine.
- Whether VolatilityEngine should later feed ConfidenceEngine.
- Whether weekly validation confirms or changes daily behaviour.
- Whether scoring thresholds require amendment after validation.
- Whether score modifiers are useful or unnecessary.
- Whether VolatilityEngine improves drawdown control, false-signal filtering, regime classification, confidence reliability, or asset qualification quality.

---

# 17. Versioning and Migration Impact

Initial implementation target: `1.0.0-draft`.

This specification introduces a new diagnostic engine contract for ATE v2.1. It does not change existing ConfidenceEngine, RiskEngine, or DecisionEngine contracts.

Any future change that allows downstream consumption by ConfidenceEngine, RiskEngine, or DecisionEngine is an architecture/contract-impacting change and requires:

- Specification amendment.
- Architecture impact review.
- RDR evidence where research claims are made.
- EDR where interface or engine-flow changes are material.
- Regression evidence.
- Product Owner review where scope/risk is affected.

---

# 18. Changelog Note

VolatilityEngine v1.0 Draft revised and approved for ATE v2.1 based on Product Owner / Chief Systems Architect decisions:

- Approved by Paul Austin for diagnostic-only ATE v2.1 implementation planning.
- Set ATE v2.1 scope to diagnostic-only.
- Prohibited ConfidenceEngine, RiskEngine, and DecisionEngine consumption in ATE v2.1.
- Prohibited impact on entry logic, exit logic, position sizing, stop placement, and alerts that imply trade action.
- Defined allowed direction values and banned bullish/bearish direction.
- Defined score meaning as volatility regime usefulness / condition quality.
- Defined allowed state values.
- Restricted v2.1 measures to ATR ratio / ATR%, Bollinger Band width ratio, and true-range shock flag.
- Removed action-suitability language from VolatilityEngine scope.
- Added dashboard and Research Mode output fields.
- Added RDR-001 validation plan.
- Added enforceable acceptance and rejection criteria.
- Separated blocking and deferrable open questions.
- Confirmed Pine diagnostics should be individual named diagnostic variables, not a complex object.

---

# 19. Approval Status

Approval: Paul Austin approves the revised VolatilityEngine Specification for ATE v2.1 diagnostic-only implementation planning.

Approval boundaries:

- VolatilityEngine may be implemented in Pine for DashboardEngine display and Research Mode output.
- VolatilityEngine must not affect ConfidenceEngine, RiskEngine, DecisionEngine, entry logic, exit logic, position sizing, stop placement, or alerts that imply trade action.
- VolatilityEngine direction must not be bullish or bearish.
- Diagnostics should be implemented in Pine as individual named diagnostic variables rather than a complex object.

Recommendation: Approved for diagnostic-only Pine implementation planning.

Rationale: This revised specification now defines scope, non-scope, inputs, output contract, state model, scoring logic, boundaries, downstream consumption rules, dashboard fields, Research Mode fields, RDR-001 validation plan, acceptance criteria, rejection criteria, open questions, and changelog note.

It is suitable to proceed into implementation planning for ATE v2.1 diagnostic-only VolatilityEngine, provided Pine implementation preserves the boundaries in this specification and no code is allowed to affect ConfidenceEngine, RiskEngine, or DecisionEngine in ATE v2.1.
