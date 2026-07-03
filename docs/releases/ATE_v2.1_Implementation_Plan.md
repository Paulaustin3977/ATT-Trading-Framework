# ATE v2.1 Implementation Plan

Task ID: ATE-2.1-PLAN
Status: Implementation Plan — Approved VolatilityEngine Specification, Pine Code Not Yet Written
Owner: Austin Trading Team
Prepared by: Hermes
Applies to: ATE v2.1 diagnostic-only VolatilityEngine implementation planning
Governance baseline: ATOS v1.1, Architecture baseline, Engine Output Contract, Quality Manual v1.1, RDR-001, approved VolatilityEngine Specification

---

## 1. Executive Summary

ATE v2.1 will add the approved VolatilityEngine v1.0.0-draft to the current ATE Pine development script as a diagnostic-only engine.

The implementation must add volatility visibility for DashboardEngine and Research Mode without changing any existing ATE v2.0 behavioural pathway.

The VolatilityEngine may calculate and expose volatility regime diagnostics, but it must not affect:

- `confidenceScore`
- `marketState`
- `structureScore`
- `momentumScore`
- ConfidenceEngine logic
- RiskEngine logic
- DecisionEngine logic
- entry logic
- exit logic
- position sizing
- stop placement
- trade-action alerts

The implementation must preserve the approved Architecture baseline: independent engines, one-way data flow, pure functions, no silent defaults, bar-close-only decisions, DashboardEngine presentation-only, and Engine Output Contract compliance.

No Pine code is authorised by this implementation plan itself. Code may be written only after this plan is accepted for implementation work.

---

## 2. Scope

ATE v2.1 scope is limited to adding a diagnostic-only VolatilityEngine to the active development Pine script.

In scope:

- Add VolatilityEngine inputs with documented defaults and ranges.
- Calculate approved volatility measures only:
  - ATR ratio / ATR%
  - Bollinger Band width ratio
  - true-range shock flag
- Derive individual named Pine diagnostic variables.
- Map VolatilityEngine outputs to the Engine Output Contract:
  - `score`
  - `state`
  - `direction`
  - `reason`
  - `diagnostics`
  - `version`
- Display VolatilityEngine outputs on DashboardEngine.
- Include VolatilityEngine outputs in Research Mode where the current Pine structure supports it.
- Preserve all existing ATE v2.0 behaviour.
- Add regression checks proving non-interference.
- Prepare release-manifest requirements for later ATE v2.1 release candidate work.

---

## 3. Non-Scope

Out of scope for ATE v2.1 implementation:

- ConfidenceEngine consumption of VolatilityEngine output.
- RiskEngine consumption of VolatilityEngine output.
- DecisionEngine consumption of VolatilityEngine output.
- Any change to `confidenceScore`.
- Any change to `marketState`.
- Any change to `structureScore`.
- Any change to `momentumScore`.
- Any change to entry logic.
- Any change to exit logic.
- Any change to position sizing.
- Any change to stop placement.
- Any buy/sell alert creation.
- Any alert that implies trade action.
- Any bullish or bearish VolatilityEngine direction.
- Keltner Channels.
- Complex realised-volatility models.
- Asset-specific fixed threshold tables.
- Fixed absolute volatility thresholds as the primary classification method.
- Performance claims, risk-reduction claims, or downstream integration claims before RDR-001 evidence exists.

---

## 4. Files to be Changed

Expected implementation files:

| File | Action | Purpose |
|---|---|---|
| `pine/development/ATE_Current.pine` | Modify | Add diagnostic-only VolatilityEngine calculations, named diagnostics, dashboard display, and Research Mode output hooks. |
| `CHANGELOG.md` | Modify | Record ATE v2.1 implementation-plan approval and later implementation changes. |
| `docs/releases/ATE_v2.1_Implementation_Plan.md` | Create | This implementation plan. |

Possible later release-candidate files, not to be created during initial implementation unless release promotion is requested:

| File | Action | Purpose |
|---|---|---|
| `pine/releases/ATE_v2.1.pine` | Create later | Frozen release artefact copied from validated development build. |
| `docs/releases/ATE_v2.1_Release_Manifest.md` | Create later | Release manifest required before Stable promotion. |
| `research/Reports/<volatility-validation-report>.md` | Create later | RDR-001 human-readable validation report. |
| `backtests/Hermes/<run-id>/` | Create later | Validation artefacts, manifests, and machine-readable summaries if Hermes validation is run. |

