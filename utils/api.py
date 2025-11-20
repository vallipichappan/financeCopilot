# # utils/api.py
# import os
# from typing import Optional
# import requests
# import pandas as pd
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY = os.getenv("ALPHAVANTAGE_API_KEY") 

# class AlphaVantageAPI:
#     @staticmethod
#     def _check_api_key():
#         if not API_KEY:
#             raise RuntimeError("Alpha Vantage API key not configured. Set ALPHAVANTAGE_API_KEY.")

#     @staticmethod
#     def get_intraday_data(symbol: str, interval: str = "1min", outputsize: str = "compact") -> pd.DataFrame:
#         AlphaVantageAPI._check_api_key()
#         url = (
#             f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
#         )
#         response = requests.get(url, timeout=30)
#         response.raise_for_status()
#         data = response.json()

#         key = f"Time Series ({interval})"
#         if key not in data:
#             # surface API error message if present
#             raise ValueError(data.get("Note") or data.get("Error Message") or f"No time series data for {symbol}")

#         df = pd.DataFrame.from_dict(data[key], orient="index")
#         df.index = pd.to_datetime(df.index)
#         df = df.sort_index()
#         df.columns = [c.split(". ")[1] for c in df.columns]
#         df = df.apply(pd.to_numeric, errors="coerce")
#         # standardize column names to lowercase
#         df.columns = [c.lower().replace(" ", "_") for c in df.columns]
#         return df

#     @staticmethod
#     def get_daily_adjusted(symbol: str, outputsize: str = "compact") -> pd.DataFrame:
#         """
#         Fetch TIME_SERIES_DAILY_ADJUSTED. Returns DataFrame indexed by date (UTC),
#         columns: open, high, low, close, adjusted_close, volume, dividend_amount, split_coefficient
#         """
#         AlphaVantageAPI._check_api_key()
#         url = (
#             f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize={outputsize}&apikey={API_KEY}"
#         )
#         response = requests.get(url, timeout=30)
#         response.raise_for_status()
#         data = response.json()

#         key = "Time Series (Daily)"
#         if key not in data:
#             raise ValueError(data.get("Note") or data.get("Error Message") or f"No daily data for {symbol}")

#         df = pd.DataFrame.from_dict(data[key], orient="index")
#         df.index = pd.to_datetime(df.index)
#         df = df.sort_index()
#         # Map the verbose AV columns to normalized names
#         col_map = {
#             "1. open": "open",
#             "2. high": "high",
#             "3. low": "low",
#             "4. close": "close",
#             "5. adjusted close": "adjusted_close",
#             "6. volume": "volume",
#             "7. dividend amount": "dividend_amount",
#             "8. split coefficient": "split_coefficient",
#         }
#         df = df.rename(columns=col_map)
#         df = df.apply(pd.to_numeric, errors="coerce")
#         return df

# utils/api.py
import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

class YahooFinanceAPI:
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = "1m", period: str = "1d") -> pd.DataFrame:
        """
        Fetch intraday data from Yahoo Finance
        
        Args:
            symbol: Stock symbol
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No intraday data found for {symbol}")
        
        # Standardize column names to lowercase with underscores
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        
        return df
    
    @staticmethod
    def get_daily_data(symbol: str, start: Optional[str] = None, end: Optional[str] = None, period: str = "1y") -> pd.DataFrame:
        """
        Fetch daily historical data
        
        Args:
            symbol: Stock symbol
            start: Start date (YYYY-MM-DD format)
            end: End date (YYYY-MM-DD format)
            period: Period if start/end not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        ticker = yf.Ticker(symbol)
        
        if start and end:
            df = ticker.history(start=start, end=end)
        elif start:
            df = ticker.history(start=start)
        else:
            df = ticker.history(period=period)
        
        if df.empty:
            raise ValueError(f"No daily data found for {symbol}")
        
        # Standardize column names
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        
        return df
    
    @staticmethod
    def get_stock_info(symbol: str) -> dict:
        """Get stock information and metadata"""
        ticker = yf.Ticker(symbol)
        return ticker.info