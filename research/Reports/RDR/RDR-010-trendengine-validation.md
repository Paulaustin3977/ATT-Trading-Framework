# RDR-010: TrendEngine Diagnostic Validation — Measurement Re-attempt

Date: 2026-07-25

Status: **MEASURED — DIAGNOSTIC-ONLY; NO PROMOTION**

Owner / Author: Hermes, Quantitative Research Department

Reviewer: Chief Systems Architect (pending)

ATE version: v2.2 release surface unchanged

TrendEngine version tested: `0.2.0-spec-impl` Python mirror

Research classification: **Mixed, instrument- and timeframe-dependent descriptive evidence**

## 1. Executive decision

The RDR-010 re-attempt ran a deterministic, fixed-parameter diagnostic harness on the existing RDR-003 daily and RDR-003W weekly OHLC caches for Gold (`GC=F`), Silver (`SI=F`), and Gilts (`IGLT.L`). It measured state frequency, duration, transitions, fixed 1/5/20-bar directional next returns, an explicit false-signal rate, early/late and volatility-regime stability, daily-versus-weekly behaviour, and a transparent no-TrendEngine benchmark.

**Decision: retain TrendEngine as research-only diagnostic output. Do not couple it to ConfidenceEngine, RiskEngine, DecisionEngine, alerts, or any trading/execution path.** The evidence is not consistent enough for promotion:

- Pooled daily TrendEngine hit rates were 51.32%, 51.64%, and 50.40% at 1/5/20 bars, but all three underperformed the always-long no-TrendEngine benchmark on both hit rate and expectancy.
- Pooled weekly TrendEngine hit rates were 52.97%, 54.79%, and 62.66%. It exceeded the benchmark at 5 and 20 bars on hit rate, but expectancy exceeded the benchmark only at 20 bars.
- Results were heterogeneous: daily Gold was positive at all horizons; daily Gilts were negative at all horizons; daily Silver's 20-bar hit rate was below 50% despite positive arithmetic expectancy.
- State behaviour was extremely persistent and almost never emitted `RANGE` after warm-up: 0.00%–0.77% daily and 0.00%–8.14% weekly. This is a material diagnostic limitation, not proof of a useful three-state classifier.
- Early/late and volatility-slice results changed materially. Weekly IGLT.L had an early/late state-distribution total-variation distance of 49.57%.

This is descriptive diagnostic validation, **not a strategy backtest**. No trades, costs, drawdowns, entries, exits, sizing, stops, orders, alerts, broker connection, or execution were modelled. No parameter search was performed. No TradingView compile is claimed.

## 2. First-attempt history (preserved)

The first RDR-010 attempt on 2026-07-07 concluded **`INSUFFICIENT EVIDENCE — RETEST REQUIRED`** because TrendEngine did not then exist on disk. Its report SHA-256 was `89b076cf9bae57a7c4fde7116df54a3035d99643c3feec850807bb5d8c4253c7`; its manifest SHA-256 was `7a5a2efc8949b665d9cce118edffc9b1141ff79ee993066ac560cc3409b79009` immediately before this replacement.

That first attempt established the gate: concrete spec, research-only development implementation, Python mirror, four deterministic fixtures, verifier coverage, daily and weekly measurement, charts, and governance boundaries. The implementation/fixture/verifier prerequisites now exist, so this document supersedes the first attempt's absence-of-evidence conclusion while preserving its history and rationale here. It does not erase or reinterpret the fact that the first attempt was a meta-RDR.

## 3. Research question and scope

> Does the fixed TrendEngine diagnostic state carry stable directional information across Gold, Silver, and Gilts on daily and weekly data, relative to a transparent no-TrendEngine benchmark?

Strict scope:

- Research/backtest/diagnostic only.
- TrendEngine outputs assessed: `trendState`, `trendStrength`, `trendAge`, and diagnostic internals.
- RiskEngine remains diagnostic-only and was not called or modified by this study.
- No ConfidenceEngine, RiskEngine, or DecisionEngine coupling.
- No live/paper trading, broker, orders, execution, position sizing, stops, entry/exit logic, or alerts.
- No parameter search and no post-result threshold tuning.

## 4. Reproducible method

Harness: `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/run_rdr010_validation.py`

Compute path: `tools/scripts/_trendengine_compute.py`

Tests: `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/test_rdr010_validation.py`

The harness uses the exact fixed parameters in the mirror:

