# Investment Framework — Good Company Cheap Price (GCCP)

> **🧠 CORE BACKBONE — All agents must read this before any analysis**

---

## 🎯 Core Principle

> **"Đầu tư là tìm mua TÀI SẢN, không phải 'đánh' (trade) hàng"**
>
> Investment is buying ASSETS, not trading goods.

## 🎯 Goal

> **Tìm CÔNG TY TỐT + MUA VỚI GIÁ RẺ**
>
> Find GOOD COMPANY + Buy at CHEAP PRICE

---

## 🧠 Mindset

- Long-term ownership, not short-term trading
- Business analysis, not price prediction
- Margin of safety always
- Think like an owner, not a trader

---

# PART I: GOOD COMPANY

## Cấu trúc tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│                    GOOD COMPANY ANALYSIS                     │
│                  (Phân tích Công ty Tốt)                     │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌──────────▼──────────┐
    │   QUALITATIVE     │         │   QUANTITATIVE      │
    │   (Định tính)     │         │   (Định lượng)      │
    └─────────┬─────────┘         └──────────┬──────────┘
              │                               │
    ┌─────────┴─────────┐         ┌──────────┴──────────┐
    │                   │         │                     │
┌───▼───┐         ┌─────▼────┐  ┌─▼──────┐      ┌──────▼─────┐
│Industry│         │ Business │  │Profit- │      │ Financial  │
│(Ngành)│         │  Model   │  │ability │      │   Health   │
└───────┘         └────┬─────┘  └────────┘      └────────────┘
                       │
                 ┌─────▼─────────┐
                 │  MANAGEMENT   │
                 │  (Quản trị)   │
                 └───────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐
    │Ownership│    │  Insider  │   │Leadership│
    │Structure│    │ Activity  │   │ Quality │
    └─────────┘    └───────────┘   └─────────┘
         │
    ┌────▼────┐
    │Governance│
    │ Signals  │
    └──────────┘
