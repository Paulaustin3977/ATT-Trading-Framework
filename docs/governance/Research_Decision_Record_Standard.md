# Research Decision Record Standard

Task ID: RDR-001
Version: 1.0 Draft
Status: Draft for Paul Austin Review
Owner: Hermes, Quantitative Research Department
Applies To: Austin Trading Engine, Austin Research Lab, Austin Strategy Framework, Austin Market Intelligence, and future Austin Trading Platform research.

---

# 1. Purpose

Research Decision Records (RDRs) preserve important research decisions so Austin Trading Team does not repeat old tests, lose negative results, or treat unsupported findings as accepted knowledge.

An RDR separates:

- Evidence
- Interpretation
- Recommendation
- Decision

Hermes may recommend. Paul Austin approves final governance, release promotion, and material risk acceptance.

---

# 2. Storage Location

RDRs are stored in:

`research/Reports/RDR/`

Canonical naming:

`RDR-0001_short-kebab-title.md`

Examples:

- `research/Reports/RDR/RDR-0001_gold-daily-trend-engine-supported.md`
- `research/Reports/RDR/RDR-0002_nvda-exceptional-history-not-generalised.md`
- `research/Reports/RDR/RDR-0003_rsi-family-operationally-rejected.md`

The standard template is:

`docs/templates/RDR_Template.md`

---

# 3. RDR ID Rules

- Format: `RDR-0001`, `RDR-0002`, etc.
- IDs are never reused.
- If an RDR is superseded, keep the old RDR and set status to `Superseded`.
- RDR ID must appear in related reports, manifests, summary CSV rows, and changelog entries where material.

---

# 4. When an RDR is Mandatory

Create an RDR when:

- A research finding changes project direction.
- A feature is accepted or rejected.
- An asset class is promoted or downgraded.
- A parameter family is approved or rejected.
- A test produces an important negative result.
- A repeated finding becomes accepted project knowledge.
- Hermes identifies a research risk that affects future development.
- A backtest/validation run supports promotion, deprecation, or rejection.
- A Product Owner override changes the outcome of a Hermes `Research Blocked` or `Quality Blocked` finding.

No RDR is required for minor exploratory checks that produce no reusable evidence, but the run manifest should still be retained if work was material.

---

# 5. RDR Status Values

Use one status only:

- `Proposed` — written but not reviewed.
- `Under Review` — awaiting Paul Austin / accountable-owner review.
- `Accepted` — decision accepted into project knowledge.
- `Rejected` — recommendation rejected.
- `Superseded` — replaced by a later RDR.
- `Deprecated` — decision no longer active but historically relevant.

Research classification is separate from RDR status.

Research classification values:

- `Supported`
- `Weakly Supported`
- `Inconclusive`
- `Falsified`
- `Operationally Rejected`

---

# 6. Required RDR Sections

Every RDR must include:

1. RDR ID
2. Title
3. Date
4. Status
5. Owner / author
6. Related ATOS version
7. Related ATE version
8. Related research reports
9. Related run manifests
10. Related summary CSV rows or run IDs
11. Research question
12. Hypothesis
13. Evidence reviewed
14. Data source and date range
15. Methodology summary
16. Bias and quality controls reviewed
17. Decision
18. Reasoning
19. Confidence level
20. Research classification
21. Recommendation
22. Limitations
23. Consequences
24. Follow-up work
25. Approval status
26. Links to artefacts
27. Research integrity statement

---

# 7. Confidence Levels

Use plain-language confidence, not false precision:

- `High` — multiple robust tests, OOS support, stable parameters, no obvious bias issue.
- `Medium` — useful evidence but limited by sample size, universe, or methodology.
- `Low` — weak evidence, early signal, fragile test, or narrow scope.
- `None` — falsified, operationally rejected, or not enough evidence.

A high historical return alone does not justify high confidence.

---

# 8. Approval and Decision Authority

Hermes may draft an RDR and recommend a decision.

Paul Austin, as Product Owner, approves:

- Stable release promotion.
- Governance effect.
- Material risk acceptance.
- Override of Hermes blocks.

An RDR can record a Hermes recommendation before Paul approval, but it must not imply final governance approval unless Paul explicitly approves it.

---

# 9. Referencing Rules

Every research report that leads to an RDR must link the RDR.

Every RDR must link:

- Human-readable report path.
- Research run manifest path.
- Machine-readable summary CSV path and row key.
- Relevant ATE release file.
- Git commit hash.

If an RDR changes project knowledge, update:

- `docs/knowledge/ATT_Knowledge_Base.md`, or
- a specialised knowledge file if one exists.

---

# 10. Negative and Failed Results

Negative, weak, inconclusive, falsified, and operationally rejected results are first-class research outputs.

They must be preserved when they prevent future rework or reveal a risk.

Failed runs should be stored if they reveal:

- Data problem.
- Methodology problem.
- Engine bug.
- Overfitting risk.
- Asset unsuitability.
- Scope or no-execution boundary concern.

Do not delete a result because it is unattractive.

---

# 11. Lean Operation Rule

Not every exploratory run needs a full RDR.

Use this rule:

- Exploratory scratch test: manifest only if material.
- Backtest report with no decision impact: report + manifest + summary row.
- Research conclusion, promotion, rejection, downgrade, or accepted knowledge: RDR required.

---

# 12. Review Checklist

Before marking an RDR ready for review:

- Evidence, interpretation, recommendation, and decision are separated.
- Report paths resolve.
- Manifest path resolves.
- Summary CSV row/run ID is listed.
- Data source and date range are stated.
- Bias controls are documented.
- Limitations are explicit.
- No live trading, broker, or paper-trading API dependency is introduced.
- Hermes recommendation does not claim final Paul Austin approval unless approval occurred.
