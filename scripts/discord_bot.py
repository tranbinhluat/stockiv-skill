#!/usr/bin/env python3
"""
Standalone Discord bot for handling approval slash commands.
Run with: uv run python scripts/discord_bot.py
"""

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Find the root directory (where .env and data/ are located)
ROOT = Path(__file__).parent.parent.absolute()
load_dotenv(ROOT / ".env")

# Try to use centralized paths from the package
import sys

sys.path.append(str(ROOT / "src"))
try:
    from stockiv.config.paths import DATA_DIR

    DB_PATH = DATA_DIR / "stockiv.db"
except ImportError:
    DB_PATH = ROOT / "data" / "stockiv.db"

# Configure logging
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "discord_bot.log"),
    ],
)
logger = logging.getLogger("discord_bot")


class ApprovalBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # We don't need message content for slash commands, but we need it if we want to use prefix commands
        # intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands to the global tree
        # Note: Global sync can take up to an hour. For testing, you can sync to a specific guild.
        await self.tree.sync()
        logger.info("Slash commands synced globally.")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Database path: {DB_PATH}")
        logger.info("------")


bot = ApprovalBot()


@bot.tree.command(name="approve", description="Approve a report request")
@app_commands.describe(request_id="The ID of the approval request")
async def approve(interaction: discord.Interaction, request_id: int):
    """Approve a report request by ID."""
    logger.info(f"Received /approve for ID: {request_id} from {interaction.user}")

    try:
        if not DB_PATH.exists():
            await interaction.response.send_message(
                f"❌ Database not found at `{DB_PATH}`.", ephemeral=True
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if ID exists and its current status
        cursor.execute(
            "SELECT ticker, status FROM approvals WHERE id = ?", (request_id,)
        )
        row = cursor.fetchone()

        if not row:
            await interaction.response.send_message(
                f"❌ Request ID `{request_id}` not found.", ephemeral=True
            )
            conn.close()
            return

        ticker, status = row
        if status != "PENDING":
            await interaction.response.send_message(
                f"⚠️ Request `{request_id}` ({ticker}) is already `{status}`.",
                ephemeral=True,
            )
            conn.close()
            return

        # Update status to APPROVED
        # We also update the timestamp to reflect when the approval happened
        cursor.execute(
            "UPDATE approvals SET status = 'APPROVED', timestamp = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id),
        )
        conn.commit()
        conn.close()

        logger.info(f"Successfully approved request {request_id} ({ticker})")
        await interaction.response.send_message(
            f"✅ Approved request `{request_id}` for **{ticker}**."
        )

    except sqlite3.OperationalError as e:
        logger.error(f"Database lock or operational error: {e}")
        await interaction.response.send_message(
            f"❌ Database error (possibly locked): {e}", ephemeral=True
        )
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        await interaction.response.send_message(
            f"❌ Database error: {e}", ephemeral=True
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await interaction.response.send_message(
            f"❌ An unexpected error occurred: {str(e)}", ephemeral=True
        )


@bot.tree.command(name="reject", description="Reject a report request with feedback")
@app_commands.describe(
    request_id="The ID of the approval request",
    feedback="Reason for rejection or feedback for the agent",
)
async def reject(interaction: discord.Interaction, request_id: int, feedback: str):
    """Reject a report request by ID with feedback."""
    logger.info(
        f"Received /reject for ID: {request_id} from {interaction.user}. Feedback: {feedback}"
    )

    try:
        if not DB_PATH.exists():
            await interaction.response.send_message(
                f"❌ Database not found at `{DB_PATH}`.", ephemeral=True
            )
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if ID exists and its current status
        cursor.execute(
            "SELECT ticker, status FROM approvals WHERE id = ?", (request_id,)
        )
        row = cursor.fetchone()

        if not row:
            await interaction.response.send_message(
                f"❌ Request ID `{request_id}` not found.", ephemeral=True
            )
            conn.close()
            return

        ticker, status = row
        if status != "PENDING":
            await interaction.response.send_message(
                f"⚠️ Request `{request_id}` ({ticker}) is already `{status}`.",
                ephemeral=True,
            )
            conn.close()
            return

        # Update status to REJECTED and populate feedback
        cursor.execute(
            "UPDATE approvals SET status = 'REJECTED', feedback = ?, timestamp = ? WHERE id = ?",
            (feedback, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id),
        )
        conn.commit()
        conn.close()

        logger.info(f"Successfully rejected request {request_id} ({ticker})")
        await interaction.response.send_message(
            f"❌ Rejected request `{request_id}` for **{ticker}**. Feedback: {feedback}"
        )

    except sqlite3.OperationalError as e:
        logger.error(f"Database lock or operational error: {e}")
        await interaction.response.send_message(
            f"❌ Database error (possibly locked): {e}", ephemeral=True
        )
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        await interaction.response.send_message(
            f"❌ Database error: {e}", ephemeral=True
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await interaction.response.send_message(
            f"❌ An unexpected error occurred: {str(e)}", ephemeral=True
        )


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error(
            "DISCORD_TOKEN not found in environment variables. Please set it in .env."
        )
        exit(1)

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid DISCORD_TOKEN provided.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
