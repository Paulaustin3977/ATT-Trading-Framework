# Research Storage Standard

Task ID: RDR-001
Version: 1.0
Status: Approved ATOS v1.1 Governance Baseline
Owner: Hermes, Quantitative Research Department
Applies To: Austin Trading research, backtests, validation runs, asset qualification, version comparisons, and negative findings.

Approval: Paul Austin approved this RDR-001 standard as part of the ATOS v1.1 governance baseline after final amendment application.

---

# 1. Purpose

This standard defines how Austin Trading research artefacts are stored, named, viewed, compared, retained, governed by retention policy, and referenced over a 5-10 year project horizon.

It exists to prevent:

- Research debt.
- Duplicated testing.
- Lost negative results.
- Inconsistent reporting.
- Untraceable backtests.
- Difficulty comparing one ATE version against another.

---

# 2. Core Principles

1. Human-readable and machine-readable outputs are both required.
2. Every material run has a manifest.
3. Reports must separate evidence, interpretation, recommendation, and decision.
4. Negative and failed results are preserved when useful.
5. Folder structure must be stable enough for automation.
6. Raw data, processed data, results, and decisions must not be confused.
7. ATE version, timeframe, asset class, direction mode, and test type must be visible in paths or metadata.
8. Do not make the process too bureaucratic for a small AI-assisted team.

---

# 3. Canonical Folder Structure

```text
research/
├── Reports/
│   ├── README.md
│   ├── RDR/
│   ├── Asset_Qualification/
│   │   ├── Gold/
│   │   ├── Silver/
│   │   ├── Equities/
│   │   ├── FX/
│   │   ├── Bonds/
│   │   └── Commodities/
│   ├── Version_Comparisons/
│   ├── Market_DNA/
│   └── Negative_Findings/
│
backtests/
├── Hermes/
│   ├── README.md
│   ├── ATE_v2.0/
│   │   ├── Daily/
│   │   ├── Weekly/
│   │   ├── Long_Only/
│   │   ├── Long_Short/
│   │   ├── Asset_Qualification/
│   │   └── Version_Comparison/
│   ├── ATE_v2.1/
│   └── Archive/
│
data/
├── raw/
├── processed/
├── manifests/
└── README.md
```

This is the approved baseline. Any future folder, schema, or reporting change must be versioned and documented.

---

# 4. Artefact Types

| Artefact | Required format | Optional format | Primary location | Purpose |
|---|---|---|---|---|
| Human-readable report | Markdown `.md` | PDF `.pdf` | `research/Reports/` | Human review and decision support |
| Machine-readable summary | CSV `.csv` | JSON `.json` | `backtests/Hermes/<ATE_VERSION>/...` | Aggregation, comparison, filtering |
| Run manifest | Markdown `.md` or YAML-like Markdown | JSON `.json` | `data/manifests/` or run folder | Reproducibility |
| Raw data | Source-native / CSV / Parquet | compressed archive | `data/raw/` | Immutable source capture |
| Processed data | CSV / Parquet | Feather | `data/processed/` | Backtest input |
| Chart/image | PNG `.png` | SVG `.svg`, PDF | report-adjacent `charts/` | Visual interpretation |
| RDR | Markdown `.md` | none | `research/Reports/RDR/` | Research decision trace |
| Version comparison | Markdown + CSV | JSON | `research/Reports/Version_Comparisons/` | ATE version evaluation |
| Asset qualification | Markdown + CSV | JSON | `research/Reports/Asset_Qualification/<class>/` | Asset suitability grading |
| Negative finding | Markdown + manifest + CSV row | JSON | `research/Reports/Negative_Findings/` | Preserve failed or rejected results |

---

# 5. Naming Conventions

## 5.1 Run ID

Canonical run ID:

`RUN-YYYYMMDD-ATE_vX.X-<TIMEFRAME>-<TESTTYPE>-<SHORTDESC>`

Examples:

- `RUN-20260703-ATE_v2.0-Daily-Backtest-GoldTrend`
- `RUN-20260703-ATE_v2.1-Weekly-VersionComparison-v2_0_vs_v2_1`
- `RUN-20260703-ATE_v2.0-Daily-AssetQualification-GoldSilverFX`

Run IDs must be filesystem-safe and stable.

## 5.2 Human Report

`<RUN_ID>_Report.md`

## 5.3 Summary CSV

`<RUN_ID>_Summary.csv`

## 5.4 Manifest

`<RUN_ID>_Manifest.md`

## 5.5 Charts

`<RUN_ID>_<chart-name>.png`

## 5.6 RDR

`RDR-0001_short-kebab-title.md`

---

# 6. Backtest Run Folder Pattern

For a material Hermes backtest run:

```text
backtests/Hermes/ATE_vX.X/<Timeframe>/<Test_Type>/<RUN_ID>/
├── <RUN_ID>_Summary.csv
├── <RUN_ID>_Manifest.md
├── <RUN_ID>_Aggregate.json        # optional but recommended
├── charts/
│   └── <RUN_ID>_equity_curve.png
└── tables/
    └── <RUN_ID>_asset_results.csv
```

The corresponding human report is stored under `research/Reports/` and links back to the run folder.

---

# 7. Report Folder Pattern

Human-readable reports should be stored by decision context:

