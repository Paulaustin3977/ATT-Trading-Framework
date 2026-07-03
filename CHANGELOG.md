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
