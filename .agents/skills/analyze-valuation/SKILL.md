---
name: analyze-valuation
description: Analyze whether a Vietnamese stock is cheap using GCCP Parts IV and V (valuation methodology, Graham checklist, target price). Use this skill when the user types /valuation <TICKER>, asks "is this cheap?", or when called internally after analyze-fundamentals in a /deepdive flow.
---

# analyze-valuation

Answers the question: **"Is this stock cheap?"** using GCCP Parts IV (market context + valuation methodology) and V (target price math).

## Depends On

- `analyze-fundamentals` must have run (`{TICKER}_fundamentals.md` required for Lynch category)
- `collect-data` must have run (`financial_summary.md` required for current price + VNINDEX ratios)

## Input Files

- `data/processed/synthesizer/{TICKER}/financial_summary.md` — current price, VNINDEX ratios, Graham checklist
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` — Lynch category (determines valuation method)

## GCCP Part IV — Market Phase + Valuation Method

Read `src/stockiv/knowledge/framework.md` Part IV and `src/stockiv/knowledge/criteria.md`.

### Step 1: Market Phase Classification

Copy VNINDEX P/E **verbatim** from `financial_summary.md` (FetchCurrentMarketSnapshotTool section):
```
uv run python -c "
vnindex_pe = {exact_value_from_file}  # copied verbatim, never approximated
if vnindex_pe < 10: phase = 'CRISIS — deep value opportunity'
elif vnindex_pe <= 17: phase = 'FAIR — normal valuation range'
else: phase = 'BUBBLE — elevated risk'
print(f'VNINDEX P/E: {vnindex_pe} → Market Phase: {phase}')
"
```

### Step 2: Graham 9-Point Checklist

Copy results **verbatim** from `financial_summary.md` (Graham section). **Never recalculate** — the checklist was pre-computed during collect-data.

Report: `X / 9 Graham criteria met`

### Step 3: Valuation Methodology (based on Lynch category from `{TICKER}_fundamentals.md`)

| Lynch Category | Method |
|---|---|
| Fast Grower | Lynch PEG = P/E ÷ Net Profit CAGR. Fair if PEG ≤ 1.0 |
| Stalwart | P/E vs historical average + Graham fair value |
| Slow Grower | Dividend yield + Graham asset value |
| Cyclical | P/B vs historical trough. P/E is unreliable for cyclicals — do not use |
| Asset Play | Book value + hidden asset discount |
| Turnaround | P/S or EV/EBITDA (no earnings yet) |

**For Lynch PEG — CRITICAL RULE**: Use **Net Profit CAGR**, never EPS CAGR.
- Vietnamese stock dividends inflate share count year over year, making EPS CAGR artificially depressed.
- Always calculate using total net profit figures from income statement.

```
uv run python -c "
# Net Profit CAGR (5Y)
net_profit_start = {value_from_financial_summary}  # year T-5
net_profit_end = {value_from_financial_summary}    # year T
cagr = (net_profit_end / net_profit_start) ** (1/5) - 1
pe = {current_pe_from_snapshot}
peg = pe / (cagr * 100)
print(f'Net Profit CAGR: {cagr:.1%}')
print(f'Current P/E: {pe}')
print(f'Lynch PEG: {peg:.2f} — {\"CHEAP (PEG <= 1)\" if peg <= 1 else \"EXPENSIVE (PEG > 1)\"}')
"
```

## GCCP Part V — Target Price Math

### Fair Value Calculation

All math via CLI:
```
uv run python -c "
# Transparent target price formula (adjust values from financial_summary.md)
lynch_category = '{category}'
fair_value_multiple = {multiple}   # e.g., PEG=1 → fair P/E = CAGR * 100
eps_or_bvps = {value}              # EPS for growth, BV/share for asset plays
margin_of_safety = 0.25            # 25% standard MOS

fair_value = fair_value_multiple * eps_or_bvps
target_buy_price = fair_value * (1 - margin_of_safety)
current_price = {exact_from_snapshot}

suggestion = 'BUY NOW' if current_price < target_buy_price else 'WAIT'
print(f'Fair Value: {fair_value:,.0f} VND')
print(f'Target Buy Price (25% MOS): {target_buy_price:,.0f} VND')
print(f'Current Price: {current_price:,.0f} VND')
print(f'Verdict: {suggestion}')
"
```

**Logic check (mandatory)**: After computing, verify:
```
uv run python -c "print('BUY NOW' if {current_price} < {target_buy_price} else 'WAIT')"
```
The result of this CLI call is the final verdict — never override it manually.

## Output File

Save to: `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`

Structure:
```markdown
# {TICKER} — Valuation Analysis (GCCP Parts IV + V)
_Generated: {date}_

## Part IV: Market Context
- VNINDEX P/E: {verbatim value} → Market Phase: {CRISIS/FAIR/BUBBLE}
- VNINDEX P/B: {verbatim value}
- Graham 9-Point: {X}/9 met

## Valuation Methodology: {method based on Lynch category}
- Lynch Category (from fundamentals): {category}
- Method applied: {PEG/P/E/P/B/Dividend Yield/etc.}

## Part V: Target Price Math
| Metric | Value |
|---|---|
| Fair Value Multiple | {multiple} |
| {EPS/BV/NP} | {value} VND |
| Fair Value | {fair_value} VND |
| Margin of Safety (25%) | {mos_amount} VND |
| **Target Buy Price** | **{target_buy_price} VND** |
| **Current Price** | **{current_price} VND** |
| **Verdict** | **{BUY NOW / WAIT / AVOID}** |

## Summary
{2-3 sentence rationale combining market phase, Graham score, and target price verdict}
```

## Output to User

Show the Target Price Math table and the final verdict (BUY NOW / WAIT / AVOID).
