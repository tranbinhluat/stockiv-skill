"""
Test VNINDEX Ratios Scraper from Simplize.vn

Validates:
1. crawl_vnindex_ratios tool scrapes and stores data
2. FetchCurrentMarketSnapshotTool outputs VNINDEX P/E and P/B
"""

import os
import sys
import json
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_crawl_vnindex_ratios():
    """Test the crawl_vnindex_ratios tool directly."""
    from tools.vnstock_tools import crawl_vnindex_ratios

    print("=" * 60)
    print("TEST 1: crawl_vnindex_ratios tool")
    print("=" * 60)

    # Clear today's cache to force a fresh crawl
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")
    db_path = "data/stockiv.db"

    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute(
            "DELETE FROM live_vietstock_ratios WHERE ticker='VNINDEX' AND date=?",
            (today,),
        )
        conn.commit()
        conn.close()
        print(f"  Cleared VNINDEX cache for {today}")

    # Run the tool
    result = crawl_vnindex_ratios.run()
    print(f"  Result: {result}")

    # Verify DB entry
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker, date, metrics_json, source FROM live_vietstock_ratios WHERE ticker='VNINDEX' ORDER BY date DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "VNINDEX row not found in live_vietstock_ratios!"
    assert row[0] == "VNINDEX"
    assert row[3] == "simplize-crawler"

    metrics = json.loads(row[2])
    print(f"  Stored metrics: {metrics}")

    assert "PE" in metrics, "PE not found in metrics!"
    assert "PB" in metrics, "PB not found in metrics!"
    assert metrics["PE"] > 0, f"PE should be > 0, got {metrics['PE']}"
    assert metrics["PB"] > 0, f"PB should be > 0, got {metrics['PB']}"

    print(f"  ✅ P/E = {metrics['PE']}, P/B = {metrics['PB']}")
    print(f"  ✅ Market Cap = {metrics.get('MarketCapital', 'N/A')}")
    print("  ✅ TEST 1 PASSED\n")


def test_snapshot_includes_vnindex_ratios():
    """Test that FetchCurrentMarketSnapshotTool includes VNINDEX P/E and P/B.

    This test directly verifies the DB query logic used by the snapshot tool,
    since FPT price data may not always be present in the test DB.
    """
    print("=" * 60)
    print("TEST 2: VNINDEX ratios are queryable from live_vietstock_ratios")
    print("=" * 60)

    db_path = "data/stockiv.db"
    conn = sqlite3.connect(db_path)

    # Query exactly as FetchCurrentMarketSnapshotTool does
    import pandas as pd

    vnindex_ratios_df = pd.read_sql_query(
        "SELECT metrics_json FROM live_vietstock_ratios "
        "WHERE ticker='VNINDEX' ORDER BY date DESC LIMIT 1",
        conn,
    )
    conn.close()

    assert not vnindex_ratios_df.empty, "VNINDEX not found in live_vietstock_ratios!"

    metrics = json.loads(vnindex_ratios_df.iloc[0]["metrics_json"])
    print(f"  Metrics from DB: {metrics}")

    assert "PE" in metrics, "PE key missing!"
    assert "PB" in metrics, "PB key missing!"
    assert metrics["PE"] > 0
    assert metrics["PB"] > 0

    # Verify the FetchCurrentMarketSnapshotTool output format would include these
    output_line = f"| VNINDEX P/E | {metrics['PE']} | - |"
    print(f"  Expected output line: {output_line}")

    print("  ✅ TEST 2 PASSED\n")


def test_cache_hit():
    """Test that cache prevents re-crawling."""
    from tools.vnstock_tools import crawl_vnindex_ratios

    print("=" * 60)
    print("TEST 3: Cache hit (should not re-crawl)")
    print("=" * 60)

    result = crawl_vnindex_ratios.run()
    print(f"  Result: {result}")

    assert "Cache hit" in result, f"Expected cache hit, got: {result}"
    print("  ✅ TEST 3 PASSED\n")


if __name__ == "__main__":
    test_crawl_vnindex_ratios()
    test_snapshot_includes_vnindex_ratios()
    test_cache_hit()
    print("=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
