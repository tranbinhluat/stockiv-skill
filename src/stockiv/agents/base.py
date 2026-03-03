"""
Base LLM Configuration for StockIV

All agents use this shared LLM configuration to avoid repetition.
"""

import os
from crewai import LLM


# Default model configuration
DEFAULT_MODEL = "zhipuai/glm-4.7"
DEFAULT_BASE_URL = "https://api.z.ai/api/coding/paas/v4/"


def get_llm(model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL) -> LLM:
    """
    Get a configured LLM instance.

    Args:
        model: Model name (default: zhipuai/glm-4.7)
        base_url: API base URL (default: https://api.z.ai/api/coding/paas/v4/)

    Returns:
        Configured LLM instance
    """
    return LLM(
        model=model,
        api_key=os.getenv("ZHIPUAI_API_KEY"),
        base_url=base_url,
    )


# Default LLM instance
glm_llm = get_llm()
