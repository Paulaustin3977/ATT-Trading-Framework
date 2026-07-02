# Research Methodology

## Purpose

This document defines how the Austin Trading Engine validates claims about market behaviour. The methodology exists to keep research reproducible, evidence-based, and free from narrative bias.

## Principles

1. **Hypothesis first.** Every research thread begins with a written hypothesis.
2. **Pre-registered scope.** The data range, instruments, and parameters are fixed before the run.
3. **No post-hoc cherry-picking.** Parameters discovered to "work" after the fact are treated as suspect.
4. **Negative results count.** A null result is recorded as a finding, not a failure.
5. **Reproducibility.** Anyone with the same inputs must be able to reproduce the result.

## Workflow

```
Hypothesis → Specification → Data → Run → Evaluation → Record
                                       ↑                  ↓
                                       └── Iteration ←─────┘
```

## Data

- **Primary source:** TradingView daily bars for the target instrument.
- **Auxiliary:** Macro and calendar context where relevant.
- **Range:** Default lookback is the maximum available daily history unless the hypothesis dictates otherwise.

## Instruments

| Category | Folder             | Notes                                   |
|----------|--------------------|-----------------------------------------|
| Gold     | `research/Gold/`   | Spot, futures, ETF proxies              |
| Silver   | `research/Silver/` | Spot, futures, ETF proxies               |
| Gilts    | `research/Gilts/`  | UK and US sovereign duration instruments|
| Forex    | `research/Forex/`  | Majors and crosses                      |

## Hermes Validation

Hermes is the validation harness. A claim is not considered supported until a Hermes run produces:

- A backtest artefact in `backtests/Hermes/<category>/`
- An evaluation summary in `research/Reports/`
- A regression entry in `tests/Regression/`

## Reporting

Each report in `research/Reports/` follows this structure:

1. Title and date
2. Hypothesis
3. Data and parameters
4. Method
5. Results (including negatives)
6. Limitations
7. Next steps

## What We Do Not Do

- We do not overfit. Multiple-testing corrections are applied where appropriate.
- We do not extrapolate beyond the data window without flagging it.
- We do not present a single backtest as proof. We present a backtest as evidence within a body of work.