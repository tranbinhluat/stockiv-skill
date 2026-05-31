---
name: analyze-fundamentals
description: Analyze the fundamental quality of a Vietnamese stock using GCCP Parts II and III. Use this skill when the user types /fundamentals <TICKER>, asks "is this a good company?", or when called internally after analyze-sentiment in a /deepdive flow.
---

# analyze-fundamentals

Answers the question: **"Is this a good company?"** using GCCP Parts II (qualitative) and III (quantitative).

## Depends On

- `collect-data` — must have run (`financial_summary.md` required)
- `analyze-sentiment` — must have run (`{TICKER}_sentiment.md` required)

## Input Files

- `data/processed/synthesizer/{TICKER}/financial_summary.md` — quantitative baseline
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md` — qualitative context

## GCCP Part II — Qualitative Analysis (sentiment-informed)

Read `src/stockiv/knowledge/framework.md` Part II and `src/stockiv/knowledge/industry_guides.md`.

### Industry Classification
Classify into: **Slow Growth / Sustainable / Fast Growth / Cyclical**
- Use industry_guides.md criteria + macro regime from sentiment

### Lynch Category
Assign one: **Stalwart / Fast Grower / Slow Grower / Cyclical / Asset Play / Turnaround**
- **Cross-check with macro regime** from `{TICKER}_sentiment.md` — if macro says cycle peak and Lynch says Fast Grower, flag the tension
- Lynch category determines valuation method in analyze-valuation (do not skip this step)

### Business Model
- Input → Engine → Output framework
- Identify the key value driver and moat (if any)

### Management & Governance
- Shareholder structure, controlling party, related-party transaction history
- **Use management flags from `{TICKER}_sentiment.md`** as qualitative evidence
- Red flags: tunneling, excessive related-party loans, auditor disclaimers

### Industry Tailwinds / Headwinds
- **Lift directly from `{TICKER}_sentiment.md`** macro resilience section
- Do not re-derive from scratch — use the cited analysis already done

### Thesis Invalidation Signals
- **From `{TICKER}_sentiment.md`**: regulatory risk, demand collapse, competition
- Surface these as qualitative red flags with a Pass/Flag verdict

## GCCP Part III — Quantitative Analysis

Read `src/stockiv/knowledge/framework.md` Part III and `src/stockiv/knowledge/financial_reading_guide.md`.

All math delegated to CLI — never computed in your head:
```
uv run python -c "
import statistics
roe_values = [0.18, 0.21, 0.19, 0.22, 0.20]  # from financial_summary.md
print(f'5Y avg ROE: {statistics.mean(roe_values):.1%}')
print(f'Min ROE: {min(roe_values):.1%}')
"
```

### Capital Structure
- Asset mix appropriate for industry type (asset-heavy vs. asset-light)
- Debt/Equity ratio vs. industry norm

### Profitability (5-year trend)
- **ROE > 15%** consistently — Pass/Fail with exact values
- **ROA > 6%** consistently — Pass/Fail with exact values
- Net margin trend — expanding/stable/compressing

### Cash Generation
- **OCF > Net Income** — Pass/Fail (earnings quality)
- **FCF margin > 5%** — Pass/Fail
- Working capital changes — flag bloat (rising receivables/inventory vs. revenue)

## Forensic Checks

Read annual report markdown files in `data/processed/annual_reports/{TICKER}/`.

- **Earnings quality**: Large OCF vs NI divergence? Recurring "non-cash" adjustments?
- **Working capital bloat**: Receivables or inventory growing faster than revenue?
- **Margin compression**: Gross margin shrinking over 3+ years?
- **Debt risk**: Short-term debt covering long-term obligations?
- **Auditor trust**: Qualified opinion? Related-party notes?
- **Off-balance-sheet**: Commitments, contingent liabilities, lease obligations?

## Output File

Save to: `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

Structure:
```markdown
# {TICKER} — Fundamentals Analysis (GCCP Parts II + III)
_Generated: {date}_

## Part II: Qualitative
### Industry: {classification}
### Lynch Category: {category} — {rationale}
### Business Model
### Management & Governance — {PASS/FLAG}
### Tailwinds / Headwinds (from sentiment)
### Thesis Invalidation Risks — {PASS/FLAG}

## Part III: Quantitative
### Capital Structure — {PASS/FLAG}
### Profitability — {PASS/FAIL}
  ROE 5Y avg: {value}% — {PASS if >15% else FAIL}
  ROA 5Y avg: {value}% — {PASS if >6% else FAIL}
### Cash Generation — {PASS/FAIL}
  OCF > NI: {TRUE/FALSE}
  FCF margin: {value}%

## Forensic Summary — {CLEAN/CAUTION/RED_FLAG}

## Overall Quality Verdict: {GOOD_COMPANY / BORDERLINE / AVOID}
Evidence: {2-3 sentence rationale}
```

## Output to User

After saving the file, show the Overall Quality Verdict and top 3 supporting evidence points.
