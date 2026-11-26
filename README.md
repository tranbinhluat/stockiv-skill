# StockIV

AI-powered Vietnamese stock analysis using the **GCCP (Good Company, Cheap Price) framework**, powered by GitHub Copilot/Gemini subscription — zero extra API cost.

Interact via **opencode** or **Claude Code** using slash commands. One primary agent (`stock-analyst`) delegates to two subagents (`market-scout`, `gatekeeper-reviewer`) and orchestrates ten skills backed by plain Python CLI tools.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Set BRAVE_API_KEY, DISCORD_TOKEN, DISCORD_CHANNEL_TICKER, DISCORD_CHANNEL_WEEKLY

# 3. Open opencode and run
/deepdive FPT
/weekly
```

In **Claude Code**, run `claude` in the repo root. `stock-analyst` is the default agent (from `.claude/settings.json`) and the same slash commands work: `/deepdive FPT`, `/weekly`.

---

## Slash Commands

| Command | What it does |
|---|---|
| `/deepdive <TICKER>` | Full GCCP analysis: collect → sentiment → fundamentals → valuation → gatekeeper → report → publish |
| `/compare TICKER1 TICKER2` | Side-by-side GCCP comparison of two tickers (gatekeeper runs once) |
| `/weekly` | Weekly macro market sentiment report + Discord publish |
| `/collect <TICKER>` | Fetch financials + news context for a ticker |
| `/sentiment [TICKER]` | Macro sentiment, or ticker sentiment if given |
| `/fundamentals <TICKER>` | GCCP Parts II + III quality assessment |
| `/valuation <TICKER>` | GCCP Parts IV + V target price |
| `/report [TICKER]` | Compile report + export PDF |
| `/publish` | Publish report to Discord |

---

## CLI Tools (invoked by AI skills)

```bash
# Collect financial data for a ticker (auto-skips if < 7 days old)
uv run stockiv-collect --ticker FPT --type all
uv run stockiv-collect --ticker FPT --force     # bypass freshness cache
uv run stockiv-collect --macro                  # macro market context (VNINDEX snapshot only — news is gathered by market-scout via stockiv-scout)

# News context — gathered by the market-scout subagent, not stockiv-collect
uv run stockiv-scout --scope FPT --query "FPT earnings 2026" --days-back 14

# Export markdown report to PDF
uv run stockiv-report --ticker FPT --format pdf

# Publish to Discord (summary post + PDF attachment)
uv run stockiv-publish --file data/report/FPT/FPT_GCCP_report.pdf \
  --channel ticker --message "Your summary text here"

# Dev
uv run pre-commit run --all-files
uv run pytest tests/ -v
```

---

## Architecture

One primary agent + two subagents + ten skills. No orchestration framework, no paid API. Runs on **opencode** (`.opencode/`).

```
.opencode/
├── agent/
│   ├── stock-analyst.md          # primary — GCCP analyst persona, delegates to subagents
│   ├── market-scout.md           # subagent — news/context research (websearch, webfetch)
│   └── gatekeeper-reviewer.md    # subagent — 8-check quality gate before publish
├── command/                      # slash command definitions ($ARGUMENTS → skill)
│   ├── deepdive.md, compare.md, weekly.md
│   ├── collect.md, sentiment.md, fundamentals.md, valuation.md
│   ├── report.md, publish.md
└── skills/                       # SKILL.md instructions used by stock-analyst
    ├── deepdive-flow/            # /deepdive orchestration
    ├── compare-flow/             # /compare orchestration (peer analysis)
    ├── weekly-flow/              # /weekly orchestration
    ├── collect-data/             # Fetch financials + context + annual report
    ├── analyze-sentiment/        # Macro sentiment + recent-trends synthesis
    ├── analyze-fundamentals/     # GCCP Parts II + III + forensic checks
    ├── analyze-valuation/        # GCCP Parts IV + V + target price
    ├── draft-report/             # Compile report + PDF export
    ├── publish-discord/          # Discord summary-post + PDF attach
    └── skill-creator/            # Create/edit/eval skills
```

Claude Code mirror (`.claude/`):

```
.claude/
├── settings.json                 # "agent": "stock-analyst" default, permissions mirror opencode.json
├── skills -> ../.opencode/skills # symlink, skills shared with opencode
├── agents/                       # stock-analyst, market-scout, gatekeeper-reviewer, annual-report-scanner
└── commands/                     # same 10 slash commands as .opencode/command/
```

Agent and command bodies mirror `.opencode/`; parity is enforced by `tests/test_claude_parity.py`. Claude models: stock-analyst and market-scout = sonnet, gatekeeper-reviewer = opus, annual-report-scanner = haiku.

| Skill | Slash Command | Purpose |
|---|---|---|
| `deepdive-flow` | `/deepdive <TICKER>` | Full analysis pipeline |
| `compare-flow` | `/compare TICKER1 TICKER2` | Side-by-side GCCP peer comparison |
| `weekly-flow` | `/weekly` | Weekly macro report |
| `collect-data` | `/collect <TICKER>` | Fetch financials + annual report |
| `analyze-sentiment` | `/sentiment [TICKER]` | Macro + ticker sentiment |
| `analyze-fundamentals` | `/fundamentals <TICKER>` | GCCP Parts II + III |
| `analyze-valuation` | `/valuation <TICKER>` | Target price, Parts IV + V |
| `draft-report` | `/report [TICKER]` | Compile + export PDF |
| `publish-discord` | `/publish` | Discord summary-post + PDF |
| `skill-creator` | — | Create/edit/eval skills (dev tooling, no slash command) |

### Deep Dive flow
```
collect-data → analyze-sentiment → analyze-fundamentals → analyze-valuation
                                         ↑ (sentiment feeds fundamentals)
→ gatekeeper (8-check gate, max 5 revisions) → draft-report → publish-discord
```

### Agent roles

- `stock-analyst` (primary, `mode: primary`) — embodies the GCCP analyst persona, only agent invocable directly by slash commands
- `market-scout` (subagent, `user-invocable: false`) — news/context research via `stockiv-scout`, purges cache first
- `gatekeeper-reviewer` (subagent, `user-invocable: false`) — validates against the 8-check gate before any Discord publish

---

## Project Structure

```
stockiv-skill/
├── .opencode/
│   ├── agent/                      # stock-analyst.md, market-scout.md, gatekeeper-reviewer.md
│   ├── command/                    # slash command definitions
│   └── skills/                     # ten skills, see Architecture above
├── .claude/                        # Claude Code mirror (agents, commands, skills symlink)
├── CLAUDE.md                       # Claude Code entrypoint (imports AGENTS.md)
├── src/stockiv/
│   ├── cli.py                      # stockiv-collect / stockiv-scout / stockiv-report / stockiv-publish
│   ├── main.py                     # stockiv-run entrypoint
│   ├── config/                     # paths.py, discord.py
│   ├── knowledge/                  # GCCP framework docs (read by AI skills)
│   └── utils/                      # logger, freshness cache
├── tools/                          # Pure Python helpers (called by CLI)
│   ├── vnstock_tools.py            # Vietnamese stock data via vnstock API
│   ├── sqlite_tools.py             # SQLite financial database queries
│   ├── brave_tools.py              # Brave Search for news context
│   ├── report_finder_tools.py      # Annual report PDF download + conversion
│   ├── pdf_exporter_tool.py        # Markdown → PDF via WeasyPrint
│   ├── discord_publisher_tool.py   # Discord message + file publishing
│   └── cache_tools.py              # Cache cleanup
├── tests/
│   └── test_*.py                   # CLI + tool unit tests
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
