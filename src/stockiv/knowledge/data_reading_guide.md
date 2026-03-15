# Data Reading Guide: Utilizing the Local SQLite Database

This guide dictates how downstream crews (like Quant Analyst, Synthesizer, and Reporter) must access quantitative and market data stored by the Collector crew. Direct API calls are expensive and rate-limited. Therefore, the Collector pre-fetches data into `data/stockiv.db`. You MUST use the provided SQLite-based tools to retrieve data.

## 1. Accessing Market Data (VNINDEX)
The macro market environment is represented by the **VNINDEX**. The Collector crew captures daily open, close, and volume data for this index.

- **Tool:** Use the `FetchMarketIndex` tool.
- **Input:** `days_back` (integer, e.g., 30 for the last month, 90 for the last quarter).
- **Return Format:** A Markdown table containing the recent trading history of VNINDEX.

*Note on VNINDEX Valuation Ratios:* The Collector crew also scrapes the current VNINDEX P/E, P/B, and Market Cap from Simplize.vn via the `Crawl VNINDEX Ratios` tool. These values are stored in the `live_vietstock_ratios` table (with `ticker='VNINDEX'`) and are automatically included in the `FetchCurrentMarketSnapshotTool` output under the "### Market Index" section.

## 2. Accessing Specific Stock Metrics (P/E, P/B, ROE)
Detailed fundamental metrics for specific stocks (e.g., FPT) are stored inside the `ratio_summary` table. Because `vnstock` returns 46 separate columns of data, this information is stored as a JSON object inside the `metrics_json` column.

- **Tool:** Use the `QueryStockDatabase` tool.
- **Input Query:** A precise SQLite query.
- **Return Format:** A Markdown table.

**Example Query:** To get the most recent P/E and P/B snapshot for FPT:
```sql
SELECT
    ticker,
    date,
    metrics_json
FROM ratio_summary
WHERE ticker = 'FPT'
ORDER BY date DESC
LIMIT 1;
```
*Agent Instruction:* Once you receive the `metrics_json` string back, you must parse the string to extract the keys you need, such as `"pe"`, `"pb"`, `"roe"`, etc.

## 3. Accessing Historical Prices for a Stock
The `historical_prices` table holds the 1D interval OHLCV data for all fetched stocks.

**Example Query:**
```sql
SELECT
    date,
    close,
    volume
FROM historical_prices
WHERE ticker = 'FPT'
ORDER BY date DESC
LIMIT 14;
```

## Summary of Core Tables in `data/stockiv.db`
1. **`historical_prices`**: `(ticker, date, open, high, low, close, volume, source, confidence, citation)` - Holds daily stock and VNINDEX OHLCV.
2. **`ratio_summary`**: `(ticker, date, year_report, metrics_json, source, confidence, citation)` - Holds complex 46-metric ratio summaries for companies.
3. **`financial_statements`**: Income, Balance Sheet, Cash Flow items.
4. **`financial_ratios`**: Basic ROA/ROE historical numbers.
5. **`company_overview`**: Static info (industry, shares outstanding).

**CRITICAL RULE:** Do NOT use external API tools (like `fetch_historical_prices`) in your downstream tasks. Always query the `stockiv.db` internal database. If the DB returns empty, it means the Collector Crew failed upstream.