| Parameter | Value |
|---|---:|
| `trendEmaLen` | 50 |
| `trendSlopeLookback` | 5 |
| `trendSlopeMin` | 0.001 |
| `trendSwingLen` | 5 |
| `trendStructureBars` | 3 |
| `trendStrengthScale` | 50.0 |
| `trendAgeMax` | 250 |

Definitions fixed before reading outcomes:

1. **Directional observation:** `UP = +1`, `DOWN = -1`; `RANGE` and `UNKNOWN` are excluded from TrendEngine directional samples.
2. **Next return:** `Close[t+h] / Close[t] - 1` for exactly `h ∈ {1,5,20}` bars. Engine state at `t` uses information through `t`; the target is strictly future close.
3. **Hit:** directional signed next return `> 0`.
4. **False signal:** a directional observation whose signed next return is `<= 0`; a zero return is a miss. Therefore, within a fixed directional sample, `false_signal_rate = 1 - hit_rate`.
5. **Expectancy:** arithmetic mean signed next return. It is not trade expectancy and includes no costs.
6. **No-TrendEngine benchmark:** always-long (`+1`) on every post-warm-up eligible bar, using the same future-return targets. It is transparent, but has a slightly larger sample than TrendEngine when TrendEngine emits `RANGE`; it is not a matched-frequency strategy.
7. **Early/late:** non-overlapping chronological halves of post-warm-up rows for each instrument/timeframe.
8. **Volatility regimes:** 20-bar trailing close-return sample standard deviation, descriptively split at each instrument/timeframe's full-sample 33.3% and 66.7% quantiles. These are fixed descriptive slices, not optimized or out-of-sample thresholds.
9. **Duration:** contiguous bars in the same state. **Transition:** adjacent-bar state change; same-state observations are excluded.

## 5. Data and integrity

| Timeframe | Instrument | Rows | Post-warm-up | Coverage |
|---|---|---:|---:|---|
| Daily | GC=F | 2,513 | 2,458 | 2016-07-05 to 2026-07-03 |
| Daily | SI=F | 2,513 | 2,458 | 2016-07-05 to 2026-07-03 |
| Daily | IGLT.L | 2,526 | 2,471 | 2016-07-04 to 2026-07-03 |
| Weekly | GC=F | 522 | 467 | 2016-07-04 to 2026-06-29 |
| Weekly | SI=F | 522 | 467 | 2016-07-04 to 2026-06-29 |
| Weekly | IGLT.L | 522 | 467 | 2016-07-04 to 2026-06-29 |

All six source CSV SHA-256 values, date ranges, row counts, and volatility thresholds are recorded in `Research_Findings.json`. The caches were reused in place and not copied or changed.

## 6. Diagnostic state distributions

Post-warm-up fractions:

| Timeframe | Instrument | UP | DOWN | RANGE | UNKNOWN |
|---|---|---:|---:|---:|---:|
| Daily | GC=F | 64.89% | 35.11% | 0.00% | 0.00% |
| Daily | SI=F | 54.56% | 44.67% | 0.77% | 0.00% |
| Daily | IGLT.L | 42.49% | 56.90% | 0.61% | 0.00% |
| Weekly | GC=F | 73.66% | 18.20% | 8.14% | 0.00% |
| Weekly | SI=F | 69.38% | 30.62% | 0.00% | 0.00% |
| Weekly | IGLT.L | 22.27% | 75.16% | 2.57% | 0.00% |

The output is predominantly binary UP/DOWN. `RANGE` is rare or absent. This is especially important because TrendEngine is described as a three-state diagnostic. The state adoption/confirmation rules produce long persistence, and this validation provides no evidence that `RANGE` is reliably represented.

## 7. State durations and transitions

Representative full-sample run statistics (warm-up `UNKNOWN` excluded from interpretation):

| Timeframe | Instrument | State | Runs | Median bars | Maximum bars |
|---|---|---|---:|---:|---:|
| Daily | GC=F | UP | 10 | 120.0 | 638 |
| Daily | GC=F | DOWN | 11 | 78.0 | 150 |
| Daily | SI=F | UP | 15 | 72.0 | 299 |
| Daily | SI=F | DOWN | 16 | 56.5 | 208 |
| Daily | IGLT.L | UP | 13 | 64.0 | 212 |
| Daily | IGLT.L | DOWN | 14 | 76.0 | 313 |
| Weekly | GC=F | UP | 3 | 152.0 | 159 |
| Weekly | SI=F | UP | 3 | 148.0 | 167 |
| Weekly | IGLT.L | DOWN | 2 | 175.5 | 281 |

