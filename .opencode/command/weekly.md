---
description: Run the weekly Vietnam macro market sentiment report and publish to Discord (human review gate ON by default)
agent: stock-analyst
---

Use the weekly-flow skill to run the weekly macro market sentiment pipeline: collect macro data → analyze sentiment → draft weekly report → human review gate → publish to Discord.

Honor the human review gate (Step 3.5) unless the user explicitly said "no review", "skip review", or "auto publish".

Additional user input: $ARGUMENTS
