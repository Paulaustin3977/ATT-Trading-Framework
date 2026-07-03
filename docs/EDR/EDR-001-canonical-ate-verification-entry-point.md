# EDR-001 — Canonical ATE Verification Entry Point

Date: 2026-07-03
Status: Accepted
Owner: ChatGPT, Engineering Lead, with Hermes, Quantitative Research Department, audit support
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Related Proposals: ERP-001 (proposed, now implemented as EDR-001)

## Decision

Adopt a canonical, repository-level ATE verification entry point.

The canonical verifier is:

```bash
python tools/scripts/verify_ate.py
```

It runs against `pine/releases/ATE_v2.1.pine` (the active ATE release file) and uses seeded fixtures stored under `tests/fixtures/ATE_v2_1/`.

## Reason

RDR-002 (daily) and RDR-002W (weekly) both ran ad-hoc verifier artefacts under `/var/folders/0b/8y8rvw6d53q2y6gt96zb6kz00000gn/T/hermes-verify-<slug>/`. This produced three issues:

1. No repeatable entry point for future RDRs or engine release candidates.
2. No version-controlled fixture library for diagnostic regression coverage.
3. No documented contract between the Pine release file, the Python reproduction script, and the verifier.

VolatilityEngine remains Weakly Supported (RDR-002 / RDR-002W). The blocker on promotion to Supported is structural rather than empirical: there is no canonical command that future ATE checks can run.

## Alternatives Considered

1. **Per-RDR ad-hoc verifier only.** Rejected — does not satisfy repeatability, CI/CD, or future ATE-release needs.
2. **Full pytest suite.** Deferred — heavier than necessary for the current scope of ATE validation; can be added incrementally later.
3. **TradingView editor only.** Rejected — no CI/CD-friendly verification.

## Consequences

- Future ATE release candidates can be verified by running `python tools/scripts/verify_ate.py` and inspecting `tools/scripts/verify.log`.
- All future diagnostic horizon RDRs (daily, weekly, intraday, etc.) can re-use the same fixtures and the same script under separate output directories.
- The verifier is bounded to behaviour and contract checks; it does not claim suite-green validation, performance, or trading advantage.
- The verifier is reproducible by other contributors. `tools/scripts/verify.log` is generated from the same source every run.
- Future ATE re-implementations can run the same verifier against a new Pine release file to detect contract regressions.

## Limitations

- The verifier is narrow. It does not replace the full unit-test foundation that a mature codebase eventually needs.
- The verifier's behavioural checks are based on three deterministic fixtures. They are not a substitute for multi-asset universe testing (covered by RDR-002 and future RDRs).
- The verifier depends on the daily reproduction script `backtests/Hermes/ATE_v2.1/Daily/Diagnostic_Validation/RDR-002/run_rdr002_validation.py` for the compute path. That script is a research port, not a Pine-equivalent reference.
- The verifier stubs out `yfinance` and `matplotlib` because it does not download market data or render charts. Future verifier enhancements that need real data must re-introduce those dependencies explicitly.
- Exit 0 means "pass on the current contract expectations". It does NOT mean:
  - the engine is approved for downstream consumers (RiskEngine, ConfidenceEngine),
  - the engine's thresholds are optimal,
  - the engine has demonstrated trading performance or risk improvement,
  - the engine is correct on assets, timeframes, or regimes not covered by the fixtures.

## Future Improvements

- Add more fixture regimes (`elevated`, `unstable`, `expanding`).
- Add intraday (e.g. 4H) fixtures.
- Add a second verifier mode that checks scoring logic determinism against reference values for each of the seven `VolatilityState` values.
- Add a CI hook that runs the verifier on every PR that touches `pine/releases/ATE_v*.pine`.
- Promote into a full `pytest` test suite when the engine surface stabilises.

## Supersedes / Superseded By

- EDR-001 implements ERP-001 (proposed). ERP-001 is effectively superseded by EDR-001 but retained as a research-proposal trail in `docs/EDR/ERP-001-canonical-ate-verification-entry-point.md`.

## Approval

- ChatGPT, Engineering Lead, drafted and implemented.
- Hermes, Quantitative Research Department, audited.
- Paul Austin approval: pending.
- Implementation date: 2026-07-03.

## Verifier Result

At acceptance time the verifier returned exit code `0` with `100/100` checks passing on the ATE v2.1 release file (`pine/releases/ATE_v2.1.pine`, SHA256 `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893`).

This verifier result is NOT:

- a reclassification of the VolatilityEngine research evidence,
- a promotion of VolatilityEngine from Weakly Supported to Supported,
- an authorisation of downstream consumption by ConfidenceEngine or RiskEngine.

It is only acceptance that the verifier infrastructure itself is in place and operational against the ATE v2.1 release.

## Side Note on a Real Project Finding

The verifier confirmed that the ATE v2.1 release exposes VolatilityEngine diagnostics as named variables in the `vol*` namespace (e.g. `volAtrPercent`, `volAtrRatio`, `volCombinedRatio`, `volShockFlag`), not under a separate `volDiag*` namespace as the formal VolatilityEngine specification text describes. Both satisfy the requirement to expose diagnostics as individual named variables, but the prefix differs. This is recorded here as a finding for a future specification amendment; it is not a blocker for EDR-001 acceptance.

## Files Created / Modified

Created:

- `tools/scripts/verify_ate.py`
- `tools/scripts/verify.log` (regenerated on every run)
- `tests/fixtures/ATE_v2_1/quiet.csv`
- `tests/fixtures/ATE_v2_1/normal.csv`
- `tests/fixtures/ATE_v2_1/shock.csv`
- `tests/fixtures/ATE_v2_1/fixture_spec.json`
- `tests/README.md`
- `docs/EDR/EDR-001-canonical-ate-verification-entry-point.md` (this document)

Modified:

- `CHANGELOG.md`
- `docs/knowledge/ATT_Knowledge_Base.md`

Not modified (per task boundary):

- `pine/releases/ATE_v2.1.pine`
- `pine/development/ATE_Current.pine`
