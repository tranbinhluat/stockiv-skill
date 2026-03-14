import json
import sqlite3

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class QueryStockDatabaseSchema(BaseModel):
    query: str = Field(
        ...,
        description="The SQL query to execute against the stockiv.db SQLite database.",
    )


class QueryStockDatabaseTool(BaseTool):
    name: str = "query_stock_database"
    description: str = (
        "Execute a SQL query against the local 'data/stockiv.db' SQLite database to extract financial numbers. "
        "CRITICAL DATABASE SCHEMA DETAILS: "
        "- financial_statements uses an EAV schema: (ticker, statement_type, period, item_id, item_name, value). "
        "  DO NOT query 'SELECT revenue'. Instead query: SELECT period, value FROM financial_statements WHERE ticker='XYZ' AND item_name='Revenue'. "
        "- financial_ratios also uses EAV: (ticker, period, item_id, item_name, value). "
        "- ratio_summary stores complex metrics as JSON: (ticker, date, year_report, metrics_json). "
        "- company_overview: (ticker, industry, company_type, established_year, outstanding_shares, charter_capital). "
        "Available tables: historical_prices, financial_statements, financial_ratios, company_overview, ratio_summary, dividend_history."
    )
    args_schema: Type[BaseModel] = QueryStockDatabaseSchema
    db_path: str = "data/stockiv.db"

    def _run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            if df.empty:
                return "Query returned no results."
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing query: {str(e)}"


# ---------------------------------------------------------------------------
# Helper: pivot EAV rows into a human-readable table
# ---------------------------------------------------------------------------


def _pivot_eav(df: pd.DataFrame, periods: list) -> str:
    """Pivot an EAV DataFrame (item_name, period, value) into a markdown table
    where columns = periods and rows = item_name.
    Values are formatted with comma separators for readability.
    """
    if df.empty:
        return "No data available.\n"

    # Keep only the requested periods
    df = df[df["period"].isin(periods)].copy()
    if df.empty:
        return "No data for the requested periods.\n"

    # Pivot: rows=item_name, columns=period
    pivot = df.pivot_table(
        index="item_name", columns="period", values="value", aggfunc="first"
    )

    # Reorder columns to match periods (most recent first)
    ordered_cols = [p for p in periods if p in pivot.columns]
    pivot = pivot[ordered_cols]

    # Drop rows where all values are NaN (which happens if an item is not present in ANY of the chosen periods)
    pivot = pivot.dropna(how="all")

    def fmt(val):
        if pd.isna(val):
            return "-"
        # Force integer formatting for large values (financial statements in VND)
        if abs(val) >= 1_000:
            return f"{int(val):,}"
        if abs(val) >= 0.01:
            return f"{val:,.2f}"
        return f"{val:.4f}"

    # Apply formatting and convert to string to prevent to_markdown from
    # re-formatting floats as scientific notation
    for col in pivot.columns:
        pivot[col] = pivot[col].apply(fmt).astype(str)

    return pivot.to_markdown(floatfmt="s") + "\n"


# ---------------------------------------------------------------------------
# FetchRecentFinancialsTool — NOW with pivot-table output
# ---------------------------------------------------------------------------


class FetchRecentFinancialsSchema(BaseModel):
    ticker: str = Field(
        ..., description="The stock ticker to fetch recent financials for."
    )


