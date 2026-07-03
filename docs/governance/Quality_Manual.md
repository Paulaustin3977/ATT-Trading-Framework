# Austin Trading Quality Manual

Version: 1.1  
Status: Approved ATOS v1.1 Governance Baseline  
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

This document is the approved Quality Manual v1.1 for the ATOS v1.1 governance baseline.

Paul Austin approved this Quality Manual as part of the ATOS v1.1 governance baseline on 2026-07-03.

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

# 4. Work Significance Levels

ATOS quality control is risk-based. Do not apply every gate to every change.

## 4.1 Minor documentation/cosmetic change

Examples:

- Typo fixes
- Formatting
- Link correction
- Clarifying wording that does not change governance, architecture, research, release, or engine meaning

Risk profile: low.

## 4.2 Small bug fix

Examples:

- Localised code correction
- Small documentation correction with behavioural implications
- Minor defect fix that does not change engine contract, architecture, or research conclusion

Risk profile: low to medium.

## 4.3 Engine change

Examples:

- Engine logic change
- Engine input/default/range change
- Engine output change
- Engine Output Contract change
- Dashboard display logic that consumes engine outputs

Risk profile: medium to high.

## 4.4 Research claim

Examples:

- Claim about market behaviour
- Claim about validated performance
- Claim that one method is better than another
- Claim that evidence supports promotion, rejection, or deprecation

Risk profile: medium to critical depending on claim.

## 4.5 Architecture change

Examples:

- Engine flow change
- Contract/interface change
- New engine, removed engine, or changed responsibility boundary
- Change to one-way data flow, bar-close logic, or DashboardEngine presentation-only rule

Risk profile: high.

## 4.6 Release candidate

Examples:

- Candidate stable release
- Versioned Pine release
- Published research package
- Governance pack proposed for active baseline

Risk profile: high to critical.

If classification is unclear, classify by the highest plausible risk.

---

# 5. Mandatory and Optional Gates by Significance Level

| Gate | Minor documentation/cosmetic | Small bug fix | Engine change | Research claim | Architecture change | Release candidate |
|---|---|---|---|---|---|---|
| Mission Clarity | Optional | Mandatory | Mandatory | Mandatory | Mandatory | Mandatory |
| Specification | Optional | Optional | Mandatory | Optional | Mandatory | Mandatory |
| Engineering Quality | Optional | Mandatory | Mandatory | Optional | Optional | Mandatory where code changes |
| Engine Contract Compliance | Optional | Optional unless engine output affected | Mandatory | Optional | Mandatory if interface affected | Mandatory for engine releases |
| Data Quality | Optional | Optional | Optional unless validation uses data | Mandatory | Optional | Mandatory where evidence uses data |
| Research Validation | Optional | Optional | Mandatory where claim/behaviour needs evidence | Mandatory | Optional unless evidence claim made | Mandatory where release contains research or behaviour claims |
| Reproducibility | Optional | Optional | Mandatory for validation artefacts | Mandatory | Mandatory for decision evidence | Mandatory |
| Regression Evidence | Optional | Mandatory | Mandatory | Optional unless behaviour affected | Mandatory where behaviour/contract affected | Mandatory |
| Documentation | Mandatory | Mandatory | Mandatory | Mandatory | Mandatory | Mandatory |
| Decision Record | Optional | Optional | Mandatory if contract/architecture/risk changes | Mandatory for accepted/rejected research conclusions | Mandatory | Mandatory for material release decisions |
| Security and Scope | Optional | Optional | Mandatory if tooling/integration/scope affected | Mandatory for performance/trading-related claims | Mandatory | Mandatory |
| Waiver / Exception | Optional | Mandatory if any required gate is skipped | Mandatory if any required gate is skipped | Mandatory if any required gate is skipped | Mandatory if any required gate is skipped | Mandatory if any required gate is skipped |
| Release Manifest | Not applicable | Not applicable | Optional unless release candidate | Not applicable unless published package | Not applicable unless release candidate | Mandatory |
| Knowledge Capture | Optional | Optional unless material lesson | Mandatory for material outcomes | Mandatory | Mandatory | Mandatory |
| Review | Mandatory | Mandatory | Mandatory | Mandatory | Mandatory | Mandatory |
| Product Owner Approval | Optional | Optional | Mandatory only for scope/risk impact or Stable promotion | Optional unless release/scope affected | Mandatory for major architecture, risk, or scope changes before Release Candidate status | Mandatory for promotion to Stable, not for preparing Release Candidate |

