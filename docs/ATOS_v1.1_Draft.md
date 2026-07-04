# ATOS v1.1 Draft

Status: Draft amendments for review, not approved governance
Date: 2026-07-03
Source: ATOS-001 Operational Readiness Review

## Amendment Notice

This document is a rewritten ATOS v1.1 draft. It incorporates recommended changes from the operational readiness review but is not authoritative until reviewed and approved by Paul Austin.

Paul Austin has approved ATOS v1.1 in principle, subject to the role-ownership amendments in this draft. This is not final approval and does not promote ATOS v1.1 to approved governance.

Draft amendments are marked with `[DRAFT v1.1]`.

## 1. Mission

The Austin Trading Operating System governs the Austin Trading Engine: a modular, explainable, evidence-based market analysis framework for TradingView indicators, strategies, Hermes research validation, AI-assisted analysis and future trading dashboards.

[DRAFT v1.1] ATOS exists to keep the project research-grade, auditable, reproducible and resistant to scope creep over a 5-10 year development horizon.

## 2. Scope

### In scope

- Pine Script v6 indicators and strategies.
- Daily-timeframe analysis as the primary horizon.
- Multi-asset research coverage: Gold, Silver, Gilts and Forex.
- Hermes-driven backtesting, validation, audit and critique.
- Specification-driven engine design.
- Human decision support.
- Research reports, validation artefacts and permanent knowledge capture.

### Out of scope

- Live trade execution.
- Broker connectivity.
- Paper-trading APIs.
- Autonomous execution.
- High-frequency or sub-second strategies.
- Repainting logic or future-data references.
- Claims of guaranteed return or predictive certainty.

[DRAFT v1.1] Any proposal that touches execution, broker integration, order routing, live-position management or paper-trading APIs is automatically out of scope unless ATOS is formally amended by the Product Owner and Risk Owner.

## 3. Operating Principles

1. Explainability: every output can be traced to inputs, rules and versioned code.
2. Evidence: claims require data, method and recorded results.
3. Modularity: engines remain independently understandable and testable.
4. Non-repainting: future data and lookahead are forbidden.
5. Reproducibility: releases and research runs must be reproducible from commit hashes and documented inputs.
6. Negative results count: rejected hypotheses are captured as knowledge.
7. Human authority: Hermes and other agents recommend; they do not independently approve governance, releases or trading decisions.
8. Scope discipline: no live trading, broker connectivity or paper-trading APIs.
9. Continuous improvement: ATOS is audited and improved through controlled amendments.

## 4. Governance Model

[DRAFT v1.1]

During early-stage development, ATOS roles may be assigned as functional responsibilities rather than separate agents or separate people. A single person or agent may hold more than one functional responsibility, provided conflicts of interest are made visible and material decisions remain reviewable.

Current draft role ownership:

| Role | Current owner | Accountability | Approval authority |
|---|---|---|---|
| Product Owner | Paul Austin | Mission, scope, priorities and business constraints | Roadmap, scope changes and ATOS approval. |
| Chief Systems Architect | ChatGPT | Architecture, engine boundaries, interfaces and technical coherence | Architecture and interface recommendations for Paul review. |
| Quantitative Research Department | Hermes | Research methodology, evidence quality, scientific integrity, validation, audit and critique | Research recommendations and evidence sufficiency assessments; no sole final approval. |
| Engineering Lead | ChatGPT, with Hermes audit support where required | Coding standards, implementation quality and regression discipline | Code readiness recommendations and technical review completion. |
| Release Manager | Paul Austin + ChatGPT | Release checklist, versioning, changelog and tag discipline | Release execution subject to Paul approval. |
| Data Steward | Hermes initially | Data lineage, data quality and retention | Data-source assessment and recommendations; escalates material risk to Paul. |
| Risk Owner | Paul Austin | Project risk register, mitigations and waivers | Risk acceptance and waiver approval. |
| Security Owner | Paul Austin | Access, credentials, tooling and repository security | Security policy and exceptions. |
| Documentation Owner | ChatGPT, with Hermes audit support | ATOS coherence, cross-references and review cadence | Documentation updates subject to Paul review where governance meaning changes. |

Ownership notes:

- These assignments are early-stage functional responsibilities, not a requirement to create separate permanent agents.
- Hermes remains the Quantitative Research Department and audit support function.
- ChatGPT may hold architecture, engineering and documentation responsibilities, but Hermes should audit material governance/research claims where practical.
- Paul Austin remains the final human authority for scope, risk, security and approval of ATOS v1.1.
- ATOS v1.1 remains draft until Paul reviews the amended draft and explicitly approves promotion.

## 5. Decision Rights and Change Control

[DRAFT v1.1]

- Governance changes require an ATOS change proposal and approval by the Product Owner plus the affected accountable owner.
- Architecture changes require an Engineering Decision Record.
- Research-methodology changes require a Research Decision Record.
- Release waivers require written risk acceptance from the Risk Owner and Release Manager.
- Hermes may recommend changes and raise concerns, but Hermes must not independently approve governance changes.
- Every approved governance change must update `CHANGELOG.md` or a dedicated ATOS changelog.

