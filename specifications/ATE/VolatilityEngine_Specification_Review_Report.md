# VolatilityEngine Specification Review Report

Date: 2026-07-03
Reviewer: Hermes, Quantitative Research Department / audit support
Subject: `specifications/ATE/VolatilityEngine.md`
Governance baseline reviewed against:
- Approved ATOS v1.1 governance baseline components available in repo
- Active Architecture baseline
- Engine Output Contract
- Austin Trading Quality Manual v1.1
- RDR-001 research storage/reporting standards

---

## Executive Verdict

Recommendation: Revise again before Pine implementation.

Current status:
- Concept is sound.
- Governance fit is directionally correct.
- Specification is not yet implementable.
- It does not satisfy the Engine Output Contract.
- It does not yet satisfy Quality Manual v1.1 Gate 2 Specification requirements.
- It does not satisfy RDR-001 validation/reproducibility expectations.
- Do not proceed to ATE v2.1 implementation until amended.

Referenced file:
- `specifications/ATE/VolatilityEngine.md`
- Current spec is only 45 lines and stops after the engine question.

---

## 1. Compliance with Engine Output Contract

Finding: Non-compliant.

Architecture baseline requires every engine to publish:

- `score`
- `state`
- `direction`
- `reason`
- `diagnostics`
- `version`

Current VolatilityEngine spec defines none of these as formal outputs.

Missing:
- No `score` definition.
- No score scale.
- No state enum.
- No direction rule.
- No diagnostics schema.
- No reason-generation rule.
- No semantic versioning rule beyond `Version: 1.0 Draft`.
- No null/`na` handling.
- No downstream consumption rule.
- No migration/version impact note.

Required amendment:
VolatilityEngine must define an explicit output contract, for example:

- `score`: 0–100 volatility condition/suitability score, not directional confidence.
- `state`: one of defined volatility regimes.
- `direction`: normally `none` or `neutral`; volatility must not imply bullish/bearish direction.
- `reason`: short deterministic explanation.
- `diagnostics`: ATR%, ATR percentile/z-score, volatility slope, expansion/contraction flag, shock flag, threshold values.
- `version`: semantic version matching the implemented engine.

---

## 2. Clarity of Purpose

Finding: Partially clear.

Good:
- The spec correctly says VolatilityEngine does not generate buy/sell signals.
- It correctly frames the engine question: “What volatility regime is the market currently in?”
- It correctly states volatility should not automatically increase confidence.

Weak:
- “Market movement expanding, contracting, normal, unstable, or unsuitable for action” is useful but not operationally defined.
- “Diagnostic and risk-support module” is directionally right but not staged clearly enough.
- No distinction between volatility regime classification, action suitability, risk adjustment, and confidence weighting.

Required amendment:
Purpose should be tightened to:

> VolatilityEngine classifies the current volatility regime and publishes diagnostic evidence for downstream engines. It does not determine direction, confidence, position size, stop distance, or final action. RiskEngine may later consume the volatility read to judge safety/suitability. ConfidenceEngine may consume volatility only as a context/quality qualifier, not as an automatic confidence booster.

---

## 3. Separation from ConfidenceEngine and RiskEngine

Finding: Conceptually good, but specification boundaries are incomplete.

Good:
- Lines 27–35 correctly separate:
  - VolatilityEngine = market condition
  - ConfidenceEngine = strength of evidence
  - RiskEngine = safety/risk interpretation

Risk:
- The phrase “unsuitable for action” edges into RiskEngine responsibility.
- If VolatilityEngine outputs “suitable/unsuitable”, that becomes a risk decision unless clearly labelled as diagnostic only.

Required amendment:
Use regime language inside VolatilityEngine, not action-permission language.

Preferred states:
- `compressed`
- `normal`
- `expanding`
- `elevated`
- `unstable`
- `shock`

