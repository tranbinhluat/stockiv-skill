---
name: weekly
description: Run a weekly macro market sentiment report for Vietnam and publish to Discord. Use this skill whenever the user types /weekly, "weekly report", "báo cáo tuần", "macro weekly", "thị trường tuần này", or asks for a weekly market summary or sentiment update.
---

# /weekly — Weekly Macro Market Sentiment Report

> **Agent active during this workflow:** `.agents/agents/stock-analyst.md`

Runs the weekly Vietnam market sentiment pipeline: macro data collection → sentiment analysis → report → Discord publish.

## Steps

Execute in order. Do not skip steps.

---

## Step 1 — Collect Macro Data

```
uv run stockiv-collect --macro
```

Fetches:
- VNINDEX snapshot (P/E, P/B, market cap, YTD)
- Macro news: GDP, inflation, interest rate, foreign flows

Output: `data/raw/context/market_context.md`

If the file is fresh (< 7 days), the CLI skips automatically. Add `--force` for a manual refresh.

---

## Step 2 — Analyze Sentiment (Macro Only)

Use the `analyze-sentiment` skill — macro mode (no ticker).

Reads `data/raw/context/market_context.md` and produces a **5-section macro report**:
1. Executive Summary — one-paragraph regime snapshot with key driver
2. Market Dashboard — VNINDEX level, P/E, P/B, YTD, foreign flow
3. Key Indicators — GDP, inflation, interest rate, credit growth, VND/USD
4. Structural Shifts — sector rotation, thematic tailwinds
5. Upcoming Catalysts — Fed decisions, earnings season, regulatory events

Also synthesizes the previous 3–4 weekly reports for regime trend analysis.

Output: `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`

---

## Step 3 — Draft Weekly Report

Use the `draft-report` skill — macro/weekly mode.

Compile the macro sentiment into a formatted weekly report:
- Header: `Báo cáo Thị trường Tuần {WW}/{YEAR}`
- 5 sections from the sentiment analysis
- Regime verdict: Bullish / Neutral / Bearish + rationale
- Top 3 catalysts to watch next week

Write to: `reports/market/{YEAR}_W{WW}_weekly_report.md`

Then export to PDF:
```
uv run stockiv-report --input reports/market/{YEAR}_W{WW}_weekly_report.md --format pdf
```

---

## Step 4 — Publish to Discord

```
uv run stockiv-publish --file reports/market/{YEAR}_W{WW}_weekly_report.md --channel weekly
```

Routes to `DISCORD_CHANNEL_WEEKLY` env var.

---

## Progress Updates

```
[1/4] ✅ Macro data collected
[2/4] ✅ Macro sentiment analyzed — regime: {regime}
[3/4] ✅ Weekly report drafted + exported to PDF
[4/4] ✅ Published to Discord (weekly channel)
```
