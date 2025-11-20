from typing import Mapping

from utils.serialization import dataframe_to_records, mapping_to_primitives, maybe_primitive
from utils.yfinance_client import InvalidTickerError, get_ticker


def register(mcp):
    @mcp.tool()
    def get_analyst_targets(ticker: str) -> dict:
        """Get analyst price targets for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            targets = getattr(stock, "analyst_price_targets", {})
            if isinstance(targets, Mapping):
                return mapping_to_primitives(targets)
            return {"data": maybe_primitive(targets)}
        except InvalidTickerError:
            return {}
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def get_recommendations(ticker: str) -> list:
        """Get analyst recommendations for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            recs = getattr(stock, "recommendations", None)
            return dataframe_to_records(recs)
        except InvalidTickerError:
            return []
        except Exception as exc:
            return [{"error": str(exc)}]


