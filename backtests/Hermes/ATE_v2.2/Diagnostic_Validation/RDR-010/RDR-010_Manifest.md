# RDR-010 Deterministic Measurement Re-attempt Manifest

Run ID: `RDR-010-deterministic-re-attempt`

Generated evidence date: 2026-07-25

Run type: fixed-parameter diagnostic measurement

Status: **MEASURED — MIXED EVIDENCE, DIAGNOSTIC-ONLY; NO PROMOTION**

ATE release version: v2.2 (unchanged)

TrendEngine version: `0.2.0-spec-impl` Python mirror

## 1. Purpose and first-attempt history

This manifest supersedes the stale feasibility-only manifest with measured evidence from the real RDR-010 re-attempt. The first attempt on 2026-07-07 correctly returned `INSUFFICIENT EVIDENCE — RETEST REQUIRED` because no TrendEngine implementation, mirror, fixtures, verifier checks, or RDR-010 harness existed then.

History preserved before replacement:

- First-attempt report SHA-256: `89b076cf9bae57a7c4fde7116df54a3035d99643c3feec850807bb5d8c4253c7`
- First-attempt manifest SHA-256: `7a5a2efc8949b665d9cce118edffc9b1141ff79ee993066ac560cc3409b79009`
- First-attempt verdict: `INSUFFICIENT EVIDENCE — RETEST REQUIRED`
- First-attempt reason: validation target absent on disk.
- Resolution: the implementation gate now exists; this re-attempt performs measurement and retains the no-promotion governance boundary.

## 2. Reproduction

From repository root:

```bash
python3 \
  backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/test_rdr010_validation.py
python3 \
  backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/run_rdr010_validation.py
python3 tools/scripts/verify_ate.py
```

Observed:

- Focused tests: `Ran 6 tests ... OK` (6/6).
- Harness: 6 datasets, 9,118 bar-output rows, 288 directional-metric rows, 4 charts, exit 0.
- Canonical verifier: 530/530 passed, 0 failed, exit 0.
- Two consecutive harness runs produced byte-identical hashes for all generated CSV, JSON, log, and PNG files.
- Network calls: 0.
- Parameter search: none.
- Trading/execution logic: none.

Execution environment recorded by `execution.log`:

- Python 3.9.6
- pandas 2.3.2
- numpy 2.0.2
- matplotlib 3.9.4

## 3. Source code and fixed parameters

- Harness: `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/run_rdr010_validation.py`
- Focused tests: `backtests/Hermes/ATE_v2.2/Diagnostic_Validation/RDR-010/test_rdr010_validation.py`
- Compute path: `tools/scripts/_trendengine_compute.py`
- Fixed parameters: EMA 50; slope lookback 5; slope threshold 0.001; swing length 5; structure confirmation 3; strength scale 50.0; maximum age 250.
- Horizons: exactly 1, 5, and 20 bars.
- No parameter sweep, optimization, model fit, or threshold search.

## 4. Source caches

| Timeframe / instrument | Relative path | Rows | Eligible | SHA-256 |
|---|---|---:|---:|---|
| Daily / GC=F | `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/GC_F.csv` | 2513 | 2458 | `20df1df094686210db778ffea40b006a81e6ea123502e97cd7da88c0b60a228b` |
| Daily / SI=F | `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/SI_F.csv` | 2513 | 2458 | `c298335a2627262bc223a84cd0bdb7406a715ea437e1727b01a3c4093d50813a` |
| Daily / IGLT.L | `backtests/Hermes/ATE_v2.2/Daily/Diagnostic_Validation/RDR-003/data_cache/IGLT.L.csv` | 2526 | 2471 | `bef339e1ffaa86ff38fbc38a133b2e72ed8fcc2ae43358d4bd58acdcd49d2344` |
| Weekly / GC=F | `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/GC_F_w.csv` | 522 | 467 | `33d11460eebf56c8c528f73b6c8cdf92f0cef084f33cee3d5ca36dc84073c173` |
| Weekly / SI=F | `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/SI_F_w.csv` | 522 | 467 | `d025b1a7ef5084685f945e86136b6413da58dc3c3bea97b7b69d7e10cc526a0a` |
| Weekly / IGLT.L | `backtests/Hermes/ATE_v2.2/Weekly/Diagnostic_Validation/RDR-003W/data_cache/IGLT.L_w.csv` | 522 | 467 | `586d3fa9370af9741a62d314ec5219fbcd8268c06562d2224570741a3faf1860` |

Caches were read in place and not modified by the harness.

## 5. Metric definitions

- Trend direction: `UP=+1`, `DOWN=-1`; `RANGE`/`UNKNOWN` excluded.
- Next return: `Close[t+h]/Close[t]-1`, `h={1,5,20}`.
- Hit: signed next return `>0`.
- False signal: directional signed next return `<=0`; zero is a miss.
- Expectancy: arithmetic mean signed next return, with no cost/trade interpretation.
- Benchmark: always-long on every post-warm-up eligible bar.
- Early/late: non-overlapping chronological halves per dataset.
- Volatility regimes: trailing 20-bar return-volatility split at descriptive sample tertiles per dataset.
- Duration: contiguous same-state bars.
- Transition: adjacent-bar state change.

