# CHANGELOG

All notable changes to the Austin Trading Engine (ATE) are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Active Architecture.md baseline approved by Paul Austin:
  - RiskEngine moved after ConfidenceEngine.
  - Engine Output Contract added.
  - DashboardEngine confirmed as presentation-only.
  - RiskEngine defined as a safety/suitability filter rather than a confidence creator.
- ATOS-001 Operational Readiness Review draft.
- ATOS v1.1 draft amendments for review.
- Quality Manual v1.1 approved by Paul Austin as part of the ATOS v1.1 governance baseline.
- RDR-001 research storage, Research Decision Record, backtest result format standards, schema-version templates, raw-data policy, and Tier A trade-count thresholds approved by Paul Austin as part of the ATOS v1.1 governance baseline.
- VolatilityEngine v1.0 draft specification added for ATE v2.1 review.
- VolatilityEngine Specification approved for diagnostic-only ATE v2.1 implementation planning.
  - Downstream consumption by ConfidenceEngine, RiskEngine, and DecisionEngine remains prohibited in ATE v2.1.
- ATE v2.1 Implementation Plan added for diagnostic-only VolatilityEngine Pine planning.
  - The plan preserves the prohibition on ConfidenceEngine, RiskEngine, DecisionEngine, entry/exit logic, position sizing, stop placement, and trade-action alert impact.
- ATE v2.1 Pine implementation added.
  - TradingView compile confirmed clean by Paul Austin.
  - ATE v2.1 stored as rollback baseline.
  - VolatilityEngine added as diagnostic-only dashboard and Research Mode module.
- RDR-002 VolatilityEngine diagnostic validation completed.
  - Classification: Weakly Supported.
  - Recommendation: Keep Diagnostic; RiskEngine and ConfidenceEngine integration remain deferred.
  - Artefacts stored under `research/Reports/RDR/` and `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/`.
- RDR-002W VolatilityEngine weekly diagnostic validation completed.
  - Same classification: Weakly Supported.
  - Recommendation unchanged: Keep Diagnostic; RiskEngine and ConfidenceEngine integration remain deferred.
  - Comparison with daily: state sequences smoother; abs momentum overlap roughly 2.6x daily but still well under the redundancy threshold; no hidden directional bias.
  - Artefacts stored under `research/Reports/RDR/RDR-002W-volatility-diagnostic-validation.md` and `backtests/Hermes/ATE_v2.1/Weekly/Diagnostic_Validation/RDR-002W/`.
- RDR-002 verifier recorded as limited behaviour verification (43/43 ad-hoc checks, NOT suite green).
- ERP-001 Engineering Review Proposal added proposing a canonical `tools/scripts/verify_ate.py` entry point for future ATE verification cycles.
  - No ATE Pine code modified.
- EDR-001 implemented: canonical ATE verifier in place.
  - `tools/scripts/verify_ate.py` created.
  - Seeded ATE v2.1 fixtures added under `tests/fixtures/ATE_v2_1/`.
  - Ad-hoc verification replaced by repo-level verification command.
  - Verifier result: 100/100 contract and behaviour checks pass against `pine/releases/ATE_v2.1.pine`.
  - No ATE Pine logic modified.
  - VolatilityEngine classification remains Weakly Supported; no reclassification, no RiskEngine/ConfidenceEngine integration authorisation.
- RiskEngine v1.0 Draft drafted and reviewed.
  - Recommendation: Approve with amendments.
  - Implementation readiness: ready for diagnostic-only implementation planning after blocking questions are answered.
  - ATE v2.2 RiskEngine remains diagnostic-only; no ConfidenceEngine, DecisionEngine, entry/exit, sizing, stop, or trade-action alert impact.
  - Revised specification saved at `specifications/ATE/RiskEngine.md`.
  - Review report saved at `research/Reports/RDR/RiskEngine_Specification_Review.md`.
