# Data Management Policy

Status: Draft ATOS v1.1 governance document

## Purpose

Protects the integrity, lineage and reproducibility of market data and research artefacts.

## Requirements

- Record data source, instrument, timeframe and date range for each research run.
- Record transformations, filters and missing-data handling.
- Preserve enough metadata to reproduce the run.
- Flag known limitations: survivorship bias, proxy mismatch, missing sessions, adjusted/unadjusted prices and regime changes.
- Do not mix datasets without documenting the merge logic.

## Reproducibility Manifest

Each major research artefact should include:

- Commit hash.
- Tool/script version.
- Data source.
- Parameters.
- Date/time of run.
- Output artefact path.
- Known limitations.
