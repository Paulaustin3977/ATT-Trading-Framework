#!/usr/bin/env python3
"""Walk-forward grid for the 6 ATE v2.2 arms across the 6-symbol panel.

Run from project root:
    .venv/bin/python scripts/optimize.py

Outputs results/optimization/{walk_forward_results.csv, walk_forward_summary.csv,
winner.json, winner_per_symbol.csv}.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.optimizer import main  # noqa: E402

if __name__ == "__main__":
    main()
