# financeCopilot

This is a playground for quantitative research workflows powered by Model Context Protocol (MCP) servers. It ships with:

- **`financial_mcp_server.py`** – a modular research assistant that wraps Yahoo Finance, SEC data and analyst intel.
- **`finance_server.py`** – the earlier QuantAssistant with classic TA tools (SMAs, returns, RSI, trade recos).

Credits for the original inspiration: [Syed Hasan’s MCP walkthrough](https://medium.com/@syed_hasan/step-by-step-guide-building-an-mcp-server-using-python-sdk-alphavantage-claude-ai-7a2bfb0c3096).

---

## Architecture

![Architecture Diagram](files/architecture.svg)

- `financial_mcp_server.py` is the only executable entry point. It loads environment variables, instantiates `FastMCP`, and registers every tool/prompt module via a `register(mcp)` hook.
- Each module under `tools/` keeps a single responsibility (summary, filings, analyst intel, etc.) and relies on shared helpers in `utils/`.
- Prompt templates such as `prompts/investment.py` remain isolated so they can be versioned separately or swapped at runtime.
- Legacy `finance_server.py` plus the TA modules (`tools/moving_average.py`, `tools/returns.py`, etc.) continue to power the QuantAssistant server; both MCP servers can run in parallel.

---

## What’s in the Financial MCP server?

| Module | Tool(s) | Description |
| --- | --- | --- |
| `tools/summary.py` | `get_stock_summary` | 5-day Yahoo Finance snapshot (price, volume, date). |
| `tools/analyst.py` | `get_analyst_targets`, `get_recommendations` | Analyst price targets and recommendation history. |
| `tools/dividends.py` | `get_dividends`, `get_splits` | Dividend and split history as simple dicts. |
| `tools/holders.py` | `get_institutional_holders`, `get_insider_transactions` | Institutional positions and insider trade logs. |
| `tools/sector.py` | `get_sector_info` | Sector & industry metadata. |
| `tools/financials.py` | `get_financial_statements` | Balance sheet, income statement, cashflow (nested dicts). |
| `prompts/investment.py` | `prompt_investment_thesis` | Ready-made user prompt for holistic theses. |


---

## Local setup (uv MCP → Claude Desktop)

### 1. Install requirements

```powershell
Python 3.11
pip install uv
```

Clone the repo and install dependencies with uv:

```powershell
git clone https://github.com/vallipichappan/financeCopilot.git
cd financeCopilot
uv sync
# `uv sync` reads `pyproject.toml` and pulls `mcp[cli]`, `yfinance`, `requests` 
```


### 2. Attach to Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` (on Windows; use `~/Library/Application Support/Claude` on macOS) and add both servers:

```json
{
  "mcpServers": {
    "FinancialResearchServer": {
      "command": "C:\\Users\\valli\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--with", "mcp[cli]",
        "--with", "pandas",
        "--with", "requests",
        "--with", "yfinance",
        "--with", "python-dotenv",
        "mcp",
        "run",
        "C:\\Users\\valli\\financeCopilot\\financial_mcp_server.py"
      ],
      "env": {
        "SEC_USER_AGENT": "Your Name or Company YourEmail@example.com"
      }
    },
    "QuantAssistant": {
      "command": "C:\\Users\\valli\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--with", "mcp[cli]",
        "--with", "pandas",
        "--with", "requests",
        "--with", "tabulate",
        "--with", "yfinance",
        "mcp",
        "run",
        "C:\\Users\\valli\\financeCopilot\\finance_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop. The “FinancialResearchServer” and “QuantAssistant” entries will appear in the MCP. Enable any of the tools available in chat. For QuantAssistant, env variables need to be set up. 

---

## Roadmap / ideas
- Instead of using claude desktop, it could be integrated with langchain for memory and conversation capabilities + web search api + llm connect
- App Development has to follow proper 3 tier structure 
- Swap Claude out with finbert
- More technical indicators & signal generation.
- Portfolio and risk analytics blocks.
- Natural-language query hub with RAG over filings.
- Visualisation stories (intraday dashboards, thematics).

---

## Output Links

- [Report 1](https://claude.ai/share/9e5fac93-b9b8-4455-b83e-50a5508fb41a)
- [Report 2](https://claude.ai/share/0193e817-540a-4cc6-8d54-caf4df29fc92)
- [Report 3](https://claude.ai/share/e0a6d949-b817-411a-ae37-cf1fd557f2d0)
- [Report 4](https://claude.ai/share/09ae70d4-2da9-400d-aa50-d8ff7f20f3b0)
