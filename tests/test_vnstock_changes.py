"""Integration tests for functions changed during vnstock 3.x -> 4.x migration."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.vnstock_tools import (  # noqa: E402
    fetch_dividend_history,
    fetch_financial_ratios,
    fetch_financial_statements,
    fetch_historical_prices,
    fetch_ratio_summary,
)

DB_PATH = "data/stockiv.db"
TEST_TICKER = "FPT"


def _clear_cache(table: str, ticker: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"DELETE FROM {table} WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# fetch_historical_prices
# ---------------------------------------------------------------------------


def test_fetch_historical_prices_returns_success():
    result = fetch_historical_prices(TEST_TICKER, days_back=5)
    assert "Successfully fetched" in result, f"Unexpected: {result}"


def test_fetch_historical_prices_stores_valid_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, open, high, low, close, volume, source "
        "FROM historical_prices WHERE ticker = ? ORDER BY date DESC LIMIT 5",
        (TEST_TICKER,),
    )
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) > 0, "No price data stored"
    for row in rows:
        date_str, open_, high, low, close, volume, source = row
        assert open_ > 0, f"open must be positive, got {open_} on {date_str}"
        assert high >= low, f"high({high}) < low({low}) on {date_str}"
        assert close > 0, f"close must be positive, got {close} on {date_str}"
        assert volume >= 0, f"volume must be non-negative, got {volume} on {date_str}"
        assert "vnstock" in source, f"source should contain vnstock, got: {source}"


# ---------------------------------------------------------------------------
# fetch_financial_statements  (KBS -> VCI migration)
# ---------------------------------------------------------------------------


class TestFinancialStatements:
    @classmethod
    def setup_class(cls):
        _clear_cache("financial_statements", TEST_TICKER)

    def test_returns_success(self):
        result = fetch_financial_statements(TEST_TICKER)
        assert "Successfully fetched" in result, f"Unexpected: {result}"

    def test_stores_key_items(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT DISTINCT statement_type FROM financial_statements WHERE ticker = ?",
            (TEST_TICKER,),
        )
        types = [r[0] for r in cursor.fetchall()]
        assert "income" in types, f"Missing income statement, have: {types}"
        assert "balance" in types, f"Missing balance sheet, have: {types}"
        assert "cashflow" in types, f"Missing cash flow, have: {types}"

        cursor.execute(
            "SELECT COUNT(*) FROM financial_statements WHERE ticker = ?", (TEST_TICKER,)
        )
        count = cursor.fetchone()[0]
        assert count > 100, f"Too few records: {count}"

        cursor.execute(
            "SELECT value FROM financial_statements WHERE ticker = ? "
            "AND (item_name LIKE '%Lợi nhuận của Cổ đông của Công ty mẹ%' "
            "  OR item_name LIKE '%Lợi nhuận sau thuế%') "
            "AND period NOT LIKE '%-Q%' ORDER BY period DESC LIMIT 1",
            (TEST_TICKER,),
        )
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "Net profit item not found"
        assert row[0] > 0, f"Net profit must be positive, got {row[0]}"

    def test_has_sort_order(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sort_order FROM financial_statements "
            "WHERE ticker = ? AND statement_type = 'income' "
            "AND period = (SELECT MAX(period) FROM financial_statements "
            "WHERE ticker = ? AND statement_type = 'income' AND period NOT LIKE '%-Q%') "
            "ORDER BY sort_order",
            (TEST_TICKER, TEST_TICKER),
        )
        orders = [r[0] for r in cursor.fetchall()]
        conn.close()
        assert len(orders) > 5, f"Too few rows with sort_order: {len(orders)}"
        assert orders == sorted(orders), "sort_order not monotonically increasing"


# ---------------------------------------------------------------------------
# fetch_financial_ratios  (KBS -> VCI migration)
# ---------------------------------------------------------------------------


class TestFinancialRatios:
    @classmethod
    def setup_class(cls):
        _clear_cache("financial_ratios", TEST_TICKER)

    def test_returns_success(self):
        result = fetch_financial_ratios(TEST_TICKER)
        assert "Successfully fetched" in result, f"Unexpected: {result}"

    def test_stores_key_metrics(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM financial_ratios WHERE ticker = ?", (TEST_TICKER,)
        )
        count = cursor.fetchone()[0]
        assert count > 30, f"Too few ratio records: {count}"

        for metric in ["ROE (%)", "ROA (%)", "Biên LN gộp (%)"]:
            cursor.execute(
                "SELECT value FROM financial_ratios WHERE ticker = ? "
                "AND item_name = ? "
                "AND period NOT LIKE '%-Q%' ORDER BY period DESC LIMIT 1",
                (TEST_TICKER, metric),
            )
            row = cursor.fetchone()
            assert row is not None, f"Metric '{metric}' not found"
            assert row[0] != 0, f"Metric '{metric}' is zero"

        conn.close()

    def test_has_sort_order(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT sort_order FROM financial_ratios "
            "WHERE ticker = ? AND period = (SELECT MAX(period) FROM financial_ratios "
            "WHERE ticker = ? AND period NOT LIKE '%-Q%') "
            "ORDER BY sort_order",
            (TEST_TICKER, TEST_TICKER),
        )
        orders = [r[0] for r in cursor.fetchall()]
        conn.close()
        assert len(orders) > 5
        assert orders == sorted(orders), "sort_order not monotonically increasing"


# ---------------------------------------------------------------------------
# fetch_ratio_summary
# ---------------------------------------------------------------------------


def test_fetch_ratio_summary_stores_json_metrics():
    _clear_cache("ratio_summary", TEST_TICKER)
    result = fetch_ratio_summary(TEST_TICKER)
    assert "Successfully fetched" in result, f"Unexpected: {result}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT metrics_json FROM ratio_summary "
        "WHERE ticker = ? ORDER BY year_report DESC LIMIT 1",
        (TEST_TICKER,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "No ratio_summary stored"
    metrics = json.loads(row[0])
    vci_keys = {"pe", "pb", "roe", "roa"}
    found = vci_keys & set(metrics.keys())
    assert found, f"None of {vci_keys} in ratio_summary keys: {list(metrics.keys())[:20]}"


# ---------------------------------------------------------------------------
# fetch_dividend_history  (column name migration: 3.x -> 4.x)
# ---------------------------------------------------------------------------


def test_fetch_dividend_history_returns_success():
    result = fetch_dividend_history(TEST_TICKER)
    assert "Successfully fetched" in result, f"Unexpected: {result}"


def test_fetch_dividend_history_stores_valid_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ex_dividend_date, record_date, issue_date, event_desc, amount, source "
        "FROM dividend_history WHERE ticker = ? ORDER BY ex_dividend_date DESC",
        (TEST_TICKER,),
    )
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) > 0, "No dividend records stored"

    valid_count = 0
    for row in rows:
        ex_date, rec_date, issue_date, desc, amount, source = row
        assert amount > 0, f"amount must be positive, got {amount} on {ex_date}"
        assert len(desc) > 0, f"event_desc must not be empty on {ex_date}"
        assert "vnstock" in source, f"source should contain vnstock, got: {source}"
        valid_count += 1

    assert valid_count >= 1, f"Need at least 1 valid dividend record, got {valid_count}"


def test_fetch_dividend_history_amount_is_float():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT amount FROM dividend_history "
        "WHERE ticker = ? AND amount > 0 ORDER BY ex_dividend_date DESC LIMIT 1",
        (TEST_TICKER,),
    )
    row = cursor.fetchone()
    conn.close()
    assert row is not None, "No dividend with positive amount"
    assert isinstance(row[0], float), f"amount must be float, got {type(row[0])}"
