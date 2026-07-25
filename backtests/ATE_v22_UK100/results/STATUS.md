# Result artefact status

The metric-bearing CSV/JSON artefacts in this directory were generated before the 2026-07 independent hardening review. The Markdown report and PNGs may be regenerated from those same historical tables, but that does not make the underlying metrics current. All are retained as historical research output, **not current evidence**.

The review found and fixed material implementation defects:

- Pine `ta.rma` was not SMA-seeded.
- confirmed-pivot `prevHigh` / `prevLow` state was lost between pivots.
- RiskEngine conflict base points were discarded, recent-cross detection was only a proximity proxy, and unavailable risk values were converted to zero.
- the execution engines could prefer a future next-open signal exit over an already-hit intrabar stop, used the completed bar's low as a stop fill, omitted entry commission from equity, and lagged final mark-to-market equity.
- the four so-called walk-forward windows were unequal chronological segments with no train-time selection; they were not genuine OOS windows.

These fixes can materially change scores, trades, and headline metrics. Expensive sweeps were deliberately not rerun during review. Do not cite the existing result files as validated performance, do not compare their rows to newly generated outputs, and do not recommend promotion or trading from them. Regenerate all derived artefacts before any further quantitative interpretation.
