# ATT Trading Framework

**Austin Trading Engine (ATE)**

The Austin Trading Engine is a modular, explainable, evidence-based market analysis framework designed to support TradingView indicators, strategies, Hermes research validation, AI-assisted analysis, and future trading dashboards.

## Project Identity

- **Project name:** Austin Trading Engine (ATE)
- **Repository:** ATT-Trading-Framework
- **Maintainer:** Austin Trading Team
- **Primary language:** Pine Script v6
- **Validation engine:** Hermes (local-first research)
- **Status:** Active development

## Goals

- Pine Script v6
- Daily timeframe first
- Non-repainting
- Modular architecture
- Optimizer friendly
- Professional risk management
- Version controlled with Git

## Current Version

v2.0 (placeholder — see `pine/releases/`)

## Repository Structure

| Folder           | Purpose                                                                |
|------------------|------------------------------------------------------------------------|
| `docs/`          | Project charter, architecture, standards, methodology, process notes   |
| `specifications/`| Per-engine specifications defining each analytical module             |
| `pine/`          | Pine Script source — development branch and released versions          |
| `laboratory/`    | Experimental features under active research, not yet promoted         |
| `research/`      | Asset-class research notes and reports                                 |
| `backtests/`     | Hermes-generated backtest outputs, organised by asset class            |
| `tests/`         | Regression and validation test definitions                            |
| `tools/`         | Helper scripts and automation                                          |

## Getting Started

1. Read [`docs/Project_Charter.md`](docs/Project_Charter.md) for mission and scope.
2. Read [`docs/Architecture.md`](docs/Architecture.md) for the engine layout.
3. Read [`docs/Coding_Standards.md`](docs/Coding_Standards.md) before writing Pine.
4. Open the latest release from `pine/releases/` in TradingView.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the long-term development plan and [`CHANGELOG.md`](CHANGELOG.md) for release history.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution workflow, evidence requirements, and review process.

## License

Internal — Austin Trading Team. Not yet released under an open-source licence.