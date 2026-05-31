---
name: analyze-sentiment
description: Analyze macro market sentiment and ticker-specific sentiment from news for Vietnamese stocks. Use this skill when the user types /sentiment [TICKER], asks about market mood, Vietnam macro outlook, or news analysis for a specific stock. Do NOT use for full analysis flows — the deepdive skill handles those automatically.
---

# analyze-sentiment

Produces structured sentiment reports from news and macro data for both GCCP qualitative context and weekly reports.

## Depends On

- `collect-data` must have run first (reads `market_context.md` and `{TICKER}_ticker_context.md`)

## What This Skill Does

### 1. Macro Sentiment (always)

Reads `data/raw/context/market_context.md` and produces a **5-section macro report**:

1. **Executive Summary** — one-paragraph regime snapshot (bullish/neutral/bearish) with key driver
2. **Market Dashboard** — VNINDEX level, P/E, P/B, YTD performance, foreign flow
3. **Key Indicators** — GDP growth, inflation, interest rate trend, credit growth, VND/USD
4. **Structural Shifts** — sector rotation, thematic tailwinds (e.g., infrastructure spend, digital economy)
5. **Upcoming Catalysts** — earnings season, Fed decisions, regulatory changes, elections

**Output**: `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`

### 2. Ticker Sentiment (when TICKER provided)

Reads `data/raw/context/{TICKER}_ticker_context.md` + the macro sentiment above.

Evaluates:
- **Company News** — recent earnings surprises, revenue guidance, margin trends
- **Management Actions** — insider buying/selling, governance changes, related-party risks
- **Macro Resilience** — how the business model holds up under the current macro regime (tailwinds/headwinds)
- **Thesis Invalidation Triggers** — regulatory risk, demand collapse, competition, accounting red flags

**Output**: `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`

## GCCP Role (Critical)

The ticker sentiment output is **consumed by analyze-fundamentals** as the qualitative layer for GCCP Part II:
- Lynch category cross-check against macro regime
- Management governance flags used as qualitative evidence
- Industry tailwinds/headwinds lifted into GCCP Part II qualitative section
- Thesis invalidation signals surface as qualitative red flags in fundamentals report

## Citation Rules (HARD — no exceptions)

Every factual claim in the report **must** have an inline citation:
```
Vietnam's GDP grew 6.1% in Q4 2024 [[1]](https://exact-url-from-source.vn/article)
```

- URLs are copied **character-for-character** from the source search results
- `.vn ≠ .cn` — do not reconstruct or guess URLs
- `.com ≠ .co` — never approximate
- If a URL is not available, state "Source: [publication name, date]" instead of fabricating a URL

## Output to User

After completing, summarize:
```
✅ Sentiment analysis complete:
Macro: {regime} — {one-sentence driver}
{TICKER}: {sentiment} — {key signal}

Key qualitative inputs for fundamentals:
- Lynch category alignment: {aligned/conflict} with macro
- Management flag: {flag or "none"}
- Tailwind: {tailwind}
- Headwind: {headwind}
- Thesis risk: {risk or "none identified"}
```