class FetchRecentFinancialsTool(BaseTool):
    name: str = "fetch_recent_financials"
    description: str = (
        "Gets ALL available financial statements and ratios for a ticker in PIVOT TABLE format. "
        "Output has columns = years/quarters, rows = financial items. "
        "Covers: Income Statement, Balance Sheet, Cash Flow Statement, and Key Ratios. "
        "Returns both YEARLY (last 4 years) and QUARTERLY (last 4 quarters) sections."
    )
    args_schema: Type[BaseModel] = FetchRecentFinancialsSchema
    db_path: str = "data/stockiv.db"

    def _run(self, ticker: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            stmts_df = pd.read_sql_query(
                "SELECT statement_type, period, item_name, value "
                "FROM financial_statements WHERE ticker=? ORDER BY period DESC",
                conn,
                params=(ticker,),
            )
            ratios_df = pd.read_sql_query(
                "SELECT period, item_name, value "
                "FROM financial_ratios WHERE ticker=? ORDER BY period DESC",
                conn,
                params=(ticker,),
            )
            conn.close()

            if stmts_df.empty and ratios_df.empty:
                return f"No financial data found for {ticker}."

            # Mix Yearly (last 3 years) and Quarterly (last 2 quarters) periods
            # e.g., ['2025', '2024', '2023', '2025-Q4', '2025-Q3']
            all_stmt_periods = sorted(stmts_df["period"].unique(), reverse=True)
            yearly_periods = [p for p in all_stmt_periods if "-Q" not in p][:3]
            quarterly_periods = [p for p in all_stmt_periods if "-Q" in p][:2]
            mixed_periods = yearly_periods + quarterly_periods

            # The same for ratios, though typically aligned
            all_ratio_periods = sorted(ratios_df["period"].unique(), reverse=True)
            r_yearly = [p for p in all_ratio_periods if "-Q" not in p][:3]
            r_quarterly = [p for p in all_ratio_periods if "-Q" in p][:2]
            mixed_ratio_periods = r_yearly + r_quarterly

            res = f"# Financial Data for {ticker} (Pivot Tables)\n\n"
            res += "## Financial Statements (Mixed Yearly & Quarterly)\n\n"
            for stmt_type, label in [
                ("income", "Income Statement"),
                ("balance", "Balance Sheet"),
                ("cashflow", "Cash Flow Statement"),
            ]:
                subset = stmts_df[stmts_df["statement_type"] == stmt_type]
                if not subset.empty:
                    res += f"### {label}\n"
                    res += _pivot_eav(subset, mixed_periods)
                    res += "\n"

            if not ratios_df.empty:
                res += "### Key Ratios (Mixed)\n"

                # Exclude P/E, P/B from this historical table since the user wants to rely
                # on the FetchCurrentMarketSnapshotTool / ratio_summary for current valuation ratios.
                filtered_ratios = ratios_df[
                    ~ratios_df["item_name"].str.contains(
                        "P/E|P/B", regex=True, case=False
                    )
                ]

                res += _pivot_eav(filtered_ratios, mixed_ratio_periods)
                res += "\n"

            res += "\n*Source: [SQLite Database — stockiv.db]*\n"
            return res
        except Exception as e:
            return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# FetchCurrentMarketSnapshot — SINGLE SOURCE OF TRUTH for current values
# ---------------------------------------------------------------------------


class FetchCurrentMarketSnapshotSchema(BaseModel):
    ticker: str = Field(
        ..., description="The stock ticker to get the current market snapshot for."
    )


class FetchCurrentMarketSnapshotTool(BaseTool):
    name: str = "fetch_current_market_snapshot"
    description: str = (
        "Returns the DEFINITIVE current market snapshot for a stock: "
        "latest price, date, P/E, P/B, EV/EBITDA, market cap, and VNINDEX value. "
        "Use this as the SINGLE SOURCE OF TRUTH for current valuations. "
        "Do NOT make up or approximate these values — use them EXACTLY as returned."
    )
    args_schema: Type[BaseModel] = FetchCurrentMarketSnapshotSchema
    db_path: str = "data/stockiv.db"

    # Key ratio item names to extract from financial_ratios table
    _RATIO_ITEMS = [
        "Chỉ số giá thị trường trên thu nhập (P/E)",
        "Chỉ số giá thị trường trên giá trị sổ sách (P/B)",
        "Giá trị doanh nghiệp trên lợi nhuận trước thuế, khấu hao và lãi vay (EV/EBITDA)",
        "Tỷ suất cổ tức",
        "Giá trị sổ sách của cổ phiếu (BVPS)",
    ]

    def _run(self, ticker: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)

            # 1. Latest stock price
            price_df = pd.read_sql_query(
                "SELECT date, close, volume FROM historical_prices "
                "WHERE ticker=? ORDER BY date DESC LIMIT 1",
                conn,
                params=(ticker,),
            )

            # 2. Extract metrics_json for Market Cap, EPS TTM, and BVPS
            metrics = {}
            cap_df = pd.read_sql_query(
                "SELECT date, metrics_json FROM ratio_summary "
                "WHERE ticker=? ORDER BY date DESC LIMIT 1",
                conn,
                params=(ticker,),
            )
            if not cap_df.empty:
                try:
                    metrics = json.loads(cap_df.iloc[0]["metrics_json"])
                except (json.JSONDecodeError, KeyError):
                    pass

            # 3. Dynamic Ratios Computation (Live Price)
            # We only strictly fetch Dividend Yield statically.
            # EV/EBITDA, P/E, P/B, P/S, and Market Cap are all computed dynamically below.
            ratios_df = pd.read_sql_query(
                "SELECT item_name, value FROM financial_ratios "
                "WHERE ticker=? AND period = ("
                "  SELECT MAX(period) FROM financial_ratios WHERE ticker=?"
                ") AND item_name IN ('Tỷ suất cổ tức')",
                conn,
                params=(ticker, ticker),
            )

            # 4. VNINDEX
            idx_df = pd.read_sql_query(
                "SELECT date, close FROM historical_prices "
                "WHERE ticker='VNINDEX' ORDER BY date DESC LIMIT 1",
                conn,
            )

            conn.close()

            # Build output
            res = f"# Current Market Snapshot for {ticker}\n"
            res += "⚠️ USE THESE VALUES EXACTLY — DO NOT APPROXIMATE OR HALLUCINATE\n\n"

            latest_price_k = 0
            if not price_df.empty:
                row = price_df.iloc[0]
                latest_price_k = float(row["close"])
                res += "| Metric | Value |\n|--------|-------|\n"
                res += (
                    f"| **Current Price** | **{latest_price_k:,.1f} (x1000 VND)** |\n"
                )
                res += f"| Price Date | {row['date']} |\n"
                res += f"| Volume | {row['volume']:,.0f} |\n"

            # Dynamic Core Valuations
            issue_share = metrics.get("issue_share", 0)
            if issue_share > 0 and latest_price_k > 0:
                live_market_cap = latest_price_k * 1000 * issue_share
                res += f"| Vốn hóa thị trường (Market Cap Live) | {live_market_cap:,.0f} VND |\n"

            res += "\n### Valuation Ratios (Live Computation)\n"
            res += "| Ratio | Value |\n|-------|-------|\n"

            eps_ttm = metrics.get("eps_ttm", metrics.get("eps", 0))
            bvps = metrics.get("bvps", 0)
            revenue = metrics.get("revenue", 0)
            ebitda = metrics.get("ebitda", 0)
            ev_static = metrics.get("ev", 0)
            pe_static = metrics.get("pe", 0)

            if eps_ttm > 0 and latest_price_k > 0:
                live_pe = (latest_price_k * 1000) / eps_ttm
                res += f"| Chỉ số giá thị trường trên thu nhập (P/E Live) | {live_pe:.2f} |\n"

            if bvps > 0 and latest_price_k > 0:
                live_pb = (latest_price_k * 1000) / bvps
                res += f"| Chỉ số giá thị trường trên giá trị sổ sách (P/B Live) | {live_pb:.2f} |\n"

            if issue_share > 0 and latest_price_k > 0:
                live_market_cap = latest_price_k * 1000 * issue_share
                if revenue > 0:
                    live_ps = live_market_cap / revenue
                    res += f"| Chỉ số giá thị trường trên doanh thu (P/S Live) | {live_ps:.2f} |\n"

                if ebitda > 0:
                    static_market_cap_implied = pe_static * eps_ttm * issue_share
                    net_debt_implied = ev_static - static_market_cap_implied
                    live_ev = live_market_cap + net_debt_implied
                    live_ev_ebitda = live_ev / ebitda
                    res += f"| Giá trị doanh nghiệp trên EBITDA (EV/EBITDA Live) | {live_ev_ebitda:.2f} |\n"

            # Other Ratios (Dividend)
            for _, r in ratios_df.iterrows():
                res += f"| {r['item_name']} | {r['value']:.2f} |\n"

            # VNINDEX
            if not idx_df.empty:
                row = idx_df.iloc[0]
                res += "\n### Market Index\n"
                res += "| Index | Value | Date |\n|-------|-------|------|\n"
                res += f"| VNINDEX | {row['close']:,.2f} | {row['date']} |\n"

            res += "\n*Source: [SQLite Database — stockiv.db]*\n"
            return res
        except Exception as e:
            return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# FetchPeerComparisonsTool — NOW parses JSON into readable table
# ---------------------------------------------------------------------------


class FetchPeerComparisonsSchema(BaseModel):
    target_ticker: str = Field(..., description="The main stock ticker.")


class FetchPeerComparisonsTool(BaseTool):
    name: str = "fetch_peer_comparisons"
    description: str = (
        "Fetches the latest valuation comparison (P/E, P/B, Market Cap) "
        "for the target stock and its domestic peers. Returns a clean comparison table."
    )
    args_schema: Type[BaseModel] = FetchPeerComparisonsSchema
    db_path: str = "data/stockiv.db"

    def _run(self, target_ticker: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                "SELECT ticker, date, metrics_json FROM ratio_summary "
                "WHERE date = (SELECT MAX(date) FROM ratio_summary)",
                conn,
            )
            idx_df = pd.read_sql_query(
                "SELECT date, close FROM historical_prices "
                "WHERE ticker='VNINDEX' ORDER BY date DESC LIMIT 1",
                conn,
            )
            conn.close()

            if df.empty:
                return "No peer comparison data found."

            # Parse metrics_json into columns
            records = []
            for _, row in df.iterrows():
                try:
                    metrics = json.loads(row["metrics_json"])
                    # Compute market cap from charter_capital or issue_share * price
                    market_cap = "-"
                    if metrics.get("charter_capital"):
                        market_cap = f"{metrics['charter_capital'] / 1e9:,.0f}"
                    records.append(
                        {
                            "Ticker": row["ticker"],
                            "P/E": f"{metrics['pe']:.2f}" if metrics.get("pe") else "-",
                            "P/B": f"{metrics['pb']:.2f}" if metrics.get("pb") else "-",
                            "EPS": f"{metrics['eps']:,.0f}"
                            if metrics.get("eps")
                            else "-",
                            "ROE": f"{metrics['roe'] * 100:.1f}%"
                            if metrics.get("roe")
                            else "-",
                            "Charter Capital (B VND)": market_cap,
                            "Date": row["date"],
                        }
                    )
                except (json.JSONDecodeError, TypeError):
                    records.append(
                        {
                            "Ticker": row["ticker"],
                            "P/E": "-",
                            "P/B": "-",
                            "EPS": "-",
                            "ROE": "-",
                            "Charter Capital (B VND)": "-",
                            "Date": row["date"],
                        }
                    )

            result_df = pd.DataFrame(records)

            res = "### Peer Comparison (Latest)\n"
            res += result_df.to_markdown(index=False) + "\n"

            if not idx_df.empty:
                res += f"\n### VNINDEX: {idx_df.iloc[0]['close']:,.2f} (as of {idx_df.iloc[0]['date']})\n"

            res += "\n*Source: [SQLite Database — stockiv.db]*\n"
            return res
        except Exception as e:
            return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# FetchMarketIndexTool (unchanged)
# ---------------------------------------------------------------------------


class FetchMarketIndexSchema(BaseModel):
    index_name: str = Field(
        "VNINDEX", description="The market index to fetch (e.g., 'VNINDEX', 'VN30')."
    )
    days_back: int = Field(
        30, description="Number of days of historical index data to fetch."
    )


class FetchMarketIndexTool(BaseTool):
    name: str = "fetch_market_index"
    description: str = "Fetches the recent daily prices (open, close, volume) for a market index to analyze overarching market trends."
    args_schema: Type[BaseModel] = FetchMarketIndexSchema
    db_path: str = "data/stockiv.db"

    def _run(self, index_name: str = "VNINDEX", days_back: int = 30) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            idx_df = pd.read_sql_query(
                "SELECT date, open, high, low, close, volume FROM historical_prices WHERE ticker=? ORDER BY date DESC LIMIT ?",
                conn,
                params=(index_name, days_back),
            )
            conn.close()
            if idx_df.empty:
                return f"No {index_name} data found in the database. Collector may need to run first."
            return f"### Recent {index_name} (Last {days_back} days)\n{idx_df.to_markdown(index=False)}"
        except Exception as e:
            return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# CalculateFrameworkMetricsTool — Deterministic GCCP Metrics
# ---------------------------------------------------------------------------


class CalculateFrameworkMetricsSchema(BaseModel):
    ticker: str = Field(..., description="The stock ticker to calculate metrics for.")


class CalculateFrameworkMetricsTool(BaseTool):
    name: str = "calculate_framework_metrics"
    description: str = (
        "Deterministically calculates required GCCP framework metrics (Cash Flow Divergence, "
        "Margins, Graham Criteria, Lynch PEG, Greenblatt ROA). Use this tool "
        "to avoid manual calculation errors."
    )
    args_schema: Type[BaseModel] = CalculateFrameworkMetricsSchema
    db_path: str = "data/stockiv.db"

    def _run(self, ticker: str) -> str:
        res = f"# GCCP Framework Deterministic Metrics for {ticker}\n\n"
        try:
            conn = sqlite3.connect(self.db_path)

            def get_stmt_yearly(item_name: str, limit=4):
                df = pd.read_sql_query(
                    "SELECT period, value FROM financial_statements WHERE ticker=? AND item_name LIKE ? AND period NOT LIKE '%-Q%' ORDER BY period DESC LIMIT ?",
                    conn,
                    params=(ticker, f"%{item_name}%", limit),
                )
                return df

            def get_ratio_yearly(item_name: str, limit=4):
                df = pd.read_sql_query(
                    "SELECT period, value FROM financial_ratios WHERE ticker=? AND item_name LIKE ? AND period NOT LIKE '%-Q%' ORDER BY period DESC LIMIT ?",
                    conn,
                    params=(ticker, f"%{item_name}%", limit),
                )
                return df

            # --- 1. Cash Flow Divergence ---
            res += "## 1. Cash Flow Divergence\n"
            ni_df = get_stmt_yearly("Lợi nhuận sau thuế của cổ đông của Công ty mẹ")
            ocf_df = get_stmt_yearly("Lưu chuyển tiền thuần từ hoạt động kinh doanh")

            if not ni_df.empty and not ocf_df.empty:
                merged = pd.merge(
                    ni_df, ocf_df, on="period", suffixes=("_ni", "_ocf")
                ).sort_values("period", ascending=False)
                res += "Year | Net Income | Operating Cash Flow | Match\n--- | --- | --- | ---\n"
                cf_flag = False
                for _, row in merged.iterrows():
                    ni = row["value_ni"]
                    ocf = row["value_ocf"]
                    match = "🟢 OK" if ocf >= ni else "🔴 Divergence (OCF < NI)"
                    if ocf < 0 and ni > 0:
                        match = "🚨 CRITICAL DIVERGENCE (Negative OCF but Positive NI)"
                        cf_flag = True
                    res += f"{row['period']} | {ni:,.0f} | {ocf:,.0f} | {match}\n"
                if cf_flag:
                    res += "\n**Anomaly Flag:** 🚨 The company reported 'paper profits' but failed to generate actual cash from operations in recent years. This is a massive red flag.\n\n"
                else:
                    res += "\n**Status:** No Cash Flow Divergence detected. OCF maps cleanly to Net Income.\n\n"
            else:
                res += "Data unavailable for Cash Flow Divergence check.\n\n"

            # --- 2. Margins & Quality ---
            res += "## 2. Margins & Quality\n"
            gross_margin = get_ratio_yearly("Tỷ suất lợi nhuận gộp biên")
            net_margin = get_ratio_yearly("Tỷ suất sinh lợi trên doanh thu thuần")
            roe = get_ratio_yearly(
                "Tỷ suất lợi nhuận trên vốn chủ sở hữu bình quân (ROEA)"
            )
            roa = get_ratio_yearly(
                "Tỷ suất sinh lợi trên tổng tài sản bình quân (ROAA)"
            )

            m_dfs = [gross_margin, net_margin, roe, roa]
            m_names = ["Gross Margin (%)", "Net Margin (%)", "ROE (%)", "ROA (%)"]

            if not gross_margin.empty:
                periods = gross_margin["period"].tolist()
                res += (
                    "Metric | "
                    + " | ".join(periods)
                    + "\n--- | "
                    + " | ".join(["---"] * len(periods))
                    + "\n"
                )
                for df, name in zip(m_dfs, m_names):
                    if not df.empty:
                        df_dict = dict(zip(df["period"], df["value"]))
                        row_vals = [f"{df_dict.get(p, 0):.2f}%" for p in periods]
                        res += f"{name} | " + " | ".join(row_vals) + "\n"
                res += "\n"
            else:
                res += "Margin data unavailable.\n\n"

            # --- 3. Base Metrics for Graham / Lynch ---
            metrics_df = pd.read_sql_query(
                "SELECT metrics_json FROM ratio_summary WHERE ticker=? ORDER BY date DESC LIMIT 1",
                conn,
                params=(ticker,),
            )
            pe, pb, ev_ebitda, roa_val, div_yield = 0, 0, 0, 0, 0
            if not metrics_df.empty:
                try:
                    metrics = json.loads(metrics_df.iloc[0]["metrics_json"])
                    pe = metrics.get("pe", 0)
                    pb = metrics.get("pb", 0)
                    roa_val = metrics.get("roa", 0) * 100
                    div_yield = metrics.get("dividend", 0)
                    ev_ebitda = metrics.get("ev_per_ebitda", 0)
                except Exception:
                    pass

            # Graham
            res += "## 3. Graham Defensive Criteria (Estimation)\n"
            cr_df = get_ratio_yearly("Tỷ số thanh toán hiện hành (ngắn hạn)", limit=1)
            de_df = pd.read_sql_query(
                "SELECT value FROM financial_ratios WHERE ticker=? AND item_name LIKE '%Tỷ lệ nợ trên vốn chủ sở hữu%' ORDER BY period DESC LIMIT 1",
                conn,
                params=(ticker,),
            )
            if de_df.empty:
                debt_st = get_stmt_yearly(
                    "10. Vay và nợ thuê tài chính ngắn hạn", limit=1
                )
                debt_lt = get_stmt_yearly(
                    "8. Vay và nợ thuê tài chính dài hạn", limit=1
                )
                eq = get_stmt_yearly("B. VỐN CHỦ SỞ HỮU", limit=1)
                try:
                    tot_debt = debt_st.iloc[0]["value"] + debt_lt.iloc[0]["value"]
                    eq_val = eq.iloc[0]["value"]
                    de_val = tot_debt / eq_val
                except Exception:
                    de_val = 0
            else:
                de_val = de_df.iloc[0]["value"]

            cr_val = cr_df.iloc[0]["value"] if not cr_df.empty else 0

            graham_score = 0
            graham_checks = []

            def check_graham(name, cond, val_str):
                nonlocal graham_score
                if cond:
                    graham_score += 1
                    graham_checks.append(f"- ✅ **{name}**: {val_str} (Pass)")
                else:
                    graham_checks.append(f"- ❌ **{name}**: {val_str} (Fail)")

            check_graham("Current Ratio >= 2", cr_val >= 2, f"{cr_val:.2f}")
            check_graham("Debt to Equity <= 2", de_val <= 2, f"{de_val:.2f}")
            if not ni_df.empty:
                pos_years = sum(ni_df["value"] > 0)
                check_graham(
                    f"Positive Earnings ({len(ni_df)}y)",
                    pos_years == len(ni_df),
                    f"{pos_years}/{len(ni_df)} years positive",
                )
            else:
                check_graham("Positive Earnings", False, "No data")

            check_graham("P/E < 15", 0 < pe < 15, f"P/E = {pe:.2f}")
            check_graham("P/B <= 1.5", 0 < pb <= 1.5, f"P/B = {pb:.2f}")
            check_graham("P/E * P/B <= 22.5", 0 < (pe * pb) <= 22.5, f"{pe * pb:.2f}")

            for g in graham_checks:
                res += g + "\n"
            res += f"\n**Graham Score:** {graham_score}/6 checks verifiable.\n\n"

            # Lynch & Greenblatt
            res += "## 4. Lynch & Greenblatt Metrics\n"
            res += f"- **ROA (Greenblatt Quality):** {roa_val:.2f}%\n"
            res += f"- **Earnings Yield (Inverse P/E):** {((1 / pe) * 100) if pe > 0 else 0:.2f}%\n"
            res += f"- **EV/EBITDA:** {ev_ebitda:.2f}x\n"

            eps_df = get_ratio_yearly("Thu nhập trên mỗi cổ phần", limit=4)
            if not eps_df.empty and len(eps_df) >= 2:
                eps_new = eps_df.iloc[0]["value"]
                eps_old = eps_df.iloc[-1]["value"]
                eps_cagr = (
                    ((eps_new / eps_old) ** (1 / max(1, len(eps_df) - 1)) - 1) * 100
                    if eps_old > 0
                    else 0
                )
                peg = (
                    pe / (eps_cagr + div_yield * 100)
                    if (eps_cagr + div_yield * 100) > 0
                    else 999
                )
                res += f"- **EPS {len(eps_df)}-Year CAGR:** {eps_cagr:.2f}%\n"
                res += f"- **Dividend Yield:** {div_yield * 100:.2f}%\n"
                res += f"- **Lynch PEG Ratio:** {peg:.2f} (Target < 1.0 for Fast Growers)\n"

            conn.close()
            return res
        except Exception as e:
            return f"Error computing framework metrics: {str(e)}"
