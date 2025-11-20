# from typing import Any, Dict
# from utils.api import AlphaVantageAPI
# from utils.data_model import market_data_cache, MarketData
# from datetime import datetime


# def calculate_moving_averages(symbol: str, short_period: int = 20, long_period: int = 50) -> Dict[str, Any]:
#     """
#     Calculate short and long moving averages for a symbol
    
#     Args:
#         symbol: The ticker symbol to analyze
#         short_period: Short moving average period in minutes
#         long_period: Long moving average period in minutes
        
#     Returns:
#         Dictionary with moving average data and analysis
#     """
#     cache_key = f"{symbol}_1min"
    
#     if cache_key not in market_data_cache:
#         df = AlphaVantageAPI.get_intraday_data(symbol, "1min", outputsize="full")
#         market_data_cache[cache_key] = MarketData(
#             symbol=symbol,
#             interval="1min",
#             data=df,
#             last_updated=datetime.now()
#         )
    
#     data = market_data_cache[cache_key].data
    
#     # Calculate moving averages
#     data[f'SMA{short_period}'] = data['close'].rolling(window=short_period).mean()
#     data[f'SMA{long_period}'] = data['close'].rolling(window=long_period).mean()
    
#     # Get latest values
#     latest = data.iloc[-1]
#     current_price = latest['close']
#     short_ma = latest[f'SMA{short_period}']
#     long_ma = latest[f'SMA{long_period}']
    
#     # Determine signal
#     if short_ma > long_ma:
#         signal = "BULLISH (Short MA above Long MA)"
#     elif short_ma < long_ma:
#         signal = "BEARISH (Short MA below Long MA)"
#     else:
#         signal = "NEUTRAL (MAs are equal)"
    
#     # Check for crossover in the last 5 periods
#     last_5 = data.iloc[-5:]
#     crossover = False
#     crossover_type = ""
    
#     for i in range(1, len(last_5)):
#         prev = last_5.iloc[i-1]
#         curr = last_5.iloc[i]
        
#         # Golden Cross (short crosses above long)
#         if prev[f'SMA{short_period}'] <= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] > curr[f'SMA{long_period}']:
#             crossover = True
#             crossover_type = "GOLDEN CROSS (Bullish)"
#             break
            
#         # Death Cross (short crosses below long)
#         if prev[f'SMA{short_period}'] >= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] < curr[f'SMA{long_period}']:
#             crossover = True
#             crossover_type = "DEATH CROSS (Bearish)"
#             break
    
#     return {
#         "symbol": symbol,
#         "current_price": current_price,
#         f"SMA{short_period}": short_ma,
#         f"SMA{long_period}": long_ma,
#         "signal": signal,
#         "crossover_detected": crossover,
#         "crossover_type": crossover_type if crossover else "None",
#         "analysis": f"""Moving Average Analysis for {symbol}:
# Current Price: ${current_price:.2f}
# {short_period}-period SMA: ${short_ma:.2f}
# {long_period}-period SMA: ${long_ma:.2f}
# Signal: {signal}
# Recent Crossover: {"Yes - " + crossover_type if crossover else "No"}

# Recommendation: {
#     "STRONG BUY" if crossover and crossover_type == "GOLDEN CROSS (Bullish)" else
#     "BUY" if signal == "BULLISH (Short MA above Long MA)" else
#     "STRONG SELL" if crossover and crossover_type == "DEATH CROSS (Bearish)" else
#     "SELL" if signal == "BEARISH (Short MA below Long MA)" else
#     "HOLD"
# }"""
#  }
 

# tools/moving_average.py
from typing import Any, Dict
from utils.api import YahooFinanceAPI
from utils.data_model import market_data_cache, MarketData
from datetime import datetime

