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
  - No ConfidenceEngine impact, DecisionEngine impact, entry/exit, position sizing, or stop logic impact.
  - ATE v2.1 release file remains unchanged (SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`).
  - RDR-003 and RDR-003W validation cycles remain scheduled future work.
- ATE v2.2 preserved `confidenceBear` alertcondition restored.
  - The user-provided v2.2 source paste ended at `confidenceBull` (9 alertcondition calls); ATE v2.1 contained 10 including `alertcondition(confidenceBear, "ATE Low Confidence Bear", "...")`.
  - Paul Austin authorised restoration of the missing alert to preserve full ATE v2.1 alert behaviour.
  - Restored alertcondition added at the end of the Alerts block in `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` (byte-identical, new SHA-256 `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`).
  - 10 alertcondition titles in v2.2 now match the 10 titles in ATE v2.1 exactly.
  - No RiskEngine logic modified. No RiskEngine alerts added. No other Pine logic altered.
  - ATE v2.1 release file remains unchanged (SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`).
  - TradingView re-compile confirmation by Paul Austin pending after restoration.
- ATE v2.2 TradingView compile confirmed clean after alert restoration.
  - Paul Austin recompiled the updated ATE v2.2 Pine release in TradingView after the restored `confidenceBear` alert; TradingView compile produced zero errors.
  - Release file SHA-256 unchanged from the restored baseline: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`.
  - Screenshots/local-evidence: `/home/paul/Pictures/Screenshots/Screenshot From 2026-07-03 23-52-49.png` (Linux-style path; actual local copy on macOS is under `/Users/paul/Pictures/` — reference only, not committed to repo).
  - ATE v2.2 preserves all 10 existing ATE alertcondition calls; no RiskEngine alerts added; RiskEngine remains diagnostic-only.
  - ATE v2.1 release file remains unchanged (SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`).
  - No Pine logic modified during this confirmation step.
- EDR-001 canonical verifier extended to load ATE v2.2 release file directly.
  - `tools/scripts/verify_ate.py` now directly loads `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` and asserts the contract recorded in the ATE v2.2 Release Manifest and the approved RiskEngine v1.0 specification.
  - New checks (v22:* namespace): file integrity (release SHA matches manifest, dev mirror byte-identical, v2.1 SHA unchanged); header/version literals; the seven approved RiskEngine input identifiers; Engine Output Contract variables including `riskScore`, `riskState`, `riskDirection`, `riskReason`, `riskEngineVersion`, component raw scores, component states, smoothed raw, and diagnostic variables; allowed RiskState values (`calm`, `normal`, `elevated`, `tense`, `extreme`, `unknown`); allowed RiskDirection values (`none`, `elevated`, `conflict`, `stable`, `indeterminate`); no `bullish`/`bearish` in state or direction; component cap clamps (`f_clamp(..., 0.0, 35.0/30.0/20.0/15.0)`) and dashboard render caps (`"/ 35"`, `"/ 30"`, `"/ 20"`, `"/ 15"`); total `riskScore` clamp `[0.0, 100.0]`; the 14 approved dashboard labels; the 15 approved Research Mode labels; exactly 10 alertcondition titles matching ATE v2.1; no RiskEngine alert; boundary discipline (no assignment to `confidenceScore`/`marketState`/`trendScore`/`structureScore`/`momentumScore`/`volScore`/`volState`/`volDirection`/`volShockFlag`; no `strategy(...)`, broker, paper-trading, order, position-size, stop-distance, stop-placement, entry-logic, exit-logic); reserved-language absence (`safe`, `unsafe`, `suitable`, `unsuitable`, `approved`, `blocked`, `tradeable`, `untradeable`) scoped to RiskEngine dashboard labels, Research Mode labels, state values, direction values, and reason text only.
  - Expected SHA constants `V22_EXPECTED_SHA` and `V21_EXPECTED_SHA` baked into the verifier to catch unintended release-file changes.
  - `tests/README.md` updated with the new release-file check scope.
  - No ATE Pine logic modified.
  - Verifier run result: 442/442 checks pass (exit code 0). v2.2 release SHA-256 matches manifest, dev mirror byte-identical, v2.1 SHA-256 unchanged.
  - This is a verifier-infrastructure extension. It does NOT claim empirical usefulness of the RiskEngine; RDR-003 / RDR-003W remain required for any diagnostic-to-downstream change.
