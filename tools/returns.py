# # analysis.py
# from typing import Dict, Any, Optional
# from datetime import datetime, date
# import pandas as pd

# from utils.api import AlphaVantageAPI
# from utils.data_model import market_data_cache, MarketData
 


# # New: unified daily fetch with caching
# def fetch_stock_data(symbol: str, start: str = "2020-01-01", end: Optional[str] = None) -> pd.DataFrame:
#     """
#     Returns a filtered daily-adjusted price DataFrame with at least 'adjusted_close'.
#     Uses local cache keyed by symbol_1d.
#     """
#     cache_key = f"{symbol}_1d"
#     if cache_key not in market_data_cache:
#         df_daily = AlphaVantageAPI.get_daily_adjusted(symbol, outputsize="full")
#         print(df_daily)
#         market_data_cache[cache_key] = MarketData(symbol, "1d", df_daily, datetime.now())
#     else:
#         df_daily = market_data_cache[cache_key].data

#     # Filter by date range
#     start_dt = pd.to_datetime(start).tz_localize(None)
#     end_dt = pd.to_datetime(end).tz_localize(None) if end else None

#     df = df_daily.copy()
#     df.index = pd.to_datetime(df.index).tz_localize(None)

#     if end_dt:
#         df = df.loc[(df.index >= start_dt) & (df.index <= end_dt)]
#     else:
#         df = df.loc[df.index >= start_dt]

#     if df.empty:
#         raise ValueError(f"No daily data in range for {symbol} from {start} to {end or 'today'}")

#     return df

# # Integrated daily returns calculation
# def calculate_returns(symbol: str, start: str = "2020-01-01", end: Optional[str] = None) -> Dict[str, Any]:
#     """
#     Calculate daily simple returns based on adjusted close.
#     """
#     df = fetch_stock_data(symbol, start, end)

#     # Prefer adjusted_close if available; fall back to close
#     price_col = "adjusted_close" if "adjusted_close" in df.columns else "close"
#     if price_col not in df.columns:
#         raise ValueError("Required price column not found in daily data")

#     # Compute returns; pct_change naturally introduces a NaN at the first row
#     returns = df[price_col].pct_change()
#     returns = returns.dropna()

#     result = {
#         "symbol": symbol,
#         "start": start,
#         "end": end or str(date.today()),
#         "mean_return": float(returns.mean()),
#         "std_dev": float(returns.std()),
#         "data_points": int(returns.shape[0]),
#     }
#     return result

# tools/returns.py
from typing import Dict, Any, Optional
from datetime import datetime, date
import pandas as pd

from utils.api import YahooFinanceAPI
from utils.data_model import market_data_cache, MarketData

def fetch_stock_data(symbol: str, start: str = "2020-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """
    Returns a filtered daily price DataFrame.
    Uses local cache keyed by symbol_1d.
    """
    cache_key = f"{symbol}_1d"
    
    if cache_key not in market_data_cache:
        # Use Yahoo Finance API
        df_daily = YahooFinanceAPI.get_daily_data(
            symbol, 
            start="2020-01-01",  # Get full history for cache
            end=end
        )
        market_data_cache[cache_key] = MarketData(symbol, "1d", df_daily, datetime.now())
    else:
        df_daily = market_data_cache[cache_key].data

    # Filter by date range if needed
    if start or end:
        start_dt = pd.to_datetime(start) if start else None
        end_dt = pd.to_datetime(end) if end else None

        df = df_daily.copy()
        
        if start_dt and end_dt:
            df = df.loc[(df.index >= start_dt) & (df.index <= end_dt)]
        elif start_dt:
            df = df.loc[df.index >= start_dt]
        elif end_dt:
            df = df.loc[df.index <= end_dt]
    else:
        df = df_daily.copy()

    if df.empty:
        raise ValueError(f"No daily data in range for {symbol} from {start} to {end or 'today'}")

    return df

def calculate_returns(symbol: str, start: str = "2020-01-01", end: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate daily simple returns based on adjusted close.
    """
    df = fetch_stock_data(symbol, start, end)

    # Yahoo Finance provides 'close' and 'adj_close' columns
    price_col = "close"  # Yahoo Finance already adjusts the 'close' price
    if price_col not in df.columns:
        raise ValueError("Required price column not found in daily data")

    # Compute returns
    returns = df[price_col].pct_change().dropna()

    # Calculate additional metrics
    annualized_return = returns.mean() * 252  # 252 trading days per year
    annualized_volatility = returns.std() * (252 ** 0.5)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0

    result = {
        "symbol": symbol,
        "start": start,
        "end": end or str(date.today()),
        "mean_daily_return": float(returns.mean()),
        "annualized_return": float(annualized_return),
        "daily_volatility": float(returns.std()),
        "annualized_volatility": float(annualized_volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "total_return": float((df[price_col].iloc[-1] / df[price_col].iloc[0]) - 1),
        "data_points": int(returns.shape[0]),
        "min_return": float(returns.min()),
        "max_return": float(returns.max())
    }
    return result