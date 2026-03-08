"""
Shared State for StockIV Flows
"""

from pydantic import BaseModel


class PipelineState(BaseModel):
    """General state flowing through StockIV orchestration pipelines."""

    # Core Flow Control
    request: str = ""
    target_ticker: str = ""
    history: str = ""
    is_mock: bool = False

    # Centralized Weekly Report Metadata
    report_year: str = ""
    report_week: str = ""
    report_title: str = ""
    report_md_path: str = ""
    report_pdf_path: str = ""

    # Centralized Context Paths
    market_context_path: str = ""
    ticker_context_path: str = ""

    # Generic dictionary for storing any workflow-specific outputs
    shared_data: dict = {}