```

---

## A. QUALITATIVE ANALYSIS (Định tính) — 50%

### 1. Industry (Ngành)

> **See also:** [industry_guides.md](industry_guides.md) for detailed Vietnam-specific industry analysis

**3 Questions to Answer:**
- What are the industry characteristics? Factors affecting it?
- What is the growth stage?
- What are the risks?

**How to Analyze (Step-by-Step):**
1. **Identify industry** from company_overview
2. **Growth stage classification:**
   - Slow Growth: Utilities, Telecom
   - Sustainable Growth: FMCG, Banking
   - Fast Growth: Tech, E-commerce
   - Cyclical: Steel, Airlines, Real Estate
3. **Check industry-specific metrics** from [industry_guides.md](industry_guides.md):
   - Banking: NIM > 3.5%, NPL < 2%, CAR > 14%
   - Real Estate: Inventory turnover < 2 years, Debt/Asset < 30%
   - Technology: Revenue growth > 25%, R&D ratio 10-15%
   - etc.

**Growth Stages:**

| Stage | Characteristics | Example Industries |
|-------|-----------------|-------------------|
| **Slow Growth** | Mature, stable, low growth | Utilities, Telecom |
| **Sustainable Growth** | Steady 5-10% growth | FMCG, Banking |
| **Fast Growth** | High growth >15% | Tech, E-commerce |
| **Cyclical** | Follows economic cycles | Steel, Airlines, Real Estate |

### 2. Business Model (Mô hình kinh doanh)

**Questions to Answer:**
- What are the business segments?
- Input: Raw materials, suppliers?
- Output: Products/services, markets?
- Is the model easy to understand?
- Single industry or diversified?

**Ideal:** Simple, understandable, focused business

---

### 3. Management Quality (Quản trị) — 4 Pillars

> **"Đầu tư vào công ty có quản trị tốt là đầu tư vào người quản lý tài ba và trung thực."** - Warren Buffett

#### Pillar 1: Ownership Structure (Cơ cấu sở hữu) — 25%

**Data Source:** `company.ownership()`, `company.shareholders()`

| Red Flags 🚩 | Threshold | Points |
|--------------|-----------|--------|
| Công ty mẹ nắm > 50% | > 50% | -30 |
| State ownership cao | > 30% | -10 |
| Free float thấp | < 20% | -20 |
| Top 3 cổ đông > 70% | > 70% | -20 |

| Green Flags ✅ | Threshold | Points |
|----------------|-----------|--------|
| Founder ownership | 10-30% | +15 |
| Insider ownership hợp lý | 5-20% | +10 |
| Institutional ownership | 20-40% | +10 |
| Free float tốt | > 40% | +5 |

#### Pillar 2: Insider Activity (Hoạt động nội bộ) — 25%

**Data Source:** `company.insider_trading()`, `company.news()`

| Red Flags 🚩 | Pattern | Points |
|--------------|---------|--------|
| HĐQT liên tục bán | > 3 sales in 6 months | -25 |
| CEO bán cổ phiếu | Any sale | -20 |
| Nhiều insider bán cùng lúc | > 3 sellers in 1 month | -30 |

| Green Flags ✅ | Pattern | Points |
|----------------|---------|--------|
| Insider mua vào | Any buy | +15 |
| CEO mua cổ phiếu | Any buy | +25 |
| Multiple insiders mua | > 2 buyers in 3 months | +20 |

#### Pillar 3: Leadership Quality (Chất lượng lãnh đạo) — 25%

**Data Source:** `company.officers()`, `company.overview()`

| Red Flags 🚩 | Pattern | Points |
|--------------|---------|--------|
| CEO turnover cao | > 2 CEOs in 5 years | -20 |
| Board size quá lớn | > 15 members | -10 |
| CEO kiêm Chairman | Same person | -15 |

| Green Flags ✅ | Pattern | Points |
|----------------|---------|--------|
| Founder-led | Founder is CEO | +20 |
| Stable leadership | CEO tenure > 5 years | +15 |
| Separate CEO/Chairman | Different people | +10 |

#### Pillar 4: Governance Signals (Tín hiệu quản trị) — 25%

**Data Source:** `company.news()`, `company.events()`

| Red Flags 🚩 | Keywords | Points |
|--------------|----------|--------|
| Fraud allegations | gian lận, fraud | -50 |
| SEC investigation | điều tra, investigation | -40 |
| Accounting issues | kế toán, restatement | -35 |
| Executive departure | từ chức, resign | -15 |

| Green Flags ✅ | Keywords | Points |
|----------------|---------|--------|
| Dividend increase | tăng cổ tức | +10 |
| Share buyback | mua lại cổ phiếu | +15 |
| New contracts | hợp đồng mới | +5 |

#### Management Quality Score (MQS)

```python
MQS = (ownership_score + insider_score + leadership_score + governance_score) / 4
# Normalized to 0-100
```

| Score | Rating | Description |
|-------|--------|-------------|
| 80-100 | ⭐⭐⭐⭐⭐ | Quản trị xuất sắc |
| 60-79 | ⭐⭐⭐⭐ | Quản trị tốt |
| 40-59 | ⭐⭐⭐ | Quản trị trung bình |
| 20-39 | ⭐⭐ | Quản trị kém |
| 0-19 | ⭐ | Quản trị rất kém, tránh |

---

## B. QUANTITATIVE ANALYSIS (Định lượng) — 50%

### A. Profitability (Khả năng sinh lời)

| Metric | Formula | Good Threshold |
|--------|---------|----------------|
| **ROA** | Net Income / Total Assets | > 6% (Greenblatt) |
| **ROE** | Net Income / Equity | > 15% (Greenblatt) |
| **Gross Margin** | (Revenue - COGS) / Revenue | Industry dependent |
| **Operating Margin** | Operating Profit / Revenue | > 15% ideal |
| **Net Margin** | Net Income / Revenue | > 15% (Greenblatt) |
| **FCF Margin** | Free Cash Flow / Revenue | > 5% (Greenblatt) |

### B. Financial Health (Sức khỏe tài chính)

| Metric | Formula | Safe Threshold |
|--------|---------|----------------|
| **Current Ratio** | Current Assets / ST Debt | ≥ 2x (Graham) |
| **Debt/Equity** | Total Debt / Equity | ≤ 2x (Graham) |
| **Debt/Assets** | Total Debt / Total Assets | ≤ 0.5 |
| **Interest Coverage** | EBIT / Interest Expense | > 3x |

### C. Growth (Tăng trưởng)

| Metric | Requirement |
|--------|-------------|
| Revenue Growth | Consistent over 5-10 years |
| EPS Growth | ≥ 33% over 10 years (Graham) |
| Profit History | Profitable 10 consecutive years (Graham) |

---

## Simplified Rating System

> **For LLM Agents:** Use threshold-based logic instead of subjective point allocation.

### Good Company Rating

| Rating | Criteria | Action |
|--------|----------|--------|
| ⭐⭐⭐⭐⭐ **Excellent** | MQS ≥ 80 AND (ROE > 15% OR ROA > 6%) AND (D/E ≤ 2 OR Current ≥ 2) | **Strong candidate** |
| ⭐⭐⭐⭐ **Good** | MQS ≥ 60 AND meets 2/3 quantitative metrics | **Good candidate** |
| ⭐⭐⭐ **Fair** | MQS 40-59 OR meets 1/3 quantitative metrics | **Investigate further** |
| ⭐⭐ **Poor** | MQS < 40 OR fails all quantitative | **Avoid** |
| ⭐ **Very Poor** | Any red flag (fraud, governance crisis) | **Reject immediately** |

### Quantitative Metrics Check

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| ROE | > 20% | 15-20% | 12-15% | < 12% |
| ROA | > 10% | 6-10% | 3-6% | < 3% |
| Net Margin | > 15% | 10-15% | 5-10% | < 5% |
| FCF Margin | > 8% | 5-8% | 2-5% | < 2% |
| Debt/Equity | < 0.5 | 0.5-1.0 | 1.0-2.0 | > 2.0 |
| Current Ratio | > 2.5 | 2.0-2.5 | 1.5-2.0 | < 1.5 |
| Interest Coverage | > 8x | 4-8x | 2-4x | < 2x |

### Rating Algorithm

```python
# Pseudo-code for LLM agents
def rate_good_company(mqs, roe, roa, de, current, net_margin, fcf_margin):
    # Check red flags first
    if has_red_flags():
        return "⭐ Very Poor - REJECT"

    # Count quantitative passes
    quant_passes = 0
    if roe > 15 or roa > 6: quant_passes += 1
    if de <= 2 or current >= 2: quant_passes += 1
    if net_margin > 15 or fcf_margin > 5: quant_passes += 1

    # Apply rating logic
    if mqs >= 80 and quant_passes >= 2:
        return "⭐⭐⭐⭐⭐ Excellent - Strong candidate"
    elif mqs >= 60 and quant_passes >= 2:
        return "⭐⭐⭐⭐ Good - Good candidate"
    elif mqs >= 40 or quant_passes >= 1:
        return "⭐⭐⭐ Fair - Investigate further"
    else:
        return "⭐⭐ Poor - Avoid"