- RiskEngine Specification v1.0 Draft approved for diagnostic-only ATE v2.2 implementation planning.
  - Status changed from Draft for Review to Approved for Diagnostic-Only Implementation Planning.
  - Approval boundaries confirmed by Paul Austin / Chief Systems Architect on 2026-07-03.
  - Downstream consumption by ConfidenceEngine, RiskEngine, and DecisionEngine remains prohibited in ATE v2.2.
  - ATE v2.1 release file must remain unchanged.
- EDR-001 canonical verifier extended for planned ATE v2.2 RiskEngine coverage.
  - RiskEngine fixture directory added under `tests/fixtures/ATE_v2_2/` with seeded `calm_normal`, `elevated`, `extreme_conflict`, `unknown` regimes.
  - `tests/fixtures/ATE_v2_2/fixture_spec.json` and `tools/scripts/_riskengine_compute.py` recorded as the planned compute-path mirror.
  - Verifier now asserts the approved RiskEngine specification defines the four-component cap table, allowed states and directions, reserved-language absence, diagnostic-only boundaries, and version literal.
  - Behavioural checks pass: 270 of 270 contract and behaviour checks against the ATE v2.1 VolatilityEngine compute path and the ATE v2.2 RiskEngine planned compute path.
  - No ATE Pine logic modified.
  - No ATE v2.2 release file created yet.
- ATE v2.2 RiskEngine implementation plan added.
  - Implementation plan saved at `docs/releases/ATE_v2.2_Implementation_Plan.md` against the approved RiskEngine v1.0 Draft specification.
  - Implementation may begin only after Paul Austin answers the open questions and the canonical verifier `tools/scripts/verify_ate.py` is extended to load the new `pine/releases/ATE_v2.2.pine` release file.
  - No Pine code written.
  - `pine/releases/ATE_v2.2.pine` not yet created.
  - `pine/releases/ATE_v2.1.pine` SHA remains unchanged at `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`.
- ATE v2.2 RiskEngine implementation plan approved and ready for Pine implementation.
  - Paul Austin / Chief Systems Architect answers to all five blocking questions recorded in §19 on 2026-07-03.
  - Verifier extension `tools/scripts/verify_ate.py` confirmed as the required implementation gate.
  - ATE v2.2 release filename confirmed as `pine/releases/ATE_v2.2.pine`.
  - Dashboard label list in §9 accepted; reserved language remains forbidden.
  - Seven Pine input names in §6 are final.
  - Pine implementation may begin only after the verifier extension lands.
  - Implementation status: Approved and ready for Pine implementation.
  - ATE v2.1 release file remains unchanged.
- ATE v2.2 Pine implementation added.
  - TradingView compile confirmed clean by Paul Austin.
  - `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` stored byte-identical (SHA-256 `743988ef7c8342c99a4f2f2fbdad27dce6d0594b702cee46fa652652a4f9c2b0`).
  - Release manifest stored at `docs/releases/ATE_v2.2_Release_Manifest.md`.
  - RiskEngine added as diagnostic-only dashboard and Research Mode module.
  - VolatilityEngine v1.0.0-draft preserved from ATE v2.1.
  - Existing ATE alerts preserved.
  - No RiskEngine alerts added.
  - No ConfidenceEngine impact, DecisionEngine impact, entry/exit impact, position sizing impact, or stop logic impact.
  - ATE v2.1 release file remains unchanged (SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`).
  - RDR-003 and RDR-003W validation cycles remain scheduled future work.
- Draft governance standards covering quality, risk, data, security, AI-agent governance, feature lifecycle, deprecation, decision records, project review and specification templates.
- Draft Austin Trading Knowledge Base entries from the ATOS-001 review.

### Existing baseline

- Full repository folder structure (specifications, laboratory, research, backtests, tests, tools).
- Documentation suite: Project Charter, Architecture, Coding Standards, Research Methodology, Release Process, Hermes Integration.
- Engine specifications: Trend, Structure, Momentum, Volatility, Confidence, Risk, Decision, Dashboard.
- Placeholder Pine scripts: `pine/development/ATE_Current.pine`, `pine/releases/ATE_v2.0.pine`.

## v0.1.0

### Added

- Project repository
- Folder structure
- Documentation framework
- Pine Script project

## v0.1.0-pre

- Initial ATT Trading Framework project bootstrap.
