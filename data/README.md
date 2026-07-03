# Austin Trading Data Folder

This folder stores research data inputs and reproducibility manifests.

## Structure

```text
data/
├── raw/
├── processed/
├── manifests/
└── README.md
```

## Rules

- `raw/` contains source data or source-native exports.
- `processed/` contains transformed data used by backtests.
- `manifests/` contains data and research-run manifests.
- Data source, date range, timeframe, transformations, missing-data handling, and limitations must be documented.
- Do not commit sensitive credentials or broker/execution data.
- Do not mix live or paper-trading execution data into this project under the current ATOS no-execution boundary.

## Raw data Git policy

`data/raw/` should remain mostly untracked in Git.

Rules:

- Commit manifests, not large raw datasets.
- Commit small sample datasets only when needed for reproducibility tests.
- Store large raw data externally or locally and reference it by manifest.
- Manifests must record data source, download date, symbol, timeframe, date range, adjustments, transformations, storage location, checksum if available, and known limitations.
