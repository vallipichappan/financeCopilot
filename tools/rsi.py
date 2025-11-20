from typing import Any, Dict
from utils.api import AlphaVantageAPI
from utils.data_model import market_data_cache, MarketData
from datetime import datetime


def calculate_rsi(symbol: str, period: int = 14) -> Dict[str, Any]:
    """
    Calculate Relative Strength Index (RSI) for a symbol
    
    Args:
        symbol: The ticker symbol to analyze
        period: RSI calculation period in minutes
        
    Returns:
        Dictionary with RSI data and analysis
    """
    cache_key = f"{symbol}_1min"
    
    if cache_key not in market_data_cache:
        df = AlphaVantageAPI.get_intraday_data(symbol, "1min", outputsize="full")
        market_data_cache[cache_key] = MarketData(
            symbol=symbol,
            interval="1min",
            data=df,
            last_updated=datetime.now()
        )
    
    data = market_data_cache[cache_key].data.copy()
    

    delta = data['close'].diff()
    
    # Create gain and loss series
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    loss = abs(loss)
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Get latest RSI
    latest_rsi = rsi.iloc[-1]
    
    # Determine signal
    if latest_rsi < 30:
        signal = "OVERSOLD (Potential buy opportunity)"
    elif latest_rsi > 70:
        signal = "OVERBOUGHT (Potential sell opportunity)"
    else:
        signal = "NEUTRAL"
    
    return {
        "symbol": symbol,
        "period": period,
        "rsi": latest_rsi,
        "signal": signal,
        "analysis": f"""RSI Analysis for {symbol}:
{period}-period RSI: {latest_rsi:.2f}
Signal: {signal}

Recommendation: {
    "BUY" if latest_rsi < 30 else
    "SELL" if latest_rsi > 70 else
    "HOLD"
}"""
    }