Files that must not be changed for the diagnostic-only implementation unless explicitly approved:

- `pine/releases/ATE_v2.0.pine`
- Any previous release file under `pine/releases/`
- Broker/execution files, if any are later introduced
- Any code path controlling live, paper, or broker execution

---

## 5. Pine Implementation Approach

Implementation should be additive, isolated, and easy to remove.

Recommended Pine section placement in `pine/development/ATE_Current.pine`:

1. Inputs section:
   - Add VolatilityEngine input group.
   - Defaults and ranges must match the approved specification.

2. Functions section:
   - Add small helper functions only if they reduce duplication.
   - Avoid over-engineering.
   - Avoid complex object-like structures.

3. Calculations section:
   - Add a clearly delimited `VolatilityEngine` block.
   - Calculate approved measures only.
   - Publish individual named diagnostic variables.

4. Dashboard/visuals section:
   - Add dashboard rows/columns for VolatilityEngine values.
   - Dashboard must remain presentation-only.

5. Alerts section:
   - Do not add buy/sell alerts.
   - Do not wire volatility state to action alerts.
   - If any diagnostic-only alert is proposed later, it requires separate Product Owner approval because the current boundary prohibits alerts implying trade action.

The implementation must be written so that removing the VolatilityEngine block and dashboard rows returns the prior ATE v2.0 behaviour.

---

## 6. New Inputs Required

Add the following inputs using a dedicated Pine input group, for example `VolatilityEngine`.

| Input | Default | Allowed Range | Pine note |
|---|---:|---:|---|
| `atrLength` | 14 | 5–100 | `input.int()` |
| `atrBaselineLength` | 100 | 20–500 | `input.int()` |
| `bbLength` | 20 | 10–100 | `input.int()` |
| `bbStdDev` | 2.0 | 1.0–3.0 | `input.float()` |
| `bbBaselineLength` | 100 | 20–500 | `input.int()` |
| `shockLookback` | 20 | 5–100 | `input.int()` |
| `shockMultiplier` | 2.5 | 1.5–5.0 | `input.float()` |
| `compressionThreshold` | 0.75 | 0.25–1.00 | `input.float()` |
| `normalUpperThreshold` | 1.25 | 1.00–1.75 | `input.float()` |
| `elevatedThreshold` | 1.75 | 1.25–3.00 | `input.float()` |
| `unstableThreshold` | 2.50 | 1.75–5.00 | `input.float()` |
| `slopeLookback` | 5 | 2–20 | `input.int()` |

Implementation constraint:

- Pine `input.*()` `maxval` and `minval` values must be literal constants.
- Do not make one input's range depend on another input.
- Document every default in comments or adjacent spec reference.

---

## 7. New VolatilityEngine Variables

Implement individual named variables rather than a complex object.

Required calculation variables:

- `volAtr`
- `volAtrPercent`
- `volAtrBaseline`
- `volAtrRatio`
- `volBbBasis`
- `volBbDev`
- `volBbUpper`
- `volBbLower`
- `volBbWidthRaw`
- `volBbWidthBaseline`
- `volBbWidthRatio`
- `volCombinedRatio`
- `volSlope`
- `volTrueRange`
- `volTrueRangeBaseline`
- `volShockFlag`
- `volInsufficientData`

Required contract variables:

- `volScore`
- `volState`
- `volDirection`
- `volReason`
- `volVersion`

Required diagnostic variables:

- `volDiagAtrPercent`
- `volDiagAtrRatio`
- `volDiagBbWidthRatio`
- `volDiagCombinedRatio`
- `volDiagSlope`
- `volDiagShockFlag`
- `volDiagMissingAtrRatio`
- `volDiagMissingBbRatio`
- `volDiagInsufficientData`

Naming rule:

- Use a clear `vol` or `volDiag` prefix so no existing engine variable is shadowed or overwritten.

---

## 8. Engine Output Contract Mapping in Pine

