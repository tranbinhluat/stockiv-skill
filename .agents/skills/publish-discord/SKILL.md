---
name: publish-discord
description: Publish a GCCP report or weekly analysis to Discord. Use this skill when the user types /publish, asks to send a report to Discord, or when called internally after draft-report and gatekeeper APPROVED in a /deepdive or /weekly flow.
---

# publish-discord

Sends a completed report to the correct Discord channel.

## Guard: Never Publish Without Approval

**Only run this skill when gatekeeper has returned APPROVED.**

If the user asks to publish without gatekeeper approval, respond:
> "The gatekeeper must validate this report before it can be published. Run the gatekeeper validation first."

## What This Skill Does

Calls the publish CLI tool which:
1. Reads the report markdown file
2. Chunks the content into ≤ 1,900-character segments (Discord limit)
3. Sends each chunk to the correct channel with a 0.5s delay between chunks
4. Optionally attaches the PDF on the last chunk

## Usage

### Ticker Report (deep dive)
```
uv run stockiv-publish --file reports/ticker/{TICKER}_GCCP_report.md --channel ticker --attach-pdf
```
Routes to `DISCORD_CHANNEL_TICKER` env var.

### Weekly Market Report
```
uv run stockiv-publish --file reports/market/{YEAR}_W{WW}_weekly_report.md --channel weekly
```
Routes to `DISCORD_CHANNEL_WEEKLY` env var.

## Environment Variables Required

- `DISCORD_TOKEN` — bot token for the Discord bot
- `DISCORD_CHANNEL_TICKER` — channel ID for ticker reports
- `DISCORD_CHANNEL_WEEKLY` — channel ID for weekly market reports
- `DISCORD_CHANNEL_DEFAULT` — fallback channel

If any of these are missing, the CLI will report the error clearly. Do not attempt to infer channel IDs.

## Output to User

```
✅ Report published to Discord:
Channel: {channel_type} ({channel_id})
Chunks sent: {n}
PDF attached: {yes/no}
```

If an error occurs, the CLI will report which chunks failed and retry instructions.
