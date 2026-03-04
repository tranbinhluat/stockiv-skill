# Financial Statement Reading Guide & Anomaly Detection

> **🧠 CORE RESOURCE — For Director and Quant Analyst Crews**
> *Use these forensic methods to evaluate the `methodology`, `accuracy`, and `anomalies` fields of your `DirectorDecision` output.*

## 1. The Double-Entry Principle (Nguyên tắc Đối ứng kép)

Every financial transaction possesses a "shape and a shadow." If Revenue (Income Statement) increases, there **must** be a corresponding increase in Cash or Accounts Receivable (Balance Sheet). If an agent claims something improved, it must explain *how* that improvement is funded.

---

## 2. Income Statement Anomalies (Báo cáo Kết quả Kinh doanh)

**Agent Goal:** Identify if "Revenue" or "Profit" is genuine cash or aggressive accounting.

| Anomaly Trigger | Condition to Check | Flag to Director |
|-----------------|--------------------|------------------|
| **Fake Revenue (Accounts Receivable Bloat)** | % Growth `Accounts Receivable` > % Growth `Revenue` | "Revenue growth driven by unpaid credit. Potential channel stuffing or fake sales." |
| **Margin Squeeze** | `COGS` growing faster than `Revenue` | "Pricing power is deteriorating or input costs are surging. Gross Margin is shrinking." |
| **Non-Core Profit Reliance** | `Financial Income` or `Other Income` > 30% of `Net Profit` | "Profit quality is low. The company is relying on selling assets or financial maneuvers rather than core business." |
| **Aggressive Capitalization** | `R&D` or `Interest Expense` is capitalized instead of expensed | "Earnings are artificially inflated by deferring costs to the balance sheet." |

---

## 3. Balance Sheet Anomalies (Bảng Cân đối Kế toán)

**Agent Goal:** Identify hidden risks, unsustainable leverage, and trapped capital.

| Anomaly Trigger | Condition to Check | Flag to Director |
|-----------------|--------------------|------------------|
| **Inventory Bloat (The Trap)** | Days Inventory Outstanding (DIO) increasing YoY by > 20% | "Capital is trapped in unsold goods. High risk of future inventory write-downs (lowering future profit)." |
| **The Liquidity Squeeze** | `Current Ratio` < 1.0 AND `Operating Cash Flow` is negative | "High bankruptcy risk. Cash cannot cover short-term debts." |
| **Hidden Debt (Phải trả khác)** | "Other Payables" (Right side) is unconventionally large (>20% of Liabilities) | "Potential hidden off-balance-sheet debt or undisclosed related-party borrowing." |
| **Related-Party Trap (Phải thu khác)** | "Other Receivables" (Left side) is large and directed at subsidiaries/associates | "Cash is being siphoned out of the core company to related parties." |

---

## 4. Cash Flow Divergence (Báo cáo Lưu chuyển Tiền tệ)

The most critical test of financial health is the reconciliation of Net Income to Operating Cash Flow (OCF).

**Agent Logic (Director / Synthesizer):**
1. Extract `Net Income` from Income Statement.
2. Extract `Net Cash from Operating Activities (OCF)` from the Cash Flow Statement.

> **The Divergence Test:** If `Net Income` is consistently highly positive, but `OCF` is consistently negative or substantially lower over a 3-year period, **REJECT** the company. Output:
> *Anomaly Detected: The company reports "paper profits" but fails to generate actual cash. Extremely high fraud or cash-burn risk.*

---

## 5. Footnotes & Qualitative Red Flags (Thuyết minh BCTC)

The Director should actively penalize companies (via the Governance Pillar) for the following:

- **Qualified Audit Opinion (Ý kiến kiểm toán ngoại trừ):** Auto-Reject unless perfectly explained.
- **Frequent Auditor Changes:** Changing auditors multiple times in 3 years is a massive red flag.
- **Constant Dilution (Phát hành thêm liên tục):** If the company constantly raises equity (issues shares) without proportional profit growth, they are destroying shareholder value. (Rule: Compare EPS growth to Net Income growth. If Net Income grows 20% but EPS grows 2%, it's massive dilution).