Mandatory means the gate must be completed or formally waived. Optional means use judgement; if the optional gate reveals material risk, it becomes mandatory for that change.

---

# 6. Quality Gates

## Gate 1 — Mission Clarity

Before work begins, the task must clearly define:

- Objective
- Scope
- Deliverables
- Success criteria
- Assumptions
- Known risks
- Applicable documents
- Work significance level
- Mandatory gates
- Optional gates intentionally skipped

If the mission is unclear, work may continue only as discovery, not implementation or release.

---

## Gate 2 — Specification

Before implementation, significant work must have a written specification or equivalent change note.

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
- Engineering Decision Record where material
- Major version bump where appropriate
- Migration note
- Architecture impact review
- Regression evidence

---

## Gate 5 — Data Quality Gate

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

## Gate 6 — Research Validation Gate

Research claims and performance claims require a documented research validation process.

A performance claim may be classified as `supported` only when it includes all applicable evidence-threshold controls listed below. Anything below that threshold must be classified as `weakly supported`, `inconclusive`, `falsified`, or `operationally rejected`.

Validation must include:

- Hypothesis
- Pre-registered scope
- Data source
- Date range
- Instruments tested
- Methodology
- Results
- Limitations
- Recommendation
- Result classification: supported, weakly supported, inconclusive, falsified, or rejected

Performance claims require controls for:

- Clear hypothesis
- Documented data source
- In-sample and out-of-sample testing where applicable
- Walk-forward or time-split validation where applicable
- Parameter sensitivity check
- Transaction costs where trading performance is claimed
- Benchmark comparison
- Stated limitations
- Reproducibility notes
- No obvious lookahead issue
- No obvious survivorship-bias issue
- No obvious data-snooping issue
- Overfitting review
- Regime-dependence review

Additional validation should include, where feasible:

- In-sample and out-of-sample separation
- Walk-forward testing
- Parameter sensitivity analysis
- Null or benchmark comparison
- Negative result capture

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

## Gate 8 — Regression Evidence Gate

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

## Gate 10 — Decision Record Gate

Decision records prevent repeat debate and undocumented architecture/research drift.

### EDR mandatory triggers

An Engineering Decision Record is mandatory when a change materially affects:

- Engine architecture
- Engine flow
- Engine Output Contract
- Data flow or one-way dependency rule
- DashboardEngine presentation-only rule
- Release process
- Tooling or automation that changes validation/release behaviour
- Breaking interface or migration decision

### RDR mandatory triggers

A Research Decision Record is mandatory when a change materially affects:

- Accepted research conclusion
- Rejected research conclusion with reusable knowledge
- Performance claim
- Research methodology
- Data assumption
- Evidence threshold
- Validation result used for promotion, rejection, or deprecation

A decision record must state context, decision, alternatives, consequences, risks, and evidence.

---

## Gate 11 — Security and Scope Gate

Every release, tool integration, performance claim, architecture change, and governance change must confirm the no-execution boundary.

The Austin Trading Platform is currently a research, analysis, indicator, strategy, dashboard, and decision-support framework.

The following remain out of scope:

- Live trade execution
- Broker connectivity
- Paper-trading APIs
- Autonomous order placement
- Handling broker credentials
- Managing real positions

Security and scope checks must confirm:

- No secrets or credentials are committed
- No broker or execution credentials are introduced
- No paper-trading API integration is introduced
- External services are documented where material
- Access or credential risks are escalated to the Security Owner
- The change does not create hidden execution capability

Any proposal touching execution, broker connectivity, order placement, or paper-trading APIs requires formal ATOS amendment before work begins.

---

## Gate 12 — Waiver / Exception Gate

A waiver is required when a mandatory quality requirement is knowingly not met.

