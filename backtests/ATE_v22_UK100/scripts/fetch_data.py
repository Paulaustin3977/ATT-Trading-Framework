#!/usr/bin/env python3
"""Fetch 6-symbol EU/UK index panel. Outputs to data/*.csv."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import fetch_all  # noqa: E402

if __name__ == "__main__":
    dfs = fetch_all()
    for sym, df in dfs.items():
        print(f"  {sym:>8s}: {len(df):>5d} bars | {df.index[0].date()} → {df.index[-1].date()}")
