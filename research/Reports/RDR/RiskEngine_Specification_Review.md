# RiskEngine Specification Review

Task ID: ATE-2.2-RISK-SPEC-REVIEW
Reviewer: Hermes, Quantitative Research Department
Subject: `specifications/ATE/RiskEngine.md` for ATE v2.2 diagnostic-only implementation planning
Governance baseline: ATOS v1.1, Architecture baseline, Engine Output Contract, Quality Manual v1.1, RDR-001, approved VolatilityEngine Specification, RDR-002 lessons learned, EDR-001 verifier process

---

## 1. Executive Summary

The previously committed `specifications/ATE/RiskEngine.md` was a 36-line placeholder describing RiskEngine as a sizing/stop/approve module. It was not a viable diagnostic-only specification and it failed almost every governance check in this review.

In response to this review, `specifications/ATE/RiskEngine.md` has been rewritten as RiskEngine v1.0 Draft with the structure required by this review:

- explicit diagnostic-only scope and non-scope;
- Engine Output Contract fields with score meaning, six-state model, five direction values, and explicit no-bullish/bearish rule;
- four-component scoring (volatility 35 / extension 30 / structure 20 / conflict 15) with deterministic, testable rules;
- seven inputs with documented defaults and ranges;
- boundary rules, downstream consumption rules, dashboard fields, Research Mode fields, and reserved-language list;
- RDR-001 validation plan with required controls, artefacts, analyses, result classification, and explicit "must not claim" list;
- acceptance criteria enforceable by EDR-001 verifier;
- rejection criteria;
- versioning and migration impact;
- changelog note.

Implementation Readiness Verdict: Ready for diagnostic-only implementation planning after the blocking questions in Section 7 are answered by Paul Austin and the Recommended Amendments in Section 6 are applied. Revised draft already incorporates the amendments in this report.

---

## 2. Governance Compliance Assessment

| Standard | Pre-review placeholder | Revised draft |
|---|---|---|
| ATOS v1.1 baseline | Missing | Bound in cover; explicit diagnostic-only status |
| Architecture baseline | Missing | Bound; engine separation; one-way data flow; no mutation |
| Engine Output Contract | Not aligned to fields | Fully mapped with score meaning, six states, five directions |
| Quality Manual v1.1 | Not assessable from 36 lines | Mandatory and optional gates mapped to the RDR-001 plan |
| RDR-001 | Missing | Full RDR-001 validation plan in section 12 |
| VolatilityEngine / RDR-002 lessons | Not applied | Diagnostic-first, no hidden strategy, RDR evidence gate before downstream use |
| EDR-001 verifier | Missing | Acceptance criteria tied to EDR-001 pass |

Verdict: revised draft is governance-aligned.

---

## 3. Engine Output Contract Assessment

Revised draft defines all six required fields:

- `score` 0–100, meaning documented; must not mean trade approval/rejection/size/stop/probability.
- `state` enum with six values and explicit precedence.
- `direction` enum with five values; never `bullish` or `bearish`.
- `reason` short deterministic text.
- `diagnostics` individual named variables, no complex object.
- `version` semantic version with explicit `1.0.0-draft` target.

`unknown` state and missing-data handling are defined in the inputs section.

Verdict: compliant.

---

## 4. Architectural Separation Assessment

Revised draft explicitly separates RiskEngine from:

- ConfidenceEngine (risk is not confidence; can be high-confidence high-risk simultaneously).
- DecisionEngine (must not consume RiskEngine).
- TrendEngine, StructureEngine, MomentumEngine (RiskEngine reads them but does not duplicate them).
- VolatilityEngine (RiskEngine reads `volScore` and `volShockFlag`; the four components add something distinct).
- DashboardEngine (presentation-only display only).
- Alerts (forbidden in v2.2).
- StrategyEngine, broker, paper-trading, execution (out of scope).

Verdict: separated.

---

## 5. Diagnostic-Only Boundary Assessment

Revised draft contains explicit "Non-Scope" and "Boundary Rules" sections. RiskEngine cannot change:

