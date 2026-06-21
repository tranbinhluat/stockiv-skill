# Brainstorm — Phase 4: Team Vote

**Date:** 2026-06-21
**Voting on:** Concept A (Conservative Migration) · Concept B (Full Restructure) · Concept C (Knowledge-First Plugin)

---

> Each agent votes with brief justification. Ties broken by Remy.
> Recall from Phase 2: strong convergence existed on Sprint 1 = zero SKILL.md content risk.

---

## 🎨 Kira — Product Designer / Analyst UX

**Vote: Concept A** (with explicit Sprint 2 commitment on compare-flow)

"I wanted Concept B. I conceded. But here's what I need on the record: Concept A is only acceptable if compare-flow is Sprint 2 ticket #1 — not backlog, not 'eventually.' Remy agreed to that in Phase 2. If Sprint 2 doesn't ship compare-flow, I'm retroactively right that we should've done B.

The analyst gets zero new capability in Sprint 1. That's the cost of A. I accept it only because the foundation work is real — plugin structure is the prerequisite for everything. But we owe her compare-flow in the next sprint."

---

## ⚙️ Nova — Flow Engineer / Skill Architect

**Vote: Concept A**

"A is the only concept that respects Sprint 1's constraint: touch `.agents/` structure, not SKILL.md content.

What swings this for me: the S-effort additions from Phase 2 debate are already folded into Concept A's delivery — `references/knowledge-map.md` (N3), `skills/_template/SKILL.md` (M1), AGENTS.md routing table (M2). These are low-risk wins that make the plugin immediately useful without opening any content-change scope.

Concept C is tempting — the skill registry idea is genuinely good — but splitting `framework.md` in Sprint 1 is the wrong risk profile. C is Sprint 3 work after we have two sprints of production evidence confirming the plugin structure holds."

---

## 🔁 Sage — Backend / Pipeline Engineer

**Vote: Concept A** (reluctantly)

"My honest preference is Concept B — the dependency contract in `analyze-fundamentals` is factually wrong today. Declaring total sentiment dependency when only Part II uses it is a correctness problem, not a performance optimization.

But Nova and Remy are right about Sprint 1 scope. If I rewrite `analyze-fundamentals`' dependency contract and it surfaces Part III hidden sentiment references I missed, we've shipped a broken atomic skill into a brand-new plugin structure with no regression baseline to compare against.

Sequence matters: A first, build the baseline, then B's parallelism work in Sprint 2 has something to regress against. I vote A on the condition that `analyze-fundamentals` dependency graph work is Sprint 2 item #2 (after compare-flow as Kira's #1).

One addition I want in Sprint 1: `references/knowledge-map.md` should be written with dependency graph semantics in mind — not just 'Skill X reads File Y' but 'Skill X requires File Y to exist before execution.' That seed pays forward to Sprint 2 parallelism."

---

## 🎨 Milo — Visual / Systems

**Vote: Concept A + Concept C's routing idea (hybrid)**

"I'm voting A but I want to rescue one thing from C: the routing table in AGENTS.md (my M2) was already accepted in Phase 2. But Concept C's `skill-routing.md` as a machine-readable registry is the better implementation of the same idea.

My proposal: in Sprint 1, implement M2 as Concept A specifies — routing table in AGENTS.md — but structure it as a standalone `references/skill-routing.md` file that AGENTS.md imports or references. That's the skeleton of Concept C's skill registry without splitting `framework.md`. Future sprints can grow the registry; we start with the trigger routing now.

This isn't Concept C. It's Concept A with C's routing architecture. Zero extra effort, same sprint scope."

---

## 🔍 Ivy — QA / Risk

**Vote: Concept A**

"Risk profile is decisive for me.

| Concept | SKILL.md risk | Path risk | Regression surface |
|---|---|---|---|
| A | Zero — no content changes | Low — known paths audited (I2) | One skill validated end-to-end (blue/green) |
| B | High — `analyze-fundamentals` rewrite | Medium | Full deepdive end-to-end required before merge |
| C | Medium — `framework.md` split | Low | Every skill that reads framework cross-referenced |

Concept B's `analyze-fundamentals` rewrite is the highest-risk change in the codebase. It's 160+ lines, referenced by both `analyze-valuation` and `draft-report`. Introducing that change simultaneously with plugin migration means any regression could be caused by either the structural change OR the content change. We lose the ability to isolate root cause.

Concept A gives us clean causal isolation: if something breaks in Sprint 1, it's because of the plugin structure, not content. That's the only safe foundation for Sprint 2 content work.

Pre-sprint requirements are non-negotiable: I2 path audit and I3 agent location verification before first sprint commit. Both are 2-hour tasks, not sprint tickets."

---

## 📦 Remy — Producer

**Vote: Concept A**

**Tiebreaker:** Not needed — consensus reached.

"Result: Concept A, with the following additions already in scope from Phase 2 (all S-effort, zero SKILL.md content risk):

- `references/knowledge-map.md` — with dependency graph semantics (Sage's requirement)
- `skills/_template/SKILL.md` — scaffold boilerplate
- `references/skill-routing.md` (Milo's hybrid) — standalone routing registry referenced by AGENTS.md
- AGENTS.md — routing table update pointing to plugin paths
- Sprint 1 design note — compare-flow contract: output format, gatekeeper behavior, trigger pattern

**What this is not:** Concept A is not 'bare minimum.' It is conservative migration done with the groundwork for Sprint 2 velocity. The knowledge-map, routing registry, and template are sprint-multipliers — the team builds once, uses for every future flow.

**Commitments recorded:**
- Compare-flow: Sprint 2 ticket #1 (Kira's condition, accepted)
- `analyze-fundamentals` dependency graph work: Sprint 2 ticket #2 (Sage's condition, accepted)
- Pre-sprint tasks: I2 path audit + I3 agent location verification (Ivy, before any Sprint 1 commits)"

---

## Vote Summary

| Agent | Vote | Condition |
|---|---|---|
| Kira | **A** | compare-flow = Sprint 2 #1 |
| Nova | **A** | S-effort additions confirmed in scope |
| Sage | **A** | dependency graph work = Sprint 2 #2; knowledge-map written with dep semantics |
| Milo | **A** | routing table → `skill-routing.md` standalone file |
| Ivy | **A** | I2 + I3 pre-sprint tasks non-negotiable |
| Remy | **A** | All conditions accepted |

**Decision: Concept A — Conservative Migration** ✅

All Sprint 2 commitments documented and locked.

---

*Phase 5 final summary in `05-summary.md`.*
