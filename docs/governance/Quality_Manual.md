# Austin Trading Quality Manual

Version: 1.1-draft  
Status: Draft for Paul Austin Review  
Owner: Austin Trading Team  
Applies To: Austin Trading Engine, Austin Research Lab, Austin Strategy Framework, Austin Market Intelligence, and all future Austin Trading Platform projects.

---

# 1. Purpose

The Quality Manual defines the minimum quality standards required before Austin Trading Team work can be accepted, promoted, released, or treated as reliable.

Its purpose is to prevent poor engineering, weak research, unclear documentation, unsupported assumptions, hidden risk, and uncontrolled scope expansion from entering the Austin Trading Platform.

Quality is not defined by whether something looks good or produces attractive historical results.

Quality is defined by:

- Clarity
- Reproducibility
- Evidence
- Explainability
- Maintainability
- Risk control
- Documentation
- Review
- Governance compliance

---

# 2. Status and Approval

This document is a revised draft for ATOS v1.1 review.

It must not be treated as approved governance until Paul Austin reviews it and explicitly promotes it to approved status.

---

# 3. Quality Philosophy

The Austin Trading Team follows this principle:

> A feature is not complete when it works.  
> A feature is complete when it works, is documented, is validated, and can be explained.

Every feature must earn its place.

Negative results are valuable.

Rejected ideas are still knowledge.

Backtests are evidence, not proof.

Quality should be proportional. The team should avoid unnecessary bureaucracy for minor work, but must not weaken controls for research claims, engine behaviour changes, architecture changes, or releases.

---

# 4. Applicability and Change Types

Quality gates are risk-based and proportional. Not every change requires every gate.

| Change type | Minimum required gates |
|---|---|
| Editorial documentation change | Documentation Gate, Review Gate |
| Minor documentation correction | Documentation Gate, Review Gate |
| Minor bug fix | Mission Clarity, Engineering Quality, Regression and Compatibility, Documentation, Review |
| Engine behaviour change | Mission Clarity, Specification, Engineering Quality, Engine Contract Compliance, Regression and Compatibility, Documentation, Review |
| Research claim | Mission Clarity, Data Quality, Research Validation, Reproducibility, Knowledge Capture, Review |
| Performance claim | Mission Clarity, Data Quality, Research Validation, Reproducibility, Security and No-Execution Boundary, Knowledge Capture, Review |
| Architecture change | Mission Clarity, Specification, Decision Record, Documentation, Review |
| Governance change | Mission Clarity, Decision Record, Documentation, Review, Product Owner approval |
| Release candidate | All applicable gates, Release Manifest, Product Owner approval |

If a change type is unclear, classify it by highest plausible risk.

---

# 5. Quality Gates

Every significant piece of work must pass the gates applicable to its change type.

## Gate 1 — Mission Clarity

Before work begins, the task must clearly define:

- Objective
- Scope
- Deliverables
- Success criteria
- Assumptions
- Known risks
- Applicable documents
- Change type
- Required gates

If the mission is unclear, the work must not proceed beyond discovery.

---

## Gate 2 — Specification

Before implementation, a significant feature or change must have a written specification.

The specification must define:

- Purpose
- Inputs
- Outputs
- Logic
- Expected behaviour
- Known limitations
- Validation plan
- Acceptance criteria
- Version impact
- Migration impact, if applicable

No major feature should be built directly from an informal idea.

---

## Gate 3 — Engineering Quality

Code must satisfy:

- Pine Script v6 compatibility where applicable
- Clean compile or documented compile limitation
- No lookahead bias
- No repainting logic unless explicitly documented and approved
- Bar-close-only decision logic unless explicitly approved
- Clear variable names
- Minimal duplication
- Modular structure
- Commented non-obvious logic
- No hidden defaults
- Documented input ranges
- No mutation of upstream engine outputs
- DashboardEngine presentation-only rule preserved

Engineering evidence should include compile notes, manual verification notes, regression evidence, or other appropriate artefacts.

---

## Gate 4 — Engine Contract Compliance

Every engine must publish outputs according to the Engine Output Contract:

- `score`
- `state`
- `direction`
- `reason`
- `diagnostics`
- `version`

If an engine does not use one of these fields, the omission must be explicit and documented.

Downstream engines may consume upstream values but must not mutate them.

Breaking changes to the contract require:

- Specification update
- Major version bump where appropriate
- Migration note
- Architecture impact review
- Regression evidence

---

## Gate 5 — Data Quality

Research, validation, and performance claims must document data quality.

Data evidence should include:

- Source
- Instrument or symbol list
- Timeframe
- Date range
- Adjusted/unadjusted status where relevant
- Missing-data handling
- Transformations
- Proxy instruments used, if any
- Known limitations
- Data owner or steward where material

