def register(mcp):
    @mcp.prompt()
    def prompt_investment_thesis(ticker: str) -> str:
        """Generates a user message requesting an investment thesis for a given ticker."""
        return (
            "Please act as a financial analyst. Using the available tools, "
            f"construct a detailed investment thesis for the stock '{ticker}'. "
            "Your thesis should include:\n"
            "1. A summary of the company and its business (sector, industry).\n"
            "2. Recent performance (stock price, volume).\n"
            "3. A financial health overview (from financial statements).\n"
            "4. Analyst sentiment (recommendations, price targets).\n"
            "5. Potential risks (insider transactions, institutional holder changes).\n"
            "6. A concluding summary of your buy, hold, or sell recommendation."
        )


