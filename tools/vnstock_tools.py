import sqlite3
import time
import pandas as pd
from vnstock import Finance, Quote, Company, Listing
from datetime import datetime, timedelta
import os

DB_PATH = "data/stockiv.db"


def _ensure_db_exists():
    """Ensure the data directory and schema exist"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create daily prices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_prices (
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
    )
    """)

    # Create financial statements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_statements (
        ticker TEXT,
        statement_type TEXT,
        period TEXT,
        item_id TEXT,
        item_name TEXT,
        value REAL,
        sort_order INTEGER DEFAULT 999,
        source TEXT,
        confidence REAL,
        citation TEXT,
        PRIMARY KEY (ticker, statement_type, period, item_id)
    )
    """)

    # Create financial ratios table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_ratios (
        ticker TEXT,
        period TEXT,
        item_id TEXT,
        item_name TEXT,
        value REAL,
        sort_order INTEGER DEFAULT 999,
        source TEXT,
        confidence REAL,
        citation TEXT,
        PRIMARY KEY (ticker, period, item_id)
    )
    """)

    # Create company overview table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_overview (
        ticker TEXT PRIMARY KEY,
        industry TEXT,
        company_type TEXT,
        established_year TEXT,
        outstanding_shares INTEGER,
        charter_capital INTEGER,
        source TEXT,
        confidence REAL,
        citation TEXT
    )
    """)

    # Create dividend history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dividend_history (
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
    )
    """)

    # Create ratio summary table (JSON-based for flexibility of the 46 columns)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ratio_summary (
        ticker TEXT,
        date TEXT,
        year_report INTEGER,
        metrics_json TEXT,
        source TEXT,
        confidence REAL,
        citation TEXT,
        PRIMARY KEY (ticker, date, year_report)
    )
    """)

    # Create live Vietstock ratios table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS live_vietstock_ratios (
        ticker TEXT,
        date TEXT,
        metrics_json TEXT,
        source TEXT,
        PRIMARY KEY (ticker, date)
    )
    """)

    conn.commit()
    conn.close()


def fetch_historical_prices(ticker: str, days_back: int = 30) -> str:
    """
    Fetches daily opening, closing, high, low prices and volume for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT', 'VCB')
        days_back: How many days of historical data to fetch (default 30)
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    try:
        df = None
        # Loop through sources as indexing can sometimes be finicky on some providers
        for src in ["TCBS", "VND", "VCI", "KBS"]:
            try:
                quote = Quote(symbol=ticker, source=src)
                df = quote.history(start=start_str, end=end_str, interval="1D")
                if df is not None and not df.empty:
                    successful_source = f"vnstock-{src}"
                    break
            except Exception:
                continue

        if df is None or df.empty:
            return f"Error: No price data found for {ticker} between {start_str} and {end_str}."

        # Standardize columns to match DB schema
        # VCI history returns: time, open, high, low, close, volume, ticker
        if "time" in df.columns:
            df = df.rename(columns={"time": "date"})

        if "ticker" not in df.columns:
            df["ticker"] = ticker

        # Ensure date format is string
        if pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Add tracking metadata
        df["source"] = successful_source
        df["confidence"] = 1.0
        df["citation"] = ""

        df = df[
            [
                "ticker",
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "source",
                "confidence",
                "citation",
            ]
        ]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO historical_prices (ticker, date, open, high, low, close, volume, source, confidence, citation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume,
                source=excluded.source,
                confidence=excluded.confidence,
                citation=excluded.citation
            """,
            df.values.tolist(),
        )
        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {len(df)} days of price data for {ticker} up to {end_str}."

    except Exception as e:
        return f"Error fetching price data for {ticker}: {str(e)}"