- RDR-003 RiskEngine daily diagnostic validation completed.
  - 16-asset daily validation across metals (Gold, Silver, Copper), index proxies (Nasdaq, S&P 500), major equities (NVDA, MSFT, AAPL, AMZN, GOOGL), bonds / rates proxies (TLT, IGLT.L as gilt proxy), FX (EUR/USD, GBP/USD, USD/JPY), and commodities (WTI crude); 34,436 daily bars between 2018-01-02 and 2026-07-03.
  - Verifier pre-flight confirmed clean: 442/442 checks pass, exit 0; v2.2 SHA matches manifest, v2.2 release/dev byte-identical, v2.1 SHA unchanged.
  - **Classification: Weakly Supported.**
  - **Recommendation: Keep Diagnostic; weekly RDR-003W and threshold review before any confidence-integration attempt.**
  - RiskEngine remains diagnostic-only: DecisionEngine integration remains deferred, ConfidenceEngine integration remains deferred, alerts remain prohibited.
  - Artefacts:
    - Report: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md`
    - Manifest: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/RDR-003_Manifest.md`
    - Summary CSV: `RDR-003_Summary.csv`
    - Durations CSV: `RDR-003_Durations.csv`
    - Transitions CSV: `RDR-003_Transitions.csv`
    - Class summary CSV: `RDR-003_Class_Summary.csv`
    - Overlap CSV: `RDR-003_Overlap.csv`
    - Hidden bias CSV: `RDR-003_HiddenBias.csv`
    - Adverse movement CSV: `RDR-003_Adverse.csv`
    - Sampled explainers CSV: `RDR-003_Sampled_Explainers.csv`
    - Reserved language audit CSV: `RDR-003_Reserved_Language_Audit.csv`
    - Per-asset charts: `charts/<symbol>_risk_states.png`
    - Reproduction script: `run_rdr003_validation.py`
  - Key findings: median absolute Spearman of RiskScore vs VolatilityScore 0.17 (low, not a renamed VolatilityEngine); vs Momentum 0.31 (low); vs Confidence 0.43 (moderate but distinct); median state_changes_per_100_bars 9.89 (not noisy); median max |pct_up-50| 4.5pp (low directional bias); reserved-language audit 0/432 hits.
  - Negative findings: state distribution heavily calm-skewed (median pct_calm ~70%); `tense`/`extreme` states very rare and thin on evidence; volatility component dominates >60% of bars in 6/16 assets (FX, TLT, IGLT.L, CL); conflict component small in most bars; what is measured here is the deterministic Python mirror, not the actual Pine implementation, until a separate Pine-vs-Python parity check is performed.
  - Follow-up: RDR-003W weekly validation, Pine-vs-Python parity check, threshold retest before any downstream consumption.
  - No ATE Pine logic modified. No broker, no paper-trading API. Diagnostic only.
- RDR-003W RiskEngine weekly diagnostic validation completed.
  - Same 16-asset universe as RDR-003 daily; 8,355 weekly bars between 2014-01-01 and 2026-07-03.
  - Verifier pre-flight confirmed clean: 442/442 checks pass, exit 0; v2.2 SHA matches manifest; v2.2 release/dev byte-identical; v2.1 SHA unchanged.
  - **Classification: Supported.** **Recommendation: Keep Diagnostic; allow controlled weekly research use; DecisionEngine / ConfidenceEngine integration remains deferred.**
  - RiskEngine remains diagnostic-only on weekly aggregations as well.
  - Artefacts:
    - Report: `research/Reports/RDR/RDR-003W-riskengine-weekly-diagnostic-validation.md`
    - Manifest: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/RDR-003W_Manifest.md`
    - Summary CSV: `RDR-003W_Summary.csv`
    - Durations CSV: `RDR-003W_Durations.csv`
    - Transitions CSV: `RDR-003W_Transitions.csv`
    - Class summary CSV: `RDR-003W_Class_Summary.csv`
    - Overlap CSV: `RDR-003W_Overlap.csv`
    - Hidden bias CSV: `RDR-003W_HiddenBias.csv`
    - Adverse movement CSV: `RDR-003W_Adverse.csv`
    - Sampled explainers CSV: `RDR-003W_Sampled_Explainers.csv`
    - Reserved language audit CSV: `RDR-003W_Reserved_Language_Audit.csv`
    - Per-asset charts: `charts/<symbol>_risk_states_weekly.png`
    - Reproduction script: `run_rdr003w_validation.py`
  - Daily-vs-weekly comparison: state_changes_per_100_bars median 9.89 → 10.15 (stable); median `dominant_vol_pct` 51.29% → 48.08% (-3.2pp); assets with `dominant_vol_pct > 60` 6 → 4 (clears the 4-asset daily threshold); median `pct_calm` 70.30% → 68.04% (-2.3pp); median abs Spearman vs VolScore 0.167 → 0.211 (+0.044); vs Momentum 0.309 → 0.258 (-0.051); vs Confidence 0.425 → 0.405 (-0.020); median max |pct_up-50| 4.52pp → 7.48pp (small-sample weekly noise, both below 12pp threshold); reserved-language audit 0/418 hits.
  - Key findings: all 9 weekly classification rules pass; weekly sequence length is comparable to daily per-100-bars; volatility dominance in low-vol asset classes (FX, TLT, IGLT.L, CL=F) attenuates on weekly aggregation; overlap with Volatility and Momentum remains in the acceptable range; diagnostic-only governance unchanged.
  - Negative findings: state distribution still calm/normal-skewed (median pct_calm 68.0%); `tense`/`extreme` evidence remains thin on weekly bars; hidden-bias median moves modestly upward 4.5pp → 7.5pp due to small `extreme`/`tense` weekly samples; Conflict component remains small in most bars; what is measured here is the deterministic Python mirror; Pine-vs-Python parity check remains a separate prerequisite before any downstream consumption claim.
  - Follow-up: Pine-vs-Python parity check; any future daily threshold retest must be re-validated on weekly bars before re-classifying RiskEngine from "Supported" → "Confirmed-Supported".
  - No ATE Pine logic modified. No broker, no paper-trading API. Diagnostic only.
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