A waiver must record:

- Owner
- Requirement waived
- Reason
- Severity
- Expiry date or review date
- Risk accepted
- Mitigation
- Approval authority

Approval authority:

- Low waiver: accountable functional owner
- Medium waiver: accountable functional owner plus Product Owner notification
- High waiver: Product Owner and Risk Owner approval
- Low waiver: 90 days maximum
- Medium waiver: 30 days default
- High waiver: 14 days maximum and requires Product Owner and Risk Owner approval
- Critical waiver: not allowed unless explicitly approved by Product Owner and Risk Owner; never allowed for hidden execution capability or knowingly released lookahead/repainting logic

Default waiver expiry is 30 days. No waiver is permanent.

---

## Gate 13 — Release Manifest Gate

A release candidate requires a release manifest before promotion.

Release manifests live in `docs/releases/` and link to the actual release artefacts in `pine/releases/`.

Required structure:

- Manifest: `docs/releases/ATE_vX.X_Release_Manifest.md`
- Release artefact: `pine/releases/ATE_vX.X.pine`

The release manifest must include:

- Version
- Release file path, for example `pine/releases/ATE_vX.X.pine`
- Manifest path, for example `docs/releases/ATE_vX.X_Release_Manifest.md`
- Commit hash
- Changed files
- Validation artefacts
- Known issues
- Rollback path
- Approval status

Recommended additional fields:

- Release date
- Approver
- Waivers, if any
- Affected specifications
- Regression evidence
- Changelog reference

No unstable, experimental, or partially validated feature should enter a stable release.

Previous stable versions must remain preserved.

---

## Gate 14 — Knowledge Capture Gate

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

## Gate 15 — Review

Every significant release, research claim, architectural change, or governance change must be reviewed.

Review must confirm:

- Applicable gates were correctly selected
- Mandatory gates are complete or waived
- The specification was followed
- Code compiles where applicable
- Logic is explainable
- Research evidence is adequate for the claim
- Risks are identified
- Required documentation is updated
- No governance boundary is violated
- Required decision records exist
- Required waivers are documented

Hermes may recommend approval, modification, rejection, or a block. Hermes may mark a release as `Research Blocked` or `Quality Blocked` when evidence, quality, scope, or research standards are not met.

Hermes cannot approve or reject final governance alone. Final release approval or override remains with Paul Austin as Product Owner.

If Paul Austin overrides a Hermes block, the override must be documented as a waiver with reason, risk accepted, expiry/review date, and mitigation.

---

# 7. Quality Classification and Promotion Criteria

Work may be classified as follows.

## Experimental

Definition: idea or prototype only. Not for release.

Promotion to Laboratory requires:

- Hypothesis or purpose documented
- Known risks noted
- Reason for testing identified

## Laboratory

Definition: being tested in Austin Research Lab. May be unstable.

Promotion to Validation Candidate requires:

- Preliminary evidence recorded
- Known limitations recorded
- Data source noted where relevant
- No no-execution boundary breach

## Validation Candidate

Definition: ready for Hermes testing. Not yet stable.

Promotion to Release Candidate requires:

- Applicable research validation complete
- Regression evidence complete where behaviour changed
- Documentation updated
- Result classified as supported or weakly supported, or explicitly accepted for non-performance reasons

## Release Candidate

Definition: passed initial checks and awaiting final review. A Release Candidate may be prepared by the normal engineering/research workflow without Product Owner approval unless it contains a major architecture, risk, or scope change.

Major architecture, risk, or scope changes require Product Owner approval before Release Candidate status.

Promotion to Stable requires:

- Release manifest complete
- Mandatory gates complete or formally waived
- Known issues listed
- Rollback path defined
- Explicit Product Owner approval obtained

## Stable

Definition: approved, documented, versioned, and released.

Stable work remains stable until:

- Superseded by a later version
- Deprecated
- Rejected due to defect or invalidated evidence

## Deprecated

Definition: still available but scheduled for replacement or removal.

Deprecation requires:

- Reason documented
- Replacement or migration path documented
- Removal target or review date recorded
- User/research impact noted

