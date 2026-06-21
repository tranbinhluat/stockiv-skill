---
name: compare-flow
description: Run a side-by-side GCCP comparison of two Vietnamese stocks. Use this skill when the user types /compare TICKER1 TICKER2, asks "compare FPT vs MWG", "which is better", or wants a peer analysis of two tickers. Runs full deepdive pipeline on both tickers then compiles a comparison report.
---

# compare-flow — Side-by-Side GCCP Stock Comparison

Runs the full Good Company, Cheap Price (GCCP) analysis pipeline for two Vietnamese stock tickers and compiles a side-by-side comparison report published to Discord.

## What This Skill Does

1. Extracts two tickers from the user's command.
2. Checks data freshness for each ticker and collects fresh data in parallel if needed.
3. Runs the full per-ticker analysis pipeline (sentiment → quant fundamentals → qual fundamentals → valuation).
4. Invokes the Gatekeeper Reviewer **once** on both analysis outputs combined.
5. Compiles a comparison report with a head-to-head metrics table and a final verdict.
6. Publishes the combined report to Discord.

## Depends On

- `collect-data` — must have run for both tickers (`financial_summary.md` required)
- `analyze-sentiment` — must have run for each ticker
- `analyze-fundamentals` — must have run for each ticker
- `analyze-valuation` — must have run for each ticker

## Input Files

**Per ticker (T1 and T2):**
- `data/processed/synthesizer/{TICKER}/financial_summary.md` — quantitative baseline
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md` — qualitative context
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` — fundamentals output
- `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md` — valuation output

## Output File

`reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md`

## Freshness Check

For each ticker, check if `data/processed/synthesizer/{TICKER}/financial_summary.md` exists and is less than 7 days old. If stale or missing, run `collect-data` for that ticker before proceeding with analysis.

---

## Execution Steps

### Step 0 — Extract Tickers

Parse the two ticker symbols from the user's command.

- Accept formats: `/compare FPT MWG`, `/compare FPT vs MWG`, "compare FPT and MWG", "which is better FPT or MWG"
- Normalize to uppercase: `TICKER1 = {T1}`, `TICKER2 = {T2}`
- If only **one** ticker is found, ask the user: "Which ticker would you like to compare against {T1}? (e.g. `/compare {T1} MWG`)"
- If zero tickers found, ask: "Please provide two tickers to compare. (e.g. `/compare FPT MWG`)"

Do not proceed until both tickers are confirmed.

---

### Step 1 — Pre-flight Freshness Check + Data Collection

For each ticker independently, check:

```
data/processed/synthesizer/{TICKER}/financial_summary.md — exists and < 7 days old?
```

**If BOTH need fresh data:**

Run `collect-data` for T1 and T2 **in parallel** — invoke both as concurrent subagents simultaneously:

- Subagent A: `uv run stockiv-collect --ticker {T1} --type financials && uv run stockiv-collect --ticker {T1} --type annual-report`
- Subagent B: `uv run stockiv-collect --ticker {T2} --type financials && uv run stockiv-collect --ticker {T2} --type annual-report`

Wait for both subagents to complete before proceeding.

**If only ONE needs fresh data:**

Run `collect-data` inline for that ticker only. The other proceeds immediately.

**If NEITHER needs fresh data:**

Skip collection entirely — use cached data.

Confirm before proceeding:
- `data/processed/synthesizer/{T1}/financial_summary.md` ✅
- `data/processed/synthesizer/{T2}/financial_summary.md` ✅

Show progress: `[1/6] ✅ Data collected for {T1} and {T2}`

---

### Step 2 — Per-Ticker Analysis Pipeline

Run the full analysis pipeline for each ticker. Both pipelines may run in parallel if context allows, but sequential is acceptable as a fallback.

For **each ticker** (T1 and T2), execute the following sub-steps in order:

#### Step 2A — Analyze Sentiment (Ticker Mode)

Check if this week's macro sentiment cache exists:
```bash
ls data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md 2>/dev/null
```

- **If macro cache EXISTS:** Run `analyze-sentiment` in ticker-only mode (skip macro collection). Output: `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- **If macro cache DOES NOT EXIST:** Run `analyze-sentiment` in full mode (collects macro + ticker sentiment).

#### Step 2B — Analyze Fundamentals (Parallel with 2A when macro cached)

**If macro cache EXISTS:** Run Step 2A and this step (quant phase) in parallel:
- Run `analyze-fundamentals` in `[quant-only]` mode.
- Reads only: `financial_summary.md`
- Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`

Wait for BOTH 2A and 2B to complete, then proceed to 2C.

**If macro cache DOES NOT EXIST:** Run sequentially after Step 2A completes.

#### Step 2C — Analyze Fundamentals Qual Phase