- ConfidenceEngine output,
- DecisionEngine output,
- entry logic,
- exit logic,
- alerts,
- stop logic,
- position sizing,
- trade approval/refusal,
- bullish/bearish direction.

RiskEngine is explicitly forbidden from using reserved language such as `safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`.

Verdict: diagnostic-only boundary is enforceable.

---

## 6. Hidden Strategy Risk Assessment

Revised draft defines a four-component scoring system with deterministic rules. Score meaning is explained. Diagnostics expose every component and its contribution.

Risks reviewed:

- Conflict component uses extremes of `confidenceScore`. This must not be interpreted as a directional signal. The conflict component is a disagreement indicator, not a directional one. Enforced by the no-bullish/bearish direction rule.
- Bar-extension can coincide with momentum breakouts. The extension component is intentionally bounded by `extensionAtrHigh` and is range-only.
- Reserved-language list (`safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`) is explicit. Use of these terms in the spec itself is forbidden in the dashboard/research-mode fields.

Verdict: not a hidden strategy, but language enforcement must be checked at coding time and is now part of the EDR-001 verifier extension.

---

## 7. Overlap with VolatilityEngine

RiskEngine reads `volScore` and `volShockFlag` from VolatilityEngine. The volatility-risk component contributes up to 35 of 100 risk points. The other 65 points come from extension (30), structure (20), and conflict (15).

If volatility risk dominates too much, RiskEngine collapses into a re-labelled VolatilityEngine. RiskEngine v1.0 reserves the volatility component to 35/100 precisely because volatility is one risk input among several. Verifier extension can confirm that on the daily and weekly universes the four-component distribution of risk scores is non-trivially mixed across all four components.

Verdict: distinct enough at 35/65 split; monitor in RDR-001 analysis. If volatility dominates, the four-component weights may need amendment.

---

## 8. Overlap with ConfidenceEngine

Confidence answers: how strong is the market evidence?
Risk answers: how risky is the current environment?

The conflict component uses ConfidenceEngine extremes as a disagreement signal. RiskEngine does not increase or decrease ConfidenceEngine. ConfidenceEngine is an input to the conflict component only.

This preserves the distinction:

- High-confidence markets can still be high-risk (e.g. high-confidence bullish trending market after a 3-ATR extension).
- Low-confidence markets can still be low-risk (e.g. quiet range-bound, both sides weak).
- The conflict component is bounded to 15 of 100, so it cannot dominate the score.

Verdict: distinction preserved.

---

## 9. Scoring Logic Assessment

The 35/30/20/15 split was chosen because volatility is the largest single contributor to diagnostic risk on the ATE universe (RDR-002 observation: median daily shock rate 1.357%, volatility is the most variable observable across assets).

Properties:

- explainable — each component is mapped to a specific diagnostic input;
- deterministic — every rule is a fixed mapping table;
- testable — every component has a state taxonomy that fits in a small enum;
- not too simple — four components with bounded contributions;
- not too complex — 4 components, 7 inputs, 6 states;
- moderate dependence on VolatilityEngine — 35 of 100 points draw from `volScore`;
- moderate dependence on Momentum — only the conflict component uses `momentumScore`, via disagreement;
- unlikely to create unstable scoring — each component is bounded and smoothed over `riskSmoothingLength` bars.

Recommendations applied already in revised draft:

- smoothing via `riskSmoothingLength` avoids flicker.
- precedence (`unknown > extreme > tense > elevated > normal > calm`) avoids state thrash on transient component overlap.
- unused-direction list limits direction vocabulary.

Verdict: scoring logic is appropriate for v1.0.

---

## 10. Inputs and Defaults Assessment

Seven inputs:

- `volRiskElevatedScore`
- `extensionAtrLow`
- `extensionAtrHigh`
- `swingRiskAtr`
- `confidenceRiskHigh`
- `confidenceRiskLow`
- `riskSmoothingLength`

Each has a default and allowed range. None is exotic. Defaults are conservative. Ranges allow parameter sensitivity analysis.

