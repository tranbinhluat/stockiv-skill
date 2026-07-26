---
description: Analyze macro market sentiment and/or ticker-specific sentiment from collected news context
agent: stock-analyst
---

Use the analyze-sentiment skill for: $ARGUMENTS

If no ticker was provided, run macro-only sentiment. If a ticker is given, also produce ticker sentiment.

Requires collect-data output to exist (`market_context.md`, `{TICKER}_ticker_context.md`). If missing, tell the user to run `/collect` first.
