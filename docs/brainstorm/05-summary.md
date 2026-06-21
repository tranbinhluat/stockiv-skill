# Brainstorm — Phase 5: Final Summary

**Date:** 2026-06-21
**Decision:** Concept A — Conservative Migration

---

## The Question We Answered

> How do we reorganize `stockiv-skill` into `stockiv-plugin` plugin format, with multi-flow support — without breaking the live analysis system?

---

## What We Decided

**Concept A — Conservative Migration**, enhanced with S-effort additions from debate.

**One sentence:** Package the 8 existing skills into plugin structure, migrate agent definitions, add routing registry + knowledge map + template scaffold — with zero SKILL.md content changes.

---

## Sprint 1 Scope (locked)

### Pre-sprint (non-negotiable, 2-hour tasks — Ivy owns)
1. **I2 — Path Audit:** Document every inter-skill file path in a table. Confirm `data/` paths are independent of `.agents/` paths.
2. **I3 — Agent Location Audit:** Verify where `gatekeeper-reviewer`, `stock-analyst`, `market-scout` agent definitions actually live. Confirm plugin migration includes them.

### Core Migration (Nova leads)
- Move 8 skills (all except `skill-creator`) from `.agents/skills/` → `.agents/plugins/stockiv-plugin/skills/`
- Create `stockiv-plugin/plugin.json`
- Migrate agent definitions to `stockiv-plugin/agents/`
- Blue/green process (Ivy I1): copy first, validate `collect-data` end-to-end, then bulk migrate, then delete originals

### S-effort Additions (zero content risk)
| Deliverable | Owner | Rationale |
|---|---|---|
| `references/knowledge-map.md` | Sage | Dependency graph semantics: "Skill X requires File Y before execution." Seed for Sprint 2 parallelism. |
| `references/skill-routing.md` | Milo | Machine-readable routing registry (all skills + trigger patterns). AGENTS.md references it. |
| `skills/_template/SKILL.md` | Milo | Scaffolded boilerplate with `{PLACEHOLDER}` comments. All standard sections pre-built. |
| AGENTS.md routing table update | Milo | Point to plugin paths; use `skill-routing.md` as source of truth. |
| compare-flow design note | Remy | Document: output format (one combined report), gatekeeper behavior (runs once on combined), trigger pattern (`/compare TICKER1 TICKER2`). No SKILL.md written yet. |

### Acceptance Criteria (Ivy)
- `/collect FPT` runs end-to-end through plugin path (not flat path)
- All 8 skill SKILL.md files exist in `stockiv-plugin/skills/` with identical content to originals
- AGENTS.md routes to plugin paths correctly
- `skill-routing.md` covers all existing trigger patterns
- `knowledge-map.md` lists all inter-skill file dependencies with "requires before" semantics
- `.agents/skills/` flat directory archived (not deleted until validation complete)

---

## What's Explicitly Out of Sprint 1

| Item | Deferred to | Owner |
|---|---|---|
| Parallelism in `deepdive-flow` (S1) | Sprint 2 | Sage |
| `analyze-fundamentals` dependency contract rewrite | Sprint 2 | Sage |
| `compare-flow` SKILL.md | Sprint 2 | Kira, Nova |
| Screener flow (K1) | Sprint 3+ | Kira |
| Watchlist digest (K3) | Sprint 3+ | Kira |
| `framework.md` splitting (Concept C) | Sprint 3+ | TBD |
| Multi-ticker parallel substrate (S3) | Sprint 3+ | Sage |
| `skill-creator` migration | Never (stays flat) | — |

---

## Sprint 2 Commitments (locked in vote)

1. **#1 — compare-flow** (Kira's condition): Full `compare-flow` SKILL.md. Input: `TICKER1 TICKER2`. Runs deepdive pipeline on both in parallel. Gatekeeper runs once on combined output. Output: `reports/compare/{T1}_vs_{T2}_comparison.md`. Trigger: `/compare TICKER1 TICKER2`.
2. **#2 — `analyze-fundamentals` dependency graph work** (Sage's condition): Restructure skill to accept partial execution (`--quant-only` mode), enabling parallel Step 2 in `deepdive-flow`. Update dependency declaration from total to conditional.

---

## Key Insights from Debate

**File-based communication is an architectural strength.** Nova confirmed: there are no direct skill-to-skill API calls. All inter-skill state passes through files in `data/`. This means plugin restructure is pure `.agents/` surgery — `data/` is untouched. Migration risk is structurally isolated.

**`skill-creator` is framework tooling, not domain logic.** It has internal relative path dependencies (`eval-viewer/`, `references/`, test cases) that assume flat `.agents/skills/` location. It never moves into `stockiv-plugin`. If ever packaged, it becomes `skill-creator-plugin` independently.

**`analyze-fundamentals`' dependency on sentiment is partially wrong.** Part III (quantitative: ROE/ROA/margins/forensics) doesn't need `{TICKER}_sentiment.md`. Only Part II qualitative analysis does. The declared total dependency is a correctness bug, not just an optimization gap. Sprint 2 fixes it.

**Sprint 1 scope discipline came from the right place.** Remy's "zero SKILL.md content changes" rule wasn't conservatism for its own sake — it preserves causal isolation. If something breaks in Sprint 1, it's the plugin structure. Sprint 2 content work then has a clean regression baseline.

**Routing table vs. routing registry.** Milo's M2 (table in AGENTS.md) and Concept C's `skill-routing.md` solve the same problem at different levels. The hybrid — standalone `skill-routing.md` referenced by AGENTS.md — gives Claude exact-match routing patterns AND gives developers a single authoritative file to update when adding new skills.

---

## What to Hand to Sprint Planning

```
Sprint 1 Goal: Clean plugin foundation. Zero SKILL.md content changes.

Pre-sprint: I2 path audit + I3 agent location audit (Ivy, before any commits)
Branch: feat/plugin-migration

Deliverables:
1. stockiv-plugin/ with plugin.json
2. 8 skills migrated (blue/green)
3. agent definitions in stockiv-plugin/agents/
4. references/knowledge-map.md (dep graph semantics)
5. references/skill-routing.md (routing registry)
6. skills/_template/SKILL.md
7. AGENTS.md updated to plugin paths + routing table
8. compare-flow design contract document

Sprint 2 locked: compare-flow (#1) + analyze-fundamentals dep work (#2)
```

---

*Brainstorm complete. Hand off to sprint planning.*