## Rejected

Definition: tested and not accepted.

Rejected work must record:

- Rejection reason
- Evidence or observation supporting rejection
- Whether knowledge should be retained
- Whether future retest conditions exist

Rejected work must remain documented if it produced useful knowledge.

---

# 8. Acceptance Criteria

A feature may be accepted only if it satisfies at least one of the following and passes all mandatory quality gates for its significance level:

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

# 9. Rejection Criteria

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

# 10. Hermes Quality Responsibilities

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
- Marking releases as `Research Blocked` or `Quality Blocked` when standards are not met

Hermes must not:

- Hide poor results
- Approve its own recommendations as final governance
- Execute trades
- Connect to brokers
- Use paper-trading APIs
- Treat backtests as proof of future performance

---

# 11. Post-Release Incident Handling

If a defect is discovered after release, create an incident note.

The incident note must include:

- Severity
- Owner
- Response expectation
- Rollback rule
- Prevention update
- Affected version or file
- Cause, if known
- Changelog and knowledge-base update requirement

## Severity response expectations

| Severity | Meaning | Response expectation | Rollback rule | Prevention update |
|---|---|---|---|---|
| Critical | Invalidates research, creates lookahead/repainting, violates scope, introduces execution/broker/paper-trading risk, or compromises credentials/security | Stop promotion or release immediately; escalate to Product Owner and Risk Owner | Roll back unless Product Owner and Risk Owner explicitly decide otherwise | Mandatory |
| High | Major logic error, incorrect dashboard output, broken alerts, unreliable release, or materially incomplete validation | Block release until resolved or formally waived | Roll back if released output is materially misleading | Mandatory |
| Medium | Incorrect documentation, minor scoring inconsistency, missing diagnostics, incomplete report, or unclear limitation | Fix before next release unless accepted as known issue | Roll back only if user-facing reliability is affected | Required where process gap exists |
| Low | Formatting, naming, cosmetic issue, or minor documentation improvement | Fix when practical | No rollback normally required | Optional |

Failures are not hidden.

Failures are converted into process improvements.

---

# 12. Quality Review Checklist

Before release, answer:

- Is the significance level clear?
- Are mandatory and optional gates identified?
- Are all mandatory gates complete or formally waived?
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
- Has the Product Owner explicitly approved promotion to Stable?

If any critical answer is "no", the release is not ready.

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

# 14. Resolved Product Owner / Chief Systems Architect Questions

All prior open questions have been resolved in this draft.

1. Product Owner approval is mandatory for promotion to Stable, not for preparing every Release Candidate. Major architecture, risk, or scope changes require Product Owner approval before Release Candidate status.
2. A performance claim is `supported` only when it meets the evidence threshold in the Research Validation Gate. Anything below that threshold is `weakly supported`, `inconclusive`, `falsified`, or `operationally rejected`.
3. Release manifests live in `docs/releases/` and link to release artefacts in `pine/releases/`, using `docs/releases/ATE_vX.X_Release_Manifest.md` and `pine/releases/ATE_vX.X.pine`.
4. Hermes may mark a release as `Research Blocked` or `Quality Blocked`, but final release approval or override remains with Paul Austin as Product Owner. Overrides require a waiver.
5. Waivers expire by severity: Low 90 days maximum, Medium 30 days default, High 14 days maximum, Critical only by explicit Product Owner and Risk Owner approval. No waiver is permanent.

---

# 15. Recommendation

Recommendation: ready for Paul Austin approval.

Rationale: the Product Owner / Chief Systems Architect answers have been incorporated. The draft is practical for a small AI-assisted engineering team because gates are proportional by significance level rather than applied universally. It now includes resolved release approval rules, supported-performance evidence thresholds, release-manifest location, Hermes block/override authority, waiver expiry rules, and post-release incident handling.

Paul Austin has reviewed and approved this document for the ATOS v1.1 governance baseline.

---

# 16. Final Principle

Quality is not a final inspection step.

Quality is built into every stage of Austin Trading Team work.

If the team cannot explain, reproduce, validate, and document a result, the result is not ready for release.