Avoid as primary VolatilityEngine states:
- `safe`
- `unsafe`
- `approved`
- `blocked`
- `tradeable`
- `untradeable`

Those belong to RiskEngine or DecisionEngine.

---

## 4. Risk of Overlap with TrendEngine or MomentumEngine

Finding: Moderate risk unless boundaries are made explicit.

Overlap risk with TrendEngine:
- Volatility expansion can coincide with trend strength.
- If VolatilityEngine uses directional slope, breakout behaviour, or persistence of move, it may duplicate TrendEngine.

Overlap risk with MomentumEngine:
- Volatility expansion can look like momentum acceleration.
- If VolatilityEngine scores rate of price change rather than dispersion/range expansion, it may duplicate MomentumEngine.

Required boundary:
VolatilityEngine should measure magnitude/dispersion of movement, not direction or rate-of-change bias.

Allowed VolatilityEngine inputs:
- ATR
- True range
- Normalised ATR / ATR%
- Bollinger Band width
- Realised volatility
- Range percentile
- Volatility percentile/z-score
- Expansion/contraction relative to historical baseline

Avoid:
- Moving average slope as a primary input.
- ROC as primary signal.
- Directional breakout confirmation.
- Bullish/bearish labels.
- Trend persistence scoring.
- Momentum divergence.

---

## 5. Scoring Logic

Finding: Currently absent, therefore insufficiently testable.

The spec has no scoring logic, so it cannot be reviewed for correctness, reproducibility, or Pine implementation safety.

Recommended scoring approach:
Keep it simple for ATE v2.1.

Do not create a complex multi-factor volatility model yet.

Suggested v2.1 model:
- Primary measure: normalised ATR or ATR percentile.
- Secondary measure: volatility expansion/contraction slope or Bollinger Band width percentile.
- Optional shock flag: current true range materially above recent baseline.

Example structure:
- `volatilityLevel`: percentile or z-score of ATR%.
- `volatilityTrend`: expanding / contracting / stable.
- `shockFlag`: true when current range exceeds defined threshold.
- `state`: deterministic mapping from level + trend + shock.
- `score`: 0–100 condition score.

Important:
Define what the score means.

Preferred:
- `score` = volatility regime intensity/suitability-for-analysis score.

Avoid:
- `score` = confidence.
- `score` = trade probability.
- `score` = direction.
- `score` = position sizing recommendation.

Testability requirements:
- Fixed formulas.
- Fixed default lookbacks.
- Fixed thresholds.
- Documented input ranges.
- Deterministic state table.
- Known examples for compressed, normal, expanding, unstable, shock conditions.

---

## 6. Validation Plan under RDR-001

Finding: Fails RDR-001 at present.

Current spec has no validation plan.

RDR-001 requires evidence discipline, reproducibility, data scope, methodology, artefact paths, limitations, and result classification where research claims are made.

Required validation plan:
Before promotion beyond draft/lab status, define:

- Research question: “Does VolatilityEngine classify volatility regimes reproducibly and usefully across the approved research universe?”
- Hypothesis: “ATR/realised-volatility percentile regimes can identify compressed, normal, expanding, elevated, and unstable conditions without using future data.”
- Instruments: Gold, Silver, Gilts, Forex, or the exact ATE v2.1 validation universe.
- Timeframe: Daily primary, unless Paul explicitly approves otherwise.
- Date range: must be specified.
- Data source: must be specified.
- Bias controls:
  - no lookahead
  - no repainting
  - bar-close only
  - no future volatility percentile leakage
  - parameter sensitivity
  - regime-dependence review
- Artefacts:
  - human report under `research/Reports/`
  - machine-readable summary under approved schema
  - manifest with schema version
  - backtest/validation artefacts under approved folder structure
  - negative/inconclusive findings retained
- Result classification: supported / weakly supported / inconclusive / falsified / operationally rejected

Important:
If the engine only claims “diagnostic classification”, validation can be lighter than a performance claim.

