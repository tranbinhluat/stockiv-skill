# Brainstorm — Phase 2: Discussion & Debate

**Date:** 2026-06-21  
**Participants:** Kira, Nova, Sage, Milo, Ivy, Remy  
**Source:** Reactions to Phase 1 ideation

---

> **Format:** Agents react to each other's ideas. At least 2 genuine disagreements marked **[DISAGREE]**.  
> The goal is to pressure-test ideas and converge on what's actually worth doing.

---

## Round 1 — First Reactions

---

**Ivy →** Nova's N1 (plugin packaging) and Sage's I2 (path audit):

"N1 is the right foundation. But I want to make sure we sequence this correctly: I2 has to happen *before* N1 begins. My path audit table in Phase 1 isn't just documentation for the sake of it — it clarifies a specific anxiety developers will have: 'If we move skills from `.agents/skills/collect-data/` to `.agents/plugins/stockiv-plugin/skills/collect-data/`, do we also need to move `data/processed/synthesizer/FPT/`?' The answer is no — data paths are entirely separate from skill paths. But without writing it down, someone will panic mid-migration and half-stop. I2 is a two-hour task. It's the prerequisite for everything else."

**Nova →** Ivy's I2:

"Completely agree. I2 runs as a pre-sprint task — half a day, not a sprint ticket. And it confirms something critical: the inter-skill communication in this system is entirely file-based. There's no direct skill-to-skill API call. `analyze-fundamentals` doesn't 'call' `collect-data` — it reads `financial_summary.md`. That means plugin restructure is pure `.agents/` surgery. The `data/` directory is untouched."

**Milo →** Nova's N3 (shared references) + his own M1 (skill template):

"N3 and M1 are siblings — they both belong in the plugin on day one. The `knowledge-map.md` that Nova proposes goes in `references/`, and the `_template/SKILL.md` goes in `skills/_template/`. Together they make the plugin self-documenting for any new skill author. When someone adds a Sprint 2 skill like `compare-flow`, they open `references/knowledge-map.md` and instantly know which sections of `framework.md` to reference. Zero hunting. Both are S effort. We should do them both in Sprint 1."

**Kira →** Sage's S1 (parallelism in deepdive-flow):

"Sage, I want to understand the real user benefit here. The current deepdive-flow takes — what, 5 minutes end-to-end? If parallelism shaves one sequential step, does the analyst notice? The pain I hear from analysts isn't 'deepdive is slow' — it's 'I can't run deepdive on multiple stocks at once.' Screener (K1) solves a different and bigger problem than pipeline parallelism. I'm not saying S1 is wrong, I'm asking: is this the speedup that matters?"

**Sage →** Kira's concern:

"Fair challenge. The parallelism isn't just about wall-clock speed — it's about structural correctness. If `analyze-fundamentals` can declare itself independent of macro-sentiment (because it is — the quantitative Part III doesn't need it), then the dependency graph is more honest. And an honest dependency graph is the prerequisite for everything downstream: screener-flow, compare-flow, watchlist. If we don't fix the dependency contract now, every new flow we build in Sprint 2 inherits the incorrect sequential assumption."

---

## Round 2 — First Major Disagreement

---

**[DISAGREE 1] — Sage vs. Nova: Should parallelism land in Sprint 1?**

**Sage:** "Nova, let me be precise about what I'm proposing in S1. I'm not asking to rebuild `analyze-fundamentals` from scratch. Here's the actual change: `deepdive-flow/SKILL.md` currently says at Step 3, *'Wait completion. Sentiment output goes to Step 3.'* I'm proposing: add a conditional. If `data/processed/sentiment/market/{YEAR}_W{WW}_macro_sentiment.md` already exists (i.e., `weekly-flow` ran this week), spawn two subagents in parallel — (A) ticker-sentiment analysis and (B) the quantitative portion of fundamentals: ROE/ROA/margins/FCF/forensic checks from `financial_summary.md`. Both write their outputs. Then Part II qualitative analysis reads both outputs. It's a SKILL.md edit to `deepdive-flow`. The atomic skill `analyze-fundamentals` doesn't change — the flow changes."

