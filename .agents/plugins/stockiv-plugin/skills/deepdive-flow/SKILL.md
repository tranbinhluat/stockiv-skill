---
name: deepdive-flow
description: Run a full GCCP deep-dive stock analysis for a Vietnamese ticker. Use this skill whenever the user types /deepdive, /deepdive <TICKER>, "phân tích sâu", "deep dive", "analyze stock", or asks for a complete stock analysis report on any Vietnamese ticker symbol (e.g. FPT, MWG, VCB, HPG).
---

# /deepdive — Full GCCP Analysis Pipeline

> **Agents active during this workflow:**
> - `Stock Analyst` — runs all analysis and reporting tasks (Steps 1–4, 6, 7)
> - `Gatekeeper Reviewer` — validates reports before draft compilation (Step 5)

Runs the complete Good Company, Cheap Price (GCCP) analysis for a single Vietnamese stock ticker, from raw data collection through to a published Discord report.

## Agent Roles

Use this skill through custom agents:
- **Stock Analyst**: Executes steps 1–4 sequentially inline, then calls the **Gatekeeper Reviewer** for Step 5 validation. Once approved, it proceeds to compile the report (Step 6) and publish to Discord (Step 7).
- **Gatekeeper Reviewer**: Triggered as a subagent by the Stock Analyst in Step 5 to review outputs against the 8-point quality checklist.

## Extract the Ticker

Parse the ticker from the user's message. If not provided, ask: "Which ticker would you like to analyze? (e.g. FPT, MWG, VCB)"

Once you have `{TICKER}` (uppercase), proceed through steps 1–7 in order. **Do not skip steps. Do not run steps in parallel.**

---

## Step 1 — Collect Data

Perform the collection in two parts:
1. **Quantitative & Annual Reports**: Run these commands inline to fetch financials (which automatically fetches peers) and reports:
   ```bash
   uv run stockiv-collect --ticker {TICKER} --type financials
   uv run stockiv-collect --ticker {TICKER} --type annual-report
   ```
2. **Dynamic News Context**: Invoke the `Market Scout` subagent using the `agent` tool to gather the news context. Provide this prompt:
   "Perform dynamic news context scouting for {TICKER}. Clean the cache, run broad searches (earnings, management, industry), scan results for key developments (CEO resignations, margins, related-party transactions, debt), and execute 1-2 targeted follow-up queries to deep-dive. Synthesize your findings and save the output directly to data/raw/context/{TICKER}_ticker_context.md."

Wait for the subagent to finish. Confirm these outputs exist before proceeding to Step 2:
- `data/processed/synthesizer/{TICKER}/financial_summary.md`
- `data/raw/context/{TICKER}_ticker_context.md`
- `data/processed/annual_reports/{TICKER}/` — check if annual report was saved or `ANNUAL_REPORT_NOT_AVAILABLE` is written.

---

## Step 2 — Parallel Analysis (Sentiment + Quant Fundamentals)

Check if this week's macro sentiment cache exists:
```bash
ls data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md 2>/dev/null
```

**If macro cache EXISTS (common case — weekly-flow ran this week):**

Run Step 2A and Step 2B in parallel — spawn both as concurrent subagents:

**Step 2A (parallel) — Ticker Sentiment:**
Run `analyze-sentiment` in ticker-only mode (skip macro collection since cache exists).
Output: `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

**Step 2B (parallel) — Quant Fundamentals (Part III only):**
Run `analyze-fundamentals` in `[quant-only]` mode.
Reads only: `financial_summary.md`
Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`

**Wait for BOTH 2A and 2B to complete.**

Then run Step 2C (sequential — requires both 2A and 2B):

**Step 2C — Qual Fundamentals (Part II only):**
Run `analyze-fundamentals` in `[qual-only]` mode.
Reads: `{TICKER}_fundamentals_quant.md` + `{TICKER}_sentiment.md`
Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

---

**If macro cache DOES NOT EXIST (first run of the week):**

Run sequentially:
1. `analyze-sentiment` (full — collects macro + ticker sentiment)
2. `analyze-fundamentals` (full mode — both Part III and Part II)

This path is slower but produces identical output to the parallel path.

---

After Step 2 completes (either path), confirm both outputs exist:
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

Then proceed to Step 3 (Analyze Valuation — previously Step 4).

---

## Step 3 — Analyze Fundamentals

Run the fundamentals analysis inline (refer to the `analyze-fundamentals` skill).

**This step requires both Step 1 and Step 2 to be complete.** It reads:
- `data/processed/synthesizer/{TICKER}/financial_summary.md`
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

Performs GCCP Parts II + III. Saves:
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

---

## Step 4 — Analyze Valuation

Run the valuation analysis inline (refer to the `analyze-valuation` skill).

Reads:
- `data/processed/synthesizer/{TICKER}/financial_summary.md`
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

Performs GCCP Parts IV + V. Saves:
- `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`

---

## Step 5 — Gatekeeper Validation

Invoke the `Gatekeeper Reviewer` subagent (the custom agent in `.github/agents/gatekeeper-reviewer.agent.md`).

Submit all analysis files for the 8-check validation. Track the attempt count — **maximum 5 revision attempts** before escalating to the user.

**Versioned files:** Each attempt writes versioned output:
- `{TICKER}_GCCP_report_v{N}.md` (draft)
- `{TICKER}_director_review_v{N}.md` (gatekeeper feedback)

**If APPROVED**: proceed to Step 6.

**If REJECTED**: read the gatekeeper's feedback carefully.
- Fix **only the failed checks** — do not rewrite sections that passed (preserve them verbatim)
- Increment version: `v1` → `v2` → etc.
- Re-run gatekeeper on the revised report
- After 5 failed attempts, stop and surface all failures to the user for manual review

**If MORE_INFO_NEEDED**: run the suggested `stockiv-collect` command and retry from Step 1.

---

## Step 6 — Draft Report

Run report drafting inline (refer to the `draft-report` skill).

Compiles all analysis into a Vietnamese GCCP report, then exports PDF:

```
uv run stockiv-report --ticker {TICKER} --format pdf
```

Output files:
- `reports/ticker/{TICKER}_GCCP_report.md`
- `reports/ticker/{TICKER}_GCCP_report.pdf`

---

## Step 7 — Publish to Discord

Run Discord publishing inline (refer to the `publish-discord` skill).

Compose a short summary post (see `publish-discord` skill for format), then run:

```
uv run stockiv-publish \
  --file reports/ticker/{TICKER}_GCCP_report.pdf \
  --message "{composed summary}" \
  --channel ticker
```

Confirm: "✅ Published to Discord — summary post sent + PDF attached."

---

## Progress Updates

After each step, show a brief status line:
```
[1/7] ✅ Data collected for {TICKER}
[2/7] ✅ Sentiment + Fundamentals complete (parallel) — macro: {regime}, quality: {verdict}
[3/7] ✅ Fundamentals complete — {quality verdict}
[4/7] ✅ Valuation complete — {BUY NOW / WAIT / AVOID}
[5/7] ✅ Gatekeeper: APPROVED
[6/7] ✅ Report exported to PDF
[7/7] ✅ Published to Discord
```