## 6. Engineering Operating Standard

[DRAFT v1.1]

Engineering work must pass the following gates before release promotion:

1. Specification updated.
2. Architecture impact assessed.
3. Pine Script v6 coding standards met.
4. No repainting or lookahead violations identified.
5. Regression case added or updated.
6. Hermes validation artefact created where applicable.
7. Documentation updated.
8. Changelog entry drafted.
9. Review completed by a role other than the primary author where possible.
10. Release checklist completed.

## 7. Research Operating Standard

[DRAFT v1.1]

Every research claim must include:

- Written hypothesis.
- Pre-registered scope: instruments, timeframe, date range and parameters.
- Data source and lineage.
- Method and evaluation criteria.
- Results, including negative or inconclusive findings.
- Limitations and known biases.
- Reproducibility notes: commit hash, script/version, parameters and artefact paths.
- Classification: supported, weakly supported, inconclusive, falsified or operationally rejected.

## 8. Evidence Standard

[DRAFT v1.1]

A claim is not considered supported unless evidence includes:

- Backtest or validation artefact in the approved folder structure.
- Evaluation summary in `research/Reports/`.
- Regression or validation entry where behaviour changes.
- Statement of limitations.
- Review against overfitting, lookahead, data snooping and regime-dependence risks.

## 9. Knowledge Management

[DRAFT v1.1]

The Austin Trading Knowledge Base records:

- Accepted principles.
- Rejected hypotheses and negative results.
- Engineering decisions.
- Research decisions.
- Known risks and mitigations.
- Release lessons.
- Open questions.

Knowledge entries must separate evidence, interpretation and recommendation.

## 10. Risk Management

[DRAFT v1.1]

The project maintains a risk register covering:

- Trading-scope risk.
- Research-validity risk.
- Engineering-quality risk.
- Data-quality risk.
- Security risk.
- Operational-continuity risk.
- Documentation-drift risk.
- AI-agent overreach risk.

Risks are classified as Critical, High, Medium or Low and assigned an owner, mitigation and review date.

## 11. Security and Data Governance

[DRAFT v1.1]

- No secrets in repository files.
- No broker credentials or execution API credentials are permitted in this project scope.
- Data sources must be documented with source, date range, transformations and known limitations.
- Research artefacts must be reproducible from documented inputs.
- Access to repository and AI tooling should be limited to authorised Austin Trading Team operators.

## 12. Hermes Charter

[DRAFT v1.1]

Hermes operates as the Quantitative Research Department and independent audit function for the Austin Trading Team.

Hermes responsibilities:

- Run and document validation cycles.
- Critique assumptions and identify weaknesses.
- Produce operational readiness reviews.
- Maintain evidence discipline and negative-result capture.
- Raise Engineering Review Proposals when technical decisions require reconsideration.
- Detect contradictions across specs, code, research and governance documents.

Hermes restrictions:

- Must not execute trades.
- Must not connect to brokers.
- Must not use paper-trading APIs.
- Must not approve its own recommendations as final governance.
- Must not hide negative findings.

## 13. Feature Lifecycle

[DRAFT v1.1]

Feature states:

1. Idea.
2. Hypothesis.
3. Specification draft.
4. Laboratory experiment.
5. Validation candidate.
6. Development implementation.
7. Regression candidate.
8. Release candidate.
9. Released.
10. Deprecated or rejected.

Promotion requires evidence appropriate to the state transition.

## 14. Deprecation

[DRAFT v1.1]

Deprecated behaviour must include:

- Reason for deprecation.
- Affected files, engines or parameters.
- Replacement or migration path.
- Effective version.
- Removal target version, if applicable.
- Evidence that deprecation does not silently break released behaviour.

## 15. Review Cadence

[DRAFT v1.1]

- Operational readiness review: at least quarterly while under active development.
- Architecture review: before major interface changes.
- Research methodology review: after any major validation failure or quarterly.
- Risk review: monthly or after critical/high-risk events.
- Documentation review: each release and monthly during rapid development.

## 16. Required Governance Documents

[DRAFT v1.1]

The following documents form the ATOS v1.1 governance pack:

- Project Charter.
- Architecture.
- Coding Standards.
- Research Methodology.
- Release Process.
- Hermes Integration.
- Quality Manual — approved by Paul Austin as part of the ATOS v1.1 governance baseline.
- Risk Management Standard.
- Data Management Policy.
- Security Policy.
- AI Ethics Policy.
- Feature Lifecycle.
- Deprecation Policy.
- Engineering Decision Record Standard.
- Research Decision Record Standard.
- Project Review Standard.
- Specification Template.
- Austin Trading Knowledge Base.

## 17. Approval Status

[DRAFT v1.1]

Paul Austin has approved ATOS v1.1 in principle, subject to review of the full amended governance pack.

Paul Austin has approved the Quality Manual v1.1 as part of the ATOS v1.1 governance baseline.

This document is not yet promoted as the full approved ATOS v1.1 governance baseline. Full ATOS v1.1 becomes approved only after Paul reviews the complete amended draft and explicitly approves promotion.

Until that approval occurs, existing repository documents remain the active ATOS baseline.
