# The StockIV Good Company Cheap Price (GCCP) Framework

> **🧠 MASTER DIRECTIVE — All Crews MUST strictly adhere to this framework.**
> *This is the core philosophical and operational backbone of StockIV.*
> *Last Updated: 2026-03-04*

## PART I: The Foundation (Investing vs. Trading)

**Operational Rule:** Any agent evaluating "Good Company" (Business Quality) or "Cheap Price" (Valuation) MUST ignore "Trading" signals. StockIV is an **Investing** framework.

| Trading (IGNORE) | Investing (APPLY) |
|------------------|-------------------|
| Focuses on Price History / Charts | Focuses on Business Fundamentals / Value |
| Short-term speculation | Long-term ownership |
| "Why did it drop today?" | "Is the business generating free cash flow?" |
| Buying to sell to someone else | Buying to hold as an owner |

---

## PART II: GOOD COMPANY (Qualitative Evaluation)

*Agents must determine if the company is fundamentally sound before looking at the price.*

### 1. Industry Dynamics (`[Data Source: Pending Specification]`, `industry_guides.md`)

Classify the company's industry into one of the four growth stages:

1. **Slow Growth (Tăng trưởng chậm):** Market is saturated. Focus is entirely on high Dividend Yield and absolute stability (e.g., legacy utilities).
2. **Sustainable Growth (Tăng trưởng bền vững):** Consistent compounding. Look for high Returns on Capital, strong moats, and reinvestment capacity (e.g., top-tier consumer goods, top banks).
3. **Fast Growth (Tăng trưởng nhanh):** High top-line expansion. Focus on Gross Margins, expanding market share, and revenue growth. Risk: Requires capital to grow.
4. **Cyclical (Tăng trưởng theo chu kỳ):** Tied to economic inputs (e.g., commodities, construction). Focus on surviving the downturns (low debt) and buying when P/E looks artificially high.

> **Agent Action:** Refer to `industry_guides.md` for specific metrics to check based on this classification.

### 2. The Business Model (Mô hình kinh doanh)

Evaluate simplicity and focus.

- **Output (Đầu ra):** Who do they sell to? What is the product? Where is the revenue from?
- **Input (Đầu vào):** What are the raw materials? Where are they sourced?
- **Core Engine (Công cụ sản xuất):** Factories, workforce, distribution network.
- **Complexity Check:** Is this a single-industry (Đơn ngành) or multi-industry (Đa ngành) conglomerate? Conglomerates require higher margins of safety due to opacity.

### 3. Management & Governance (Quản trị)

Evaluate the people running the engine.

- **Structure:** Who are the major shareholders? Who is on the Board of Directors vs. the Executive Board?
- **Reputation:** Are they known for diluting shareholders or prioritizing related parties? (Ref: `financial_reading_guide.md` for proxy checks).

---

## PART III: GOOD COMPANY (Quantitative Evaluation)

*The numbers must reflect the narrative.*

> **Agent Core Rule:** Use the **Double-Entry Principle**. Every transaction leaves a trace. To find the truth, trace the numbers across all three statements. (Ref: `financial_reading_guide.md`).

| Metric Category | Key Agent Checks | Target Signatures |
|-----------------|------------------|-------------------|
| **Capital Structure (Cơ cấu vốn)** | Where are the biggest assets? What % is ST vs LT debt? | Asset structure matches the Industry type (e.g., heavy cash for services, heavy PPE for manufacturing). |
| **Profitability (Khả năng sinh lời)** | Gross, Operating, Pre-Tax, and Net Margins over time. ROE and ROA. | Consistently high ROE (>15%) and ROA (>6%) over a 5-10 year period. |
| **Cash Generation (Dòng tiền)** | Operating Cash Flow > Net Income. Free Cash Flow Margin. | `OCF` must convert "paper profit" into real cash. `FCF margin > 5%`. |

> **Agent Protocol (Return vs Yield):** The framework strictly separates `Return` and `Yield`.
> - **Return (ROA/ROE):** Profit relative to *Book Value* (How good is the internal engine?).
> - **Yield (Earnings Yield/FCF Yield):** Profit relative to *Market Capitalization* (How good is the price I am paying?).