```text
research/Reports/Asset_Qualification/<Asset_Class>/<RUN_ID>_Report.md
research/Reports/Version_Comparisons/<RUN_ID>_Report.md
research/Reports/Market_DNA/<RUN_ID>_Report.md
research/Reports/Negative_Findings/<RUN_ID>_Report.md
research/Reports/RDR/RDR-0001_short-kebab-title.md
```

If a report spans multiple contexts, store it under the primary decision context and link it elsewhere from README or index files.

---

# 8. Data Storage Rules

## Raw data

Store in:

`data/raw/<source>/<asset_class>/<symbol>/<timeframe>/`

Raw data should be immutable. If corrected data is downloaded, save it as a new dated copy or document replacement in the manifest.

`data/raw/` should remain mostly untracked in Git. Commit manifests, not large raw datasets. Commit small sample datasets only when needed for reproducibility tests. Large raw data should be stored externally or locally and referenced by manifest.

## Processed data

Store in:

`data/processed/<source>/<asset_class>/<symbol>/<timeframe>/`

Processed data must document:

- Source.
- Transformations.
- Missing-data handling.
- Adjusted/unadjusted status.
- Timezone and session assumptions.
- Date range.

## Data manifests

Store in:

`data/manifests/`

Every material run must link to a manifest or embed manifest details.

Manifests must record:

- Data source.
- Download date.
- Symbol.
- Timeframe.
- Date range.
- Adjustments.
- Transformations.
- Storage location.
- Checksum if available.
- Known limitations.
- Research summary CSV schema version used.

---

# 9. Required Metadata

Every material run must record:

- `run_id`
- `date`
- `researcher`
- `atos_version`
- `ate_version`
- `strategy_version`
- `engine_version` where applicable
- `timeframe`
- `direction_mode`
- `test_type`
- `asset_universe`
- `data_source`
- `start_date`
- `end_date`
- `parameters`
- `git_commit_hash`
- `report_path`
- `manifest_path`
- `summary_csv_path`
- `classification`
- `recommendation`

---

# 10. Human Viewing Standard

Every major report should start with a dashboard block:

```text
ATE Version:
Test Type:
Universe:
Timeframe:
Direction:
Classification:
Recommendation:
```

Then include:

- Core Metrics Table.
- Asset Ranking Table.
- Findings.
- Decision.
- Artefact links.

This lets Paul Austin, ChatGPT, Hermes, and future agents assess the result quickly before reading details.

---

# 11. Machine-Readable Standard

Every material run must produce a CSV summary using the current locked schema:

`docs/templates/Research_Summary_Table_Template_CURRENT.csv`

The core schema is locked. Hermes may add new columns only at the end of the CSV. New columns must be documented in the run manifest. Breaking schema changes require a new schema version.

Preserved schema templates:

- `docs/templates/Research_Summary_Table_Template_v1.csv`
- `docs/templates/Research_Summary_Table_Template_v2.csv`
- `docs/templates/Research_Summary_Table_Template_CURRENT.csv`

Rules:

- One row per asset/symbol/test slice where practical.
- Include aggregate rows only if `symbol=ALL` and `asset_class=Aggregate`.
- Use blank fields for not-applicable values; do not invent zeros.
- Numeric fields should be raw decimals unless the column name states otherwise.
- Path fields must be repository-relative.
- `classification` must use approved Quality Manual values.
- `recommendation` must use `Promote`, `Modify`, `Retest`, or `Reject`.

---

# 12. Retention Rules

Keep permanently:

- RDRs.
- Stable release validation reports.
- Version comparison reports.
- Asset qualification reports.
- Negative findings that affect future research.
- Manifests for material runs.
- Machine-readable summaries used for decisions.

Archive but do not delete:

- Superseded reports.
- Failed runs that revealed a process/data/engine issue.
- Deprecated asset or parameter-family reports.

Temporary scratch data can be deleted if:

- It has no decision impact.
- It is not referenced by a report/RDR.
- It can be regenerated.

---

# 13. Future Automation Requirements

The structure must support future tools that can:

- Aggregate all summary CSV files.
- Compare ATE versions.
- Rank assets by suitability.
- Detect repeated negative findings.
- Generate dashboards.
- Trace decisions back to raw evidence.

Therefore:

- Do not rename historical run IDs.
- Do not move reports without updating references.
- Keep CSV headers stable once approved.
- Add new columns only to the end of the CSV.
- Document new columns in the run manifest.
- Preserve old schema templates as separate versioned files.
- Record the schema version used in every manifest.
- Use `Research_Summary_Table_Template_CURRENT.csv` as the active pointer.

---

# 14. Lean Operation Rule

For small changes, use the minimum artefact set.

| Work type | Minimum artefacts |
|---|---|
| Quick exploratory note | Short note or manifest if material |
| Backtest with no decision impact | Report + summary CSV + manifest |
| Performance claim | Report + summary CSV + manifest + bias controls |
| Asset qualification | Asset qualification report + summary CSV + manifest |
| Version comparison | Version comparison report + summary CSV + manifest |
| Accepted/rejected research decision | RDR + linked evidence |
| Stable release validation | Report + summary CSV + manifest + release manifest + RDR where decision-impacting |

---

# 15. Integrity Rules

- Never overwrite a released result in place.
- Never delete negative findings that influenced a decision.
- Never report in-sample performance as the headline decision metric.
- Never mix live/paper-trading execution data into this research standard under the current no-execution boundary.
- Never classify a result as `Supported` without the Quality Manual evidence threshold.