A result based on undocumented data must not be treated as reliable.

---

## Gate 6 — Research Validation

Where applicable, Hermes must validate the feature or claim using an appropriate research process.

Validation should include:

- Hypothesis
- Pre-registered scope
- Data source
- Date range
- Instruments tested
- In-sample results where applicable
- Out-of-sample results where applicable
- Walk-forward testing for strategy/performance claims where feasible
- Sensitivity analysis for tunable logic where feasible
- Benchmark or null comparison where relevant
- Transaction costs for strategy/performance claims where relevant
- Bias checks: lookahead, repainting, data snooping, survivorship, regime dependence, proxy mismatch
- Limitations
- Recommendation
- Result classification: supported, weakly supported, inconclusive, falsified, or rejected

A backtest alone is not sufficient unless the research question is explicitly narrow and the limitation is stated.

---

## Gate 7 — Reproducibility

Every significant result must be reproducible or must clearly state why reproducibility is limited.

Research and validation artefacts should include:

- Code version
- Commit hash where available
- Data source
- Parameters
- Date range
- Instrument list
- Methodology
- Output report location
- Tool/version notes where relevant

If reproducibility is limited, the limitation must be stated clearly in the report and review notes.

---

## Gate 8 — Regression and Compatibility

Behaviour-changing work must include regression and compatibility evidence.

Regression evidence should confirm:

- Existing intended behaviour remains intact or changed intentionally
- No new lookahead or repainting risk is introduced
- Engine Output Contract remains compatible or migration is documented
- Released files are not edited in place
- Dashboard output remains presentation-only
- Known issues are recorded with severity

If automated regression is unavailable, manual verification evidence must be recorded.

---

## Gate 9 — Documentation

Every accepted feature must update the relevant documentation.

This may include:

- Architecture
- Engine specification
- Research methodology
- Changelog
- Release notes
- Knowledge base
- Engineering Decision Record
- Research Decision Record
- Risk register
- Deprecation note

A feature is not complete if required documentation is missing.

---

## Gate 10 — Decision Records

A decision record is required when a change materially affects architecture, research methodology, release policy, data assumptions, risk posture, or governance.

Use:

- Engineering Decision Record for architecture, engine contracts, tooling, release, or implementation decisions.
- Research Decision Record for hypotheses, methodology, evidence interpretation, or research acceptance/rejection decisions.

A decision record must state context, decision, alternatives, consequences, risks, and evidence.

---

## Gate 11 — Security and No-Execution Boundary

Every release, tool integration, and governance change must confirm the no-execution boundary.

The Austin Trading Platform is currently a research, analysis, indicator, strategy, dashboard, and decision-support framework.

The following remain out of scope:

- Live trade execution
- Broker connectivity
- Paper-trading APIs
- Autonomous order placement
- Handling broker credentials
- Managing real positions

Security checks must confirm:

- No secrets or credentials are committed
- No broker or execution credentials are introduced
- No paper-trading API integration is introduced
- External services are documented where material
- Access or credential risks are escalated to the Security Owner

Any proposal touching execution, broker connectivity, order placement, or paper-trading APIs requires formal ATOS amendment before work begins.

---

## Gate 12 — Review

Every significant release, research claim, architectural change, or governance change must be reviewed.

Review must confirm:

- The specification was followed
- Code compiles where applicable
- Logic is explainable
- Research evidence is adequate for the claim
- Risks are identified
- Required documentation is updated
- No governance boundary is violated
- Required decision records exist
- Required waivers are documented

Hermes may recommend approval, modification, or rejection.

Final approval remains with the accountable human role.

---

## Gate 13 — Release Manifest and Release Readiness

A release may only be promoted when all applicable gates are complete.

A release manifest must record:

- Release version
- Commit hash
- Files released
- Affected specifications
- Research artefacts
- Regression evidence
- Known issues and severity
- Waivers, if any
- Rollback path
- Approver
- Release date

No unstable, experimental, or partially validated feature should enter a stable release.

Previous stable versions must remain preserved.

---

## Gate 14 — Waivers and Exceptions

A waiver is required when a quality requirement is knowingly not met.

A waiver must include:

- Requirement waived
- Reason
- Risk severity
- Mitigation
- Owner
- Expiry or review date
- Approval by the Product Owner and/or Risk Owner where material

Critical risks must not be waived if they violate the no-execution boundary or knowingly introduce lookahead/repainting into released logic.

---

## Gate 15 — Knowledge Capture

Material outcomes must be captured as knowledge.

Knowledge capture is required for:

- Accepted research findings
- Negative or rejected research findings
- Major engineering decisions
- Release failures
- Repeated defects
- Governance changes
- Lessons that prevent future rework

