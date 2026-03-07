# Collector Crew 

The **Collector Crew** is the foundation of the StockIV analytics pipeline. Acting as the "Data Gathering Authority," its primary objective is to autonomously fetch, validate, and store all raw quantitative financial data and qualitative market context required by downstream analytical crews (like the Quant Analyst and Synthesizer).

## Overview Architecture

Below is the high-level representation of data flow and agent responsibilities.

```mermaid
flowchart LR
    %% Grouping Agents
    subgraph Agents ["Collector Crew"]
        direction TB
        MDF["Market Data Fetcher"]
        MMS["Macro Micro Scout"]
    end

    %% Grouping External Sources
    subgraph Sources ["External APIs & Web"]
        direction TB
        VNSTOCK["vnstock API"]
        WEB["Brave Search"]
        PDF["Official Reports"]
    end

    %% Grouping Local Storage
    subgraph Storage ["Local Storage"]
        direction TB
        DB[("stockiv.db")]
        MD1["macro_context.md"]
        MD2["ticker_context.md"]
        MD3["annual_report.md"]
    end

    %% Relationships
    MDF -- "Quantitative Tools" --> VNSTOCK
    VNSTOCK -- "Structured Metrics" --> DB

    MDF -- "PDF Tools" --> PDF
    PDF -- "OCR extracted text" --> MD3

    MMS -- "Search Tools" --> WEB
    WEB -- "Macro News" --> MD1
    WEB -- "Ticker News" --> MD2
```

---

## 🧑‍🤝‍🧑 The Agents

### 1. Quantitative Market Data Specialist (`market_data_fetcher`)
**Role:** Extracts precise numerical data from stock APIs and populates the local database with high accuracy.
- **Tools Included:**
  - `fetch_historical_prices`: Captures OHLCV price history (stocks).
  - `fetch_market_index`: Captures macroeconomic index baselines (VNINDEX).
  - `fetch_financial_statements`: Pulls 10-year quarterly/annual Income, Balance, and Cash Flow assertions.
  - `fetch_financial_ratios`: Pulls historical ROE, ROA, and margin percentages.
  - `fetch_ratio_summary`: Grabs the deep 46-metric summary (P/E, P/B, EV/EBITDA).
  - `fetch_company_overview`: Collects static industry classification and shares outstanding.
  - `fetch_dividend_history`: Scrapes historical dividend payout cash values.
  - `search_annual_report_pdf` & `download_and_convert_pdf`: Automates finding and converting physical Annual Report PDFs into readable Markdown.

### 2. Macroeconomic & Market Context Researcher (`macro_micro_scout`)
**Role:** Hunts down global events, domestic news, and macroeconomic indicators that impact the target stock or its industry.
- **Tools Included:**
  - `search_market_context`: Autonomously searches the web (e.g., via Brave Search) to read news articles, management interviews, and macroeconomic reports. Uncovers the qualitative narrative behind the numbers.

---

## 📋 Task Execution Pipeline

The Collector Crew executes its tasks sequentially to ensure dependencies are met.

```mermaid
sequenceDiagram
    autonumber
    participant Orchestrator
    participant MDF as Data Fetcher
    participant MMS as Context Scout
    participant DB as SQLite
    participant Disk as File System

    Orchestrator->>MDF: fetch_financials_task
    MDF->>DB: INSERT Statements, Ratios, Dividends
    
    Orchestrator->>MDF: fetch_daily_market_data_task
    MDF->>DB: INSERT VNINDEX, P/E, Peers
    
    Orchestrator->>MMS: fetch_macro_context_task
    MMS->>Disk: Write macro_context.md
    
    Orchestrator->>MMS: fetch_ticker_context_task
    MMS->>Disk: Write ticker_context.md
    
    Orchestrator->>MDF: fetch_annual_report_task
    MDF->>Disk: Write parsed annual_report.md
```

### Detailed Task Breakdown

1. **`fetch_financials_task`**
   - **Goal:** Build the historical foundation. 
   - **Action:** Triggers the Data Fetcher to utilize `vnstock` tools to pull 10-year financial records and ratios, caching them directly into `stockiv.db` to prevent repetitive, expensive API calls down the line.

2. **`fetch_daily_market_data_task`**
   - **Goal:** Capture the "Today" snapshot.
   - **Action:** Pulls current daily prices for VNINDEX and the target stock. Updates the `ratio_summary` with live valuation metrics (P/E, P/B). It also identifies and retrieves data for top domestic competitors for instant peer comparisons.

3. **`fetch_macro_context_task`**
   - **Goal:** Big picture qualitative research.
   - **Action:** The Context Scout explicitly avoids researching the specific ticker. Instead, it looks at US Fed rates, Vietnam's domestic economy, and broad sector/industry headwinds/tailwinds. Outputs raw, comprehensive narratives to `data/raw/context/`.

4. **`fetch_ticker_context_task`**
   - **Goal:** Narrow qualitative research.
   - **Action:** With macro context understood, the Scout searches for specific news events, product launches, or earnings leaks explicitly tied to the target ticker. Results are physically saved to `data/raw/context/`.

5. **`fetch_annual_report_task`**
   - **Goal:** Deep fundamental document retrieval.
   - **Action:** Calculates the most recent fiscal year, hunts the web for the official Vietnamese "Báo cáo thường niên" PDF, downloads it, and utilizes extraction tools (like PyMuPDF) to convert the heavy PDF into an LLM-friendly Markdown file stored in `data/processed/annual_reports/`.

---

## 💾 Storage & Data Accessibility

**Rule of Thumb for Downstream Crews:** *If the Collector Crew ran successfully, you do NOT need API tools. Read from disk.*

- **Quantitative Analysts / Synthesizer:** Use the `QueryStockDatabaseTool` and `FetchMarketIndexTool` to execute SQL queries directly against `data/stockiv.db`.
- **Sentiment Analysts / Reporting:** Use the `DirectoryReadTool` or `FileReadTool` to read the context `.md` files residing in `data/raw/` and `data/processed/`.
![alt text](image.png)