"""
Strategy dataclasses for the ATE v2.2 6-arm backtest.

Each arm trades a single score:
  - TrendLong      : long if trend_score > long_thr, flat if trend_score < exit_thr
  - StructureLong  : long if structure_score > long_thr, flat if structure_score < exit_thr
  - MomentumLong   : long if momentum_score > long_thr, flat if momentum_score < exit_thr
  - ConfidenceLong : long if confidence_score > long_thr, flat if confidence_score < exit_thr
  - VolLong        : long if vol_score > long_thr, flat if vol_score < exit_thr
                      (NOTE: vol is non-directional — surface as "all of them"
                      literal interpretation; you'll see it's not an edge)
  - RiskLong       : long if risk_score > long_thr, flat if risk_score < exit_thr
                      (risk>60 = more risk-off; this is contrarian and is
                      kept per the "all of them" instruction)

All arms default to long_thr=60, exit_thr=40 to match the Pine score-color
discrete tiers (≥60 = BULL/GREEN, >40 = NEUTRAL/YELLOW, ≤40 = BEAR/ORANGE/RED).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

SCORE_ARMS = (
    "trend_long",
    "structure_long",
    "momentum_long",
    "confidence_long",
    "vol_long",
    "risk_long",
)


@dataclass
class ScoreStrategy:
    arm: str
    score_col: str
    long_thr: float = 60.0
    exit_thr: float = 40.0

    def __post_init__(self):
        if self.long_thr <= self.exit_thr:
            raise ValueError(f"{self.arm}: long_thr {self.long_thr} must be > exit_thr {self.exit_thr}")


def all_strategies(
    long_thr: float = 60.0,
    exit_thr: float = 40.0,
) -> dict:
    """Return a dict of all 6 strategies with the given thresholds."""
    return {
        "trend_long": ScoreStrategy("trend_long", "trend_score", long_thr, exit_thr),
        "structure_long": ScoreStrategy("structure_long", "structure_score", long_thr, exit_thr),
        "momentum_long": ScoreStrategy("momentum_long", "momentum_score", long_thr, exit_thr),
        "confidence_long": ScoreStrategy("confidence_long", "confidence_score", long_thr, exit_thr),
        "vol_long": ScoreStrategy("vol_long", "vol_score", long_thr, exit_thr),
        "risk_long": ScoreStrategy("risk_long", "risk_score", long_thr, exit_thr),
    }


def param_grid_default() -> list:
    """Coarse 3×3 grid (long_thr × exit_thr) per arm — 9 combos × 6 arms = 54."""
    combos = []
    for lt in (55.0, 60.0, 65.0):
        for et in (35.0, 40.0, 45.0):
            if lt <= et:
                continue
            combos.append((lt, et))
    return combos