**Nova:** "Sage, that's not accurate. Look at `analyze-fundamentals/SKILL.md` — it's not split into Part II and Part III execution blocks. The skill is a single sequential execution: it reads `financial_summary.md` AND `{TICKER}_sentiment.md` at the top, then runs quantitative analysis, then qualitative. There's no clean 'stop here and wait for sentiment' cut point in the current SKILL.md. What you're describing requires rewriting `analyze-fundamentals` to accept an optional `--quant-only` mode that skips Part II. That IS a content change to an atomic skill. It changes the skill's declared dependency contract: `## Depends On: analyze-sentiment must run ({TICKER}_sentiment.md required)` becomes conditional. That's a different skill than what exists today."

**Sage:** "The dependency contract is wrong today. `analyze-fundamentals` declares a total dependency on sentiment, but only Part II uses it. Fixing the contract makes the system more correct, not more risky."

**Nova:** "You can be right about the dependency being wrong and still be wrong about doing it in Sprint 1. Sprint 1's constraint is zero SKILL.md content changes. The moment we start rewriting `analyze-fundamentals`' dependency contract, we're doing structural analysis work on an atomic skill. That opens a scope door. What if the rewrite surfaces issues? What if Part III has hidden sentiment references we missed? We ship the plugin structure clean in Sprint 1, then do the dependency graph work in Sprint 2 with full attention."

**Remy (mediating):** "Nova's right on Sprint 1 scope. Sage, the parallelism insight is correct and valuable — it goes into the Sprint 2 plan as a specific deliverable: 'restructure `analyze-fundamentals` to accept partial execution, enabling parallel Step 2 in deepdive-flow.' It's not lost, it's sequenced properly."

---

## Round 3 — Second Major Disagreement

---

**[DISAGREE 2] — Kira vs. Remy: Should compare-flow be in Sprint 1?**

**Kira:** "Remy, I already conceded on screener (K1). But compare-flow (K2) is different. The analyst has been running deepdives and the peer data is already there — `collect-data` already writes peer ratio summaries as a side effect. I've been looking at this as 'new feature work' but it's not. It's surfacing something that's already collected. The `compare-flow` SKILL.md is 40 lines: 'given TICKER1 and TICKER2, verify both have fresh `financial_summary.md`, run `deepdive-flow` logic for each, output a comparison table.' The atomic skills don't change. It's pure orchestration. Sprint 1 that only migrates files and adds a template is a developer sprint, not an analyst sprint. Can we give the analyst one visible win in Sprint 1?"

**Remy:** "Kira, I hear the intent. But let's be honest about what 'pure orchestration' means in practice. Writing `compare-flow` SKILL.md requires: (1) designing the comparison output format — do we get one merged report, two separate PDFs, or a table? (2) deciding how the gatekeeper handles two tickers — does it run twice or once? (3) handling the case where only one ticker has fresh data. (4) updating AGENTS.md with new trigger patterns `/compare TICKER1 TICKER2`. (5) validating end-to-end. That's not 40 lines — that's a full skill with edge cases. And we're doing it while simultaneously migrating 8 skills and updating AGENTS.md. Sprint 1 has one job: clean foundation. Sprint 2 has one priority: compare-flow."

**Kira:** "I'm going to push back on one point: gatekeeper running twice. That's actually a design decision we should make *now*, even if we don't ship it in Sprint 1. If we don't answer it, the compare-flow design in Sprint 2 will be ambiguous. Can we at least add a design note to Sprint 1's deliverables: 'document the compare-flow design contract so Sprint 2 can ship it clean'?"

**Remy:** "That I'll accept. Sprint 1 includes a design note for compare-flow — output format, gatekeeper behavior, trigger pattern. No SKILL.md yet, just the design decision document. That way Sprint 2 starts clean."

**Kira:** "Done. And compare-flow is Sprint 2 priority #1, not 'backlog.'"

**Remy:** "Agreed. Compare-flow is Sprint 2 ticket #1."

---

## Round 4 — Finer Points

---

**Milo →** his own M2 (AGENTS.md routing table):

"I want a quick sanity check from the group on this. Current AGENTS.md — line 5 — is pure prose: *'Use `weekly-flow` skill user asks weekly reports, macro sentiment updates, types `/weekly`. Use `deepdive-flow` skill user types `/deepdive`...'* My routing table replaces that with an explicit `| Trigger | Skill | Notes |` table. Nova, Sage — does this actually help Claude route more reliably, or am I optimizing the wrong thing?"

**Sage:** "Tables are reliable for exact match patterns. The current prose is fuzzy on edge cases — what happens if the analyst types `/deepdive` without a ticker? The prose says 'asks full GCCP analysis specific stock ticker' which is ambiguous. A table with explicit trigger patterns removes that ambiguity. I support M2."

