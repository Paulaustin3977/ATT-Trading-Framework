"""Focused behavioural tests for the deterministic RDR-010 harness."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "run_rdr010_validation.py"
spec = importlib.util.spec_from_file_location("rdr010", SCRIPT)
rdr010 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(rdr010)


class RDR010HarnessTests(unittest.TestCase):
    def test_state_runs_and_transitions_are_contiguous(self) -> None:
        states = pd.Series(["UNKNOWN", "UNKNOWN", "UP", "UP", "RANGE", "DOWN", "DOWN"])
        runs = rdr010.state_runs(states)
        self.assertEqual(runs[["state", "duration"]].values.tolist(), [
            ["UNKNOWN", 2], ["UP", 2], ["RANGE", 1], ["DOWN", 2]
        ])
        transitions = rdr010.transition_counts(states)
        got = {(r.from_state, r.to_state): r.count for r in transitions.itertuples()}
        self.assertEqual(got, {("UNKNOWN", "UP"): 1, ("UP", "RANGE"): 1, ("RANGE", "DOWN"): 1})

    def test_false_signal_is_nonpositive_directional_future_return(self) -> None:
        frame = pd.DataFrame({
            "trendState": ["UP", "UP", "DOWN", "DOWN", "RANGE", "UNKNOWN"],
            "fwd_ret_1": [0.02, -0.01, -0.03, 0.04, 0.50, -0.50],
        })
        row = rdr010.directional_metric(frame, horizon=1, model="TrendEngine")
        self.assertEqual(row["n"], 4)
        self.assertAlmostEqual(row["hit_rate"], 0.5)
        self.assertAlmostEqual(row["false_signal_rate"], 0.5)
        self.assertAlmostEqual(row["expectancy"], 0.0)

    def test_no_trendengine_benchmark_is_always_long_on_every_eligible_bar(self) -> None:
        frame = pd.DataFrame({
            "trendState": ["UP", "DOWN", "RANGE", "UNKNOWN"],
            "fwd_ret_1": [0.02, -0.01, 0.03, np.nan],
        })
        row = rdr010.directional_metric(frame, horizon=1, model="No-TrendEngine benchmark")
        self.assertEqual(row["n"], 3)
        self.assertAlmostEqual(row["hit_rate"], 2 / 3)
        self.assertAlmostEqual(row["false_signal_rate"], 1 / 3)
        self.assertAlmostEqual(row["expectancy"], (0.02 - 0.01 + 0.03) / 3)

    def test_forward_returns_use_strict_future_close(self) -> None:
        frame = pd.DataFrame({"Close": [100.0, 110.0, 121.0, 100.0]})
        got = rdr010.add_forward_returns(frame, horizons=(1, 2))
        self.assertAlmostEqual(got.loc[0, "fwd_ret_1"], 0.10)
        self.assertAlmostEqual(got.loc[0, "fwd_ret_2"], 0.21)
        self.assertTrue(np.isnan(got.loc[3, "fwd_ret_1"]))

    def test_chronological_halves_are_nonoverlapping_and_exhaustive(self) -> None:
        labels = rdr010.chronological_halves(pd.Series([False, True, True, True, True, False]))
        self.assertEqual(labels.tolist(), ["excluded", "early", "early", "late", "late", "excluded"])

    def test_volatility_regimes_use_fixed_20_bar_rolling_vol_and_tertiles(self) -> None:
        close = pd.Series(100.0 * np.cumprod(1.0 + np.r_[np.zeros(20), [0.01, -0.01] * 20]))
        regimes, thresholds = rdr010.volatility_regimes(close, eligible=pd.Series([True] * len(close)))
        self.assertEqual(thresholds["window"], 20)
        self.assertEqual(set(regimes.dropna().unique()), {"low", "mid", "high"})
        self.assertLessEqual(thresholds["q33"], thresholds["q67"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
