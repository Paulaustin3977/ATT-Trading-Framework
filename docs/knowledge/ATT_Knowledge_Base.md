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

### RDR-002 VolatilityEngine diagnostic validation

Evidence: `research/Reports/RDR/RDR-002-volatility-diagnostic-validation.md` validated ATE v2.1 VolatilityEngine diagnostic behaviour across daily multi-asset data.

Knowledge entry: VolatilityEngine v1.0.0-draft is weakly supported as a diagnostic-only module. It should remain available for DashboardEngine and Research Mode, but RiskEngine and ConfidenceEngine integration remain deferred pending stronger evidence. The validation found useful regime diagnostics, low redundancy with Trend/Momentum, and no material hidden directional bias, but threshold/state-frequency concerns justify retesting before any downstream use.

### RDR-002W VolatilityEngine weekly diagnostic validation

Evidence: `research/Reports/RDR/RDR-002W-volatility-diagnostic-validation.md` validated ATE v2.1 VolatilityEngine diagnostic behaviour across weekly multi-asset data.

Knowledge entry: VolatilityEngine v1.0.0-draft is also weakly supported on weekly aggregation. The weekly pattern agrees with the daily finding: useful diagnostic information, no hidden directional bias, smoother state sequences on weekly bars. RiskEngine and ConfidenceEngine integration remain deferred.

### ERP-001 canonical ATE verification entry point

Evidence: `docs/EDR/ERP-001-canonical-ate-verification-entry-point.md` proposed adding `tools/scripts/verify_ate.py` and a fixtures directory as the future canonical verification command for ATE validation cycles.

Knowledge entry: RDR-002 verification currently relies on ad-hoc verifier artefacts under `/var/folders/0b/8y8rvw6d53q2y6gt96zb6kz00000gn/T/hermes-verify-<slug>/`. The verify script on RDR-002W behaviour is `ad-hoc hermes-verify, NOT suite green` and explicitly labelled as such. Promotion to `Supported`, or any future diagnostic-to-downstream change, requires a canonical repo-level verification command. No ATE Pine code was modified for ERP-001; the Engineering Review Proposal itself records the proposal only.

### EDR-001 canonical ATE verification entry point implemented

Evidence: `docs/EDR/EDR-001-canonical-ate-verification-entry-point.md` records the accepted decision to add `tools/scripts/verify_ate.py`, versioned fixtures under `tests/fixtures/ATE_v2_1/`, and `tests/README.md` as the canonical repo-level verification command.

Knowledge entry: The canonical verifier command is `python tools/scripts/verify_ate.py`. It exits `0` on pass, `1` on fail, `2` on environment error. Initial result: 100/100 contract and behaviour checks pass against `pine/releases/ATE_v2.1.pine`. This verifier result does NOT change the RDR-002 / RDR-002W classification. VolatilityEngine remains `Weakly Supported`, diagnostic-only, with RiskEngine and ConfidenceEngine integration deferred. The verifier also surfaced a real project finding: the ATE v2.1 release exposes VolatilityEngine diagnostic variables under the `vol*` namespace (e.g. `volAtrPercent`, `volAtrRatio`, `volCombinedRatio`, `volShockFlag`), while the VolatilityEngine specification text describes a separate `volDiag*` prefix; both expose individual named diagnostic variables, but the prefix differs. Record this as a future specification amendment candidate; it is not a blocker for EDR-001 acceptance and is not a reclassification of the engine. Future ATE releases should use this command as part of the quality gate.

### RiskEngine v2.2 implementation is blocked until verifier coverage exists

Evidence: EDR-001 verifier was extended in 2026-07 under task ATE-2.2-RISK-VERIFY to cover the planned ATE v2.2 RiskEngine v1.0.0-draft compute path against seeded fixtures under `tests/fixtures/ATE_v2_2/` (`calm_normal`, `elevated`, `extreme_conflict`, `unknown`).

Knowledge entry: The verifier coverage is infrastructure only and does NOT by itself prove empirical usefulness. RDR-001 validation (state frequency, hidden directional bias, overlap with VolatilityEngine, cross-asset behaviour) is still required after RiskEngine Pine implementation. Until that RDR-001 validation produces a non-falsified result and the verifier confirms Pine-vs-Python mirror parity (i.e. the actual Pine implementation matches the deterministic Python mirror the verifier tests), RiskEngine remains diagnostic-only and may not be consumed by DecisionEngine, ConfidenceEngine, entry/exit logic, position sizing, stop logic, or trade-action alerts.

