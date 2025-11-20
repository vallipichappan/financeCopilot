from utils.serialization import maybe_primitive
from utils.yfinance_client import InvalidTickerError, get_ticker


def register(mcp):
    @mcp.tool()
    def get_sector_info(ticker: str) -> dict:
        """Get sector and industry information for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            info = getattr(stock, "info", {})
            if not isinstance(info, dict):
                return {"data": maybe_primitive(info)}
            return {
                "sector": maybe_primitive(info.get("sector")),
                "industry": maybe_primitive(info.get("industry")),
            }
        except InvalidTickerError:
            return {}
        except Exception as exc:
            return {"error": str(exc)}


