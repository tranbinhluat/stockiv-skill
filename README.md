# StockIV

AI-powered Vietnamese stock analysis using the **GCCP (Good Company, Cheap Price) framework**, powered by GitHub Copilot/Gemini subscription — zero extra API cost.

Users interact via **GitHub Copilot chat** or **Antigravity** using slash commands. Analysis flows are orchestrated by two AI agents backed by six atomic skills.

## Quick Start

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Set BRAVE_API_KEY, DISCORD_TOKEN, DISCORD_CHANNEL_TICKER, DISCORD_CHANNEL_WEEKLY

# Run pre-commit hooks
uv run pre-commit run --all-files
```

---

## Usage — Copilot Chat Slash Commands

Open GitHub Copilot chat and use these commands:

| Command | What it does |
|---|---|
| `/deepdive FPT` | Full GCCP analysis: collect → sentiment → fundamentals → valuation → report → publish |
| `/weekly` | Weekly macro market sentiment report |
| `/collect FPT` | Fetch/refresh financial data for a ticker |
| `/sentiment FPT` | Ticker + macro sentiment analysis only |
| `/fundamentals FPT` | GCCP qualitative + quantitative analysis |
| `/valuation FPT` | Target price and valuation verdict |
| `/report FPT` | Compile and export report to PDF |
| `/publish --file path.md --channel ticker` | Publish report to Discord |

---

## CLI Commands (called by AI skills)

The AI skills invoke these CLI tools via `uv run`:

```bash
# Collect financial data for a ticker (auto-skips if < 7 days old)
uv run stockiv-collect --ticker FPT --type all
uv run stockiv-collect --ticker FPT --force   # bypass freshness cache
uv run stockiv-collect --macro                # macro market context

# Export markdown report to PDF
uv run stockiv-report --ticker FPT --format pdf

# Publish report to Discord
uv run stockiv-publish --file reports/ticker/FPT_GCCP_report.md --channel ticker --attach-pdf

# Dev tools
uv run pre-commit run --all-files
.venv/bin/python -m pytest tests/test_cli.py -v
```

---

## Architecture

```
Before (CrewAI)                       After (Copilot Skills)
──────────────────────────────────    ──────────────────────────────────
orchestrator + director crew     →    gatekeeper agent  (validates + routes)
collector + sentiment + synth    →    stock-analyst agent (orchestrates)
DeepDiveFlow                     →    /deepdive <TICKER> slash command
WeeklyReportFlow                 →    /weekly slash command
Crews with @tool functions       →    Skills calling uv run CLI tools
Qwen/DashScope API (paid)        →    GitHub Copilot / Gemini (subscription)
```

### 2 Agents (`.agents/skills/`)
- **`stock-analyst`** — GCCP analysis specialist. Handles `/deepdive`, `/report`, `/collect`, etc.
- **`gatekeeper`** — Quality validator + router. 5-check validation gate. Routes all slash commands.

### 6 Skills (`.agents/skills/`)
| Skill | Slash Command | Replaces |
|---|---|---|
| `collect-data` | `/collect <TICKER>` | CollectorCrew |
| `analyze-sentiment` | `/sentiment [TICKER]` | SentimentAnalystCrew |
| `analyze-fundamentals` | `/fundamentals <TICKER>` | SynthesizerCrew (qualitative) |
| `analyze-valuation` | `/valuation <TICKER>` | SynthesizerCrew (valuation) |
| `draft-report` | `/report [TICKER]` | ReporterCrew |
| `publish-discord` | `/publish` | ReporterCrew (Discord) |

### Analysis Flow (Deep Dive)
```
collect-data → analyze-sentiment → analyze-fundamentals → analyze-valuation
                                         ↑ (sentiment feeds fundamentals)
→ gatekeeper validate → draft-report → publish-discord
```

---

## Project Structure

```
stock-agent/
├── .agents/
│   └── skills/
│       ├── stock-analyst/          # Agent persona + orchestration
│       ├── gatekeeper/             # Validator + slash command routing
│       ├── collect-data/           # Fetch financial data + context
│       ├── analyze-sentiment/      # Macro + ticker sentiment
│       ├── analyze-fundamentals/   # GCCP Parts II + III
│       ├── analyze-valuation/      # GCCP Parts IV + V + target price
│       ├── draft-report/           # Compile report + PDF export
│       └── publish-discord/        # Discord publishing
├── src/stockiv/
│   ├── cli.py                      # CLI: stockiv-collect/report/publish
│   ├── config/                     # paths.py, discord.py
│   ├── knowledge/                  # GCCP framework docs (read by AI skills)
│   └── utils/                      # Logger, etc.
├── tools/                          # Pure Python tools (no CrewAI decorators)
│   ├── vnstock_tools.py            # Vietnamese stock data via vnstock API
│   ├── sqlite_tools.py             # SQLite financial database queries
│   ├── brave_tools.py              # Brave Search for news context
│   ├── report_finder_tools.py      # Annual report PDF download + conversion
│   ├── pdf_exporter_tool.py        # Markdown → PDF via WeasyPrint
│   ├── discord_publisher_tool.py   # Discord message chunking + publishing
│   └── cache_tools.py              # Cache cleanup
├── tests/
│   └── test_cli.py                 # CLI unit tests (14 tests)
├── data/                           # Runtime data (gitignored)
├── reports/                        # Generated reports
├── Slave/                          # AI identity + long-term memory
├── memory/                         # Daily progress logs
└── pyproject.toml
```

---

## GCCP Framework

The **Good Company, Cheap Price** framework guides all analysis:

- **Part II** — Qualitative: Industry classification, Lynch category, Business model, Management governance
- **Part III** — Quantitative: ROE > 15%, ROA > 6% (5Y), OCF > Net Income, FCF > 5%
- **Part IV** — Market phase (VNINDEX P/E) + Graham 9-point checklist
- **Part V** — Target price: Fair Value Multiple × EPS/BV → Fair Value → 25% MOS → Target Buy Price

**Key rules (never violated):**
- Net Profit CAGR for Lynch PEG (not EPS CAGR — Vietnamese dividends distort EPS)
- Graham checklist copied verbatim from collected data, never recalculated
- All arithmetic via `uv run python -c` — never in LLM head
- `Current Price < Target Buy Price` = BUY NOW (never inverted)

---

## Environment Variables

```bash
BRAVE_API_KEY=          # Brave Search API key (news context)
DISCORD_TOKEN=          # Discord bot token
DISCORD_CHANNEL_TICKER= # Channel ID for ticker reports
DISCORD_CHANNEL_WEEKLY= # Channel ID for weekly reports
DISCORD_CHANNEL_DEFAULT=# Fallback channel
```

See `.env.example` for the full list.

## Resources

- [vnstock Documentation](https://docs.vnstock.site/)
- GCCP Framework: `src/stockiv/knowledge/framework.md`