---

## PART IV: CHEAP PRICE (Valuation)

*A Good Company can be a bad investment if the price is too high.*

### 1. The Market Phase (`market_context.md`)

Before valuing the individual stock, the agent MUST determine the overall market phase.

- **Crisis Phase (P/E ~ 10x):** Heavy buying opportunity.
- **Fair/Expensive (P/E 12-20x):** Selective buying. Higher Margin of Safety required.
- **Bubble Phase (P/E > 20x):** Extreme caution.

### 2. Relative Valuation Metrics

Evaluate the price relative to the internal engine.

- **P/B (Price to Book):** Price paid relative to contributed capital. Use for banks and asset-heavy cyclicals.
- **P/E (Price to Earnings):** Price paid for profitability. **For Growth Companies:** P/E must be less than `(Growth Rate + Dividend Yield)`.
- **EV/EBITDA:** Enterprise value relative to operating cash flow. Neutralizes debt variations.

---

## PART V: HOLDING & EXIT STRATEGIES

*A framework must dictate not just when to buy, but how long to hold and when to sell.*

**Agent Protocol:** Based on the investor profile and company classification, recommend the following selling strategies:

1. **Defensive Portfolios (Phòng thủ):**
   - **Method:** Fixed Ratio / Dollar Cost Averaging (DCA).
   - **Sell Trigger:** Rebalance when portfolio weight deviates significantly from the fixed ratio, or when P/E becomes excessively expensive.
   - **Hold Time:** Long-term (Years/Decades).

2. **Greenblatt Magic Formula Portfolios:**
   - **Method:** High conviction ranking.
   - **Sell Trigger:** Always sell and re-run the formula after exactly **1 Year** (or rebalance winners/losers for tax loss harvesting).
   - **Hold Time:** Strictly 1 Year cycles.

3. **Cyclicals (Chu kỳ - NĐT Mạnh bạo):**
   - **Method:** Contrary investing.
   - **Sell Trigger:** Sell when the P/E looks *low* (Earnings have peaked) and the market is highly optimistic.
   - **Hold Time:** 2-3 years (the length of the cycle).

4. **Peter Lynch Categories (Fast Growers / Stalwarts):**
   - **Method:** Fundamental trailing.
   - **Sell Trigger:**
     - *Fast Growers:* Sell when growth decelerates or P/E wildly exceeds Growth Rate.
     - *Stalwarts:* Sell if price jumps >50% ahead of earnings.

---

## PART VI: THE INTELLIGENT INVESTOR EXECUTION

*How to synthesize the qualitative, quantitative, and valuation findings.*

1. **Classify the User/Portfolio (`criteria.md`):** Are they a Defensive (Phòng thủ) or Enterprising (Mạnh bạo) investor?
2. **Apply the Specific Filters (`criteria.md`):**
   - For Defensive: Apply the strict 9 Graham criteria (Must pass 8/9).
   - For Enterprising: Apply strict low valuation metrics (P/E < 9, P/B < 1.2), Greenblatt Magic Formula, or Lynch Categorical rules.
3. **Verify Evidence (`evidence_standard.md`):** Ensure all numbers are sourced from Tier 1 verified financial statements (`[Data Source: Pending Specification]`), not rumors.

---

## PART VII: KNOWLEDGE BASE INDEX (Cross-References)

When drafting a final report, the Director MUST utilize these specific files to validate its logic:

1. **`industry_guides.md`:** Quantitative metric thresholds optimized for 8 specific Vietnamese industries.
2. **`criteria.md`:** Explicit IF/THEN logic for Graham, Greenblatt, and Lynch strategies.
3. **`market_context.md`:** Current VN-Index state machine and exact Margin of Safety adjustments.
4. **`financial_reading_guide.md`:** Financial forensic rules to catch anomalies (Double-entry violations, fake revenue, inventory bloat).
5. **`evidence_standard.md`:** The "Zero Trust" data sourcing and audit trail policy for the Director execution.
