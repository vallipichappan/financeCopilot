from functools import lru_cache

import yfinance as yf


class InvalidTickerError(ValueError):
    """Raised when a ticker symbol is missing or invalid."""


@lru_cache(maxsize=256)
def get_ticker(symbol: str) -> yf.Ticker:
    """Return a cached yfinance.Ticker for the cleaned symbol."""
    if symbol is None:
        raise InvalidTickerError("Ticker symbol is required.")
    clean = symbol.strip().upper()
    if not clean:
        raise InvalidTickerError("Ticker symbol is required.")
    return yf.Ticker(clean)