Post-warm-up transition totals were only 20/31/27 on daily GC=F/SI=F/IGLT.L and 5/5/3 on weekly GC=F/SI=F/IGLT.L. Full transition matrices and every contiguous run are in `state_transitions.csv` and `state_durations.csv`.

## 8. Fixed-horizon directional results and benchmark

### 8.1 Pooled descriptive results

| TF | Horizon | Trend n | Trend hit | Trend false | Trend expectancy | Benchmark n | Benchmark hit | Benchmark expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Daily | 1 | 7,350 | 51.32% | 48.68% | 0.0288% | 7,384 | 51.54% | 0.0371% |
| Daily | 5 | 7,338 | 51.64% | 48.36% | 0.1376% | 7,372 | 52.70% | 0.1783% |
| Daily | 20 | 7,293 | 50.40% | 49.60% | 0.3853% | 7,327 | 53.39% | 0.7423% |
| Weekly | 1 | 1,348 | 52.97% | 47.03% | 0.1827% | 1,398 | 53.65% | 0.2037% |
| Weekly | 5 | 1,336 | 54.79% | 45.21% | 0.9577% | 1,386 | 53.17% | 1.0032% |
| Weekly | 20 | 1,291 | 62.66% | 37.34% | 5.3810% | 1,341 | 59.14% | 4.6784% |

Daily TrendEngine minus benchmark hit-rate differences were -0.22, -1.06, and -2.99 percentage points at 1/5/20 bars; expectancy differences were -0.0082%, -0.0408%, and -0.3569%. Weekly hit-rate differences were -0.68, +1.62, and +3.53 points; expectancy differences were -0.0210%, -0.0455%, and +0.7026%.

### 8.2 Per-instrument TrendEngine results

| TF | Instrument | H | n | Hit | False | Expectancy |
|---|---|---:|---:|---:|---:|---:|
| Daily | GC=F | 1 / 5 / 20 | 2457 / 2453 / 2438 | 52.99% / 54.67% / 55.25% | 47.01% / 45.33% / 44.75% | 0.0513% / 0.2360% / 0.8408% |
| Daily | SI=F | 1 / 5 / 20 | 2438 / 2434 / 2419 | 51.31% / 51.36% / 47.79% | 48.69% / 48.64% / 52.21% | 0.0378% / 0.1926% / 0.3789% |
| Daily | IGLT.L | 1 / 5 / 20 | 2455 / 2451 / 2436 | 49.65% / 48.88% / 48.15% | 50.35% / 51.12% / 51.85% | -0.0025% / -0.0154% / -0.0641% |
| Weekly | GC=F | 1 / 5 / 20 | 428 / 424 / 409 | 54.91% / 55.42% / 68.46% | 45.09% / 44.58% / 31.54% | 0.2096% / 0.9961% / 5.4847% |
| Weekly | SI=F | 1 / 5 / 20 | 466 / 462 / 447 | 53.00% / 54.98% / 63.76% | 47.00% / 45.02% / 36.24% | 0.2574% / 1.4783% / 9.0642% |
| Weekly | IGLT.L | 1 / 5 / 20 | 454 / 450 / 435 | 51.10% / 54.00% / 56.09% | 48.90% / 46.00% / 43.91% | 0.0807% / 0.3871% / 1.4986% |

The per-instrument split prevents the strong weekly metal results from masking daily Gilt weakness.

## 9. Stability: early/late and volatility regimes

### 9.1 Chronological halves, pooled TrendEngine

| TF | Half | H=1 hit / exp | H=5 hit / exp | H=20 hit / exp |
|---|---|---|---|---|
| Daily | Early | 50.27% / 0.0123% | 50.30% / 0.0593% | 48.09% / -0.0708% |
| Daily | Late | 52.36% / 0.0452% | 52.96% / 0.2155% | 52.74% / 0.8449% |
| Weekly | Early | 52.45% / 0.1121% | 50.92% / 0.6603% | 57.06% / 3.5012% |
| Weekly | Late | 53.45% / 0.2489% | 58.48% / 1.2413% | 68.39% / 7.2989% |

Late samples were stronger than early samples at every pooled cell shown. That is instability, not validation by itself. Early/late state-distribution total-variation distances were 12.29%–17.98% for five instrument/timeframe pairs and 49.57% for weekly IGLT.L.

### 9.2 Volatility regimes, pooled TrendEngine

