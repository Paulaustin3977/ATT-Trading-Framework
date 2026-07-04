# ERP-001: Add Canonical ATE Verification Entry Point

Date: 2026-07-03
Status: Proposed
Owner: ChatGPT, Engineering Lead, with Hermes, Quantitative Research Department, audit support
Related ATOS Version: ATOS v1.1
Related ATE Version: ATE v2.1
Risk classification: Low to medium
Recommendation: Implement in a future ATE release, not in ATE v2.1 diagnostic VolatilityEngine release

## Context

ATE v2.1 RDR-002 verification relies on a temporary verifier artefact written under `/var/folders/0b/8y8rvw6d53q2y6gt96zb6kz00000gn/T/hermes-verify-<slug>/`. Each verification run reproduces the verifier, the fixture strategy, and the boundary handling. There is no canonical, repo-level command that future ATE checks can call.

This is acceptable for ad-hoc verification but creates three issues:

1. No repeatable entry point for future RDRs or engine re-implementations.
2. No version-controlled fixture library for diagnostic regressions.
3. No documented contract between the Pine release file, the python reproduction script, and the verifier.

The verifier result for RDR-002 is recorded as `Weakly Supported` (limited behaviour verification, not a full validation suite). A canonical entry point is required before that result can be promoted to `Supported`, before any engine is promoted from diagnostic to downstream consumer of ConfidenceEngine or RiskEngine, and before RDR-002W and future diagnostic horizons are repeated.

## Decision

Create a standard verification script under `tools/scripts/` and define a canonical verification command.

Target layout:

```
tools/scripts/verify_ate.py            # canonical verifier
tools/scripts/verify_fixtures/         # seeded OHLCV fixtures
tools/scripts/README.md                # canonical command and exit codes
```

Canonical command (proposed):

```bash
./tools/scripts/verify_ate.py
```

Exit codes:

- `0` all checks passed
- `1` behaviour or contract check failed
- `2` verifier environment error (missing dependency, fixture missing, etc.)

The canonical verifier must:

1. Load the latest ATE release Pine file from `pine/releases/ATE_vX.Y.pine`.
2. Run the matching Python reproduction script (when present).
3. Execute seeded fixture scenarios covering quiet, normal, expanding, elevated, unstable and shock regimes.
4. Verify Engine Output Contract fields, direction values, score meaning, regime classification, Research Mode labels, and the no-bullish/bearish-direction rule.
5. Write a `verify.log` next to the verifier, capturing pass count, fail count, fixture summaries, and a machine-readable JSON summary.
6. Refuse to claim suite-green success. The exit code label is `pass`, `fail`, or `environment_error`, never `green`.

The ATE v2.1 VolatilityEngine release remains diagnostic-only. The canonical verifier must not introduce live trading, broker, or paper-trading integration.

## Alternatives Considered

1. Per-RDR ad-hoc verifier only. Rejected: produces fragile, non-reproducible artefacts.
2. pytest suite under `tests/`. Deferred: more powerful but slower to set up; a focused shell-friendly verifier is sufficient for diagnostic-only validation.
3. TradingView editor only. Rejected: does not provide CI/CD-friendly verification.

## Consequences

- Future RDRs and engine release candidates can run a stable command instead of reinventing a verifier each time.
- Regression risk reduces because fixture libraries are version-controlled.
- The verifier script must be kept aligned with the latest approved Pine contract. Drift between verifier and Pine file must itself be flagged as a verification warning.
- CI/CD systems can run the canonical command against future ATE release candidates.

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Canonical verifier drifts from Pine release contract | Medium | Verifier must load the active Pine release file and parse contract values from it; fixture summaries must include a contract-diff line |
| Verifier becomes a hidden complexity layer | Medium | Keep verifier small, prefer stdlib + `pandas`/`numpy`; reject heavy testing frameworks |
| Verifier is mistaken for a full validation suite | High | Verifier must explicitly label output as ad-hoc behaviour verification, not suite green |
| Verifier accidentally enables broker/paper integration | Low | Verifier must not import or call broker APIs |

## Validation Evidence

- RDR-002 daily verifier result: 45/46 checks passed (1 verifier-side regex false-negative).
- RDR-002 weekly artefacts verifier: 44/45 checks passed (1 verifier hardcoded SHA false-negative).
- RDR-002 weekly script verifier: 19/20 structural checks passed (1 verifier over-strictness false-negative on negative-scope disclaimer).
- RDR-002 weekly behaviour verifier: 43/43 behaviour checks passed on seeded quiet, normal and shock fixtures.

All four verifier runs were ad-hoc, not suite green. None of them is a substitute for ERP-001.

## Supersedes / Superseded By

None.

## Approval

- Hermes recommendation: propose ERP-001 for implementation in a future ATE release.
- Paul Austin approval: pending.
- Approval date: pending.

Implementation is not part of the current ATE v2.1 diagnostic-only VolatilityEngine release. No ATE Pine code was modified.
