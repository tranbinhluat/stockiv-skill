import os
import requests
from crewai.tools import tool


import time


@tool("send_discord_message")
def send_discord_message(channel_id: str, content: str, file_path: str = None) -> str:
    """
    Sends a message to a Discord channel using the bot token.
    Automatically handles splitting the message if it exceeds Discord's 2000 character limit.
    Can also attach a file if `file_path` is provided.

    Args:
        channel_id (str): The ID of the Discord channel to send the message to.
        content (str): The markdown content to send to the channel.
        file_path (str, optional): The absolute path to a file to attach to the last message chunk.
    """
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        return "Error: DISCORD_TOKEN environment variable not set."

    headers = {
        "Authorization": f"Bot {discord_token}",
    }
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    chunk_size = 1900
    chunks = []
    current_chunk = ""

    # Split by newline to preserve line breaks
    lines = content.split("\n")

    for line in lines:
        # Edge case: A single line is longer than the chunk size
        if len(line) > chunk_size:
            # If we have accumulated text, save it as a chunk first
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # Force-split the massive line by characters
            for i in range(0, len(line), chunk_size):
                chunks.append(line[i : i + chunk_size])
            continue

        # Normal case: check if adding this line exceeds the limit
        # +1 accounts for the newline character we will add
        if len(current_chunk) + len(line) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = line  # Start new chunk with the current line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line

    # Catch any remaining text
    if current_chunk:
        chunks.append(current_chunk)

    # --- API Sending Logic ---
    success_count = 0
    errors = []

    for idx, chunk in enumerate(chunks):
        payload = {"content": chunk}

        # Only attach the file to the last chunk, or if there's only one chunk
        is_last_chunk = idx == len(chunks) - 1

        try:
            if is_last_chunk and file_path and os.path.exists(file_path):
                # Send multipart form-data
                with open(file_path, "rb") as f:
                    file_name = os.path.basename(file_path)
                    files = {
                        "payload_json": (
                            None,
                            __import__("json").dumps(payload),
                            "application/json",
                        ),
                        "file": (
                            file_name,
                            f,
                            "application/pdf"
                            if file_path.endswith(".pdf")
                            else "application/octet-stream",
                        ),
                    }
                    response = requests.post(url, headers=headers, files=files)
            else:
                # Send JSON normally, ensure Content-Type is set for this single request
                json_headers = {**headers, "Content-Type": "application/json"}
                response = requests.post(url, headers=json_headers, json=payload)

            response.raise_for_status()
            success_count += 1

            # Simple rate limit backoff
            if len(chunks) > 1 and idx < len(chunks) - 1:
                time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            err_text = (
                response.text
                if "response" in locals() and hasattr(response, "text")
                else "None"
            )
            errors.append(
                f"Failed to send chunk {idx + 1}/{len(chunks)}: {str(e)} - Response: {err_text}"
            )

    if errors:
        return f"Partial failure. Sent {success_count} chunks, but encountered errors: {'; '.join(errors)}"

    return f"Successfully sent message to Discord channel {channel_id} in {len(chunks)} chunk(s)."
