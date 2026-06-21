---
name: weekly-flow
description: Run a weekly macro market sentiment report for Vietnam and publish to Discord. Use this skill whenever the user types /weekly, "weekly report", "báo cáo tuần", "macro weekly", "thị trường tuần này", or asks for a weekly market summary or sentiment update.
---

# /weekly — Weekly Macro Market Sentiment Report

> **Agent active during this workflow:** `Stock Analyst` (../.github/agents/stock-analyst.agents.md)

Runs the weekly Vietnam market sentiment pipeline: macro data collection → sentiment analysis → report → Discord publish.

## Agent Roles

Use this skill through custom agents:
- **Stock Analyst**: Executes all steps sequentially inline (macro data collection, sentiment analysis, report drafting, human review, and Discord publishing).

## Steps

Execute in order. Do not skip steps.

> **Review gate (default ON):** After Step 3, present the report summary to the user and wait for approval before publishing to Discord. Skip the review gate only if the user explicitly said "no review", "skip review", "auto publish", or equivalent in their original message.

---

## Step 1 — Collect Macro Data

Perform the collection in two parts:
1. **Macro Data Snapshot**: Run this command inline to fetch the basic VNINDEX and macroeconomic indicator snapshot:
   ```bash
   uv run stockiv-collect --macro
   ```
2. **Dynamic Macro News scouting**: Invoke the `Market Scout` subagent (../.github/agents/market-scout.agents.md) using the `agent` tool to gather the macro news context. Provide this prompt:
   "Perform dynamic macroeconomic and market context scouting. Clean the cache, run broad queries (Vietnam GDP growth, inflation, SBV interest rate policies, FDI, and credit growth), scan results for key developments, and run 1-2 targeted follow-up queries to drill down into key catalysts or risks. Synthesize your findings and save the output directly to data/raw/context/market_context.md."

Wait for the subagent to finish. Confirm that `data/raw/context/market_context.md` has been updated before proceeding to Step 2.

---

## Step 2 — Analyze Sentiment (Macro Only)

Run sentiment analysis inline in macro mode (refer to the `analyze-sentiment` skill).

The skill will first check if `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md` already exists this week. **If it does, skip to Step 3** — no need to re-run sentiment analysis.

If it does not exist, the skill reads `data/raw/context/market_context.md` and produces:

1. **5-section macro report** (`{YEAR}_W{WW}_macro_sentiment.md`):
   - Executive Summary — regime snapshot with key driver
   - Market Dashboard — VNINDEX level, P/E, P/B, YTD, foreign flow
   - Key Macro Indicators — GDP, inflation, interest rate, credit growth, VND/USD
   - Structural Shifts — sector rotation, thematic tailwinds
   - Upcoming Catalysts — Fed decisions, earnings season, regulatory events

2. **Recent trends synthesis** (`{YEAR}_overall_macro_sentiment.md`):
   - Reads the last 3–4 weekly macro files from `data/processed/sentiment/market/`
   - Regime shift analysis, ongoing situations, 3-scenario forward outlook (base/bull/bear), contrarian view, allocation playbook

Outputs:
- `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`
- `data/processed/sentiment/market/{YEAR}_overall_macro_sentiment.md`

---

## Step 3 — Draft Weekly Report

Run report drafting inline in macro/weekly mode (refer to the `draft-report` skill).

Compile the macro sentiment into a formatted weekly report:
- Header: `Báo cáo Thị trường Tuần {WW}/{YEAR}`
- 5 sections from the sentiment analysis
- Regime verdict: Bullish / Neutral / Bearish + rationale
- Top 3 catalysts to watch next week

Write to: `data/reports/market/{YEAR}_W{WW}_weekly_report.md`

Then export to PDF:
```
uv run stockiv-report --input data/reports/market/{YEAR}_W{WW}_weekly_report.md --format pdf
```

---

## Step 3.5 — Human Review Gate

**Skip this step only if the user explicitly said "no review", "skip review", "auto publish", or equivalent.**

Otherwise, show a preview of the report to the user:

```
📋 Weekly Report Preview — Tuần {WW}/{YEAR}

Regime: {Bullish / Neutral / Bearish}
Key driver: {one sentence}
Top catalysts next week:
1. {catalyst 1}
2. {catalyst 2}
3. {catalyst 3}

Full report: data/reports/market/{YEAR}_W{WW}_weekly_report.md

Publish to Discord? Reply "yes" / "publish" to confirm, or give feedback to revise.
```

**Wait for explicit approval before proceeding to Step 4.** If the user requests changes, revise the report (re-run Step 3) and show the preview again.

---

## Step 4 — Publish to Discord

Run Discord publishing inline (refer to the `publish-discord` skill).

Compose a short summary post (see `publish-discord` skill for format), then run:

```
uv run stockiv-publish \
  --file data/reports/market/{YEAR}_W{WW}_weekly_report.pdf \
  --message "{composed summary}" \
  --channel weekly
```

---

## Progress Updates

```
[1/4] ✅ Macro data collected
[2/4] ✅ Macro sentiment analyzed — regime: {regime}
[3/4] ✅ Weekly report drafted + exported to PDF
[3.5] ⏸ Awaiting review... (or ✅ Review skipped — auto publish)
[4/4] ✅ Published to Discord (weekly channel)
```
