import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.vnstock_tools import crawl_vietstock_ratios  # noqa: E402

DB_PATH = "data/stockiv.db"
TEST_TICKER = "FPT"


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear today's cache for the test ticker so the crawler actually hits the web."""
    from tools.vnstock_tools import _ensure_db_exists
    _ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM live_vietstock_ratios WHERE ticker = ?",
        (TEST_TICKER,),
    )
    conn.commit()
    conn.close()


def _fetch_stored_metrics() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metrics_json FROM live_vietstock_ratios "
        "WHERE ticker = ? ORDER BY date DESC LIMIT 1",
        (TEST_TICKER,),
    )
    row = cursor.fetchone()
    conn.close()
    assert row is not None, f"No data stored for {TEST_TICKER} after crawl"
    return json.loads(row[0])


def test_crawl_stores_float_pe_pb():
    result = crawl_vietstock_ratios(TEST_TICKER)
    assert "Successfully crawled" in result, f"Unexpected result: {result}"

    metrics = _fetch_stored_metrics()
    pe = metrics["PE"]
    pb = metrics["PB"]

    assert isinstance(pe, (int, float, str)), f"PE is {type(pe)}, expected numeric or string"
    assert isinstance(pb, (int, float, str)), f"PB is {type(pb)}, expected numeric or string"

    pe_float = float(str(pe).replace(",", ""))
    pb_float = float(str(pb).replace(",", ""))

    assert pe_float > 0, f"PE={pe_float} must be positive"
    assert pb_float > 0, f"PB={pb_float} must be positive"

    print(f"{TEST_TICKER}: PE={pe_float}, PB={pb_float}")
