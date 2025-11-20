from datetime import date
from mcp.server.fastmcp import FastMCP
from tools.moving_average import calculate_moving_averages
from tools.returns import calculate_returns
# from tools.rsi import calculate_rsi
# from tools.trade_reco import trade_recommendation

mcp = FastMCP("QuantAssistant", dependencies=["requests", "pandas", "tabulate", "yfinance"])

# Register tools
@mcp.tool()
def sma_tool(symbol: str, short_period: int = 20, long_period: int = 50):
    return calculate_moving_averages(symbol, short_period, long_period)

# @mcp.tool()
# def rsi_tool(symbol: str, period: int = 14):
#     return calculate_rsi(symbol, period)

# @mcp.tool()
# def trade_reco_tool(symbol: str):
#     return trade_recommendation(symbol)

@mcp.tool()
def fetch_returns_tool(symbol: str, start: str = "2020-01-01", end: str = str(date.today())):
    return calculate_returns(symbol, start, end)


