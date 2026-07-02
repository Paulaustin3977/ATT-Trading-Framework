# Hermes Integration

## Role of Hermes

Hermes is the validation and research harness for the Austin Trading Engine. It runs backtests, evaluates engine outputs, and produces evidence artefacts that ship alongside each engine change.

Hermes does not execute trades. It is a research tool.

## What Hermes Consumes

- Pine Script source under `pine/development/` and `pine/releases/`
- Engine specifications under `specifications/ATE/`
- The methodology rules defined in `docs/Research_Methodology.md`

## What Hermes Produces

| Artefact                       | Location                              |
|--------------------------------|---------------------------------------|
| Backtest outputs               | `backtests/Hermes/<category>/`        |
| Evaluation reports             | `research/Reports/`                   |
| Regression evidence            | `tests/Regression/`                   |
| Validation evidence            | `tests/Validation/`                   |

`<category>` is one of: `Gold`, `Silver`, `Gilts`, `Forex`.

## Workflow

1. **Spec change.** Update the engine specification.
2. **Code change.** Update the Pine script in `pine/development/`.
3. **Hermes run.** Trigger a Hermes validation sweep.
4. **Review.** Compare Hermes output against the spec and the hypothesis.
5. **Archive.** Store outputs in the appropriate folder.
6. **Promote.** Once green, the change is eligible for release.

## Non-negotiables

- Hermes runs are reproducible from the commit hash they reference.
- Hermes outputs are never edited by hand. Re-run instead.
- A negative Hermes result blocks promotion until resolved or explicitly waived in writing.

## Constraints

- No live trading integration.
- No broker connectivity.
- No paper-trading APIs.
- Hermes is local-first and version-controlled.