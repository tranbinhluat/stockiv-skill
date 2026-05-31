---
name: collect-data
description: Fetch financial data and news context for a Vietnamese stock ticker or the macro market. Use this skill when the user types /collect <TICKER>, asks to fetch or refresh stock data for a specific ticker, or needs to collect macro market data before a weekly report. Do NOT use for full analysis flows — use the deepdive skill for that.
---

# collect-data

Fetches all financial data and news context needed for GCCP analysis.

## What This Skill Does

Runs CLI tools to populate the data files that all downstream analysis skills read from.

### For a Ticker (`/collect <TICKER>` or before any analysis)

**Financials** — calls `uv run stockiv-collect --ticker <TICKER> --type financials`:
- Income statement, balance sheet, cash flow (5 years)
- Financial ratios (ROE, ROA, margins, debt ratios)
- Ratio summary (GCCP metrics pre-computed)
- Company overview (industry, charter capital, outstanding shares)
- Dividend history
- Vietstock ratios (crawler)
- Current market snapshot: live price, P/E, P/B, VNINDEX P/E + P/B

**Context (news)** — calls `uv run stockiv-collect --ticker <TICKER> --type context`:
- Brave Search: recent earnings news, management statements, industry developments

**Output files**:
- `data/processed/synthesizer/{TICKER}/financial_summary.md` — ground truth for all analysis
- `data/raw/context/{TICKER}_ticker_context.md` — news for sentiment analysis

### For Macro Market (`/collect --macro` or before `/weekly`)

Calls `uv run stockiv-collect --macro`:
- VNINDEX snapshot (P/E, P/B, market cap)
- Brave Search: Vietnam macro news, GDP, inflation, Fed impact, investor flows

**Output file**:
- `data/raw/context/market_context.md` — used by analyze-sentiment for macro analysis

## Freshness Check

Data is considered **fresh** if files are < 7 days old. The CLI skips re-fetching automatically.

To force a refresh: add `--force` flag.

```
uv run stockiv-collect --ticker FPT --force
uv run stockiv-collect --macro --force
```

## When to Run This Skill

- **Before every deepdive** — always check data freshness first
- **When gatekeeper returns MORE_INFO_NEEDED** due to missing data files
- **Before weekly report** — macro data must be fresh

## Output Summary

After running, report to the user:
```
✅ Data collected for {TICKER}:
- financial_summary.md: {size} — covers {date_range}
- {TICKER}_ticker_context.md: {size} — {n} news articles
Data is fresh. Proceed to analyze-sentiment.
```
