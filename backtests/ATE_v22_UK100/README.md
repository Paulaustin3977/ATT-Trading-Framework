# ATE v2.2 — UK100 research backtest

Research-only Python experiments derived from the diagnostic indicator
`pine/releases/ATE_v2.2.pine`. This directory contains no broker, live, paper,
or execution integration.

## Evidence status

**Do not use the checked-in result artefacts as current performance evidence.**
An independent hardening review found material Pine-parity and execution-accounting
bugs and fixed the source. The existing CSV/JSON/Markdown/PNG files were produced
before those fixes and have not been regenerated. See `results/STATUS.md`.

The historical artefacts were negative overall. A previously highlighted
`risk_long_inv` row averaged only about two trades per symbol, while the composite
results were negative. That sample is far too weak for promotion and is now also
invalidated by source changes. This project makes no recommendation to promote,
paper-trade, or trade any rule.

## Reproducible local setup

Tested with CPython 3.9 and the exact direct dependencies in `requirements.txt`.
The following keeps the environment outside the repository and does not use the
ignored local `.venv`:

```bash
cd backtests/ATE_v22_UK100
python3 -m venv /private/tmp/ate-v22-uk100-venv
/private/tmp/ate-v22-uk100-venv/bin/python -m pip install --upgrade pip
/private/tmp/ate-v22-uk100-venv/bin/python -m pip install -r requirements.txt
/private/tmp/ate-v22-uk100-venv/bin/python -m pytest tests -q
/private/tmp/ate-v22-uk100-venv/bin/python -m compileall -q src scripts tests
```

The deterministic test suite uses synthetic OHLC fixtures and does not access the
network. Cached market CSVs under `data/` allow the non-fetch scripts to run
offline. `scripts/fetch_data.py` is the only intended data-refresh entry point and
uses yfinance.

## Scripts

```bash
PY=/private/tmp/ate-v22-uk100-venv/bin/python
$PY scripts/sanity_check.py       # cached-data buy-and-hold diagnostic
$PY scripts/backtest_all.py       # 6 arms × 6 symbols; rewrites base results
$PY scripts/optimize.py           # expensive segmented parameter sweep
$PY scripts/adversarial_sweep.py  # expensive polarity sweep
$PY scripts/composite_backtest.py # expensive composite sweep
$PY scripts/build_report.py       # rewrites report and charts from result files
```

Do not run the result-generating scripts merely to verify installation: they
rewrite historical artefacts. The review intentionally ran focused tests,
compilation, and lightweight cached-data scripts instead of the expensive sweeps.

## Method and limitations

- The indicator port is checked against selected Pine semantics: SMA-seeded Wilder
  RMA, confirmed-pivot state, RiskEngine conflict logic, missing-data propagation,
  and prefix invariance (future bars do not change prior scores).
- Full TradingView parity has **not** been established because no immutable export
  fixture from TradingView is included. Do not call this a line-by-line or exact
  port.
- The Pine release is an indicator and explicitly gives RiskEngine no entry/exit,
  sizing, stop, or alert authority. Threshold strategies and ATR stops here are
  research hypotheses, not Pine strategy semantics.
- Orders generated from a close execute at the next open. Intrabar stops take
  precedence on the bar where they occur; gap-through stops fill at the open.
  Commission is charged on both entry and exit.
- Legacy files and columns containing `walk_forward` or `oos` actually describe
  non-overlapping chronological segments. There is no train-time parameter
  selection, so they are not genuine walk-forward/OOS evidence.
- Six correlated UK/EU instruments over roughly ten daily years are a small,
  non-independent panel. Multiple parameter searches further weaken nominal
  Sharpe comparisons. No statistical promotion threshold was met.

## Layout

- `src/` — indicator calculations, research strategy definitions, simulators,
  segmented evaluator, and metrics
- `tests/` — deterministic synthetic parity/execution tests
- `scripts/` — data refresh and result-generation entry points
- `data/` — cached adjusted daily yfinance bars
- `results/` — historical pre-fix artefacts; see `results/STATUS.md`