| Contract field | Pine variable | Allowed values / type | Notes |
|---|---|---|---|
| `score` | `volScore` | numeric 0–100 or `na` for unknown | Means volatility regime usefulness / condition quality only. |
| `state` | `volState` | `compressed`, `normal`, `expanding`, `elevated`, `unstable`, `shock`, `unknown` | Must follow deterministic state table. |
| `direction` | `volDirection` | `none`, `expanding`, `contracting`, `stable`, `unstable` | Must never be bullish/bearish. |
| `reason` | `volReason` | string | Short deterministic explanation. |
| `diagnostics` | individual `volDiag*` variables | numeric/bool/string values | No complex object; use individual named variables. |
| `version` | `volVersion` | `1.0.0-draft` | Must match approved specification target. |

The implementation must not map VolatilityEngine values into existing non-volatility variables such as:

- `confidenceScore`
- `marketState`
- `structureScore`
- `momentumScore`

---

## 9. Dashboard Changes

Dashboard changes may add a VolatilityEngine display area with the following fields:

- Volatility score
- Volatility state
- Volatility direction
- Volatility reason
- ATR ratio
- ATR%
- BB width ratio
- Combined volatility ratio
- Shock flag
- Volatility slope
- VolatilityEngine version

Dashboard rules:

- DashboardEngine must be presentation-only.
- DashboardEngine may display VolatilityEngine values but must not reinterpret them.
- DashboardEngine must not normalise, smooth, overwrite, or mutate VolatilityEngine values.
- Display formatting is allowed only if clearly presentation-only.
- Dashboard labels must not imply trade action.
- Do not display volatility as bullish/bearish.
- Do not use green/red in a way that implies buy/sell unless explicitly labelled as condition quality only.

---

## 10. Research Mode Changes

Research Mode may expose or log the following fields where Pine and the existing project structure support it:

- bar date / timestamp
- symbol
- timeframe
- VolatilityEngine version
- `volScore`
- `volState`
- `volDirection`
- `volReason`
- `volAtrPercent`
- `volAtrRatio`
- `volBbWidthRatio`
- `volCombinedRatio`
- `volSlope`
- `volShockFlag`
- input settings used
- missing/invalid data flags

Research Mode rules:

- Research Mode output is diagnostic evidence only.
- Research Mode must not trigger entries, exits, stops, sizing, or alerts.
- Research Mode output must support later RDR-001 validation artefacts.
- If Pine cannot export all fields directly, the implementation should at minimum expose values visually/table-style and document the limitation for Hermes validation.

---

## 11. Alert Policy

ATE v2.1 VolatilityEngine must not create buy/sell alerts.

It must not create alerts that imply:

- enter long
- enter short
- exit
- reduce/increase position
- move stop
- trade now
- trade approved
- risk approved
- confidence confirmed

Existing alert behaviour must remain unchanged.

If diagnostic-only volatility alerts are later desired, they require separate Product Owner approval and must be labelled as diagnostic-only. They are not included in this plan.

---

## 12. Regression Checks

Regression checks must prove non-interference.

Required checks after implementation:

1. Diff review:
   - Confirm changes are limited to VolatilityEngine diagnostics, dashboard display, Research Mode hooks, and docs.

2. Variable isolation:
   - Search for writes to `confidenceScore`, `marketState`, `structureScore`, and `momentumScore`.
   - Confirm VolatilityEngine variables are not used in their calculations.

3. Entry/exit isolation:
   - Search for `strategy.entry`, `strategy.exit`, entry booleans, exit booleans, and alert conditions.
   - Confirm no VolatilityEngine variable participates in trade-action logic.

4. Alert isolation:
   - Search for `alertcondition` and `alert()`.
   - Confirm no new buy/sell or trade-action alert was added.

5. Direction isolation:
   - Confirm `volDirection` never returns `bullish` or `bearish`.

6. Engine Output Contract:
   - Confirm all required fields have Pine variables.

7. Dashboard presentation-only:
   - Confirm table/display code reads VolatilityEngine values but does not mutate them.

8. No release overwrite:
   - Confirm `pine/releases/ATE_v2.0.pine` was not edited.

Suggested commands:

```bash
git diff --check -- pine/development/ATE_Current.pine CHANGELOG.md docs/releases/ATE_v2.1_Implementation_Plan.md

git diff -- pine/development/ATE_Current.pine

grep -n "confidenceScore\|marketState\|structureScore\|momentumScore\|strategy.entry\|strategy.exit\|alertcondition\|alert(" pine/development/ATE_Current.pine
```

Use `grep` manually or equivalent repository search tooling. The final validation note must record what was found.

