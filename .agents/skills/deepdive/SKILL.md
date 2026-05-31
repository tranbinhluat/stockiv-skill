---
name: deepdive
description: Run a full GCCP deep-dive stock analysis for a Vietnamese ticker. Use this skill whenever the user types /deepdive, /deepdive <TICKER>, "phân tích sâu", "deep dive", "analyze stock", or asks for a complete stock analysis report on any Vietnamese ticker symbol (e.g. FPT, MWG, VCB, HPG).
---

# /deepdive — Full GCCP Analysis Pipeline

> **Agents active during this workflow:**
> - `.agents/agents/stock-analyst.md` — GCCP analyst persona (Steps 1–4, 6)
> - `.agents/agents/gatekeeper.md` — quality validator (Step 5)

Runs the complete Good Company, Cheap Price (GCCP) analysis for a single Vietnamese stock ticker, from raw data collection through to a published Discord report.

## Extract the Ticker

Parse the ticker from the user's message. If not provided, ask: "Which ticker would you like to analyze? (e.g. FPT, MWG, VCB)"

Once you have `{TICKER}` (uppercase), proceed through steps 1–7 in order. **Do not skip steps. Do not run steps in parallel.**

---

## Step 1 — Collect Data

Use the `collect-data` skill.

```
uv run stockiv-collect --ticker {TICKER} --type all
```

If output files already exist and are fresh (< 7 days), the CLI will skip re-fetching automatically. If you suspect stale data, add `--force`.

**Wait for completion.** Confirm:
- `data/processed/synthesizer/{TICKER}/financial_summary.md` exists
- `data/raw/context/{TICKER}_ticker_context.md` exists

---

## Step 2 — Analyze Sentiment

Use the `analyze-sentiment` skill.

Read:
- `data/raw/context/market_context.md` (run `uv run stockiv-collect --macro` first if missing)
- `data/raw/context/{TICKER}_ticker_context.md`

Write the 5-section macro report + ticker sentiment report:
- `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

**Wait for completion.** Sentiment output is required by Step 3.

---

## Step 3 — Analyze Fundamentals

Use the `analyze-fundamentals` skill.

**This step requires both Step 1 and Step 2 to be complete.** It reads:
- `data/processed/synthesizer/{TICKER}/financial_summary.md`
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

Performs GCCP Parts II + III. Saves:
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

---

## Step 4 — Analyze Valuation

Use the `analyze-valuation` skill.

Reads:
- `data/processed/synthesizer/{TICKER}/financial_summary.md`
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

Performs GCCP Parts IV + V. Saves:
- `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`

---

## Step 5 — Gatekeeper Validation

Apply the `.agents/agents/gatekeeper.md` agent persona.

Submit all three analysis files for the 5-check validation:
1. `financial_data_verified`
2. `numbers_accurate`
3. `logic_and_reasoning_sound`
4. `no_hallucinated_prices`
5. `buy_sell_logic`

**If APPROVED**: proceed to Step 6.
**If REJECTED**: fix the reported issues (usually recalculate or re-read source files) and re-submit.
**If MORE_INFO_NEEDED**: run the suggested `stockiv-collect` command and retry from Step 1.

---

## Step 6 — Draft Report

Use the `draft-report` skill.

Compiles all analysis into a Vietnamese GCCP report, then exports PDF:

```
uv run stockiv-report --ticker {TICKER} --format pdf
```

Output files:
- `reports/ticker/{TICKER}_GCCP_report.md`
- `reports/ticker/{TICKER}_GCCP_report.pdf`

---

## Step 7 — Publish to Discord

Use the `publish-discord` skill.

```
uv run stockiv-publish --file reports/ticker/{TICKER}_GCCP_report.md --channel ticker --attach-pdf
```

Confirm: "✅ Published to Discord."

---

## Progress Updates

After each step, show a brief status line:
```
[1/7] ✅ Data collected for {TICKER}
[2/7] ✅ Sentiment analyzed — macro: {regime}, ticker: {sentiment}
[3/7] ✅ Fundamentals complete — {quality verdict}
[4/7] ✅ Valuation complete — {BUY NOW / WAIT / AVOID}
[5/7] ✅ Gatekeeper: APPROVED
[6/7] ✅ Report exported to PDF
[7/7] ✅ Published to Discord
```