def fetch_financial_statements(ticker: str) -> str:
    """
    Fetches the 10-year quarterly financial statements (Income, Balance, Cash Flow) for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cache check: if we have data from this year or last year, skip fetching
    current_year = datetime.now().year
    cursor.execute(
        "SELECT MAX(period) FROM financial_statements WHERE ticker = ?", (ticker,)
    )
    latest_period = cursor.fetchone()[0]
    if latest_period and (
        str(current_year) in latest_period or str(current_year - 1) in latest_period
    ):
        conn.close()
        return f"Cache hit: Financial statements for {ticker} are already up to date (latest: {latest_period})."

    try:
        finance = Finance(symbol=ticker, source="VCI")

        # We fetch BOTH yearly and quarterly data to allow flexible "mix" analysis
        periods_to_fetch = ["year", "quarter"]
        total_rows = 0

        for p in periods_to_fetch:
            statements = {
                "income": finance.income_statement(period=p),
                "balance": finance.balance_sheet(period=p),
                "cashflow": finance.cash_flow(period=p),
            }

            for stmt_type, df in statements.items():
                if df is None or df.empty:
                    continue

                # Build sort_order map from the API's original row index
                # The API returns items in Vietnam standard format order
                sort_order_map = {row["item_id"]: idx for idx, row in df.iterrows()}

                # Melt the VCI dataframe structure: [item, item_en, item_id, 2025, 2024, ...]
                id_vars = ["item", "item_id"]
                # Only keep period columns, filter out item_en and other metadata
                val_vars = [
                    col
                    for col in df.columns
                    if col not in id_vars
                    and ("Q" in col or "-" in col or col.isdigit())
                ]

                melted_df = df.melt(
                    id_vars=id_vars,
                    value_vars=val_vars,
                    var_name="period",
                    value_name="value",
                )
                melted_df = melted_df.dropna(subset=["value"])

                # Insert into database using parameterization
                for _, row in melted_df.iterrows():
                    sort_idx = sort_order_map.get(row["item_id"], 999)
                    cursor.execute(
                        """
                    INSERT OR REPLACE INTO financial_statements (ticker, statement_type, period, item_id, item_name, value, sort_order, source, confidence, citation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            ticker,
                            stmt_type,
                            row["period"],
                            row["item_id"],
                            row["item"],
                            row["value"],
                            sort_idx,
                            "vnstock-VCI",
                            1.0,
                            "",
                        ),
                    )
                    total_rows += 1

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {total_rows} financial statement records for {ticker}."

    except Exception as e:
        conn.close()
        return f"Error fetching financial statements for {ticker}: {str(e)}"


def fetch_financial_ratios(ticker: str) -> str:
    """
    Fetches the historical financial ratios (ROE, ROA, Margins) for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cache check
    current_year = datetime.now().year
    cursor.execute(
        "SELECT MAX(period) FROM financial_ratios WHERE ticker = ?", (ticker,)
    )
    latest_period = cursor.fetchone()[0]
    if latest_period and (
        str(current_year) in latest_period or str(current_year - 1) in latest_period
    ):
        conn.close()
        return f"Cache hit: Financial ratios for {ticker} are already up to date (latest: {latest_period})."

    try:
        finance = Finance(symbol=ticker, source="VCI")

        # We fetch BOTH yearly and quarterly data
        periods_to_fetch = ["year", "quarter"]
        total_rows = 0

        for p in periods_to_fetch:
            # NOTE: Finance.ratio()'s public wrapper hardcodes limit=4 and the
            # underlying VCI API returns periods oldest-first, so the public
            # call silently returns only the OLDEST 4 periods (e.g. 2018-2019)
            # instead of the most recent ones. Call the private report method
            # directly with a generous limit to get the full period range;
            # fall back to the public method if vnstock's internals change.
            try:
                df = finance._get_financial_report(
                    "ratio", period=p, lang="en", dropna=True, limit=100
                )
            except (AttributeError, TypeError):
                df = finance.ratio(period=p)

            if df is None or df.empty:
                continue

            # Build sort_order map from the API's original row index
            sort_order_map = {row["item_id"]: idx for idx, row in df.iterrows()}

            # Melt the VCI dataframe structure
            id_vars = ["item", "item_id"]
            val_vars = [
                col
                for col in df.columns
                if col not in id_vars and ("Q" in col or "-" in col or col.isdigit())
            ]

            melted_df = df.melt(
                id_vars=id_vars,
                value_vars=val_vars,
                var_name="period",
                value_name="value",
            )
            melted_df = melted_df.dropna(subset=["value"])

            for _, row in melted_df.iterrows():
                sort_idx = sort_order_map.get(row["item_id"], 999)
                cursor.execute(
                    """
                INSERT OR REPLACE INTO financial_ratios (ticker, period, item_id, item_name, value, sort_order, source, confidence, citation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        ticker,
                        row["period"],
                        row["item_id"],
                        row["item"],
                        row["value"],
                        sort_idx,
                        "vnstock-VCI",
                        1.0,
                        "",
                    ),
                )
                total_rows += 1

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {total_rows} financial ratio records for {ticker}."

    except Exception as e:
        return f"Error fetching financial ratios for {ticker}: {str(e)}"


