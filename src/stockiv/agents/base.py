"""
Base LLM Configuration for StockIV

All agents use this shared LLM configuration to avoid repetition.
"""

import os
from crewai import LLM


# Default model configuration
DEFAULT_MODEL = "qwen3.5-plus"
DEFAULT_BASE_URL = os.getenv(
    "ANTHROPIC_BASE_URL", "https://coding-intl.dashscope.aliyuncs.com/apps/anthropic"
)


def get_llm(model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL) -> LLM:
    """
    Get a configured LLM instance.

    Args:
        model: Model name (default: qwen3.5-plus)
        base_url: API base URL

    Returns:
        Configured LLM instance
    """
    return LLM(
        model=model,
        api_key=os.getenv("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN")),
        base_url=base_url,
        provider="anthropic",
    )


# Default LLM instance
primary_llm = get_llm()
