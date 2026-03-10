import sqlite3
import pandas as pd
from pydantic import BaseModel, Field
from typing import Type
from crewai.tools import BaseTool


class QueryStockDatabaseSchema(BaseModel):
    query: str = Field(
        ...,
        description="The SQL query to execute against the stockiv.db SQLite database.",
    )


class QueryStockDatabaseTool(BaseTool):
    name: str = "Query Stock Database"
    description: str = (
        "Execute a SQL query against the local 'data/stockiv.db' SQLite database to extract financial numbers. "
        "Available tables: historical_prices, financial_statements, financial_ratios, company_overview, ratio_summary."
    )
    args_schema: Type[BaseModel] = QueryStockDatabaseSchema
    db_path: str = "data/stockiv.db"

    def _run(self, query: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            # Convert to markdown table or JSON string
            if df.empty:
                return "Query returned no results."
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing query: {str(e)}"


class FetchRecentFinancialsSchema(BaseModel):
    ticker: str = Field(
        ..., description="The stock ticker to fetch recent financials for."
    )


class FetchRecentFinancialsTool(BaseTool):
    name: str = "Fetch Recent Financials"
    description: str = "Gets the last 4 quarters and last 2 years of financial statements and ratios for a ticker."
    args_schema: Type[BaseModel] = FetchRecentFinancialsSchema
    db_path: str = "data/stockiv.db"

    def _run(self, ticker: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                f"SELECT * FROM financial_statements WHERE ticker='{ticker}' ORDER BY period DESC LIMIT 100",
                conn,
            )
            ratios_df = pd.read_sql_query(
                f"SELECT * FROM financial_ratios WHERE ticker='{ticker}' ORDER BY period DESC LIMIT 50",
                conn,
            )
            conn.close()
            res = f"### Financials for {ticker}\n{df.to_markdown(index=False)}\n\n"
            res += f"### Ratios for {ticker}\n{ratios_df.to_markdown(index=False)}"
            return res
        except Exception as e:
            return f"Error: {str(e)}"


class FetchPeerComparisonsSchema(BaseModel):
    target_ticker: str = Field(..., description="The main stock ticker.")


class FetchPeerComparisonsTool(BaseTool):
    name: str = "Fetch Peer Comparisons"
    description: str = "Fetches the latest Ratio Summary (P/E, P/B, Market Cap) for the target and its top domestic peers."
    args_schema: Type[BaseModel] = FetchPeerComparisonsSchema
    db_path: str = "data/stockiv.db"

    def _run(self, target_ticker: str) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            # Fetch ratio summary for target AND its peers from ratio_summary table
            df = pd.read_sql_query(
                "SELECT ticker, date, metrics_json FROM ratio_summary "
                "WHERE date = (SELECT MAX(date) FROM ratio_summary)",
                conn,
            )

            # Include VNINDEX as well
            idx_df = pd.read_sql_query(
                "SELECT * FROM historical_prices WHERE ticker='VNINDEX' ORDER BY date DESC LIMIT 1",
                conn,
            )
            conn.close()

            res = f"### Latest Peer Ratio Summaries\n{df.to_markdown(index=False)}\n\n"
            res += f"### Latest VNINDEX\n{idx_df.to_markdown(index=False)}"
            return res
        except Exception as e:
            return f"Error: {str(e)}"


class FetchMarketIndexSchema(BaseModel):
    index_name: str = Field(
        "VNINDEX", description="The market index to fetch (e.g., 'VNINDEX', 'VN30')."
    )
    days_back: int = Field(
        30, description="Number of days of historical index data to fetch."
    )


class FetchMarketIndexTool(BaseTool):
    name: str = "Fetch Market Index"
    description: str = "Fetches the recent daily prices (open, close, volume) for a market index to analyze overarching market trends."
    args_schema: Type[BaseModel] = FetchMarketIndexSchema
    db_path: str = "data/stockiv.db"

    def _run(self, index_name: str = "VNINDEX", days_back: int = 30) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            idx_df = pd.read_sql_query(
                f"SELECT date, open, high, low, close, volume FROM historical_prices WHERE ticker='{index_name}' ORDER BY date DESC LIMIT {days_back}",
                conn,
            )
            conn.close()
            if idx_df.empty:
                return f"No {index_name} data found in the database. Collector may need to run first."
            return f"### Recent {index_name} (Last {days_back} days)\n{idx_df.to_markdown(index=False)}"
        except Exception as e:
            return f"Error: {str(e)}"
