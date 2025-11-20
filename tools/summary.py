from utils.yfinance_client import InvalidTickerError, get_ticker


def register(mcp):
    @mcp.tool()
    def get_stock_summary(ticker: str) -> str:
        """Get a basic stock summary using Yahoo Finance for a given stock ticker."""
        try:
            stock = get_ticker(ticker)
            hist = stock.history(period="5d")
            if hist.empty:
                return f"No recent data found for {stock.ticker}."
            latest = hist.iloc[-1]
            close_price = float(latest["Close"])
            volume = int(latest["Volume"])
            trade_date = latest.name.date()
            summary = (
                f"{stock.ticker} Summary:\n"
                f"Close Price: ${close_price:.2f}\n"
                f"Volume: {volume}\n"
                f"Date: {trade_date}\n"
            )
            return summary
        except InvalidTickerError as error:
            return f"Error: {error}"
        except Exception as exc:
            return f"Error retrieving stock data for {ticker}: {exc}"


