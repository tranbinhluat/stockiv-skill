# StockIV

AI-powered Vietnamese stock analysis using the **GCCP (Good Company, Cheap Price) framework**, powered by GitHub Copilot/Gemini subscription — zero extra API cost.

Interact via **GitHub Copilot chat** or **Antigravity** using slash commands. Two AI agents orchestrate eight atomic skills backed by plain Python CLI tools.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Set BRAVE_API_KEY, DISCORD_TOKEN, DISCORD_CHANNEL_TICKER, DISCORD_CHANNEL_WEEKLY

# 3. Open Copilot chat and run
/deepdive-flow FPT
/weely-flow
```

---

## Slash Commands

| Command | What it does |
|---|---|
| `/deepdive-flow FPT` | Full GCCP analysis: collect → sentiment → fundamentals → valuation → report → publish |
| `/weekly-flow` | Weekly macro market sentiment report + Discord publish |

---

## CLI Tools (invoked by AI skills)

```bash
# Collect financial data for a ticker (auto-skips if < 7 days old)
uv run stockiv-collect --ticker FPT --type all
uv run stockiv-collect --ticker FPT --force     # bypass freshness cache
uv run stockiv-collect --macro                  # macro market context

# Export markdown report to PDF
uv run stockiv-report --ticker FPT --format pdf

# Publish to Discord (summary post + PDF attachment)
uv run stockiv-publish --file reports/ticker/FPT_GCCP_report.pdf \
  --channel ticker --message "Your summary text here"

# Dev
uv run pre-commit run --all-files
.venv/bin/python -m pytest tests/test_cli.py -v
```

---

## Architecture

Two agents + eight skills. No orchestration framework, no paid API.

Custom subagent orchestration is now configured via workspace custom agents in `.github/agents`.

```
.github/agents/
├── deepdive-coordinator.agent.md   # Orchestrates deep-dive via worker subagents
├── weekly-coordinator.agent.md     # Orchestrates weekly macro flow
├── data-collector.agent.md
├── sentiment-analyst.agent.md
├── fundamentals-analyst.agent.md
├── valuation-analyst.agent.md
├── gatekeeper-reviewer.agent.md
├── report-drafter.agent.md
└── discord-publisher.agent.md

.agents/agents/stock-analyst.md   — GCCP analysis specialist
.agents/agents/gatekeeper.md      — quality validator (8-check gate)
```

| Skill | Slash Command | Purpose |
|---|---|---|
| `deepdive-flow` | `/deepdive-flow <TICKER>` | Full analysis pipeline |
| `weekly-flow` | `/weekly-flow` | Weekly macro report |
| `collect-data` | `/collect <TICKER>` | Fetch financials + annual report |
| `analyze-sentiment` | `/sentiment [TICKER]` | Macro + ticker sentiment |
| `analyze-fundamentals` | `/fundamentals <TICKER>` | GCCP Parts II + III |
| `analyze-valuation` | `/valuation <TICKER>` | Target price, Parts IV + V |
| `draft-report` | `/report [TICKER]` | Compile + export PDF |
| `publish-discord` | `/publish` | Discord summary-post + PDF |

### Deep Dive flow
```
collect-data → analyze-sentiment → analyze-fundamentals → analyze-valuation
                                         ↑ (sentiment feeds fundamentals)
→ gatekeeper (8-check gate, max 5 revisions) → draft-report → publish-discord
```

### Subagent controls

- Coordinators use explicit worker allowlists (`agents` frontmatter)
- Internal workers set `user-invocable: false`
- Sensitive workers (`Gatekeeper Reviewer`, `Discord Publisher`) set `disable-model-invocation: true`
- Nested subagents are disabled via workspace setting (`chat.subagents.allowInvocationsFromSubagents: false`)

---

## Project Structure

```
stock-agent/
├── .agents/
│   ├── agents/
│   │   ├── stock-analyst.md        # GCCP analyst persona
│   │   └── gatekeeper.md           # Quality validator persona
│   └── skills/
│       ├── deepdive-flow/          # /deepdive-flow orchestration
│       ├── weekly-flow/            # /weekly-flow orchestration
│       ├── collect-data/           # Fetch financials + context + annual report
│       ├── analyze-sentiment/      # Macro sentiment + recent-trends synthesis
│       ├── analyze-fundamentals/   # GCCP Parts II + III + forensic checks
│       ├── analyze-valuation/      # GCCP Parts IV + V + target price
│       ├── draft-report/           # Compile report + PDF export
│       └── publish-discord/        # Discord summary-post + PDF attach
├── src/stockiv/
│   ├── cli.py                      # stockiv-collect / stockiv-report / stockiv-publish
│   ├── config/                     # paths.py, discord.py
│   ├── knowledge/                  # GCCP framework docs (read by AI skills)
│   └── utils/                      # Logger
├── tools/                          # Pure Python helpers (called by CLI)
│   ├── vnstock_tools.py            # Vietnamese stock data via vnstock API
│   ├── sqlite_tools.py             # SQLite financial database queries
│   ├── brave_tools.py              # Brave Search for news context
│   ├── report_finder_tools.py      # Annual report PDF download + conversion
│   ├── pdf_exporter_tool.py        # Markdown → PDF via WeasyPrint
│   ├── discord_publisher_tool.py   # Discord message + file publishing
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