def calculate_moving_averages(symbol: str, short_period: int = 20, long_period: int = 50) -> Dict[str, Any]:
    """
    Calculate short and long moving averages for a symbol using daily data
    
    Args:
        symbol: The ticker symbol to analyze
        short_period: Short moving average period in days
        long_period: Long moving average period in days
        
    Returns:
        Dictionary with moving average data and analysis
    """
    cache_key = f"{symbol}_daily_ma"
    
    if cache_key not in market_data_cache:
        # Get enough data to calculate the longer moving average
        periods_needed = max(long_period * 2, 200)  # Get extra data for accuracy
        df = YahooFinanceAPI.get_daily_data(symbol, period="1y")  # Get 1 year of data
        market_data_cache[cache_key] = MarketData(
            symbol=symbol,
            interval="1d",
            data=df,
            last_updated=datetime.now()
        )
    
    data = market_data_cache[cache_key].data
    
    # Calculate moving averages
    data[f'SMA{short_period}'] = data['close'].rolling(window=short_period).mean()
    data[f'SMA{long_period}'] = data['close'].rolling(window=long_period).mean()
    
    # Get latest values (drop NaN rows first)
    valid_data = data.dropna()
    if valid_data.empty:
        raise ValueError(f"Insufficient data to calculate moving averages for {symbol}")
    
    latest = valid_data.iloc[-1]
    current_price = latest['close']
    short_ma = latest[f'SMA{short_period}']
    long_ma = latest[f'SMA{long_period}']
    
    # Determine signal
    if short_ma > long_ma:
        signal = "BULLISH (Short MA above Long MA)"
    elif short_ma < long_ma:
        signal = "BEARISH (Short MA below Long MA)"
    else:
        signal = "NEUTRAL (MAs are equal)"
    
    # Check for crossover in the last 5 periods
    last_5 = valid_data.iloc[-5:]
    crossover = False
    crossover_type = ""
    
    if len(last_5) >= 2:  # Need at least 2 data points
        for i in range(1, len(last_5)):
            prev = last_5.iloc[i-1]
            curr = last_5.iloc[i]
            
            # Golden Cross (short crosses above long)
            if prev[f'SMA{short_period}'] <= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] > curr[f'SMA{long_period}']:
                crossover = True
                crossover_type = "GOLDEN CROSS (Bullish)"
                break
                
            # Death Cross (short crosses below long)
            if prev[f'SMA{short_period}'] >= prev[f'SMA{long_period}'] and curr[f'SMA{short_period}'] < curr[f'SMA{long_period}']:
                crossover = True
                crossover_type = "DEATH CROSS (Bearish)"
                break
    
    # Calculate distance from MAs
    price_vs_short_ma = ((current_price - short_ma) / short_ma) * 100
    price_vs_long_ma = ((current_price - long_ma) / long_ma) * 100
    
    return {
        "symbol": symbol,
        "current_price": float(current_price),
        f"SMA{short_period}": float(short_ma),
        f"SMA{long_period}": float(long_ma),
        "price_vs_short_ma_pct": float(price_vs_short_ma),
        "price_vs_long_ma_pct": float(price_vs_long_ma),
        "signal": signal,
        "crossover_detected": crossover,
        "crossover_type": crossover_type if crossover else "None",
        "analysis": f"""Moving Average Analysis for {symbol}:
Current Price: ${current_price:.2f}
{short_period}-day SMA: ${short_ma:.2f} ({price_vs_short_ma:+.1f}% from price)
{long_period}-day SMA: ${long_ma:.2f} ({price_vs_long_ma:+.1f}% from price)
Signal: {signal}
Recent Crossover: {"Yes - " + crossover_type if crossover else "No"}

Recommendation: {
    "STRONG BUY" if crossover and crossover_type == "GOLDEN CROSS (Bullish)" else
    "BUY" if signal == "BULLISH (Short MA above Long MA)" else
    "STRONG SELL" if crossover and crossover_type == "DEATH CROSS (Bearish)" else
    "SELL" if signal == "BEARISH (Short MA below Long MA)" else
    "HOLD"
}"""
    }