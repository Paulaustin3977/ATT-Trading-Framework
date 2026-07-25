# ATE Diagnostic Roadmap

ATE is currently a research-only market-diagnostics project. Roadmap completion means documented, reproducible diagnostic evidence; it does not mean a trading system is ready for orders or execution.

## Status vocabulary

- **Implemented:** code exists in the named source artefact.
- **Verified:** automated integrity, contract, boundary, or fixture checks pass. Verification is not empirical validation.
- **Validated:** an RDR has tested diagnostic behaviour and assigned an evidence classification.
- **Approved:** the Product Owner has authorised a precisely stated scope. Diagnostic or research approval does not imply action authority.

## Completed baseline work

- [x] Repository, documentation, research storage, and canonical verifier established.
- [x] Immutable ATE v2.2 release stored at `pine/releases/ATE_v2.2.pine`.
- [x] Paul Austin confirmed the immutable v2.2 release compiles cleanly in TradingView.
- [x] Existing trend score, StructureEngine, MomentumEngine, ConfidenceEngine, DashboardEngine, and Research Mode implemented in v2.2.
- [x] VolatilityEngine `1.0.0-draft` implemented as diagnostic-only.
- [x] RiskEngine `1.0.0-draft` implemented as diagnostic-only; it publishes no `riskApproved` value and has no decision authority.
- [x] Ten pre-existing indicator-event alerts preserved; no RiskEngine alert added.
- [x] Canonical ATE release contract/integrity verification established.

## Validation evidence completed

- [x] RDR-002 daily VolatilityEngine validation — **Weakly Supported; Keep Diagnostic**.
- [x] RDR-002W weekly VolatilityEngine validation — **Weakly Supported; Keep Diagnostic**.
- [x] RDR-003 daily RiskEngine validation — **Weakly Supported; Keep Diagnostic**.
- [x] RDR-003W weekly RiskEngine validation — **Supported for controlled weekly research use; Keep Diagnostic**.

These classifications do not approve VolatilityEngine or RiskEngine consumption by ConfidenceEngine or DecisionEngine.

## Active research lineage

- [x] TrendEngine `0.2.0-spec-impl` specified and implemented in `pine/development/ATE_Current.pine` only.
- [x] TrendEngine contract and deterministic fixture checks added to the canonical verifier.
- [x] Re-attempt RDR-010 TrendEngine validation on daily and weekly Gold, Silver, and Gilts — **Mixed evidence; retain diagnostic-only; no promotion**.
- [ ] Investigate the near-absence of `RANGE`, add inference-aware/non-overlapping evaluation, and pre-register any future acceptance criteria.
- [ ] Obtain explicit Product Owner approval before any promotion from development research to an immutable release.

No TradingView compile evidence is claimed for the development-only TrendEngine. Its verification is local/canonical-verifier evidence, not TradingView compile confirmation.

## Remaining diagnostic work

- [ ] Complete and govern Pine-versus-research-mirror parity evidence where required before stronger empirical claims.
- [ ] Investigate documented weak/negative findings: RiskEngine calm/normal skew, thin tense/extreme samples, component dominance, and threshold sensitivity.
- [ ] Add dedicated empirical validation for StructureEngine, MomentumEngine, ConfidenceEngine, and the existing trend score only if research priorities require claims beyond implementation/verification.
- [ ] Keep specifications, release manifests, RDRs, README, roadmap, and journal synchronised as evidence changes.
- [ ] Promote an engine only after separate verification, validation, and explicit approval gates are each satisfied.

## Deferred / outside current scope

- DecisionEngine implementation or activation.
- No trade approval/rejection logic and no `riskApproved` contract.
- Entries, exits, orders, broker connectivity, paper/live execution, position sizing, stop placement, and trade management.
- Any strategy layer or autonomous action based on diagnostic outputs.
- A live execution dashboard.

A future proposal to change any of these boundaries requires a separate specification amendment, research evidence, architecture/governance review, and explicit Product Owner approval. It is not part of the current roadmap.
