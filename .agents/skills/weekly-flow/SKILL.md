---
name: weekly-flow
description: Run a weekly macro market sentiment report for Vietnam and publish to Discord. Use this skill whenever the user types /weekly, "weekly report", "báo cáo tuần", "macro weekly", "thị trường tuần này", or asks for a weekly market summary or sentiment update.
---

# /weekly — Weekly Macro Market Sentiment Report

> **Agent active during this workflow:** `.agents/agents/stock-analyst.md`

Runs the weekly Vietnam market sentiment pipeline: macro data collection → sentiment analysis → report → Discord publish.

## Steps

Execute in order. Do not skip steps.

> **Review gate (default ON):** After Step 3, present the report summary to the user and wait for approval before publishing to Discord. Skip the review gate only if the user explicitly said "no review", "skip review", "auto publish", or equivalent in their original message.

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

Use the `draft-report` skill — macro/weekly mode.

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

Use the `publish-discord` skill.

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
