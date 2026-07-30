# MomentumEngine — ATE v2.2 As-Built Diagnostic Specification

## Status

Implemented in the immutable `pine/releases/ATE_v2.2.pine` baseline and covered by release verification. No dedicated MomentumEngine RDR classification or separate downstream/action approval is recorded. This is an as-built description, not a Pine change proposal.

## Inputs and derived values

- `showMomentum`: default `true`.
- RSI: `rsiLen=14`, minimum `2`; `rsiVal=ta.rsi(close, rsiLen)`; `rsiUp=rsiVal > rsiVal[1]`.
- MACD: `macdFast=12`, `macdSlow=26`, `macdSignal=9`, each minimum `1`; `macdBull=macdLine > macdSig`, `macdBear=macdLine < macdSig`, `macdRising=macdHist > macdHist[1]`.
- DMI/ADX: `adxLen=14`, `adxSmooth=14`, each minimum `2`; `adxRising=adxVal > adxVal[1]`. `plusDI` and `minusDI` are calculated by `ta.dmi` but are not used in scoring.

## Component scoring

First matching condition in each table wins.

| RSI condition | `rsiScore` |
|---|---:|
| `55 <= rsiVal <= 70` and rising | 35 |
| `50 < rsiVal < 80` | 28 |
| `45 <= rsiVal <= 55` | 18 |
| `rsiVal < 45` | 8 |
| Fallback | 15 |

| MACD condition | `macdScore` |
|---|---:|
| Bullish, histogram positive and rising | 35 |
| Bullish and histogram positive | 28 |
| Bullish | 22 |
| Bearish, histogram negative and not rising | 5 |
| Fallback | 15 |

| ADX condition | `adxScore` |
|---|---:|
| `25 <= adxVal <= 45` and rising | 30 |
| `adxVal >= 25` | 24 |
| `adxVal >= 18` | 16 |
| Fallback | 8 |

`momentumScore = rsiScore + macdScore + adxScore` when enabled; disabling the engine publishes `50`.

## State mapping

| Score condition | `momentumState` |
|---|---|
| `>= 80` | `STRONG MOMENTUM` |
| `>= 60` | `BULLISH MOMENTUM` |
| `> 40` | `NEUTRAL MOMENTUM` |
| `> 20` | `BEARISH MOMENTUM` |
| Otherwise | `WEAK MOMENTUM` |

The implementation does not calculate divergence and does not expose the placeholder-era `momentumValue`/`divergenceFlag` contract. It has no separate version literal, reason field, or diagnostics object.

## Consumption and presentation

- ConfidenceEngine consumes `momentumScore`.
- RiskEngine compares `trendScore - momentumScore` for its conflict diagnostic.
- Dashboard shows Momentum Score, Momentum State, and the `RSI/MACD/ADX` component scores.
- Research Mode emits `MomentumScore` and `MomentumState`.
- Existing threshold events are `momentumBull` when score crosses above/equal `70`, and `momentumBear` when score crosses below/equal `30`; their alert titles are `ATE Momentum Bullish` and `ATE Momentum Bearish`.

## Boundaries

Momentum outputs are directional diagnostics, not orders or action approval. The engine does not size positions, set stops, connect to execution, or activate DecisionEngine.
