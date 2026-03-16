"""
Centralized Discord channel configuration.

Each flow publishes to a dedicated channel. Override via environment variables.
Channels:
    - weekly_report:  Weekly macro sentiment summaries
    - ticker_report:  Per-ticker GCCP deep-dive reports (report_loop / deepdive)
    - default:        Fallback when no specific channel is configured
"""

import os

# Channel registry: flow_name → env var name
# Values are resolved lazily from env at call time so dotenv can load first.
_CHANNEL_ENV_MAP: dict[str, str] = {
    "weekly_report": "DISCORD_CHANNEL_WEEKLY",
    "ticker_report": "DISCORD_CHANNEL_TICKER",
    "default": "DISCORD_CHANNEL_DEFAULT",
}


def get_discord_channel(flow_name: str) -> str:
    """Get the Discord channel ID for a given flow.

    Resolves from environment variables at call time (not import time)
    so that dotenv loading order doesn't matter.

    Falls back to 'default' if the specific flow channel is not set.
    Raises ValueError if no channel is configured at all.
    """
    env_var = _CHANNEL_ENV_MAP.get(flow_name)
    channel_id = os.getenv(env_var, "") if env_var else ""

    # Fallback to default
    if not channel_id:
        default_var = _CHANNEL_ENV_MAP["default"]
        channel_id = os.getenv(default_var, "")

    if not channel_id:
        configured = {
            name: os.getenv(var, "")
            for name, var in _CHANNEL_ENV_MAP.items()
            if os.getenv(var, "")
        }
        raise ValueError(
            f"No Discord channel configured for '{flow_name}'. "
            f"Set {env_var or flow_name.upper()} in .env. "
            f"Currently configured: {configured or 'none'}"
        )
    return channel_id
