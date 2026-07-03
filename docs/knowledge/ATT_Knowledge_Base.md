# Austin Trading Knowledge Base

Status: Draft knowledge entries created from ATOS-001
Date: 2026-07-03

## Permanent Principles

### No execution boundary

Evidence: `docs/Project_Charter.md` and `docs/Hermes_Integration.md` explicitly prohibit live trade execution, broker connectivity and paper-trading APIs.

Knowledge entry: Austin Trading Engine is a research and decision-support framework only. Execution, broker integration and paper-trading APIs are out of scope.

### Evidence before promotion

Evidence: `docs/Research_Methodology.md`, `CONTRIBUTING.md` and `docs/Release_Process.md` require evidence, regression checks and Hermes validation.

Knowledge entry: A feature or research claim is not accepted on intent alone; it requires documented hypothesis, data, method, result, limitation and reproducibility notes.

### Negative results are first-class outputs

Evidence: `docs/Research_Methodology.md` and `CONTRIBUTING.md` state that negative/null results must be recorded.

Knowledge entry: Negative findings reduce future research waste and must be preserved rather than hidden.

### Hermes recommends, humans approve

Evidence: ATOS-001 audit identified a conflict risk if Hermes both generates evidence and approves governance.

Knowledge entry: Hermes may audit, critique and recommend, but should not be sole approval authority for governance, releases or trading-related scope decisions.

### Modularity requires interface governance

Evidence: `docs/Architecture.md` defines independent engines and one-way data flow, but no decision-record standard exists yet.

Knowledge entry: Engine modularity must be protected through explicit interface contracts and Engineering Decision Records.

## Open Governance Questions

- Who is the named Risk Owner?
- Who is the named Documentation Owner?
- What minimum statistical standard is required before a claim is classified as supported?
- What manual TradingView validation evidence is acceptable when automated checks are unavailable?
- What cadence should be used for ATOS reviews once the project reaches stable maintenance?

## Negative Findings from ATOS-001

- Governance responsibilities are not yet complete enough for 5-10 year scaling.
- Security and data governance are missing from the current document set.
- Research reproducibility is required in principle but not yet controlled by a manifest/template.
- Release readiness is defined as a checklist but lacks named owner and waiver policy.
