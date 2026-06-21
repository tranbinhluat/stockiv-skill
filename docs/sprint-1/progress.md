# Sprint 1 — Progress Tracker

> **Recovery prompt:** "Read `docs/sprint-1/plan.md` and this file. Continue Sprint 1 from where it left off."
> **Branch:** `feat/plugin-migration`

---

## Task Status

| # | Task | Status | Notes |
|---|------|--------|-------|
| P1 | Path Audit (I2) | ✅ Done | All data/ paths independent of .agents/. Discrepancy found in sentiment path (simplified vs versioned) — Sprint 2 item |
| P2 | Agent Location Audit (I3) | ✅ Done | All 3 agents confirmed in .github/agents/ only. .agents/agents/ does not exist |
| 1 | Create `stockiv-plugin/plugin.json` | ✅ Done | `{ "name": "stockiv-plugin", "version": "1.0.0" }` |
| 2 | Blue/green: copy + validate `collect-data` | ✅ Done | diff confirmed IDENTICAL |
| 3 | Bulk migrate remaining 7 skills | ✅ Done | All 7 diff-confirmed IDENTICAL |
| 4 | Migrate agent definitions | ✅ Done | Copied (not moved) all 3 agents; originals intact in .github/agents/ |
| 5 | Create `references/skill-routing.md` | ⬜ Not started | |
| 6 | Create `references/knowledge-map.md` | ⬜ Not started | |
| 7 | Create `skills/_template/SKILL.md` | ⬜ Not started | |
| 8 | Update `AGENTS.md` routing table | ⬜ Not started | |
| 9 | Write compare-flow design note | ⬜ Not started | |
| 10 | Archive flat `.agents/skills/` | ⬜ Not started | |
| 11 | Write `docs/sprint-1/done.md` | ⬜ Not started | |

---

## Bugs Found

| # | Description | Severity | Status | Fix |
|---|-------------|----------|--------|-----|
| — | (none yet) | | | |

---

## Notes

- Branch: `feat/plugin-migration` (created 2026-06-21)
- Rule: No SKILL.md content changes. If you need to edit skill logic, stop and document as Sprint 2 item.
- `skill-creator` must NOT be moved into `stockiv-plugin` — it has internal relative path dependencies.
- Agent files currently live in `.github/agents/` (not `.agents/agents/`). Audit (P2) must confirm before migration.