---

## 13. Manual TradingView Validation Checklist

Before any release candidate:

- [ ] Paste updated `pine/development/ATE_Current.pine` into TradingView Pine Editor.
- [ ] Confirm Pine Script v6 compile succeeds.
- [ ] Confirm no new compile warnings suggest future-data, repainting, or invalid inputs.
- [ ] Confirm VolatilityEngine dashboard fields display.
- [ ] Confirm `volState` displays only approved states.
- [ ] Confirm `volDirection` displays only approved direction values.
- [ ] Confirm `volDirection` never displays bullish/bearish.
- [ ] Confirm score is numeric 0–100 or `na`/unknown handling behaves as documented.
- [ ] Confirm insufficient-history bars show `unknown`/missing diagnostics rather than silent defaults.
- [ ] Confirm existing dashboard fields remain present.
- [ ] Confirm existing ATE v2.0 behaviour is unchanged except added volatility visibility.
- [ ] Confirm no new buy/sell alerts were added.
- [ ] Confirm existing alerts, if any, are unchanged.
- [ ] Confirm no entry/exit markers appear because of VolatilityEngine.
- [ ] Record screenshots or notes for validation evidence.

TradingView editor reminder:

- After editing local Pine, TradingView may still show the old cached script until the file is re-pasted into the editor.
- Refresh by copying the updated `.pine` file and replacing the full editor contents.

---

## 14. Hermes Validation Requirements After Implementation

Hermes validation must occur after Pine implementation and before any non-diagnostic promotion.

Required Hermes validation:

- Review implementation against approved VolatilityEngine Specification.
- Confirm Engine Output Contract compliance.
- Confirm no downstream consumption by ConfidenceEngine, RiskEngine, or DecisionEngine.
- Confirm no entry/exit/position/stop/alert impact.
- Confirm no bullish/bearish VolatilityEngine direction.
- Confirm only approved measures are used.
- Confirm defaults and input ranges match the specification.
- Confirm diagnostics are individual named variables.
- Confirm DashboardEngine remains presentation-only.
- Confirm Research Mode output is diagnostic-only.
- Confirm no released file was edited in place.

RDR-001 validation should later test the balanced daily universe:

- Gold
- Silver
- Nasdaq / major equities
- S&P 500
- Treasury / gilt proxy
- Major FX pairs

Validation output should include:

- human-readable report under `research/Reports/`
- machine-readable summary using the approved schema
- run manifest with schema version and data lineage
- negative/inconclusive result capture
- classification: supported, weakly supported, inconclusive, falsified, or operationally rejected

No claim about drawdown control, false-signal filtering, confidence reliability, or risk improvement may be made until RDR-001 evidence supports it.

---

## 15. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| VolatilityEngine accidentally affects confidence/risk/decision logic | High | Use strict variable isolation; regression search for downstream consumption; code review before release. |
| Volatility direction is confused with price direction | High | Use only `none`, `expanding`, `contracting`, `stable`, `unstable`; label dashboard as volatility direction. |
| Dashboard colours imply buy/sell action | Medium | Use neutral labels and avoid bullish/bearish colour semantics. |
| Too many inputs create parameter clutter | Medium | Use only approved inputs; do not add optional models. |
| Fixed absolute thresholds reduce cross-asset reliability | Medium | Use ATR and BB width versus each asset's own baseline. |
| Insufficient-history values silently default to normal | High | Explicit `unknown` state and missing-data diagnostics. |
| Pine diagnostic implementation becomes complex object-like logic | Medium | Use individual named diagnostic variables. |
| Existing ATE v2.0 behaviour changes unintentionally | High | Compare diff; verify no changes to existing behaviour variables or action logic. |
| Release file edited in place | High | Modify only development file until release candidate copy is explicitly approved. |
| Research Mode limitations prevent full export | Medium | Document limitations; expose fields visually/table-style at minimum; use Hermes validation notes. |

---

## 16. Acceptance Criteria

This implementation plan is acceptable if it:

- Preserves diagnostic-only scope.
- Identifies exact files expected to change.
- Defines Pine implementation approach without writing Pine code.
- Defines new inputs and variables.
- Maps Pine variables to the Engine Output Contract.
- Defines dashboard and Research Mode changes.
- Prohibits trade-action alerts.
- Defines regression checks for non-interference.
- Defines manual TradingView validation.
- Defines Hermes validation requirements.
- Defines risks and mitigations.
- Defines rollback and release-manifest requirements.