If the engine claims “improves decisions”, “reduces risk”, or “improves returns”, full research validation is required.

---

## 7. Acceptance and Rejection Criteria

Finding: Not enforceable yet.

Current spec has no acceptance or rejection criteria.

Required acceptance criteria:
The specification should say VolatilityEngine may proceed only if:

- It publishes all Engine Output Contract fields.
- It compiles in Pine v6.
- It is bar-close only.
- It has no lookahead/repainting.
- Its states are deterministic from documented inputs.
- Its thresholds/defaults/ranges are documented.
- It does not produce buy/sell signals.
- It does not output bullish/bearish direction except explicit `none`/`neutral`.
- It does not mutate or reinterpret other engine outputs.
- It can be validated on the approved daily research universe.
- It produces reproducible diagnostics.

Required rejection criteria:
Reject or revise if:

- It duplicates TrendEngine or MomentumEngine.
- It behaves as a hidden confidence booster.
- It makes action/risk approval decisions directly.
- It requires undocumented thresholds.
- It cannot explain each state.
- It creates parameter clutter without evidence.
- It depends on future bars or repainting pivots.
- It makes performance claims without RDR-001 evidence.
- It creates “unsuitable for action” decisions that belong to RiskEngine.

---

## 8. Diagnostic Only, Risk-Support, Confidence Input, or Staged Combination

Recommendation: staged combination.

Best governance-compliant staging:

Stage 1 — ATE v2.1 draft/lab:
- Diagnostic only.
- Publishes volatility regime.
- No direct effect on confidence, risk approval, or final decisions.
- Used by DashboardEngine for inspection only.
- Used by Hermes for validation.

Stage 2 — validation candidate:
- Risk-support input.
- RiskEngine may consume VolatilityEngine output to qualify risk.
- Example: elevated/unstable volatility can widen caution, reduce suitability, or require stronger confirmation.
- VolatilityEngine still does not approve/reject actions itself.

Stage 3 — later, only if validated:
- Confidence input as a context modifier, not a booster.
- Example: unstable volatility may reduce evidence reliability.
- Compressed volatility may mark “low information” rather than increase confidence.
- Expanding volatility may support confidence only when Trend/Structure/Momentum independently agree.

Do not let VolatilityEngine become:
- a directional signal engine,
- a position-sizing engine,
- a stop-distance engine,
- a hidden trade filter,
- a confidence amplifier without evidence.

---

## 9. Open Questions That Must Be Answered Before Pine Implementation

Must answer before implementation:

1. What is the official `score` meaning?
   - volatility intensity?
   - volatility suitability?
   - regime confidence?
   - risk pressure?

2. What are the allowed `state` values?

3. Should `direction` always be `none`/`neutral`?

4. Which volatility measures are approved for v2.1?
   - ATR%
   - ATR percentile
   - Bollinger Band width
   - realised volatility
   - true-range shock flag

5. What are the default lookbacks and allowed ranges?

6. How are thresholds defined?
   - fixed?
   - percentile-based?
   - z-score?
   - asset-specific?
   - universal across assets?

7. Should the first implementation be diagnostic-only?

8. Can RiskEngine consume VolatilityEngine in ATE v2.1, or only after validation?

9. Can ConfidenceEngine consume VolatilityEngine in ATE v2.1, or should that be explicitly deferred?

10. What is the minimum validation universe for ATE v2.1?

11. Does “unsuitable for action” belong in VolatilityEngine terminology, or should that wording be reserved for RiskEngine?

12. What exact diagnostics must DashboardEngine display?

13. What result would cause rejection?
   - poor state stability?
   - too much overlap with momentum?
   - no explanatory value?
   - inconsistent behaviour across assets?

Can defer until after initial diagnostic prototype:
- Final tuned thresholds.
- Weighting into ConfidenceEngine.
- RiskEngine adjustment formulas.
- Performance-improvement claims.
- Release-candidate promotion decision.