```

---

# PART II: CHEAP PRICE

## Market Cycle Awareness

> **See also:** [market_context.md](market_context.md) for current VN-Index status

**Check market phase before valuation:**

| Market Phase | VN-Index P/E | Action | Required Margin of Safety |
|--------------|--------------|--------|---------------------------|
| **Crisis** | ~10x | **Best buying opportunity** | 15% (lower OK) |
| **Fair Value** | 12-15x | Normal buying | 20% |
| **Expensive** | 16-20x | Be selective | 30%+ (need wider margin) |
| **Bubble** | >20x | **Don't buy** | 50%+ (must be extremely cheap) |

**How to use:**
1. Check current VN-Index P/E from [market_context.md](market_context.md)
2. Identify market phase
3. Adjust required margin of safety accordingly
4. Example: If market P/E = 18x (Expensive), require 30% discount to fair value

---

## Valuation Metrics

| Metric | Formula | Graham Rule |
|--------|---------|-------------|
| **P/B** | Price / Book Value Per Share | < 1.5x |
| **P/E** | Price / Earnings Per Share | < 15x |
| **P/E × P/B** | Combined metric | ≤ 22.5 |

## Valuation Methods

### 1. Discounted Cash Flow (DCF)

**When to use:** All companies with stable cash flows

**Process:**
1. Forecast free cash flows (5-10 years)
2. Apply discount rate (WACC or target return)
3. Calculate terminal value
4. Sum PV of FCF + PV of terminal value

**Vietnam context:**
- Higher country risk premium (2-3%)
- Currency risk (VND/USD)
- Emerging market discount

### 2. Relative Valuation

**P/E Ratio:** Compare to industry peers, 5-year average, market average
**P/B Ratio:** Compare to industry peers, historical range
**EV/EBITDA:** Useful for capital-intensive industries

### 3. Sum-of-the-Parts (SOTP)

**When to use:** Conglomerates with unrelated businesses

---

## Margin of Safety

**Minimum requirement:** 20% discount to fair value

**Higher discount required when:**
- Emerging growth company (volatility risk)
- Regulatory uncertainty
- Weak governance
- Competitive threats
- Illiquid stock

---

# PART III: RANKING (Greenblatt Magic Formula)

## The Formula

Joel Greenblatt's "Magic Formula" ranks stocks by combining:

1. **ROA** (Return on Assets) — measures company efficiency
2. **P/E** (Price to Earnings) — measures valuation (lower = cheaper)

## Step-by-Step Calculation

### Step 1: Get Raw Data
For each stock: ROA, P/E

### Step 2: Rank Each Metric

**ROA Ranking (highest = 1):**
- Sort all stocks by ROA (highest to lowest)

**P/E Ranking (lowest = 1):**
- Sort all stocks by P/E (lowest to highest)

### Step 3: Combined Score
```
Combined Score = ROA_Rank + PE_Rank
```

### Step 4: Final Ranking
- Sort by Combined Score (lowest = best)

## Example

| Stock | ROA | P/E | ROA Rank | P/E Rank | Combined |
|-------|-----|-----|----------|----------|----------|
| MWG   | 18% | 22x | 1 | 5 | 6 |
| FPT   | 15% | 14x | 2 | 4 | 6 |
| VCB   | 14% | 12x | 3 | 2 | **5** |
| VNM   | 12% | 11x | 4 | 1 | **5** |
| HPG   | 10% | 13x | 5 | 3 | 8 |

**Result:** VCB and VNM have best combination

## Strategy

1. Buy top 20-30 stocks from ranking
2. Hold for 2-3 years minimum
3. Rebalance annually
4. Don't panic sell on dips

---

# PART IV: TIER COMPARISON RULES

## Tier Definitions

| Tier | Market Cap (B VND) | Examples |
|------|-------------------|----------|
| **Large Cap** | > 20,000 | VNM, FPT, VCB, VIC |
| **Mid Cap** | 5,000 - 20,000 | PNJ, MSN, HPG, SSI |
| **Small Cap** | < 5,000 | Smaller companies |

## ✅ DO Compare
- Same industry
- Same tier (market cap)
- Same business model

## ❌ DON'T Compare
- Large cap vs small cap
- Different industries
- Different business models

---

# PART V: CHECKLIST

## Good Company Checklist

```markdown
□ Industry: Đặc điểm, giai đoạn, rủi ro?
□ Business Model: Dễ hiểu, tập trung?
□ Management: Score __/100
  □ Ownership Structure
  □ Insider Activity
  □ Leadership Quality
  □ Governance Signals
