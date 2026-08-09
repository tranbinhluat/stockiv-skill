---
name: shortlist
description: Shortlist "good company, cheap price" from the top 100 Vietnamese stocks (VN100) using a Quality-Value Composite Rank (ROE/ROA + P/E) screener. Use this skill when the user types /shortlist, asks for a "good company cheap price screener", "quality value screener", or wants a VN100-wide ranked shortlist rather than a single-ticker deep dive. Do NOT use for single-ticker analysis — use deepdive/fundamentals/valuation for that.
---

# shortlist

Screens all VN100 constituents and ranks them by a two-composite Quality-Value
Rank (a variant of Greenblatt's Magic Formula, not the literal formula):

- **Composite A:** `roa_rank + pe_rank`, re-ranked
- **Composite B:** `roe_rank + pe_rank`, re-ranked
- **`final_rank`** = rank of `(rank_score_roa_pe + rank_score_roe_pe)`, ascending

Rank 1 = highest ROE/ROA. Rank 1 = cheapest (lowest) P/E. Missing/negative P/E
is kept in the universe but forced to the worst-possible P/E rank (last place)
rather than dropped.

## What This Skill Does

Runs `uv run stockiv-shortlist [--force]`, which:

1. Fetches the current VN100 ticker list (`Listing().symbols_by_group('VN100')`)
2. Batch-fetches each ticker's ratio summary (ROE, ROA, static P/E, market cap,
   shares outstanding), throttled at ~1s/ticker to respect rate limits — skips
   and continues on any individual ticker fetch failure
3. Fetches live prices for all 100 tickers in ONE bulk call
   (`Trading(source='VCI').price_board(...)`) and live-adjusts each ticker's
   P/E: `live_pe = static_pe * (live_price / (market_cap / shares))`
4. Computes both composites + re-ranks + `final_rank` via pandas
5. Persists every run to the `screener_rankings` SQLite table (historical
   tracking, keyed by `run_date, ticker`)
6. Exports **all 100 rows** to `data/reports/market/shortlist_{YYYY-MM-DD}.csv`,
   sorted by `final_rank`

## Usage

```
uv run stockiv-shortlist
uv run stockiv-shortlist --force   # bypass today's ratio_summary cache
```

Caching: ratio summaries reuse the existing per-ticker daily cache — reruns
the same day are near-instant (only re-runs the ranking math + CSV export).

## Output to User

After running, report:
1. The **top 5** tickers (ticker, `final_rank`, ROE, ROA, live P/E) as a
   markdown table — the CLI already prints this
2. The full CSV path: `data/reports/market/shortlist_{date}.csv`
3. Note any skipped tickers if `batch_fetch_ratio_summaries` reported failures

Do **not** generate a markdown report for this skill — CSV + top-5 chat
summary is the only output format (no PDF, no full report).
