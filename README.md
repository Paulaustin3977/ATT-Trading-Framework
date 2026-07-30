# ATT Trading Framework

## Austin Trading Engine (ATE)

ATE is a Pine Script v6 market-diagnostics indicator and a local research/verification framework. The current immutable release baseline is [`pine/releases/ATE_v2.2.pine`](pine/releases/ATE_v2.2.pine). It displays explainable trend, structure, momentum, volatility, confidence, and risk diagnostics; it is not an order, execution, position-management, or trade-management system.

## Current status

| Artefact or engine | Implemented | Verified | Empirically validated | Approved |
|---|---|---|---|---|
| ATE v2.2 release baseline | Yes | Yes — canonical source checks; Paul Austin confirmed the immutable release compiled in TradingView | Engine-specific evidence varies below | Approved only as the stored diagnostic rollback/release baseline |
| Existing trend score / market state | Yes, in v2.2 | Covered by release verification | No dedicated RDR classification recorded | No downstream action authority |
| StructureEngine | Yes, in v2.2 | Covered by release verification | No dedicated RDR classification recorded | No downstream action authority |
| MomentumEngine | Yes, in v2.2 | Covered by release verification | No dedicated RDR classification recorded | No downstream action authority |
| VolatilityEngine `1.0.0-draft` | Yes, diagnostic-only | Covered by release verification | RDR-002 and RDR-002W: **Weakly Supported** | Diagnostic display/research only; downstream integration not approved |
| ConfidenceEngine | Yes, in v2.2 | Covered by release verification | No dedicated RDR classification recorded | Uses only trend score, structure, and momentum in v2.2 |
| RiskEngine `1.0.0-draft` | Yes, diagnostic-only | Covered by release verification | RDR-003 daily: **Weakly Supported**; RDR-003W weekly: **Supported** | Diagnostic display/research only; DecisionEngine and ConfidenceEngine integration remain deferred |
| DashboardEngine and Research Mode | Yes, in v2.2 | Covered by release verification | Presentation/export surfaces are not evidence of engine usefulness | Presentation only |
| DecisionEngine | No | No | No | Deferred and outside the current research-only scope |
| TrendEngine `0.2.0-spec-impl` in `pine/development/ATE_Current.pine` | Yes, development mirror only | Canonical verifier/fixtures cover the research implementation | RDR-010 re-attempt: **Mixed, instrument- and timeframe-dependent evidence** | Research/diagnostic only; not promoted to v2.2 release or coupled downstream |

These terms are intentionally distinct:

- **Implemented** means code exists in the named Pine artefact.
- **Verified** means deterministic contract, boundary, fixture, or integrity checks passed; it does not prove usefulness.
- **Validated** means an RDR evaluated empirical diagnostic behaviour and assigned an evidence classification.
- **Approved** means Paul Austin authorised the stated scope. Approval for a diagnostic baseline or research plan does not authorise downstream decisions or execution.

No TradingView compile claim is made for the development-only TrendEngine. The TradingView compile evidence applies to the immutable ATE v2.2 release baseline before the development mirror intentionally diverged.

## Diagnostic boundaries

- Daily-first research, with weekly companion studies where recorded.
- Bar-close, deterministic, non-lookahead intent.
- No broker connectivity, automated or manual order placement, paper/live execution, position sizing, stop placement, or trade management.
- No DecisionEngine or action logic is implemented or active.
- RiskEngine publishes diagnostic scores, states, directions, reasons, and component evidence. It does **not** publish `riskApproved` and does not approve or reject trades.
- The ten preserved TradingView alerts report indicator events only; none is a RiskEngine alert or an execution instruction.

## Repository map

| Path | Purpose |
|---|---|
| `pine/releases/` | Immutable Pine release baselines |
| `pine/development/` | Research/development Pine work; may intentionally differ from the release baseline |
| `specifications/ATE/` | Engine specifications and as-built diagnostic descriptions |
| `docs/` | Architecture, governance, release records, journal, and user documentation |
| `research/Reports/RDR/` | Human-readable Research Decision Records |
| `backtests/Hermes/` | Machine-readable validation artefacts and manifests |
| `tests/fixtures/` | Deterministic verifier fixtures |
| `tools/scripts/verify_ate.py` | Canonical ATE contract and behaviour verifier |

## Start here

1. Read [`docs/Project_Charter.md`](docs/Project_Charter.md) and [`docs/Architecture.md`](docs/Architecture.md) for governance and target architecture.
2. Read [`docs/releases/ATE_v2.2_Release_Manifest.md`](docs/releases/ATE_v2.2_Release_Manifest.md) with the later RDR reports and [`CHANGELOG.md`](CHANGELOG.md); the manifest records the release-time state, while later RDRs record subsequent validation.
3. Open [`pine/releases/ATE_v2.2.pine`](pine/releases/ATE_v2.2.pine) for the immutable release baseline.
4. Run `python3 tools/scripts/verify_ate.py` for the current canonical verification gate.
5. See [`ROADMAP.md`](ROADMAP.md) for remaining diagnostic research work.

## Governance and contributing

Draft ATOS material remains draft unless explicitly marked approved. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CHANGELOG.md`](CHANGELOG.md), and [`docs/knowledge/ATT_Knowledge_Base.md`](docs/knowledge/ATT_Knowledge_Base.md).

## Licence

Internal — Austin Trading Team. Not released under an open-source licence.