Run `analyze-fundamentals` in `[qual-only]` mode (or Full mode if sequential path).
- Reads: `{TICKER}_fundamentals_quant.md` + `{TICKER}_sentiment.md`
- Output: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

#### Step 2D — Analyze Valuation

Run `analyze-valuation` inline (refer to the `analyze-valuation` skill).
- Reads: `financial_summary.md` + `{TICKER}_fundamentals.md`
- Output: `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`

---

After Step 2 completes for T1:

`[2/6] ✅ Analysis complete for {T1} — {quality verdict}, {valuation verdict}`

After Step 2 completes for T2:

`[3/6] ✅ Analysis complete for {T2} — {quality verdict}, {valuation verdict}`

---

### Step 3 — Gatekeeper Review (Once for Both)

Invoke the `Gatekeeper Reviewer` subagent (refer to `.github/agents/gatekeeper-reviewer.agent.md`) **once** with **both** tickers' analysis outputs combined.

Use this prompt:
> "Review this side-by-side GCCP comparison of {T1} vs {T2}. Validate that both tickers' numbers are accurate, logic is sound, and the comparison verdict is justified. Check: (1) ROE/ROA/margins for both tickers are internally consistent with financial_summary.md; (2) Lynch categories are appropriate; (3) valuation verdicts and target prices use the correct method for each Lynch category; (4) the head-to-head comparison verdict is clearly reasoned."

**If APPROVED:** proceed to Step 4.

**If REJECTED:** read the gatekeeper's feedback, fix only the failed checks (preserve passing sections verbatim), and resubmit. Maximum 5 revision attempts before escalating to the user.

Show: `[4/6] ✅ Gatekeeper: APPROVED`

---

### Step 4 — Compile Comparison Report

Compile the comparison report and save to:
`reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md`

Use this exact structure:

```markdown
# {T1} vs {T2} — GCCP Comparison
_Generated: {date}_

## Executive Summary
| | {T1} | {T2} |
|---|---|---|
| Lynch Category | ... | ... |
| Quality Verdict | GOOD_COMPANY / BORDERLINE / AVOID | ... |
| Valuation Verdict | BUY NOW / WAIT / AVOID | ... |
| Target Buy Price | {VND} | {VND} |
| Current Price | {VND} | {VND} |
| Upside to Target | {%} | {%} |

## Head-to-Head: Key Ratios
| Metric | {T1} | {T2} | Better |
|---|---|---|---|
| ROE (5Y avg) | | | |
| ROA (5Y avg) | | | |
| Net Margin | | | |
| FCF Margin | | | |
| D/E Ratio | | | |
| Revenue CAGR (5Y) | | | |
| P/E | | | |
| PEG (if Fast Grower) | | | |

## Qualitative Summary
### {T1}
{3-sentence summary: Lynch category, moat, main risk}

### {T2}
{3-sentence summary: Lynch category, moat, main risk}

## Verdict
**If forced to choose one:** {TICKER} — {1-sentence rationale}
**Caveat:** {context — e.g., "FPT is higher quality but more expensive; MWG offers more upside if turnaround thesis holds"}
```

Show: `[5/6] ✅ Comparison report compiled`

---

### Step 5 — Publish to Discord

Run Discord publishing inline (refer to the `publish-discord` skill).

Compose a short summary post with both tickers' verdicts, then run:

```
uv run stockiv-publish \
  --file reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md \
  --channel ticker
```

Show: `[6/6] ✅ Published to Discord`

---

## Progress Updates

After each major step, show a status line:
```
[1/6] ✅ Data collected for {T1} and {T2}
[2/6] ✅ Analysis complete for {T1} — {quality}, {valuation}
[3/6] ✅ Analysis complete for {T2} — {quality}, {valuation}
[4/6] ✅ Gatekeeper: APPROVED
[5/6] ✅ Comparison report compiled
[6/6] ✅ Published to Discord
```

---

## Output to User

After publishing, show:
```
✅ Comparison report: reports/compare/{T1}_vs_{T2}_{DATE}_comparison.md

{T1}: {Quality Verdict} | {Valuation Verdict} — Target: {VND} ({upside}% upside)
{T2}: {Quality Verdict} | {Valuation Verdict} — Target: {VND} ({upside}% upside)

Verdict: {TICKER} wins — {1-sentence rationale}
```

---

## Error Handling

- **Missing ticker:** Ask the user before proceeding (Step 0).
- **collect-data fails for one ticker:** Abort the comparison; report which ticker failed and suggest running `/collect {TICKER}` manually.
- **Gatekeeper rejects after 5 attempts:** Stop; surface all failed checks to the user for manual review. Do not publish.
- **Freshness check unavailable (file permission error):** Treat as stale and re-collect.
