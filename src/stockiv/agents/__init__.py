"""
StockIV Agents Package

Shared agent definitions and LLM configuration.
"""

from stockiv.agents.base import DEFAULT_BASE_URL, DEFAULT_MODEL, gemini_llm, get_llm

__all__ = ["get_llm", "gemini_llm", "DEFAULT_MODEL", "DEFAULT_BASE_URL"]
