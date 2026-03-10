# StockIV Database Guide

This document outlines the structure, schema, and query patterns for the local SQLite database (`data/stockiv.db`) used in the StockIV project.

## Overview
StockIV uses a local SQLite database to store structured financial data retrieved primarily through the `vnstock` library (VCI/KBS providers). This architectural choice prevents LLM context window blowouts by allowing downstream agents (like Quant Analysts) to query specific required data instead of reading raw JSON dumps.

**Database Path:** `data/stockiv.db`

---

## Schema & Data Structure

### 1. historical_prices
Stores daily trading data for stock symbols and market indices.
```sql
CREATE TABLE historical_prices (
    ticker TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    source TEXT,
    confidence REAL,
    citation TEXT,
    PRIMARY KEY (ticker, date)
);
```

### 2. financial_statements
Stores narrow, melted data for all financial statements (Balance Sheet, Income Statement, Cash Flow). Both annual (`period="year"`) and quarterly (`period="quarter"`) data are stored here.
```sql
CREATE TABLE financial_statements (
    ticker TEXT,
    statement_type TEXT,
    period TEXT,
    item_id TEXT,
    item_name TEXT,
    value REAL,
    source TEXT,
    confidence REAL,
    citation TEXT,
    PRIMARY KEY (ticker, statement_type, period, item_id)
);
```

### 3. financial_ratios
Stores granular, itemized financial ratios (e.g. ROE, ROA, Margins) fetched from providers.
```sql
CREATE TABLE financial_ratios (
    ticker TEXT,
    period TEXT,
    item_id TEXT,
    item_name TEXT,
    value REAL,
    source TEXT,
    confidence REAL,
    citation TEXT,
    PRIMARY KEY (ticker, period, item_id)
);
```

### 4. ratio_summary
Stores aggregated metric summaries for a specific ticker and date. Note the compound key `(ticker, date, year_report)` which correctly captures time-sensitive ratios (like P/E and P/B) that change daily.
```sql
CREATE TABLE ratio_summary (
    ticker TEXT,
    date TEXT,
    year_report INTEGER,
    metrics_json TEXT,
    source TEXT,
    confidence REAL,
    citation TEXT,
    PRIMARY KEY (ticker, date, year_report)
);
```

### 5. dividend_history
Stores cash and stock dividend events parsed dynamically from the news/events endpoint.
```sql
CREATE TABLE dividend_history (
    ticker TEXT,
    ex_dividend_date TEXT,
    record_date TEXT,
    issue_date TEXT,
    event_desc TEXT,
    amount REAL,
    source TEXT,
    confidence REAL,
    citation TEXT,
    PRIMARY KEY (ticker, ex_dividend_date)
);
```

### 6. company_overview
Stores static, top-level company metadata.
```sql
CREATE TABLE company_overview (
    ticker TEXT PRIMARY KEY,
    industry TEXT,
    company_type TEXT,
    established_year TEXT,
    outstanding_shares INTEGER,
    charter_capital INTEGER,
    source TEXT,
    confidence REAL,
    citation TEXT
);
```

---

## Query Patterns and Best Practices

### Python/CrewAI Tool Querying
Tools should connect to the database securely and use parametrized queries to avoid SQL Injection:
```python
import sqlite3

def get_db_connection():
    db_path = "data/stockiv.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Returns dict-like rows
    return conn
```

### Example Queries

**1. Fetching the most recent 10 days of closing prices:**
```sql
SELECT date, close, volume
FROM historical_prices
WHERE ticker = 'FPT'
ORDER BY date DESC LIMIT 10;
```

**2. Fetching annual Net Income for the last 5 years:**
```sql
SELECT period, value
FROM financial_statements
WHERE ticker = 'FPT'
  AND item_name = 'Net Income' -- Example item name, actual names depend on VNSTOCK dictionary
  AND statement_type = 'income_statement'
ORDER BY period DESC LIMIT 5;
```

**3. Checking for Cached P/E Ratio before making an API call:**
Before calling external APIs, tools MUST perform a cache check across the compound key:
```sql
SELECT metrics_json
FROM ratio_summary
WHERE ticker = 'FPT'
  AND date = (SELECT MAX(date) FROM ratio_summary WHERE ticker = 'FPT')
```

**4. Filtering Dividend Events:**
Because some providers return `value=NaN` for historical dividends, query the string-based event description directly:
```sql
SELECT ex_dividend_date, event_desc, amount
FROM dividend_history
WHERE ticker = 'FPT'
ORDER BY ex_dividend_date DESC;
```

**5. Fetching Current Market Indices (VNINDEX, VN30, HNX, etc.):**
Market indices are treated as standard tickers in the `historical_prices` table.

For the overall market (VN-Index):
```sql
SELECT date, close, volume
FROM historical_prices
WHERE ticker = 'VNINDEX'
ORDER BY date DESC LIMIT 5;
```

For the VN30 index:
```sql
SELECT date, close, volume
FROM historical_prices
WHERE ticker = 'VN30'
ORDER BY date DESC LIMIT 5;
```

*(Note: There is no direct "VIX" equivalent stored natively through vnstock for Vietnam. Volatility must be calculated manually from the `VNINDEX` price history if needed, or sourced externally.)*

### Data fetching constraints to remember:
- Narrow DataFrame extraction: The `financial_statements` uses `item_id` and `item_name` because the original wide DataFrames from vnstock are "melted" before insertion.
- Broad market indices (like `VNINDEX`) are restricted from `ratio_summary` and events tracking. Rely solely on their `history()` price endpoints.
