import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.vnstock_tools import (
    fetch_market_index,
    fetch_ratio_summary,
    _ensure_db_exists,
)
import sqlite3
import pandas as pd


def test_market():
    print("--- Fetching VNINDEX Prices ---")
    res1 = fetch_market_index.func(days_back=5)
    print("Result:", res1)

    # Try fetching ratio summary for VNINDEX
    print("\n--- Fetching Ratio Summary for VNINDEX ---")
    res2 = fetch_ratio_summary.func("VNINDEX")
    print("Result:", res2)

    print("\n--- Fetching Ratio Summary for a stock (FPT) ---")
    res3 = fetch_ratio_summary.func("FPT")
    print("Result:", res3)

    print("\n--- DB Check ---")
    conn = sqlite3.connect("data/stockiv.db")
    df1 = pd.read_sql(
        "SELECT * FROM historical_prices WHERE ticker='VNINDEX' LIMIT 2", conn
    )
    print("VNINDEX Prices:\n", df1)

    df2 = pd.read_sql(
        "SELECT ticker, date, metrics_json FROM ratio_summary WHERE ticker='FPT' ORDER BY date DESC LIMIT 1",
        conn,
    )
    print("\nFPT Ratio Summary:")
    if not df2.empty:
        metrics = json.loads(df2.iloc[0]["metrics_json"])
        print("PE:", metrics.get("pe", "N/A"))
        print("PB:", metrics.get("pb", "N/A"))
    else:
        print("FPT ratio summary is empty!")


if __name__ == "__main__":
    _ensure_db_exists()
    test_market()
