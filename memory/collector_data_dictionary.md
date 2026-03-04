# Collector Database Detailed Schema & Content (FPT)

Here is the explicit mapping of exact metrics, columns, and line items stored across the `data/stockiv.db` tables for downstream Quant Analysts.

---

## 1. `ratio_summary` (Mega-Metrics dumped to JSON)

The `fetch_ratio_summary` tool fetches 46 deeply integrated metrics for the Good Company Cheap Price (GCCP) framework. Because metrics like `pe` and `pb` change daily based on the stock price, this data is cached uniquely by `(ticker, date, year_report)`. The JSON blob `metrics_json` contains:

* `symbol`: Ticker symbol (e.g. FPT)
* `year_report`: Reporting year (e.g. 2025)
* `revenue`: Total revenue
* `revenue_growth`: YoY Revenue growth
* `net_profit`: Net Profit
* `net_profit_growth`: YoY Net Profit growth
* `ebit_margin`: EBIT Margin
* `roe`: Return on Equity
* `roic`: Return on Invested Capital
* `roa`: Return on Assets
* `pe`: Price to Earnings ratio (Trailing)
* `pb`: Price to Book ratio
* `eps`: Earnings Per Share
* `eps_ttm`: Earnings Per Share (Trailing 12 Months)
* `ev`: Enterprise Value
* `ev_per_ebitda`: EV / EBITDA
* `dividend`: Dividend Yield
* `current_ratio`: Current Ratio
* `quick_ratio`: Quick Ratio
* `cash_ratio`: Cash Ratio
* `interest_coverage`: Interest Coverage Ratio
* `gross_margin`: Gross Profit Margin
* `net_profit_margin`: Net Profit Margin
* `ps`: Price to Sales Ratio
* `bvps`: Book Value Per Share
* `outstanding_shares` / `issue_share`: Total shares outstanding

These 46 keys are readily parseable in Python via `json.loads(row['metrics_json'])`.

---

## 2. `financial_ratios` (Traditional Line-by-Line)

This table saves 16 standardized period-over-period financial ratios.
**Total unique ratios tracked:**

- `[asset_on_equity]` Tài sản trên vốn chủ sở hữu (A/E)
- `[book_value_per_share]` Giá trị sổ sách của cổ phiếu (BVPS)
- `[cash_on_current_liabilities]` Chỉ số tiền mặt
- `[current_payment]` Chỉ số thanh toán hiện hành
- `[ebit_on_interest_and_principal]` Tỷ lệ đảm bảo trả nợ
- `[ebit_on_interest_expense]` Tỷ lệ thanh toán lãi vay (EBIT/Chi phí lãi vay)
- `[equity_on_liability]` Vốn chủ sở hữu trên nợ phải trả
- `[equity_on_total_assets]` Vốn chủ sở hữu trên tổng tài sản
- `[gross_profit_margin]` Tỷ suất lợi nhuận gộp
- `[liability_on_total_assets]` Nợ phải trả trên tổng tài sản
- `[net_interest_margin]` Tỉ lệ hệ số thu nhập lãi thuần (NIM)
- `[operating_profit_margin]` Tỷ suất lợi nhuận từ hoạt động kinh doanh
- `[profit_after_tax_margin]` Tỷ suất lợi nhuận sau thuế
- `[quick_payment]` Chỉ số thanh toán nhanh
- `[roa]` Tỷ suất sinh lời trên tổng tài sản (ROA)
- `[roe]` Tỷ suất sinh lời trên vốn chủ sở hữu (ROE)
- `[trailing_eps]` Thu nhập trên mỗi cổ phần của 4 quý gần nhất (EPS)
- `[year_over_year_profit_after_tax_growth]` Tỷ lệ tăng trưởng lợi nhuận sau thuế so với cùng kỳ năm trước
- `[year_over_year_revenue_growth]` Tỷ lệ tăng trưởng doanh thu so với cùng kỳ năm trước

---

## 3. `financial_statements` (Core Accounting)

The full history of 10-year quarterly accounting data, normalized into `balance`, `income`, and `cashflow` categories.

**Income Statement (`statement_type: income`):**
1. Doanh thu bán hàng và cung cấp dịch vụ (`n_1.revenue`)
2. Doanh thu thuần về bán hàng (`n_3.net_revenue`)
3. Giá vốn hàng bán (`n_4.cost_of_goods_sold`)
4. Lợi nhuận gộp (`n_5.gross_profit`)
5. Doanh thu hoạt động tài chính (`n_6.financial_income`)
6. Chi phí tài chính (`n_7.financial_expenses`), incl. Lãi vay (`of_which_interest_expenses`)
7. Phần lãi/lỗ trong liên kết (`n_8.share_of_associates_and_joint_ventures_result`)
8. Chi phí bán hàng (`n_9.selling_expenses`)
9. Chi phí quản lý doanh nghiệp (`n_10.general_and_administrative_expenses`)
10. Lợi nhuận thuần HĐKD (`n_11.operating_profit`)
11. Lợi nhuận sau thuế TNDN (`n_18.net_profit_after_tax`)
12. Lợi nhuận của cổ đông công ty mẹ (`profit_after_tax_for_shareholders_of_parent_company`)
13. Lãi cơ bản trên cổ phiếu (`n_19.earnings_per_share_vnd`)

**Balance Sheet (`statement_type: balance`):**
*(Selection of major components tracked)*
- **Assets:** Tiền và tương đương tiền (`i.cash_and_cash_equivalents`), Phải thu ngắn hạn (`iii.short_term_receivables`), Hàng tồn kho (`iv.inventories`), Tài sản cố định (`ii.fixed_assets`), Tổng Tài Sản (`total_assets`).
- **Liabilities:** Nợ ngắn hạn (`i.short_term_liabilities`), Nợ dài hạn (`ii.long_term_liabilities`), Người mua trả tiền trước nhanh (`n_2.short_term_advances_from_customers`).
- **Equity:** Vốn chủ sở hữu (`i.owners_equity`), Lợi nhuận chưa phân phối (`undistributed_earnings_in_this_period`), Tổng Nguồn Vốn (`total_owners_equity_and_liabilities`).

**Cash Flow Statement (`statement_type: cashflow`):**
- Lưu chuyển tiền thuần từ HĐKD (`net_cash_flows_from_operating_activities`)
- Lưu chuyển tiền thuần từ HĐĐT (`net_cash_flows_from_investing_activities`)
- Lưu chuyển tiền thuần từ HĐTC (`net_cash_flows_from_financing_activities`)
- Lưu chuyển tiền thuần trong kỳ (`net_cash_flows_during_the_period`)

---

### Table 4: `company_overview` & `historical_prices`

- `company_overview`: Contains exactly the base identifiers: `industry` (e.g. Technology), `company_type` (CTCP), `established_year`, `outstanding_shares`, `charter_capital`.
- `historical_prices`: Standard daily OHLCV (Open, High, Low, Close, Volume) data cached by specific date.

---

## Provenance Tracking (Auditing Metadata)
To allow the Synthesizer and Director crews to audit the data and filter out hallucinations, **every single table** above also natively stores three tracking columns:
1. `source`: The exact API endpoint or proxy used (e.g., `vnstock-KBS`, `vnstock-VCI-regex`, `brave-search`).
2. `confidence`: A float (0.0 - 1.0) indicating reliability. Direct Broker API hits = `1.0`. Regex extracted items = `0.8`.
3. `citation`: The raw URL or endpoint string for citation checking.