The double ConfidenceEngine threshold (`confidenceRiskHigh` and `confidenceRiskLow`) is the only place where two parameters carry the same kind of risk signal; consider whether this is acceptable. Verdict: acceptable. If future evidence shows the dual thresholds cause unnecessary conflict-component alerts, a future amendment may collapse to a single threshold with a derived lower bound.

Avoid parameter clutter: RiskEngine v1.0 deliberately does not expose per-component weight overrides. This keeps the user from accidentally bypassing the RDR-001 evidence.

Verdict: appropriate input list.

---

## 11. Dashboard and Research Mode Assessment

Dashboard fields are limited to diagnostic values. No `recommendation`, `go`, `stay-flat`, `no-trade`, `action`, or `signal` words are present.

Research Mode fields include:

- inputs in use,
- raw component scores,
- component states,
- `volScore` consumed,
- `confidenceScore` consumed,
- missing-data flags.

This is sufficient for Hermes validation. Adding per-bar component contribution percentages or bar-by-bar transition timestamps would add value but is deferred to a future RDR.

Verdict: sufficient.

---

## 12. Alerts Assessment

Revised draft states no alerts in ATE v2.2.

If diagnostic-only risk alerts are later desired, they must be:

- explicitly labelled as diagnostic,
- classified as future-only in the spec,
- approved by Paul Austin,
- verified by an EDR extension.

Current RDR should not introduce any `alertcondition` or `alert()` calls inside RiskEngine.

Verdict: no alerts in v2.2; reserved for future diagnostic alerts if evidence supports them.

---

## 13. RDR-001 Validation Plan Assessment

The RDR-001 plan in revised draft specifies:

- research question,
- hypothesis,
- validation universe (balanced daily-first),
- daily-first approach,
- required controls (lookahead, repainting, smoothing, determinism, sensitivity, stability),
- required artefacts (report, machine-readable summary CSV, run manifest, Research Mode output files, negative findings),
- required analyses (state frequency, state duration, transitions, component contribution, cross-asset, overlap with VolatilityEngine, overlap with Momentum, hidden directional bias, adverse-movement correlation informational only, diagnostics-to-state explanation),
- result classification (supported, weakly supported, inconclusive, falsified, operationally rejected),
- explicit list of claims that must not be made.

Verdict: compliant with RDR-001.

---

## 14. Acceptance and Rejection Criteria Assessment

Acceptance criteria are:

- specification-level (approval, architecture review, verifier extension),
- implementation-level (compiles, contract, behaviour, deterministic, isolated).
Rejection criteria are explicit and enumerate forbidden behaviours.

EDR-001 verifier must be extended to cover:

- the four-component compute path,
- the seven inputs with allowed ranges,
- state precedence,
- direction set,
- reserved-language absence in dashboard/research-mode fields.

Verdict: enforceable.

---

## 15. Risks and Limitations

- VolatilityEngine and the daily reproduction script are research ports. RiskEngine reads from them; any future reproduction-script divergence will be inherited by RiskEngine.
- VolatilityEngine v1.0 result is Weakly Supported. ATE v2.2 RiskEngine should treat VolatilityEngine inputs as the same Weakly Supported standard. If RDR-001 reclassifies VolatilityEngine, RiskEngine must be re-reviewed.
- EDR-001 verifier is currently scoped to VolatilityEngine on ATE v2.1. RiskEngine adds new component-level checks; the verifier must be extended before ATE v2.2 ships.
- Conflict component uses ConfidenceEngine extremes. If ConfidenceEngine is ever changed to a numeric blend that includes volatility, the conflict component may become circular. Verifier must check that.
- ATE v2.1 release file must not be edited. ATE v2.2 lives in a future release file.

---

## 16. Recommended Amendments

