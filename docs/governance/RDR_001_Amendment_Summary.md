# RDR-001 Final Amendment Summary

Date: 2026-07-03
Status: Approved ATOS v1.1 Governance Baseline
Owner: Hermes, Quantitative Research Department
Approval: Paul Austin

## Summary

RDR-001 research storage and reporting standards have been updated with Paul Austin / Chief Systems Architect answers and approved as part of the ATOS v1.1 governance baseline.

## Amendments Applied

1. RDR-001 standards are approved for ATOS v1.1 governance. Future folder, schema, or reporting changes must be versioned and documented.
2. The core research summary CSV schema is locked. Hermes may add columns only at the end, and new columns must be documented in the run manifest. Breaking schema changes require a new schema version.
3. Schema version files are maintained:
   - `docs/templates/Research_Summary_Table_Template_v1.csv`
   - `docs/templates/Research_Summary_Table_Template_v2.csv`
   - `docs/templates/Research_Summary_Table_Template_CURRENT.csv`
4. Every research run manifest must record the schema version used.
5. Tier A asset qualification now has initial trade-count thresholds:
   - Daily: minimum 30 trades per asset, or 100+ trades across the tested universe.
   - Weekly: minimum 8 trades per asset, or 30+ trades across the tested universe.
   - Monthly / long-horizon: no fixed minimum, but must be marked Low Statistical Confidence unless supported by long history and cross-asset confirmation.
6. `data/raw/` should remain mostly untracked in Git. Commit manifests, not large raw datasets. Commit small sample datasets only when needed for reproducibility tests. Large raw data should be stored externally or locally and referenced by manifest.
7. Manifests now require data source, download date, symbol, timeframe, date range, adjustments, transformations, storage location, checksum if available, and known limitations.

## Open Questions

All previous RDR-001 open questions are resolved.

## Recommendation

Ready for active use as the approved ATOS v1.1 research storage and reporting governance baseline.

## Research Integrity Statement

This amendment governs research storage and reporting only. It does not authorise live trading, broker connectivity, paper-trading APIs, autonomous execution, or broker credential handling. Hermes may recommend; Paul Austin approves final governance and release decisions.