### ATE v2.2 TradingView compile confirmed clean after alert restoration

Evidence: Paul Austin recompiled the updated ATE v2.2 Pine release in TradingView after the restored `confidenceBear` alertcondition was added back to `pine/releases/ATE_v2.2.pine` (and mirrored into `pine/development/ATE_Current.pine`). Local screenshot evidence retained by Paul Austin at `/home/paul/Pictures/Screenshots/Screenshot From 2026-07-03 23-52-49.png` (Linux-style path; the macOS-local reference is under `/Users/paul/Pictures/` and is not committed to the repo).

Knowledge entry: ATE v2.2 TradingView compile produces zero errors at release SHA-256 `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239`. ATE v2.2 now preserves all 10 ATE alertcondition calls (matching ATE v2.1 exactly), no RiskEngine alerts were added, and RiskEngine remains diagnostic-only. The compile confirmation step did not modify any Pine logic. RDR-003 and RDR-003W validation cycles for RiskEngine remain scheduled future work and are not authorised or claimed by this confirmation.

### RDR-003 RiskEngine daily diagnostic validation completed

Evidence: `research/Reports/RDR/RDR-003-riskengine-daily-diagnostic-validation.md` validates the ATE v2.2 RiskEngine v1.0.0-draft Python mirror against daily Yahoo Finance OHLC across 16 assets (Gold, Silver, Copper, NQ=F, SPY, NVDA, MSFT, AAPL, AMZN, GOOGL, TLT, IGLT.L as gilt proxy, EURUSD, GBPUSD, USDJPY, CL=F) over 2018-01-02 to 2026-07-03 (34,436 daily bars). Run script: `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/run_rdr003_validation.py`. ATE v2.2 release SHA-256 `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` and v2.1 release SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` confirmed unchanged by the canonical verifier (442/442 checks pass, exit 0).

Knowledge entry: **RiskEngine v1.0.0-draft is Weakly Supported as a diagnostic-only module on daily data.** Median absolute Spearman between RiskScore and VolatilityScore is 0.17 (range 0.02–0.30 across assets) — RiskEngine is not a renamed VolatilityEngine. Median absolute Spearman between RiskScore and MomentumScore is 0.31 and between RiskScore and ConfidenceScore is 0.43 — both below the relaxed overlap thresholds. State sequence is not noisy on daily data (median state_changes_per_100_bars = 9.89). Hidden directional bias is limited (median max |pct_up-50| per state = 4.5pp). RiskEngine remains diagnostic-only: **DecisionEngine integration remains deferred; ConfidenceEngine integration remains deferred; alerts remain prohibited.** Negative findings: (1) state distribution skews heavily calm (~70% median pct_calm); `tense` and `extreme` states are very rare (medians 0.26% and 0.02%) which limits evidence for those states; (2) the volatility component is the dominant contributor in >60% of bars for 6 of 16 assets (FX, TLT, IGLT.L, CL=F) — these are precisely the asset classes with the lowest daily-range variability, where the vol component acts as a floor rather than duplicating VolScore; the overlap statistics rule out a renamed VolatilityEngine interpretation; (3) the Conflict component is small in most bars (median 4.1 of 15 cap); (4) the Python mirror is what was measured — actual Pine RiskEngine parity still requires a separate Pine-vs-Python check. Daily RDR-003 narrowly missed "Supported" because the 6/16 `dominant_vol_pct > 60` count exceeded the 4-asset acceptance threshold; weekly RDR-003W (see next entry) confirmed this is a daily-bars phenomenon that resolves at weekly aggregation.

### RDR-003W RiskEngine weekly diagnostic validation completed

Evidence: `research/Reports/RDR/RDR-003W-riskengine-weekly-diagnostic-validation.md` validates the ATE v2.2 RiskEngine v1.0.0-draft Python mirror on weekly Yahoo Finance OHLC across the same 16-asset universe as RDR-003 (Gold, Silver, Copper, NQ=F, SPY, NVDA, MSFT, AAPL, AMZN, GOOGL, TLT, IGLT.L, EURUSD, GBPUSD, USDJPY, CL=F) over 2014-01-01 to 2026-07-03 (8,355 weekly bars). Run script: `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/run_rdr003w_validation.py`. ATE v2.2 release SHA-256 `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` and v2.1 release SHA-256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` confirmed unchanged by canonical verifier (442/442 checks pass, exit 0).