---

## 10. Should Implementation Proceed into ATE v2.1?

Recommendation: No, not yet.

Proceed only after specification amendments.

Current VolatilityEngine.md is a concept note, not an implementation-ready specification.

Quality status:
- Specification Gate: not passed.
- Engine Contract Compliance Gate: not passed.
- Architecture impact: partially addressed, not complete.
- RDR-001 validation plan: not passed.
- Acceptance/rejection criteria: absent.
- Implementation readiness: blocked.

---

## Recommended Amendments

Add the following sections before implementation:

1. Scope and non-scope
- Explicitly state what VolatilityEngine does and does not do.

2. Inputs
- OHLC daily bars.
- ATR length.
- Percentile/z-score lookback.
- Expansion/contraction lookback.
- Optional Bollinger width setting if used.
- Defaults and allowed ranges.

3. Output Contract
Define:
- `score`
- `state`
- `direction`
- `reason`
- `diagnostics`
- `version`

4. State model
Example:
- `compressed`
- `normal`
- `expanding`
- `elevated`
- `unstable`
- `shock`
- `unknown`

5. Deterministic scoring table
Example:
- Low percentile + contracting = compressed.
- Mid percentile + stable = normal.
- Rising percentile + positive vol slope = expanding.
- High percentile = elevated.
- Extreme percentile or shock flag = unstable/shock.

6. Boundary rules
- No bullish/bearish output.
- No buy/sell signals.
- No action approval.
- No position sizing.
- No stop placement.
- No mutation of other engine outputs.

7. Downstream consumption rule
- ATE v2.1: diagnostic-only unless Paul approves risk-support use.
- RiskEngine use requires explicit amendment.
- ConfidenceEngine use requires explicit amendment and validation.

8. Validation plan
Must satisfy RDR-001:
- hypothesis
- universe
- timeframe
- data source
- date range
- methodology
- artefacts
- reproducibility manifest
- bias controls
- limitations
- classification

9. Acceptance criteria
Make them testable.

10. Rejection criteria
Make them enforceable.

11. Open questions
Separate:
- blocking before Pine
- deferrable until validation
- Product Owner decisions

---

## Open Questions for Paul Austin

Blocking:

1. Should VolatilityEngine v2.1 be diagnostic-only, with RiskEngine/ConfidenceEngine integration deferred?
2. Should `direction` always be `none` for VolatilityEngine?
3. Should the volatility score represent volatility intensity, market condition suitability, reliability of evidence, or risk pressure?
4. Are the first supported regimes compressed, normal, expanding, elevated, unstable/shock?
5. Which primary measure should be used first: ATR%, ATR percentile, realised volatility, Bollinger Band width, or a combined simple model?
6. Should “unsuitable for action” be removed from VolatilityEngine and reserved for RiskEngine?
7. Should ATE v2.1 include only Dashboard visibility, or should downstream engines consume volatility immediately?
8. What validation universe should be used for first acceptance: Gold/Silver/Gilts/Forex daily, or narrower initial set?
9. Should volatility thresholds be universal or asset-normalised?
10. What is the minimum acceptable evidence before VolatilityEngine can affect RiskEngine or ConfidenceEngine?

---

## Final Recommendation

Recommendation: Revise again.

Reason:
The concept is approved in principle, but the specification is not implementation-ready. It lacks the mandatory Engine Output Contract fields, scoring logic, validation plan, acceptance criteria, rejection criteria, and enforceable downstream-boundary rules required under the Architecture baseline, Quality Manual v1.1, and RDR-001.

Implementation into ATE v2.1 should be blocked until amended.

Best path:
- Revise the spec.
- Keep v2.1 diagnostic-only.
- Validate behaviour under RDR-001.
- Then consider staged RiskEngine support.
- Defer ConfidenceEngine integration until evidence shows volatility improves evidence quality rather than merely adding complexity.
