---
name: analyze-fundamentals
description: Analyze the fundamental quality of a Vietnamese stock using GCCP Parts II and III. Use this skill when the user types /fundamentals <TICKER>, asks "is this a good company?", asks about ROE/ROA/margins/moat for a specific stock, or wants a standalone qualitative + quantitative quality assessment. Do NOT use for full analysis flows — the deepdive skill handles those automatically.
---

# analyze-fundamentals

Answers the question: **"Is this a good company?"** using GCCP Parts II (qualitative) and III (quantitative).

## Depends On

**Quant phase (Part III only):**
- `collect-data` — must have run (`financial_summary.md` required)
- No sentiment dependency — can run immediately after collect-data

**Qual phase (Part II — default when running standalone):**
- `collect-data` — must have run
- `analyze-sentiment` — must have run (`{TICKER}_sentiment.md` required)

## Input Files

**Always required:**
- `data/processed/synthesizer/{TICKER}/financial_summary.md` — quantitative baseline

**Required for Full or Qual-only mode:**
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md` — qualitative context
  (Use most recent weekly file — check `data/processed/sentiment/ticker/{TICKER}/` for latest `_W{WW}_` file)

**Intermediate file (Quant-only output, Qual-only input):**
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`

## Execution Mode

This skill can be called in two modes:

### Mode A — Full (default for standalone `/fundamentals <TICKER>`)
Runs Part III first, then Part II. Requires both `financial_summary.md` and `{TICKER}_sentiment.md`.

### Mode B — Quant-only (called by `deepdive-flow` in parallel with sentiment)
Runs Part III ONLY. Requires only `financial_summary.md`. Does NOT output `{TICKER}_fundamentals.md` — outputs `{TICKER}_fundamentals_quant.md` as intermediate file.
Triggered when: deepdive-flow detects macro sentiment cache exists and calls with `[quant-only]` flag.

### Mode C — Qual-only (called by `deepdive-flow` after quant + sentiment both complete)
Runs Part II ONLY, reading `{TICKER}_fundamentals_quant.md` + `{TICKER}_sentiment.md`.
Merges outputs into final `{TICKER}_fundamentals.md`.
Triggered when: deepdive-flow has both `{TICKER}_fundamentals_quant.md` and `{TICKER}_sentiment.md`.

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

Delegate annual report review to the `annual-report-scanner` subagent. If no report exists, the subagent marks all narrative checks as `ANNUAL_REPORT_NOT_AVAILABLE` and the analysis continues.

### A. Quantitative Anomaly Pre-Scan

Run these checks against `financial_summary.md` first — flag anything that requires deeper investigation:

- **Earnings Quality**: Is OCF significantly below Net Income? Recurring "non-cash" adjustments that inflate profit?
- **Working Capital Bloat**: Are receivables or inventory growing faster than revenue? (If receivables CAGR > revenue CAGR, flag.)
- **Margin Compression**: Is gross margin declining consistently over 3+ years?
- **Debt Risk**: Short-term debt covering long-term obligations? Interest coverage below 3x?

For any suspected anomaly, verify with CLI:
```
uv run python -c "
receivables = [...]  # from financial_summary.md
revenue = [...]
for i in range(1, len(revenue)):
    ratio = (receivables[i]/receivables[i-1]) / (revenue[i]/revenue[i-1])
    print(f'Year {i}: receivables/revenue growth ratio = {ratio:.2f}')
"
```

### B. Annual Report Narrative Checks (5 qualitative forensic checks)

Invoke `annual-report-scanner` via the `task` tool with:

> "Scan annual report for `{TICKER}`. Read the most recent markdown in `data/processed/annual_reports/{TICKER}/`. Return the exact five-row output contract from your agent instructions."

Use the returned five-row table in the Forensic Summary. Preserve statuses and key quotes verbatim. Do not re-read the annual report or duplicate these searches in the parent agent.

> **Boundary rule**: These are qualitative/legal forensic checks. Do not calculate ratios here — that belongs to the Quantitative Anomaly Pre-Scan above.

## Output File

**Full mode / Qual-only mode (final output):**
`data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`

**Quant-only mode (intermediate output):**
`data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals_quant.md`

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

### Quantitative Anomalies: {none / list}
### Annual Report Narrative Checks:
  1. Auditor Trust — {PASS/FLAG}: {key quote}
  2. Related Party — {PASS/FLAG}: {key quote}
  3. Off-Balance-Sheet — {PASS/FLAG}: {key quote}
  4. Management Remuneration — {PASS/FLAG}: {key quote}
  5. Revenue Recognition — {PASS/FLAG}: {key quote}

## Overall Quality Verdict: {GOOD_COMPANY / BORDERLINE / AVOID}
Evidence: {2-3 sentence rationale}
```

## Output to User

After saving the file, show the Overall Quality Verdict and top 3 supporting evidence points.
