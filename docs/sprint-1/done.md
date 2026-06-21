# Sprint 1 — Done

> **Sprint:** Plugin Migration (Concept A — Conservative)
> **Branch:** `feat/plugin-migration`
> **Completed:** 2026-06-21

---

## What Was Built

### Plugin Structure Created

```
.agents/plugins/stockiv-plugin/
  plugin.json                              ← plugin manifest (version 1.0.0)
  skills/
    collect-data/SKILL.md                  ← copied verbatim from .agents/skills/
    analyze-sentiment/SKILL.md
    analyze-fundamentals/SKILL.md
    analyze-valuation/SKILL.md
    draft-report/SKILL.md
    publish-discord/SKILL.md
    deepdive-flow/SKILL.md
    weekly-flow/SKILL.md
    _template/SKILL.md                     ← NEW scaffold for future skills
  agents/
    stock-analyst.agent.md                 ← copied from .github/agents/
    gatekeeper-reviewer.agent.md
    market-scout.agent.md
  references/
    skill-routing.md                       ← NEW routing registry (8 skills + planned compare-flow)
    knowledge-map.md                       ← NEW dependency graph + Sprint 2 parallelism note
```

### Files Changed

| File | Action | Notes |
|---|---|---|
| `.agents/plugins/stockiv-plugin/plugin.json` | Created | Plugin manifest |
| `.agents/plugins/stockiv-plugin/skills/*/SKILL.md` | Created (8 files) | Verbatim copies, all diff-verified identical |
| `.agents/plugins/stockiv-plugin/agents/*.agent.md` | Created (3 files) | Verbatim copies, originals intact in `.github/agents/` |
| `.agents/plugins/stockiv-plugin/references/skill-routing.md` | Created | Machine-readable routing registry |
| `.agents/plugins/stockiv-plugin/references/knowledge-map.md` | Created | Dependency graph + Sprint 2 parallelism note |
| `.agents/plugins/stockiv-plugin/skills/_template/SKILL.md` | Created | Scaffold for new skills |
| `AGENTS.md` | Updated | Replaced prose trigger description with structured routing table |
| `.agents/skills/` | Archived to `.agents/skills-archived/` | Flat skills preserved, not deleted |
| `.agents/skills/skill-creator/` | Preserved in-place | NOT migrated (has internal relative paths) |
| `docs/sprint-1/path-audit.md` | Created | Inter-skill file path audit |
| `docs/sprint-1/agent-audit.md` | Created | Agent location audit |
| `docs/sprint-1/compare-flow-design.md` | Created | compare-flow design contract |

---

## What Is NOT Done (Deferred to Sprint 2)

| Item | Reason |
|---|---|
| `compare-flow` SKILL.md | Sprint 2 #1 — design contract only in Sprint 1 |
| `analyze-fundamentals` dependency contract rewrite | Sprint 2 #2 — needs regression baseline first |
| Parallelism in `deepdive-flow` | Sprint 2 — depends on fundamentals split |
| `skill-creator` migration | Never — has internal relative paths |
| `framework.md` splitting | Sprint 3+ — risk of cross-reference drift |
| Screener / watchlist flows | Sprint 3+ |

---

## Known Issues / Sprint 2 Review Items

### 1. Sentiment Path Discrepancy
- **Plan spec (`skill-routing.md`, `knowledge-map.md`):** `data/processed/sentiment/ticker/{TICKER}_sentiment.md`
- **Actual `analyze-sentiment/SKILL.md` output:** `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- **Actual `analyze-fundamentals/SKILL.md` input:** `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- **Action:** Reconcile plan spec with actual SKILL.md paths in Sprint 2. No SKILL.md edits in Sprint 1.

### 2. Agent Path Typo in `weekly-flow/SKILL.md`
- **What:** References `../.github/agents/stock-analyst.agents.md` and `../.github/agents/market-scout.agents.md` (`.agents.md` should be `.agent.md`)
- **Action:** Fix typo in SKILL.md as part of Sprint 2 SKILL.md review pass. Do NOT fix in Sprint 1.

### 3. `harness-plugin` is an embedded git repo (submodule)
- **What:** `.agents/plugins/harness-plugin/` has its own `.git` directory and was added as a gitlink (submodule reference) in the commit.
- **Action:** Not a blocker for Sprint 1. Sprint 2 should decide whether to add it as a proper git submodule or `.gitignore` the nested `.git`.

---

## Commit Log (Sprint 1)

```
chore: pre-sprint path + agent audits
feat: create stockiv-plugin with 8 migrated skills
feat: add agent definitions to stockiv-plugin
feat: add skill-routing, knowledge-map, template; update AGENTS.md
chore: compare-flow design, archive flat skills, sprint 1 done
```

---

## Verification Checklist

- [x] `plugin.json` valid JSON, matches harness-plugin format
- [x] All 8 skills in `stockiv-plugin/skills/` — diff-verified identical to originals
- [x] `skill-creator` NOT in plugin
- [x] Agent definitions present in `stockiv-plugin/agents/`
- [x] Originals in `.github/agents/` NOT deleted
- [x] `AGENTS.md` routes to plugin paths with structured routing table
- [x] `skill-routing.md` covers all 8 skills + planned `compare-flow` entry
- [x] `knowledge-map.md` dependency table + Sprint 2 parallelism note
- [x] `_template/SKILL.md` exists with all standard sections
- [x] `docs/sprint-1/path-audit.md` exists
- [x] `docs/sprint-1/agent-audit.md` exists
- [x] `docs/sprint-1/compare-flow-design.md` exists
- [x] `.agents/skills-archived/` exists (flat skills archived, not deleted)
- [x] `.agents/skills/skill-creator/` preserved at original location
