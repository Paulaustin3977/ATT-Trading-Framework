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

### Early-stage role ownership may be functional

Evidence: Paul Austin approved ATOS v1.1 in principle and clarified that roles may be assigned as functional responsibilities rather than separate agents during early-stage development.

Knowledge entry: ATOS roles do not require separate permanent agents at this stage. Current functional ownership is: Product Owner Paul Austin; Chief Systems Architect ChatGPT; Quantitative Research Department Hermes; Release Manager Paul Austin + ChatGPT; Documentation Owner ChatGPT with Hermes audit support; Data Steward Hermes initially; Risk Owner Paul Austin; Security Owner Paul Austin.


### Quality Manual v1.1 approved

Evidence: Paul Austin approved `docs/governance/Quality_Manual.md` as part of the ATOS v1.1 governance baseline.

Knowledge entry: Quality Manual v1.1 is the active quality governance baseline for ATOS v1.1. It defines proportional gates, supported-performance evidence thresholds, release-manifest structure, Hermes block authority, waiver expiry rules and post-release incident handling.

### RDR-001 research storage standard approved

Evidence: Paul Austin approved RDR-001 after final amendment application.

Knowledge entry: RDR-001 is the active ATOS v1.1 research storage and reporting baseline. Core CSV schema is locked; additions must be appended and documented in manifests; breaking schema changes require versioned templates; raw data remains mostly untracked with manifests committed.

## Open Governance Questions

- What manual TradingView validation evidence is acceptable when automated checks are unavailable?
- What cadence should be used for ATOS reviews once the project reaches stable maintenance?

## Current Role Ownership

| Functional role | Current owner |
|---|---|
| Product Owner | Paul Austin |
| Chief Systems Architect | ChatGPT |
| Quantitative Research Department | Hermes |
| Release Manager | Paul Austin + ChatGPT |
| Documentation Owner | ChatGPT, with Hermes audit support |
| Data Steward | Hermes initially |
| Risk Owner | Paul Austin |
| Security Owner | Paul Austin |

Quality Manual v1.1 is approved as part of the ATOS v1.1 governance baseline. Full ATOS v1.1 remains draft until Paul reviews the complete amended governance pack and explicitly approves promotion.

## Negative Findings from ATOS-001

- Governance responsibilities are not yet complete enough for 5-10 year scaling.
- Security and data governance are missing from the current document set.
- Research reproducibility is required in principle but not yet controlled by a manifest/template.
- Release readiness is defined as a checklist but lacks named owner and waiver policy.