def fetch_company_overview(ticker: str) -> str:
    """
    Fetches the company profile and overview (industry, shares, capital) for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check cache
    cursor.execute("SELECT ticker FROM company_overview WHERE ticker = ?", (ticker,))
    if cursor.fetchone():
        conn.close()
        return f"Cache hit: Company overview for {ticker} already exists."

    try:
        company = Company(symbol=ticker)
        df = company.overview()

        if df is None or df.empty:
            conn.close()
            return f"Error: No company overview found for {ticker}."

        row = df.iloc[0]
        cursor.execute(
            """
        INSERT OR REPLACE INTO company_overview (ticker, industry, company_type, established_year, outstanding_shares, charter_capital, source, confidence, citation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                ticker,
                str(row.get("icb_name4", row.get("industry", ""))),
                str(row.get("company_type", "")),
                str(row.get("founded_date", row.get("establishedYear", ""))),
                int(row.get("outstanding_shares", 0))
                if pd.notna(row.get("outstanding_shares"))
                else 0,
                int(row.get("charter_capital", 0))
                if pd.notna(row.get("charter_capital"))
                else 0,
                "vnstock",
                1.0,
                "",
            ),
        )

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored company overview for {ticker}."

    except Exception as e:
        conn.close()
        return f"Error fetching company overview for {ticker}: {str(e)}"


def fetch_ratio_summary(ticker: str) -> str:
    """
    Fetches the comprehensive 46-metric ratio summary (PE, PB, ROE, margins, etc) for a stock.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    import json

    _ensure_db_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Check cache by date since price-dependent metrics like PE/PB change daily
    cursor.execute("SELECT MAX(date) FROM ratio_summary WHERE ticker = ?", (ticker,))
    latest_date = cursor.fetchone()[0]
    if latest_date and latest_date == today_str:
        conn.close()
        return f"Cache hit: Ratio summary for {ticker} is already up to date for {today_str}."

    try:
        company = Company(symbol=ticker, source="VCI")
        df = company.ratio_summary()

        if df is None or df.empty:
            conn.close()
            return f"Error: No ratio summary found for {ticker}."

        # Store as JSON string to handle all 46 columns flexibly
        for _, row in df.iterrows():
            year_report = int(row.get("year_report", 0))
            metrics_dict = row.dropna().to_dict()
            metrics_json = json.dumps(metrics_dict)

            cursor.execute(
                """
            INSERT OR REPLACE INTO ratio_summary (ticker, date, year_report, metrics_json, source, confidence, citation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (ticker, today_str, year_report, metrics_json, "vnstock-VCI", 0.9, ""),
            )

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored 46-metric ratio summary for {ticker} up to date {today_str}."

    except Exception as e:
        conn.close()
        return f"Error fetching ratio summary for {ticker}: {str(e)}"


def fetch_dividend_history(ticker: str) -> str:
    """
    Fetches the historical cash dividend payout history for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    import re

    _ensure_db_exists()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        company = Company(symbol=ticker, source="VCI")
        df = company.events()

        if df is None or df.empty:
            conn.close()
            return f"Error: No events found for {ticker}."

        df_div = df[df["event_code"] == "DIV"].copy()

        if df_div.empty:
            conn.close()
            return f"No dividend events found for {ticker}."

        # VCI vnstock 4.x provides value_per_share directly
        # Fallback to parsing title if value_per_share is NaN
        def extract_dividend(row):
            citation = str(row.get("source_url", ""))
            # Try value_per_share first (vnstock 4.x VCI format)
            val = row.get("value_per_share")
            if pd.notna(val) and float(val) > 0:
                return pd.Series([float(val), "vnstock-VCI", 1.0, citation])
            # Fallback: parse from event title
            title = str(row.get("event_title_vi", row.get("event_title", "")))
            match = re.search(r"([\d\.,]+)\s*VND?/?C[P]?", title, re.IGNORECASE)
            if match:
                val_str = match.group(1).replace(".", "").replace(",", ".")
                try:
                    return pd.Series(
                        [float(val_str), "vnstock-VCI-regex", 0.8, citation]
                    )
                except ValueError:
                    pass
            return pd.Series([0.0, "vnstock-VCI-fail", 0.0, citation])

        df_div[["amount", "source", "confidence", "citation"]] = df_div.apply(
            extract_dividend, axis=1
        )

        # Filter out invalid records where amount couldn't be parsed
        df_div = df_div[
            (df_div["amount"] > 0) & (df_div["exright_date"] != "1753-01-01")
        ]

        total_rows = 0
        for _, row in df_div.iterrows():
            cursor.execute(
                """
            INSERT OR REPLACE INTO dividend_history (ticker, ex_dividend_date, record_date, issue_date, event_desc, amount, source, confidence, citation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    ticker,
                    row["exright_date"],
                    row["record_date"],
                    row["issue_date"],
                    row["event_title_vi"],
                    row["amount"],
                    row["source"],
                    row["confidence"],
                    row["citation"],
                ),
            )
            total_rows += 1

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {total_rows} dividend history records for {ticker}."

    except Exception as e:
        conn.close()
        return f"Error fetching dividend history for {ticker}: {str(e)}"