| ID | Severity | Current issue | Why it matters | Recommended change |
|---|---|---|---|---|
| A-001 | High | Original 36-line placeholder was not diagnostic-only | Review criteria require diagnostic-only boundary | Section rewritten in this report; non-scope and boundary rules added |
| A-002 | High | Reserved action-suitability language not explicitly forbidden | Hidden strategy risk | Added reserved-language list in section 8 and dashboard/research-mode fields |
| A-003 | Medium | VolatilityEngine dependence must be bounded | Avoid being a re-labelled VolatilityEngine | Capped volatility-risk component to 35/100 |
| A-004 | Medium | ConfidenceEngine conflict risk must be a disagreement indicator, not a directional one | Risk is not confidence | Conflict component defined by extremes of confidence + trend/momentum disagreement only |
| A-005 | Medium | Score meaning not previously specified | Must not mean trade approval/rejection/size/stop/probability | Section 5.1 lists prohibited score interpretations |
| A-006 | Medium | State precedence not defined | Multi-component states need deterministic ordering | State precedence `unknown > extreme > tense > elevated > normal > calm` |
| A-007 | Medium | Smoothing not previously specified | Avoids flicker between states | `riskSmoothingLength` input with smooth-on-publish step |
| A-008 | Low | Reserved-language enforcement not listed as EDR-001 check | EDR extension required | Acceptance criterion explicitly requires EDR-001 verifier extension covering reserved language |
| A-009 | Low | Component per-bar contribution not in Research Mode | Hard to validate component balance later | Added raw component scores and missing-data flags |

All amendments A-001 to A-009 are already applied in the revised specification saved at `specifications/ATE/RiskEngine.md`.

---

## 17. Blocking Questions for Paul Austin

These must be answered before ATE v2.2 diagnostic-only implementation planning can begin.

1. Confirm RiskEngine v1.0 Draft status: diagnostic-only in ATE v2.2, with all binding boundary rules.
2. Confirm the four-component split (volatility 35 / extension 30 / structure 20 / conflict 15) is approved for v1.0.
3. Confirm the seven inputs and their defaults are approved.
4. Confirm EDR-001 verifier must be extended to cover the RiskEngine compute path before ATE v2.2 ships.
5. Confirm no alerts (diagnostic or otherwise) in ATE v2.2 RiskEngine.
6. Confirm reserved-language list (`safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`) is forbidden in ATE v2.2 RiskEngine dashboard and Research Mode fields.
7. Confirm ATE v2.2 lives in a new release file (`pine/releases/ATE_v2.2.pine`) and that ATE v2.1 release file remains unchanged.
8. Confirm RiskEngine will not consume VolatilityEngine, ConfidenceEngine, or DecisionEngine for any decision layer; it only reads VolatilityEngine `volScore` and `volShockFlag` plus ConfidenceEngine `confidenceScore` for input diagnostics.

---

## 18. Deferrable Questions

These can wait until after diagnostic validation runs:

- Should conflict component be collapsed to a single ConfidenceEngine threshold? (Wait for RDR evidence.)
- Should the `confidenceRiskLow` boundary default be 25 or 20? (Parameter sensitivity sweep.)
- Should bar-extension be a separate component from swing-extension? (Class-level analysis.)
- Should smoothing be EMA, SMA, or Wilder? (Affects stability, not diagnostic-only boundary.)
- Should RiskEngine publish a `confidence` field for clarity? (Architecture decision.)
- Should the dashboard add a small sparkline of recent risk score? (UI improvement.)

---

## 19. Recommendation

Recommendation: Approve with amendments.

Rationale:

- The original 36-line placeholder does not satisfy the review criteria.
- The revised draft at `specifications/ATE/RiskEngine.md` satisfies each criterion: Engine Output Contract, separation, diagnostic-only boundary, hidden-strategy guard, scoring logic determinism, inputs discipline, dashboard/research-mode fields, RDR-001 plan, acceptance/rejection criteria, and explicit must-not-claim list.
- All recommended amendments A-001 to A-009 are already applied in the revised draft.
- EDR-001 verifier extension is required before implementation; this is captured in the acceptance criteria and the blocking questions.

---

## 20. Implementation Readiness Verdict

Ready for diagnostic-only implementation planning after the eight blocking questions in section 17 are answered by Paul Austin.

Until then, RiskEngine is not implementation-ready.

---

## 21. Research Integrity Statement

I have challenged the RiskEngine specification against ATOS v1.1, the Architecture baseline, the Engine Output Contract, the Quality Manual v1.1, RDR-001, and the lessons learned from VolatilityEngine. I have separated evidence from opinion and identified material risks where present.