**Nova:** "I'd fold M2 into the plugin packaging task rather than treating it as a separate ticket. When we create the plugin and update AGENTS.md to point to it, we update the format at the same time. It's one AGENTS.md edit, not two."

**Milo:** "Agreed. M2 is part of the AGENTS.md update step in the plugin migration, not a standalone task."

---

**Ivy →** Nova's N2 (atomic vs. orchestrator separation) and skill-creator:

"Nova, I want to flag something before we commit to the atomic/orchestrator separation in N2. `skill-creator` is not like the other 8 skills. It has subdirectories — `agents/`, `references/`, `eval-viewer/` — and it references a script at `eval-viewer/generate_review.py`. If we put `skill-creator` inside `stockiv-plugin/skills/skill-creator/`, all its internal relative paths break. The eval-viewer script, the agents subfolder, the test cases — they all have relative path dependencies that assume `skill-creator` lives at the top-level `.agents/skills/` location."

**Nova:** "Good catch. `skill-creator` should not move into `stockiv-plugin`. It's framework tooling, not stockiv domain logic — it's a meta-skill for building skills, not for analyzing Vietnamese stocks. It either stays flat in `.agents/skills/skill-creator/` or gets its own `skill-creator-plugin` if we ever want to package it. For this sprint, it's explicitly excluded from the migration."

**Sage:** "Agreed. Eight skills migrate. `skill-creator` stays put."

**Ivy:** "Document this in the migration plan. If someone sees `.agents/skills/` still has one entry after Sprint 1, they shouldn't assume the migration failed."

---

**Nova →** Sage's S2 (structured `deps.json` manifest):

"Sage, I want to close out S2 since we haven't talked about it. The `deps.json` idea — machine-readable input/output declarations per skill — is genuinely interesting for Sprint 3 or 4 when we have a smart orchestrator that can dynamically build a pipeline. But for now, the freshness check in `collect-data` (`## Freshness Check: files < 7 days old`) handles most of the 'what needs to run?' decision-making adequately. And the `## Depends On` section in each SKILL.md is human-readable enough for now. `deps.json` is premature optimization until we have an orchestrator that actually reads it."

**Sage:** "Fair. I'll table S2. The `## Depends On` prose format is sufficient for Sprint 1–2 scale."

---

## Round 5 — Convergence

---

**Remy:** "Let me summarize where we've landed. High agreement on the Sprint 1 core:

1. **Pre-sprint:** I2 path audit (Ivy) + I3 agent location verification (Ivy) — 2-hour task, not a sprint ticket
2. **Sprint 1 core:** Plugin packaging — migrate 8 skills (minus `skill-creator`) from `.agents/skills/` to `.agents/plugins/stockiv-plugin/skills/`; create `plugin.json`; migrate agent definitions to `stockiv-plugin/agents/`
3. **Sprint 1 additions (S effort):** `references/knowledge-map.md` (Nova N3), `skills/_template/SKILL.md` (Milo M1), AGENTS.md routing table update (Milo M2 folded into packaging)
4. **Sprint 1 process:** Blue/green migration (Ivy I1) — copy before delete, validate one skill end-to-end before bulk migration
5. **Sprint 1 design note:** compare-flow contract document (Kira's concession — design only, no SKILL.md)

Explicitly out of Sprint 1:
- Parallelism (Sage S1) — Sprint 2 after `analyze-fundamentals` restructure
- Compare-flow SKILL.md (Kira K2) — Sprint 2 priority #1
- Screener-flow (Kira K1) — Sprint 2 priority #2 or Sprint 3
- Watchlist-flow (Kira K3) — Sprint 3
- Multi-ticker parallel pattern (Sage S3) — Sprint 3
- `deps.json` manifest (Sage S2) — indefinitely deferred
- `skill-creator` migration — excluded from `stockiv-plugin` entirely"

**Kira:** "Agreed — with the firm commitment that compare-flow design note is a Sprint 1 deliverable, not just 'we'll think about it later.'"

**Nova:** "Agreed. One more item: the Sprint 1 validation check should be a full end-to-end `/deepdive FPT` run after migration to confirm no regressions. Not just file existence checks."

**Ivy:** "Strongly seconded. That's the acceptance criterion."

**Sage:** "And the knowledge-map.md isn't just documentation — it's the seed of the dependency graph work we'll need for Sprint 2 parallelism. Write it with that in mind."

---

*Phase 3 concept synthesis begins in `03-concepts.md`.*