Knowledge entry: **RiskEngine v1.0.0-draft is Supported as a diagnostic-only module on weekly data — a marginal improvement over daily.** All 9 weekly classification rules passed: median absolute Spearman between RiskScore and VolatilityScore 0.21 (vs daily 0.17); median absolute Spearman RiskScore vs Momentum 0.26 (vs 0.31); vs Confidence 0.41 (vs 0.43); all overlap thresholds met. **Volatility dominance count (assets with `dominant_vol_pct > 60`) dropped from 6 of 16 (daily) to 4 of 16 (weekly)**, clearing the 4-asset acceptance threshold that daily narrowly missed. Median `dominant_vol_pct` moved from 51.3% (daily) to 48.1% (weekly). Hidden directional bias remained limited (median 7.5pp weekly vs 4.5pp daily, both below the 12pp threshold); weekly bar sample is small, the modest increase reflects small-sample noise on `extreme`/`tense` weekly bars. Reserved-language audit 0/418 hits. The `RiskEngine is diagnostic-only` boundary is unchanged. **DecisionEngine integration remains deferred; ConfidenceEngine integration remains deferred; alerts remain prohibited.** Follow-up: Pine-vs-Python parity check remains the gating item before any downstream consumption; the weekly evidence corroborates daily without replacing it. RDR-003 → RDR-003W also represents the first daily+weekly dual-coverage validation pair for any ATE engine.

### EDR-001 canonical verifier extended to load ATE v2.2 release file

Evidence: `tools/scripts/verify_ate.py` was extended in 2026-07 to directly load `pine/releases/ATE_v2.2.pine` and `pine/development/ATE_Current.pine` and assert the contract recorded in `docs/releases/ATE_v2.2_Release_Manifest.md` and the approved RiskEngine v1.0 specification. Expected SHA constants `V22_EXPECTED_SHA = d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` and `V21_EXPECTED_SHA = 7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` are baked into the verifier to catch unintended release-file changes. `tests/README.md` was updated with the new release-file check scope.

Knowledge entry: The canonical verifier command remains `python tools/scripts/verify_ate.py`. Current result: 442/442 checks pass (exit 0); v2.2 release SHA matches the manifest, the dev mirror is byte-identical, and v2.1 SHA is unchanged. The release-file checks are static and scope-reserved (no Pine execution); they cover the seven approved RiskEngine inputs, the Engine Output Contract variables, the allowed state and direction literals (`calm`/`normal`/`elevated`/`tense`/`extreme`/`unknown` and `none`/`elevated`/`conflict`/`stable`/`indeterminate`), the four-component cap clamps (`f_clamp(..., 0.0, 35.0/30.0/20.0/15.0)`), the total `riskScore` clamp `[0.0, 100.0]`, the 14 approved dashboard labels, the 15 Research Mode labels, exactly 10 alertcondition titles matching ATE v2.1, no RiskEngine alert, boundary discipline (no assignment to other engines' outputs and no `strategy(...)`/broker/order/sizing/stop/entry-logic/exit-logic logic), and reserved-language absence (`safe`/`unsafe`/`suitable`/`unsuitable`/`approved`/`blocked`/`tradeable`/`untradeable`) scoped to the RiskEngine literal assignment blocks, RiskEngine dashboard cells, and Research Mode body only. Like the existing compute-path checks, this extension does NOT prove empirical usefulness and does NOT change the RiskEngine classification. RDR-003 / RDR-003W remain required for any future diagnostic-to-downstream change.

### ATE v2.2 user handbook published

Evidence: `docs/user/ATE_User_Handbook.md` was added as the plain-English user guide for reading the ATE v2.2 TradingView indicator.

Knowledge entry: ATE v2.2 is a user-facing TradingView market analysis indicator with a dashboard. VolatilityEngine and RiskEngine are user-visible on the dashboard but remain diagnostic-only. ATE does not place trades, does not connect to a broker, does not manage positions, does not guarantee profit, and does not issue financial advice. The 10 ATE alerts are Golden Cross, Death Cross, Strong Bull, Strong Bear, Bullish BOS, Bearish BOS, Momentum Bullish, Momentum Bearish, High Confidence Bull, and Low Confidence Bear. These are the only alerts produced by ATE v2.2. ConfidenceEngine does not consume VolatilityEngine or RiskEngine. The handbook is plain-English and contains no research methodology or technical implementation detail.

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
