# Brainstorm — Phase 1: Free Ideation

**Date:** 2026-06-21  
**Topic:** Reorganizing stockiv-skill into `stockiv-plugin` — plugin structure, subagent architecture, and multi-flow support  
**Facilitator:** Remy (Producer)

---

> **Ground rules:** Each agent pitches 2–3 raw ideas from their own perspective.  
> Pros, cons, and effort estimate (S = half-day, M = 2–3 days, L = week+) required for every idea.  
> No debating yet — that's Phase 2.

---

## 🎨 Kira — Product Designer / Analyst UX

*"I think about the stock analyst sitting down on a Monday morning. What does she actually want to do?"*

---

### K1 · Screener Flow (`/screen [TICKER1 TICKER2 ...]`)

**Pitch:** The analyst's real first question is never "analyze FPT in full depth" — it's "which of these 8 stocks on my list is worth a deepdive today?" A screener flow runs a lightweight GCCP scoring pass (collect data + valuation only, skip heavy forensic Part III) on a list of tickers and outputs a ranked leaderboard with BUY/WAIT/AVOID verdicts and target prices side by side.

**What it needs:** New `screener-flow` SKILL.md. Reuses `collect-data` and `analyze-valuation` as building blocks. Skip `analyze-fundamentals` Part III forensics for speed — produce a "quick score" column. Output: `reports/screener/{date}_screen_results.md`.

**Pros:** Highest-value gap in the current system. Analyst currently has to manually trigger `/deepdive` per ticker one by one. This is the daily-use case.

**Cons:** Context window explosion with 10 tickers. Need to define what "GCCP quick score" means without full forensics — risk of false positives. Parallel subagent complexity (N concurrent collect-data calls).

**Effort:** L

---

### K2 · Compare Flow (`/compare TICKER1 TICKER2`)

**Pitch:** `collect-data` already says *"identify 1-2 top domestic competitors in same industry and pre-load ratio summaries for downstream peer comparisons."* That peer data is already written to `data/processed/synthesizer/{TICKER}/`. The analyst is already getting the data — she just can't see a clean side-by-side view. A compare-flow makes it explicit: full GCCP run on both tickers, single output table, side-by-side verdicts.

**What it needs:** New `compare-flow` SKILL.md. Runs `deepdive-flow` logic for each of two tickers. Output: combined markdown comparison report.

**Pros:** Medium effort. Genuinely reuses all existing atomic skills. High analyst value for peer analysis decisions. The hard part (data collection with peers) is already done.

**Cons:** Double context window usage. Output format needs a design decision — one combined PDF, or two? The gatekeeper runs twice?

**Effort:** M

---

### K3 · Watchlist Weekly Digest (`/watchlist`)

**Pitch:** The analyst has 5 stocks she's tracking. Every Monday she wants: "What changed on my watchlist this week? Did any thesis break? Did any price drop into buy range?" Not a full deepdive — just a freshness check + sentiment delta per stock.

