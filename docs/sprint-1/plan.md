# Sprint 1 — Plugin Migration (Concept A: Conservative)

> **Sprint Goal:** Package 8 existing skills into `stockiv-plugin` format — zero SKILL.md content changes, clean plugin structure as foundation for Sprint 2.
> **Branch:** `feat/plugin-migration`
> **Estimated effort:** S–M · 3–5 days

---

## Context

This is the outcome of the brainstorm documented in `docs/brainstorm/`. Decision: **Concept A — Conservative Migration**.

**Rule: No SKILL.md content changes.** If you find yourself editing a SKILL.md's logic, stop and document it as a Sprint 2 item instead.

---

## Pre-Sprint Tasks (Ivy — run before any commits)

| # | Task | Est | Description |
|---|------|-----|-------------|
| P1 | Path Audit (I2) | 1h | Document all inter-skill file paths in `docs/sprint-1/path-audit.md`. Confirm `data/` paths are independent of `.agents/` paths. Table format: `Written By | Path | Read By`. |
| P2 | Agent Location Audit (I3) | 1h | Verify exact file paths for `gatekeeper-reviewer`, `stock-analyst`, `market-scout`. Confirm current paths, target plugin paths. Document in `docs/sprint-1/agent-audit.md`. |

---

## Prioritized Task List

| # | Task | Owner | Est | Description |
|---|------|-------|-----|-------------|
| 1 | Create `stockiv-plugin/plugin.json` | Nova | 30m | `{ "name": "stockiv-plugin", "description": "...", "version": "1.0.0" }` at `.agents/plugins/stockiv-plugin/plugin.json` |
| 2 | Blue/green: copy + validate `collect-data` | Nova + Ivy | 1h | Copy `.agents/skills/collect-data/` → `.agents/plugins/stockiv-plugin/skills/collect-data/`. Validate by running a test prompt. If pass, proceed to bulk migration. |
| 3 | Bulk migrate remaining 7 skills | Nova | 1h | Copy (not move) `analyze-sentiment`, `analyze-fundamentals`, `analyze-valuation`, `draft-report`, `publish-discord`, `deepdive-flow`, `weekly-flow` to plugin. **Do not move `skill-creator`.** |
| 4 | Migrate agent definitions | Nova | 45m | Copy `.github/agents/gatekeeper-reviewer.agent.md`, `stock-analyst.agent.md`, `market-scout.agent.md` → `.agents/plugins/stockiv-plugin/agents/`. Use `.md` format matching harness-plugin convention. |
| 5 | Create `references/skill-routing.md` | Milo | 1h | Machine-readable routing registry. All skills + trigger patterns. Include `[planned]` rows for Sprint 2 (compare-flow). See spec below. |
| 6 | Create `references/knowledge-map.md` | Sage | 1h | Dependency graph: "Skill X requires File Y before execution." Seed for Sprint 2 parallelism. See spec below. |
| 7 | Create `skills/_template/SKILL.md` | Milo | 30m | Scaffolded boilerplate with all standard sections and `{PLACEHOLDER}` comments. |
| 8 | Update `AGENTS.md` routing table | Milo | 30m | Point to plugin paths. Add structured routing table referencing `skill-routing.md`. |
| 9 | Write compare-flow design note | Remy | 30m | Document: output format, gatekeeper behavior, trigger pattern. Save to `docs/sprint-1/compare-flow-design.md`. No SKILL.md. |
| 10 | Archive flat `.agents/skills/` | Ivy | 30m | After all 8 skills validated in plugin: rename `.agents/skills/` → `.agents/skills-archived/`. Do NOT delete. |
| 11 | Write `docs/sprint-1/done.md` | Nova | 30m | Sprint done doc. |

---

## Work Schedule

### Phase 1: Pre-sprint Audits (P1 + P2)
- Run path audit, document all inter-skill file paths
- Run agent location audit, confirm exact paths
- Commit: `chore: pre-sprint path + agent audits`

### Phase 2: Plugin Foundation (Tasks 1–3)
- Create `plugin.json`
- Blue/green `collect-data` copy + validate
- Bulk migrate remaining 7 skills
- Commit: `feat: migrate 8 skills to stockiv-plugin`

### Phase 3: Agent Migration (Task 4)
- Copy agent `.md` files into plugin `agents/` folder
- Commit: `feat: migrate agent definitions to stockiv-plugin`

### Phase 4: Reference Files + AGENTS.md (Tasks 5–8)
- `skill-routing.md` (routing registry)
- `knowledge-map.md` (dependency graph)
- `_template/SKILL.md` (scaffold)
- AGENTS.md routing table update
- Commit: `feat: add skill-routing, knowledge-map, template; update AGENTS.md`

### Phase 5: Design Note + Done Doc + Archive (Tasks 9–11)
- compare-flow design note
- Archive `.agents/skills/`
- Write `done.md`
- Commit: `chore: compare-flow design note, archive flat skills, sprint done`

---

## File Specs

### `references/skill-routing.md`

```markdown
# Skill Registry — stockiv-plugin

## Registered Skills

### collect-data
- **Trigger:** `/collect <TICKER>`, `/collect --macro`
- **Type:** atomic
- **Inputs:** (none — generates data via CLI)
- **Outputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/raw/context/market_context.md`
- **Depends on:** (none — first in pipeline)

### analyze-sentiment
- **Trigger:** `/sentiment [TICKER]`, "market mood", "macro outlook"
- **Type:** atomic
- **Inputs:** `data/raw/context/{TICKER}_ticker_context.md`, `data/raw/context/market_context.md`
- **Outputs:** `data/processed/sentiment/ticker/{TICKER}_sentiment.md`, `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md`
- **Depends on:** collect-data

