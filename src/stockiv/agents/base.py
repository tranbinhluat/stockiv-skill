"""
Base LLM Configuration for StockIV

All agents use this shared LLM configuration to avoid repetition.
"""

import os
from crewai import LLM


# Default model configuration
DEFAULT_MODEL = "gemini-3-flash"
DEFAULT_BASE_URL = None


def get_llm(model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL) -> LLM:
    """
    Get a configured LLM instance.

    Args:
        model: Model name (default: gemini-2.5-pro)
        base_url: API base URL (default: None)

    Returns:
        Configured LLM instance
    """
    return LLM(
        model=f"gemini/{model}",
        api_key=os.getenv("GOOGLE_API_KEY"),
        base_url=base_url,
    )


# Default LLM instance
gemini_llm = get_llm()
