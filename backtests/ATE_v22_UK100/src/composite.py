"""
Composite-gate strategy — the most defensible 'real' trading rule I can
construct from ATE v2.2's diagnostic scores, given the v2.2 release's
"Entry/exit impact: NO" boundary.

Three-class rule (long-only):
    ENTER long on next-bar-open when ALL of:
        trend_score     > T_enter
        confidence_score > C_enter
        risk_score       < R_max       (inv-polarity: risk must be CALM)

    EXIT long on next-bar-open when ANY of:
        trend_score     < T_exit
        confidence_score < C_exit
        risk_score       > R_exit       (risk has spiked)

    Plus the existing ATR(14)*2 trailing stop on intrabar lows.

Why this shape:
  - Two corroborating directional scores (trend + confidence) cut false-trend
    traps: trend can run hot during a momentum exhaustion; confidence reweights
    by structure + momentum so it dips earlier.
  - risk_score is non-directional (higher = more risk pressure); using it as an
    entry ceiling (R_max) and exit floor (R_exit) is the "trade only when calm,
    exit when chaotic" discipline.

This is one research hypothesis consistent with the score polarities. The
diagnostic Pine release itself does not authorise or define this signal shape.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Composite:
    name: str
    T_enter: float = 60.0
    C_enter: float = 60.0
    R_max:   float = 40.0   # enter ceiling (risk must be BELOW)
    T_exit:  float = 40.0
    C_exit:  float = 40.0
    R_exit:  float = 50.0   # exit floor (risk above this triggers exit)
    require_risk_filter: bool = True

    def short_label(self) -> str:
        if not self.require_risk_filter:
            return f"T{int(self.T_enter)}/C{int(self.C_enter)}"
        return f"T{int(self.T_enter)}/C{int(self.C_enter)}/R<{int(self.R_max)}"


def composite_grid() -> list:
    """Grid: 3 T_enter × 3 C_enter × 2 R_max = 18 with risk filter; 9 without.

    Note on R_max values: the risk_score's distribution on these EU/UK indices is
    heavily skewed (median 5, 90th percentile 8, max ~15). A 'risk ceiling' that
    gates trade entry must be in that range, not in the [0,100] naive band. We
    test R_max values {5, 15} which correspond to "moderate risk accepted" and
    "calm-only" respectively. The R_exit floor is set to 15 (above the typical
    regime) so it actually fires.
    """
    grid = []
    for te in (50.0, 60.0, 70.0):
        for ce in (50.0, 60.0, 70.0):
            # Without risk filter (ablation)
            grid.append(Composite(
                name=f"composite_T{te:.0f}_C{ce:.0f}_noR",
                T_enter=te, C_enter=ce,
                R_max=99.0, R_exit=99.0,
                T_exit=40.0, C_exit=40.0,
                require_risk_filter=False,
            ))
            for rmax in (5.0, 15.0):
                grid.append(Composite(
                    name=f"composite_T{te:.0f}_C{ce:.0f}_Rmax{rmax:.0f}",
                    T_enter=te, C_enter=ce, R_max=rmax,
                    T_exit=40.0, C_exit=40.0, R_exit=15.0,
                    require_risk_filter=True,
                ))
    return grid


def signal_long(composite: Composite, trend: float, conf: float, risk: float) -> str:
    """One-bar signal evaluation. Returns 'enter' | 'in_trade' | 'exit' | 'flat'."""
    if composite.require_risk_filter:
        calm_risk = risk < composite.R_max
        chaotic_risk = risk > composite.R_exit
    else:
        calm_risk = True
        chaotic_risk = True   # never use as exit trigger
    bull_trend = trend > composite.T_enter
    bull_conf  = conf  > composite.C_enter

    # Decode (one bar's read):
    in_trend = trend > composite.T_exit
    in_conf  = conf  > composite.C_exit

    if bull_trend and bull_conf and calm_risk:
        return "enter"
    if not in_trend or not in_conf or chaotic_risk:
        return "exit"
    return "in_trade"