def crawl_vietstock_ratios(ticker: str) -> str:
    """
    Crawls the live overview and real-time financial ratios for a stock directly from Vietstock Finance.
    Should be used to fetch the absolute latest P/E, P/B, Market Cap, Beta, and EPS.

    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data has been extracted and saved to SQLite.
    """
    import json
    import re
    import requests

    _ensure_db_exists()

    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cache check
    cursor.execute(
        "SELECT date FROM live_vietstock_ratios WHERE ticker = ? AND date = ?",
        (ticker, today_str),
    )
    if cursor.fetchone():
        conn.close()
        return f"Cache hit: Live Vietstock ratios for {ticker} already crawled today ({today_str})."

    url = f"https://finance.vietstock.vn/{ticker}-ctcp-{ticker.lower()}.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            conn.close()
            return (
                f"Error crawling {ticker} from Vietstock: HTTP {response.status_code}"
            )

        # Extract the `_stockTrade` JavaScript object using brace counting
        # (simple regex fails because the object contains nested JSON structures)
        # The object looks like: _stockTrade={"StockStatus":"","StatusName":...}||{};
        stock_trade_idx = response.text.find("_stockTrade")
        if stock_trade_idx < 0:
            conn.close()
            return f"Error crawling {ticker}: Could not locate `_stockTrade` variable in HTML."

        brace_start = response.text.find("{", stock_trade_idx)
        if brace_start < 0:
            conn.close()
            return (
                f"Error crawling {ticker}: No opening brace after `_stockTrade`."
            )

        # Count braces to find the matching closing brace
        depth = 0
        json_str = None
        for i in range(brace_start, len(response.text)):
            if response.text[i] == "{":
                depth += 1
            elif response.text[i] == "}":
                depth -= 1
                if depth == 0:
                    json_str = response.text[brace_start : i + 1]
                    break

        if json_str is None:
            conn.close()
            return (
                f"Error crawling {ticker}: Could not extract complete JSON object from `_stockTrade`."
            )

        # Verify it parses as valid JSON
        try:
            parsed_metrics = json.loads(json_str)
        except json.JSONDecodeError as de:
            conn.close()
            return f"Error crawling {ticker}: Invalid JSON extracted - {str(de)}"

        # Clean up some empty or purely visual HTML span fields injected by Vietstock
        cleaned_metrics = {}
        for k, v in parsed_metrics.items():
            if isinstance(v, str):
                # Remove spans and pure HTML tags like <span class="txt-red price">77,000</span>
                v_clean = re.sub(r"<[^>]+>", "", v)
                cleaned_metrics[k] = v_clean
            else:
                cleaned_metrics[k] = v

        final_json = json.dumps(cleaned_metrics)

        # Insert into DB
        cursor.execute(
            """
            INSERT OR REPLACE INTO live_vietstock_ratios (ticker, date, metrics_json, source)
            VALUES (?, ?, ?, ?)
            """,
            (ticker, today_str, final_json, "vietstock-crawler"),
        )

        conn.commit()
        conn.close()

        return f"Successfully crawled and stored live Vietstock ratios for {ticker} (Date: {today_str})."

    except Exception as e:
        conn.close()
        return f"Error crawling Vietstock for {ticker}: {str(e)}"


def fetch_vn100_list() -> list[str]:
    """
    Fetches the current VN100 index constituent tickers.
    Returns:
        A list of 100 ticker symbols (uppercase strings).
    """
    listing = Listing()
    symbols = listing.symbols_by_group("VN100")
    return sorted(str(s).strip().upper() for s in symbols.tolist())


