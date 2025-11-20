# financeCopilot

This is a playground for quantitative research workflows powered by Model Context Protocol (MCP) servers. It ships with:

- **`financial_mcp_server.py`** – a modular research assistant that wraps Yahoo Finance, SEC data and analyst intel.
- **`finance_server.py`** – the earlier QuantAssistant with classic TA tools (SMAs, returns, RSI, trade recos).

Credits for the original inspiration: [Syed Hasan’s MCP walkthrough](https://medium.com/@syed_hasan/step-by-step-guide-building-an-mcp-server-using-python-sdk-alphavantage-claude-ai-7a2bfb0c3096).

---

## Architecture

<svg width="1000" height="700" viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg">

  <!-- Arrow marker -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#333" />
    </marker>
  </defs>

  <!-- Styles -->
  <style>
    .box { fill:#f8f8f8; stroke:#333; stroke-width:1.2; rx:6; }
    text { font-family: Arial, sans-serif; font-size:14px; }
    .header { font-size:16px; font-weight:bold; }
  </style>

  <!-- MCP Client -->
  <rect class="box" x="40" y="40" width="260" height="80" />
  <text x="55" y="75" class="header">Claude Desktop / MCP Client</text>
  <text x="55" y="100">JSON‑RPC</text>

  <!-- Server -->
  <rect class="box" x="370" y="40" width="280" height="80" />
  <text x="385" y="75" class="header">financial_mcp_server.py</text>
  <text x="385" y="100">Registers tools • Routes requests</text>

  <!-- Arrow Client → Server -->
  <line x1="300" y1="80" x2="370" y2="80"
        stroke="#333" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Tools Box -->
  <rect class="box" x="370" y="160" width="280" height="350" />
  <text x="385" y="190" class="header">Tools</text>

  <text x="385" y="220">• summary</text>
  <text x="385" y="245">• filings</text>
  <text x="385" y="270">• analyst</text>
  <text x="385" y="295">• dividends</text>
  <text x="385" y="320">• holders</text>
  <text x="385" y="345">• sector</text>
  <text x="385" y="370">• financials</text>
  <text x="385" y="395">• prompts/*</text>

  <!-- Arrow Server → Tools -->
  <line x1="510" y1="120" x2="510" y2="160"
        stroke="#333" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Yahoo Finance -->
  <rect class="box" x="720" y="200" width="230" height="150" />
  <text x="740" y="235" class="header">Yahoo Finance API</text>
  <text x="740" y="260">Prices / Financials</text>
  <text x="740" y="285">Dividends / Analysts</text>

  <!-- Tools → Yahoo -->
  <line x1="650" y1="260" x2="720" y2="260"
        stroke="#333" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Utils -->
  <rect class="box" x="40" y="200" width="260" height="200" />
  <text x="55" y="235" class="header">Utils</text>
  <text x="55" y="265">• serialization</text>
  <text x="55" y="290">• yfinance_client</text>
  <text x="55" y="315">• sec</text>

  <!-- Tools → Utils -->
  <line x1="370" y1="300" x2="300" y2="300"
        stroke="#333" stroke-width="2" marker-end="url(#arrow)" />
</svg>

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
else mcp + langchain for memory and conversation capabilities + web search api + llm connect
follow proper 3 - tier structure for 
swap it out with finbert
- More technical indicators & signal generation.
- Portfolio and risk analytics blocks.
- Natural-language query hub with RAG over filings.
- Visualization stories (intraday dashboards, thematics).

