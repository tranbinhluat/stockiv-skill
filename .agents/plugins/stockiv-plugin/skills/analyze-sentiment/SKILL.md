---
name: analyze-sentiment
description: Analyze macro market sentiment and ticker-specific sentiment from news for Vietnamese stocks. Use this skill when the user types /sentiment [TICKER], asks about market mood, Vietnam macro outlook, or news analysis for a specific stock. Do NOT use for full analysis flows — the deepdive skill handles those automatically.
---

# analyze-sentiment

Produces structured sentiment reports from news and macro data for both GCCP qualitative context and weekly reports.

## Depends On

- `collect-data` must have run first (reads `market_context.md` and `{TICKER}_ticker_context.md`)

---

## Step 0 — Freshness Check

Before doing any work, check if this week's macro sentiment file already exists:

```
data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md
```

To get the current `{YEAR}` and `{WW}`:
```
uv run python -c "from datetime import datetime; now=datetime.now(); y=now.year; w=now.isocalendar()[1]; print(f'{y} W{w:02d}')"
```

**If the file exists → skip Steps 1 and 2, go directly to Step 3 (Recent Trends) or Step 4 (Ticker, if ticker mode).**

**If the file does not exist → proceed with Steps 1 and 2.**

---

## Step 1 — Macro Sentiment (always, when file missing)

Reads `data/raw/context/market_context.md` and produces a **5-section macro report**:

1. **I. Executive Summary** — 2-3 sentence regime snapshot (Reflation, Stagflation, etc.) with key driver
2. **Market Dashboard** — markdown table: VNINDEX level, P/E, P/B, YTD, foreign flow. ONLY include indicators explicitly in the source. Each `Value` cell must embed the inline citation (e.g. `1,280 [[1]](URL)`). Do NOT fabricate values.
3. **II. Key Macro Indicators** — BLUF format: **bold keyword**, status in 1-2 words, one sentence of capital allocation context. GDP, inflation, interest rate, credit growth, VND/USD.
4. **III. Structural Shifts** — early signs of phase changes based solely on this week's news flow (sector rotation, thematic tailwinds).
5. **IV. Upcoming Macro Catalysts** — table: `Timeframe` | `Event` | `Expected Impact (High/Med/Low)`.
6. **V. Additional Crucial Findings** *(optional)* — critical themes that don't fit above.

**Citation rules (hard):**
- Every factual claim: inline `[[1]](exact-URL)` immediately after the claim
- Never use `[^1]` footnote syntax
- Copy URLs character-for-character — `.vn ≠ .cn`, `.com ≠ .co`
- Include a `References` section at the bottom

**Output**: `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`

---

## Step 2 — Synthesize Recent Trends (always, after Step 1)

Scan `data/processed/sentiment/market/` for the most recent 3–4 weekly files matching `{YEAR}_W*_macro_sentiment.md`. Read their contents and synthesize a unified view of the market's trajectory.

This produces a **single cross-week synthesis** — not a list of individual week summaries.

### Report Format

**I. Regime Shift Analysis**
Are we entering a new structural phase (e.g., growth-led → value-led) or continuing the previous trend? Cite the specific weekly files that support the conclusion.

**II. Critical Ongoing Situations & News**
For each critical real-world situation (wars, supply chain, central bank shifts, AI disruption, etc.):
- *The Situation:* current status
- *What makes it worse:* specific escalation triggers to watch
- *What makes it better:* specific de-escalation factors

**III. Forward Market Scenarios (3–6 Months)**
- *Base Case (60%):* most likely outcome
- *Bull Case (20%):* what data would surprise to the upside
- *Bear Case (20%):* hidden systemic risk

**IV. The Consensus Fallacy (Contrarian View)**
Where is consensus crowded? What happens if the market's "base case" pricing is wrong?

**V. Strategic Allocation Playbook**
Sectors/themes to **Overweight** and **Underweight** for long-term investing based on the multi-week trend.

**Citation rules:** cite weekly source files inline, e.g. `[[1]](2026_W21_macro_sentiment.md)`. Include `References` at bottom.

**Output**: `data/processed/sentiment/market/{YEAR}_overall_macro_sentiment.md`

> **If this file already exists:** overwrite it — it is always updated with the latest weeks' data.

---

## Step 3 — Ticker Sentiment (when TICKER provided)

Reads:
- `data/raw/context/{TICKER}_ticker_context.md`
- `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md` (macro backdrop)
- `data/processed/sentiment/market/{YEAR}_overall_macro_sentiment.md` (multi-week regime context)

Evaluates:
- **Company News** — recent earnings surprises, revenue guidance, margin trends
- **Management Actions** — insider buying/selling, governance changes, related-party risks
- **Macro Resilience** — how the business model holds under the current macro regime (tailwinds/headwinds from overall sentiment)
- **Thesis Invalidation Triggers** — regulatory risk, demand collapse, competition, accounting red flags

**Output**: `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

---

## GCCP Role (Critical)

The ticker sentiment output is **consumed by analyze-fundamentals** as the qualitative layer for GCCP Part II:
- Lynch category cross-check against macro regime
- Management governance flags used as qualitative evidence
- Industry tailwinds/headwinds lifted into GCCP Part II qualitative section
- Thesis invalidation signals surface as qualitative red flags in fundamentals report

---

## Output to User

After completing, summarize:
```
✅ Sentiment analysis complete:
Macro: {regime} — {one-sentence driver}
Recent trends: {one-sentence synthesis from overall_macro_sentiment}
{TICKER if provided}: {sentiment} — {key signal}

Key qualitative inputs for fundamentals:
- Lynch category alignment: {aligned/conflict} with macro
- Management flag: {flag or "none"}
- Tailwind: {tailwind}
- Headwind: {headwind}
- Thesis risk: {risk or "none identified"}
```