def batch_fetch_ratio_summaries(
    tickers: list[str], sleep_sec: float = 1.0, force: bool = False
) -> dict:
    """
    Throttled batch fetch of ratio summaries for a list of tickers, calling the
    existing fetch_ratio_summary() per ticker with a sleep between calls to
    respect rate limits. Failures are logged and skipped (not aborted).

    Args:
        tickers: List of ticker symbols to fetch.
        sleep_sec: Seconds to sleep between per-ticker calls (default 1.0).
        force: If True, bypass today's cache and re-fetch even if already stored.
    Returns:
        dict with keys: success (int), failed (int), failed_tickers (list[str]).
    """
    _ensure_db_exists()

    success = 0
    failed = 0
    failed_tickers: list[str] = []

    today_str = datetime.now().strftime("%Y-%m-%d")

    for i, ticker in enumerate(tickers):
        if force:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "DELETE FROM ratio_summary WHERE ticker = ? AND date = ?",
                (ticker, today_str),
            )
            conn.commit()
            conn.close()

        was_cache_hit = False
        try:
            result = fetch_ratio_summary(ticker)
            if result.startswith("Cache hit"):
                was_cache_hit = True
                success += 1
            elif result.startswith("Successfully fetched"):
                success += 1
            else:
                failed += 1
                failed_tickers.append(ticker)
        except Exception:
            failed += 1
            failed_tickers.append(ticker)

        # Only throttle after calls that actually hit the network — cache
        # hits are instant and don't need rate-limit protection.
        if i < len(tickers) - 1 and sleep_sec > 0 and not was_cache_hit:
            time.sleep(sleep_sec)

    return {"success": success, "failed": failed, "failed_tickers": failed_tickers}


def crawl_vnindex_ratios() -> str:
    """
    Crawls the live VNINDEX P/E, P/B, and Market Cap from Simplize.vn.
    This fills the gap where vnstock APIs do not provide ratio_summary for broad market indices.

    Returns:
        A confirmation message that VNINDEX ratios have been extracted and saved to SQLite.
    """
    import json
    import re
    import requests

    _ensure_db_exists()

    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cache check — reuse live_vietstock_ratios table with ticker='VNINDEX'
    cursor.execute(
        "SELECT date FROM live_vietstock_ratios WHERE ticker = 'VNINDEX' AND date = ?",
        (today_str,),
    )
    if cursor.fetchone():
        conn.close()
        return f"Cache hit: VNINDEX ratios already crawled today ({today_str})."

    url = "https://simplize.vn/chi-so/VNINDEX"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            conn.close()
            return f"Error crawling VNINDEX from Simplize: HTTP {response.status_code}"

        html = response.text

        # HTML pattern: <h6 class="css-1r49m3h">LABEL</h6> ... <h6 class="css-1rshmnm">VALUE</h6>
        # Extract: P/E, P/B, Vốn hoá (Market Cap)
        def extract_value(label: str) -> str | None:
            pattern = (
                r'css-1r49m3h">' + re.escape(label) + r"</h6>"
                r'.*?css-1rshmnm">([\d,.]+[TBM]?)</h6>'
            )
            match = re.search(pattern, html, re.DOTALL)
            return match.group(1) if match else None

        pe_str = extract_value("P/E")
        pb_str = extract_value("P/B")
        market_cap_str = extract_value("Vốn hoá")

        if not pe_str and not pb_str:
            conn.close()
            return "Error crawling VNINDEX: Could not extract P/E or P/B from Simplize HTML. Page structure may have changed."

        # Build metrics dict matching the live_vietstock_ratios JSON format
        metrics = {}
        if pe_str:
            metrics["PE"] = float(pe_str.replace(",", ""))
        if pb_str:
            metrics["PB"] = float(pb_str.replace(",", ""))
        if market_cap_str:
            metrics["MarketCapital"] = market_cap_str

        final_json = json.dumps(metrics)

        cursor.execute(
            """
            INSERT OR REPLACE INTO live_vietstock_ratios (ticker, date, metrics_json, source)
            VALUES (?, ?, ?, ?)
            """,
            ("VNINDEX", today_str, final_json, "simplize-crawler"),
        )

        conn.commit()
        conn.close()

        return (
            f"Successfully crawled VNINDEX ratios from Simplize.vn (Date: {today_str}). "
            f"P/E={metrics.get('PE', 'N/A')}, P/B={metrics.get('PB', 'N/A')}, "
            f"Market Cap={metrics.get('MarketCapital', 'N/A')}"
        )

    except Exception as e:
        conn.close()
        return f"Error crawling Simplize for VNINDEX: {str(e)}"
