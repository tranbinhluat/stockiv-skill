# Knowledge Map — stockiv-plugin

> Maps which files each skill requires before execution. Used for dependency verification and Sprint 2 parallelism planning.

| Skill | Requires File (before execution) | Written By |
|---|---|---|
| analyze-sentiment | `data/raw/context/{TICKER}_ticker_context.md` | collect-data |
| analyze-sentiment | `data/raw/context/market_context.md` | collect-data |
| analyze-fundamentals | `data/processed/synthesizer/{TICKER}/financial_summary.md` | collect-data |
| analyze-fundamentals | `data/processed/sentiment/ticker/{TICKER}_sentiment.md` | analyze-sentiment |
| analyze-valuation | `data/processed/synthesizer/{TICKER}/financial_summary.md` | collect-data |
| analyze-valuation | `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` | analyze-fundamentals |
| draft-report | `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` | analyze-fundamentals |
| draft-report | `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md` | analyze-valuation |
| draft-report | `data/processed/sentiment/ticker/{TICKER}_sentiment.md` | analyze-sentiment |
| publish-discord | `reports/ticker/{TICKER}_GCCP_report.md` OR `.pdf` | draft-report |

---

## Sprint 2 Parallelism Note

`analyze-fundamentals` declares a total dependency on `analyze-sentiment`. However:

- **Part III (quantitative):** Reads only `financial_summary.md` — does NOT need `{TICKER}_sentiment.md`
- **Part II (qualitative):** Reads `{TICKER}_sentiment.md` — Lynch category cross-check and macro regime context

**Proposed Sprint 2 split:**
- Run `analyze-fundamentals` Part III in parallel with `analyze-sentiment`
- Gate `analyze-fundamentals` Part II on `analyze-sentiment` completion
- This requires rewriting the dependency contract in `analyze-fundamentals/SKILL.md` — a Sprint 2 task

**Risk:** Do not implement this parallelism in Sprint 1. The current SKILL.md declares a full dependency — changing it without a regression baseline is risky.
