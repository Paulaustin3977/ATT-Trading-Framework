# Quality Manual v1.1 Draft Amendment Summary

Date: 2026-07-03
Status: Draft summary for Paul Austin review
Document: `docs/governance/Quality_Manual.md`

## Short Amendment Summary

The Quality Manual has been revised into a practical v1.1 draft for a small AI-assisted engineering team.

Key amendments:

- Defined six work significance levels:
  - Minor documentation/cosmetic change
  - Small bug fix
  - Engine change
  - Research claim
  - Architecture change
  - Release candidate
- Added a mandatory/optional gate matrix so not all gates apply to all changes.
- Added new gates:
  - Data Quality Gate
  - Security and Scope Gate
  - Regression Evidence Gate
  - Decision Record Gate
  - Waiver / Exception Gate
  - Release Manifest Gate
  - Knowledge Capture Gate
- Strengthened Research Validation for performance claims with controls for:
  - overfitting
  - data snooping
  - lookahead
  - survivorship bias
  - parameter stability
  - benchmark comparison
  - regime dependence
  - transaction costs where relevant
- Added release manifest requirements:
  - version
  - release file path
  - commit hash
  - changed files
  - validation artefacts
  - known issues
  - rollback path
  - approval status
- Defined mandatory triggers for EDRs and RDRs.
- Added promotion criteria for Experimental, Laboratory, Validation Candidate, Release Candidate, Stable, Deprecated, and Rejected classifications.
- Added waiver rules covering owner, reason, severity, expiry date, risk accepted, mitigation, and approval authority.
- Added post-release incident handling covering severity, owner, response expectation, rollback rule, and prevention update.
- Preserved lean operation by using proportional gate application rather than applying every gate to every change.

## Open Questions for Paul Austin

1. Should Product Owner approval be mandatory for every Release Candidate, or only for stable releases?
2. What is the minimum acceptable evidence threshold for a performance claim to be called "supported" rather than "weakly supported"?
3. Should release manifests live in a dedicated `releases/` documentation folder, or beside each release artefact?
4. Should Hermes be allowed to mark a release as blocked, or only recommend blocking to Paul Austin?
5. How long should waivers remain valid by default before expiry review?

## Recommendation

Recommendation: approve with amendments after Paul Austin review.

The revised draft is materially stronger and practical enough to use as ATOS v1.1 quality governance, but it should not be promoted to approved status until Paul Austin reviews the open questions and explicitly approves the document.
