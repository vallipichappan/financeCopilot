# quant_server.py
from mcp.server.fastmcp import FastMCP
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from datetime import datetime
from typing import Dict, Any, List

mcp = FastMCP("YahooFinanceQuant", dependencies=["yfinance", "pandas", "numpy", "scikit-learn"])

market_data_cache: Dict[str, pd.DataFrame] = {}

def fetch_stock_data(symbol: str, start="2020-01-01", end=None, interval="1d") -> pd.DataFrame:
    """Fetch stock OHLCV data from Yahoo Finance with caching."""
    cache_key = f"{symbol}_{interval}_{start}_{end}"
    if cache_key in market_data_cache:
        return market_data_cache[cache_key]
    
    df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
    df = df.rename(columns=str.lower)
    df.dropna(inplace=True)
    market_data_cache[cache_key] = df 
    return df

@mcp.tool()
def calculate_returns(symbol: str, start="2020-01-01", end=None) -> Dict[str, Any]:
    """Calculate daily returns for a stock."""
    df = fetch_stock_data(symbol, start, end)
    df["returns"] = df["adj close"].pct_change().dropna()
    
    return {
        "symbol": symbol,
        "start": start,
        "end": end or str(datetime.today().date()),
        "mean_return": df["returns"].mean(),
        "std_dev": df["returns"].std(),
        "data_points": len(df),
    }

@mcp.tool()
def calculate_volatility(symbol: str, window: int = 21, start="2020-01-01", end=None) -> Dict[str, Any]:
    """Calculate rolling volatility (annualized)."""
    df = fetch_stock_data(symbol, start, end)
    df["returns"] = df["adj close"].pct_change()
    df["volatility"] = df["returns"].rolling(window).std() * np.sqrt(252)
    latest_vol = df["volatility"].iloc[-1]
    
    return {
        "symbol": symbol,
        "window_days": window,
        "latest_volatility": latest_vol,
    }

@mcp.tool()
def calculate_sharpe(symbol: str, rf_rate: float = 0.02, start="2020-01-01", end=None) -> Dict[str, Any]:
    """Calculate Sharpe ratio for a stock."""
    df = fetch_stock_data(symbol, start, end)
    df["returns"] = df["adj close"].pct_change()
    excess_returns = df["returns"].mean() * 252 - rf_rate
    volatility = df["returns"].std() * np.sqrt(252)
    sharpe = excess_returns / volatility if volatility > 0 else None
    
    return {
        "symbol": symbol,
        "sharpe_ratio": sharpe,
        "period": f"{start} to {end or str(datetime.today().date())}"
    }

@mcp.tool()
def calculate_correlations(symbols: List[str], start="2020-01-01", end=None) -> Dict[str, Any]:
    """Calculate correlation matrix for multiple stocks."""
    data = {}
    for s in symbols:
        df = fetch_stock_data(s, start, end)
        data[s] = df["adj close"].pct_change()
    returns_df = pd.DataFrame(data).dropna()
    corr_matrix = returns_df.corr()
    
    return {
        "symbols": symbols,
        "correlation_matrix": corr_matrix.to_dict()
    }

@mcp.tool()
def perform_pca(symbols: List[str], start="2020-01-01", end=None, n_components: int = 3) -> Dict[str, Any]:
    """Perform PCA on stock returns to extract factors."""
    data = {}
    for s in symbols:
        df = fetch_stock_data(s, start, end)
        data[s] = df["adj close"].pct_change()
    returns_df = pd.DataFrame(data).dropna()
    
    pca = PCA(n_components=n_components)
    pca.fit(returns_df)
    
    return {
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "components": pca.components_.tolist(),
        "symbols": symbols,
    }

if __name__ == "__main__":
    result = fetch_stock_data("AAPL", start="2022-01-01", end="2023-01-01")
    print(result)