## 6. Generated artefacts and deterministic hashes

| File | Purpose | SHA-256 |
|---|---|---|
| `bar_outputs.csv` | Bar-level TrendEngine output, slices, and fixed forward returns | `47fb2dfd85509362ef3ad5db3a301bc6a1112feb95e979745b5ca1f09a8aa8b4` |
| `state_distribution.csv` | All/post-warm-up state counts and fractions | `07cfdf1d985289a0b8e1d5505e1d3951dc0a0ac90621819809084fb8547b2a44` |
| `state_durations.csv` | Every contiguous state run | `c5c61dde535a8d19d832e36a68a3c2b20cfb555cdc6872e71952b7551800f0f4` |
| `state_transitions.csv` | All/post-warm-up transition counts | `b3d2406e4dbc99649cff6b2696c65aa328a280accd95e736113fd697cc47a035` |
| `directional_metrics.csv` | Overall, early/late, and volatility directional metrics plus benchmark | `1e498c45132a71a934cf956b67cfce15e1ca80b5630ec7c0b8c019130d6ba111` |
| `stability_summary.csv` | State shares, transition rates, early/late TV distance | `4aa58d3ac51d3c23730b355fcafcf8972818a1896b760d08a4fee175aaaec659` |
| `daily_weekly_comparison.csv` | Daily/weekly side-by-side differences | `8764ed59722986d01fc06962be6ae40389e4e224c7a7ce5dbaa66f53f3781611` |
| `Research_Findings.json` | Definitions, sources, hashes, pooled metrics, limitations | `db7ec6d6e411cfaee335f9baa7094fc678b0ccfee62f968933c81ae8ead87b81` |
| `execution.log` | Deterministic command/environment/run summary | `03afcb01213c31d578b32db9ea176474838ba340718beb7d96a4c52c18999768` |
| `charts/state_distribution_daily.png` | Daily state distribution | `ea30e9df8095b139a8b683a4cd325d253e14b1d964c93d557322ca6a43646420` |
| `charts/state_distribution_weekly.png` | Weekly state distribution | `4454a5d4b49fddeea26f8124930c2e59309a5ce778cc60e3693a3f8b94134fbc` |
| `charts/pooled_directional_metrics.png` | TrendEngine/benchmark pooled hit and expectancy | `08fdf9d253e67947cb4e2ee812913604b21dff8180a41b91aee1b6e49f68e4c5` |
| `charts/daily_stability_transitions.png` | Daily transition stability slices | `d5b483de9f814b36502e97c6f322b38510e110ab2485d2af39f8f5dde381cfda` |

The report and this manifest are evidence documents and are not included in the harness's self-hash set.

## 7. Headline measured outcome

Pooled TrendEngine directional hit / expectancy:

- Daily 1 bar: 51.32% / 0.0288%; benchmark 51.54% / 0.0371%.
- Daily 5 bars: 51.64% / 0.1376%; benchmark 52.70% / 0.1783%.
- Daily 20 bars: 50.40% / 0.3853%; benchmark 53.39% / 0.7423%.
- Weekly 1 bar: 52.97% / 0.1827%; benchmark 53.65% / 0.2037%.
- Weekly 5 bars: 54.79% / 0.9577%; benchmark 53.17% / 1.0032%.
- Weekly 20 bars: 62.66% / 5.3810%; benchmark 59.14% / 4.6784%.

State `RANGE` was rare/absent post warm-up. Early/late outcomes and state mixes shifted materially; weekly IGLT.L early/late state total variation was 49.57%. These findings support diagnostic-only retention and no promotion.

## 8. Release and governance invariants

| Invariant | Result |
|---|---|
| ATE v2.2 release SHA | `d55ca5efe0c277edbac3596a0a7cb6548ba56c8e9eae085acdfda4b15fc19239` — unchanged |
| ATE v2.1 release SHA | `7dc704df87489811cf033841e3249a84dda352cf2b6f92a8d5c11c0a9a7cd893` — unchanged |
| Canonical verifier | 530/530, exit 0 |
| RiskEngine status | Preserved diagnostic-only |
| ConfidenceEngine / RiskEngine / DecisionEngine coupling | None added |
| Trading/execution functionality | None added or used |
| Pine release modification | None |
| TradingView compilation claim | None |
| Commit / push | None |

## 9. Limitations and integrity

Overlapping 5/20-bar returns are dependent; no significance claim is made. The benchmark is transparent but not matched-frequency. Volatility tertiles are descriptive full-sample slices. No trades exist, so drawdown/profit-factor/cost metrics are not applicable. The Python mirror was exercised; no TradingView compile or live Pine run is claimed.

The evidence is mixed and negative findings are preserved. The measured result does not authorise promotion, coupling, alerts, or execution. Paul Austin retains final governance authority.
