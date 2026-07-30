# DecisionEngine — Deferred Scope Notice

## Status

**Deferred — not implemented, not verified, not validated, and not approved for implementation.**

DecisionEngine is outside the current ATE diagnostic/research-only scope. The immutable `pine/releases/ATE_v2.2.pine` source contains no DecisionEngine compute block, no decision output, and no action pathway. The development-only TrendEngine work does not change this status.

## Current contract

There is no active DecisionEngine input, output, threshold, state model, or Pine version. In particular:

- RiskEngine does **not** publish `riskApproved`.
- RiskEngine classifies diagnostic environment risk only; it does not approve, reject, block, qualify, or authorise a trade.
- ConfidenceEngine publishes evidence aggregation only; it does not publish permission to act.
- Existing indicator alerts describe chart conditions and do not constitute DecisionEngine output.

The previous placeholder proposal for `LONG`, `SHORT`, or `NEUTRAL` action logic is not an as-built capability and is intentionally removed from the current specification.

## Out of current scope

- Decision/action logic or trade permission.
- Long/short/no-action recommendations.
- Entries, exits, orders, broker connectivity, paper/live execution.
- Position sizing, stop placement, exposure control, or trade management.
- Consumption of RiskEngine diagnostics as an approval gate.

## Future change gate

Any future DecisionEngine proposal must begin as a separate governance and research initiative. It would require an approved specification amendment, explicit inputs/outputs and boundary rules, validation evidence, canonical verifier changes, release planning, and explicit Product Owner approval. No such proposal or approval is implied by ATE v2.2 or by this notice.
