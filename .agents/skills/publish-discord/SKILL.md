---
name: publish-discord
description: Publish a GCCP report or weekly analysis to Discord. Use this skill when the user types /publish, asks to send a report to Discord, or when called internally after draft-report and gatekeeper APPROVED in a /deepdive or /weekly flow.
---

# publish-discord

Sends a short, catchy summary post to the Discord channel and attaches the full PDF report.

## Guard: Never Publish Without Approval

**Only run this skill when gatekeeper has returned APPROVED (deepdive) or the user has confirmed at the review gate (weekly).**

If the user asks to publish without approval, respond:
> "The report must be validated before publishing. Complete the gatekeeper check (deepdive) or confirm at the review gate (weekly) first."

## What This Skill Does

Compose a short, catchy summary post first, then call the CLI to send it with the PDF attached. The channel receives one clean post — not a wall of chunked markdown.

## Step 1 — Compose the Summary Post

### Ticker Report (deepdive)

```
📊 **{TICKER} — {MUA NGAY / CHỜ / TRÁNH}**

_{Hook line from the report — one sentence investment thesis}_

📌 **Điểm nổi bật:**
• Giá mục tiêu: **{value} VND** | Giá hiện tại: {value} VND ({upside}%)
• {1-line qualitative verdict — Lynch category + moat}
• {1-line key risk}

📎 Báo cáo đầy đủ đính kèm ↑
```

### Weekly Market Report

```
📈 **Thị trường Tuần {WW}/{YEAR} — {Tăng giá / Trung lập / Giảm giá}**

_{Key regime driver in one sentence}_

🔍 **3 điểm theo dõi tuần tới:**
1. {catalyst 1}
2. {catalyst 2}
3. {catalyst 3}

📎 Báo cáo đầy đủ đính kèm ↑
```

## Step 2 — Publish via CLI

Pass the composed summary as `--message` and attach the PDF:

### Ticker Report
```
uv run stockiv-publish \
  --file reports/ticker/{TICKER}_GCCP_report.pdf \
  --message "{composed summary}" \
  --channel ticker
```

### Weekly Market Report
```
uv run stockiv-publish \
  --file data/reports/market/{YEAR}_W{WW}_weekly_report.pdf \
  --message "{composed summary}" \
  --channel weekly
```

The CLI sends the `--message` text as the Discord post body and attaches the PDF file.

## Environment Variables Required

- `DISCORD_TOKEN` — bot token
- `DISCORD_CHANNEL_TICKER` — channel ID for ticker reports
- `DISCORD_CHANNEL_WEEKLY` — channel ID for weekly reports
- `DISCORD_CHANNEL_DEFAULT` — fallback channel

## Output to User

```
✅ Published to Discord:
Channel: {channel_type}
Summary post sent + PDF attached: {filename}
```
