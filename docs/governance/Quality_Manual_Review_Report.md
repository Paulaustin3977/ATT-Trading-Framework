# Quality Manual Review Report

Date: 2026-07-03
Reviewer: Hermes, Quantitative Research Department
Document reviewed: `docs/governance/Quality_Manual.md`
Scope: ATOS v1.1 draft quality governance
Status: Review report for Paul Austin; not an approval

## Executive Assessment

The draft Quality Manual is directionally strong and consistent with the Austin Trading Team's evidence-first culture. It correctly rejects cosmetic quality, treats negative results as useful knowledge, reinforces the no-execution boundary, and gives Hermes a challenge/research role rather than final approval authority.

However, the draft is not yet enforceable enough for ATOS v1.1. Several standards are phrased as principles rather than testable gates. It also lacks explicit data, security, waiver, decision-record, release-manifest, regression, and post-release incident controls. These omissions would make quality dependent on judgement rather than a repeatable operating system.

Recommended verdict: Revise before approval.

## Strengths

- Clear quality philosophy: working code is not sufficient without documentation, validation, and explanation.
- Correctly states that backtests are evidence, not proof.
- Reinforces the no-live-execution, no-broker, no-paper-trading boundary.
- Includes a useful nine-gate structure.
- Aligns with the active `Architecture.md` Engine Output Contract.
- Preserves Hermes as a critical reviewer, not final governance approver.
- Captures negative results and rejected work as knowledge.

## Findings

| ID | Severity | Finding | Why it matters | Recommendation |
|---|---|---|---|---|
| QM-001 | High | "Every significant piece of work" is not defined. | Creates ambiguity and bureaucracy risk. | Define significance levels and which gates apply to each. |
| QM-002 | High | Missing Data Quality Gate. | Research validity depends on data lineage, missing values, proxies, adjustments, and transformations. | Add a mandatory/conditional data-quality gate. |
| QM-003 | High | Missing Security/Scope Gate before release. | No-execution boundary and credential controls need an explicit gate, not just a principle. | Add security and no-execution boundary checks. |
| QM-004 | High | Research controls are incomplete. | In-sample/out-of-sample alone is insufficient; overfitting, data snooping, benchmark, regime and parameter stability controls need enforcement. | Add pre-registration, bias controls, robustness controls, and result classification. |
| QM-005 | High | Release readiness lacks a release manifest. | Version, artefacts, known issues and rollback path need a single auditable package. | Add release manifest requirement. |
| QM-006 | Medium | Engineering controls lack concrete verification artefacts. | "Clean compile" and "no repainting" need evidence records. | Add compile evidence, static/manual checks, regression evidence, and non-repainting review. |
| QM-007 | Medium | Waivers/exceptions are missing. | Real projects sometimes release with known limitations; uncontrolled exceptions are risky. | Add waiver record with owner, expiry, severity and risk acceptance. |
| QM-008 | Medium | Decision records are mentioned but not required by trigger. | EDR/RDR use will be inconsistent. | Define when EDR/RDR is mandatory. |
| QM-009 | Medium | Quality classifications do not specify promotion criteria. | States are useful but insufficient if transition rules are undefined. | Add entry/exit criteria by classification. |
| QM-010 | Medium | Post-release failure handling lacks response owners and severity response expectations. | Defect handling may be slow or inconsistent. | Add severity response expectations and escalation. |
| QM-011 | Medium | Acceptance criteria include "demonstrably improves validated performance" without evidence threshold. | Can invite overfitting. | Require performance claims to satisfy research controls and limitations. |
| QM-012 | Low | Some wording is aspirational rather than enforceable. | Good principles may not translate into decisions. | Convert principles into checkable requirements where possible. |

## Conflicts with ATOS v1.1

No direct hard conflict found.

Potential alignment issues:

- ATOS v1.1 says governance changes require approval by the Product Owner plus affected accountable owner. The Quality Manual should repeat that final approval remains with Paul Austin or the relevant accountable human role.
- ATOS v1.1 requires data governance and risk ownership. The Quality Manual should include explicit data and risk gates.
- ATOS v1.1 requires knowledge capture. The Quality Manual mentions knowledge base updates but should require negative findings and failures to be captured when material.
- Active `Architecture.md` requires engine output contracts and one-way/non-mutating downstream use. The Quality Manual aligns with this but should reference contract compliance as a release blocker for engine work.

## Bureaucracy Risk

The current draft risks over-applying all gates to minor edits because it says every significant piece of work must pass all gates but does not define significance.

Recommended control:

- Minor documentation/cosmetic changes: documentation + review only.
- Small bug fixes: mission, engineering, regression, documentation, review.
- Engine changes: all engineering, contract, regression, research where applicable, release controls.
- Research claims: mission, data, research validation, reproducibility, knowledge capture, review.
- Releases and architecture changes: all applicable gates plus decision record and Product Owner approval.

## Enforceability Review

Too vague to enforce without amendment:

- "Where applicable, Hermes must validate..." — define applicable.
- "Sensitivity analysis where appropriate" — define triggers.
- "Transaction costs where relevant" — define relevance for strategy/performance claims.
- "Code compiles" — define evidence, e.g. TradingView compile/manual screenshot or recorded compile note.
- "Review should confirm" — for blockers use "must confirm".
- "Known issues are listed" — require severity and owner.

## Recommendation

Revise the Quality Manual before approval.

The revised draft should:

1. Define applicability and significance.
2. Add Data Quality, Security/Scope, Regression, Decision Record, Waiver, Release Manifest, and Knowledge Capture controls.
3. Make research validation controls stricter and more explicit.
4. Add promotion criteria for quality classifications.
5. Preserve lean operation by making gates conditional rather than universal.
6. Keep status as Draft for Paul Austin Review.
