# Quality Manual Recommended Amendments

Date: 2026-07-03
Status: Recommendations for Paul Austin review
Source: Hermes Quality Manual Review

## Required Amendments

### 1. Define applicability

Add a section explaining that quality gates are risk-based and proportional. Not every small change requires every gate.

Recommended wording:

> The applicable gates depend on change type and risk. Minor editorial changes do not require full research validation. Engine behaviour changes, research claims, releases, and architecture changes require stricter gates.

### 2. Add missing gates

Add these gates:

- Data Quality Gate
- Security and No-Execution Gate
- Regression and Compatibility Gate
- Decision Record Gate
- Release Manifest Gate
- Waiver and Exception Gate
- Knowledge Capture Gate

### 3. Make research controls enforceable

Add explicit controls for:

- Pre-registered hypothesis.
- Data source and transformations.
- In-sample/out-of-sample or reason not applicable.
- Walk-forward testing for strategy/performance claims where feasible.
- Parameter sensitivity for tunable logic.
- Benchmark/null comparison where relevant.
- Transaction costs for strategy/performance claims.
- Bias checks: lookahead, data snooping, survivorship, regime dependence, proxy mismatch.
- Result classification: supported, weakly supported, inconclusive, falsified, rejected.

### 4. Strengthen engineering controls

Add explicit requirements for:

- Compile evidence.
- Non-repainting/lookahead review.
- Engine Output Contract compliance.
- One-way data-flow compliance.
- DashboardEngine not mutating upstream values.
- Regression evidence for behaviour changes.
- Migration note for breaking contract changes.

### 5. Add release controls

Add a Release Manifest requiring:

- Release version.
- Commit hash.
- Files released.
- Specs updated.
- Research artefacts.
- Regression evidence.
- Known issues and severity.
- Rollback path.
- Approver.

### 6. Add waiver controls

Add a waiver process requiring:

- Requirement waived.
- Reason.
- Risk severity.
- Mitigation.
- Owner.
- Expiry/review date.
- Approval by Product Owner and/or Risk Owner.

### 7. Reduce bureaucracy risk

Add a change-size matrix:

| Change type | Minimum gates |
|---|---|
| Editorial documentation | Documentation, review |
| Minor bug fix | Mission, engineering, regression, documentation, review |
| Engine behaviour change | Specification, engineering, contract, regression, documentation, review |
| Research claim | Mission, data, research validation, reproducibility, knowledge capture, review |
| Release | All applicable gates, release manifest, Product Owner approval |
| Architecture/governance change | Decision record, documentation, review, Product Owner approval |

### 8. Preserve draft status

Keep the document as draft until Paul Austin reviews and explicitly approves it.
