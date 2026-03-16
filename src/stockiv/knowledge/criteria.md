# Selection Criteria (Graham / Greenblatt / Lynch)

> **🧠 CORE RESOURCE — For Director and Quant Analyst Crews**
> *Use these criteria to evaluate the class, safety, and ranking of an investment.*

## 1. Investor Type Classification

Before evaluating a stock, identify the user's/portfolio's profile.

| Attribute | Defensive Investor (Phòng thủ) | Enterprising Investor (Mạnh bạo) |
|-----------|--------------------------------|----------------------------------|
| **Time/Style** | Less time, passive holding | Active research, full-time monitoring |
| **Target Return** | Matches the market | Beats the market |
| **Portfolio** | Diversified (10-30 stocks) | Concentrated/Opportunistic |
| **Target Assets** | Top 100 size, stable dividends, high safety | M&A targets, Parent/Subsidiary disconnects, High Growth, P/B < 1 |

---

## 2. Benjamin Graham's Defensive Criteria

**Agent Logic:** A stock must pass at least **8 out of 9** of these criteria to be classified as a "Safe/Defensive" investment.

1. **Size:** Must be among the Top 100 market cap (VND) or large enterprise status.
2. **Current Ratio:** Current Assets >= 2x Current Liabilities.
3. **Debt to Equity:** Total Debt <= 2x Equity (or Long-term Debt < Working Capital).
4. **Earnings Stability:** 10 consecutive years of positive earnings.
5. **Dividend Record:** 10 consecutive years of uninterrupted dividend payments.
6. **Earnings Growth:** Minimum 33% increase in EPS over the past 10 years (compare avg of past 3 years to avg of first 3 years).
7. **P/E Ratio:** Moderate P/E < 15x (using 3-year trailing average EPS).
8. **P/B Ratio:** Moderate P/B <= 1.5x.
9. **Combined Limit:** P/E × P/B <= 22.5.

---

## 3. Joel Greenblatt's Magic Formula

Used to rank multiple companies to find "Good Companies at Cheap Prices."

**Prerequisite (Good Company Filter):** Before ranking, a company MUST pass these thresholds to ensure it is not a value trap:
1. `ROE` > 15% and `ROA` > 6%
2. `FCF Margin` > 5%
3. `Net Margin` > 15%

**Logic Flow (For Quant Analyst/Synthesizer):**
1. **Calculate Return:** Rank the filtered companies by `ROA` (Return on Assets) or `ROC` (Return on Capital). Highest = Rank 1.
2. **Calculate Yield:** Rank by `Earnings Yield` (EBIT/Enterprise Value) or simply `P/E`. Lowest P/E = Rank 1.
3. **Combined Score:** `ROA Rank` + `Yield Rank`.
4. **Action:** Focus on the lowest resulting combined score (Best combination of cheap + high quality).
5. **Holding Rule:** Hold for at least 1 year (or until the annual rebalance).

---

## 4. Peter Lynch's 6 Categories

**Agent Logic:** Classify the company into one of the following 6 buckets before making a valuation judgment.

| Category | Description | Key Investment Rule | Exit Strategy |
|----------|-------------|---------------------|---------------|
| **1. Slow Growers** | Mature companies, high dividends. | Must have high dividend yield. | Dividend is cut or fundamentals deteriorate. |
| **2. Stalwarts** | Large companies, steady 10-12% growth. | Buy on dips (P/E near historical low). | Price gets ahead of earnings (+50% jump). |
| **3. Fast Growers** | Small, aggressive, >20% growth. | **P/E < Growth Rate** OR **P/E < (Growth Rate + Div Yield) × 1.5**. Debt/Capital must be 25%-75%. | Growth decelerates or P/E gets extreme. |
| **4. Cyclicals** | Sales/Profits tied to economic cycle. | Buy when earnings look terrible (P/E is high artificially). | Sell when earnings peak (P/E looks low). |
| **5. Turnarounds** | Beaten down, potential bankruptcy. | Must have cash to survive the crisis. | Company recovers and normalizes. |
| **6. Asset Plays** | Value of assets (real estate/cash) > Market Cap. | P/B << 1, or hidden assets unrecorded. | Wait for catalyst or buyout. |

---

## 5. Sector Valuation Benchmarks

Use these as baseline sanity checks for the `Cheap Price` evaluation.

| Sector | Normal P/E Range | Normal P/B Range | Normal EV/EBITDA |
|--------|------------------|------------------|------------------|
| **Banking** | 8x - 12x | 1.0x - 2.0x | N/A |
| **Real Estate** | 10x - 15x | 1.0x - 2.5x | 8x - 14x |
| **Retail/FMCG** | 15x - 22x | 3.0x - 6.0x | 10x - 18x |
| **Technology** | 15x - 25x | 3.0x - 5.0x | 12x - 20x |
| **Steel/Resources** | 6x - 15x (Cyclical) | 1.0x - 2.0x | 5x - 8x |
| **Construction** | 6x - 16x | 0.9x - 2.2x | 5x - 15x |
| **Logistics** | 7x - 18x | 1.0x - 2.5x | 6x - 17x |
| **Insurance** | 8x - 22x | 1.1x - 2.8x | N/A |
| **Telecommunications** | 9x - 24x | 1.5x - 3.5x | 5x - 13x |

> *Note: If a stock is trading significantly above these averages, it requires a very strong fundamental justification (e.g. Fast Grower with PEG < 1).*

---

## 6. Benjamin Graham's Enterprising Criteria (Mạnh bạo)

**Agent Logic:** Use this criteria for Enterprising investors looking for Midcap or Turnaround opportunities. The safety rules are slightly relaxed compared to Defensive investing, but valuation rules are stricter.

1. **Current Ratio:** Current Assets >= 1.5x Current Liabilities.
2. **Debt to Net Current Assets:** Total Debt <= 1.1x Net Current Assets (Current Assets - Current Liabilities).
3. **Earnings Stability:** 5 consecutive years of positive earnings (relaxed from 10).
4. **Dividend Record:** Must have paid *some* cash dividends in recent years.
5. **Earnings Growth:** The most recent year's earnings must be higher than the earnings from 5 years ago.
6. **P/E Ratio:** Strict P/E < 9x (Trailing 12 months).
7. **P/B Ratio:** Strict P/B <= 1.2x.
8. **Growth Valuation Limit (if applicable):** P/E <= 8.5 + (2 * Growth Rate).
