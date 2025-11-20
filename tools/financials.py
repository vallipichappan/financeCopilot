import pandas as pd

from utils.serialization import dataframe_to_nested_dict
from utils.yfinance_client import InvalidTickerError, get_ticker


def register(mcp):
    @mcp.tool()
    def get_financial_statements(ticker: str) -> dict:
        """Get balance sheet, income statement, and cashflow for a ticker."""
        try:
            stock = get_ticker(ticker)
            return {
                "balance_sheet": dataframe_to_nested_dict(
                    getattr(stock, "balance_sheet", pd.DataFrame())
                ),
                "income_statement": dataframe_to_nested_dict(
                    getattr(stock, "income_stmt", pd.DataFrame())
                ),
                "cashflow": dataframe_to_nested_dict(
                    getattr(stock, "cashflow", pd.DataFrame())
                ),
            }
        except InvalidTickerError:
            return {}
        except Exception as exc:
            return {"error": str(exc)}