Knowledge entries must separate evidence, interpretation, and recommendation.

---

# 6. Quality Classification

Work may be classified as:

## Experimental

Idea or prototype only. Not for release.

Exit criteria: hypothesis or reason to abandon is documented.

## Laboratory

Being tested in Austin Research Lab. May be unstable.

Exit criteria: preliminary evidence and limitations are recorded.

## Validation Candidate

Ready for Hermes testing. Not yet stable.

Exit criteria: validation report or explicit rejection is produced.

## Release Candidate

Passed initial checks and awaiting final review.

Exit criteria: release manifest complete and Product Owner approval obtained.

## Stable

Approved, documented, versioned, and released.

Exit criteria: remains stable until superseded, deprecated, or defected.

## Deprecated

Still available but scheduled for replacement or removal.

Exit criteria: migration path and removal target are documented.

## Rejected

Tested and not accepted.

Exit criteria: rejection reason and reusable knowledge are documented.

Rejected work must remain documented if it produced useful knowledge.

---

# 7. Acceptance Criteria

A feature may be accepted only if it satisfies at least one of the following and passes all applicable quality gates:

- Improves market understanding
- Improves explainability
- Improves research quality
- Improves engineering reliability
- Improves risk control
- Improves reproducibility
- Improves maintainability
- Demonstrably improves validated performance

Performance improvement claims require research validation and must state limitations.

Features that only add visual complexity, parameter clutter, or unvalidated optionality should be rejected.

---

# 8. Rejection Criteria

A feature should be rejected if it:

- Introduces repainting or lookahead bias
- Cannot be explained clearly
- Duplicates existing logic without benefit
- Adds complexity without evidence
- Weakens reproducibility
- Produces unstable results
- Performs only on a narrow overfit sample
- Violates the no-execution boundary
- Cannot be maintained safely
- Mutates upstream engine values without explicit architecture approval
- Requires undocumented data or hidden assumptions

---

# 9. Hermes Quality Responsibilities

Hermes is responsible for:

- Challenging assumptions
- Testing hypotheses
- Identifying weaknesses
- Reporting negative findings
- Producing reproducible research
- Reviewing documentation quality
- Recommending improvement
- Maintaining research integrity
- Escalating no-execution boundary risks

Hermes must not:

- Hide poor results
- Approve its own recommendations as final governance
- Execute trades
- Connect to brokers
- Use paper-trading APIs
- Treat backtests as proof of future performance

---

# 10. Quality Review Checklist

Before release, answer:

- Is the change type clear?
- Are the applicable gates identified?
- Does it compile where applicable?
- Is the purpose clear?
- Is the logic explainable?
- Is there any lookahead or repainting risk?
- Are defaults documented?
- Are outputs contract-compliant?
- Are upstream values preserved and not mutated downstream?
- Has Hermes validated it where needed?
- Are data sources and limitations documented?
- Are research limitations documented?
- Has regression or manual verification evidence been recorded?
- Has the changelog been updated?
- Is the previous stable version preserved?
- Is rollback possible?
- Are waivers documented and approved?
- Has the Product Owner approved release?

If any critical answer is "no", the release is not ready.

---

# 11. Quality Failure Handling

If a defect is discovered after release:

1. Record the defect.
2. Classify severity.
3. Preserve the faulty version for audit.
4. Roll back if necessary.
5. Create a fix branch or replacement version.
6. Document the cause.
7. Add a prevention rule if possible.
8. Update the changelog and knowledge base.
9. Review whether a quality gate failed or was missing.

Failures are not hidden.

Failures are converted into process improvements.

---

# 12. Severity Levels

## Critical

Invalidates research, creates lookahead/repainting, violates scope, introduces execution/broker/paper-trading risk, or compromises credentials/security.

Expected response: stop promotion or release immediately; escalate to Product Owner and Risk Owner.

## High

Major logic error, incorrect dashboard output, broken alerts, unreliable release, or materially incomplete validation.

Expected response: block release until resolved or formally waived.

## Medium

Incorrect documentation, minor scoring inconsistency, missing diagnostics, incomplete report, or unclear limitation.

Expected response: fix before release unless explicitly accepted as known issue.

## Low

Formatting, naming, cosmetic issue, or minor documentation improvement.

Expected response: fix when practical; does not normally block release.

---

# 13. Continuous Improvement

Every completed significant task should answer:

- What improved in the product?
- What improved in the research process?
- What improved in the engineering process?
- What documentation should change?
- What should be remembered for future work?
- Did any quality gate need clarification?

Quality improves when lessons become permanent.

---

# 14. Final Principle

Quality is not a final inspection step.

Quality is built into every stage of Austin Trading Team work.

If the team cannot explain, reproduce, validate, and document a result, the result is not ready for release.
