import pandas as pd

from utils.serialization import format_index_key, maybe_primitive
from utils.yfinance_client import InvalidTickerError, get_ticker


def _series_to_dict(series: pd.Series | None) -> dict:
    if isinstance(series, pd.Series):
        return {format_index_key(k): maybe_primitive(v) for k, v in series.items()}
    return {}


def register(mcp):
    @mcp.tool()
    def get_dividends(ticker: str) -> dict:
        """Get dividend history for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            return _series_to_dict(getattr(stock, "dividends", None))
        except InvalidTickerError:
            return {}
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def get_splits(ticker: str) -> dict:
        """Get stock split history for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            return _series_to_dict(getattr(stock, "splits", None))
        except InvalidTickerError:
            return {}
        except Exception as exc:
            return {"error": str(exc)}


