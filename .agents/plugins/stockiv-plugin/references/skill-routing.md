# Skill Registry — stockiv-plugin

> **Machine-readable routing registry for all stockiv-plugin skills.**
> Agents and orchestrators consult this file to determine trigger patterns, input/output contracts, and dependency order.

## Registered Skills

### collect-data
- **Trigger:** `/collect <TICKER>`, `/collect --macro`
- **Type:** atomic
- **Inputs:** (none — generates data via CLI)
- **Outputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/raw/context/market_context.md`
- **Depends on:** (none — first in pipeline)

### analyze-sentiment
- **Trigger:** `/sentiment [TICKER]`, "market mood", "macro outlook"
- **Type:** atomic
- **Inputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/raw/context/market_context.md`
- **Outputs:** `data/processed/sentiment/ticker/{TICKER}_sentiment.md`, `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`
- **Depends on:** collect-data

### analyze-fundamentals
- **Trigger:** `/fundamentals <TICKER>`, "is this good company"
- **Type:** atomic
- **Inputs:** `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/processed/sentiment/ticker/{TICKER}_sentiment.md`
- **Outputs:** `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`
- **Depends on:** collect-data, analyze-sentiment

### analyze-valuation
- **Trigger:** `/valuation <TICKER>`, "is it cheap", "target price"
- **Type:** atomic
- **Inputs:** `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`
- **Outputs:** `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`
- **Depends on:** collect-data, analyze-fundamentals

### draft-report
- **Trigger:** `/report [TICKER]`
- **Type:** atomic
- **Inputs:** `{TICKER}_fundamentals.md`, `{TICKER}_valuation.md`, `{TICKER}_sentiment.md`
- **Outputs:** `reports/ticker/{TICKER}_GCCP_report.md`, `reports/ticker/{TICKER}_GCCP_report.pdf`
- **Depends on:** analyze-fundamentals, analyze-valuation, analyze-sentiment

### publish-discord
- **Trigger:** `/publish`, "send Discord"
- **Type:** atomic
- **Inputs:** approved report file path
- **Outputs:** Discord message (channel: weekly or ticker)
- **Depends on:** draft-report (gatekeeper APPROVED)

### deepdive-flow
- **Trigger:** `/deepdive`, `/deepdive <TICKER>`, "phân tích sâu", "deep dive", "analyze stock"
- **Type:** orchestrator
- **Pipeline:** collect-data → analyze-sentiment → analyze-fundamentals → analyze-valuation → gatekeeper → draft-report → publish-discord
- **Depends on:** all atomic skills

### weekly-flow
- **Trigger:** `/weekly`, "weekly report", "báo cáo tuần", "macro weekly", "thị trường tuần này"
- **Type:** orchestrator
- **Pipeline:** collect-data (macro) → analyze-sentiment → draft-report → publish-discord
- **Depends on:** collect-data, analyze-sentiment, draft-report, publish-discord

---

## Planned Skills (Sprint 2+)

### compare-flow [planned — Sprint 2]
- **Trigger:** `/compare TICKER1 TICKER2`
- **Type:** orchestrator
- **Pipeline:** deepdive TICKER1 ‖ deepdive TICKER2 → gatekeeper (once) → comparison report → publish-discord
- **Output:** `reports/compare/{T1}_vs_{T2}_comparison.md`