| TF | Volatility | H=1 hit / exp | H=5 hit / exp | H=20 hit / exp |
|---|---|---|---|---|
| Daily | Low | 51.06% / 0.0334% | 50.33% / 0.1009% | 49.55% / 0.1510% |
| Daily | Mid | 50.80% / -0.0082% | 50.76% / 0.0473% | 47.31% / 0.2596% |
| Daily | High | 52.10% / 0.0610% | 53.82% / 0.2643% | 54.40% / 0.7509% |
| Weekly | Low | 52.55% / 0.0648% | 50.23% / 0.2231% | 65.02% / 3.0918% |
| Weekly | Mid | 49.56% / 0.1234% | 54.93% / 1.0569% | 56.75% / 4.1150% |
| Weekly | High | 56.65% / 0.3493% | 58.95% / 1.5541% | 66.36% / 8.9519% |

High-volatility slices were generally stronger, especially at longer horizons. Because regime thresholds are full-sample descriptive tertiles, this finding is hypothesis-generating, not an operational rule.

## 10. Daily versus weekly

Weekly outcomes were stronger than daily outcomes on pooled 5- and 20-bar hit rates and all pooled TrendEngine expectancies. However, a weekly 20-bar target spans roughly 20 weeks while a daily 20-bar target spans roughly 20 trading days; the horizons are fixed in bars, not calendar-matched. Weekly samples are also much smaller and overlap heavily at 5/20 bars. Therefore this is a timeframe diagnostic, not evidence that weekly should be traded or preferred operationally.

## 11. Interpretation and limitations

1. **Benchmark:** daily TrendEngine did not improve the transparent always-long benchmark. Weekly improvement was limited to hit rate at 5/20 bars and expectancy at 20 bars.
2. **State semantics:** very rare `RANGE` output and long run durations indicate a sticky near-binary classifier. This warrants rule-level review before any promotion claim.
3. **Heterogeneity:** Gold, Silver, and Gilts do not tell one consistent daily story.
4. **Dependence:** 5/20-bar observations overlap; no independence or statistical-significance claim is made.
5. **No strategy metrics:** no trades were defined, so drawdown, profit factor, transaction costs, and trade expectancy are intentionally not reported.
6. **Benchmark limitation:** always-long is transparent and reproducible, but not matched-frequency and not a complete investable benchmark.
7. **Regime limitation:** volatility tertiles are full-sample descriptive labels, not deployable thresholds.
8. **External validity:** three instruments and about ten years do not establish broad robustness.
9. **Implementation target:** validation exercised the Python mirror against cached OHLC. It does not claim TradingView compilation or Pine execution parity beyond the canonical verifier's existing checks.

## 12. Decision and next actions

**RDR-010 classification: MEASURED, MIXED EVIDENCE, DIAGNOSTIC-ONLY; NO PROMOTION.**

- Keep TrendEngine research-only and diagnostic.
- Preserve RiskEngine diagnostic-only status.
- Do not feed TrendEngine into ConfidenceEngine, RiskEngine, or DecisionEngine.
- Do not create filters, entries, exits, sizing, stops, alerts, or execution from these results.
- Before any future promotion RDR, investigate why `RANGE` is almost never adopted, pre-register acceptance criteria, add a matched-frequency benchmark, use non-overlapping or inference-aware evaluation, and expand instruments/time periods without parameter search on this same sample.

## 13. Verification and invariants

- Focused harness tests: **6/6 passed**.
- Determinism: all 13 generated CSV/JSON/log/PNG artefacts were byte-identical across two consecutive runs.
- Canonical verifier: **530/530 passed, exit 0** on 2026-07-25.
- ATE v2.2 release SHA-256: `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` (unchanged).
- ATE v2.1 release SHA-256: `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` (unchanged).
- No commit or push was performed.

## 14. Artefacts

The manifest at `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/RDR-010_Manifest.md` lists every generated file, source-cache hash, command, and reproducibility result. Primary machine-readable evidence is in `Research_Findings.json`, `directional_metrics.csv`, `state_distribution.csv`, `state_durations.csv`, `state_transitions.csv`, `stability_summary.csv`, and `daily_weekly_comparison.csv`.

## 15. Research integrity statement

Evidence and interpretation are separated. All headline values above are derived from generated CSV/JSON artefacts. Negative and heterogeneous findings are reported directly. No parameter search, selective horizon removal, or post-result parameter change was performed. This record authorises no trading or engine coupling. Paul Austin retains final governance and promotion authority.