### analyze-fundamentals
- **Trigger:** `/fundamentals <TICKER>`, "is this a good company"
- **Type:** atomic
- **Inputs:** `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/processed/sentiment/ticker/{TICKER}_sentiment.md`
- **Outputs:** `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`
- **Depends on:** collect-data, analyze-sentiment

### analyze-valuation
- **Trigger:** `/valuation <TICKER>`, "is it cheap", "target price"
- **Type:** atomic
- **Inputs:** `data/processed/synthesizer/{TICKER}/financial_summary.md`, `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`
- **Outputs:** `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`
- **Depends on:** collect-data, analyze-fundamentals

### draft-report
- **Trigger:** `/report [TICKER]`
- **Type:** atomic
- **Inputs:** `{TICKER}_fundamentals.md`, `{TICKER}_valuation.md`, `{TICKER}_sentiment.md`
- **Outputs:** `reports/ticker/{TICKER}_GCCP_report.md`, `reports/ticker/{TICKER}_GCCP_report.pdf`
- **Depends on:** analyze-fundamentals, analyze-valuation, analyze-sentiment

### publish-discord
- **Trigger:** `/publish`, "send to Discord"
- **Type:** atomic
- **Inputs:** approved report file path
- **Outputs:** Discord message (channel: weekly or ticker)
- **Depends on:** draft-report (gatekeeper APPROVED)

### deepdive-flow
- **Trigger:** `/deepdive`, `/deepdive <TICKER>`, "phân tích sâu", "deep dive", "analyze stock"
- **Type:** orchestrator
- **Pipeline:** collect-data → analyze-sentiment → analyze-fundamentals → analyze-valuation → gatekeeper → draft-report → publish-discord
- **Depends on:** all atomic skills

### weekly-flow
- **Trigger:** `/weekly`, "weekly report", "báo cáo tuần", "macro weekly", "thị trường tuần này"
- **Type:** orchestrator
- **Pipeline:** collect-data (macro) → analyze-sentiment → draft-report → publish-discord
- **Depends on:** collect-data, analyze-sentiment, draft-report, publish-discord

## Planned Skills (Sprint 2+)

### compare-flow [planned — Sprint 2]
- **Trigger:** `/compare TICKER1 TICKER2`
- **Type:** orchestrator
- **Pipeline:** deepdive TICKER1 ‖ deepdive TICKER2 → gatekeeper (once) → comparison report → publish-discord
- **Output:** `reports/compare/{T1}_vs_{T2}_comparison.md`
```

### `references/knowledge-map.md`

```markdown
# Knowledge Map — stockiv-plugin

Maps which skills require which files before execution. Used for dependency verification and Sprint 2 parallelism planning.

| Skill | Requires File (before execution) | Written By |
|---|---|---|
| analyze-sentiment | `data/raw/context/{TICKER}_ticker_context.md` | collect-data |
| analyze-sentiment | `data/raw/context/market_context.md` | collect-data |
| analyze-fundamentals | `data/processed/synthesizer/{TICKER}/financial_summary.md` | collect-data |
| analyze-fundamentals | `data/processed/sentiment/ticker/{TICKER}_sentiment.md` | analyze-sentiment |
| analyze-valuation | `data/processed/synthesizer/{TICKER}/financial_summary.md` | collect-data |
| analyze-valuation | `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` | analyze-fundamentals |
| draft-report | `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md` | analyze-fundamentals |
| draft-report | `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md` | analyze-valuation |
| draft-report | `data/processed/sentiment/ticker/{TICKER}_sentiment.md` | analyze-sentiment |
| publish-discord | `reports/ticker/{TICKER}_GCCP_report.md` OR `.pdf` | draft-report |

## Sprint 2 Parallelism Note

`analyze-fundamentals` declares total dependency on `analyze-sentiment`. However:
- **Part III (quantitative):** Reads only `financial_summary.md` — does NOT need `{TICKER}_sentiment.md`
- **Part II (qualitative):** Reads `{TICKER}_sentiment.md`

→ Part III can run in parallel with `analyze-sentiment` after `collect-data` completes.
→ Part II must wait for `analyze-sentiment` output.
→ This is Sprint 2 work (requires `analyze-fundamentals` content change).
```

---

## Success Criteria

- [ ] `collect-data` SKILL.md exists at `.agents/plugins/stockiv-plugin/skills/collect-data/SKILL.md` with identical content to original
- [ ] All 8 skills present in `stockiv-plugin/skills/` with zero content changes
- [ ] `skill-creator` NOT present in `stockiv-plugin/`
- [ ] `plugin.json` exists and is valid JSON
- [ ] Agent definitions present in `stockiv-plugin/agents/`
- [ ] AGENTS.md routes to plugin paths
- [ ] `skill-routing.md` covers all 8 skills + planned compare-flow entry
- [ ] `knowledge-map.md` has dependency table + Sprint 2 parallelism note
- [ ] `_template/SKILL.md` exists with all standard sections
- [ ] `docs/sprint-1/path-audit.md` exists
- [ ] `docs/sprint-1/agent-audit.md` exists
- [ ] `docs/sprint-1/compare-flow-design.md` exists
- [ ] `.agents/skills-archived/` exists (flat skills archived, not deleted)

---

## What's NOT in This Sprint

| Feature | Reason |
|---|---|
| `analyze-fundamentals` dependency contract rewrite | Sprint 2 #2 — needs clean regression baseline first |
| `compare-flow` SKILL.md | Sprint 2 #1 — design contract doc only in Sprint 1 |
| Parallelism in `deepdive-flow` | Sprint 2 — depends on fundamentals split |
| `framework.md` splitting | Sprint 3+ — risk of cross-reference drift |
| `skill-creator` migration | Never — framework tooling, has internal relative paths |
| Screener / watchlist flows | Sprint 3+ |
