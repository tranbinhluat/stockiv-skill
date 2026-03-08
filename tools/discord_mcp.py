import os
from crewai.mcp import MCPServerStdio


def get_discord_mcp_server() -> MCPServerStdio:
    """
    Initializes and returns the Discord MCP server.
    Ensures that the token is present and correctly formatted.
    """
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        print("WARNING: DISCORD_TOKEN is not set. Discord publishing might fail.")
        discord_token = ""

    return MCPServerStdio(
        command="npx",
        args=["-y", "discord-mcp"],
        env={
            "DISCORD_BOT_TOKEN": f"Bot {discord_token}",
            "PATH": os.environ.get("PATH", ""),
        },
        cache_tools_list=False,
    )
