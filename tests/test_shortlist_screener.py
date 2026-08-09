"""Tests for the /shortlist GCCP Quality-Value Composite Screener (Sprint 3)."""
import json
import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.vnstock_tools import (  # noqa: E402
    fetch_vn100_list,
    batch_fetch_ratio_summaries,
)
from tools.sqlite_tools import (  # noqa: E402
    _rank_dataframe,
    compute_shortlist_rankings,
)

DB_PATH = "data/stockiv.db"


# ---------------------------------------------------------------------------
# _rank_dataframe — pure ranking math, no network (hand-verified expectations)
# ---------------------------------------------------------------------------


def _synthetic_df():
    # A,B,D have valid PE; C is negative PE; E has missing PE.
    return pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D", "E"],
            "roe": [0.30, 0.20, 0.25, 0.10, 0.05],
            "roa": [0.15, 0.10, 0.20, 0.05, 0.02],
            "pe": [10, 8, -5, 12, None],
        }
    )


def test_rank_dataframe_roe_rank_1_is_highest():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")
    assert row.loc["A", "roe_rank"] == 1  # highest ROE (.30)
    assert row.loc["E", "roe_rank"] == 5  # lowest ROE (.05)


def test_rank_dataframe_roa_rank_1_is_highest():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")
    assert row.loc["C", "roa_rank"] == 1  # highest ROA (.20)
    assert row.loc["E", "roa_rank"] == 5  # lowest ROA (.02)


def test_rank_dataframe_pe_rank_1_is_cheapest():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")
    assert row.loc["B", "pe_rank"] == 1  # cheapest valid PE (8)
    assert row.loc["A", "pe_rank"] == 2  # PE=10
    assert row.loc["D", "pe_rank"] == 3  # PE=12


def test_rank_dataframe_negative_pe_gets_worst_rank():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")
    n = len(df)
    assert row.loc["C", "pe_rank"] == n  # negative PE forced to last place


def test_rank_dataframe_missing_pe_gets_worst_rank():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")
    n = len(df)
    assert row.loc["E", "pe_rank"] == n  # missing PE forced to last place


def test_rank_dataframe_final_rank_matches_hand_calculation():
    df = _rank_dataframe(_synthetic_df())
    row = df.set_index("ticker")

    # Hand-verified composite: rank_score_roa_pe + rank_score_roe_pe, re-ranked
    expected_final_rank = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    for ticker, expected in expected_final_rank.items():
        assert row.loc[ticker, "final_rank"] == expected, (
            f"{ticker}: expected final_rank={expected}, got "
            f"{row.loc[ticker, 'final_rank']}"
        )


def test_rank_dataframe_keeps_all_tickers():
    df = _rank_dataframe(_synthetic_df())
    assert len(df) == 5
    assert set(df["ticker"]) == {"A", "B", "C", "D", "E"}


# ---------------------------------------------------------------------------
# fetch_vn100_list — network
# ---------------------------------------------------------------------------


def test_fetch_vn100_list_returns_100_tickers():
    tickers = fetch_vn100_list()
    assert len(tickers) == 100
    assert all(isinstance(t, str) and t.isupper() for t in tickers)
    assert "FPT" in tickers or "ACB" in tickers


# ---------------------------------------------------------------------------
# batch_fetch_ratio_summaries — network, small batch to keep test fast
# ---------------------------------------------------------------------------


def test_batch_fetch_ratio_summaries_small_batch():
    result = batch_fetch_ratio_summaries(["FPT", "MWG"], sleep_sec=0)
    assert result["success"] >= 1
    assert result["success"] + result["failed"] == 2


def test_batch_fetch_ratio_summaries_skips_bad_ticker():
    result = batch_fetch_ratio_summaries(["FPT", "ZZZINVALID"], sleep_sec=0)
    assert result["success"] >= 1
    assert "ZZZINVALID" in result["failed_tickers"]


# ---------------------------------------------------------------------------
# compute_shortlist_rankings — network (small subset via `tickers` override)
# ---------------------------------------------------------------------------


def test_compute_shortlist_rankings_creates_table_and_csv():
    subset = ["FPT", "MWG", "VCB"]
    batch_fetch_ratio_summaries(subset, sleep_sec=0)

    summary = compute_shortlist_rankings(tickers=subset)
    assert isinstance(summary, str)
    assert "FPT" in summary or "MWG" in summary or "VCB" in summary

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM screener_rankings WHERE ticker IN (?, ?, ?) "
        "AND run_date = (SELECT MAX(run_date) FROM screener_rankings)",
        conn,
        params=subset,
    )
    conn.close()
    assert len(df) >= 1
    for col in [
        "roe",
        "roa",
        "pe",
        "roe_rank",
        "roa_rank",
        "pe_rank",
        "score_roa_pe",
        "score_roe_pe",
        "rank_score_roa_pe",
        "rank_score_roe_pe",
        "final_rank",
    ]:
        assert col in df.columns


def test_compute_shortlist_rankings_exports_csv():
    from datetime import datetime

    subset = ["FPT", "MWG", "VCB"]
    batch_fetch_ratio_summaries(subset, sleep_sec=0)
    compute_shortlist_rankings(tickers=subset)

    today_str = datetime.now().strftime("%Y-%m-%d")
    csv_path = Path(f"data/reports/market/shortlist_{today_str}.csv")
    assert csv_path.exists()
    csv_df = pd.read_csv(csv_path)
    assert "final_rank" in csv_df.columns
    assert csv_df["final_rank"].is_monotonic_increasing
