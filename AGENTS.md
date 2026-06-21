## Harness: stock-analyst

**Objective:** Orchestrate the weekly Vietnam macro market sentiment report and execute related stock analysis tasks.

**Trigger:** Use the `weekly-flow` skill when the user asks for weekly reports, macro sentiment updates, or types `/weekly`. Use the `deepdive-flow` skill when the user types `/deepdive` or asks for full GCCP analysis of a specific stock ticker. Direct simple questions can be answered directly. For deep analysis, you may trigger other skills or subagents within the plugin.

