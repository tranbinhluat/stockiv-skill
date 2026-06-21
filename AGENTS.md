## Harness: stock-analyst

**Objective:** Orchestrate the weekly Vietnam macro market sentiment report and execute related stock analysis tasks.

**Plugin:** `.agents/plugins/stockiv-plugin/` — see `references/skill-routing.md` for full trigger patterns and skill routing.

| Trigger | Skill | Flow Type | Notes |
|---|---|---|---|
| `/weekly`, "báo cáo tuần", "weekly report", "macro weekly", "thị trường tuần này" | `weekly-flow` | Orchestrator | Macro pipeline; human review gate default ON |
| `/deepdive`, `/deepdive <TICKER>`, "phân tích sâu", "deep dive", "analyze stock" | `deepdive-flow` | Orchestrator | Full GCCP; 7-step pipeline |
| `/compare TICKER1 TICKER2`, "compare ... vs ...", "which is better" | `compare-flow` | Orchestrator | Side-by-side GCCP; gatekeeper runs once |
| `/collect <TICKER>`, "fetch data for" | `collect-data` | Atomic | Data freshness check first |
| `/sentiment [TICKER]`, "market mood", "macro outlook" | `analyze-sentiment` | Atomic | Standalone or upstream of deepdive |
| `/fundamentals <TICKER>`, "is this a good company?" | `analyze-fundamentals` | Atomic | Requires collect + sentiment first |
| `/valuation <TICKER>`, "is it cheap?", "target price" | `analyze-valuation` | Atomic | Requires fundamentals first |
| `/report [TICKER]`, "export report", "generate PDF" | `draft-report` | Atomic | Requires all analysis files |
| `/publish`, "send to Discord" | `publish-discord` | Atomic | Gatekeeper APPROVED required |
