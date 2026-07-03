# Quality Manual v1.1 Draft Final Amendment Summary

Date: 2026-07-03
Status: Final draft summary for Paul Austin approval review
Document: `docs/governance/Quality_Manual.md`

## Short Amendment Summary

The Quality Manual v1.1 Draft has been updated with Product Owner / Chief Systems Architect answers to all open questions.

Final amendments incorporated:

- Product Owner approval is mandatory for promotion to Stable, not for preparing every Release Candidate.
- Major architecture, risk, or scope changes require Product Owner approval before Release Candidate status.
- A `supported` performance claim now requires:
  - clear hypothesis
  - documented data source
  - in-sample and out-of-sample testing where applicable
  - walk-forward or time-split validation where applicable
  - parameter sensitivity check
  - transaction costs where trading performance is claimed
  - benchmark comparison
  - stated limitations
  - reproducibility notes
  - no obvious lookahead, survivorship, or data-snooping issue
- Claims below that threshold must be classified as weakly supported, inconclusive, falsified, or operationally rejected.
- Release manifests now live in `docs/releases/` and link to artefacts in `pine/releases/`:
  - `docs/releases/ATE_vX.X_Release_Manifest.md`
  - `pine/releases/ATE_vX.X.pine`
- Hermes may mark releases as `Research Blocked` or `Quality Blocked` when evidence, quality, scope, or research standards are not met.
- Hermes cannot approve or reject final governance alone.
- Final release approval or override remains with Paul Austin as Product Owner.
- Product Owner overrides of Hermes blocks must be documented as waivers.
- Waiver expiry rules added:
  - Default waiver expiry: 30 days
  - Critical waiver: only by explicit Product Owner and Risk Owner approval; no hidden execution or known lookahead/repainting release waiver
  - High waiver: 14 days maximum
  - Medium waiver: 30 days default
  - Low waiver: 90 days maximum
  - No waiver is permanent

## Confirmation: Open Questions Resolved

All previous open questions have been resolved and incorporated into `docs/governance/Quality_Manual.md`.

Resolved questions:

1. Product Owner approval timing.
2. Evidence threshold for supported performance claims.
3. Release manifest location and naming structure.
4. Hermes release-blocking authority and Product Owner override rule.
5. Waiver expiry rules.

## Recommendation

Recommendation: ready for Paul Austin approval.

The document should remain `Draft for Paul Austin Review` until Paul explicitly approves and promotes it to approved governance.
