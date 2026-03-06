import sqlite3
import pandas as pd
from pydantic import BaseModel, Field
from typing import Any, Type
from crewai.tools import BaseTool
import json

class QueryStockDatabaseSchema(BaseModel):
    query: str = Field(..., description="The SQL query to execute against the stockiv.db SQLite database.")

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
