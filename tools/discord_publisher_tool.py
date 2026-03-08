import os
import requests
from crewai.tools import tool


@tool("send_discord_message")
def send_discord_message(channel_id: str, content: str) -> str:
    """
    Sends a message to a Discord channel using the bot token.
    Automatically handles splitting the message if it exceeds Discord's 2000 character limit.

    Args:
        channel_id (str): The ID of the Discord channel to send the message to.
        content (str): The markdown content to send to the channel.
    """
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        return "Error: DISCORD_TOKEN environment variable not set."

    headers = {
        "Authorization": f"Bot {discord_token}",
        "Content-Type": "application/json",
    }
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    # Discord limit is 2000 characters. We use smart chunking by lines/headers.
    chunk_size = 1900
    chunks = []
    current_chunk = []
    current_length = 0

    for line in content.split("\n"):
        # Force a break before major Markdown headings to keep topics grouped nicely
        is_heading = line.strip().startswith(("# ", "## ", "### "))

        # +1 for the newline character that will be added back when joined
        line_length = len(line) + 1

        # If adding this line exceeds the limit, OR it is a new heading, finalize the current chunk
        if current_chunk and (
            is_heading or (current_length + line_length > chunk_size)
        ):
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    success_count = 0
    errors = []

    for idx, chunk in enumerate(chunks):
        payload = {"content": chunk}
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            success_count += 1

            # Rate limit backoff (simple) if many chunks
            import time

            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            err_text = response.text if hasattr(response, "text") else "None"
            errors.append(
                f"Failed to send chunk {idx + 1}/{len(chunks)}: {str(e)} - Response: {err_text}"
            )

    if errors:
        return f"Partial failure. Sent {success_count} chunks, but encountered errors: {'; '.join(errors)}"

    return f"Successfully sent message to Discord channel {channel_id} in {len(chunks)} chunk(s)."
