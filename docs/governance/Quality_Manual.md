# Austin Trading Quality Manual

Version: 1.0  
Status: Draft for Review  
Owner: Austin Trading Team  
Applies To: Austin Trading Engine, Austin Research Lab, Austin Strategy Framework, Austin Market Intelligence, and all future Austin Trading Platform projects.

---

# 1. Purpose

The Quality Manual defines the minimum quality standards required before any Austin Trading Team work can be accepted, promoted, released, or treated as reliable.

Its purpose is to prevent poor engineering, weak research, unclear documentation, and unsupported assumptions from entering the Austin Trading Platform.

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

---

# 2. Quality Philosophy

The Austin Trading Team follows this principle:

> A feature is not complete when it works.  
> A feature is complete when it works, is documented, is validated, and can be explained.

Every feature must earn its place.

Negative results are valuable.

Rejected ideas are still knowledge.

Backtests are evidence, not proof.

---

# 3. Quality Gates

Every significant piece of work must pass the following gates.

## Gate 1 — Mission Clarity

Before work begins, the task must clearly define:

- Objective
- Scope
- Deliverables
- Success criteria
- Assumptions
- Known risks
- Applicable documents

If the mission is unclear, the work must not proceed.

---

## Gate 2 — Specification

Before implementation, the feature or change must have a written specification.

The specification must define:

- Purpose
- Inputs
- Outputs
- Logic
- Expected behaviour
- Known limitations
- Validation plan
- Acceptance criteria

No major feature should be built directly from an informal idea.

---

## Gate 3 — Engineering Quality

Code must satisfy:

- Pine Script v6 compatibility where applicable
- Clean compile
- No lookahead bias
- No repainting logic unless explicitly documented and approved
- Bar-close-only decision logic unless explicitly approved
- Clear variable names
- Minimal duplication
- Modular structure
- Commented non-obvious logic
- No hidden defaults
- Documented input ranges

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

---

## Gate 5 — Research Validation

Where applicable, Hermes must validate the feature using an appropriate research process.

Validation should include:

- Hypothesis
- Data source
- Date range
- Instruments tested
- In-sample results
- Out-of-sample results
- Walk-forward testing where appropriate
- Sensitivity analysis where appropriate
- Transaction costs where relevant
- Limitations
- Recommendation

A backtest alone is not sufficient unless the research question is explicitly narrow.

---

## Gate 6 — Reproducibility

Every significant result must be reproducible.

Research and validation artefacts should include:

- Code version
- Commit hash where available
- Data source
- Parameters
- Date range
- Instrument list
- Methodology
- Output report location

If reproducibility is limited, the limitation must be stated clearly.

---

## Gate 7 — Documentation

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

A feature is not complete if documentation is missing.

---

## Gate 8 — Review

Every significant release or architectural change must be reviewed.

Review should confirm:

- The specification was followed
- Code compiles
- Logic is explainable
- Research evidence is adequate
- Risks are identified
- Documentation is updated
- No governance boundary is violated

Hermes may recommend approval, modification, or rejection.

Final approval remains with the accountable human role.

---

## Gate 9 — Release Readiness

A release may only be promoted when:

- All required gates are complete
- Changelog is updated
- Version number is correct
- Release file is saved
- Previous stable version remains preserved
- Known issues are listed
- Rollback path is clear

No unstable, experimental, or partially validated feature should enter a stable release.

---

# 4. Quality Classification

Work may be classified as:

## Experimental

Idea or prototype only.

Not for release.

## Laboratory

Being tested in Austin Research Lab.

May be unstable.

## Validation Candidate

Ready for Hermes testing.

Not yet stable.

## Release Candidate

Passed initial checks and awaiting final review.

## Stable

Approved, documented, versioned, and released.

## Deprecated

Still available but scheduled for replacement or removal.

## Rejected

Tested and not accepted.

Rejected work must remain documented if it produced useful knowledge.

---

# 5. Acceptance Criteria

A feature may be accepted only if it satisfies at least one of the following:

- Improves market understanding
- Improves explainability
- Improves research quality
- Improves engineering reliability
- Improves risk control
- Improves reproducibility
- Improves maintainability
- Demonstrably improves validated performance

Features that only add visual complexity or parameter clutter should be rejected.

---

# 6. Rejection Criteria

A feature should be rejected if it:

- Introduces repainting or lookahead bias
- Cannot be explained clearly
- Duplicates existing logic
- Adds complexity without evidence
- Weakens reproducibility
- Produces unstable results
- Performs only on a narrow overfit sample
- Violates the no-execution boundary
- Cannot be maintained safely

---

# 7. No-Execution Boundary

The Austin Trading Platform is currently a research, analysis, indicator, strategy, dashboard, and decision-support framework.

The following remain out of scope:

- Live trade execution
- Broker connectivity
- Paper-trading APIs
- Autonomous order placement
- Handling broker credentials
- Managing real positions

Any proposal touching these areas requires formal ATOS amendment before work begins.

---

# 8. Hermes Quality Responsibilities

Hermes is responsible for:

- Challenging assumptions
- Testing hypotheses
- Identifying weaknesses
- Reporting negative findings
- Producing reproducible research
- Reviewing documentation quality
- Recommending improvement
- Maintaining research integrity

Hermes must not:

- Hide poor results
- Approve its own recommendations as final governance
- Execute trades
- Connect to brokers
- Treat backtests as proof of future performance

---

# 9. Quality Review Checklist

Before release, answer:

- Does it compile?
- Is the purpose clear?
- Is the logic explainable?
- Is there any lookahead or repainting risk?
- Are defaults documented?
- Are outputs contract-compliant?
- Has Hermes validated it where needed?
- Are limitations documented?
- Has the changelog been updated?
- Is the previous stable version preserved?
- Is rollback possible?
- Has the Product Owner approved release?

If any critical answer is “no”, the release is not ready.

---

# 10. Quality Failure Handling

If a defect is discovered after release:

1. Record the defect.
2. Classify severity.
3. Preserve the faulty version for audit.
4. Roll back if necessary.
5. Create a fix branch or replacement version.
6. Document the cause.
7. Add a prevention rule if possible.
8. Update the changelog and knowledge base.

Failures are not hidden.

Failures are converted into process improvements.

---

# 11. Severity Levels

## Critical

Invalidates research, creates lookahead/repainting, violates scope, or risks live execution.

## High

Major logic error, incorrect dashboard output, broken alerts, or unreliable release.

## Medium

Incorrect documentation, minor scoring inconsistency, missing diagnostics, or incomplete report.

## Low

Formatting, naming, cosmetic issue, or minor documentation improvement.

---

# 12. Continuous Improvement

Every completed task should answer:

- What improved in the product?
- What improved in the research process?
- What improved in the engineering process?
- What documentation should change?
- What should be remembered for future work?

Quality improves when lessons become permanent.

---

# 13. Final Principle

Quality is not a final inspection step.

Quality is built into every stage of Austin Trading Team work.

If the team cannot explain, reproduce, validate, and document a result, the result is not ready for release.
