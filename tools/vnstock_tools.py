import sqlite3
from crewai.tools import tool
from vnstock import stock_historical_data
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
        PRIMARY KEY (ticker, date)
    )
    """)
    conn.commit()
    conn.close()


@tool("Fetch Historical Prices")
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
        # Fetch from vnstock
        df = stock_historical_data(ticker, start_str, end_str, "1D")

        if df is None or df.empty:
            return f"Error: No price data found for {ticker} between {start_str} and {end_str}."

        # Standardize columns
        if "time" in df.columns:
            df = df.rename(columns={"time": "date"})

        # Ensure we have the ticker column
        if "ticker" not in df.columns:
            df["ticker"] = ticker

        # Keep only required columns
        df = df[["ticker", "date", "open", "high", "low", "close", "volume"]]

        # Save to SQLite
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(
            "historical_prices", conn, if_exists="append", index=False, method="multi"
        )
        conn.close()

        # NOTE: UPSERT logic is complex with pandas to_sql, so in a real production app
        # we would use executemany with ON CONFLICT DO UPDATE.
        # For simplicity here, we append and downstream readers will take max(date).

        return f"Successfully fetched and stored {len(df)} days of price data for {ticker} up to {end_str}."

    except Exception as e:
        return f"Error fetching price data for {ticker}: {str(e)}"


# TODO: Add tool for financial statements.
# Note: vnstock financial_ratio and financial_flow endpoints are currently blocked
# by 401 Unauthorized errors from TCBS upstream. A localized CSV approach or a paid
# API key will be required to fetch quarterly financial statements reliably.
