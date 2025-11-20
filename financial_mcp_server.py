from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from prompts import investment
from tools import analyst, dividends, financials, holders, sector, summary

load_dotenv()


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    server = FastMCP(
        "FinancialResearchServer",
        dependencies=[
            "requests",
            "pandas",
            "yfinance",
            "beautifulsoup4",
            "python-dotenv",
        ],
    )

    tool_modules = [
        summary,
        analyst,
        dividends,
        holders,
        sector,
        financials,
    ]

    for module in tool_modules:
        module.register(server)

    investment.register(server)

    return server


mcp = create_server()