The later Pine implementation is acceptable only if:

- It compiles in Pine Script v6.
- It uses only approved measures.
- It exposes all required Engine Output Contract fields.
- It uses individual named diagnostic variables.
- It never outputs bullish/bearish VolatilityEngine direction.
- It does not affect `confidenceScore`, `marketState`, `structureScore`, or `momentumScore`.
- It does not affect entry logic, exit logic, position sizing, stop placement, or trade-action alerts.
- It changes existing ATE v2.0 behaviour only by adding diagnostic volatility visibility.
- It passes manual TradingView validation.
- It passes Hermes review against this plan and the approved specification.

---

## 17. Rollback Plan

Rollback must be simple because the feature is additive and diagnostic-only.

Rollback steps:

1. Revert the implementation commit touching `pine/development/ATE_Current.pine`.
2. Confirm VolatilityEngine dashboard rows are removed.
3. Confirm Research Mode volatility fields are removed or disabled.
4. Confirm `confidenceScore`, `marketState`, `structureScore`, and `momentumScore` match the pre-v2.1 development baseline.
5. Confirm no release files were edited in place.
6. Record rollback reason in `CHANGELOG.md` if implementation had already been documented.
7. If a release candidate had been created, do not overwrite it; create a superseding candidate or mark the candidate rejected.

Suggested command for a not-yet-pushed implementation commit:

```bash
git revert <implementation_commit_sha>
```

For local uncommitted implementation work:

```bash
git checkout -- pine/development/ATE_Current.pine
```

Use the second command only when intentionally discarding uncommitted local implementation work.

---

## 18. Release Manifest Requirements

Before ATE v2.1 can become a release candidate or stable release, create:

- `docs/releases/ATE_v2.1_Release_Manifest.md`
- `pine/releases/ATE_v2.1.pine`

The release manifest must include:

- Version: ATE v2.1
- Release file path: `pine/releases/ATE_v2.1.pine`
- Manifest path: `docs/releases/ATE_v2.1_Release_Manifest.md`
- Source development file: `pine/development/ATE_Current.pine`
- Commit hash
- Changed files
- Affected specification: `specifications/ATE/VolatilityEngine.md`
- Implementation plan: `docs/releases/ATE_v2.1_Implementation_Plan.md`
- Validation artefacts
- Manual TradingView validation notes
- Regression evidence
- Known issues
- Rollback path
- Approval status
- Waivers, if any
- Confirmation that ATE v2.0 release file remains preserved
- Confirmation that VolatilityEngine remains diagnostic-only
- Confirmation that downstream consumption remains prohibited in ATE v2.1

No unstable, experimental, or partially validated feature should enter a stable release.

---

## 19. Open Questions for Paul Austin

No blocking Product Owner questions remain for implementation planning.

Implementation-level questions to resolve during or after Pine implementation:

1. Dashboard layout preference:
   - Add a compact Volatility row, or a dedicated Volatility panel/table area?

2. Research Mode mechanism:
   - Should Research Mode be table/display-only in Pine initially, or should a specific export workflow be defined later?

3. Dashboard colour policy:
   - Should condition quality use neutral colours only, or allow non-trade colours for normal/elevated/shock states?

4. Release timing:
   - Should ATE v2.1 remain a development build until RDR-001 daily validation completes, or can it become a Release Candidate after compile/manual regression checks while retaining diagnostic-only status?

5. Validation universe symbols:
   - Which exact TradingView symbols should represent Gold, Silver, Nasdaq/major equities, S&P 500, Treasury/gilt proxy, and major FX pairs?

---

## 20. Recommendation

Recommendation: Approve this implementation plan and proceed to diagnostic-only Pine implementation as a separate task.

Implementation should be narrow and additive:

- Modify only `pine/development/ATE_Current.pine` for code.
- Preserve all existing ATE v2.0 behaviour.
- Add VolatilityEngine diagnostic variables and dashboard/Research Mode visibility only.
- Do not wire VolatilityEngine into confidence, risk, decisions, entries, exits, sizing, stops, or trade-action alerts.
- Perform regression and manual TradingView validation before any release-candidate work.

This plan does not authorise Pine implementation by itself; it defines the controlled path for the next implementation task.
