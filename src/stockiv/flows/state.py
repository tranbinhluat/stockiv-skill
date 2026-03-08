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
    mock_crews: list[str] = []

    # Generic dictionary for storing any workflow-specific outputs
    shared_data: dict = {}
