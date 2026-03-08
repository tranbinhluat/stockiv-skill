import os
from crewai import Agent, Task, Crew
from crewai.mcp import MCPServerStdio
from dotenv import load_dotenv

from stockiv.agents.base import primary_llm

load_dotenv()

# Verify token is loaded
discord_token = os.getenv("DISCORD_TOKEN")
if not discord_token:
    raise ValueError("DISCORD_TOKEN must be set in .env file")

print(f"Token length: {len(discord_token)}")

# Use npx to run discord-mcp dynamically without installing locally
discord_mcp_server = MCPServerStdio(
    command="npx",
    args=["-y", "discord-mcp"],
    env={
        "DISCORD_BOT_TOKEN": f"Bot {discord_token}",
        "PATH": os.environ.get("PATH", ""),
    },
    # Optional: cache tools list for faster subsequent accesses
    cache_tools_list=False,
)

discord_agent = Agent(
    role="Discord Community Manager",
    goal="Interact with Discord via MCP tools to read messages, manage channels, etc.",
    backstory="You are a highly efficient assistant equipped with advanced network capabilities across Discord.",
    llm=primary_llm,
    mcps=[discord_mcp_server],
    verbose=True,
    # tracing=True, # Optional: if you want telemetry on app.crew.ai
)

# A simple task asking the agent to read recent messages and send a greeting
test_task = Task(
    description="""
    Use your Discord MCP tools to:
    1. Read the latest messages in the Server ID: 1377362666762539058 with discord channel ID: 1477341143766143128
    2. Then, send a very short message to the same channel saying: "Hello from CrewAI via the MCP integration!"

    IMPORTANT INSTRUCTION FOR SENDING MESSAGE:
    When calling the send message tool, ONLY provide `channelId` and `content`. DO NOT pass the `files`, `tts`, or `replyTo` arguments at all. Passing them as empty strings will cause validation errors.
    """,
    expected_output="A summary text detailing what messages the bot saw, and confirmation that it sent the greeting.",
    agent=discord_agent,
)

crew = Crew(
    agents=[discord_agent],
    tasks=[test_task],
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n--- Final Result ---")
    print(result.raw)