**What it needs:** A `data/watchlist.json` state file (tickers + last analysis date). New `watchlist-flow` SKILL.md: for each tracked ticker, runs `analyze-sentiment` (ticker mode only, skipping macro since it's already cached) and diffs against the prior `{YEAR}_W{WW}_sentiment.md`. Flags tickers where sentiment materially changed.

**Pros:** Tight integration with existing sentiment cadence. Completes the loop between `weekly-flow` (macro) and `deepdive-flow` (individual stock). Genuinely valuable recurring use case.

**Cons:** Requires new state management. The diff logic ("did sentiment materially change?") needs clear criteria. Adds a new data artifact class (`watchlist.json`) to maintain.

**Effort:** M

---

## ⚙️ Nova — Flow Engineer / Skill Architect

*"I think about the simplest structure that actually works without creating a maintenance headache."*

---

### N1 · Plugin Packaging — Migrate All Skills to `stockiv-plugin`

**Pitch:** The nine flat skills in `.agents/skills/` violate the copilot plugin format that `harness-plugin` already demonstrates. The fix is a pure structural migration — no content changes. Create `.agents/plugins/stockiv-plugin/plugin.json`, then move each `SKILL.md` from `.agents/skills/{name}/SKILL.md` to `.agents/plugins/stockiv-plugin/skills/{name}/SKILL.md`. Update AGENTS.md to point to the new paths.

**What it needs:** `plugin.json` (3 lines), directory moves, one AGENTS.md update.

**Pros:** Zero content risk — not a single SKILL.md line changes. Follows the established `harness-plugin` convention. Makes the project structure discoverable and consistent. Future skills land in the right place from day one.

**Cons:** All path references in AGENTS.md change (`.agents/skills/collect-data/` → `.agents/plugins/stockiv-plugin/skills/collect-data/`). Need to verify whether any CLI tools or scripts reference `.agents/skills/` paths directly.

**Effort:** S

---

### N2 · Formalize Atomic vs. Orchestrator Separation

**Pitch:** Right now `deepdive-flow` says *"Run inline (refer `analyze-sentiment` skill)"* — it absorbs atomic skill content rather than delegating to it. This is the root cause of monolithism. Formalize the split with a naming convention: **atomic skills** (`collect-data`, `analyze-sentiment`, `analyze-fundamentals`, `analyze-valuation`, `draft-report`, `publish-discord`) live in `skills/atomic/`. **Orchestrator flows** (`deepdive-flow`, `weekly-flow`) live in `skills/flows/`. Rewrite flow SKILL.md files to say "invoke atomic skill X" rather than duplicating its steps inline.

**What it needs:** Directory reorganization within the plugin. Rewrite of `deepdive-flow/SKILL.md` and `weekly-flow/SKILL.md` to use delegation language instead of "run inline."

**Pros:** Makes composability explicit. Sprint 2 flows (screener, compare) can delegate to atomic skills without copy-paste. Removes the "inline vs. dedicated" ambiguity in current flow SKILL.md files.

**Cons:** "Invoke skill X" semantics need to be confirmed as supported by the Antigravity CLI. If not, we're writing aspirational SKILL.md files that don't actually work. Risk: shipping an architecture that looks clean but doesn't execute.

**Effort:** S (structure) + M (flow SKILL.md rewrites)

---

### N3 · Shared References Index in the Plugin

**Pitch:** Six knowledge files in `src/stockiv/knowledge/` are referenced with hard paths in multiple SKILL.md files: `framework.md` (Parts II, III, IV spread across three different skills), `criteria.md` (in `analyze-valuation`), `industry_guides.md` and `financial_reading_guide.md` (in `analyze-fundamentals`). This duplication means every skill author has to know which part of `framework.md` is "theirs" — there's no map. Create `.agents/plugins/stockiv-plugin/references/knowledge-map.md` as a single index: which skill reads which sections of which knowledge files.

**What it needs:** A single new markdown file. The knowledge files themselves stay in `src/stockiv/knowledge/` — we're not moving them.

**Pros:** Zero path changes to the actual knowledge files. When a new skill is added, the author checks `knowledge-map.md` instead of hunting across six source files. Eliminates the "which part of framework.md is mine?" problem.

**Cons:** One extra indirection. Doesn't eliminate the per-skill path references — it supplements them. Someone has to keep knowledge-map.md in sync.

**Effort:** S

---

## 🔁 Sage — Backend / Pipeline Engineer

*"I look at the pipeline and see sequential bottlenecks that cost the analyst 3–4 unnecessary wait cycles per deepdive."*

---

### S1 · Parallelize fundamentals + sentiment in `deepdive-flow`

**Pitch:** The current deepdive-flow pipeline is fully sequential: `collect → sentiment → fundamentals → valuation`. But macro sentiment (`{YEAR}_W{WW}_macro_sentiment.md`) is already cached by `weekly-flow` most of the time. That cache means we can start fundamentals quantitative work (Part III — ROE/ROA/margins/forensics from `financial_summary.md`) immediately after collect, in parallel with ticker-sentiment analysis. Only Part II qualitative analysis (Lynch cross-check, tailwinds/headwinds) actually needs the `{TICKER}_sentiment.md` output. 

Proposed deepdive sequence:
```
Step 1: collect-data
Step 2: [ticker-sentiment ‖ quant-fundamentals(Part III)]  ← parallel
Step 3: qual-fundamentals(Part II) ← joins both results
Step 4: analyze-valuation
```

**What it needs:** Split `analyze-fundamentals` SKILL.md into two phases. Rewrite `deepdive-flow` Step 2 to spawn two subagents when macro is cached.

**Pros:** Eliminates one full sequential wait from the deepdive pipeline. The quantitative side (ROE, FCF, forensics) is pure number-crunching with no dependency on sentiment. Real speedup.

**Cons:** Requires restructuring `analyze-fundamentals`' dependency contract — it currently declares `{TICKER}_sentiment.md` as a top-level dependency. That's a content change to an atomic skill. This is not just a flow rewrite.

**Effort:** M

---

### S2 · Dedicated Agent Definitions for Market Scout, Stock Analyst, Gatekeeper

**Pitch:** Three agents are referenced by name across multiple SKILL.md files: `Stock Analyst` (deepdive-flow, weekly-flow), `Gatekeeper Reviewer` (deepdive-flow), `Market Scout` (collect-data, weekly-flow). The README mentions they live at `.agents/agents/` as `.md` files — but the plugin format expects `agent.json` in `.agents/plugins/{name}/agents/{agent-name}/`. Formally defining each agent in the plugin gives them explicit scope boundaries: Market Scout gets a search budget (max 5 queries, one focused topic), Gatekeeper Reviewer gets `disable-model-invocation: true`, etc.

**What it needs:** `stockiv-plugin/agents/stock-analyst/agent.json`, `gatekeeper-reviewer/agent.json`, `market-scout/agent.json`. Reference `harness-plugin` format.

**Pros:** Clean agent boundaries. Each agent's allowed scope is machine-readable. Prevents Market Scout from over-searching (currently undefined budget). Aligns with copilot plugin conventions.

**Cons:** More files to maintain. The current system works without formal `agent.json` — so this is improvement, not fix.

**Effort:** M

---

### S3 · Multi-Ticker Parallel Pipeline (foundation for Screener)

**Pitch:** For a screener-flow to work efficiently across 8–10 tickers, we need a fan-out pattern: spawn N parallel subagents via `invoke_subagent`, each running collect + valuation for one ticker independently. Results flow back to a coordinator that produces the ranking table. This isn't screener-flow itself — it's the parallel execution substrate that screener-flow (and eventually compare-flow) would use.

**What it needs:** Design a "parallel batch" invocation pattern in SKILL.md format. Document how N subagents share results through files (each writes to `data/processed/synthesizer/{TICKER}/`). Verify Antigravity CLI's `invoke_subagent` supports concurrent spawning.

**Pros:** Once the pattern exists, screener-flow becomes straightforward. Also unlocks watchlist-flow.

**Cons:** Context window grows with N. API cost multiplies. Error handling — if 1 of 8 ticker subagents fails, does the whole screener fail or produce partial results? Not trivial to design.

**Effort:** L

---

## 🛠 Milo — Developer Experience

*"I think about the poor developer staring at nine flat SKILL.md files with no idea where to start."*

---

### M1 · Skill Template in the Plugin

**Pitch:** Adding a new skill currently requires copying an existing SKILL.md and adapting it. This produces inconsistency: some skills have `## Freshness Check` (collect-data, analyze-sentiment), some don't. Some have `## Output to User` (all atomic skills), some don't. The `## Depends On` format varies. Create `.agents/plugins/stockiv-plugin/skills/_template/SKILL.md` with all standard sections scaffolded with `{PLACEHOLDER}` comments. skill-creator already follows this mental model — formalize it.

**Pros:** Consistency across all current and future skills. Zero friction for new skill authors. The template itself documents the expected sections.

**Cons:** Requires discipline to keep the template in sync with conventions as skills evolve.

**Effort:** S

---

### M2 · Routing Table in AGENTS.md

**Pitch:** Current AGENTS.md trigger block is unstructured prose: *"Use `weekly-flow` skill user asks weekly reports, macro sentiment updates, types `/weekly`. Use `deepdive-flow` skill user types `/deepdive`..."* Hard to scan, hard to extend, and fragile for new trigger patterns. Replace with a structured routing table:

```markdown
| Trigger | Skill | Notes |
|---|---|---|
| `/weekly`, "báo cáo tuần" | `weekly-flow` | Macro pipeline |
| `/deepdive <TICKER>`, "phân tích sâu" | `deepdive-flow` | Full GCCP |
| `/collect <TICKER>` | `collect-data` | Data refresh |
| `/sentiment [TICKER]` | `analyze-sentiment` | Standalone |
...
```

Add Sprint 2 rows with `[planned]` status — the table doubles as a roadmap.

**Pros:** Extremely scannable. Adding a new trigger = one table row. Claude may parse explicit patterns more reliably than prose for skill dispatching.

**Cons:** Unknown whether table format performs better or worse than prose for the model's routing decisions. Needs testing.

**Effort:** S

---

### M3 · `CONTRIBUTING.md` for Skill Authors

**Pitch:** No guide exists for how to add a new skill correctly. As screener-flow, compare-flow, and watchlist-flow get added in Sprint 2, each developer will invent their own data path conventions unless there's a reference doc. Write `docs/contributing/skill-guide.md`: plugin directory structure, required SKILL.md sections, data path conventions (the `data/processed/synthesizer/{TICKER}/` pattern), naming conventions, and how to register in AGENTS.md.

**Pros:** Scales the team. Prevents conflicting data path inventions in Sprint 2. Essential if any external contributors join.

**Cons:** Pure overhead if it's a single-developer project.

**Effort:** S

---

## 🔍 Ivy — QA / Risk

*"I think about what breaks the moment we start moving files around."*

---

### I1 · Blue/Green Migration — Keep Flat Skills Running During Migration

**Pitch:** The production system today uses `.agents/skills/`. AGENTS.md points there. If we migrate all nine skills to `stockiv-plugin` in one PR and there's any misconfiguration (wrong path in AGENTS.md, wrong plugin.json format), the entire system goes dark. Instead: copy (not move) skills to the plugin structure, validate end-to-end with one skill (`collect-data` is safest — simplest dependency chain), then migrate one by one. Only remove `.agents/skills/` once all skills are validated in the plugin.

**Pros:** Zero downtime during migration. If one migrated skill breaks, the others still work from the flat structure.

**Cons:** Temporary duplication. Developer must know which copy is canonical. Risk: someone edits the flat copy thinking it's current.

**Effort:** S (process discipline, not engineering)

---

### I2 · Hardcoded Path Audit — Document Before Any Restructure

**Pitch:** Before touching a single file, document every hardcoded path that skills pass to each other:

| Written by | Path | Read by |
|---|---|---|
| `collect-data` | `data/raw/context/{TICKER}_ticker_context.md` | `analyze-sentiment` |
| `collect-data` | `data/raw/context/market_context.md` | `analyze-sentiment`, `weekly-flow` |
| `collect-data` | `data/processed/synthesizer/{TICKER}/financial_summary.md` | `analyze-fundamentals`, `analyze-valuation` |
| `analyze-sentiment` | `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md` | `analyze-fundamentals`, `deepdive-flow` |
| `analyze-sentiment` | `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md` | `analyze-fundamentals`, `draft-report` |
| `analyze-fundamentals` | `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` | `analyze-valuation`, `draft-report` |
| `analyze-valuation` | `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md` | `draft-report` |
| `draft-report` | `reports/ticker/{TICKER}_GCCP_report.pdf` | `publish-discord` |
| `weekly-flow` | `data/reports/market/{YEAR}_W{WW}_weekly_report.pdf` | `publish-discord` |

**These paths live in `data/` and `reports/` — they don't change with plugin restructure.** Documenting this prevents panic.

**Pros:** Prevents scope confusion. Confirms the migration is `.agents/` surgery only — not a data pipeline change.

**Cons:** None. It's just documentation.

**Effort:** S

---

### I3 · Gatekeeper + Market Scout Agent Location Risk

**Pitch:** `deepdive-flow` references `Gatekeeper Reviewer` as a subagent. `weekly-flow` says `Market Scout` lives at `../.github/agents/market-scout.agents.md`. The README shows agent files at `.agents/agents/`. These paths are inconsistent — `deepdive-flow` references `.github/agents/`, not `.agents/agents/`. Before migrating anything, we need to: (1) verify where these three agent files actually live, (2) confirm which path format is correct, (3) ensure any migration moves the agent definitions together with the skills that reference them.

**Risk:** Migrating `deepdive-flow` to the plugin without migrating `Gatekeeper Reviewer`'s definition = silent breakage that only surfaces during a full `/deepdive` run, past Step 5.

**Pros:** Prevents a non-obvious breakage that would only appear during integration testing.

**Cons:** None.

**Effort:** S

---

*Phase 2 discussion begins in `02-discussion.md`.*
