import sqlite3
import pandas as pd
from crewai.tools import tool
from vnstock import Finance, Quote
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

    # Create financial statements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_statements (
        ticker TEXT,
        statement_type TEXT,
        period TEXT,
        item_id TEXT,
        item_name TEXT,
        value REAL,
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
        PRIMARY KEY (ticker, period, item_id)
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
        # Fetch from vnstock 3.x
        quote = Quote(symbol=ticker, source="KBS")
        df = quote.history(start=start_str, end=end_str, interval="1D")

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

        df = df[["ticker", "date", "open", "high", "low", "close", "volume"]]

        # Save to SQLite using append (in a real app, use UPSERT)
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(
            "historical_prices", conn, if_exists="append", index=False, method="multi"
        )
        conn.close()

        return f"Successfully fetched and stored {len(df)} days of price data for {ticker} up to {end_str}."

    except Exception as e:
        return f"Error fetching price data for {ticker}: {str(e)}"


@tool("Fetch Financial Statements")
def fetch_financial_statements(ticker: str) -> str:
    """
    Fetches the 10-year quarterly financial statements (Income, Balance, Cash Flow) for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    try:
        finance = Finance(symbol=ticker, source="KBS")

        statements = {
            "income": finance.income_statement(period="quarter"),
            "balance": finance.balance_sheet(period="quarter"),
            "cashflow": finance.cash_flow(period="quarter"),
        }

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        total_rows = 0
        for stmt_type, df in statements.items():
            if df is None or df.empty:
                continue

            # Melt the KBS dataframe structure: [item, item_id, 2025-Q4, 2025-Q3, ...]
            id_vars = ["item", "item_id"]
            # Only keep quarter columns, sometimes there are extraneous columns
            val_vars = [
                col
                for col in df.columns
                if col not in id_vars and ("Q" in col or "-" in col)
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
                cursor.execute(
                    """
                INSERT OR REPLACE INTO financial_statements (ticker, statement_type, period, item_id, item_name, value)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        ticker,
                        stmt_type,
                        row["period"],
                        row["item_id"],
                        row["item"],
                        row["value"],
                    ),
                )
                total_rows += 1

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {total_rows} financial statement records for {ticker}."

    except Exception as e:
        return f"Error fetching financial statements for {ticker}: {str(e)}"


@tool("Fetch Financial Ratios")
def fetch_financial_ratios(ticker: str) -> str:
    """
    Fetches the historical financial ratios (ROE, ROA, Margins) for a specific stock ticker.
    Args:
        ticker: The stock symbol (e.g., 'FPT')
    Returns:
        A confirmation message that data is saved to SQLite.
    """
    _ensure_db_exists()

    try:
        finance = Finance(symbol=ticker, source="KBS")
        df = finance.ratio(period="quarter")

        if df is None or df.empty:
            return f"Error: No financial ratio data found for {ticker}."

        # Melt the KBS dataframe structure
        id_vars = ["item", "item_id"]
        val_vars = [
            col
            for col in df.columns
            if col not in id_vars and ("Q" in col or "-" in col)
        ]

        melted_df = df.melt(
            id_vars=id_vars, value_vars=val_vars, var_name="period", value_name="value"
        )
        melted_df = melted_df.dropna(subset=["value"])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insert into database using parameterization
        for _, row in melted_df.iterrows():
            cursor.execute(
                """
            INSERT OR REPLACE INTO financial_ratios (ticker, period, item_id, item_name, value)
            VALUES (?, ?, ?, ?, ?)
            """,
                (ticker, row["period"], row["item_id"], row["item"], row["value"]),
            )

        conn.commit()
        conn.close()

        return f"Successfully fetched and stored {len(melted_df)} financial ratio records for {ticker}."

    except Exception as e:
        return f"Error fetching financial ratios for {ticker}: {str(e)}"
