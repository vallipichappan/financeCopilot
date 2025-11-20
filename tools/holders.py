from utils.serialization import dataframe_to_records
from utils.yfinance_client import InvalidTickerError, get_ticker


def register(mcp):
    @mcp.tool()
    def get_institutional_holders(ticker: str) -> list:
        """Get institutional holders for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            holders = getattr(stock, "institutional_holders", None)
            return dataframe_to_records(holders)
        except InvalidTickerError:
            return []
        except Exception as exc:
            return [{"error": str(exc)}]

    @mcp.tool()
    def get_insider_transactions(ticker: str) -> list:
        """Get insider transactions for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            insiders = getattr(stock, "insider_transactions", None)
            return dataframe_to_records(insiders)
        except InvalidTickerError:
            return []
        except Exception as exc:
            return [{"error": str(exc)}]


