---
name: collect-data
description: Fetch financial data and news context for a Vietnamese stock ticker or the macro market. Use this skill when the user types /collect <TICKER>, asks to fetch or refresh stock data for a specific ticker, or needs to collect macro market data before a weekly report. Do NOT use for full analysis flows — use the deepdive skill for that.
---

# collect-data

Fetches all financial data and news context needed for GCCP analysis.

## What This Skill Does

Runs CLI tools to populate the data files that all downstream analysis skills read from.

### For a Ticker (`/collect <TICKER>` or before any analysis)

**Step 1 — Financials** — calls `uv run stockiv-collect --ticker <TICKER> --type financials`:
- Income statement, balance sheet, cash flow (5 years)
- Financial ratios (ROE, ROA, margins, debt ratios)
- Ratio summary (GCCP metrics pre-computed)
- Company overview (industry, charter capital, outstanding shares)
- Dividend history
- Vietstock ratios (crawler)
- Current market snapshot: live price, P/E, P/B, VNINDEX P/E + P/B
- **Peer ratios** — identify 1-2 top domestic competitors in the same industry and pre-load their ratio summaries for downstream peer comparisons

**Step 2 — Context (news)** — Invoke the `market-scout` subagent via the `task` tool with this prompt:

> "Perform dynamic news context scouting for {TICKER}. Clean the cache, run broad searches (earnings, management, industry), scan results for key developments (CEO resignations, margins, related-party transactions, debt), and execute 1-2 targeted follow-up queries to deep-dive. Synthesize your findings and save the output directly to data/raw/context/{TICKER}_ticker_context.md."

The scout saves results to `data/raw/context/{TICKER}_ticker_context.md`.

**Step 3 — Annual Reports** — calls `uv run stockiv-collect --ticker <TICKER> --type annual-report`:
- Search for and download the most recent annual report PDF for `<TICKER>`
- Convert to markdown: `data/processed/annual_reports/{TICKER}/{TICKER}_annual_report_{YEAR}.md`
- If no PDF is found, log `ANNUAL_REPORT_NOT_AVAILABLE` and continue — downstream forensic checks will skip gracefully

**Output files**:
- `data/processed/synthesizer/{TICKER}/financial_summary.md` — ground truth for all analysis
- `data/raw/context/{TICKER}_ticker_context.md` — news for sentiment analysis
- `data/processed/annual_reports/{TICKER}/{TICKER}_annual_report_{YEAR}.md` — for forensic review

### For Macro Market (`/collect --macro` or before `/weekly`)

1. Run inline: `uv run stockiv-collect --macro` — populates the basic VNINDEX + macro indicator snapshot.
2. Invoke the `market-scout` subagent via the `task` tool with this prompt:

> "Perform dynamic macroeconomic and market context scouting. Clean the cache, run broad queries (Vietnam GDP growth, inflation, SBV interest rate policies, FDI, and credit growth), scan results for key developments, and run 1-2 targeted follow-up queries to drill down into key catalysts or risks. Synthesize your findings and save the output directly to data/raw/context/market_context.md."

**Output file**:
- `data/raw/context/market_context.md` — used by analyze-sentiment for macro analysis


## Freshness Check

Data is considered **fresh** if files are < 7 days old. The CLI skips re-fetching automatically.

To force a refresh: add `--force` flag.

```
uv run stockiv-collect --ticker FPT --force
uv run stockiv-collect --macro --force
```


## Output Summary

After running, report to the user:
```
✅ Data collected for {TICKER}:
- financial_summary.md: {size} — covers {date_range}
- {TICKER}_ticker_context.md: {size} — {n} news articles
- {TICKER}_annual_report_{YEAR}.md: {found / ANNUAL_REPORT_NOT_AVAILABLE}
Data is fresh. Proceed to analyze-sentiment.
```