□ Profitability: ROE > 15%, ROA > 6%?
□ Financial Health: D/E ≤ 2, Current ≥ 2?
□ Growth: Consistent 5-10 years?
```

## Cheap Price Checklist

```markdown
□ P/E < 15x?
□ P/B < 1.5x?
□ P/E × P/B ≤ 22.5?
□ Margin of safety ≥ 20%?
□ Valuation triangulated (DCF + Relative)?
```

---

# PART VI: RELATED RESOURCES

> **Complete GCCP knowledge system - Refer to these files for detailed analysis**

## Core Framework Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **[industry_guides.md](industry_guides.md)** | Vietnam-specific industry analysis (8 industries) | Industry classification step |
| **[criteria.md](criteria.md)** | Graham/Greenblatt/Lynch selection criteria | Final screening & ranking |
| **[market_context.md](market_context.md)** | VN-Index market states & daily data | Before valuation (check market phase) |
| **[evidence_standard.md](evidence_standard.md)** | Evidence tiers & audit trail requirements | Data validation & sourcing |

## Quick Reference

**Industry Analysis:** See [industry_guides.md](industry_guides.md)
- Banking: NIM, NPL, CAR, CASA metrics
- Real Estate: Inventory turnover, legal risk
- Technology: Revenue growth, R&D ratio
- Construction: Order book, payment terms
- Logistics: Fleet utilization, fuel cost
- Insurance: Combined ratio, solvency
- Telecom: ARPU, churn rate
- Manufacturing: Capacity utilization, export ratio
- Consumer Goods: Distribution coverage, brand share

**Selection Criteria:** See [criteria.md](criteria.md)
- Graham: 9 defensive criteria (pass 8-9 = Strong)
- Greenblatt: Magic Formula (ROA rank + P/E rank)
- Lynch: 6 categories (Stable, Moderate, Fast Growth, Cyclical, Turnaround, Asset Play)

**Market Data:** See [market_context.md](market_context.md)
- Current VN-Index P/E level
- Market phase (Crisis/Fair/Expensive/Bubble)
- Foreign flow direction
- Sector performance

**Evidence Requirements:** See [evidence_standard.md](evidence_standard.md)
- Tier 1: HOSE/HNX filings, Annual Reports, vnstock API
- Tier 2: Broker reports, news (verification only)
- Tier 3: Social media, blogs (REJECTED)

---

## ⚠️ Important Rules for Agents

1. **ALWAYS read this file first** before any analysis
2. **ALWAYS compare within same tier**
3. **ALWAYS check industry context**
4. **ALWAYS apply margin of safety**
5. **NEVER recommend without understanding the business**
6. **NEVER ignore qualitative factors**

---

*Last Updated: 2026-03-03*
*This document is the single source of truth for investment logic.*
*This document is the single source of truth for investment logic.*
