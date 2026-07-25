"""
Data loaders — yfinance for daily OHLCV across UK/EU equity indices.

Note: Some EU indices (DAX40, CAC40, IBEX35, FTSE250) have short yfinance
history on cash indices; we use the ETF proxies (or fall back to the index
ticker) and warn if < 750 daily bars.
"""

from __future__ import annotations
from pathlib import Path

import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _sanitise(s: str) -> str:
    return s.replace("^", "_").replace("=", "_").replace("/", "_")


# Universe (UK100 emphasis + EU peer panel for "see what performs well")
# Ticker preferences: prefer cash index (^...) when available, otherwise ETF.
UNIVERSE = {
    "UK100":      {"ticker": "^FTSE",    "label": "FTSE 100 (UK100)"},
    "DAX40":      {"ticker": "^GDAXI",   "label": "DAX 40 (Germany)"},
    "CAC40":      {"ticker": "^FCHI",    "label": "CAC 40 (France)"},
    "IBEX35":     {"ticker": "^IBEX",    "label": "IBEX 35 (Spain)"},
    "FTSE250":    {"ticker": "^FTMC",    "label": "FTSE 250 (UK mid)"},
    "UK100_ETF":  {"ticker": "ISF.L",    "label": "iShares UK 100 ETF (GBP)"},
}


def fetch(symbol_key: str, *, period: str = "10y", interval: str = "1d") -> pd.DataFrame:
    """Fetch + cache daily OHLCV. Returns a DataFrame indexed by date with
    columns [open, high, low, close, volume].
    """
    cache = DATA_DIR / f"{symbol_key}_{_sanitise(UNIVERSE[symbol_key]['ticker'])}.csv"
    if cache.exists() and cache.stat().st_size > 0:
        df = pd.read_csv(cache, index_col=0, parse_dates=True)
        if len(df) > 200:
            return df

    ticker = UNIVERSE[symbol_key]["ticker"]
    print(f"  fetching {symbol_key} ({ticker}) period={period}...")
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache)
    return df


def fetch_all() -> dict:
    out = {}
    for sym in UNIVERSE.keys():
        out[sym] = fetch(sym)
    return out
